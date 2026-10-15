"""Native-array deposit mapping and source preservation."""
import copy
import json
import unittest
from unittest.mock import patch
from normalization.adapters import isolved as adapter
from normalization.mapping_engine import MappingEngine


class DepositMappingChecks(unittest.TestCase):
    def test_requires_owner_context(self):
        for value in [None, '', '  ', 7]:
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'nonblank employee_id'):
                adapter.normalize('direct_deposit', [], {}, employee_id=value)

    def test_empty_input_skips_engine_and_retains_result(self):
        with patch.object(adapter, 'MappingEngine') as factory:
            result = adapter.normalize('direct_deposit', [], {}, employee_id='007')
        self.assertEqual(result['employee_id'], '007')
        self.assertEqual(result['direct_deposits'], [])
        factory.assert_not_called()

    def test_one_response_validation_and_engine_per_input(self):
        validator = adapter.IsolvedEmployeeDirectDepositResponse.model_validate
        with patch.object(adapter.IsolvedEmployeeDirectDepositResponse, 'model_validate', wraps=validator) as validation, \
             patch.object(adapter.IsolvedEmployeeDirectDepositModel, 'model_validate') as again, \
             patch.object(adapter, 'MappingEngine', wraps=MappingEngine) as factory:
            result = adapter.normalize('direct_deposit', [{'id': 1}, {'id': 2}], {}, employee_id='007')
        self.assertEqual(validation.call_count, 1)
        again.assert_not_called()
        self.assertEqual(factory.call_count, 1)
        self.assertEqual(len(result['direct_deposits']), 2)

    def test_native_array_preserves_values_links_extras_and_input(self):
        payload = [{'id': 12, 'accountNumber': '000123', 'routingNumber': '001234567',
                    'accountType': 'Checking', 'amount': 0.0, 'percent': None,
                    'sequenceNumber': 0, 'status': 'Inactive', 'frequency': 'Every Pay',
                    'links': [{'href': '/synthetic/account', 'method': 'GET', 'future': False}],
                    'future': {'flag': False}},
                   {'id': None, 'percent': 10.0, 'accountType': 'UNVERIFIED'}]
        before = copy.deepcopy(payload)
        result = adapter.normalize('direct_deposit', payload, {}, employee_id='007')
        first, second = result['direct_deposits']
        self.assertEqual(first['deposit_id'], '12')
        self.assertEqual(first['account_number'], '000123')
        self.assertEqual(first['routing_number'], '001234567')
        self.assertEqual(first['allocation_amount'], 0.0)
        self.assertEqual(first['sequence'], 0)
        self.assertEqual(first['account_type'], 'checking')
        self.assertEqual(first['provider_fields']['isolved']['unmapped']['links'][0]['href'], '/synthetic/account')
        self.assertIs(first['source_extras']['isolved']['future']['flag'], False)
        self.assertIs(first['source_extras']['isolved']['links'][0]['future'], False)
        self.assertIsNone(second['deposit_id'])
        self.assertEqual(second['allocation_percentage'], 10.0)
        self.assertEqual(second['source_metadata']['original_values']['accountType'], 'UNVERIFIED')
        self.assertEqual(first['employee_id'], '007')
        self.assertNotIn('response', result.get('source_metadata', {}))
        self.assertEqual(payload, before)
        json.dumps(result, allow_nan=False)
