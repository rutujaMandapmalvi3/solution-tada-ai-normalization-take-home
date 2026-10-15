"""Complete PrismHR employee YAML coverage, without executing unfinished helpers."""
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

PRISM_EMPLOYEE = contracts.response_schema("prismhr", "/employee/v1/getEmployee").at("employee[]")


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


class PrismHREmployeeYamlChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resource = files("normalization").joinpath("mappings/prismhr/employee.yaml")
        cls.config = MappingConfig.model_validate(yaml.safe_load(cls.resource.read_text()))

    def test_every_current_employee_source_path_is_covered_once(self):
        mappings = collect(self.config.fields, PRISM_EMPLOYEE, CanonicalEmployee)
        counts = Counter(source for source, target in mappings)
        self.assertEqual(set(counts), contract_paths(PRISM_EMPLOYEE))
        self.assertEqual({key: value for key, value in counts.items() if value != 1}, {})
        self.assertEqual(len(counts), 385)

    def test_destinations_follow_the_approved_proposal(self):
        proposal = (Path(__file__).parents[1] / "docs/solution-docs/data-types-cpmparison"
                    / "Employee Canonical Mapping Proposal.md").read_text()
        expected = {}
        for line in proposal.splitlines():
            cells = [cell.strip() for cell in line.split("|")]
            if len(cells) != 8 or cells[1] != "prismhr":
                continue
            source = re.match(r"`([^`]+)`", cells[2]).group(1)
            if source.startswith("response."):
                continue
            target = cells[3].strip("`")
            if target.startswith("prismhr."):
                target = "provider_fields." + target
            expected[source] = target
        actual = dict(collect(self.config.fields, PRISM_EMPLOYEE, CanonicalEmployee))
        # Scalar-list field destinations have no [] in YAML paths; inventory uses [] as notation.
        actual = {source: (target if expected[source].endswith("[]")
                           else target.removesuffix("[]")) for source, target in actual.items()}
        self.assertEqual(actual, expected)

    def test_approved_labels_do_not_invent_missing_provider_dictionaries(self):
        rules = {rule.source: rule for rule in self.config.fields
                 if isinstance(rule, FieldMapping) and isinstance(rule.source, str)}
        self.assertEqual(rules["person.gender"].transform.arguments["labels"], {
            "M": "male", "F": "female", "X": "non-binary", "D": "declined", "U": "unknown",
        })
        self.assertEqual(rules["client.rehireOk"].transform.arguments["labels"][""], "no preference")
        self.assertEqual(rules["client.employeeStatus"].transform.arguments["labels"], {})
        self.assertEqual(rules["client.employeeType"].transform.arguments["labels"], {})
        self.assertEqual(rules["compensation.hourlyPayPeriod"].transform.arguments["labels"], {
            "H": "hourly", "W": "weekly", "B": "bi-weekly", "S": "semi-monthly", "M": "monthly", "Y": "yearly",
        })
        postal = next(rule for rule in self.config.fields if rule.target == "postal_code")
        self.assertEqual(postal.source, ["contactInformation.zipcode", "contactInformation.zipSuffix"])
        self.assertEqual(postal.transform.name, "postal_code")
        self.assertFalse(any(rule.target.startswith("source_metadata") for rule in self.config.fields))


if __name__ == "__main__":
    unittest.main()
