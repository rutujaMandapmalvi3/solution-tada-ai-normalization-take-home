"""Common employee output contract, independent of provider input validation."""
import json
import unittest
from datetime import date, datetime

from pydantic import ValidationError

from normalization.canonical_models.canonical_model_employee import CanonicalEmployee


class EmployeeCanonicalChecks(unittest.TestCase):
    def test_all_providers_use_same_minimal_output_and_nullable_record_id(self):
        for provider in ("prismhr", "isolved", "ukg-ready"):
            with self.subTest(provider=provider):
                employee = CanonicalEmployee(provider=provider, employee_id=None)
                self.assertIsNone(employee.employee_id)
                self.assertIsNone(employee.first_name)
                self.assertIsNone(employee.prismhr_employer_ids)
                self.assertEqual(employee.provider_fields, {})
                self.assertEqual(employee.source_extras, {})
        for payload in ({}, {"provider": "prismhr"}, {"employee_id": "001"}):
            with self.subTest(payload=payload), self.assertRaises(ValidationError):
                CanonicalEmployee.model_validate(payload)

    def test_mapper_must_supply_converted_types_and_declared_fields(self):
        for invalid in (
            {"provider": "unknown"}, {"employee_id": 123},
            {"ukg_ein_id": 123}, {"prismhr_employer_ids": [123]},
            {"birth_date": "2000-01-02"},
            {"birth_date": datetime(2000, 1, 2, 0, 0)},
            {"hourly_rate": "25.50"}, {"hourly_rate": float("inf")},
            {"hourly_rate": float("nan")}, {"eligible_for_rehire": True},
            {"first_nmae": "Example"},
        ):
            with self.subTest(invalid=invalid), self.assertRaises(ValidationError):
                CanonicalEmployee.model_validate(
                    {"provider": "prismhr", "employee_id": "001", **invalid}
                )

    def test_readable_labels_are_not_provider_codes(self):
        for field, valid, invalid in (
            ("gender", ["male", "female", "non-binary", "declined", "unknown", "", None], "M"),
            ("marital_status", ["single", "married", "divorced", "widowed", "civil union", "other", "", None], "S"),
            ("eligible_for_rehire", ["eligible", "ineligible", "no preference", None], ""),
            ("prismhr_employment_status_class", ["active", "on leave", "terminated", "", None], "A"),
            ("other_pay_rate_basis", ["hourly", "weekly", "bi-weekly", "semi-monthly", "monthly", "yearly", "", None], "H"),
        ):
            for value in valid:
                with self.subTest(field=field, value=value):
                    employee = CanonicalEmployee(
                        provider="isolved", employee_id="001", **{field: value}
                    )
                    self.assertEqual(getattr(employee, field), value)
            with self.subTest(field=field), self.assertRaises(ValidationError):
                CanonicalEmployee(provider="isolved", employee_id="001", **{field: invalid})

    def test_serialization_preserves_nesting_extras_and_source_provenance(self):
        employee = CanonicalEmployee(
            provider="prismhr", employee_id="0007", birth_date=date(2000, 1, 2),
            hourly_rate=0.0, is_hispanic=False, prismhr_employer_ids=["001", "002"],
            provider_fields={"prismhr": {"person": {"emergency_contacts": []}}},
            source_extras={"prismhr": {"client": [{"new_flag": False}, {"new_value": None}]}},
            source_metadata={
                "prismhr": {"errorCode": "0", "infoMessage": ["Informational"]},
                "original_values": {"person.gender": "B"},
                "mapping_issues": [{"source_path": "person.gender", "reason": "Unmapped code"}],
            },
        )
        output = employee.model_dump(mode="json", exclude_unset=True)
        self.assertEqual(output["birth_date"], "2000-01-02")
        self.assertEqual(output["employee_id"], "0007")
        self.assertEqual(output["prismhr_employer_ids"], ["001", "002"])
        self.assertEqual(output["hourly_rate"], 0.0)
        self.assertIs(output["is_hispanic"], False)
        self.assertEqual(output["source_extras"], employee.source_extras)
        self.assertEqual(output["source_metadata"]["original_values"], {"person.gender": "B"})
        self.assertEqual(output["source_metadata"]["prismhr"]["infoMessage"], ["Informational"])
        self.assertEqual(json.loads(employee.model_dump_json())["birth_date"], "2000-01-02")
        self.assertNotIn("termination_date", output)

    def test_absent_null_and_empty_values_remain_distinguishable(self):
        for supplied in ({}, {"prismhr_employer_ids": None}, {"prismhr_employer_ids": []}):
            employee = CanonicalEmployee(provider="prismhr", employee_id="1", **supplied)
            output = employee.model_dump(mode="json", exclude_unset=True)
            self.assertEqual("prismhr_employer_ids" in output, "prismhr_employer_ids" in supplied)
            if supplied:
                self.assertEqual(output["prismhr_employer_ids"], supplied["prismhr_employer_ids"])

    def test_mutable_containers_are_independent_and_issue_records_are_typed(self):
        first = CanonicalEmployee(provider="isolved", employee_id="1")
        second = CanonicalEmployee(provider="isolved", employee_id="2")
        first.provider_fields["isolved"] = {"value": 1}
        first.source_extras["isolved"] = {"future": 1}
        first.source_metadata.original_values["gender"] = "unmapped"
        self.assertEqual(second.provider_fields, {})
        self.assertEqual(second.source_extras, {})
        self.assertEqual(second.source_metadata.original_values, {})
        with self.assertRaises(ValidationError):
            CanonicalEmployee(
                provider="isolved", employee_id="1",
                source_metadata={"mapping_issues": [{"source_path": "gender"}]},
            )


if __name__ == "__main__":
    unittest.main()
