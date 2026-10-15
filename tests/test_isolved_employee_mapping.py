"""isolved employee routes: detail, paging, salary history merged by id, preservation."""
import contextlib
import copy
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from bundle_helpers import ISOL, ISOL_EMPLOYEE, ISOL_LEGALS, codes, response, run, run_one
from normalization.__main__ import main

DETAIL = ISOL_LEGALS + "/{legalId}/employees/{id}"
LIST = ISOL_LEGALS + "/{legalId}/employees"
SALARIES = ISOL_EMPLOYEE + "/salaries"


def employee(record_id=7):
    return {
        "id": record_id, "nameAddress": {"id": 10, "firstName": "Example",
            "lastName": "Employee", "preferredPronouns": "they/them"},
        "personal": {"id": 11, "preferredPronouns": "they/them", "future_flag": False},
        "eligibleForRehire": False, "birthDate": "2000-01-02T00:30:00+14:00",
        "gender": "Male", "maritalStatus": "Married", "employmentCategoryCode": "UNVERIFIED",
        "annualSalary": 50000.0, "workLocation": "001", "legalCode": "002",
        "links": [{"href": "/synthetic/employee", "rel": "self", "method": "GET"}],
    }


SALARY_HISTORY = [{"id": 99, "perPaySalary": 2000.0, "seasons": [{"id": 3, "description": "Summer"}]}]


def detail(payload, record_id="7"):
    return run_one("isolved", DETAIL, payload, **ISOL, id=record_id)


