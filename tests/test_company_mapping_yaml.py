"""Company YAML execution preserves source identity, scope and recursive references."""
from importlib.resources import files
from pathlib import Path
import unittest

from normalization import contracts
from normalization.canonical_models.canonical_model_company import CanonicalCompany
from normalization.mapping_engine import MappingEngine, load_mapping_config

# Company record schemas from the contracts, as the adapters route them.
PRISM = contracts.response_schema("prismhr", "/clientMaster/v1/getClientMaster").at("clientMaster")
ISOLVED = contracts.response_schema("isolved", "/api/clients/{clientId}/legals").at("[]")
UKG = contracts.response_schema("ukg-ready", "/v2/companies/{cid}/lookup/eins").at("items[]")


def synthetic(schema, seen=()):
    """Synthetic record covering every contract-declared field (no customer data)."""
    node = schema.node
    kind = node.get("type")
    if isinstance(kind, list):
        kind = next((k for k in kind if k != "null"), None)
    if kind == "array" or (kind is None and "items" in node):
        return [synthetic(schema.items(), seen)]
    if kind == "object" or (kind is None and "properties" in node):
        if schema.is_open:
            return {"synthetic": False}
        if id(node) in seen:  # recursive reference: keep only its identity
            return {"id": synthetic(schema.child("id"), seen)} if "id" in schema.declared() else {}
        seen = seen + (id(node),)
        return {name: synthetic(schema.child(name), seen) for name in sorted(schema.declared())}
    return {"string": "synthetic", "integer": 0, "number": 0.0, "boolean": False}.get(kind)


class CompanyMappingYamlChecks(unittest.TestCase):
    variants = [('prismhr', PRISM, 'client'),
                ('isolved', ISOLVED, 'legal_company'),
                ('ukg_ready', UKG, 'ein')]

    def engine(self, module, schema):
        resource = files('normalization').joinpath(f'mappings/{module}/company.yaml')
        return MappingEngine(load_mapping_config(Path(str(resource))), schema, CanonicalCompany)

    def test_all_three_configs_validate_and_all_supplied_sections_serialize(self):
        for module, schema, kind in self.variants:
            with self.subTest(module=module):
                payload = synthetic(schema)
                payload['future_flag'] = False
                result = self.engine(module, schema).map(payload, context={'source_record_type': kind})
                self.assertEqual(result.source_record_type, kind)
                self.assertEqual(result.source_record_id, 'synthetic' if module == 'prismhr' else '0')
                self.assertIs(result.source_extras[module.replace('_', '-')]['future_flag'], False)
                result.model_dump_json(exclude_unset=True)

    def test_prism_verified_names_identifiers_and_status_class_remain_distinct(self):
        source = {'id': '0007', 'legalName': 'Example Legal',
            'clientName': 'Example Trade', 'federalIdNumber': '001234', 'naicsCode': '00120',
            'statusClass': 'A', 'status': 'CUSTOM'}
        result = self.engine('prismhr', PRISM).map(source, context={'source_record_type': 'client'})
        self.assertEqual(result.source_record_id, '0007')
        self.assertEqual(result.legal_name, 'Example Legal')
        self.assertEqual(result.trade_name, 'Example Trade')
        self.assertEqual(result.federal_tax_id, '001234')
        self.assertEqual(result.naics_code, '00120')
        self.assertEqual(result.provider_fields['prismhr']['status_class'], 'active')
        self.assertEqual(result.provider_fields['prismhr']['status'], 'CUSTOM')

    def test_isolved_parent_and_recursive_records_do_not_replace_root_company(self):
        source = {'id': 7, 'legalName': 'Root Legal',
            'client': {'id': 8, 'clientName': 'Parent Client', 'legalCompanies': [
                {'id': 9, 'legalName': 'Nested Legal', 'future': False}]}}
        result = self.engine('isolved', ISOLVED).map(source, context={'source_record_type': 'legal_company'})
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
        source = {'id': 7, 'ein_name': 'Example EIN',
            'ein_tax_id': '001234', 'ein_currency_code': 'USD', 'ein_country_id': 'US'}
        result = self.engine('ukg_ready', UKG).map(source, context={'source_record_type': 'ein'})
        self.assertEqual(result.source_record_id, '7')
        self.assertEqual(result.ukg_ein_name, 'Example EIN')
        self.assertEqual(result.ukg_ein_tax_id, '001234')
        self.assertNotIn('legal_name', result.model_fields_set)
        self.assertNotIn('federal_tax_id', result.model_fields_set)
        self.assertEqual(result.provider_fields['ukg-ready']['ein_currency_code'], 'USD')
