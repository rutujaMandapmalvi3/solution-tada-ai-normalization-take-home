"""UKG detail/list YAML schema coverage and execution; no adapter integration."""
from collections import Counter
import inspect
from importlib.resources import files
from pathlib import Path
import types
from typing import Any, Union, get_args, get_origin
import unittest

from pydantic import BaseModel

from normalization.canonical_models.canonical_model_employee import CanonicalEmployee
from normalization.mapping_config import FieldMapping, ListMapping
from normalization.mapping_engine import MappingEngine, load_mapping_config
from normalization.source_models.ukg_ready.ukg_ready_source_model_employee import (
    UKGReadyEmployeeInput,
)


def unwrap(annotation):
    if get_origin(annotation) in (Union, types.UnionType):
        return next(t for t in get_args(annotation) if t is not type(None))
    return annotation


def path_type(model, path):
    for key in path.split("."):
        model = unwrap(model)
        if model is Any:
            return Any
        if get_origin(model) is dict:
            model = get_args(model)[1]
        else:
            model.model_rebuild()
            field = next(f for n, f in model.model_fields.items() if key in (n, f.alias))
            model = field.annotation
    return unwrap(model)


def declared_paths(model, prefix=""):
    model.model_rebuild()
    result = set()
    for name, field in model.model_fields.items():
        annotation = unwrap(field.annotation)
        array = get_origin(annotation) is list
        path = prefix + (field.alias or name) + ("[]" if array else "")
        result.add(path)
        nested = unwrap(get_args(annotation)[0]) if array else annotation
        if inspect.isclass(nested) and issubclass(nested, BaseModel):
            result.update(declared_paths(nested, path + "."))
    return result


def mapped_paths(rules, source_model, output_model, prefix=""):
    result = []
    for rule in rules:
        target_type = path_type(output_model, rule.target)
        self_type = path_type(source_model, rule.source)
        array = get_origin(self_type) is list
        path = prefix + rule.source + ("[]" if array else "")
        result.append(path)
        if not isinstance(rule, FieldMapping):
            if isinstance(rule, ListMapping):
                if not array:
                    raise AssertionError("List rule source is not a list")
                self_type = unwrap(get_args(self_type)[0])
                if target_type is not Any:
                    target_type = unwrap(get_args(target_type)[0])
            result.extend(mapped_paths(rule.fields, self_type, target_type, path + "."))
    return result


def synthetic_record(model):
    model.model_rebuild()
    def value(annotation):
        annotation = unwrap(annotation)
        if get_origin(annotation) is list:
            return [value(get_args(annotation)[0])]
        if get_origin(annotation) is dict:
            return {"synthetic": False}
        if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
            return synthetic_record(annotation)
        return {str: "synthetic", int: 0, float: 0.0, bool: False, Any: None}[annotation]
    return {(field.alias or name): value(field.annotation) for name, field in model.model_fields.items()}


