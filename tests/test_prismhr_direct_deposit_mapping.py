"""PrismHR deposits: getEmployee accounts -> direct_deposit records linked to the employee."""
import contextlib
import copy
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from bundle_helpers import PRISM, codes, run_one
from normalization.__main__ import main

EMPLOYEE = "/employee/v1/getEmployee"


def response(accounts=None):
    return {'errorCode': '0', 'errorMessage': '', 'employee': [{
        'id': '007', 'firstName': 'Example', 'directDeposit': {
            'achStatus': 'A', 'voucherType': 'RVS', 'suppressAccountPrint': False,
            'directDepositChecksum': 'synthetic', 'achVoucher': accounts,
        },
    }]}


def account(method='F', amount=500, number='000123'):
    return {'accountNum': number, 'transitNum': '001234567', 'accountType': 'S',
            'method': method, 'amount': amount, 'status': 'D', 'bankName': 'Example'}


def bundle(payload):
    return {'provider': 'prismhr', 'responses': [
        {'endpoint': EMPLOYEE, 'params': {**PRISM, 'employeeId': '007'}, 'body': payload}]}


class PrismDirectDepositMappingChecks(unittest.TestCase):
    def test_maps_accounts_and_preserves_wrapper_setup_extras_and_input(self):
        # Distinct account numbers: the account identifies the deposit record.
        payload = response([account(), {**account('P', 10, '000124'), 'future_account_flag': False}])
        payload.update(infoMessage=['Informational'], updateMessage='Updated',
                       extension={'any': {'note': 'Preserved'}}, future_wrapper={'value': 0})
        payload['employee'][0]['future_employee'] = {'value': None}
        payload['employee'][0]['directDeposit']['future_setup'] = {'flag': False}
        before = copy.deepcopy(payload)
        result = run_one('prismhr', EMPLOYEE, payload, **PRISM, employeeId='007')
        self.assertEqual(len(result['direct_deposits']), 2)
        fixed, percent = sorted(result['direct_deposits'], key=lambda r: r['account_number'])
        for record in [fixed, percent]:
            self.assertEqual(record['employee_id'], '007')
            self.assertEqual(record['employee_ref'], 'prismhr:employee:001:007')
            self.assertIsNone(record['deposit_id'])
            self.assertEqual(record['routing_number'], '001234567')
            self.assertEqual(record['account_type'], 'savings')
        self.assertEqual(fixed['id'], 'prismhr:direct_deposit:001:007:001234567:000123')
        self.assertEqual(fixed['allocation_amount'], 500.0)
        self.assertIsNone(percent['allocation_amount'])
        self.assertEqual(percent['provider_fields']['prismhr']['method_amount'], 10.0)
        self.assertEqual(percent['source_metadata']['original_values']['method'], 'P')
        self.assertIs(percent['source_extras']['prismhr']['future_account_flag'], False)
        self.assertEqual(percent['source_metadata']['prismhr']['sources'][0]['path'],
                         'employee/0/directDeposit/achVoucher/1')
        # Employee-level setup and parent fields now belong to the employee record.
        employee = result['employees'][0]
        self.assertEqual(employee['first_name'], 'Example')
        setup = employee['provider_fields']['prismhr']['direct_deposit']
        self.assertEqual(setup['ach_status'], 'A')
        self.assertEqual(setup['voucher_type'], 'RVS')
        self.assertIs(setup['suppress_account_print'], False)
        self.assertNotIn('achVoucher', json.dumps(employee))
        self.assertEqual(employee['source_extras']['prismhr']['future_employee'], {'value': None})
        self.assertIs(employee['source_extras']['prismhr']['directDeposit']['future_setup']['flag'], False)
        self.assertEqual(result['source_metadata']['prismhr']['responses'][0]['wrapper'],
                         {key: value for key, value in before.items() if key != 'employee'})
        self.assertEqual(payload, before)
        json.dumps(result, allow_nan=False)

    def test_missing_null_or_empty_accounts_produce_no_deposits(self):
        for supplied in [{}, {'employee': None}, {'employee': []},
                         {'employee': [{'id': '007'}]},
                         {'employee': [{'id': '007', 'directDeposit': None}]},
                         {'employee': response([])['employee']},
                         {'employee': response(None)['employee']}]:
            with self.subTest(supplied=supplied):
                result = run_one('prismhr', EMPLOYEE, {'errorCode': '0', 'errorMessage': '', **supplied},
                                 **PRISM, employeeId='007')
                self.assertEqual(result['direct_deposits'], [])
                self.assertEqual(len(result['employees']), len(supplied.get('employee') or []))

    def test_employee_param_conflicting_with_response_stops_the_run(self):
        payload = response([account()])
        payload['employee'].append({'id': 'different', 'directDeposit': None})
        with self.assertRaisesRegex(ValueError, 'conflicts'):
            run_one('prismhr', EMPLOYEE, payload, **PRISM, employeeId='007')

    def test_each_account_is_one_record(self):
        result = run_one('prismhr', EMPLOYEE, response([account(), account('P', 10, '000124')]),
                         **PRISM, employeeId='007')
        self.assertEqual(len(result['direct_deposits']), 2)
        self.assertNotIn('merge_conflict', codes(result))

    def test_cli_actual_mapping_and_no_overwrite(self):
        with TemporaryDirectory() as folder:
            source = Path(folder) / 'input.json'
            output = Path(folder) / 'output.json'
            source.write_text(json.dumps(bundle(response([account('P', 10)]))))
            args = ['normalize', '--input', str(source), '--output', str(output)]
            with contextlib.redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(main(args), 0, errors.getvalue())
            original = output.read_text()
            result = json.loads(original)
            self.assertEqual(result['direct_deposits'][0]['employee_id'], '007')
            self.assertEqual(result['direct_deposits'][0]['provider_fields']['prismhr']['method_amount'], 10.0)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(args), 1)
            self.assertEqual(output.read_text(), original)

    def test_cli_conflict_does_not_create_output(self):
        with TemporaryDirectory() as folder:
            source = Path(folder) / 'input.json'
            output = Path(folder) / 'output.json'
            data = bundle(response([account()]))
            data['responses'][0]['params']['employeeId'] = 'different'
            source.write_text(json.dumps(data))
            with contextlib.redirect_stderr(io.StringIO()) as errors:
                code = main(['normalize', '--input', str(source), '--output', str(output)])
            self.assertEqual(code, 1)
            self.assertIn('conflicts', errors.getvalue())
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
