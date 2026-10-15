"""Prism fixed allocation selection never discards other method amounts."""
import copy
import unittest
from importlib.resources import files
from pathlib import Path

from normalization.canonical_models.canonical_model_direct_deposit import CanonicalDirectDeposit
from normalization.helpers.mapping import conditional_number, validate_helper
from normalization.mapping_engine import MappingEngine, load_mapping_config
from normalization.source_models.prismhr.prismhr_source_model_direct_deposit import PrismHRAchVoucher


class PrismDirectDepositAmountChecks(unittest.TestCase):
    def engine(self):
        path = files('normalization').joinpath('mappings/prismhr/direct_deposit.yaml')
        return MappingEngine(load_mapping_config(Path(str(path))), PrismHRAchVoucher, CanonicalDirectDeposit)

    def test_fixed_amount_reuses_numeric_conversion(self):
        for value, expected in [(500, 500.0), ('500.25', 500.25), (0, 0.0), (-2, -2.0), (None, None)]:
            with self.subTest(value=value):
                converted = conditional_number(value, 'F', equals='F')
                self.assertEqual(converted.value, expected)
                self.assertIsNone(converted.issue)
        for value in [True, 'invalid', float('inf'), float('nan')]:
            with self.subTest(value=value):
                converted = conditional_number(value, 'F', equals='F')
                self.assertIsNone(converted.value)
                self.assertIsNotNone(converted.issue)

    def test_nonmatching_methods_do_not_produce_fixed_allocation(self):
        for method in ['P', 'PN', 'FS', 'B', 'unknown', 'f', '', None]:
            with self.subTest(method=method):
                self.assertIsNone(conditional_number(10, method, equals='F').value)

    def test_helper_configuration_requires_two_sources_and_text_condition(self):
        validate_helper('conditional_number', 2, {'equals': 'F'})
        for count, arguments in [(1, {'equals': 'F'}), (3, {'equals': 'F'}),
                                 (2, {}), (2, {'equals': True}),
                                 (2, {'equals': 'F', 'extra': 'unused'})]:
            with self.subTest(count=count, arguments=arguments), self.assertRaises(ValueError):
                validate_helper('conditional_number', count, arguments)

    def test_complete_yaml_preserves_percentage_amount_and_raw_method(self):
        payload = {'amount': 10, 'method': 'P', 'limit': 200}
        before = copy.deepcopy(payload)
        source = PrismHRAchVoucher.model_validate(payload)
        output = self.engine().map(source, context={'deposit_id': None, 'employee_id': '007'})
        self.assertIsNone(output.allocation_amount)
        preserved = output.provider_fields['prismhr']
        self.assertEqual(preserved['method_amount'], 10.0)
        self.assertEqual(preserved['ach_method'], 'percentage')
        self.assertEqual(preserved['percentage_method_limit'], 200.0)
        self.assertEqual(output.source_metadata.original_values['amount'], 10.0)
        self.assertEqual(output.source_metadata.original_values['method'], 'P')
        self.assertEqual(payload, before)
        self.assertEqual(source.amount, 10.0)
        self.assertEqual(source.method, 'P')
        self.assertEqual(output.model_dump(mode='json')['provider_fields']['prismhr']['method_amount'], 10.0)

    def test_fixed_zero_and_other_methods_keep_provider_amount(self):
        engine = self.engine()
        for method, amount, expected in [('F', 500, 500.0), ('F', 0, 0.0), ('FS', 500, None),
                                         ('PN', 10, None), ('B', None, None), ('unknown', 10, None)]:
            with self.subTest(method=method, amount=amount):
                output = engine.map(PrismHRAchVoucher.model_validate({'method': method, 'amount': amount}),
                                    context={'deposit_id': None})
                self.assertEqual(output.allocation_amount, expected)
                self.assertEqual(output.provider_fields['prismhr']['method_amount'], amount)
                self.assertEqual(output.source_metadata.original_values['method'], method)

    def test_missing_method_or_amount_is_not_invented(self):
        for payload in [{}, {'amount': 10}, {'method': 'F'}, {'amount': None, 'method': None}]:
            with self.subTest(payload=payload):
                output = self.engine().map(PrismHRAchVoucher.model_validate(payload), context={'deposit_id': None})
                self.assertIsNone(output.allocation_amount)
                dumped = output.model_dump(exclude_unset=True)
                self.assertEqual('allocation_amount' in dumped, bool(payload))
                for field in ['method', 'amount']:
                    self.assertEqual(field in output.source_metadata.original_values, field in payload)
