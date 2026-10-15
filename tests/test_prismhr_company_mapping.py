"""PrismHR company route: source-scoped identity, preserved wrapper and extras."""
import copy
import json
import unittest

from bundle_helpers import PRISM, only, run_one

CLIENT_MASTER = "/clientMaster/v1/getClientMaster"


class CompanyMappingChecks(unittest.TestCase):
    def test_wrapper_settings_extras_and_no_input_mutation(self):
        payload = {'errorCode': '0', 'errorMessage': '', 'extension': {'any': {'note': 'Retained'}},
                   'future_wrapper': False, 'clientMaster': {'id': '0007', 'legalName': 'Legal',
                   'clientName': 'Trade', 'federalIdNumber': '001234', 'statusClass': 'A',
                   'status': 'CUSTOM', 'future': {'flag': False}}}
        before = copy.deepcopy(payload)
        result = run_one('prismhr', CLIENT_MASTER, payload, clientId='0007')
        record = only(result, 'companies')
        self.assertEqual(record['id'], 'prismhr:company:0007')
        self.assertEqual(record['source_record_id'], '0007')
        self.assertEqual(record['source_record_type'], 'client')
        self.assertEqual(record['legal_name'], 'Legal')
        self.assertEqual(record['trade_name'], 'Trade')
        self.assertEqual(record['federal_tax_id'], '001234')
        self.assertEqual(record['provider_fields']['prismhr']['status_class'], 'active')
        self.assertEqual(record['provider_fields']['prismhr']['status'], 'CUSTOM')
        self.assertIs(record['source_extras']['prismhr']['future']['flag'], False)
        # Wrapper fields now live with the response in document metadata.
        self.assertEqual(result['source_metadata']['prismhr']['responses'][0]['wrapper'],
                         {k: v for k, v in before.items() if k != 'clientMaster'})
        self.assertEqual(payload, before)
        json.dumps(result, allow_nan=False)

    def test_empty_company_retains_wrapper(self):
        for extra in [{}, {'clientMaster': None}]:
            with self.subTest(extra=extra):
                result = run_one('prismhr', CLIENT_MASTER, {'errorCode': '0', 'errorMessage': '',
                                 'extension': {'any': {'note': 'Retained'}}, **extra}, **PRISM)
                self.assertEqual(result['companies'], [])
                self.assertEqual(result['source_metadata']['prismhr']['responses'][0]['wrapper']['extension'],
                                 {'any': {'note': 'Retained'}})

    def test_client_id_param_conflicting_with_record_stops_the_run(self):
        with self.assertRaisesRegex(ValueError, 'conflicts'):
            run_one('prismhr', CLIENT_MASTER, {'errorCode': '0', 'clientMaster': {'id': '7'}}, clientId='8')


if __name__ == '__main__':
    unittest.main()
