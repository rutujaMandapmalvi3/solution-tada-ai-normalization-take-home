"""PrismHR employee route: contract validation -> YAML engine -> CLI JSON."""
import contextlib
import copy
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from bundle_helpers import run_one
from normalization.__main__ import main

EMPLOYEE = "/employee/v1/getEmployee"


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


def bundle(payload, client_id="00132"):
    return {"provider": "prismhr", "responses": [
        {"endpoint": EMPLOYEE, "params": {"clientId": client_id}, "body": payload}]}


class PrismHREmployeeMappingChecks(unittest.TestCase):
    def test_records_are_json_ready_with_context_metadata_and_extras(self):
        payload = {**response(employee()), "infoMessage": ["Informational"],
                   "updateMessage": "Updated", "extension": {"any": {"note": "Retained"}},
                   "future_wrapper": {"value": 0}}
        before = copy.deepcopy(payload)
        result = run_one("prismhr", EMPLOYEE, payload, clientId="00132")
        self.assertEqual(len(result["employees"]), 1)
        output = result["employees"][0]
        self.assertEqual(output["provider"], "prismhr")
        self.assertEqual(output["id"], "prismhr:employee:00132:0007")
        self.assertEqual(output["company_ref"], "prismhr:company:00132")
        self.assertEqual(output["employee_id"], "0007")
        self.assertEqual(output["prismhr_client_id"], "00132")
        self.assertEqual(output["prismhr_employer_ids"], ["001"])  # live singular employerId renamed
        self.assertEqual(output["birth_date"], "2000-01-02")
        self.assertEqual(output["gender"], "female")
        self.assertEqual(output["marital_status"], "married")
        self.assertEqual(output["postal_code"], "02108-0123")
        self.assertEqual(output["hourly_rate"], 25.5)
        self.assertEqual(output["standard_hours_per_pay_period"], 0.0)
        self.assertIsNone(output["employment_type"])
        self.assertEqual(output["source_metadata"]["original_values"]["client.employeeType"], "FT")
        self.assertIs(output["source_extras"]["prismhr"]["person"]["future_flag"], False)
        wrapper = result["source_metadata"]["prismhr"]["responses"][0]["wrapper"]
        self.assertEqual(wrapper, {key: value for key, value in payload.items() if key != "employee"})
        self.assertNotIn("termination_date", output)
        self.assertEqual(payload, before)
        json.dumps(result, allow_nan=False)

    def test_each_employee_is_its_own_record(self):
        result = run_one("prismhr", EMPLOYEE, response(employee("001"), employee("002")), clientId="00132")
        self.assertEqual(sorted(record["employee_id"] for record in result["employees"]), ["001", "002"])

    def test_missing_null_and_empty_employee_collections_produce_no_records(self):
        for supplied in ({}, {"employee": None}, {"employee": []}):
            with self.subTest(supplied=supplied):
                result = run_one("prismhr", EMPLOYEE, {"errorCode": "0", "errorMessage": "", **supplied},
                                 clientId="00132")
                self.assertEqual(result["employees"], [])

    def test_employee_without_id_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "cannot build employee id"):
            run_one("prismhr", EMPLOYEE, response(employee(), {}), clientId="00132")

    def test_wrong_type_is_rejected_before_mapping(self):
        bad = {**employee(), "firstName": 5}
        with self.assertRaisesRegex(ValueError, "employee/0/firstName"):
            run_one("prismhr", EMPLOYEE, response(bad), clientId="00132")

    def test_cli_writes_the_actual_document_as_json(self):
        with TemporaryDirectory() as folder:
            source = Path(folder) / "input.json"
            output = Path(folder) / "output.json"
            source.write_text(json.dumps(bundle(response(employee()))))
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                code = main(["normalize", "--input", str(source), "--output", str(output)])
            self.assertEqual(code, 0, errors.getvalue())
            result = json.loads(output.read_text())
            self.assertEqual(result["employees"][0]["employee_id"], "0007")
            self.assertEqual(result["employees"][0]["birth_date"], "2000-01-02")
            self.assertEqual(result["employees"][0]["gender"], "female")
            self.assertTrue(output.read_text().endswith("\n"))

    def test_provider_failure_does_not_create_a_cli_output_file(self):
        with TemporaryDirectory() as folder:
            source = Path(folder) / "input.json"
            output = Path(folder) / "output.json"
            source.write_text(json.dumps(bundle({"errorCode": "1", "errorMessage": "Provider failure"})))
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                code = main(["normalize", "--input", str(source), "--output", str(output)])
            self.assertEqual(code, 1, errors.getvalue())
            self.assertIn("failed (errorCode=1)", errors.getvalue())
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
