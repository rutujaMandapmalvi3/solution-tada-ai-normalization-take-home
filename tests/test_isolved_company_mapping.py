"""isolved company route: legals list -> legal-company records with source-scoped identity."""
import copy
import json
import unittest

from bundle_helpers import ISOL_LEGALS, only, run_one


class CompanyMappingChecks(unittest.TestCase):
    def test_legal_root_parent_and_nested_records_keep_separate_identity(self):
        legal = {'id': 7, 'legalName': 'Root Legal', 'dbaName': 'Trade', 'federalEIN': '001234',
                 'client': {'id': 8, 'clientName': 'Parent', 'legalCompanies': [
                     {'id': 9, 'legalName': 'Nested', 'future': False}]},
                 'links': [{'href': '/synthetic/legal', 'method': 'GET'}], 'future': {'flag': False}}
        payload = [legal]
        before = copy.deepcopy(payload)
        result = run_one('isolved', ISOL_LEGALS, payload, clientId='4000')
        record = only(result, 'companies')
        self.assertEqual(record['id'], 'isolved:company:4000:7')
        self.assertEqual(record['source_record_id'], '7')
        self.assertEqual(record['source_record_type'], 'legal_company')
        self.assertEqual(record['legal_name'], 'Root Legal')
        self.assertEqual(record['trade_name'], 'Trade')
        parent = record['provider_fields']['isolved']['client']
        self.assertEqual(parent['id'], '8')
        self.assertEqual(parent['legal_companies'][0]['id'], '9')
        self.assertEqual(record['provider_fields']['isolved']['unmapped']['client']['legalCompanies'][0]['legalName'], 'Nested')
        self.assertEqual(record['provider_fields']['isolved']['unmapped']['links'][0]['href'], '/synthetic/legal')
        self.assertIs(record['source_extras']['isolved']['future']['flag'], False)
        self.assertEqual(payload, before)
        # A list body has no wrapper fields to keep.
        self.assertNotIn('wrapper', result['source_metadata']['isolved']['responses'][0])
        json.dumps(result, allow_nan=False)

    def test_null_source_identity_stops_the_run_instead_of_inventing_one(self):
        # Policy: a record key that is missing has no fallback for companies.
        with self.assertRaisesRegex(ValueError, 'cannot build company id'):
            run_one('isolved', ISOL_LEGALS, [{'id': None, 'legalName': None}], clientId='4000')

    def test_null_business_values_stay_null(self):
        record = only(run_one('isolved', ISOL_LEGALS, [{'id': 7, 'legalName': None}], clientId='4000'),
                      'companies')
        self.assertIsNone(record['legal_name'])


if __name__ == '__main__':
    unittest.main()
