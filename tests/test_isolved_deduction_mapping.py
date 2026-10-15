"""Deduction adapter selection, identity and source preservation."""
import copy
import json
import unittest
from unittest.mock import patch
from normalization.adapters import isolved as adapter
from normalization.mapping_engine import MappingEngine


class DeductionMappingChecks(unittest.TestCase):
    def test_only_exact_deduction_type_is_selected_and_other_records_survive(self):
        payload = [{'id': 1, 'employeeId': 7, 'payItemType': 'Deduction', 'payItemName': 'Example',
                    'payItemCode': '001', 'calcParams': [{'paramType': 'Amount2', 'paramValue': 10}],
                    'links': [{'href': '/synthetic/item'}], 'balance': 0, 'future': False},
                   {'id': 2, 'employeeId': 99, 'payItemType': 'Earning', 'future': {'flag': False}},
                   {'id': 3, 'payItemType': 'Memo Calc'}, {'id': 4},
                   {'id': 5, 'payItemType': None}, {'id': 6, 'payItemType': 'deduction'}]
        before = copy.deepcopy(payload)
        result = adapter.normalize('deduction', payload, {}, employee_id='7')
        self.assertEqual(len(result['deductions']), 1)
        record = result['deductions'][0]
        self.assertEqual(record['deduction_id'], '1')
        self.assertEqual(record['employee_id'], '7')
        self.assertEqual(record['deduction_name'], 'Example')
        fields = record['provider_fields']['isolved']
        self.assertEqual(fields['calc_params'], [{'param_type': 'Amount2', 'param_value': 10.0}])
        self.assertEqual(fields['pay_item_code'], '001')
        self.assertEqual(fields['balance'], 0)
        self.assertEqual(fields['unmapped']['links'][0]['href'], '/synthetic/item')
        self.assertIs(record['source_extras']['isolved']['future'], False)
        other = result['provider_fields']['isolved']['non_deduction_items']
        self.assertEqual([item['id'] for item in other], [2, 3, 4, 5, 6])
        self.assertEqual(other[0]['employeeId'], 99)
        self.assertEqual(result['source_metadata']['isolved']['non_deduction_source_indexes'], [1, 2, 3, 4, 5])
        self.assertIs(result['source_extras']['isolved']['records'][1]['future']['flag'], False)
        self.assertEqual(payload, before)
        json.dumps(result, allow_nan=False)

    def test_missing_owner_uses_context_but_conflicting_owner_fails_before_mapping(self):
        for fields in [{}, {'employeeId': None}, {'employeeId': 7}]:
            with self.subTest(fields=fields):
                result = adapter.normalize('deduction', [{'id': 1, 'payItemType': 'Deduction', **fields}], {}, employee_id='7')
                self.assertEqual(result['deductions'][0]['employee_id'], '7')
        with patch.object(adapter, 'MappingEngine') as factory, self.assertRaisesRegex(ValueError, 'conflicts'):
            adapter.normalize('deduction', [{'id': 1, 'payItemType': 'Deduction', 'employeeId': 8}], {}, employee_id='7')
        factory.assert_not_called()

    def test_no_selected_records_preserves_input_without_engine_or_fake_deduction(self):
        payload = [{'id': 1, 'payItemType': 'Earning', 'calcParams': [{'paramValue': 0}]}]
        with patch.object(adapter, 'MappingEngine') as factory:
            result = adapter.normalize('deduction', payload, {}, employee_id='7')
        self.assertEqual(result['deductions'], [])
        self.assertEqual(result['provider_fields']['isolved']['non_deduction_items'], payload)
        factory.assert_not_called()

    def test_source_validation_once_even_with_mixed_records(self):
        validate = adapter.IsolvedEmployeePayItemResponse.model_validate
        with patch.object(adapter.IsolvedEmployeePayItemResponse, 'model_validate', wraps=validate) as validation, \
             patch.object(adapter.IsolvedEmployeePayItemModel, 'model_validate') as repeated:
            adapter.normalize('deduction', [{'id': 1, 'payItemType': 'Deduction'},
                                            {'id': 2, 'payItemType': 'Earning'}], {}, employee_id='7')
        self.assertEqual(validation.call_count, 1)
        repeated.assert_not_called()
