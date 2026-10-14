"""Request client context for PrismHR employee normalization."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError

from normalization.__main__ import main
from normalization.adapters import prismhr
from normalization.canonical_models.canonical_model_employee import (
    PrismHREmployee,
)


class ClientIdChecks(unittest.TestCase):
    def test_cli_rejects_missing_or_blank_client_id_before_reading_input(self):
        args = ["normalize", "--provider", "prismhr", "--entity", "employee",
                "--input", "missing.json", "--output", "output.json"]
        for extra in ([], ["--client-id", ""], ["--client-id", "   "]):
            with self.subTest(extra=extra), contextlib.redirect_stderr(io.StringIO()) as errors:
                with self.assertRaises(SystemExit) as raised:
                    main(args + extra)
                self.assertEqual(raised.exception.code, 2)
                self.assertIn("--client-id", errors.getvalue())

    def test_cli_passes_client_id_unchanged_and_writes_adapter_result(self):
        with tempfile.TemporaryDirectory() as folder:
            input_path = Path(folder) / "input.json"
            output_path = Path(folder) / "output.json"
            response = {"errorCode": "0", "errorMessage": "", "employee": []}
            input_path.write_text(json.dumps(response))
            with patch.object(prismhr, "normalize", return_value=[]) as normalize:
                code = main(["normalize", "--provider", "prismhr", "--entity", "employee",
                             "--input", str(input_path), "--output", str(output_path),
                             "--client-id", "00132"])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output_path.read_text()), [])
            self.assertEqual(normalize.call_args.args[:2], ("employee", response))
            self.assertEqual(normalize.call_args.kwargs, {"client_id": "00132"})

    def test_adapter_forwards_client_id_to_employee_helper(self):
        response = {"employee": []}
        with patch.object(prismhr, "normalize_employees", return_value=[]) as helper:
            self.assertEqual(prismhr.normalize("employee", response, {}, client_id="00132"), [])
        helper.assert_called_once_with(response, {}, client_id="00132")

    def test_direct_employee_calls_require_nonblank_client_id(self):
        for function in (prismhr.normalize_employees,
                         lambda response, reference, **kwargs: prismhr.normalize(
                             "employee", response, reference, **kwargs)):
            for client_id in (None, "", "   ", 132):
                with self.subTest(function=function, client_id=client_id):
                    with self.assertRaisesRegex(ValueError, "nonblank client_id"):
                        function({}, {}, client_id=client_id)

    def test_other_entity_keeps_original_call_signature(self):
        with tempfile.TemporaryDirectory() as folder:
            input_path = Path(folder) / "input.json"
            output_path = Path(folder) / "output.json"
            input_path.write_text("{}")
            with patch.object(prismhr, "normalize", return_value={}) as normalize:
                self.assertEqual(main(["normalize", "--provider", "prismhr", "--entity", "company",
                                       "--input", str(input_path), "--output", str(output_path)]), 0)
            self.assertEqual(len(normalize.call_args.args), 3)
            self.assertEqual(normalize.call_args.kwargs, {})

    def test_other_provider_does_not_require_client_id(self):
        with patch("normalization.__main__.readiness_issues", return_value=["reference issue"]):
            with contextlib.redirect_stderr(io.StringIO()) as errors:
                code = main(["normalize", "--provider", "isolved", "--entity", "employee",
                             "--input", "missing.json", "--output", "output.json"])
        self.assertEqual(code, 2)
        self.assertIn("reference issue", errors.getvalue())

    def test_canonical_employee_requires_source_client_id(self):
        fields = dict(employee_id="E1", first_name="Test", last_name="Employee",
                      middle_name="", preferred_name="")
        with self.assertRaises(ValidationError):
            PrismHREmployee.model_validate(fields)
        employee = PrismHREmployee.model_validate({**fields, "source_client_id": "00132"})
        self.assertEqual(employee.source_client_id, "00132")


if __name__ == "__main__":
    unittest.main()
