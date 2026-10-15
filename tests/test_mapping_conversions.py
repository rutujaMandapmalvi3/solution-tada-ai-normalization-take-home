"""Label, number and ZIP conversions, including the complete PrismHR YAML."""
from datetime import date
from importlib.resources import files
from pathlib import Path
import unittest

from normalization import contracts
from normalization.canonical_models.canonical_model_employee import CanonicalEmployee
from normalization.contracts import Schema
from normalization.helpers.mapping import label, number, postal_code
from normalization.mapping_config import MappingConfig
from normalization.mapping_engine import MappingEngine, load_mapping_config

SOURCE = Schema({"type": "object", "properties": {
    "id": {"type": "string"}, "details": {"type": ["object", "null"]}}}, {})
PRISM_EMPLOYEE = contracts.response_schema("prismhr", "/employee/v1/getEmployee").at("employee[]")


def synthetic(schema, seen=()):
    """Synthetic record covering every contract-declared field (no customer data)."""
    node = schema.node
    kind = node.get("type")
    if isinstance(kind, list):
        kind = next((k for k in kind if k != "null"), None)
    if kind == "array" or (kind is None and "items" in node):
        return [synthetic(schema.items(), seen)]
    if kind == "object" or (kind is None and "properties" in node):
        if schema.is_open:
            return {"synthetic": False}
        if id(node) in seen:  # recursive reference: keep only its identity
            return {"id": synthetic(schema.child("id"), seen)} if "id" in schema.declared() else {}
        seen = seen + (id(node),)
        return {name: synthetic(schema.child(name), seen) for name in sorted(schema.declared())}
    return {"string": "synthetic", "integer": 0, "number": 0.0, "boolean": False}.get(kind)