class IsolvedEmployeeMappingChecks(unittest.TestCase):
    def test_detail_and_salaries_map_to_one_employee_and_preserve_raw_category_and_links(self):
        payload = employee()
        before = copy.deepcopy(payload)
        document = run("isolved", response(DETAIL, payload, **ISOL, id="7"),
                       response(SALARIES, SALARY_HISTORY, **ISOL, employeeId="7"))
        self.assertEqual(len(document["employees"]), 1)
        item = document["employees"][0]
        self.assertEqual(item["provider"], "isolved")
        self.assertEqual(item["id"], "isolved:employee:4000:1:7")
        self.assertEqual(item["company_ref"], "isolved:company:4000:1")
        self.assertEqual(item["employee_id"], "7")
        self.assertEqual(item["first_name"], "Example")
        self.assertEqual(item["birth_date"], "2000-01-02")
        self.assertEqual(item["gender"], "male")
        self.assertEqual(item["marital_status"], "married")
        self.assertEqual(item["preferred_pronouns"], "they/them")
        self.assertEqual(item["eligible_for_rehire"], "ineligible")
        self.assertEqual(item["annual_salary"], 50000.0)
        self.assertEqual(item["work_location_code"], "001")
        self.assertEqual(item["isolved_legal_code"], "002")
        self.assertNotIn("employment_type", item)
        provider = item["provider_fields"]["isolved"]
        self.assertEqual(provider["employment_category_code"], "UNVERIFIED")
        self.assertEqual(provider["unmapped"]["links"], payload["links"])
        self.assertEqual(provider["salary_history"][0]["id"], "99")
        self.assertEqual(provider["salary_history"][0]["seasons"][0]["id"], "3")
        self.assertIs(item["source_extras"]["isolved"]["personal"]["future_flag"], False)
        self.assertEqual(item["source_metadata"].get("mapping_issues", []), [])
        self.assertNotIn("merge_conflict", codes(document))
        self.assertEqual(payload, before)
        json.dumps(document, allow_nan=False)

    def test_paged_records_preserve_wrapper_without_results(self):
        payload = {"results": [employee(7), employee(8)], "totalItems": 2,
                   "totalPages": 1.0, "nextPageUrl": None, "previousPageUrl": "/synthetic/previous",
                   "future_wrapper": {"flag": False}}
        before = copy.deepcopy(payload)
        document = run_one("isolved", LIST, payload, **ISOL)
        self.assertEqual(sorted(record["employee_id"] for record in document["employees"]), ["7", "8"])
        self.assertEqual(document["source_metadata"]["isolved"]["responses"][0]["wrapper"],
                         {key: value for key, value in payload.items() if key != "results"})
        self.assertEqual(payload, before)

    def test_raw_category_preserves_missing_null_blank_and_nonblank_values(self):
        for supplied in ({}, {"employmentCategoryCode": None}, {"employmentCategoryCode": ""},
                         {"employmentCategoryCode": "FT"}):
            with self.subTest(supplied=supplied):
                item = detail({"id": 1, **supplied}, "1")["employees"][0]
                provider = item.get("provider_fields", {}).get("isolved", {})
                self.assertNotIn("employment_type", item)
                self.assertEqual("employment_category_code" in provider, "employmentCategoryCode" in supplied)
                if supplied:
                    self.assertEqual(provider["employment_category_code"], supplied["employmentCategoryCode"])

    def test_pronoun_conflicts_and_rehire_true_keep_common_canonical_labels(self):
        payload = employee()
        payload["personal"]["preferredPronouns"] = "she/her"
        payload["eligibleForRehire"] = True
        item = detail(payload)["employees"][0]
        self.assertIsNone(item["preferred_pronouns"])
        self.assertEqual(item["eligible_for_rehire"], "eligible")
        meta = item["source_metadata"]
        self.assertEqual(meta["original_values"]["nameAddress.preferredPronouns"], "they/them")
        self.assertEqual(meta["original_values"]["personal.preferredPronouns"], "she/her")
        self.assertEqual(len(meta["mapping_issues"]), 1)

    def test_salary_history_alone_takes_its_owner_from_params_not_salary_ids(self):
        payload = [{"id": 99, "perPaySalary": 2000.0}, {"id": 100, "perPaySalary": 2500.0}]
        before = copy.deepcopy(payload)
        document = run_one("isolved", SALARIES, payload, **ISOL, employeeId="7")
        self.assertEqual(len(document["employees"]), 1)
        item = document["employees"][0]
        self.assertEqual(item["id"], "isolved:employee:4000:1:7")
        self.assertEqual(item["employee_id"], "7")
        self.assertEqual([row["id"] for row in item["provider_fields"]["isolved"]["salary_history"]],
                         ["99", "100"])
        self.assertEqual(payload, before)

    def test_empty_collections_produce_no_records(self):
        for payload in ({"results": []}, {"results": None}, {"totalItems": 0}):
            with self.subTest(payload=payload):
                self.assertEqual(run_one("isolved", LIST, payload, **ISOL)["employees"], [])

    def test_records_without_id_or_with_wrong_types_stop_the_run(self):
        for endpoint, payload, params, message in (
            (DETAIL, {}, {"id": "1"}, "cannot build employee id"),
            (DETAIL, {"id": None}, {"id": "1"}, "cannot build employee id"),
            (LIST, {"results": [{"id": 1}, {}]}, {}, "cannot build employee id"),
            (DETAIL, {"id": 1, "annualSalary": []}, {"id": "1"}, "annualSalary"),
            (DETAIL, {"id": 2}, {"id": "1"}, "conflicts"),
        ):
            with self.subTest(payload=payload), self.assertRaisesRegex(ValueError, message):
                run_one("isolved", endpoint, payload, **ISOL, **params)

    def test_reference_warning_is_preserved_in_cli_output(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            output = Path(directory) / "output.json"
            source.write_text(json.dumps({"provider": "isolved", "responses": [
                {"endpoint": DETAIL, "params": {**ISOL, "id": "7"}, "body": employee()}]}))
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                code = main(["normalize", "--input", str(source), "--output", str(output)])
            self.assertEqual(code, 0)
            self.assertIn("Candidate-distribution permission", errors.getvalue())
            saved = json.loads(output.read_text())
            self.assertIn("reference_pack", saved["source_metadata"]["isolved"])


if __name__ == "__main__":
    unittest.main()
