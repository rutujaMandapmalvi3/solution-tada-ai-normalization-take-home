"""Shared pronoun conflict handling and execution of complete isolved employee rules."""
from importlib.resources import files
from pathlib import Path
import unittest

from normalization import contracts
from normalization.canonical_models.canonical_model_employee import CanonicalEmployee
from normalization.helpers.mapping import pronouns, validate_helper
from normalization.mapping_config import load_mapping_config
from normalization.mapping_engine import MappingEngine

DETAIL = "/api/clients/{clientId}/legals/{legalId}/employees/{id}"
SALARIES = "/api/clients/{clientId}/legals/{legalId}/employees/{employeeId}/salaries"


def full_record(schema, depth=0):
    """A synthetic value for every property the contract schema declares."""
    kind = schema.node.get("type")
    if schema.is_array:
        return [full_record(schema.items(), depth + 1)] if depth < 6 else []
    if schema.node.get("properties"):
        if depth >= 6:
            return {}
        return {name: full_record(schema.child(name), depth + 1) for name in sorted(schema.declared())}
    return {"string": "synthetic", "boolean": False, "integer": 0, "number": 0.0}.get(kind, None)


def engine(yaml_name, schema):
    resource = files("normalization").joinpath(f"mappings/isolved/{yaml_name}.yaml")
    return MappingEngine(load_mapping_config(Path(str(resource))), schema, CanonicalEmployee)


class IsolvedPronounsChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = contracts.response_schema("isolved", DETAIL)
        cls.engine = engine("employee", cls.schema)
        # Salary history is its own endpoint now, wrapped as {salary_history: [...]}.
        cls.salary_schema = contracts.response_schema("isolved", SALARIES).wrap("salary_history")
        cls.salary_engine = engine("employee_salaries", cls.salary_schema)

    def test_helper_handles_agreement_single_blank_and_conflicting_values(self):
        for first, second, expected in (
            (None, None, None), ("", None, ""), (None, "", ""), (" ", "", " "),
            ("they/them", None, "they/them"), (None, "they/them", "they/them"),
            ("", "they/them", "they/them"), ("they/them", " ", "they/them"),
            ("they/them", "they/them", "they/them"),
        ):
            with self.subTest(first=first, second=second):
                converted = pronouns(first, second)
                self.assertEqual(converted.value, expected)
                self.assertIsNone(converted.issue)
        for first, second in (("she/her", "they/them"), ("They/Them", "they/them"),
                              (False, "they/them"), ([], None)):
            with self.subTest(first=first, second=second):
                self.assertIsNone(pronouns(first, second).value)
                self.assertIsNotNone(pronouns(first, second).issue)
        validate_helper("pronouns", 2, {})
        for count in (1, 3):
            with self.subTest(count=count), self.assertRaises(ValueError):
                validate_helper("pronouns", count, {})

    def test_complete_yaml_preserves_conflicts_rehire_and_nested_link_positions(self):
        result = self.engine.map({
            "id": 7, "eligibleForRehire": False, "gender": "Male", "maritalStatus": "Married",
            "employmentCategoryCode": "UNVERIFIED", "employmentStatus": "Terminated",
            "nameAddress": {"id": 10, "preferredPronouns": "she/her",
                            "links": [{"href": "/synthetic/name", "rel": "self", "method": "GET"}]},
            "personal": {"id": 11, "preferredPronouns": "they/them", "future_flag": False},
            "links": [{"href": "/synthetic/employee", "rel": "self", "method": "GET"}],
        })
        self.assertEqual(result.employee_id, "7")
        self.assertIsNone(result.preferred_pronouns)
        self.assertEqual(result.gender, "male")
        self.assertEqual(result.marital_status, "married")
        self.assertEqual(result.eligible_for_rehire, "ineligible")
        self.assertEqual(result.employment_status, "terminated")
        self.assertIsNone(result.employment_type)
        originals = result.source_metadata.original_values
        self.assertEqual(originals["nameAddress.preferredPronouns"], "she/her")
        self.assertEqual(originals["personal.preferredPronouns"], "they/them")
        self.assertEqual(result.provider_fields["isolved"]["employment_category_code"], "UNVERIFIED")
        self.assertNotIn("employmentCategoryCode", originals)
        self.assertEqual({issue.source_path for issue in result.source_metadata.mapping_issues},
                         {"nameAddress.preferredPronouns"})
        unmapped = result.provider_fields["isolved"]["unmapped"]
        self.assertEqual(unmapped["links"][0]["href"], "/synthetic/employee")
        self.assertEqual(unmapped["nameAddress"]["links"][0]["href"], "/synthetic/name")
        self.assertIs(result.source_extras["isolved"]["personal"]["future_flag"], False)
        result.model_dump_json(exclude_unset=True)

    def test_salary_history_rules_keep_ids_and_nested_link_positions(self):
        result = self.salary_engine.map(
            {"salary_history": [{"id": 12, "perPaySalary": 2500.0,
                                 "seasons": [{"id": 13, "links": [{"href": "/synthetic/season"}]}]}]},
            context={"employee_id": "7"})
        self.assertEqual(result.employee_id, "7")
        history = result.provider_fields["isolved"]["salary_history"][0]
        self.assertEqual(history["id"], "12")
        self.assertEqual(history["seasons"][0]["id"], "13")
        unmapped = result.provider_fields["isolved"]["unmapped"]
        self.assertEqual(unmapped["salary_history"][0]["seasons"][0]["links"][0]["href"], "/synthetic/season")

    def test_absent_and_single_pronoun_fields_keep_presence_and_original_values(self):
        missing = self.engine.map({"id": 1})
        self.assertNotIn("preferred_pronouns", missing.model_fields_set)
        for field in ("nameAddress", "personal"):
            with self.subTest(field=field):
                result = self.engine.map({"id": 1, field: {"id": 2, "preferredPronouns": "they/them"}})
                self.assertEqual(result.preferred_pronouns, "they/them")
                self.assertIn(field + ".preferredPronouns", result.source_metadata.original_values)
                other = "personal" if field == "nameAddress" else "nameAddress"
                self.assertNotIn(other + ".preferredPronouns", result.source_metadata.original_values)
                self.assertEqual(result.source_metadata.mapping_issues, [])

    def test_every_nested_section_executes_and_serializes_using_existing_engine(self):
        result = self.engine.map(full_record(self.schema))
        self.assertEqual(result.preferred_pronouns, "synthetic")
        self.assertEqual(result.employee_id, "0")
        self.assertIn("direct_deposits", result.provider_fields["isolved"])
        result.model_dump_json(exclude_unset=True)
        salary = self.salary_engine.map(full_record(self.salary_schema), context={"employee_id": "0"})
        self.assertIn("salary_history", salary.provider_fields["isolved"])
        salary.model_dump_json(exclude_unset=True)


if __name__ == "__main__":
    unittest.main()
