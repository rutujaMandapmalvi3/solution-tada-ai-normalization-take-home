"""The packaged YAML example follows the rule and employee schema contracts."""
from importlib.resources import files
import unittest

import yaml

from normalization import contracts
from normalization.canonical_models.canonical_model_employee import CanonicalEmployee
from normalization.mapping_config import MappingConfig

PRISM_EMPLOYEE = contracts.response_schema("prismhr", "/employee/v1/getEmployee").at("employee[]")


class MappingYamlChecks(unittest.TestCase):
    def test_example_loads_safely_and_matches_validated_employee_fields(self):
        resource = files("normalization").joinpath("mappings/prismhr/employee.example.yaml")
        configuration = MappingConfig.model_validate(yaml.safe_load(resource.read_text()))
        self.assertEqual((configuration.provider, configuration.entity), ("prismhr", "employee"))
        self.assertEqual(len(configuration.fields), 4)

        source = {
            "id": "0007", "firstName": "Example",
            "person": {"birthDate": "2000-01-02", "employerIds": ["001", "002"]},
        }
        values = {}
        for rule in configuration.fields:
            # Check real contract/canonical names, without implementing the engine.
            value, schema = source, PRISM_EMPLOYEE
            for segment in rule.source.split("."):
                self.assertIn(segment, schema.declared())
                schema, value = schema.child(segment), value[segment]
            self.assertIn(rule.target, CanonicalEmployee.model_fields)
            values[rule.target] = value
        self.assertEqual(values["employee_id"], "0007")
        self.assertEqual(values["first_name"], "Example")
        self.assertEqual(values["birth_date"], "2000-01-02")
        self.assertEqual(values["prismhr_employer_ids"], ["001", "002"])
        self.assertEqual(configuration.fields[0].transform.name, "identifier")
        self.assertEqual(configuration.fields[2].transform.name, "date")


if __name__ == "__main__":
    unittest.main()
