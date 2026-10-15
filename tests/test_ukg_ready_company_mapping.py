"""UKG company: the cid company record plus EIN records linked to it."""
import copy
import json
import unittest
from unittest.mock import patch

from bundle_helpers import UKG, UKG_CO, run_one
from normalization import contracts, pipeline
from normalization.mapping_engine import MappingEngine

EINS = UKG_CO + "/lookup/eins"


class CompanyMappingChecks(unittest.TestCase):
    def test_ein_records_wrappers_and_extras_are_preserved_without_company_inference(self):
        payload = {'items': [{'id': 7, 'ein_name': 'EIN Label', 'ein_tax_id': '001234',
                   'ein_currency_code': 'USD', 'ein_country_id': 'US', 'future': False}, {'id': 8}],
                   'future_wrapper': {'flag': False}}
        before = copy.deepcopy(payload)
        result = run_one("ukg-ready", EINS, payload, **UKG)
        root, first, second = result['companies']
        self.assertEqual((root['id'], root['source_record_type'], root['source_record_id']),
                         ('ukg-ready:company:001', 'company', '001'))
        self.assertEqual([first['source_record_id'], second['source_record_id']], ['7', '8'])
        self.assertEqual(first['source_record_type'], 'ein')
        self.assertEqual(first['company_ref'], 'ukg-ready:company:001')
        self.assertEqual(first['ukg_ein_name'], 'EIN Label')
        self.assertEqual(first['ukg_ein_tax_id'], '001234')
        self.assertNotIn('legal_name', first)
        self.assertNotIn('federal_tax_id', first)
        self.assertEqual(first['provider_fields']['ukg-ready']['ein_currency_code'], 'USD')
        self.assertIs(first['source_extras']['ukg-ready']['future'], False)
        # The response body is the cid company record, so its other fields stay with it.
        self.assertEqual(root['source_extras']['ukg-ready']['future_wrapper'], {'flag': False})
        self.assertEqual(payload, before)
        json.dumps(result, allow_nan=False)

    def test_empty_items_still_produce_the_cid_company(self):
        result = run_one("ukg-ready", EINS, {'items': [], 'future': False}, **UKG)
        self.assertEqual([c['id'] for c in result['companies']], ['ukg-ready:company:001'])
        self.assertIs(result['companies'][0]['source_extras']['ukg-ready']['future'], False)

    def test_one_validation_and_one_engine_per_route_for_multiple_records(self):
        with patch.object(contracts, 'validate', wraps=contracts.validate) as validation, \
             patch.object(pipeline, 'MappingEngine', wraps=MappingEngine) as engine:
            result = run_one("ukg-ready", EINS, {'items': [{'id': 7}, {'id': 8}]}, **UKG)
        self.assertEqual(len(result['companies']), 3)
        self.assertEqual(validation.call_count, 1)
        self.assertEqual(engine.call_count, 2)  # cid company route + EIN route, not per record
