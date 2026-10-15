"""isolved deposits: native array mapping, employee link and source preservation."""
import copy
import json
import unittest

from bundle_helpers import ISOL, ISOL_EMPLOYEE, run_one

DEPOSITS = ISOL_EMPLOYEE + "/directdeposits"


def run(payload, **params):
    return run_one('isolved', DEPOSITS, payload, **{**ISOL, 'employeeId': '007', **params})


class DepositMappingChecks(unittest.TestCase):
    def test_requires_owner_param(self):
        with self.assertRaisesRegex(ValueError, 'cannot build direct_deposit id'):
            run_one('isolved', DEPOSITS, [{'id': 1}], **ISOL)

    def test_empty_input_produces_no_records(self):
        result = run([])
        self.assertEqual(result['direct_deposits'], [])

    def test_each_account_is_one_record(self):
        result = run([{'id': 1}, {'id': 2}])
        self.assertEqual(len(result['direct_deposits']), 2)

    def test_native_array_preserves_values_links_extras_and_input(self):
        payload = [{'id': 12, 'accountNumber': '000123', 'routingNumber': '001234567',
                    'accountType': 'Checking', 'amount': 0.0, 'percent': None,
                    'sequenceNumber': 0, 'status': 'Inactive', 'frequency': 'Every Pay',
                    'links': [{'href': '/synthetic/account', 'method': 'GET', 'future': False}],
                    'future': {'flag': False}},
                   {'id': 13, 'percent': 10.0, 'accountType': 'UNVERIFIED'}]
        before = copy.deepcopy(payload)
        result = run(payload)
        first, second = sorted(result['direct_deposits'], key=lambda r: r['deposit_id'])
        self.assertEqual(first['id'], 'isolved:direct_deposit:4000:1:007:12')
        self.assertEqual(first['employee_ref'], 'isolved:employee:4000:1:007')
        self.assertEqual(first['deposit_id'], '12')
        self.assertEqual(first['account_number'], '000123')
        self.assertEqual(first['routing_number'], '001234567')
        self.assertEqual(first['allocation_amount'], 0.0)
        self.assertEqual(first['sequence'], 0)
        self.assertEqual(first['account_type'], 'checking')
        self.assertEqual(first['provider_fields']['isolved']['unmapped']['links'][0]['href'], '/synthetic/account')
        self.assertIs(first['source_extras']['isolved']['future']['flag'], False)
        self.assertIs(first['source_extras']['isolved']['links'][0]['future'], False)
        self.assertEqual(second['allocation_percentage'], 10.0)
        self.assertEqual(second['source_metadata']['original_values']['accountType'], 'UNVERIFIED')
        self.assertEqual(first['employee_id'], '007')
        self.assertNotIn('wrapper', result['source_metadata']['isolved']['responses'][0])
        self.assertEqual(payload, before)
        json.dumps(result, allow_nan=False)

    def test_account_without_id_stops_the_run(self):
        # Policy: deposits need their own id; a null id is not replaced by an invented one.
        with self.assertRaisesRegex(ValueError, 'cannot build direct_deposit id'):
            run([{'id': None, 'percent': 10.0}])


if __name__ == '__main__':
    unittest.main()
