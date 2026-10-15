"""isolved employee rules: schema paths, complete coverage and conservative labels."""
from collections import Counter
from importlib.resources import files
from pathlib import Path
import re
import types
from typing import Any, Union, get_args, get_origin
import unittest

import yaml

from normalization import contracts
from normalization.canonical_models.canonical_model_employee import CanonicalEmployee
from normalization.mapping_config import FieldMapping, ListMapping, MappingConfig
from normalization.mapping_engine import load_mapping_config

LEGAL = "/api/clients/{clientId}/legals/{legalId}/employees"
EMPLOYEE = contracts.response_schema("isolved", LEGAL + "/{id}")
SALARIES = contracts.response_schema("isolved", LEGAL + "/{employeeId}/salaries").wrap("salary_history")


def config(name):
    return load_mapping_config(Path(str(files("normalization").joinpath(f"mappings/isolved/{name}.yaml"))))


def unwrap(annotation):
    if get_origin(annotation) in (Union, types.UnionType):
        values = [value for value in get_args(annotation) if value is not type(None)]
        if len(values) == 1:
            return values[0]
    return annotation


def output_type(model, path):
    """Canonical (Pydantic) type at a target path; Any below dict-typed fields."""
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


def contract_paths(schema, prefix="", seen=()):
    """Every contract-declared source path ('[]' marks arrays), recursion-safe."""
    result = set()
    if schema.is_open or id(schema.node) in seen:
        return result
    seen = seen + (id(schema.node),)
    for name in schema.declared():
        child = schema.child(name)
        path = prefix + name + ("[]" if child.is_array else "")
        result.add(path)
        result |= contract_paths(child.items() if child.is_array else child, path + ".", seen)
    return result


def collect(rules, schema, output_model, source_prefix="", target_prefix=""):
    """(source path, target path) pairs, checking source paths against the contract."""
    pairs = []
    for rule in rules:
        target_type = output_type(output_model, rule.target)
        target = target_prefix + rule.target
        if isinstance(rule, FieldMapping) and rule.source_scope == "context":
            continue
        for path in rule.source if isinstance(rule.source, list) else [rule.source]:
            array = schema.at(path).is_array
            pairs.append((source_prefix + path + ("[]" if array else ""), target + ("[]" if array else "")))
        if not isinstance(rule, FieldMapping):
            source = schema.at(rule.source)
            array = source.is_array
            full = source_prefix + rule.source + ("[]" if array else "")
            if isinstance(rule, ListMapping):
                if not array:
                    raise AssertionError(f"Expected list source at {rule.source}")
                source = source.items()
                if target_type is not Any:
                    target_type = unwrap(get_args(target_type)[0])
            pairs.extend(collect(rule.fields, source, target_type, full + ".",
                                 target + ("[]" if isinstance(rule, ListMapping) else "") + "."))
    return pairs


def canonical_path(path):
    path = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", path)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", path).lower()


class IsolvedEmployeeYamlChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = config("employee")
        cls.salaries = config("employee_salaries")  # salary history is its own endpoint now

    def actual(self):
        return (collect(self.config.fields, EMPLOYEE, CanonicalEmployee)
                + collect(self.salaries.fields, SALARIES, CanonicalEmployee))

    def test_every_source_path_is_mapped_or_retained_by_the_existing_link_fallback(self):
        actual = self.actual()
        counts = Counter(source for source, _ in actual)
        expected = contract_paths(EMPLOYEE) | contract_paths(SALARIES)
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
        actual = dict(self.actual())
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
