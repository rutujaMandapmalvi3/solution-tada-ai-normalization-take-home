"""isolved employee adapter mapping, paging, supplemental ownership and preservation."""
import contextlib
import copy
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from normalization.__main__ import main
from normalization.adapters import isolved
from normalization.mapping_engine import MappingEngine
from normalization.source_models.isolved.isolved_source_model_employee import IsolvedEmployeeInput


def employee(record_id=7):
    return {
        "id": record_id, "nameAddress": {"id": 10, "firstName": "Example",
            "lastName": "Employee", "preferredPronouns": "they/them"},
        "personal": {"id": 11, "preferredPronouns": "they/them", "future_flag": False},
        "eligibleForRehire": False, "birthDate": "2000-01-02T00:30:00+14:00",
        "gender": "Male", "maritalStatus": "Married", "employmentCategoryCode": "UNVERIFIED",
        "annualSalary": 50000.0, "workLocation": "001", "legalCode": "002",
        "links": [{"href": "/synthetic/employee", "rel": "self", "method": "GET"}],
        "salary_history": [{"id": 99, "perPaySalary": 2000.0,
                            "seasons": [{"id": 3, "description": "Summer"}]}],
    }


class IsolvedEmployeeMappingChecks(unittest.TestCase):
    def test_detail_maps_to_shared_output_and_preserves_raw_category_and_links(self):
        payload = employee()
        before = copy.deepcopy(payload)
        output = isolved.normalize("employee", payload, {})
        self.assertEqual(len(output), 1)
        item = output[0]
        self.assertEqual(item["provider"], "isolved")
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
        self.assertEqual(item["source_metadata"]["mapping_issues"] if "mapping_issues" in item["source_metadata"] else [], [])
        self.assertEqual(payload, before)
        json.dumps(output, allow_nan=False)

    def test_paged_records_reuse_one_engine_and_preserve_wrapper_without_results(self):
        payload = {"results": [employee(7), employee(8)], "totalItems": 2,
                   "totalPages": 1.0, "nextPageUrl": None, "previousPageUrl": "/synthetic/previous",
                   "future_wrapper": {"flag": False}}
        before = copy.deepcopy(payload)
        validate = IsolvedEmployeeInput.validate_response
        with patch.object(isolved, "MappingEngine", wraps=MappingEngine) as factory, \
                patch.object(IsolvedEmployeeInput, "validate_response", wraps=validate) as validation:
            output = isolved.normalize_employees(payload, {})
        self.assertEqual(factory.call_count, 1)
        self.assertEqual(validation.call_count, 1)
        self.assertEqual([record["employee_id"] for record in output], ["7", "8"])
        self.assertEqual(output[0]["source_metadata"]["isolved"]["response"],
                         {key: value for key, value in payload.items() if key != "results"})
        self.assertEqual(payload, before)
        output[0]["source_metadata"]["isolved"]["response"]["future_wrapper"]["flag"] = True
        self.assertIs(output[1]["source_metadata"]["isolved"]["response"]["future_wrapper"]["flag"], False)
        self.assertIs(payload["future_wrapper"]["flag"], False)

    def test_raw_category_preserves_missing_null_blank_and_nonblank_values(self):
        for supplied in ({}, {"employmentCategoryCode": None}, {"employmentCategoryCode": ""},
                         {"employmentCategoryCode": "FT"}):
            with self.subTest(supplied=supplied):
                item = isolved.normalize_employees({"id": 1, **supplied}, {})[0]
                provider = item.get("provider_fields", {}).get("isolved", {})
                self.assertNotIn("employment_type", item)
                self.assertEqual("employment_category_code" in provider, "employmentCategoryCode" in supplied)
                if supplied:
                    self.assertEqual(provider["employment_category_code"], supplied["employmentCategoryCode"])

    def test_pronoun_conflicts_and_rehire_true_keep_common_canonical_labels(self):
        payload = employee()
        payload["personal"]["preferredPronouns"] = "she/her"
        payload["eligibleForRehire"] = True
        item = isolved.normalize_employees(payload, {})[0]
        self.assertIsNone(item["preferred_pronouns"])
        self.assertEqual(item["eligible_for_rehire"], "eligible")
        meta = item["source_metadata"]
        self.assertEqual(meta["original_values"]["nameAddress.preferredPronouns"], "they/them")
        self.assertEqual(meta["original_values"]["personal.preferredPronouns"], "she/her")
        self.assertEqual(len(meta["mapping_issues"]), 1)

    def test_standalone_salary_history_never_uses_salary_record_ids_as_employee_id(self):
        payload = [{"id": 99, "perPaySalary": 2000.0}, {"id": 100, "perPaySalary": 2500.0}]
        before = copy.deepcopy(payload)
        output = isolved.normalize_employees(payload, {})
        self.assertEqual(len(output), 1)
        item = output[0]
        self.assertIsNone(item["employee_id"])
        self.assertEqual([row["id"] for row in item["provider_fields"]["isolved"]["salary_history"]],
                         ["99", "100"])
        self.assertEqual(item["source_metadata"]["isolved"]["input_kind"], "standalone_salary_history")
        self.assertEqual(item["source_metadata"]["mapping_issues"][0]["source_path"], "salary_history")
        self.assertNotIn("id", item["source_metadata"]["original_values"])
        self.assertEqual(payload, before)

    def test_empty_and_nullable_records_remain_supported(self):
        for payload in ([], {"results": []}, {"results": None}, {"totalItems": 0}):
            with self.subTest(payload=payload), patch.object(isolved, "MappingEngine") as factory:
                self.assertEqual(isolved.normalize_employees(payload, {}), [])
                factory.assert_not_called()
        self.assertIsNone(isolved.normalize_employees({"id": None}, {})[0]["employee_id"])

    def test_invalid_source_records_fail_before_engine_creation(self):
        for payload in ({}, {"results": [{"id": 1}, {}]}, [{"id": 1}, {}],
                        {"id": 1, "annualSalary": []}):
            with self.subTest(payload=payload), patch.object(isolved, "MappingEngine") as factory:
                with self.assertRaises(ValidationError):
                    isolved.normalize_employees(payload, {})
                factory.assert_not_called()

    def test_reference_warning_is_preserved_in_cli_output(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            output = Path(directory) / "output.json"
            source.write_text(json.dumps(employee()))
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                code = main(["normalize", "--provider", "isolved", "--entity", "employee",
                             "--input", str(source), "--output", str(output)])
            self.assertEqual(code, 0)
            self.assertIn("Candidate-distribution permission", errors.getvalue())
            self.assertTrue(output.exists())
            saved = json.loads(output.read_text())
            self.assertIn("reference_pack", saved[0]["source_metadata"]["isolved"])


if __name__ == "__main__":
    unittest.main()
