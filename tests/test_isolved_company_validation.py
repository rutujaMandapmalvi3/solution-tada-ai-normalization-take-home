"""isolved legal-company validation; mapping is connected."""
import copy
import unittest
from normalization.adapters import isolved


class IsolvedCompanyChecks(unittest.TestCase):
    def assert_valid(self, payload):
        before = copy.deepcopy(payload)
        result = isolved.normalize("company", payload, {})
        self.assertEqual(len(result["companies"]), 1)
        self.assertEqual(payload, before)

    def test_record_id_required_but_nullable_and_other_fields_optional(self):
        self.assert_valid({"id": 1})
        self.assert_valid({"id": None, "legalName": None, "client": None})
        for payload in [None, [], {}, {"id": []}, {"id": 1, "legalName": []}]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                isolved.normalize("company", payload, {})

    def test_nested_client_and_company_records_are_validated(self):
        payload = {"id": 1, "legalName": "Synthetic", "client": {
            "id": 2, "clientName": "Synthetic client", "legalCompanies": [{"id": 3}]},
            "compensationPlans": [{"id": 4, "code": "source-code"}],
            "legalAddress": {"city": "Synthetic", "zipCode": "00001"}}
        self.assert_valid(payload)
        for field, value in [("client", {}), ("compensationPlans", [{}]),
                             ("legalAddress", {"city": []}), ("payGroups", [{}])]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                isolved.normalize("company", {**payload, field: value}, {})
        payload["client"]["legalCompanies"].append({})
        with self.assertRaises(ValueError):
            isolved.normalize("company", payload, {})

    def test_optional_collections_and_unknown_fields(self):
        self.assert_valid({"id": 1, "workLocations": [], "payGroups": None,
                           "services": [], "futureField": {"test": 0}})
        self.assert_valid({"id": 1, "workLocations": [{"id": None, "address1": None}]})


if __name__ == "__main__":
    unittest.main()
