"""Company adapter integration with source-scoped identity and preserved context."""
import copy
import json
import unittest
from unittest.mock import patch
from normalization.adapters import prismhr as adapter
from normalization.mapping_engine import MappingEngine


class CompanyMappingChecks(unittest.TestCase):
    def test_wrapper_settings_extras_and_no_input_mutation(self):
        payload = {'errorCode': '0', 'errorMessage': '', 'extension': {'any': {'note': 'Retained'}},
                   'future_wrapper': False, 'clientMaster': {'id': '0007', 'legalName': 'Legal',
                   'clientName': 'Trade', 'federalIdNumber': '001234', 'statusClass': 'A',
                   'status': 'CUSTOM', 'future': {'flag': False}}}
        before = copy.deepcopy(payload)
        result = adapter.normalize('company', payload, {})
        record = result['companies'][0]
        self.assertEqual(record['source_record_id'], '0007')
        self.assertEqual(record['source_record_type'], 'client')
        self.assertEqual(record['legal_name'], 'Legal')
        self.assertEqual(record['trade_name'], 'Trade')
        self.assertEqual(record['federal_tax_id'], '001234')
        self.assertEqual(record['provider_fields']['prismhr']['status_class'], 'active')
        self.assertEqual(record['provider_fields']['prismhr']['status'], 'CUSTOM')
        self.assertIs(record['source_extras']['prismhr']['future']['flag'], False)
        self.assertEqual(result['source_metadata']['prismhr']['response'],
                         {k: v for k, v in before.items() if k != 'clientMaster'})
        self.assertEqual(payload, before)
        json.dumps(result, allow_nan=False)

    def test_empty_company_retains_wrapper_and_does_not_create_engine(self):
        for extra in [{}, {'clientMaster': None}]:
            with self.subTest(extra=extra), patch.object(adapter, 'MappingEngine') as engine:
                result = adapter.normalize('company', {'errorCode': '0', 'errorMessage': '',
                    'extension': {'any': {'note': 'Retained'}}, **extra}, {})
                self.assertEqual(result['companies'], [])
                self.assertEqual(result['source_metadata']['prismhr']['response']['extension'],
                                 {'any': {'note': 'Retained'}})
                engine.assert_not_called()

    def test_validates_once_and_does_not_repeat_client_source_validation(self):
        validate = adapter.PrismHRGetClientMasterResponse.model_validate
        with patch.object(adapter.PrismHRGetClientMasterResponse, 'model_validate', wraps=validate) as validation, \
             patch.object(adapter.PrismHRClientMaster, 'model_validate') as repeated:
            adapter.normalize('company', {'errorCode': '0', 'errorMessage': '', 'clientMaster': {'id': '7'}}, {})
        self.assertEqual(validation.call_count, 1)
        repeated.assert_not_called()
