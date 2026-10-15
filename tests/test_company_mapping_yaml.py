"""Company YAML execution preserves source identity, scope and recursive references."""
import inspect
from importlib.resources import files
from pathlib import Path
import types
from typing import Any, Union, get_args, get_origin
import unittest

from pydantic import BaseModel
from normalization.canonical_models.canonical_model_company import CanonicalCompany
from normalization.mapping_engine import MappingEngine, load_mapping_config
from normalization.source_models.prismhr.prismhr_source_model_company import PrismHRClientMaster
from normalization.source_models.isolved.isolved_source_model_company import IsolvedLegalModel
from normalization.source_models.ukg_ready.ukg_ready_source_model_company import UKGReadyEinsResponseItemsItem


def synthetic(model, seen=()):
    model.model_rebuild()
    recursive = model in seen
    def value(t):
        if get_origin(t) in (Union, types.UnionType):
            return value(next(x for x in get_args(t) if x is not type(None)))
        if get_origin(t) is list:
            return [value(get_args(t)[0])]
        if get_origin(t) is dict:
            return {'future': False}
        if inspect.isclass(t) and issubclass(t, BaseModel):
            return synthetic(t, (*seen, model))
        return {str: 'synthetic', int: 0, float: 0.0, bool: False, Any: None}[t]
    return {(f.alias or n): value(f.annotation) for n, f in model.model_fields.items()
            if not recursive or n == 'id'}


class CompanyMappingYamlChecks(unittest.TestCase):
    variants = [('prismhr', PrismHRClientMaster, 'client'),
                ('isolved', IsolvedLegalModel, 'legal_company'),
                ('ukg_ready', UKGReadyEinsResponseItemsItem, 'ein')]

    def engine(self, module, model):
        resource = files('normalization').joinpath(f'mappings/{module}/company.yaml')
        return MappingEngine(load_mapping_config(Path(str(resource))), model, CanonicalCompany)

    def test_all_three_configs_validate_and_all_supplied_sections_serialize(self):
        for module, model, kind in self.variants:
            with self.subTest(module=module):
                payload = synthetic(model)
                payload['future_flag'] = False
                result = self.engine(module, model).map(model.model_validate(payload),
                                                       context={'source_record_type': kind})
                self.assertEqual(result.source_record_type, kind)
                self.assertEqual(result.source_record_id, 'synthetic' if module == 'prismhr' else '0')
                self.assertIs(result.source_extras[module.replace('_', '-')]['future_flag'], False)
                result.model_dump_json(exclude_unset=True)

    def test_prism_verified_names_identifiers_and_status_class_remain_distinct(self):
        source = PrismHRClientMaster.model_validate({'id': '0007', 'legalName': 'Example Legal',
            'clientName': 'Example Trade', 'federalIdNumber': '001234', 'naicsCode': '00120',
            'statusClass': 'A', 'status': 'CUSTOM'})
        result = self.engine('prismhr', PrismHRClientMaster).map(source, context={'source_record_type': 'client'})
        self.assertEqual(result.source_record_id, '0007')
        self.assertEqual(result.legal_name, 'Example Legal')
        self.assertEqual(result.trade_name, 'Example Trade')
        self.assertEqual(result.federal_tax_id, '001234')
        self.assertEqual(result.naics_code, '00120')
        self.assertEqual(result.provider_fields['prismhr']['status_class'], 'active')
        self.assertEqual(result.provider_fields['prismhr']['status'], 'CUSTOM')

    def test_isolved_parent_and_recursive_records_do_not_replace_root_company(self):
        source = IsolvedLegalModel.model_validate({'id': 7, 'legalName': 'Root Legal',
            'client': {'id': 8, 'clientName': 'Parent Client', 'legalCompanies': [
                {'id': 9, 'legalName': 'Nested Legal', 'future': False}]} })
        result = self.engine('isolved', IsolvedLegalModel).map(source, context={'source_record_type': 'legal_company'})
        self.assertEqual(result.source_record_id, '7')
        self.assertEqual(result.legal_name, 'Root Legal')
        parent = result.provider_fields['isolved']['client']
        self.assertEqual(parent['id'], '8')
        self.assertEqual(parent['client_name'], 'Parent Client')
        self.assertEqual(parent['legal_companies'][0]['id'], '9')
        remaining = result.provider_fields['isolved']['unmapped']['client']['legalCompanies'][0]
        self.assertEqual(remaining['legalName'], 'Nested Legal')
        self.assertIs(result.source_extras['isolved']['client']['legalCompanies'][0]['future'], False)

    def test_ukg_ein_fields_are_not_promoted_to_company_legal_or_federal_fields(self):
        source = UKGReadyEinsResponseItemsItem.model_validate({'id': 7, 'ein_name': 'Example EIN',
            'ein_tax_id': '001234', 'ein_currency_code': 'USD', 'ein_country_id': 'US'})
        result = self.engine('ukg_ready', UKGReadyEinsResponseItemsItem).map(source, context={'source_record_type': 'ein'})
        self.assertEqual(result.source_record_id, '7')
        self.assertEqual(result.ukg_ein_name, 'Example EIN')
        self.assertEqual(result.ukg_ein_tax_id, '001234')
        self.assertNotIn('legal_name', result.model_fields_set)
        self.assertNotIn('federal_tax_id', result.model_fields_set)
        self.assertEqual(result.provider_fields['ukg-ready']['ein_currency_code'], 'USD')
