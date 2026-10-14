"""UKG Ready company validation; mapping is pending."""
import copy
import unittest
from normalization.adapters import ukg_ready


class UKGReadyCompanyValidationChecks(unittest.TestCase):
    def assert_valid(self, entity, payload):
        before = copy.deepcopy(payload)
        with self.assertRaisesRegex(NotImplementedError, "source validation passed"):
            ukg_ready.normalize(entity, payload, {})
        self.assertEqual(payload, before)

    def test_company_ein_lookup_wrapper_and_records(self):
        self.assert_valid("company", {"items": [{"id": 1, "ein_name": "Synthetic", "ein_tax_id": "00001"}]})
        self.assertEqual(ukg_ready.normalize("company", {"items": []}, {}), [])
        for payload in [{}, {"items": None}, {"items": [{}]},
                        {"items": [{"id": 1}, {"id": None}]},
                        {"items": [{"id": 1, "ein_name": []}]}]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                ukg_ready.normalize("company", payload, {})

