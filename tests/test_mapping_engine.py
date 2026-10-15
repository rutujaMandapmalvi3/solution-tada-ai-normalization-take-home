"""Execute the small YAML example and check preservation/failure behavior."""
from copy import deepcopy
from datetime import date
from importlib.resources import files
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import yaml

from pydantic import ValidationError

from normalization import contracts
from normalization.canonical_models.canonical_model_employee import CanonicalEmployee
from normalization.contracts import Schema
from normalization.helpers.mapping import date_value, identifier
from normalization.mapping_config import MappingConfig
from normalization.mapping_engine import MappingEngine, load_mapping_config

# Synthetic source schema (the engine reads contract schemas; this stands in for one).
SOURCE = Schema({"type": "object", "properties": {
    "id": {"type": ["number", "string", "null"]},
    "person": {"type": ["object", "null"], "properties": {
        "contacts": {"type": ["array", "null"], "items": {"type": "object", "properties": {
            "name": {"type": "string"}, "note": {"type": "string"}}}},
        "nickname": {"type": "string"}}},
    "details": {"type": ["object", "null"]},
    "_link": {"type": "string"},
}}, {})
PRISM_EMPLOYEE = contracts.response_schema("prismhr", "/employee/v1/getEmployee").at("employee[]")


def field(source="id", target="employee_id", **kwargs):
    return {"kind": "field", "source": source, "target": target, **kwargs}


def config(*rules, provider="prismhr"):
    return MappingConfig.model_validate({
        "version": 1, "provider": provider, "entity": "employee", "fields": list(rules),
    })


def engine(*rules, provider="prismhr"):
    return MappingEngine(config(*rules, provider=provider), SOURCE, CanonicalEmployee)


