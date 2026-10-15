"""PrismHR deduction setup source validation; mapping is connected."""
import copy
import unittest

from normalization.adapters import prismhr


def response(records=None):
    return {"errorCode": "0", "errorMessage": "",
            "employeeDeductions": {"deduction": [] if records is None else records}}


def deduction():
    return {"deductionCode": "synthetic", "amount": 0.0, "period": "12345"}


class DeductionValidationChecks(unittest.TestCase):
    def assert_valid(self, payload):
        before = copy.deepcopy(payload)
        result = prismhr.normalize("deduction", payload, {}, employee_id="007")
        self.assertIsInstance(result["deductions"], list)
        self.assertEqual(payload, before)

    def test_valid_records_and_empty_collection(self):
        self.assertEqual(prismhr.normalize("deduction", response(), {}, employee_id="007")["deductions"], [])
        self.assert_valid(response([deduction(), deduction()]))
        self.assert_valid(response([{}]))

    def test_requires_wrapper_fields(self):
        for field in ["errorCode", "errorMessage"]:
            payload = response()
            del payload[field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                prismhr.normalize_deductions(payload, {}, employee_id="007")

    def test_provider_errors_do_not_become_empty_success(self):
        for code in ["1", "NOT_FOUND"]:
            with self.subTest(code=code), self.assertRaisesRegex(ValueError, "request failed"):
                prismhr.normalize_deductions({"errorCode": code, "errorMessage": "test"}, {}, employee_id="007")

    def test_success_accepts_missing_null_and_empty_deduction_data(self):
        for payload in [
            {"errorCode": "0", "errorMessage": ""},
            {"errorCode": "0", "errorMessage": "", "employeeDeductions": None},
            {"errorCode": "0", "errorMessage": "", "employeeDeductions": {}},
            {"errorCode": "0", "errorMessage": "", "employeeDeductions": {"deduction": None}},
        ]:
            with self.subTest(payload=payload):
                before = copy.deepcopy(payload)
                self.assertEqual(prismhr.normalize("deduction", payload, {}, employee_id="007")["deductions"], [])
                self.assertEqual(payload, before)

    def test_invalid_shapes_and_each_record_are_validated(self):
        for payload in [None, [], {**response(), "employeeDeductions": "invalid"},
                        response([deduction(), {"deductionCode": []}]),
                        response([{**deduction(), "amount": []}])]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                prismhr.normalize_deductions(payload, {}, employee_id="007")

    def test_nullable_extension_and_optional_record_fields(self):
        self.assert_valid({**response([{**deduction(), "description": None, "limit": None}]),
                           "extension": None})
        self.assert_valid({**response([deduction()]), "extension": {"any": {"note": "synthetic"}}})
        with self.assertRaises(ValueError):
            prismhr.normalize_deductions({**response(), "extension": []}, {}, employee_id="007")


if __name__ == "__main__":
    unittest.main()
