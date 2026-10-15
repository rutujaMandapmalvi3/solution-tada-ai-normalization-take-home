"""isolved employee rules: schema paths, complete coverage and conservative labels."""
from collections import Counter
from importlib.resources import files
from pathlib import Path
import re
import types
from typing import Any, Union, get_args, get_origin
import unittest

from pydantic import BaseModel
import yaml

from normalization.canonical_models.canonical_model_employee import CanonicalEmployee
from normalization.mapping_config import FieldMapping, ListMapping, MappingConfig
from normalization.source_models.isolved.isolved_source_model_employee import IsolvedEmployeeInput


def unwrap(annotation):
    if get_origin(annotation) in (Union, types.UnionType):
        return next(t for t in get_args(annotation) if t is not type(None))
    return annotation


def schema_type(model, path):
    for segment in path.split("."):
        model = unwrap(model)
        if model is Any:
            return Any
        if get_origin(model) is dict:
            model = get_args(model)[1]
        else:
            model.model_rebuild()
            model = model.model_fields[segment].annotation
    return unwrap(model)


def source_paths(model, prefix=""):
    model.model_rebuild()
    result = set()
    for name, field in model.model_fields.items():
        annotation = unwrap(field.annotation)
        array = get_origin(annotation) is list
        path = prefix + name + ("[]" if array else "")
        result.add(path)
        nested = unwrap(get_args(annotation)[0]) if array else annotation
        if isinstance(nested, type) and issubclass(nested, BaseModel):
            result.update(source_paths(nested, path + "."))
    return result


def collect(rules, source_model, output_type, source_prefix="", target_prefix=""):
    result = []
    for rule in rules:
        target_type = schema_type(output_type, rule.target)
        target = target_prefix + rule.target
        paths = rule.source if isinstance(rule.source, list) else [rule.source]
        for path in paths:
            annotation = schema_type(source_model, path)
            array = get_origin(annotation) is list
            full_source = source_prefix + path + ("[]" if array else "")
            result.append((full_source, target + ("[]" if array else "")))
        if not isinstance(rule, FieldMapping):
            if isinstance(rule, ListMapping):
                if get_origin(annotation) is not list:
                    raise AssertionError("Expected list source")
                annotation = unwrap(get_args(annotation)[0])
                if target_type is not Any:
                    target_type = unwrap(get_args(target_type)[0])
            result.extend(collect(rule.fields, annotation, target_type, full_source + ".",
                                  target + ("[]" if isinstance(rule, ListMapping) else "") + "."))
    return result


def canonical_path(path):
    path = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", path)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", path).lower()


class IsolvedEmployeeYamlChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        resource = files("normalization").joinpath("mappings/isolved/employee.yaml")
        cls.config = MappingConfig.model_validate(yaml.safe_load(resource.read_text()))

    def test_every_source_path_is_mapped_or_retained_by_the_existing_link_fallback(self):
        actual = collect(self.config.fields, IsolvedEmployeeInput, CanonicalEmployee)
        counts = Counter(source for source, _ in actual)
        expected = source_paths(IsolvedEmployeeInput)
        preserved = {path for path in expected if "links[]" in path.split(".")}
        self.assertEqual(set(counts), expected - preserved)
        self.assertTrue(all(count == 1 for count in counts.values()))
        self.assertEqual(len(expected), 524)
        self.assertEqual(len(counts), 408)
        self.assertEqual(len(preserved), 116)
        self.assertIn("salary_history[].seasons[].id", counts)

    def test_targets_follow_the_approved_inventory_with_consistent_snake_case(self):
        text = (Path(__file__).parents[1] / "docs/solution-docs/data-types-cpmparison"
                / "Employee Canonical Mapping Proposal.md").read_text()
        expected = {}
        for line in text.splitlines():
            cells = [cell.strip() for cell in line.split("|")]
            if len(cells) != 8 or cells[1] != "isolved":
                continue
            source = re.match(r"`([^`]+)`", cells[2]).group(1)
            if source.startswith("employee_list.") or cells[3].strip("`").startswith("source_metadata."):
                continue
            target = canonical_path(cells[3].strip("`"))
            if target.startswith("isolved."):
                target = "provider_fields." + target
            expected[source] = target
        actual = dict(collect(self.config.fields, IsolvedEmployeeInput, CanonicalEmployee))
        actual = {source: target if expected[source].endswith("[]") else target.removesuffix("[]")
                  for source, target in actual.items()}
        self.assertEqual(actual, expected)

    def test_conflicting_pronouns_have_one_multi_source_rule(self):
        matches = [r for r in self.config.fields if r.target == "preferred_pronouns"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].source, ["nameAddress.preferredPronouns", "personal.preferredPronouns"])
        self.assertEqual(matches[0].transform.name, "pronouns")

    def test_labels_do_not_reuse_prism_or_corestream_code_meanings(self):
        self.assertEqual((self.config.provider, self.config.entity), ("isolved", "employee"))
        rules = {r.source: r for r in self.config.fields if isinstance(r.source, str)}
        self.assertEqual(rules["gender"].transform.arguments["labels"]["male"], "male")
        self.assertNotIn("M", rules["gender"].transform.arguments["labels"])
        self.assertNotIn("M", rules["maritalStatus"].transform.arguments["labels"])
        self.assertEqual(rules["employmentCategoryCode"].target,
                         "provider_fields.isolved.employment_category_code")
        self.assertIsNone(rules["employmentCategoryCode"].transform)
        self.assertEqual(rules["eligibleForRehire"].transform.arguments["labels"],
                         {"true": "eligible", "false": "ineligible"})
        self.assertEqual(rules["id"].transform.name, "identifier")
        self.assertEqual(rules["birthDate"].transform.name, "date")


if __name__ == "__main__":
    unittest.main()
