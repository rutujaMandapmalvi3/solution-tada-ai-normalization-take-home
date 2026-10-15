"""Deduction CLI routing, owner requirements and unchanged reference gates."""
import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from normalization.__main__ import main


class DeductionCliChecks(unittest.TestCase):
    def args(self, provider, source, output):
        return ['normalize', '--provider', provider, '--entity', 'deduction',
                '--input', str(source), '--output', str(output)]

    def test_all_providers_require_nonblank_owner_before_input(self):
        for provider in ['prismhr', 'isolved', 'ukg-ready']:
            for extra in [[], ['--employee-id', ''], ['--employee-id', ' ']]:
                with self.subTest(provider=provider, extra=extra), contextlib.redirect_stderr(io.StringIO()) as errors:
                    with self.assertRaises(SystemExit) as raised:
                        main(self.args(provider, 'missing.json', 'unused.json') + extra)
                    self.assertEqual(raised.exception.code, 2)
                    self.assertIn('--employee-id', errors.getvalue())

    def test_cli_actual_mapping_and_source_preservation(self):
        cases = [('prismhr', {'errorCode': '0', 'errorMessage': '', 'employeeDeductions': {
                    'deduction': [{'deductionCode': '001', 'amount': 10}]}}, '7'),
                 ('isolved', [{'id': 1, 'employeeId': 7, 'payItemType': 'Deduction'},
                              {'id': 2, 'payItemType': 'Earning'}], '7'),
                 ('ukg-ready', {'assignments': {'deductions': [{'id': 1}]},
                                'code_lookup': {'items': [{'id': 2}]}}, '007')]
        for provider, payload, owner in cases:
            with self.subTest(provider=provider), TemporaryDirectory() as folder:
                source, output = Path(folder) / 'input.json', Path(folder) / 'output.json'
                source.write_text(json.dumps(payload))
                # Prism uses real readiness; other providers' gates are isolated only in this integration test.
                with contextlib.ExitStack() as stack:
                    if provider != 'prismhr':
                        stack.enter_context(patch('normalization.__main__.readiness_issues', return_value=[]))
                    errors = stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
                    code = main(self.args(provider, source, output) + ['--employee-id', owner])
                self.assertEqual(code, 0, errors.getvalue())
                result = json.loads(output.read_text())
                self.assertEqual(result['employee_id'], owner)
                self.assertEqual(len(result['deductions']), 1)
                self.assertEqual(result['deductions'][0]['employee_id'], owner)
                if provider == 'isolved':
                    self.assertEqual(result['provider_fields']['isolved']['non_deduction_items'][0]['id'], 2)
                if provider == 'ukg-ready':
                    self.assertEqual(result['provider_fields']['ukg-ready']['code_lookup']['items'][0]['id'], 2)

    def test_isolved_owner_conflict_does_not_write_output(self):
        with TemporaryDirectory() as folder:
            source, output = Path(folder) / 'input.json', Path(folder) / 'output.json'
            source.write_text(json.dumps([{'id': 1, 'employeeId': 8, 'payItemType': 'Deduction'}]))
            with patch('normalization.__main__.readiness_issues', return_value=[]), \
                 contextlib.redirect_stderr(io.StringIO()) as errors:
                code = main(self.args('isolved', source, output) + ['--employee-id', '7'])
            self.assertEqual(code, 1)
            self.assertIn('conflicts', errors.getvalue())
            self.assertFalse(output.exists())

    def test_reference_warnings_do_not_hide_missing_input(self):
        for provider in ['isolved', 'ukg-ready']:
            with self.subTest(provider=provider), TemporaryDirectory() as folder:
                output = Path(folder) / 'output.json'
                with contextlib.redirect_stderr(io.StringIO()) as errors:
                    code = main(self.args(provider, Path(folder) / 'missing.json', output) + ['--employee-id', '7'])
                self.assertEqual(code, 1)
                self.assertIn('reference_warnings', errors.getvalue())
                self.assertFalse(output.exists())
