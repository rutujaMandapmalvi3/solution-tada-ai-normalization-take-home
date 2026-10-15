"""Deterministic generation, source validation and expected-output protection."""
import copy
import importlib.util
import json
from pathlib import Path
import random
from unittest.mock import patch
import pytest

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("fixture_generator", ROOT/"scripts/generate_fixtures.py")
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


def test_all_fifteen_cases_validate_and_match_reviewed_default_inputs(tmp_path):
    paths = generator.generate(output_dir=tmp_path)
    assert len(paths)==15
    for path in paths:
        relative=path.relative_to(tmp_path)
        provider,entity,_=relative.parts
        payload=json.loads(path.read_text())
        before=copy.deepcopy(payload)
        generator.validate_case(provider,entity,payload)
        assert payload==before
        assert payload==json.loads((ROOT/"tests/fixtures"/relative).read_text())
    assert json.loads((tmp_path/"manifest.json").read_text())==json.loads((ROOT/"tests/fixtures/manifest.json").read_text())
    generation=json.loads((tmp_path/"generation_manifest.json").read_text())
    assert generation["seed"]==42 and generation["case_count"]==15
    assert len(generation["files"])==15 and len(generation["evidence"])==3


def test_repeatable_and_different_seed_preserves_source_validity(tmp_path):
    generator.generate(42,tmp_path)
    before={str(p.relative_to(tmp_path)):p.read_bytes() for p in tmp_path.rglob("*.json")}
    generator.generate(42,tmp_path)
    assert before=={str(p.relative_to(tmp_path)):p.read_bytes() for p in tmp_path.rglob("*.json")}
    other=generator.build_cases(43)
    assert other!=generator.build_cases(42)
    for provider,entities in other.items():
        for entity,payload in entities.items():
            generator.validate_case(provider,entity,payload)


def test_does_not_touch_expected_files_or_global_random_state(tmp_path):
    expected=tmp_path/"prismhr/employee/expected.json"
    expected.parent.mkdir(parents=True)
    expected.write_text("reviewed baseline\n")
    state=random.getstate()
    generator.generate(output_dir=tmp_path)
    assert random.getstate()==state
    assert expected.read_text()=="reviewed baseline\n"
    assert list(tmp_path.rglob("expected.json"))==[expected]


def test_invalid_case_does_not_write_partial_fixture_set(tmp_path):
    cases=generator.build_cases()
    cases["ukg-ready"]["company"]["items"][0].pop("id")
    target=tmp_path/"not-created"
    with patch.object(generator,"build_cases",return_value=cases),pytest.raises(ValueError):
        generator.generate(output_dir=target)
    assert not target.exists()


def test_cli_options(tmp_path,capsys):
    assert generator.main(["--seed","43","--output-dir",str(tmp_path)])==0
    assert "Generated 15 input fixtures" in capsys.readouterr().out
    assert json.loads((tmp_path/"generation_manifest.json").read_text())["seed"]==43