class ConversionChecks(unittest.TestCase):
    def test_numbers_keep_zero_and_negatives_and_do_not_guess_currency_or_units(self):
        for value, expected in ((None, None), ("", None), ("  ", None), ("0", 0.0),
                                (0, 0.0), ("-12.50", -12.5), (".5", 0.5), ("1e2", 100.0)):
            with self.subTest(value=value):
                result = number(value)
                self.assertEqual(result.value, expected)
                self.assertIsNone(result.issue)
        for value in (True, "$25", "1,000", "1_000", "25%", "NaN", "1e9999",
                      float("inf"), float("nan"), [], 10**1000):
            with self.subTest(value=value):
                self.assertIsNone(number(value).value)
                self.assertIsNotNone(number(value).issue)

    def test_labels_use_only_the_supplied_dictionary_and_keep_blank_distinct(self):
        labels = {"M": "married", "S": "single"}
        for value, expected in (("M", "married"), ("Married", "married"),
                                ("SINGLE", "single"), (None, None), ("", ""), ("  ", "  ")):
            with self.subTest(value=value):
                self.assertEqual(label(value, labels=labels).value, expected)
        self.assertEqual(label("", labels={"": "no preference"}).value, "no preference")
        for value in ("m", "unknown-code", False):
            with self.subTest(value=value):
                self.assertIsNone(label(value, labels=labels).value)
                self.assertIsNotNone(label(value, labels=labels).issue)
        self.assertIsNone(label("FT", labels={}).value)
        self.assertIsNotNone(label("FT", labels={}).issue)

    def test_zip_keeps_leading_zeros_and_handles_missing_or_conflicting_parts(self):
        for base, suffix, expected in (("02108", "0123", "02108-0123"),
                                       ("02108", None, "02108"), ("02108", "", "02108"),
                                       (None, None, None), ("", None, ""),
                                       ("02108-0123", "0123", "02108-0123")):
            with self.subTest(base=base, suffix=suffix):
                self.assertEqual(postal_code(base, suffix).value, expected)
                self.assertIsNone(postal_code(base, suffix).issue)
        for base, suffix, expected in (("02108-0123", "9999", "02108-0123"),
                                       (None, "0123", None), ("", "0123", ""),
                                       (2108, "0123", None), ("02108", 123, "02108")):
            with self.subTest(base=base, suffix=suffix):
                self.assertEqual(postal_code(base, suffix).value, expected)
                self.assertIsNotNone(postal_code(base, suffix).issue)

    def test_complete_yaml_maps_real_types_readable_labels_provenance_and_extras(self):
        path = files("normalization").joinpath("mappings/prismhr/employee.yaml")
        engine = MappingEngine(load_mapping_config(Path(str(path))), PRISM_EMPLOYEE, CanonicalEmployee)
        source = {
            "id": "0007", "firstName": "Example",
            "person": {"gender": "X", "maritalStatus": "M", "birthDate": "2000-01-02",
                       "future_flag": False},
            "client": {"employeeStatus": "A", "employeeType": "FT", "statusClass": "L",
                       "rehireOk": "", "homeLocation": "001"},
            "contactInformation": {"zipcode": "02108", "zipSuffix": "0123"},
            "compensation": {"hourlyPay": "25.50", "salary": "2500", "payMethod": "S",
                             "hourlyPayPeriod": "B", "standardHours": "0",
                             "payRate2": "bad-number"},
        }
        result = engine.map(source, context={"client_id": "00132"})
        self.assertEqual(result.employee_id, "0007")
        self.assertEqual(result.prismhr_client_id, "00132")
        self.assertEqual(result.gender, "non-binary")
        self.assertEqual(result.marital_status, "married")
        self.assertEqual(result.birth_date, date(2000, 1, 2))
        self.assertEqual(result.eligible_for_rehire, "no preference")
        self.assertEqual(result.prismhr_employment_status_class, "on leave")
        self.assertEqual(result.postal_code, "02108-0123")
        self.assertEqual(result.hourly_rate, 25.5)
        self.assertEqual(result.per_pay_salary, 2500.0)
        self.assertEqual(result.standard_hours_per_pay_period, 0.0)
        self.assertEqual(result.other_pay_rate_basis, "bi-weekly")
        self.assertIsNone(result.employment_status)  # No invented employee-status dictionary.
        self.assertIsNone(result.employment_type)
        self.assertIs(result.source_extras["prismhr"]["person"]["future_flag"], False)
        self.assertEqual(result.source_metadata.original_values["client.employeeType"], "FT")
        self.assertEqual(result.source_metadata.original_values["contactInformation.zipSuffix"], "0123")
        paths = {issue.source_path for issue in result.source_metadata.mapping_issues}
        self.assertEqual(paths, {"client.employeeStatus", "client.employeeType", "compensation.payRate2"})
        self.assertNotIn("unmapped", result.provider_fields["prismhr"])
        self.assertEqual(result.model_dump(mode="json")["birth_date"], "2000-01-02")

    def test_complete_yaml_executes_all_nested_sections_and_serializes(self):
        path = files("normalization").joinpath("mappings/prismhr/employee.yaml")
        engine = MappingEngine(load_mapping_config(Path(str(path))), PRISM_EMPLOYEE, CanonicalEmployee)
        source = synthetic(PRISM_EMPLOYEE)
        result = engine.map(source, context={"client_id": "00132"})
        self.assertIn("auto_policies", result.provider_fields["prismhr"]["person"])
        self.assertIn("scheduled_deduction", result.provider_fields["prismhr"])
        self.assertNotIn("unmapped", result.provider_fields["prismhr"])
        result.model_dump_json(exclude_unset=True)

    def test_zip_multiple_sources_preserve_missing_null_and_empty_distinctions(self):
        config = MappingConfig.model_validate({
            "version": 1, "provider": "prismhr", "entity": "employee", "fields": [
                {"kind": "field", "source": "id", "target": "employee_id"},
                {"kind": "field", "source": ["details.zip", "details.suffix"],
                 "target": "postal_code", "transform": {"name": "postal_code"}},
            ],
        })
        engine = MappingEngine(config, SOURCE, CanonicalEmployee)
        for details, expected, present in (({}, None, False), ({"zip": None}, None, True),
                                           ({"zip": ""}, "", True), ({"zip": "02108"}, "02108", True),
                                           ({"suffix": "0123"}, None, True)):
            with self.subTest(details=details):
                result = engine.map({"id": "1", "details": details})
                self.assertEqual(result.postal_code, expected)
                self.assertEqual("postal_code" in result.model_fields_set, present)
                originals = result.source_metadata.original_values
                self.assertEqual("details.zip" in originals, "zip" in details)
                self.assertEqual("details.suffix" in originals, "suffix" in details)
                if "suffix" in details and "zip" not in details:
                    self.assertEqual(len(result.source_metadata.mapping_issues), 1)

    def test_helper_parameters_and_source_counts_are_checked_before_execution(self):
        invalid = [
            ("label", "id", {}), ("label", "id", {"labels": {"M": 1}}),
            ("number", "id", {"round": 2}), ("postal_code", "id", {}),
            ("date", ["id", "id"], {}), ("label", "id", {"labels": {}, "guess": True}),
        ]
        for name, source, arguments in invalid:
            with self.subTest(name=name, arguments=arguments), self.assertRaises(ValueError):
                config = MappingConfig.model_validate({
                    "version": 1, "provider": "prismhr", "entity": "employee", "fields": [
                        {"kind": "field", "source": source, "target": "employee_id",
                         "transform": {"name": name, "arguments": arguments}},
                    ],
                })
                MappingEngine(config, SOURCE, CanonicalEmployee)


if __name__ == "__main__":
    unittest.main()
