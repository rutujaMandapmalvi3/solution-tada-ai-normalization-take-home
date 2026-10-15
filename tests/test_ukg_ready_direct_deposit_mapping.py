"""UKG account mapping with preserved destination types and wrapper metadata."""
import copy
import json
import unittest
from unittest.mock import patch

from bundle_helpers import UKG, UKG_CO, only, run_one
from normalization import contracts, pipeline
from normalization.mapping_engine import MappingEngine

DEPOSITS = UKG_CO + "/employees/{aid}/direct-deposits"


class DepositMappingChecks(unittest.TestCase):
    def test_requires_owner_param(self):
        # Previously the --employee-id flag; now params.aid builds the id and employee_ref.
        with self.assertRaisesRegex(ValueError, 'cannot build direct_deposit id'):
            run_one("ukg-ready", DEPOSITS, {'deposits': [{'id': 1}], '_links': {}}, **UKG)

    def test_empty_input_maps_nothing_and_keeps_wrapper(self):
        result = run_one("ukg-ready", DEPOSITS, {'deposits': [], '_links': {}}, **UKG, aid="007")
        self.assertEqual(result['direct_deposits'], [])
        self.assertEqual(result['source_metadata']['ukg-ready']['responses'][0]['wrapper'], {'_links': {}})

    def test_one_validation_and_engine_per_input(self):
        with patch.object(contracts, 'validate', wraps=contracts.validate) as validation, \
             patch.object(pipeline, 'MappingEngine', wraps=MappingEngine) as factory:
            result = run_one("ukg-ready", DEPOSITS, {'deposits': [{'id': 1}, {'id': 2}], '_links': {}},
                             **UKG, aid="007")
        self.assertEqual(validation.call_count, 1)
        self.assertEqual(factory.call_count, 1)
        self.assertEqual(len(result['direct_deposits']), 2)

    def test_flat_and_percentage_values_types_wrappers_and_links_are_preserved(self):
        payload = {'deposits': [
            {'id': 12, 'account_number': '000123', 'routing_number': '001234567', 'account_type': 'CHECKING',
             'amount': 500.0, 'calc_method': {'type': 'FLAT_AMOUNT', 'display_name': 'Flat Amount'},
             'type': 'DIRECT_DEPOSIT', 'active': False, '_links': {'self': '/synthetic/deposit'},
             'payroll_frequency': {'holiday_profile': {'id': 3}}, 'future_flag': False},
            {'id': 13, 'amount': 10.0, 'percentage': 5.0, 'calc_method': {'type': 'GROSS_EARNING'},
             'type': 'RESERVE_LIVE_CHECK'}], '_links': {'self': '/synthetic/deposits'},
             '_total_count': 2, '_routing_type': 'ABA', 'future_wrapper': {'flag': False}}
        before = copy.deepcopy(payload)
        result = run_one("ukg-ready", DEPOSITS, payload, **UKG, aid="007")
        fixed, other = result['direct_deposits']
        self.assertEqual(fixed['id'], 'ukg-ready:direct_deposit:001:007:12')
        self.assertEqual(fixed['employee_ref'], 'ukg-ready:employee:001:007')
        self.assertEqual(fixed['employee_id'], '007')
        self.assertEqual(fixed['deposit_id'], '12')
        self.assertEqual(fixed['allocation_amount'], 500.0)
        self.assertEqual(fixed['account_number'], '000123')
        self.assertEqual(fixed['account_type'], 'checking')
        fields = fixed['provider_fields']['ukg-ready']
        self.assertIs(fields['active'], False)
        self.assertEqual(fields['payroll_frequency']['holiday_profile']['id'], '3')
        self.assertEqual(fields['unmapped']['_links']['self'], '/synthetic/deposit')
        self.assertIs(fixed['source_extras']['ukg-ready']['future_flag'], False)
        self.assertIsNone(other['allocation_amount'])
        self.assertEqual(other['provider_fields']['ukg-ready']['amount'], 10.0)
        self.assertEqual(other['provider_fields']['ukg-ready']['percentage'], 5.0)
        self.assertEqual(other['provider_fields']['ukg-ready']['type'], 'RESERVE_LIVE_CHECK')
        self.assertEqual(other['source_metadata']['original_values']['calc_method.type'], 'GROSS_EARNING')
        self.assertEqual(result['source_metadata']['ukg-ready']['responses'][0]['wrapper'],
                         {k: v for k, v in before.items() if k != 'deposits'})
        self.assertEqual(payload, before)
        json.dumps(result, allow_nan=False)

    def test_empty_wrapper_metadata_and_unknown_methods_are_retained(self):
        payload = {'deposits': [], '_links': {'self': '/synthetic'}, 'future': False}
        result = run_one("ukg-ready", DEPOSITS, payload, **UKG, aid="007")
        self.assertEqual(result['source_metadata']['ukg-ready']['responses'][0]['wrapper'],
                         {'_links': {'self': '/synthetic'}, 'future': False})
        for method in [None, {}, {'type': 'UNVERIFIED'}]:
            with self.subTest(method=method):
                result = run_one("ukg-ready", DEPOSITS, {'deposits': [
                    {'id': 1, 'amount': 10, 'calc_method': method}], '_links': {}}, **UKG, aid="007")
                deposit = only(result, 'direct_deposits')
                self.assertIsNone(deposit['allocation_amount'])
                self.assertEqual(deposit['provider_fields']['ukg-ready']['amount'], 10.0)
