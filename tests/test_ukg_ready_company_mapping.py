"""Company adapter integration with source-scoped identity and preserved context."""
import copy
import json
import unittest
from unittest.mock import patch
from normalization.adapters import ukg_ready as adapter
from normalization.mapping_engine import MappingEngine


class CompanyMappingChecks(unittest.TestCase):
    def test_ein_records_wrappers_and_extras_are_preserved_without_company_inference(self):
        payload = {'items': [{'id': 7, 'ein_name': 'EIN Label', 'ein_tax_id': '001234',
                   'ein_currency_code': 'USD', 'ein_country_id': 'US', 'future': False}, {'id': 8}],
                   'future_wrapper': {'flag': False}}
        before = copy.deepcopy(payload)
        result = adapter.normalize('company', payload, {})
        first, second = result['companies']
        self.assertEqual([first['source_record_id'], second['source_record_id']], ['7', '8'])
        self.assertEqual(first['source_record_type'], 'ein')
        self.assertEqual(first['ukg_ein_name'], 'EIN Label')
        self.assertEqual(first['ukg_ein_tax_id'], '001234')
        self.assertNotIn('legal_name', first)
        self.assertNotIn('federal_tax_id', first)
        self.assertEqual(first['provider_fields']['ukg-ready']['ein_currency_code'], 'USD')
        self.assertIs(first['source_extras']['ukg-ready']['future'], False)
        self.assertEqual(result['source_metadata']['ukg-ready']['response'],
                         {'future_wrapper': {'flag': False}})
        self.assertEqual(payload, before)
        json.dumps(result, allow_nan=False)

    def test_empty_items_preserve_wrapper_data(self):
        with patch.object(adapter, 'MappingEngine') as engine:
            result = adapter.normalize('company', {'items': [], 'future': False}, {})
        self.assertEqual(result['companies'], [])
        self.assertIs(result['source_metadata']['ukg-ready']['response']['future'], False)
        engine.assert_not_called()

    def test_source_response_and_engine_created_once_for_multiple_records(self):
        validate = adapter.UKGReadyEinsResponse.model_validate
        with patch.object(adapter.UKGReadyEinsResponse, 'model_validate', wraps=validate) as validation, \
             patch.object(adapter.UKGReadyEinsResponseItemsItem, 'model_validate') as repeated, \
             patch.object(adapter, 'MappingEngine', wraps=MappingEngine) as engine:
            adapter.normalize('company', {'items': [{'id': 7}, {'id': 8}]}, {})
        self.assertEqual(validation.call_count, 1)
        repeated.assert_not_called()
        self.assertEqual(engine.call_count, 1)
