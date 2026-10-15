"""UKG shared employee validation and adapter mapping."""
import copy
import unittest
from pydantic import ValidationError
from normalization.adapters import ukg_ready
from normalization.source_models.ukg_ready.ukg_ready_source_model_employee import UKGReadyEmployeeInput


class UKGEmployeeMappingChecks(unittest.TestCase):
    def test_detail_and_list_share_validation_and_mapping(self):
        record = {"id": 7.0, "first_name": "Example", "ein_name": "Example EIN",
                  "ein": {"id": 3}, "address": {"city": "Example city"},
                  "dates": {"birthday": "2000-01-02"},
                  "_links": {"country-fields": "/synthetic/country"},
                  "future_field": {"flag": False}}
        wrapped = {"employees": [record], "next_page": "/synthetic/next"}
        before = copy.deepcopy(wrapped)
        for payload in (record, wrapped):
            with self.subTest(wrapped="employees" in payload):
                validated = UKGReadyEmployeeInput.validate_response(payload)
                self.assertIs(type(validated[0]), UKGReadyEmployeeInput)
                result = ukg_ready.normalize("employee", payload, {})[0]
                self.assertEqual(result["employee_id"], "7")
                self.assertEqual(result["ukg_ein_id"], "3")
                self.assertEqual(result["ukg_ein_name"], "Example EIN")
                self.assertEqual(result["source_extras"]["ukg-ready"]["future_field"], {"flag": False})
                self.assertEqual(result["provider_fields"]["ukg-ready"]["unmapped"]["_links"]["country-fields"],
                                 "/synthetic/country")
        self.assertEqual(result["source_metadata"]["ukg-ready"]["response"]["next_page"], "/synthetic/next")
        self.assertEqual(wrapped, before)

    def test_list_validates_supplied_detail_fields(self):
        with self.assertRaises(ValidationError):
            UKGReadyEmployeeInput.validate_response({"employees": [{"id": 1, "address": {"city": []}}]})
        for payload in ({}, {"employees": [{}]}):
            with self.subTest(payload=payload), self.assertRaises(ValidationError):
                UKGReadyEmployeeInput.validate_response(payload)

    def test_numeric_id_and_empty_collection_policies(self):
        self.assertEqual(ukg_ready.normalize("employee", {"employees": []}, {}), [])
        for payload in ({"id": None}, {"employees": [{"id": None}]}):
            self.assertIsNone(ukg_ready.normalize("employee", payload, {})[0]["employee_id"])
        with self.assertRaises(ValueError):
            ukg_ready.normalize("employee", {"employees": [{"id": 7.5}]}, {})
