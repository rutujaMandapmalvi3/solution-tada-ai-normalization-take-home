"""isolved deduction validation; mapping is connected."""
import copy
import unittest
from normalization.adapters import isolved


class IsolvedDeductionChecks(unittest.TestCase):
    def assert_valid(self, payload):
        before = copy.deepcopy(payload)
        result = isolved.normalize("deduction", payload, {}, employee_id="007")
        self.assertIsInstance(result["deductions"], list)
        self.assertEqual(payload, before)

    def test_valid_partial_records_nullable_id_and_empty_list(self):
        self.assertEqual(isolved.normalize("deduction", [], {}, employee_id="007")["deductions"], [])
        self.assert_valid([{"id": 1}, {"id": None, "balance": None}])
        self.assert_valid([{"id": 1, "calcParams": [{"paramType": "source", "paramValue": 0.0}],
                            "balance": 0, "payItemName": None}])

    def test_optional_nested_fields(self):
        for params in [None, [], [{}]]:
            self.assert_valid([{"id": 1, "calcParams": params}])

    def test_invalid_shapes_missing_ids_and_nested_types(self):
        for payload in [None, {}, {"results": []}, [{}], [{"id": 1}, {}],
                        [{"id": 1, "calcParams": "wrong"}],
                        [{"id": 1, "calcParams": [{"paramValue": []}]}],
                        [{"id": 1, "balance": []}]]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                isolved.normalize("deduction", payload, {}, employee_id="007")


if __name__ == "__main__":
    unittest.main()
