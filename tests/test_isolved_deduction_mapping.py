"""isolved pay items: Deduction selection, identity and source preservation."""
import copy
import json
import unittest

from bundle_helpers import ISOL, ISOL_EMPLOYEE, run_one

PAY_ITEMS = ISOL_EMPLOYEE + "/payItems"


def run(payload, employee_id='7'):
    return run_one('isolved', PAY_ITEMS, payload, **ISOL, employeeId=employee_id)


class DeductionMappingChecks(unittest.TestCase):
    def test_only_exact_deduction_type_is_selected_and_other_records_survive(self):
        payload = [{'id': 1, 'employeeId': 7, 'payItemType': 'Deduction', 'payItemName': 'Example',
                    'payItemCode': '001', 'calcParams': [{'paramType': 'Amount2', 'paramValue': 10}],
                    'links': [{'href': '/synthetic/item'}], 'balance': 0, 'future': False},
                   {'id': 2, 'employeeId': 99, 'payItemType': 'Earning', 'future': {'flag': False}},
                   {'id': 3, 'payItemType': 'Memo Calc'}, {'id': 4},
                   {'id': 5, 'payItemType': None}, {'id': 6, 'payItemType': 'deduction'}]
        before = copy.deepcopy(payload)
        result = run(payload)
        self.assertEqual(len(result['deductions']), 1)
        record = result['deductions'][0]
        self.assertEqual(record['id'], 'isolved:deduction:4000:1:7:1')
        self.assertEqual(record['employee_ref'], 'isolved:employee:4000:1:7')
        self.assertEqual(record['deduction_id'], '1')
        self.assertEqual(record['employee_id'], '7')
        self.assertEqual(record['deduction_name'], 'Example')
        fields = record['provider_fields']['isolved']
        self.assertEqual(fields['calc_params'], [{'param_type': 'Amount2', 'param_value': 10.0}])
        self.assertEqual(fields['pay_item_code'], '001')
        self.assertEqual(fields['balance'], 0)  # live-only field (contracts.LIVE_FIELDS)
        self.assertEqual(fields['unmapped']['links'][0]['href'], '/synthetic/item')
        self.assertIs(record['source_extras']['isolved']['future'], False)
        # Non-deduction items are kept verbatim as filtered records with their position.
        other = result['provider_fields']['isolved']['filtered_records']
        self.assertEqual([item['record']['id'] for item in other], [2, 3, 4, 5, 6])
        self.assertEqual([item['path'] for item in other], ['1', '2', '3', '4', '5'])
        self.assertEqual(other[0]['record']['employeeId'], 99)
        self.assertIs(other[0]['record']['future']['flag'], False)
        self.assertEqual(payload, before)
        json.dumps(result, allow_nan=False)

    def test_missing_owner_uses_params_but_conflicting_owner_fails(self):
        for fields in [{}, {'employeeId': None}, {'employeeId': 7}]:
            with self.subTest(fields=fields):
                result = run([{'id': 1, 'payItemType': 'Deduction', **fields}])
                self.assertEqual(result['deductions'][0]['employee_id'], '7')
        with self.assertRaisesRegex(ValueError, 'conflicts'):
            run([{'id': 1, 'payItemType': 'Deduction', 'employeeId': 8}])

    def test_no_selected_records_preserves_input_without_fake_deduction(self):
        payload = [{'id': 1, 'payItemType': 'Earning', 'calcParams': [{'paramValue': 0}]}]
        result = run(payload)
        self.assertEqual(result['deductions'], [])
        self.assertEqual([item['record'] for item in result['provider_fields']['isolved']['filtered_records']],
                         payload)

    def test_mixed_records_map_only_deductions(self):
        result = run([{'id': 1, 'payItemType': 'Deduction'}, {'id': 2, 'payItemType': 'Earning'}])
        self.assertEqual([record['deduction_id'] for record in result['deductions']], ['1'])


if __name__ == '__main__':
    unittest.main()
