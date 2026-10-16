"""UKG employee YAML: contract coverage and execution across profile, pay-info and compensation."""
from collections import Counter
from importlib.resources import files
from pathlib import Path
import unittest

from bundle_helpers import UKG, UKG_CO, only, response, run
from normalization import contracts
from normalization.canonical_models.canonical_model_employee import CanonicalEmployee
from normalization.mapping_config import FieldMapping, ListMapping
from normalization.mapping_config import load_mapping_config
from normalization.mapping_engine import MappingEngine

DETAIL = UKG_CO + "/employees/{aid}"
# (YAML file, record schema as the adapter routes it)
VARIANTS = (
    ("employee", contracts.response_schema("ukg-ready", DETAIL)),
    ("employee_pay_info", contracts.response_schema("ukg-ready", DETAIL + "/pay-info").wrap("pay_info")),
    ("employee_compensation",
     contracts.response_schema("ukg-ready", DETAIL + "/compensation/history").wrap("compensation_history")),
)


def configuration(name):
    return load_mapping_config(Path(str(files("normalization").joinpath(f"mappings/ukg_ready/{name}.yaml"))))


def engine(name):
    return MappingEngine(configuration(name), dict(VARIANTS)[name], CanonicalEmployee)


def contract_paths(schema, prefix="", seen=()):
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


def mapped_paths(rules, schema, prefix=""):
    result = []
    for rule in rules:
        if isinstance(rule, FieldMapping) and rule.source_scope == "context":
            continue
        source = schema.at(rule.source)
        array = source.is_array
        path = prefix + rule.source + ("[]" if array else "")
        result.append(path)
        if not isinstance(rule, FieldMapping):
            if isinstance(rule, ListMapping):
                if not array:
                    raise AssertionError("List rule source is not a list")
                source = source.items()
            result.extend(mapped_paths(rule.fields, source, path + "."))
    return result


def synthetic(schema, seen=()):
    node = schema.node
    kind = node.get("type")
    if isinstance(kind, list):
        kind = next((k for k in kind if k != "null"), None)
    if kind == "array" or (kind is None and "items" in node):
        return [synthetic(schema.items(), seen)]
    if kind == "object" or (kind is None and "properties" in node):
        if schema.is_open:
            return {"synthetic": False}
        if id(node) in seen:
            return {}
        seen = seen + (id(node),)
        return {name: synthetic(schema.child(name), seen) for name in sorted(schema.declared())}
    return {"string": "synthetic", "integer": 0, "number": 0.0, "boolean": False}.get(kind)