class UKGEmployeeYamlChecks(unittest.TestCase):
    variants = (
        ("employee", UKGReadyEmployeeInput, 178, 165, 11, {"ein", "pay_info.employee_type"}),
    )

    @staticmethod
    def configuration(name):
        resource = files("normalization").joinpath(f"mappings/ukg_ready/{name}.yaml")
        return load_mapping_config(Path(str(resource)))

    def test_all_current_source_paths_are_mapped_preserved_or_projected(self):
        for name, model, total, explicit, links, projections in self.variants:
            with self.subTest(name=name):
                config = self.configuration(name)
                self.assertEqual((config.provider, config.entity), ("ukg-ready", "employee"))
                actual = Counter(mapped_paths(config.fields, model, CanonicalEmployee))
                expected = declared_paths(model)
                retained = {p for p in expected if "_links" in p.split(".")}
                self.assertEqual(expected - set(actual) - retained, projections)
                self.assertTrue(all(count == 1 for count in actual.values()))
                self.assertEqual((len(expected), len(actual), len(retained)), (total, explicit, links))
                for projected in projections:
                    self.assertIn(projected + ".id", actual)
                MappingEngine(config, model, CanonicalEmployee)

    def test_detail_preserves_unknown_status_units_references_and_nested_links(self):
        engine = MappingEngine(self.configuration("employee"), UKGReadyEmployeeInput, CanonicalEmployee)
        source = UKGReadyEmployeeInput.model_validate({
            "id": 7, "employee_id": "EMP007", "first_name": "Example", "status": "UNVERIFIED",
            "primary_account_id": 12.0, "ein": {"id": 3},
            "address": {"state_code": "CA", "state": "source-state", "zip": "02108"},
            "pay_info": {"employee_type": {"id": 2.0}, "standard_work_day": 28800000},
            "compensation_history": {"compensations": [{
                "id": 9, "employee": {"account_id": 7.0}, "amount": 2500.0,
                "amount_period": "SOURCE_PERIOD", "currency": "USD", "effective_from": "2026-10-01",
                "_links": {"self": "/synthetic/history"}, "future_flag": False,
            }]}, "_links": {"self": "/synthetic/employee"},
        })
        result = engine.map(source)
        self.assertEqual(result.employee_id, "7")
        self.assertEqual(result.ukg_employee_id, "EMP007")
        self.assertEqual(result.ukg_primary_account_id, "12")
        self.assertEqual(result.ukg_ein_id, "3")
        self.assertEqual(result.ukg_employee_type_id, "2")
        self.assertEqual(result.ukg_standard_work_day_milliseconds, 28800000)
        self.assertNotIn("employment_status", result.model_fields_set)
        self.assertNotIn("employment_type", result.model_fields_set)
        provider = result.provider_fields["ukg-ready"]
        self.assertEqual(provider["status"], "UNVERIFIED")
        self.assertEqual(provider["unmapped"]["_links"]["self"], "/synthetic/employee")
        self.assertEqual(provider["unmapped"]["compensation_history"]["compensations"][0]["_links"]["self"],
                         "/synthetic/history")
        history = provider["compensation_history"]["compensations"][0]
        self.assertEqual(history["id"], "9")
        self.assertEqual(history["employee"]["account_id"], "7")
        self.assertEqual(history["amount_period"], "SOURCE_PERIOD")
        self.assertEqual(history["amount"], 2500.0)
        self.assertIs(result.source_extras["ukg-ready"]["compensation_history"]["compensations"][0]["future_flag"], False)
        result.model_dump_json(exclude_unset=True)

    def test_list_item_uses_same_canonical_names_without_coercing_its_source_schema(self):
        engine = MappingEngine(self.configuration("employee"), UKGReadyEmployeeInput, CanonicalEmployee)
        source = UKGReadyEmployeeInput.model_validate({
            "id": 7.0, "employee_id": "EMP007", "first_name": "Example", "ein_name": "Source EIN name",
            "primary_account_id": 12.0, "dates": {"hired": "2020-01-02", "terminated": "2025-01-02"},
            "_links": {"pay-info": "/synthetic/pay-info"},
        })
        result = engine.map(source)
        self.assertEqual(result.employee_id, "7")
        self.assertEqual(result.ukg_employee_id, "EMP007")
        self.assertEqual(result.ukg_ein_name, "Source EIN name")
        self.assertEqual(result.model_dump(mode="json")["original_hire_date"], "2020-01-02")
        self.assertEqual(result.provider_fields["ukg-ready"]["unmapped"]["_links"]["pay-info"], "/synthetic/pay-info")
        with self.assertRaises(ValueError):
            engine.map(UKGReadyEmployeeInput.model_validate({"id": 7.5}))

    def test_all_nested_sections_and_helpers_execute_for_both_source_models(self):
        for name, model, *_ in self.variants:
            with self.subTest(name=name):
                engine = MappingEngine(self.configuration(name), model, CanonicalEmployee)
                source = model.model_validate(synthetic_record(model))
                output = engine.map(source)
                self.assertEqual(output.employee_id, "0")
                self.assertIn("compensation_history", output.provider_fields["ukg-ready"])
                output.model_dump_json(exclude_unset=True)

    def test_projected_nullable_reference_containers_are_not_silently_discarded(self):
        engine = MappingEngine(self.configuration("employee"), UKGReadyEmployeeInput, CanonicalEmployee)
        output = engine.map(UKGReadyEmployeeInput.model_validate({"id": None, "ein": None,
                                                                "pay_info": {"employee_type": None}}))
        self.assertIsNone(output.employee_id)
        unmapped = output.provider_fields["ukg-ready"]["unmapped"]
        self.assertIsNone(unmapped["ein"])
        self.assertIsNone(unmapped["pay_info"]["employee_type"])


if __name__ == "__main__":
    unittest.main()
