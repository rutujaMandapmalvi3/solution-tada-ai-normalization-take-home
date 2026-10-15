"""Boolean isolved input uses the same canonical rehire labels as PrismHR."""
from importlib.resources import files
from pathlib import Path
import unittest

from normalization.canonical_models.canonical_model_employee import CanonicalEmployee
from normalization.helpers.mapping import label
from normalization.mapping_config import MappingConfig
from normalization.mapping_engine import MappingEngine, load_mapping_config
from normalization.source_models.isolved.isolved_source_model_employee import IsolvedEmployeeInput


class IsolvedRehireMappingChecks(unittest.TestCase):
    def test_yaml_rehire_rule_maps_booleans_and_retains_original_values(self):
        resource = files("normalization").joinpath("mappings/isolved/employee.yaml")
        full_config = load_mapping_config(Path(str(resource)))
        # Exercise the actual YAML rules without claiming the pronouns helper exists.
        rules = [rule.model_dump() for rule in full_config.fields
                 if rule.target in ("employee_id", "eligible_for_rehire")]
        config = MappingConfig.model_validate({
            "version": 1, "provider": "isolved", "entity": "employee", "fields": rules,
        })
        engine = MappingEngine(config, IsolvedEmployeeInput, CanonicalEmployee)
        for supplied, expected in ((True, "eligible"), (False, "ineligible"), (None, None)):
            with self.subTest(supplied=supplied):
                employee = IsolvedEmployeeInput.model_validate({"id": 7, "eligibleForRehire": supplied})
                result = engine.map(employee)
                self.assertEqual(result.employee_id, "7")
                self.assertEqual(result.eligible_for_rehire, expected)
                self.assertIs(result.source_metadata.original_values["eligibleForRehire"], supplied)
                self.assertEqual(result.source_metadata.mapping_issues, [])
                self.assertEqual(result.model_dump(mode="json")["eligible_for_rehire"], expected)
        missing = engine.map(IsolvedEmployeeInput.model_validate({"id": 7}))
        self.assertNotIn("eligible_for_rehire", missing.model_fields_set)
        self.assertNotIn("eligibleForRehire", missing.source_metadata.original_values)

    def test_boolean_translation_requires_explicit_yaml_labels(self):
        for value, expected in ((True, "eligible"), (False, "ineligible")):
            with self.subTest(value=value):
                result = label(value, labels={"true": "eligible", "false": "ineligible"})
                self.assertEqual(result.value, expected)
                self.assertIsNone(result.issue)
                result = label(value, labels={"M": "male"})
                self.assertIsNone(result.value)
                self.assertIsNotNone(result.issue)
        for value in (0, 1):
            with self.subTest(value=value):
                result = label(value, labels={"true": "eligible", "false": "ineligible"})
                self.assertIsNone(result.value)
                self.assertIsNotNone(result.issue)


if __name__ == "__main__":
    unittest.main()
