"""Complete PrismHR employee YAML coverage, without executing unfinished helpers."""
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
from normalization.source_models.prismhr.prismhr_source_model_employee import PrismHREmployee


def unwrap(annotation):
    if get_origin(annotation) in (Union, types.UnionType):
        values = [value for value in get_args(annotation) if value is not type(None)]
        if len(values) == 1:
            return values[0]
    return annotation


def path_type(model, path):
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


def declared_paths(model, prefix=""):
    model.model_rebuild()
    result = set()
    for name, field in model.model_fields.items():
        annotation = unwrap(field.annotation)
        array = get_origin(annotation) is list
        path = prefix + name + ("[]" if array else "")
        result.add(path)
        nested = unwrap(get_args(annotation)[0]) if array else annotation
        if isinstance(nested, type) and issubclass(nested, BaseModel):
            result.update(declared_paths(nested, path + "."))
    return result


def collect_rules(rules, source_model, output_model, source_prefix="", target_prefix=""):
    """Independently compare rule paths to actual source/output schemas."""
    mappings = []
    for rule in rules:
        target_type = path_type(output_model, rule.target)
        target = target_prefix + rule.target
        if isinstance(rule, FieldMapping) and rule.source_scope == "context":
            if rule.source != "client_id" or rule.target != "prismhr_client_id":
                raise AssertionError("Unexpected request-context rule")
            continue
        paths = rule.source if isinstance(rule.source, list) else [rule.source]
        for path in paths:
            annotation = path_type(source_model, path)
            array = get_origin(annotation) is list
            full_source = source_prefix + path + ("[]" if array else "")
            mappings.append((full_source, target + ("[]" if array else "")))
        if not isinstance(rule, FieldMapping):
            annotation = path_type(source_model, rule.source)
            if isinstance(rule, ListMapping):
                if get_origin(annotation) is not list:
                    raise AssertionError(f"Expected list source at {rule.source}")
                annotation = unwrap(get_args(annotation)[0])
                if target_type is not Any:
                    target_type = unwrap(get_args(target_type)[0])
            mappings.extend(collect_rules(
                rule.fields, annotation, target_type,
                full_source + ".", target + ("[]" if isinstance(rule, ListMapping) else "") + ".",
            ))
    return mappings


class PrismHREmployeeYamlChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resource = files("normalization").joinpath("mappings/prismhr/employee.yaml")
        cls.config = MappingConfig.model_validate(yaml.safe_load(cls.resource.read_text()))

    def test_every_current_employee_source_path_is_covered_once(self):
        mappings = collect_rules(self.config.fields, PrismHREmployee, CanonicalEmployee)
        counts = Counter(source for source, target in mappings)
        self.assertEqual(set(counts), declared_paths(PrismHREmployee))
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
        actual = dict(collect_rules(self.config.fields, PrismHREmployee, CanonicalEmployee))
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
