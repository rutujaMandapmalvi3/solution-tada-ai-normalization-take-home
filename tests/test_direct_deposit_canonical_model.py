"""Shared direct_deposit output validation and preservation contracts."""
import json
import unittest
from datetime import date, datetime

from pydantic import ValidationError

from normalization.canonical_models.canonical_model_direct_deposit import CanonicalDirectDeposit
from normalization.canonical_models.canonical_document import CanonicalDocument
from normalization.contracts import Schema
from normalization.mapping_config import MappingConfig
from normalization.mapping_engine import MappingEngine


class DirectDepositCanonicalChecks(unittest.TestCase):
    def test_identity_policy_and_strict_converted_values(self):
        for provider in ("prismhr", "isolved", "ukg-ready"):
            output = CanonicalDirectDeposit(provider=provider, deposit_id=None)
            self.assertIsNone(output.deposit_id)
            self.assertEqual(output.provider_fields, {})
        for invalid in ([{"provider": "unknown"}, {"deposit_id": 123}, {"employee_id": 7},
                         {"undeclared_business_field": "value"}] + [{"account_number": 123}, {"allocation_amount": "12.50"}, {"allocation_amount": float("inf")}, {"allocation_percentage": float("nan")}, {"sequence": 1.5}]):
            with self.subTest(invalid=invalid), self.assertRaises(ValidationError):
                CanonicalDirectDeposit.model_validate({"provider": "prismhr", "deposit_id": None, **invalid})
        with self.assertRaises(ValidationError):
            CanonicalDirectDeposit(provider="prismhr")

    def test_business_values_and_json_serialization(self):
        record = CanonicalDirectDeposit(provider="isolved", deposit_id="0007", employee_id="0002", **{"account_number": "000123", "routing_number": "001234567", "allocation_amount": 0.0, "sequence": 0})
        document = CanonicalDocument(provider="isolved",
                                     direct_deposits=[record.model_dump(mode="json", exclude_unset=True)])
        data = json.loads(document.model_dump_json(exclude_unset=True))
        self.assertEqual(data["direct_deposits"][0]["deposit_id"], "0007")
        self.assertEqual(data["direct_deposits"][0]["employee_id"], "0002")
        for key, value in {"account_number": "000123", "routing_number": "001234567", "allocation_amount": 0.0, "sequence": 0}.items():
            self.assertEqual(data["direct_deposits"][0][key], value.isoformat() if isinstance(value, date) else value)

    def test_empty_records_can_preserve_supplements_and_unexpected_items(self):
        # Supplements without records now live at document level (the per-entity
        # result wrapper was retired); record-level preservation is checked below.
        preserved = {"ukg-ready": {"settings": {"active": False},
                                    "unmapped": {"_links": {"self": "/synthetic"}}},
                     "isolved": {"non_deduction_items": [{"payItemType": "Earning", "amount": 0}]}}
        output = CanonicalDocument(provider="ukg-ready", provider_fields=preserved).model_dump(mode="json")
        self.assertEqual(output["direct_deposits"], [])
        self.assertEqual(output["provider_fields"], preserved)
        record = CanonicalDirectDeposit(provider="ukg-ready", deposit_id=None,
            source_extras={"ukg-ready": {"future_flag": False}},
            source_metadata={"ukg-ready": {"response": {"message": None}},
                             "original_values": {"sample": "raw"},
                             "mapping_issues": [{"source_path": "sample", "reason": "Unknown meaning"}]})
        dumped = record.model_dump(mode="json")
        self.assertIs(dumped["source_extras"]["ukg-ready"]["future_flag"], False)
        self.assertEqual(dumped["source_metadata"]["original_values"], {"sample": "raw"})
        json.dumps(dumped, allow_nan=False)

    def test_mutable_defaults_and_presence_are_preserved(self):
        first = CanonicalDirectDeposit(provider="prismhr", deposit_id=None)
        second = CanonicalDirectDeposit(provider="prismhr", deposit_id=None)
        first.provider_fields["prismhr"] = {"setting": False}
        first.source_extras["prismhr"] = {"x": 1}
        self.assertEqual(second.provider_fields, {})
        self.assertEqual(second.source_extras, {})
        omitted = CanonicalDirectDeposit(provider="prismhr", deposit_id=None).model_dump(exclude_unset=True)
        supplied = CanonicalDirectDeposit(provider="prismhr", deposit_id=None, employee_id=None).model_dump(exclude_unset=True)
        self.assertNotIn("employee_id", omitted)
        self.assertIsNone(supplied["employee_id"])
        with self.assertRaises(ValidationError):
            CanonicalDirectDeposit(provider="isolved", deposit_id=None, source_metadata={"mapping_issues": [{"source_path": "id"}]})

    def test_common_engine_preserves_known_and_unknown_fields(self):
        source_schema = Schema({"type": "object", "properties": {
            "id": {"type": "integer"}, "setting": {"type": "boolean"}}}, {})

        config = MappingConfig.model_validate({"version": 1, "provider": "isolved", "entity": "direct_deposit",
            "fields": [{"kind": "field", "source": "id", "target": "deposit_id", "transform": {"name": "identifier"}}]})
        engine = MappingEngine(config, source_schema, CanonicalDirectDeposit)
        record = engine.map({"id": 7, "setting": False, "future": {"nested": None}},
                            metadata={"response": {"links": []}})
        self.assertEqual(record.deposit_id, "7")
        self.assertIs(record.provider_fields["isolved"]["unmapped"]["setting"], False)
        self.assertEqual(record.source_extras["isolved"]["future"], {"nested": None})
        self.assertEqual(record.source_metadata.original_values, {"id": 7})
        self.assertEqual(record.source_metadata.model_extra["isolved"]["response"], {"links": []})
