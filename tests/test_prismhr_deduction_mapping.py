"""PrismHR deduction route: selection, identity and source preservation."""
import copy
import json
import unittest

from bundle_helpers import PRISM, run_one

DEDUCTIONS = "/deductions/v1/getDeductions"


class DeductionMappingChecks(unittest.TestCase):
    def test_maps_section_and_preserves_amount_context_wrapper_and_extras(self):
        payload = {'errorCode': '0', 'errorMessage': '', 'extension': {'any': {'flag': False}},
            'future_wrapper': {'value': 0}, 'employeeDeductions': {
                'deduction': [{'deductionCode': '001', 'description': 'Example', 'amount': 10,
                    'usePercent': True, 'basis': 'M', 'matchMethod': 'P', 'matchAmount': 0,
                    'startDate': '2026-01-02', 'loanOrGarnishId': '0003', 'future': False}],
                'future_section': {'flag': False}}}
        before = copy.deepcopy(payload)
        result = run_one('prismhr', DEDUCTIONS, payload, **PRISM, employeeId='007')
        record = result['deductions'][0]
        self.assertEqual(record['id'], 'prismhr:deduction:001:007:001')
        self.assertEqual(record['employee_ref'], 'prismhr:employee:001:007')
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
        # Section siblings and wrapper fields are kept with the response metadata.
        wrapper = result['source_metadata']['prismhr']['responses'][0]['wrapper']
        self.assertIs(wrapper['employeeDeductions']['future_section']['flag'], False)
        self.assertEqual({k: v for k, v in wrapper.items() if k != 'employeeDeductions'},
                         {k: v for k, v in before.items() if k != 'employeeDeductions'})
        self.assertEqual(payload, before)
        json.dumps(result, allow_nan=False)

    def test_empty_sections_produce_no_records(self):
        for extra in [{}, {'employeeDeductions': None}, {'employeeDeductions': {}},
                      {'employeeDeductions': {'deduction': None}},
                      {'employeeDeductions': {'deduction': []}}]:
            with self.subTest(extra=extra):
                result = run_one('prismhr', DEDUCTIONS, {'errorCode': '0', 'errorMessage': '', **extra},
                                 **PRISM, employeeId='007')
                self.assertEqual(result['deductions'], [])

    def test_each_deduction_becomes_one_record(self):
        result = run_one('prismhr', DEDUCTIONS, {'errorCode': '0', 'errorMessage': '',
                         'employeeDeductions': {'deduction': [{'deductionCode': 'A'}, {'deductionCode': 'B'}]}},
                         **PRISM, employeeId='007')
        self.assertEqual(len(result['deductions']), 2)

    def test_employee_param_is_required(self):
        with self.assertRaisesRegex(ValueError, 'cannot build deduction id'):
            run_one('prismhr', DEDUCTIONS, {'errorCode': '0', 'employeeDeductions': {
                'deduction': [{'deductionCode': 'A'}]}}, **PRISM)


if __name__ == '__main__':
    unittest.main()
