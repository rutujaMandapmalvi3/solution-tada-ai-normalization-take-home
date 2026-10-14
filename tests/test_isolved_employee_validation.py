"""isolved employee source validation; canonical mapping is pending."""
import copy
import unittest

from normalization.adapters import isolved


def employee():
    return {"id": 1, "employmentCategoryCode": "source-category", "employmentStatus": "source-status",
            "hireDate": "2026-10-14", "legalCode": "001", "payFrequency": 0,
            "payGroup": "source-group", "payType": "source-type",
            "ssn": "synthetic", "workLocation": "source-location"}


def salary():
    return {"id": 1, "effectiveDate": "2026-10-14", "frequency": {"id": 0},
            "payGroup": {"id": None}, "payType": {"id": None}, "hourlyRate": 0.0}


class IsolvedEmployeeValidationChecks(unittest.TestCase):
    def assert_valid(self, payload):
        before = copy.deepcopy(payload)
        with self.assertRaisesRegex(NotImplementedError, "source validation passed"):
            isolved.normalize("employee", payload, {})
        self.assertEqual(payload, before)

    def test_detail_and_paged_employees_preserve_source(self):
        self.assert_valid(employee())
        self.assert_valid({"results": [employee(), employee()], "totalItems": 2,
                           "totalPages": 1.0, "nextPageUrl": None})

    def test_empty_optional_collections_return_empty_list(self):
        for payload in [[], {"results": []}, {"results": None}, {"totalItems": 0}]:
            with self.subTest(payload=payload):
                self.assertEqual(isolved.normalize("employee", payload, {}), [])

    def test_detail_requires_record_id_but_accepts_partial_record(self):
        self.assert_valid({"id": 1})
        self.assert_valid({"id": None, "annualSalary": None})
        payload = employee()
        del payload["id"]
        with self.assertRaises(ValueError):
            isolved.normalize_employees(payload, {})
        with self.assertRaises(ValueError):
            isolved.normalize_employees({"id": 1, "annualSalary": []}, {})

    def test_rejects_invalid_detail_and_list_shapes(self):
        for payload in [None, "wrong", {}, {"results": "wrong"},
                        {"results": [employee(), {}]}, {"totalItems": []}]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                isolved.normalize_employees(payload, {})

    def test_salary_history_validates_each_record(self):
        self.assert_valid([salary(), salary()])
        for payload in [[salary(), {}], [{**salary(), "frequency": "wrong"}]]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                isolved.normalize_employees(payload, {})

    def test_nested_deposit_record_id_and_optional_sequence_types(self):
        deposit = {"id": None, "accountNumber": "0001", "accountType": "source-type",
                   "frequency": "source-frequency", "routingNumber": "001234567",
                   "sequenceNumber": None, "status": "source-status"}
        payload = {**employee(), "directDeposits": [deposit]}
        self.assert_valid(payload)
        for field, value in [("sequenceNumber", []), ("accountNumber", [])]:
            invalid = copy.deepcopy(payload)
            invalid["directDeposits"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                isolved.normalize_employees(invalid, {})
        del payload["directDeposits"][0]["sequenceNumber"]
        self.assert_valid(payload)
        del payload["directDeposits"][0]["id"]
        with self.assertRaises(ValueError):
            isolved.normalize_employees(payload, {})

    def test_optional_sections_and_unknown_fields_remain_accepted(self):
        self.assert_valid({**employee(), "directDeposits": None, "futureField": {"test": 0}})
        self.assert_valid({**employee(), "directDeposits": [], "idType": None})


    def test_combined_employee_and_salary_history(self):
        payload = {"id": 1, "birthDate": "1990-01-01",
                   "salary_history": [{"id": 10, "seasons": [
                       {"id": 2, "description": "Summer", "isSelected": True}]}]}
        self.assert_valid(payload)
        self.assert_valid({"results": [payload], "totalItems": 1})
        from normalization.source_models.isolved.isolved_source_model_employee import IsolvedEmployeeInput
        validated = IsolvedEmployeeInput.model_validate(payload)
        self.assertEqual(validated.salary_history[0].seasons[0].description, "Summer")

    def test_combined_salary_history_validates_nested_ids_and_types(self):
        invalid_histories = [
            "wrong", [{}], [{"id": 10, "seasons": [{}]}],
            [{"id": 10, "seasons": [{"id": 2, "isSelected": []}]}],
            [{"id": 10, "perPaySalary": []}],
        ]
        for history in invalid_histories:
            payload = {"id": 1, "birthDate": "1990-01-01", "salary_history": history}
            for response in [payload, {"results": [payload]}]:
                with self.subTest(response=response), self.assertRaises(ValueError):
                    isolved.normalize("employee", response, {})

    def test_combined_salary_history_is_optional_and_separates_conflicting_fields(self):
        for history in [None, []]:
            self.assert_valid({"id": 1, "salary_history": history})
        self.assert_valid({
            "id": 1, "payGroup": "employee-group", "payType": "employee-type",
            "salary_history": [{"id": 10, "payGroup": {"id": 3},
                                "payType": {"id": "salary-type"}}],
        })


if __name__ == "__main__":
    unittest.main()
