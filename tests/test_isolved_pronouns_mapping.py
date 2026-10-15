"""Shared pronoun conflict handling and execution of complete isolved employee rules."""
import inspect
from importlib.resources import files
from pathlib import Path
import types
from typing import Any, Union, get_args, get_origin
import unittest

from pydantic import BaseModel

from normalization.canonical_models.canonical_model_employee import CanonicalEmployee
from normalization.helpers.mapping import pronouns, validate_helper
from normalization.mapping_engine import MappingEngine, load_mapping_config
from normalization.source_models.isolved.isolved_source_model_employee import IsolvedEmployeeInput


def full_record(model):
    model.model_rebuild()
    def value(annotation):
        if get_origin(annotation) in (Union, types.UnionType):
            return value(next(a for a in get_args(annotation) if a is not type(None)))
        if get_origin(annotation) is list:
            return [value(get_args(annotation)[0])]
        if get_origin(annotation) is dict:
            return {"synthetic": 0}
        if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
            return full_record(annotation)
        return {str: "synthetic", bool: False, int: 0, float: 0.0, Any: None}[annotation]
    return {name: value(field.annotation) for name, field in model.model_fields.items()}


class IsolvedPronounsChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        resource = files("normalization").joinpath("mappings/isolved/employee.yaml")
        cls.engine = MappingEngine(load_mapping_config(Path(str(resource))), IsolvedEmployeeInput, CanonicalEmployee)

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
        source = IsolvedEmployeeInput.model_validate({
            "id": 7, "eligibleForRehire": False, "gender": "Male", "maritalStatus": "Married",
            "employmentCategoryCode": "UNVERIFIED", "employmentStatus": "Terminated",
            "nameAddress": {"id": 10, "preferredPronouns": "she/her",
                            "links": [{"href": "/synthetic/name", "rel": "self", "method": "GET"}]},
            "personal": {"id": 11, "preferredPronouns": "they/them", "future_flag": False},
            "links": [{"href": "/synthetic/employee", "rel": "self", "method": "GET"}],
            "salary_history": [{"id": 12, "perPaySalary": 2500.0,
                                "seasons": [{"id": 13, "links": [{"href": "/synthetic/season"}]}]}],
        })
        result = self.engine.map(source)
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
        self.assertEqual(unmapped["salary_history"][0]["seasons"][0]["links"][0]["href"],
                         "/synthetic/season")
        history = result.provider_fields["isolved"]["salary_history"][0]
        self.assertEqual(history["id"], "12")
        self.assertEqual(history["seasons"][0]["id"], "13")
        self.assertIs(result.source_extras["isolved"]["personal"]["future_flag"], False)
        result.model_dump_json(exclude_unset=True)

    def test_absent_and_single_pronoun_fields_keep_presence_and_original_values(self):
        missing = self.engine.map(IsolvedEmployeeInput.model_validate({"id": 1}))
        self.assertNotIn("preferred_pronouns", missing.model_fields_set)
        for field in ("nameAddress", "personal"):
            with self.subTest(field=field):
                result = self.engine.map(IsolvedEmployeeInput.model_validate({
                    "id": 1, field: {"id": 2, "preferredPronouns": "they/them"},
                }))
                self.assertEqual(result.preferred_pronouns, "they/them")
                self.assertIn(field + ".preferredPronouns", result.source_metadata.original_values)
                other = "personal" if field == "nameAddress" else "nameAddress"
                self.assertNotIn(other + ".preferredPronouns", result.source_metadata.original_values)
                self.assertEqual(result.source_metadata.mapping_issues, [])

    def test_every_nested_section_executes_and_serializes_using_existing_engine(self):
        source = IsolvedEmployeeInput.model_validate(full_record(IsolvedEmployeeInput))
        result = self.engine.map(source)
        self.assertEqual(result.preferred_pronouns, "synthetic")
        self.assertEqual(result.employee_id, "0")
        self.assertIn("direct_deposits", result.provider_fields["isolved"])
        self.assertIn("salary_history", result.provider_fields["isolved"])
        result.model_dump_json(exclude_unset=True)


if __name__ == "__main__":
    unittest.main()
