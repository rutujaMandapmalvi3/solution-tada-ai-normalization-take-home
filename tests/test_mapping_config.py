"""Mapping configuration safety before a YAML loader or engine is added."""
import copy
import unittest

from pydantic import ValidationError

from normalization.mapping_config import MappingConfig


def config(fields):
    return {"version": 1, "provider": "prismhr", "entity": "employee", "fields": fields}


def field(source="firstName", target="first_name", **kwargs):
    return {"kind": "field", "source": source, "target": target, **kwargs}


class MappingConfigChecks(unittest.TestCase):
    def test_rename_helper_context_and_recursive_lists(self):
        rules = [
            field(),
            field("id", "employee_id", transform={"name": "identifier"}),
            field("client_id", "prismhr_client_id", source_scope="context"),
            {"kind": "object", "source": "person", "target": "provider_fields.prismhr.person",
             "fields": [
                 {"kind": "list", "source": "emergencyContact", "target": "contacts",
                  "fields": [field("name", "name"),
                             field("_links.country-fields", "country_link")]},
             ]},
        ]
        validated = MappingConfig.model_validate(config(rules))
        self.assertEqual(validated.fields[0].source, "firstName")
        self.assertEqual(validated.fields[1].transform.name, "identifier")
        self.assertEqual(validated.fields[2].source_scope, "context")
        self.assertEqual(validated.fields[3].fields[0].fields[1].source, "_links.country-fields")

    def test_multi_source_mapping_is_one_rule_not_overwriting_rules(self):
        rule = field(["contactInformation.zipcode", "contactInformation.zipSuffix"],
                     "postal_code", transform={"name": "postal_code"})
        self.assertEqual(MappingConfig.model_validate(config([rule])).fields[0].source,
                         ["contactInformation.zipcode", "contactInformation.zipSuffix"])
        with self.assertRaises(ValidationError):
            MappingConfig.model_validate(config([field(["a", "b"])]))

    def test_rejects_unknown_helpers_and_configuration_typos(self):
        invalid = [
            field(transform={"name": "eval"}),
            field(transfrom={"name": "date"}),
            field(transform={"name": "date", "argumnts": {}}),
            {"kind": "condition", "source": "a", "target": "b"},
        ]
        for rule in invalid:
            with self.subTest(rule=rule), self.assertRaises(ValidationError):
                MappingConfig.model_validate(config([rule]))
        payload = config([field()])
        payload["provider_name"] = "prismhr"
        with self.assertRaises(ValidationError):
            MappingConfig.model_validate(payload)

    def test_rejects_ambiguous_or_empty_paths_and_implicit_array_traversal(self):
        for path in ("", " ", " person.id", "person..id", ".id", "person.",
                     "employee[].id", "contacts[0].name", "*", "$context.id"):
            for key in ("source", "target"):
                with self.subTest(path=path, key=key), self.assertRaises(ValidationError):
                    MappingConfig.model_validate(config([field(**{key: path})]))
        with self.assertRaises(ValidationError):
            MappingConfig.model_validate(config([field(source=[], transform={"name": "pronouns"})]))

    def test_rejects_duplicate_and_overlapping_targets_at_each_scope(self):
        for targets in (("name", "name"), ("person", "person.name"),
                        ("person.name", "person")):
            rules = [field("first", targets[0]), field("second", targets[1])]
            for kind in (None, "object", "list"):
                payload = config(rules if kind is None else [
                    {"kind": kind, "source": "records", "target": "records", "fields": rules}
                ])
                with self.subTest(targets=targets, kind=kind), self.assertRaisesRegex(
                        ValidationError, "Overlapping mapping targets"):
                    MappingConfig.model_validate(payload)
        # Different item scopes can legitimately have the same child field name.
        MappingConfig.model_validate(config([
            {"kind": "object", "source": "a", "target": "a", "fields": [field()]},
            {"kind": "object", "source": "b", "target": "b", "fields": [field()]},
        ]))

    def test_requires_supported_provider_entity_version_and_nonempty_rules(self):
        for patch in ({"version": "1"}, {"version": True}, {"version": 1.0},
                      {"version": 2}, {"provider": "ukg_ready"},
                      {"entity": "paycheck"}, {"fields": []}):
            with self.subTest(patch=patch), self.assertRaises(ValidationError):
                MappingConfig.model_validate({**config([field()]), **patch})
        for kind in ("object", "list"):
            with self.subTest(kind=kind), self.assertRaises(ValidationError):
                MappingConfig.model_validate(config([
                    {"kind": kind, "source": "a", "target": "b", "fields": []}
                ]))

    def test_transform_parameters_are_data_and_config_instances_are_independent(self):
        raw = config([field(transform={"name": "label", "arguments": {"labels": {"M": "married"}}})])
        first = MappingConfig.model_validate(raw)
        second = MappingConfig.model_validate(copy.deepcopy(raw))
        first.fields[0].transform.arguments["new"] = True
        self.assertNotIn("new", second.fields[0].transform.arguments)
        raw["fields"][0]["transform"]["arguments"] = {"callable": lambda: None}
        with self.assertRaises(ValidationError):
            MappingConfig.model_validate(raw)

    def test_schema_can_be_generated_and_round_trip_config(self):
        original = MappingConfig.model_validate(config([field()]))
        self.assertEqual(MappingConfig.model_validate_json(original.model_dump_json()), original)
        self.assertIn("$defs", MappingConfig.model_json_schema())


if __name__ == "__main__":
    unittest.main()
