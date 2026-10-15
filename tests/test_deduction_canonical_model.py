"""Shared deduction output validation and preservation contracts."""
import json
import unittest
from datetime import date, datetime

from pydantic import ValidationError

from normalization.canonical_models.canonical_model_deduction import CanonicalDeduction
from normalization.canonical_models.canonical_document import CanonicalDocument
from normalization.contracts import Schema
from normalization.mapping_config import MappingConfig
from normalization.mapping_engine import MappingEngine


class DeductionCanonicalChecks(unittest.TestCase):
    def test_identity_policy_and_strict_converted_values(self):
        for provider in ("prismhr", "isolved", "ukg-ready"):
            output = CanonicalDeduction(provider=provider, deduction_id=None)
            self.assertIsNone(output.deduction_id)
            self.assertEqual(output.provider_fields, {})
        for invalid in ([{"provider": "unknown"}, {"deduction_id": 123}, {"employee_id": 7},
                         {"undeclared_business_field": "value"}] + [{"deduction_code": 123}, {"start_date": "2026-01-02"}, {"start_date": datetime(2026, 1, 2)}, {"deduction_name": 123}]):
            with self.subTest(invalid=invalid), self.assertRaises(ValidationError):
                CanonicalDeduction.model_validate({"provider": "prismhr", "deduction_id": None, **invalid})
        with self.assertRaises(ValidationError):
            CanonicalDeduction(provider="prismhr")

    def test_business_values_and_json_serialization(self):
        record = CanonicalDeduction(provider="isolved", deduction_id="0007", employee_id="0002", **{"deduction_code": "001", "deduction_name": "Example", "description": "Separate description", "start_date": date(2026, 1, 2)})
        document = CanonicalDocument(provider="isolved",
                                     deductions=[record.model_dump(mode="json", exclude_unset=True)])
        data = json.loads(document.model_dump_json(exclude_unset=True))
        self.assertEqual(data["deductions"][0]["deduction_id"], "0007")
        self.assertEqual(data["deductions"][0]["employee_id"], "0002")
        for key, value in {"deduction_code": "001", "deduction_name": "Example", "description": "Separate description", "start_date": date(2026, 1, 2)}.items():
            self.assertEqual(data["deductions"][0][key], value.isoformat() if isinstance(value, date) else value)

    def test_empty_records_can_preserve_supplements_and_unexpected_items(self):
        # Supplements without records now live at document level (the per-entity
        # result wrapper was retired); record-level preservation is checked below.
        preserved = {"ukg-ready": {"code_lookup": {"items": [{"id": "4", "name": "Example"}]},
                                    "benefits": {"benefits": []}},
                     "isolved": {"non_deduction_items": [{"payItemType": "Earning", "amount": 0}]}}
        output = CanonicalDocument(provider="ukg-ready", provider_fields=preserved).model_dump(mode="json")
        self.assertEqual(output["deductions"], [])
        self.assertEqual(output["provider_fields"], preserved)
        record = CanonicalDeduction(provider="ukg-ready", deduction_id=None,
            source_extras={"ukg-ready": {"future_flag": False}},
            source_metadata={"ukg-ready": {"response": {"message": None}},
                             "original_values": {"sample": "raw"},
                             "mapping_issues": [{"source_path": "sample", "reason": "Unknown meaning"}]})
        dumped = record.model_dump(mode="json")
        self.assertIs(dumped["source_extras"]["ukg-ready"]["future_flag"], False)
        self.assertEqual(dumped["source_metadata"]["original_values"], {"sample": "raw"})
        json.dumps(dumped, allow_nan=False)

    def test_mutable_defaults_and_presence_are_preserved(self):
        first = CanonicalDeduction(provider="prismhr", deduction_id=None)
        second = CanonicalDeduction(provider="prismhr", deduction_id=None)
        first.provider_fields["prismhr"] = {"setting": False}
        first.source_extras["prismhr"] = {"x": 1}
        self.assertEqual(second.provider_fields, {})
        self.assertEqual(second.source_extras, {})
        omitted = CanonicalDeduction(provider="prismhr", deduction_id=None).model_dump(exclude_unset=True)
        supplied = CanonicalDeduction(provider="prismhr", deduction_id=None, employee_id=None).model_dump(exclude_unset=True)
        self.assertNotIn("employee_id", omitted)
        self.assertIsNone(supplied["employee_id"])
        with self.assertRaises(ValidationError):
            CanonicalDeduction(provider="isolved", deduction_id=None, source_metadata={"mapping_issues": [{"source_path": "id"}]})

    def test_common_engine_preserves_known_and_unknown_fields(self):
        source_schema = Schema({"type": "object", "properties": {
            "id": {"type": "integer"}, "setting": {"type": "boolean"}}}, {})

        config = MappingConfig.model_validate({"version": 1, "provider": "isolved", "entity": "deduction",
            "fields": [{"kind": "field", "source": "id", "target": "deduction_id", "transform": {"name": "identifier"}}]})
        engine = MappingEngine(config, source_schema, CanonicalDeduction)
        record = engine.map({"id": 7, "setting": False, "future": {"nested": None}},
                            metadata={"response": {"links": []}})
        self.assertEqual(record.deduction_id, "7")
        self.assertIs(record.provider_fields["isolved"]["unmapped"]["setting"], False)
        self.assertEqual(record.source_extras["isolved"]["future"], {"nested": None})
        self.assertEqual(record.source_metadata.original_values, {"id": 7})
        self.assertEqual(record.source_metadata.model_extra["isolved"]["response"], {"links": []})
