"""Company output identity scopes, preservation and mapping-engine compatibility."""
import json
import unittest
from pydantic import ValidationError
from normalization.canonical_models.canonical_model_company import CanonicalCompany, CanonicalCompanyResult
from normalization.mapping_config import MappingConfig
from normalization.mapping_engine import MappingEngine
from normalization.source_models.isolved.isolved_source_model_company import IsolvedLegalModel


class CompanyCanonicalChecks(unittest.TestCase):
    def test_source_scoped_identity_and_strict_types(self):
        for provider, kind in [('prismhr', 'client'), ('isolved', 'legal_company'), ('ukg-ready', 'ein')]:
            record = CanonicalCompany(provider=provider, source_record_type=kind, source_record_id=None)
            self.assertIsNone(record.source_record_id)
            self.assertIsNone(record.legal_name)
        base = dict(provider='isolved', source_record_type='legal_company', source_record_id='007')
        for invalid in ({'provider': 'other'}, {'source_record_type': 'global_company'},
                        {'source_record_id': 7}, {'federal_tax_id': 123}, {'naics_code': 123},
                        {'company_id': 'invented'}, {'legal_name': 7}):
            with self.subTest(invalid=invalid), self.assertRaises(ValidationError):
                CanonicalCompany.model_validate({**base, **invalid})
        for key in base:
            with self.subTest(missing=key), self.assertRaises(ValidationError):
                CanonicalCompany.model_validate({k: v for k, v in base.items() if k != key})

    def test_ein_values_and_nested_parent_identity_are_not_promoted(self):
        record = CanonicalCompany(provider='ukg-ready', source_record_type='ein', source_record_id='003',
            ukg_ein_name='Source EIN label', ukg_ein_tax_id='000123',
            provider_fields={'ukg-ready': {'ein_country_id': 'source-country'}},
            source_extras={'ukg-ready': {'future_flag': False}})
        result = CanonicalCompanyResult(provider='ukg-ready', companies=[record])
        output = json.loads(result.model_dump_json(exclude_unset=True))['companies'][0]
        self.assertNotIn('legal_name', output)
        self.assertNotIn('federal_tax_id', output)
        self.assertEqual(output['ukg_ein_tax_id'], '000123')
        self.assertIs(output['source_extras']['ukg-ready']['future_flag'], False)
        self.assertEqual(output['source_record_type'], 'ein')

    def test_defaults_metadata_and_empty_result_preservation(self):
        first = CanonicalCompanyResult(provider='prismhr', source_metadata={
            'original_values': {'id': 7},
            'mapping_issues': [{'source_path': 'status', 'reason': 'Unknown meaning'}],
            'prismhr': {'response': {'errorCode': '0', 'extension': None}}})
        second = CanonicalCompanyResult(provider='prismhr')
        first.provider_fields['prismhr'] = {'settings': {'enabled': False}}
        self.assertEqual(second.provider_fields, {})
        self.assertEqual(first.companies, [])
        self.assertEqual(first.model_dump(mode='json')['source_metadata']['original_values'], {'id': 7})
        with self.assertRaises(ValidationError):
            CanonicalCompanyResult(provider='prismhr', source_metadata={'mapping_issues': [{'reason': 'missing path'}]})

    def test_existing_engine_preserves_nested_client_and_unmatched_values(self):
        configuration = MappingConfig.model_validate({'version': 1, 'provider': 'isolved', 'entity': 'company', 'fields': [
            {'kind': 'field', 'source': 'id', 'target': 'source_record_id', 'transform': {'name': 'identifier'}},
            {'kind': 'field', 'source': 'source_record_type', 'source_scope': 'context', 'target': 'source_record_type'},
            {'kind': 'field', 'source': 'legalName', 'target': 'legal_name'},
        ]})
        source = IsolvedLegalModel.model_validate({'id': 7, 'legalName': 'Example Legal',
            'client': {'id': 8, 'clientName': 'Parent name'}, 'allowRemoteWorkers': False,
            'future': {'value': None}})
        result = MappingEngine(configuration, IsolvedLegalModel, CanonicalCompany).map(
            source, context={'source_record_type': 'legal_company'})
        self.assertEqual(result.source_record_id, '7')
        self.assertEqual(result.legal_name, 'Example Legal')
        self.assertEqual(result.provider_fields['isolved']['unmapped']['client']['id'], 8)
        self.assertIs(result.provider_fields['isolved']['unmapped']['allowRemoteWorkers'], False)
        self.assertEqual(result.source_extras['isolved']['future'], {'value': None})