class UKGEmployeeYamlChecks(unittest.TestCase):
    def test_all_contract_paths_are_mapped_preserved_or_projected(self):
        actual, expected = Counter(), set()
        for name, schema in VARIANTS:
            config = configuration(name)
            self.assertEqual((config.provider, config.entity), ("ukg-ready", "employee"))
            actual.update(mapped_paths(config.fields, schema))
            expected |= contract_paths(schema)
            MappingEngine(config, schema, CanonicalEmployee)  # preflight passes
        retained = {p for p in expected if "_links" in p.replace("[]", "").split(".")}
        projections = {"ein", "pay_info.employee_type"}
        self.assertEqual(expected - set(actual) - retained, projections)
        self.assertTrue(all(count == 1 for count in actual.values()))
        # 177/165/10: the source model also declared the live-only
        # _links.country-fields; it is not in the contract, so it is now an extra.
        self.assertEqual((len(expected), len(actual), len(retained)), (177, 165, 10))
        for projected in projections:
            self.assertIn(projected + ".id", actual)

    def test_detail_preserves_unknown_status_units_references_and_nested_links(self):
        document = run("ukg-ready",
            response(DETAIL, {
                "id": 7, "employee_id": "EMP007", "first_name": "Example", "status": "UNVERIFIED",
                "primary_account_id": 12.0, "ein": {"id": 3},
                "address": {"state_code": "CA", "state": "source-state", "zip": "02108"},
                "_links": {"self": "/synthetic/employee"}}, **UKG, aid="7"),
            response(DETAIL + "/pay-info", {"employee_type": {"id": 2.0}, "standard_work_day": 28800000},
                     **UKG, aid="7"),
            response(DETAIL + "/compensation/history", {"compensations": [{
                "id": 9, "employee": {"account_id": 7.0}, "amount": 2500.0,
                "amount_period": "SOURCE_PERIOD", "currency": "USD", "effective_from": "2026-10-01",
                "_links": {"self": "/synthetic/history"}, "future_flag": False}]}, **UKG, aid="7"))
        result = only(document, "employees")
        self.assertEqual(result["employee_id"], "7")
        self.assertEqual(result["ukg_employee_id"], "EMP007")
        self.assertEqual(result["ukg_primary_account_id"], "12")
        self.assertEqual(result["ukg_ein_id"], "3")
        self.assertEqual(result["ukg_employee_type_id"], "2")
        self.assertEqual(result["ukg_standard_work_day_milliseconds"], 28800000)
        self.assertNotIn("employment_status", result)
        self.assertNotIn("employment_type", result)
        provider = result["provider_fields"]["ukg-ready"]
        self.assertEqual(provider["status"], "UNVERIFIED")
        self.assertEqual(provider["unmapped"]["_links"]["self"], "/synthetic/employee")
        self.assertEqual(provider["unmapped"]["compensation_history"]["compensations"][0]["_links"]["self"],
                         "/synthetic/history")
        history = provider["compensation_history"]["compensations"][0]
        self.assertEqual(history["id"], "9")
        self.assertEqual(history["employee"]["account_id"], "7")
        self.assertEqual(history["amount_period"], "SOURCE_PERIOD")
        self.assertEqual(history["amount"], 2500.0)
        self.assertIs(result["source_extras"]["ukg-ready"]["compensation_history"]["compensations"][0]["future_flag"],
                      False)

    def test_list_item_uses_same_canonical_names(self):
        result = engine("employee").map({
            "id": 7.0, "employee_id": "EMP007", "first_name": "Example", "ein_name": "Source EIN name",
            "primary_account_id": 12.0, "dates": {"hired": "2020-01-02", "terminated": "2025-01-02"},
            "_links": {"pay-info": "/synthetic/pay-info"},
        })
        self.assertEqual(result.employee_id, "7")
        self.assertEqual(result.ukg_employee_id, "EMP007")
        self.assertEqual(result.ukg_ein_name, "Source EIN name")
        self.assertEqual(result.model_dump(mode="json")["original_hire_date"], "2020-01-02")
        self.assertEqual(result.provider_fields["ukg-ready"]["unmapped"]["_links"]["pay-info"], "/synthetic/pay-info")
        with self.assertRaises(ValueError):
            engine("employee").map({"id": 7.5})

    def test_all_nested_sections_and_helpers_execute_end_to_end(self):
        profile, pay_info, compensation = (synthetic(schema) for _, schema in VARIANTS)
        document = run("ukg-ready",
                       response(DETAIL, profile, **UKG, aid="0"),
                       response(DETAIL + "/pay-info", pay_info["pay_info"], **UKG, aid="0"),
                       response(DETAIL + "/compensation/history", compensation["compensation_history"],
                                **UKG, aid="0"))
        output = only(document, "employees")
        self.assertEqual(output["employee_id"], "0")
        self.assertIn("compensation_history", output["provider_fields"]["ukg-ready"])

    def test_projected_nullable_reference_containers_are_not_silently_discarded(self):
        output = engine("employee").map({"id": None, "ein": None})
        self.assertIsNone(output.employee_id)
        self.assertIsNone(output.provider_fields["ukg-ready"]["unmapped"]["ein"])
        pay = engine("employee_pay_info").map({"pay_info": {"employee_type": None}},
                                              context={"employee_id": None})
        self.assertIsNone(pay.provider_fields["ukg-ready"]["unmapped"]["pay_info"]["employee_type"])


if __name__ == "__main__":
    unittest.main()
