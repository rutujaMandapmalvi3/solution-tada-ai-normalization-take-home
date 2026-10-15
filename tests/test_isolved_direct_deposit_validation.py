"""isolved account setup validation; canonical mapping is connected."""
import copy
import unittest

from normalization.adapters import isolved


class IsolvedDirectDepositChecks(unittest.TestCase):
    def assert_valid(self, payload):
        before = copy.deepcopy(payload)
        result = isolved.normalize("direct_deposit", payload, {}, employee_id="007")
        self.assertIsInstance(result["direct_deposits"], list)
        self.assertEqual(payload, before)

    def test_valid_accounts_preserve_identifiers_zero_values_and_input(self):
        self.assert_valid([{"id": 1, "accountNumber": "00001",
                            "routingNumber": "001234567", "amount": 0.0,
                            "percent": 0.0, "sequenceNumber": None}])

    def test_empty_account_list_returns_empty_list(self):
        self.assertEqual(isolved.normalize("direct_deposit", [], {}, employee_id="007")["direct_deposits"], [])

    def test_requires_record_id_and_retains_nullable_id_policy(self):
        self.assert_valid([{"id": 1}, {"id": None}])
        with self.assertRaises(ValueError):
            isolved.normalize_direct_deposits([{"accountNumber": "00001"}], {}, employee_id="007")

    def test_rejects_invalid_response_shapes_and_every_invalid_record(self):
        for payload in [None, {}, {"results": []}, "wrong", [None],
                        [{"id": 1}, {"id": []}],
                        [{"id": 1}, {"id": 2, "amount": []}]]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                isolved.normalize_direct_deposits(payload, {}, employee_id="007")

    def test_optional_fields_links_and_extras(self):
        self.assert_valid([{"id": 1, "accountNumber": None, "amount": None,
                            "links": [{"href": "synthetic", "method": None}],
                            "futureField": {"note": "test"}}])
        self.assert_valid([{"id": 1, "links": []}])
        with self.assertRaises(ValueError):
            isolved.normalize_direct_deposits(
                [{"id": 1, "links": [{"href": []}]}], {}, employee_id="007")


if __name__ == "__main__":
    unittest.main()
