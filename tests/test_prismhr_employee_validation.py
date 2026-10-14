"""PrismHR employee validation; canonical mapping is pending."""
import copy
import unittest
from normalization.adapters import prismhr


def employee_response():
    return {
        "errorCode": "0", "errorMessage": "",
        "employee": [{"id": "synthetic", "firstName": "Test", "lastName": "Employee",
                      "middleInitial": "", "preferredName": "", "directDeposit": None}],
    }


class EmployeeWrapperChecks(unittest.TestCase):
    def test_accepts_populated_informational_fields_without_mutating_input(self):
        payload = {**employee_response(), "infoMessage": ["test"],
                   "updateMessage": "test", "extension": {"any": {"note": "test"}}}
        original = copy.deepcopy(payload)
        prismhr.normalize_employees(payload, {}, client_id="00132")
        self.assertEqual(payload, original)

    def test_rejects_invalid_informational_field_types(self):
        for field, value in [("infoMessage", "wrong"), ("updateMessage", []),
                             ("extension", "wrong")]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                prismhr.normalize_employees(
                    {**employee_response(), field: value}, {}, client_id="00132")

    def test_rejects_provider_errors_despite_informational_fields(self):
        for code in ["1", "NOT_FOUND"]:
            with self.subTest(code=code), self.assertRaisesRegex(ValueError, "request failed"):
                prismhr.normalize_employees(
                    {**employee_response(), "errorCode": code, "infoMessage": ["test"],
                     "extension": {"any": {"note": "test"}}}, {}, client_id="00132")

