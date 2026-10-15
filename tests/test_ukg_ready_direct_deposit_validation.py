"""UKG Ready direct deposit validation; mapping is connected."""
import copy
import unittest
from normalization.adapters import ukg_ready


class UKGReadyDirectDepositValidationChecks(unittest.TestCase):
    def assert_valid(self, entity, payload):
        before = copy.deepcopy(payload)
        result = ukg_ready.normalize(entity, payload, {}, employee_id="007")
        self.assertIsInstance(result["direct_deposits"], list)
        self.assertEqual(payload, before)

    def test_direct_deposit_wrapper_accounts_and_aliases(self):
        payload = {"deposits": [{"id": 1, "account_number": "0001", "amount": 0.0}],
                   "_links": {}, "_total_count": 1}
        self.assert_valid("direct_deposit", payload)
        self.assertEqual(ukg_ready.normalize("direct_deposit", {"deposits": [], "_links": {}}, {}, employee_id="007")["direct_deposits"], [])
        for bad in [{"deposits": []}, {"_links": {}},
                    {"deposits": [{}], "_links": {}},
                    {"deposits": [{"id": None}], "_links": {}},
                    {"deposits": [{"id": 1, "amount": []}], "_links": {}},
                    {"deposits": [], "_links": "wrong"}]:
            with self.subTest(payload=bad), self.assertRaises(ValueError):
                ukg_ready.normalize("direct_deposit", bad, {}, employee_id="007")