class MappingEngineChecks(unittest.TestCase):
    def test_real_yaml_to_canonical_employee_without_mutating_source(self):
        resource = files("normalization").joinpath("mappings/prismhr/employee.example.yaml")
        mapper = MappingEngine(load_mapping_config(Path(str(resource))), PRISM_EMPLOYEE, CanonicalEmployee)
        source = {
            "id": "0007", "firstName": "Example", "lastName": "Employee",
            "person": {"birthDate": "2000-01-02T00:30:00+14:00",
                       "employerIds": ["001", "002"], "new_flag": False},
            "first_name": "must stay an extra", "future": {"amount": 0},
        }
        before = deepcopy(source)
        employee = mapper.map(source, metadata={"infoMessage": ["Informational"], "extension": None})
        self.assertEqual(employee.employee_id, "0007")
        self.assertEqual(employee.first_name, "Example")
        self.assertEqual(employee.birth_date, date(2000, 1, 2))
        self.assertEqual(employee.prismhr_employer_ids, ["001", "002"])
        self.assertEqual(employee.provider_fields["prismhr"]["unmapped"], {"lastName": "Employee"})
        self.assertEqual(employee.source_extras["prismhr"]["first_name"], "must stay an extra")
        self.assertIs(employee.source_extras["prismhr"]["person"]["new_flag"], False)
        self.assertEqual(employee.source_metadata.original_values["person.birthDate"],
                         "2000-01-02T00:30:00+14:00")
        self.assertEqual(employee.source_metadata.model_extra["prismhr"]["infoMessage"], ["Informational"])
        self.assertEqual(employee.model_dump(mode="json")["birth_date"], "2000-01-02")
        self.assertEqual(source, before)
        employee.source_extras["prismhr"]["future"]["amount"] = 999
        self.assertEqual(source["future"]["amount"], 0)

    def test_nested_objects_and_lists_preserve_unmapped_fields_and_extra_positions(self):
        mapper = engine(field(), {
            "kind": "object", "source": "person", "target": "provider_fields.prismhr.profile",
            "fields": [{"kind": "list", "source": "contacts", "target": "contacts", "fields": [
                field("name", "display_name"),
            ]}],
        })
        source = {"id": "1", "person": {"contacts": [
            {"name": "First", "note": "retained", "future": False},
            {"name": "Second", "note": None},
            {"name": "Third", "future": []},
        ], "nickname": "kept"}}
        employee = mapper.map(source)
        provider = employee.provider_fields["prismhr"]
        self.assertEqual(provider["profile"]["contacts"], [
            {"display_name": "First"}, {"display_name": "Second"}, {"display_name": "Third"}])
        self.assertEqual(provider["unmapped"]["person"], {
            "nickname": "kept", "contacts": [{"note": "retained"}, {"note": None}, {}]})
        self.assertEqual(employee.source_extras["prismhr"]["person"]["contacts"],
                         [{"future": False}, {}, {"future": []}])

    def test_missing_null_and_empty_collections_are_not_interchangeable(self):
        mapper = engine(field(), {"kind": "list", "source": "person.contacts",
                                  "target": "provider_fields.prismhr.contacts",
                                  "fields": [field("name", "name")]})
        for supplied, expected in (({}, "missing"), ({"contacts": None}, None), ({"contacts": []}, [])):
            with self.subTest(supplied=supplied):
                output = mapper.map({"id": "1", "person": supplied}).model_dump(exclude_unset=True)
                provider = output.get("provider_fields", {}).get("prismhr", {})
                if expected == "missing":
                    self.assertNotIn("contacts", provider)
                    self.assertEqual(provider["unmapped"]["person"], {})
                else:
                    self.assertEqual(provider["contacts"], expected)
        output = mapper.map({"id": "1", "person": None})
        self.assertIsNone(output.provider_fields["prismhr"]["unmapped"]["person"])

    def test_context_is_separate_from_record_and_engine_is_reusable(self):
        mapper = engine(field(), field("client_id", "prismhr_client_id", source_scope="context"))
        first = mapper.map({"id": "1"}, context={"client_id": "00132"})
        second = mapper.map({"id": "2"})
        self.assertEqual(first.prismhr_client_id, "00132")
        self.assertNotIn("prismhr_client_id", second.model_fields_set)
        self.assertEqual(second.source_metadata.original_values, {})

    def test_json_names_are_read_and_unknown_paths_are_rejected(self):
        # Paths are contract (JSON) names, e.g. "_link"; there is no alias resolution.
        employee = engine(field(), field("_link", "work_email")).map({"id": "1", "_link": "example"})
        self.assertEqual(employee.work_email, "example")
        for source in ("missing", "__class__", "person.missing", "link"):
            with self.subTest(source=source), self.assertRaises(ValueError):
                engine(field(), field(source, "first_name"))

    def test_preflight_rejects_field_path_through_a_list_without_brackets(self):
        with self.assertRaises(ValueError):
            engine(field(), field("person.contacts.name", "first_name"))

    def test_preflight_rejects_bad_targets_shapes_and_unimplemented_helpers(self):
        for rule in (
            field("id", "first_nmae"), field("id", "provider"),
            field("id", "source_metadata.original_values"), field("id", "source_extras.x"),
            field("id", "provider_fields.prismhr.unmapped.id"),
            field(transform={"name": "pronouns"}),
            field(transform={"name": "date", "arguments": {"guess": True}}),
            field(["id", "id"], transform={"name": "identifier"}),
            {"kind": "object", "source": "person", "target": "first_name", "fields": [field("nickname", "name")]},
        ):
            with self.subTest(rule=rule), self.assertRaises(ValueError):
                engine(rule)

    def test_preflight_rejects_list_rule_on_scalar_source(self):
        with self.assertRaises(ValueError):
            engine({"kind": "list", "source": "id", "target": "provider_fields.prismhr.items",
                    "fields": [field()]})

    def test_invalid_dates_are_preserved_with_path_specific_issues(self):
        mapper = engine(field(), field("details.birthday", "birth_date", transform={"name": "date"}))
        employee = mapper.map({"id": "1", "details": {"birthday": "not-a-date", "keep": False}})
        self.assertIsNone(employee.birth_date)
        self.assertEqual(employee.source_metadata.original_values["details.birthday"], "not-a-date")
        self.assertEqual(employee.source_metadata.mapping_issues[0].source_path, "details.birthday")
        self.assertIs(employee.provider_fields["prismhr"]["unmapped"]["details"]["keep"], False)

    def test_required_output_and_record_type_are_enforced(self):
        mapper = engine(field())
        for not_a_record in (["id", "1"], "1", None):
            with self.subTest(source=not_a_record), self.assertRaises(TypeError):
                mapper.map(not_a_record)
        with self.assertRaises(ValidationError):
            engine(field("_link", "first_name")).map({"id": "1"})  # employee_id is required
        with self.assertRaises(ValidationError):
            mapper.map({"id": 123.0})  # No identifier transform: strict output catches the number.
        converted = engine(field(transform={"name": "identifier"})).map({"id": 123.0})
        self.assertEqual(converted.employee_id, "123")
        with self.assertRaisesRegex(ValueError, "id: Identifier"):
            engine(field(transform={"name": "identifier"})).map({"id": 1.5})

    def test_provider_identity_comes_from_configuration_for_each_provider(self):
        for provider in ("prismhr", "isolved", "ukg-ready"):
            with self.subTest(provider=provider):
                result = engine(field(), provider=provider).map({"id": "1", "extra_flag": False})
                self.assertEqual(result.provider, provider)
                self.assertIs(result.source_extras[provider]["extra_flag"], False)

    def test_yaml_loader_rejects_duplicate_keys_and_python_tags(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "rules.yaml"
            for text in ("version: 1\nversion: 1\n", "!!python/object:builtins.object {}",
                         "version: 1\nprovider: prismhr\nentity: employee\nfields:\n"
                         "  - kind: field\n    source: id\n    target: employee_id\n    target: first_name\n"):
                path.write_text(text)
                with self.subTest(text=text), self.assertRaises(yaml.YAMLError):
                    load_mapping_config(path)


class MappingHelperChecks(unittest.TestCase):
    def test_identifiers_preserve_text_and_reject_lossy_conversions(self):
        for value, expected in ((None, None), ("0007", "0007"), (7, "7"), (7.0, "7"), (0, "0")):
            with self.subTest(value=value):
                self.assertEqual(identifier(value).value, expected)
        for value in (True, 1.5, float("inf"), float("nan"), {}, []):
            with self.subTest(value=value), self.assertRaises(ValueError):
                identifier(value)

    def test_dates_preserve_written_calendar_day_and_handle_blank_invalid_values(self):
        for value, expected in ((None, None), ("", None), ("  ", None),
                                ("2000-01-02", date(2000, 1, 2)),
                                ("2000-01-02T00:30:00+14:00", date(2000, 1, 2))):
            with self.subTest(value=value):
                self.assertEqual(date_value(value).value, expected)
        for value in ("20000102", "2000-02-30", "yesterday", 123):
            with self.subTest(value=value):
                self.assertIsNone(date_value(value).value)
                self.assertIsNotNone(date_value(value).issue)


if __name__ == "__main__":
    unittest.main()
