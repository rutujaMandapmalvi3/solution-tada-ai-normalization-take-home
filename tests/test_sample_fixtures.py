"""Exercise all 15 saved fixtures through the real CLI and real reference packs."""
import json
from pathlib import Path
import pytest
from normalization.__main__ import main

FIXTURES=Path(__file__).parent/"fixtures"
CASES=json.loads((FIXTURES/"manifest.json").read_text())


@pytest.mark.parametrize("case",CASES,ids=[c["provider"]+"-"+c["entity"] for c in CASES])
def test_cli_matches_reviewed_fixture(case,tmp_path,capsys):
    folder=FIXTURES/case["provider"]/case["entity"]
    source=folder/"input.json"
    before=source.read_bytes()
    output=tmp_path/"output.json"
    argv=["normalize","--provider",case["provider"],"--entity",case["entity"],
          "--input",str(source),"--output",str(output)]
    for name,value in case["context"].items():
        argv.extend(["--"+name.replace("_","-"),value])
    assert main(argv)==0,capsys.readouterr().err
    assert json.loads(output.read_text())==json.loads((folder/"expected.json").read_text())
    assert source.read_bytes()==before


def test_fixture_coverage_has_all_five_entities_for_every_provider():
    from normalization.adapters import ADAPTERS,ENTITIES
    assert {(c["provider"],c["entity"]) for c in CASES}=={(p,e) for p in ADAPTERS for e in ENTITIES}
    assert len(CASES)==15
