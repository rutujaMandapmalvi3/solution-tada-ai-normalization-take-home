"""Company adapter integration with source-scoped identity and preserved context."""
import copy
import json
import unittest
from unittest.mock import patch
from normalization.adapters import isolved as adapter
from normalization.mapping_engine import MappingEngine


class CompanyMappingChecks(unittest.TestCase):
    def test_legal_root_parent_and_nested_records_keep_separate_identity(self):
        payload = {'id': 7, 'legalName': 'Root Legal', 'dbaName': 'Trade', 'federalEIN': '001234',
                   'client': {'id': 8, 'clientName': 'Parent', 'legalCompanies': [
                       {'id': 9, 'legalName': 'Nested', 'future': False}]},
                   'links': [{'href': '/synthetic/legal', 'method': 'GET'}], 'future': {'flag': False}}
        before = copy.deepcopy(payload)
        result = adapter.normalize('company', payload, {})
        record = result['companies'][0]
        self.assertEqual(record['source_record_id'], '7')
        self.assertEqual(record['source_record_type'], 'legal_company')
        self.assertEqual(record['legal_name'], 'Root Legal')
        self.assertEqual(record['trade_name'], 'Trade')
        parent = record['provider_fields']['isolved']['client']
        self.assertEqual(parent['id'], '8')
        self.assertEqual(parent['legal_companies'][0]['id'], '9')
        self.assertEqual(record['provider_fields']['isolved']['unmapped']['client']['legalCompanies'][0]['legalName'], 'Nested')
        self.assertEqual(record['provider_fields']['isolved']['unmapped']['links'][0]['href'], '/synthetic/legal')
        self.assertIs(record['source_extras']['isolved']['future']['flag'], False)
        self.assertEqual(payload, before)
        self.assertNotIn('response', result['source_metadata'])
        json.dumps(result, allow_nan=False)

    def test_nullable_source_identity_remains_null_without_new_identity(self):
        result = adapter.normalize('company', {'id': None, 'legalName': None}, {})
        self.assertIsNone(result['companies'][0]['source_record_id'])
        self.assertIsNone(result['companies'][0]['legal_name'])

    def test_native_legal_record_is_validated_once(self):
        validate = adapter.IsolvedLegalModel.model_validate
        with patch.object(adapter.IsolvedLegalModel, 'model_validate', wraps=validate) as validation:
            adapter.normalize('company', {'id': 7}, {})
        self.assertEqual(validation.call_count, 1)
