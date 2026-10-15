"""Prism deposit mapping: validated envelope -> account YAML -> result -> CLI JSON."""
import contextlib
import copy
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from normalization.__main__ import main
from normalization.adapters import prismhr
from normalization.canonical_models.canonical_model_direct_deposit import CanonicalDirectDepositResult
from normalization.mapping_engine import MappingEngine


def response(accounts=None):
    return {'errorCode': '0', 'errorMessage': '', 'employee': [{
        'id': '007', 'firstName': 'Example', 'directDeposit': {
            'achStatus': 'A', 'voucherType': 'RVS', 'suppressAccountPrint': False,
            'directDepositChecksum': 'synthetic', 'achVoucher': accounts,
        },
    }]}


def account(method='F', amount=500):
    return {'accountNum': '000123', 'transitNum': '001234567', 'accountType': 'S',
            'method': method, 'amount': amount, 'status': 'D', 'bankName': 'Example'}


class PrismDirectDepositMappingChecks(unittest.TestCase):
    def test_maps_accounts_and_preserves_wrapper_setup_extras_and_input(self):
        payload = response([account(), {**account('P', 10), 'future_account_flag': False}])
        payload.update(infoMessage=['Informational'], updateMessage='Updated',
                       extension={'any': {'note': 'Preserved'}}, future_wrapper={'value': 0})
        payload['employee'][0]['future_employee'] = {'value': None}
        payload['employee'][0]['directDeposit']['future_setup'] = {'flag': False}
        before = copy.deepcopy(payload)
        result = prismhr.normalize('direct_deposit', payload, {}, employee_id='007')
        CanonicalDirectDepositResult.model_validate(result)
        self.assertEqual(len(result['direct_deposits']), 2)
        fixed, percent = result['direct_deposits']
        for record in [fixed, percent]:
            self.assertEqual(record['employee_id'], '007')
            self.assertIsNone(record['deposit_id'])
            self.assertEqual(record['account_number'], '000123')
            self.assertEqual(record['routing_number'], '001234567')
            self.assertEqual(record['account_type'], 'savings')
        self.assertEqual(fixed['allocation_amount'], 500.0)
        self.assertIsNone(percent['allocation_amount'])
        self.assertEqual(percent['provider_fields']['prismhr']['method_amount'], 10.0)
        self.assertEqual(percent['source_metadata']['original_values']['method'], 'P')
        self.assertIs(percent['source_extras']['prismhr']['future_account_flag'], False)
        self.assertEqual(percent['source_metadata']['prismhr']['source_location'],
                         {'employee_index': 0, 'ach_voucher_index': 1})
        parent = result['provider_fields']['prismhr']['unmapped']['employee'][0]
        self.assertEqual(parent['firstName'], 'Example')
        setup = parent['directDeposit']
        self.assertEqual(setup['achStatus'], 'A')
        self.assertEqual(setup['voucherType'], 'RVS')
        self.assertIs(setup['suppressAccountPrint'], False)
        self.assertNotIn('achVoucher', setup)
        outer_extras = result['source_extras']['prismhr']['employee'][0]
        self.assertEqual(outer_extras['future_employee'], {'value': None})
        self.assertIs(outer_extras['directDeposit']['future_setup']['flag'], False)
        self.assertEqual(result['source_metadata']['prismhr']['response'],
                         {key: value for key, value in before.items() if key != 'employee'})
        self.assertEqual(payload, before)
        json.dumps(result, allow_nan=False)

    def test_empty_records_preserve_distinct_setup_and_employee_inputs(self):
        for supplied in [{}, {'employee': None}, {'employee': []},
                         {'employee': [{'id': '007'}]},
                         {'employee': [{'id': '007', 'directDeposit': None}]},
                         {'employee': response([])['employee']},
                         {'employee': response(None)['employee']}]:
            payload = {'errorCode': '0', 'errorMessage': '', **supplied}
            with self.subTest(supplied=supplied), patch.object(prismhr, 'MappingEngine') as engine:
                result = prismhr.normalize_direct_deposits(payload, {}, employee_id='007')
                self.assertEqual(result['direct_deposits'], [])
                engine.assert_not_called()
                remaining = result['provider_fields'].get('prismhr', {}).get('unmapped', {})
                self.assertEqual('employee' in remaining, 'employee' in supplied)
                if 'employee' in supplied:
                    self.assertEqual(remaining['employee'], supplied['employee'])

    def test_context_is_required_and_conflicts_do_not_map(self):
        for owner in [None, '', '   ', 7]:
            with self.subTest(owner=owner), self.assertRaisesRegex(ValueError, 'nonblank employee_id'):
                prismhr.normalize_direct_deposits(response([]), {}, employee_id=owner)
        payload = response([account()])
        payload['employee'].append({'id': 'different', 'directDeposit': None})
        with patch.object(prismhr, 'MappingEngine') as engine, self.assertRaisesRegex(ValueError, 'conflicts'):
            prismhr.normalize_direct_deposits(payload, {}, employee_id='007')
        engine.assert_not_called()

    def test_one_source_validation_and_one_engine_for_all_accounts(self):
        validate = prismhr.PrismHRDirectDepositResponse.model_validate
        with patch.object(prismhr.PrismHRDirectDepositResponse, 'model_validate', wraps=validate) as validation, \
             patch.object(prismhr.PrismHRAchVoucher, 'model_validate') as repeat_validation, \
             patch.object(prismhr, 'MappingEngine', wraps=MappingEngine) as engine:
            result = prismhr.normalize_direct_deposits(response([account(), account('P', 10)]), {}, employee_id='007')
        self.assertEqual(validation.call_count, 1)
        repeat_validation.assert_not_called()
        self.assertEqual(engine.call_count, 1)
        self.assertEqual(len(result['direct_deposits']), 2)

    def test_cli_requires_context_before_reading_input(self):
        args = ['normalize', '--provider', 'prismhr', '--entity', 'direct_deposit',
                '--input', 'missing.json', '--output', 'unused.json']
        for extra in [[], ['--employee-id', ''], ['--employee-id', ' ']]:
            with self.subTest(extra=extra), contextlib.redirect_stderr(io.StringIO()) as errors:
                with self.assertRaises(SystemExit) as raised:
                    main(args + extra)
                self.assertEqual(raised.exception.code, 2)
                self.assertIn('--employee-id', errors.getvalue())

    def test_cli_actual_mapping_and_no_overwrite(self):
        with TemporaryDirectory() as folder:
            source = Path(folder) / 'input.json'
            output = Path(folder) / 'output.json'
            source.write_text(json.dumps(response([account('P', 10)])))
            args = ['normalize', '--provider', 'prismhr', '--entity', 'direct_deposit',
                    '--input', str(source), '--output', str(output), '--employee-id', '007']
            with contextlib.redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(main(args), 0, errors.getvalue())
            original = output.read_text()
            result = json.loads(original)
            self.assertEqual(result['employee_id'], '007')
            self.assertEqual(result['direct_deposits'][0]['provider_fields']['prismhr']['method_amount'], 10.0)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(args), 1)
            self.assertEqual(output.read_text(), original)

    def test_cli_conflict_does_not_create_output(self):
        with TemporaryDirectory() as folder:
            source = Path(folder) / 'input.json'
            output = Path(folder) / 'output.json'
            source.write_text(json.dumps(response([account()])))
            with contextlib.redirect_stderr(io.StringIO()) as errors:
                code = main(['normalize', '--provider', 'prismhr', '--entity', 'direct_deposit',
                             '--input', str(source), '--output', str(output), '--employee-id', 'different'])
            self.assertEqual(code, 1)
            self.assertIn('conflicts', errors.getvalue())
            self.assertFalse(output.exists())
