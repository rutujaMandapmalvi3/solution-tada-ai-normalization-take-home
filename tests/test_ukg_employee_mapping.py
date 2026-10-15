"""UKG employee mapping through the bundle pipeline (detail, list, merged supplements)."""
import copy
import unittest

from bundle_helpers import UKG, UKG_CO, codes, only, response, run, run_one

DETAIL = UKG_CO + "/employees/{aid}"
LIST = UKG_CO + "/employees"


class UKGEmployeeMappingChecks(unittest.TestCase):
    def test_detail_and_list_share_mapping(self):
        record = {"id": 7.0, "first_name": "Example", "ein_name": "Example EIN",
                  "ein": {"id": 3}, "address": {"city": "Example city"},
                  "dates": {"birthday": "2000-01-02"},
                  "_links": {"country-fields": "/synthetic/country"},
                  "future_field": {"flag": False}}
        wrapped = {"employees": [record], "next_page": "/synthetic/next"}
        before = copy.deepcopy(wrapped)
        # Draft 4 "integer" rejects 7.0, so the detail body uses 7; the list schema types id as number.
        for endpoint, body in ((DETAIL, {**record, "id": 7}), (LIST, wrapped)):
            with self.subTest(endpoint=endpoint):
                document = run_one("ukg-ready", endpoint, body, **UKG, aid="7")
                result = only(document, "employees")
                self.assertEqual(result["id"], "ukg-ready:employee:001:7")
                self.assertEqual(result["employee_id"], "7")
                self.assertEqual(result["ukg_ein_id"], "3")
                self.assertEqual(result["ukg_ein_name"], "Example EIN")
                self.assertEqual(result["source_extras"]["ukg-ready"]["future_field"], {"flag": False})
                # country-fields is not in the contract's _links schema: an extra, not "unmapped".
                self.assertEqual(result["source_extras"]["ukg-ready"]["_links"]["country-fields"],
                                 "/synthetic/country")
        # The list wrapper is kept per response in document metadata.
        self.assertEqual(document["source_metadata"]["ukg-ready"]["responses"][0]["wrapper"]["next_page"],
                         "/synthetic/next")
        self.assertEqual(wrapped, before)

    def test_pay_info_and_compensation_merge_into_the_employee(self):
        document = run("ukg-ready",
                       response(DETAIL, {"id": 7, "first_name": "Example"}, **UKG, aid="7"),
                       response(UKG_CO + "/employees/{aid}/pay-info", {"standard_work_day": 28800000},
                                **UKG, aid="7"),
                       response(UKG_CO + "/employees/{aid}/compensation/history",
                                {"compensations": [{"id": 9, "amount": 1}]}, **UKG, aid="7"))
        employee = only(document, "employees")
        self.assertEqual(employee["ukg_standard_work_day_milliseconds"], 28800000)
        self.assertIn("compensation_history", employee["provider_fields"]["ukg-ready"])
        self.assertEqual(len(employee["source_metadata"]["ukg-ready"]["sources"]), 3)
        self.assertNotIn("merge_conflict", codes(document))

    def test_list_validates_supplied_detail_fields(self):
        # Contract type errors stop the run (previously a Pydantic ValidationError).
        with self.assertRaisesRegex(ValueError, "address/city"):
            run_one("ukg-ready", DETAIL, {"id": 1, "address": {"city": []}}, **UKG, aid="1")
        # The list schema does not describe address; the canonical model still rejects a non-text city.
        with self.assertRaises(ValueError):
            run_one("ukg-ready", LIST, {"employees": [{"id": 1, "address": {"city": []}}]}, **UKG)
        # An employee without an id cannot get a canonical id.
        with self.assertRaisesRegex(ValueError, "cannot build employee id"):
            run_one("ukg-ready", LIST, {"employees": [{}]}, **UKG)
        # Missing required wrapper fields are not enforced: nothing to map.
        self.assertEqual(run_one("ukg-ready", LIST, {}, **UKG)["employees"], [])

    def test_numeric_id_and_empty_collection_policies(self):
        self.assertEqual(run_one("ukg-ready", LIST, {"employees": []}, **UKG)["employees"], [])
        for endpoint, body in ((DETAIL, {"id": None}), (LIST, {"employees": [{"id": None}]})):
            with self.subTest(endpoint=endpoint), self.assertRaisesRegex(ValueError, "cannot build employee id"):
                run_one("ukg-ready", endpoint, body, **UKG)
        with self.assertRaises(ValueError):
            run_one("ukg-ready", LIST, {"employees": [{"id": 7.5}]}, **UKG)
