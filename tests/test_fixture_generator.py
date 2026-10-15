"""Deterministic bundle generation, contract validation and expected-output protection."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("fixture_generator", ROOT / "scripts/generate_fixtures.py")
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


def test_default_seed_reproduces_committed_bundles(tmp_path):
    paths = generator.generate(output_dir=tmp_path)
    assert sorted(path.name for path in paths) == ["isolved.bundle.json", "prismhr.bundle.json",
                                                    "ukg-ready.bundle.json"]
    for path in paths:
        assert path.read_text() == (ROOT / "tests/fixtures" / path.name).read_text()
    manifest = json.loads((tmp_path / "generation_manifest.json").read_text())
    assert manifest["seed"] == 42 and manifest["bundle_count"] == 3
    assert len(manifest["files"]) == 3 and len(manifest["evidence"]) == 3


def test_generation_never_writes_expected_outputs(tmp_path):
    generator.generate(output_dir=tmp_path)
    assert not list(tmp_path.glob("*.expected.json"))


def test_another_seed_changes_values_not_shape(tmp_path):
    default, other = generator.build_bundles(42), generator.build_bundles(7)
    for provider in default:
        assert [r["endpoint"] for r in default[provider]["responses"]] == \
               [r["endpoint"] for r in other[provider]["responses"]]


def test_every_bundle_names_its_owner_in_params():
    for bundle in generator.build_bundles().values():
        for response in bundle["responses"]:
            assert response["params"], response["endpoint"]


def test_type_errors_are_rejected_before_writing(tmp_path):
    bundle = generator.build_bundles()["ukg-ready"]
    bundle["responses"][0]["body"]["items"][0]["id"] = "not-an-integer"
    with pytest.raises(ValueError, match="items/0/id"):
        generator.validate_bundle(bundle)
