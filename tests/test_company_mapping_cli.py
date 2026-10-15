"""Company CLI integration and unchanged reference-readiness behavior."""
import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from normalization.__main__ import main


class CompanyCliChecks(unittest.TestCase):
    def args(self, provider, source, output):
        return ['normalize', '--provider', provider, '--entity', 'company',
                '--input', str(source), '--output', str(output)]

    def test_prism_actual_cli_needs_no_additional_context_and_preserves_empty_metadata(self):
        with TemporaryDirectory() as folder:
            source, output = Path(folder) / 'input.json', Path(folder) / 'output.json'
            source.write_text(json.dumps({'errorCode': '0', 'errorMessage': '',
                'clientMaster': {'id': '007', 'legalName': 'Example'}, 'extension': {'any': {'flag': False}}}))
            with contextlib.redirect_stderr(io.StringIO()) as errors:
                code = main(self.args('prismhr', source, output))
            self.assertEqual(code, 0, errors.getvalue())
            result = json.loads(output.read_text())
            self.assertEqual(result['companies'][0]['source_record_id'], '007')
            self.assertEqual(result['companies'][0]['source_record_type'], 'client')
            self.assertIs(result['source_metadata']['prismhr']['response']['extension']['any']['flag'], False)

    def test_isolated_cli_uses_real_adapters_yaml_and_output(self):
        for provider, payload, kind in [('isolved', {'id': 7, 'legalName': 'Example'}, 'legal_company'),
                                       ('ukg-ready', {'items': [{'id': 7, 'ein_name': 'Example EIN'}]}, 'ein')]:
            with self.subTest(provider=provider), TemporaryDirectory() as folder:
                source, output = Path(folder) / 'input.json', Path(folder) / 'output.json'
                source.write_text(json.dumps(payload))
                # Only the known deferred readiness gate is isolated in this test.
                with patch('normalization.__main__.readiness_issues', return_value=[]), \
                     contextlib.redirect_stderr(io.StringIO()) as errors:
                    code = main(self.args(provider, source, output))
                self.assertEqual(code, 0, errors.getvalue())
                record = json.loads(output.read_text())['companies'][0]
                self.assertEqual(record['source_record_id'], '7')
                self.assertEqual(record['source_record_type'], kind)

    def test_reference_warnings_continue_to_missing_input_error(self):
        for provider in ['isolved', 'ukg-ready']:
            with self.subTest(provider=provider), TemporaryDirectory() as folder:
                output = Path(folder) / 'output.json'
                with contextlib.redirect_stderr(io.StringIO()) as errors:
                    code = main(self.args(provider, Path(folder) / 'missing.json', output))
                self.assertEqual(code, 1)
                self.assertIn('reference_warnings', errors.getvalue())
                self.assertFalse(output.exists())
