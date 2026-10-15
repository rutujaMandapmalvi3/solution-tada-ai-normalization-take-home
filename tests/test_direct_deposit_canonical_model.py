"""Shared direct_deposit output validation and preservation contracts."""
import json
import unittest
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, ValidationError

from normalization.canonical_models.canonical_model_direct_deposit import CanonicalDirectDeposit, CanonicalDirectDepositResult
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
        result = CanonicalDirectDepositResult(provider="isolved", direct_deposits=[record])
        data = json.loads(result.model_dump_json(exclude_unset=True))
        self.assertEqual(data["direct_deposits"][0]["deposit_id"], "0007")
        self.assertEqual(data["direct_deposits"][0]["employee_id"], "0002")
        for key, value in {"account_number": "000123", "routing_number": "001234567", "allocation_amount": 0.0, "sequence": 0}.items():
            self.assertEqual(data["direct_deposits"][0][key], value.isoformat() if isinstance(value, date) else value)

    def test_empty_records_can_preserve_supplements_and_unexpected_items(self):
        preserved = {"ukg-ready": {"settings": {"active": False},
                                    "unmapped": {"_links": {"self": "/synthetic"}}},
                     "isolved": {"non_deduction_items": [{"payItemType": "Earning", "amount": 0}]}}
        result = CanonicalDirectDepositResult(provider="ukg-ready", provider_fields=preserved,
            source_extras={"ukg-ready": {"future_flag": False}},
            source_metadata={"ukg-ready": {"response": {"message": None}},
                             "original_values": {"sample": "raw"},
                             "mapping_issues": [{"source_path": "sample", "reason": "Unknown meaning"}]})
        output = result.model_dump(mode="json")
        self.assertEqual(output["direct_deposits"], [])
        self.assertEqual(output["provider_fields"], preserved)
        self.assertIs(output["source_extras"]["ukg-ready"]["future_flag"], False)
        self.assertEqual(output["source_metadata"]["original_values"], {"sample": "raw"})
        json.dumps(output, allow_nan=False)

    def test_mutable_defaults_and_presence_are_preserved(self):
        first = CanonicalDirectDepositResult(provider="prismhr")
        second = CanonicalDirectDepositResult(provider="prismhr")
        first.provider_fields["prismhr"] = {"setting": False}
        first.direct_deposits.append(CanonicalDirectDeposit(provider="prismhr", deposit_id=None))
        self.assertEqual(second.provider_fields, {})
        self.assertEqual(second.direct_deposits, [])
        omitted = CanonicalDirectDeposit(provider="prismhr", deposit_id=None).model_dump(exclude_unset=True)
        supplied = CanonicalDirectDeposit(provider="prismhr", deposit_id=None, employee_id=None).model_dump(exclude_unset=True)
        self.assertNotIn("employee_id", omitted)
        self.assertIsNone(supplied["employee_id"])
        with self.assertRaises(ValidationError):
            CanonicalDirectDepositResult(provider="isolved", source_metadata={"mapping_issues": [{"source_path": "id"}]})

    def test_common_engine_preserves_known_and_unknown_fields(self):
        class Source(BaseModel):
            model_config = ConfigDict(extra="allow")
            id: int
            setting: bool

        config = MappingConfig.model_validate({"version": 1, "provider": "isolved", "entity": "direct_deposit",
            "fields": [{"kind": "field", "source": "id", "target": "deposit_id", "transform": {"name": "identifier"}}]})
        engine = MappingEngine(config, Source, CanonicalDirectDeposit)
        record = engine.map(Source.model_validate({"id": 7, "setting": False, "future": {"nested": None}}),
                            metadata={"response": {"links": []}})
        self.assertEqual(record.deposit_id, "7")
        self.assertIs(record.provider_fields["isolved"]["unmapped"]["setting"], False)
        self.assertEqual(record.source_extras["isolved"]["future"], {"nested": None})
        self.assertEqual(record.source_metadata.original_values, {"id": 7})
        self.assertEqual(record.source_metadata.model_extra["isolved"]["response"], {"links": []})
