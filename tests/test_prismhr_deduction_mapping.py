"""Deduction adapter selection, identity and source preservation."""
import copy
import json
import unittest
from unittest.mock import patch
from normalization.adapters import prismhr as adapter
from normalization.mapping_engine import MappingEngine


class DeductionMappingChecks(unittest.TestCase):
    def test_maps_section_and_preserves_amount_context_wrapper_and_extras(self):
        payload = {'errorCode': '0', 'errorMessage': '', 'extension': {'any': {'flag': False}},
            'future_wrapper': {'value': 0}, 'employeeDeductions': {
                'deduction': [{'deductionCode': '001', 'description': 'Example', 'amount': 10,
                    'usePercent': True, 'basis': 'M', 'matchMethod': 'P', 'matchAmount': 0,
                    'startDate': '2026-01-02', 'loanOrGarnishId': '0003', 'future': False}],
                'future_section': {'flag': False}}}
        before = copy.deepcopy(payload)
        result = adapter.normalize('deduction', payload, {}, employee_id='007')
        record = result['deductions'][0]
        self.assertIsNone(record['deduction_id'])
        self.assertEqual(record['employee_id'], '007')
        self.assertEqual(record['deduction_code'], '001')
        self.assertEqual(record['start_date'], '2026-01-02')
        fields = record['provider_fields']['prismhr']
        self.assertEqual(fields['amount'], 10.0)
        self.assertIs(fields['use_percent'], True)
        self.assertEqual(fields['maximum_basis'], 'monthly')
        self.assertEqual(fields['match_amount'], 0.0)
        self.assertEqual(fields['loan_or_garnish_id'], '0003')
        self.assertIs(record['source_extras']['prismhr']['future'], False)
        self.assertIs(result['source_extras']['prismhr']['employeeDeductions']['future_section']['flag'], False)
        self.assertEqual(result['source_metadata']['prismhr']['response'],
                         {k: v for k, v in before.items() if k != 'employeeDeductions'})
        self.assertEqual(payload, before)
        json.dumps(result, allow_nan=False)

    def test_empty_sections_preserve_absence_null_empty_and_metadata(self):
        for extra in [{}, {'employeeDeductions': None}, {'employeeDeductions': {}},
                      {'employeeDeductions': {'deduction': None}},
                      {'employeeDeductions': {'deduction': []}}]:
            with self.subTest(extra=extra), patch.object(adapter, 'MappingEngine') as factory:
                result = adapter.normalize('deduction', {'errorCode': '0', 'errorMessage': '', **extra}, {}, employee_id='007')
                self.assertEqual(result['deductions'], [])
                factory.assert_not_called()
                remaining = result['provider_fields'].get('prismhr', {}).get('unmapped', {})
                self.assertEqual(remaining, extra)

    def test_source_validation_and_engine_are_not_repeated(self):
        validate = adapter.PrismHRDeductionResponse.model_validate
        with patch.object(adapter.PrismHRDeductionResponse, 'model_validate', wraps=validate) as validation, \
             patch.object(adapter.PrismHREmployeeDeductionsDeduction, 'model_validate') as repeated, \
             patch.object(adapter, 'MappingEngine', wraps=MappingEngine) as factory:
            result = adapter.normalize('deduction', {'errorCode': '0', 'errorMessage': '',
                'employeeDeductions': {'deduction': [{}, {}]}}, {}, employee_id='007')
        self.assertEqual(validation.call_count, 1)
        repeated.assert_not_called()
        self.assertEqual(factory.call_count, 1)
        self.assertEqual(len(result['deductions']), 2)
