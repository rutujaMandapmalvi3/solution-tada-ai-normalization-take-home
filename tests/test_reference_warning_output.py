"""Reference metadata gaps warn and survive serialization; corrupt packs still block."""
import json
from unittest.mock import patch
import pytest
from normalization.__main__ import main


@pytest.mark.parametrize("provider,payload,entity", [
    ("isolved", {"id":7}, "company"),
    ("ukg-ready", {"items":[{"id":7}]}, "company"),
    ("isolved", {"results":[]}, "employee"),
    ("ukg-ready", {"employees":[]}, "employee"),
])
def test_actual_reference_gaps_warn_and_are_saved(tmp_path,capsys,provider,payload,entity):
    source=tmp_path/"input.json"; target=tmp_path/"output.json"
    source.write_text(json.dumps(payload))
    assert main(["normalize","--provider",provider,"--entity",entity,"--input",str(source),"--output",str(target)])==0
    saved=json.loads(target.read_text())
    pack=saved["source_metadata"][provider]["reference_pack"]
    assert pack["distribution_status"]=="user_approved_private_upload"
    assert "Candidate-distribution permission has not been verified." in pack["warnings"]
    assert "Warning:" in capsys.readouterr().err
    if provider=="ukg-ready":
        assert "OpenAPI artifact is absent or unverified." in pack["warnings"]


@pytest.mark.parametrize("issue",["Lookup reference must be a JSON object.",
    "Reference provider identifier does not match the folder.","Lookup domains must be an array.",
    "Cannot read reference metadata: invalid JSON", "Cannot read reference metadata: file missing"])
def test_operational_reference_errors_still_block(tmp_path,capsys,issue):
    target=tmp_path/"output.json"
    with patch("normalization.__main__.readiness_issues",return_value=[issue]):
        assert main(["normalize","--provider","isolved","--entity","company", "--input",str(tmp_path/"missing.json"),"--output",str(target)])==2
    assert not target.exists()
    assert issue in capsys.readouterr().err
