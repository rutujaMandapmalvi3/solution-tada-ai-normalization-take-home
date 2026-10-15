"""Employee mapping integration: source validation -> YAML engine -> CLI JSON."""
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
from normalization.adapters import prismhr
from normalization.mapping_engine import MappingEngine
from normalization.source_models.prismhr.prismhr_source_model_employee import PrismHREmployee


def employee(identifier="0007"):
    return {
        "id": identifier, "firstName": "Example", "lastName": "Employee",
        "person": {"birthDate": "2000-01-02T00:30:00+14:00", "gender": "F",
                   "maritalStatus": "M", "employerId": ["001"], "future_flag": False},
        "client": {"employeeType": "FT", "statusClass": "A", "rehireOk": ""},
        "contactInformation": {"zipcode": "02108", "zipSuffix": "0123"},
        "compensation": {"hourlyPay": "25.50", "standardHours": "0"},
    }


def response(*records):
    return {"errorCode": "0", "errorMessage": "", "employee": list(records)}


class PrismHREmployeeMappingChecks(unittest.TestCase):
    def test_adapter_returns_json_ready_records_with_context_metadata_and_extras(self):
        payload = {**response(employee()), "infoMessage": ["Informational"],
                   "updateMessage": "Updated", "extension": {"any": {"note": "Retained"}},
                   "future_wrapper": {"value": 0}}
        before = copy.deepcopy(payload)
        result = prismhr.normalize("employee", payload, {}, client_id="00132")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        output = result[0]
        self.assertEqual(output["provider"], "prismhr")
        self.assertEqual(output["employee_id"], "0007")
        self.assertEqual(output["prismhr_client_id"], "00132")
        self.assertEqual(output["prismhr_employer_ids"], ["001"])
        self.assertEqual(output["birth_date"], "2000-01-02")
        self.assertEqual(output["gender"], "female")
        self.assertEqual(output["marital_status"], "married")
        self.assertEqual(output["postal_code"], "02108-0123")
        self.assertEqual(output["hourly_rate"], 25.5)
        self.assertEqual(output["standard_hours_per_pay_period"], 0.0)
        self.assertIsNone(output["employment_type"])
        self.assertEqual(output["source_metadata"]["original_values"]["client.employeeType"], "FT")
        self.assertIs(output["source_extras"]["prismhr"]["person"]["future_flag"], False)
        wrapper = output["source_metadata"]["prismhr"]["response"]
        self.assertEqual(wrapper, {key: value for key, value in payload.items() if key != "employee"})
        self.assertNotIn("employee", wrapper)
        self.assertNotIn("termination_date", output)
        self.assertEqual(payload, before)
        json.dumps(result, allow_nan=False)

    def test_one_engine_is_reused_and_each_employee_is_validated_once(self):
        validate = PrismHREmployee.model_validate
        with patch.object(prismhr, "MappingEngine", wraps=MappingEngine) as factory, \
                patch.object(PrismHREmployee, "model_validate", wraps=validate) as validation:
            outputs = prismhr.normalize_employees(response(employee("001"), employee("002")), {},
                                                  client_id="00132")
        self.assertEqual(factory.call_count, 1)
        self.assertEqual(validation.call_count, 2)
        self.assertEqual([record["employee_id"] for record in outputs], ["001", "002"])
        outputs[0]["source_metadata"]["prismhr"]["response"]["errorMessage"] = "changed"
        self.assertEqual(outputs[1]["source_metadata"]["prismhr"]["response"]["errorMessage"], "")

    def test_missing_null_and_empty_employee_collections_return_empty_list(self):
        for supplied in ({}, {"employee": None}, {"employee": []}):
            with self.subTest(supplied=supplied), patch.object(prismhr, "MappingEngine") as factory:
                output = prismhr.normalize_employees(
                    {"errorCode": "0", "errorMessage": "", **supplied}, {}, client_id="00132")
                self.assertEqual(output, [])
                factory.assert_not_called()

    def test_invalid_employee_input_is_rejected_before_mapping(self):
        with patch.object(prismhr, "MappingEngine") as factory:
            with self.assertRaises(ValidationError):
                prismhr.normalize_employees(response(employee(), {}), {}, client_id="00132")
            factory.assert_not_called()

    def test_cli_writes_the_actual_adapter_result_as_json(self):
        with TemporaryDirectory() as folder:
            source = Path(folder) / "input.json"
            output = Path(folder) / "output.json"
            source.write_text(json.dumps(response(employee())))
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                code = main(["normalize", "--provider", "prismhr", "--entity", "employee",
                             "--input", str(source), "--output", str(output),
                             "--client-id", "00132"])
            self.assertEqual(code, 0, errors.getvalue())
            result = json.loads(output.read_text())
            self.assertEqual(result[0]["employee_id"], "0007")
            self.assertEqual(result[0]["birth_date"], "2000-01-02")
            self.assertEqual(result[0]["gender"], "female")
            self.assertTrue(output.read_text().endswith("\n"))

    def test_provider_failure_does_not_create_a_cli_output_file(self):
        with TemporaryDirectory() as folder:
            source = Path(folder) / "input.json"
            output = Path(folder) / "output.json"
            source.write_text(json.dumps({"errorCode": "1", "errorMessage": "Provider failure"}))
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                code = main(["normalize", "--provider", "prismhr", "--entity", "employee",
                             "--input", str(source), "--output", str(output),
                             "--client-id", "00132"])
            self.assertEqual(code, 1, errors.getvalue())
            self.assertIn("request failed", errors.getvalue())
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
