"""Owner context routing; readiness policy is unchanged and tested separately."""
import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from normalization.__main__ import main


class DirectDepositCliContextChecks(unittest.TestCase):
    def arguments(self, provider, source, output):
        return ['normalize', '--provider', provider, '--entity', 'direct_deposit',
                '--input', str(source), '--output', str(output)]

    def test_isolved_and_ukg_require_nonblank_employee_context_before_reading(self):
        for provider in ['isolved', 'ukg-ready']:
            for extra in [[], ['--employee-id', ''], ['--employee-id', ' ']]:
                with self.subTest(provider=provider, extra=extra), contextlib.redirect_stderr(io.StringIO()) as errors:
                    with self.assertRaises(SystemExit) as raised:
                        main(self.arguments(provider, 'missing.json', 'unused.json') + extra)
                    self.assertEqual(raised.exception.code, 2)
                    self.assertIn('--employee-id', errors.getvalue())

    def test_actual_adapters_write_json_when_readiness_is_isolated_in_test(self):
        for provider, payload in [('isolved', [{'id': 1, 'amount': 0.0}]),
                                  ('ukg-ready', {'deposits': [{'id': 1, 'amount': 10.0,
                                      'calc_method': {'type': 'FLAT_AMOUNT'}}], '_links': {}})]:
            with self.subTest(provider=provider), TemporaryDirectory() as folder:
                source = Path(folder) / 'input.json'
                output = Path(folder) / 'output.json'
                source.write_text(json.dumps(payload))
                # Reference readiness is deferred work. Only this test bypasses it;
                # source validation, YAML execution, canonical validation and output are real.
                with patch('normalization.__main__.readiness_issues', return_value=[]), \
                     patch('normalization.__main__.load_reference', return_value={}), \
                     contextlib.redirect_stderr(io.StringIO()) as errors:
                    code = main(self.arguments(provider, source, output) + ['--employee-id', '007'])
                self.assertEqual(code, 0, errors.getvalue())
                result = json.loads(output.read_text())
                self.assertEqual(result['employee_id'], '007')
                self.assertEqual(result['direct_deposits'][0]['employee_id'], '007')
                self.assertEqual(result['direct_deposits'][0]['deposit_id'], '1')
                self.assertEqual(result['direct_deposits'][0]['allocation_amount'],
                                 0.0 if provider == 'isolved' else 10.0)

    def test_reference_warnings_continue_to_missing_input_error(self):
        for provider in ['isolved', 'ukg-ready']:
            with self.subTest(provider=provider), TemporaryDirectory() as folder:
                output = Path(folder) / 'output.json'
                with contextlib.redirect_stderr(io.StringIO()) as errors:
                    code = main(self.arguments(provider, Path(folder) / 'missing.json', output)
                                + ['--employee-id', '007'])
                self.assertEqual(code, 1)
                self.assertIn('reference_warnings', errors.getvalue())
                self.assertFalse(output.exists())
