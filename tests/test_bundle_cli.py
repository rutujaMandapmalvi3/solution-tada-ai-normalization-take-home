"""End-to-end CLI: bundle in, canonical document out (replaces the per-entity flag tests)."""
import contextlib
import io
import json
from pathlib import Path

import pytest

from normalization.__main__ import main

FIXTURES = Path(__file__).parent / "fixtures"
PROVIDERS = ("prismhr", "isolved", "ukg-ready")


def run_cli(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(args))
    return code, err.getvalue()


@pytest.mark.parametrize("provider", PROVIDERS)
def test_fixture_bundle_matches_reviewed_expected_document(provider, tmp_path):
    output = tmp_path / "out.json"
    code, _ = run_cli("normalize", "--input", str(FIXTURES / f"{provider}.bundle.json"), "--output", str(output))
    assert code == 0
    assert json.loads(output.read_text()) == json.loads((FIXTURES / f"{provider}.expected.json").read_text())


@pytest.mark.parametrize("provider", ("isolved", "ukg-ready"))
def test_reference_pack_gaps_are_warnings_kept_in_the_document(provider, tmp_path):
    output = tmp_path / "out.json"
    code, err = run_cli("normalize", "--input", str(FIXTURES / f"{provider}.bundle.json"), "--output", str(output))
    assert code == 0 and err.startswith("Warning:")
    pack = json.loads(output.read_text())["source_metadata"][provider]["reference_pack"]
    assert pack["provider"] == provider and pack["warnings"]


def test_prismhr_has_no_reference_warnings(tmp_path):
    output = tmp_path / "out.json"
    run_cli("normalize", "--input", str(FIXTURES / "prismhr.bundle.json"), "--output", str(output))
    assert "reference_pack" not in json.loads(output.read_text())["source_metadata"]["prismhr"]


def test_existing_output_is_never_overwritten(tmp_path):
    output = tmp_path / "out.json"
    output.write_text("keep")
    code, err = run_cli("normalize", "--input", str(FIXTURES / "prismhr.bundle.json"), "--output", str(output))
    assert code == 1 and output.read_text() == "keep"


@pytest.mark.parametrize("bundle, message", [
    ({"responses": []}, "provider"),
    ({"provider": "prismhr"}, "responses"),
    ({"provider": "prismhr", "responses": [{"params": {}}]}, "endpoint"),
    ({"provider": "prismhr", "responses": [{"endpoint": "/employee/v1/getEmployee", "params": {"clientId": "1"},
                                            "body": {"errorCode": "9", "errorMessage": "denied"}}]}, "errorCode=9"),
])
def test_bad_bundles_exit_1_with_a_reason(bundle, message, tmp_path):
    source = tmp_path / "in.json"
    source.write_text(json.dumps(bundle))
    code, err = run_cli("normalize", "--input", str(source), "--output", str(tmp_path / "out.json"))
    assert code == 1 and message in err
    assert not (tmp_path / "out.json").exists()


def test_removed_flags_are_rejected():
    with pytest.raises(SystemExit):
        run_cli("normalize", "--input", "x", "--output", "y", "--client-id", "1")
