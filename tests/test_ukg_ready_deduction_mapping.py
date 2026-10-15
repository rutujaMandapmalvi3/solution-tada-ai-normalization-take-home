"""Deduction adapter selection, identity and source preservation."""
import copy
import json
import unittest
from unittest.mock import patch
from normalization.adapters import ukg_ready as adapter
from normalization.mapping_engine import MappingEngine


class DeductionMappingChecks(unittest.TestCase):
    def test_only_assignments_are_mapped_and_supplements_keep_source_scope(self):
        payload = {'assignments': {'deductions': [{'id': 1, 'deduction': {'code': '001', 'name': 'Example'},
                       'effective_from': '2026-01-02', '_links': {'self': '/synthetic/deduction'}, 'future': False}]},
                   'code_lookup': {'items': [{'id': 2, 'code': '001', 'name': 'Catalog', 'future': False}]},
                   'benefits': {'benefits': [{'id': 3, 'employee': {'account_id': 99},
                       'benefit_plan': {'id': 4}, 'name': 'Enrollment'}]}, 'future_wrapper': False}
        before = copy.deepcopy(payload)
        result = adapter.normalize('deduction', payload, {}, employee_id='007')
        self.assertEqual(len(result['deductions']), 1)
        record = result['deductions'][0]
        self.assertEqual(record['deduction_id'], '1')
        self.assertEqual(record['employee_id'], '007')
        self.assertEqual(record['provider_fields']['ukg-ready']['deduction']['code'], '001')
        self.assertEqual(record['provider_fields']['ukg-ready']['unmapped']['_links']['self'], '/synthetic/deduction')
        self.assertIs(record['source_extras']['ukg-ready']['future'], False)
        fields = result['provider_fields']['ukg-ready']
        self.assertEqual(fields['code_lookup']['items'][0]['id'], 2)
        self.assertEqual(fields['benefits']['benefits'][0]['employee']['account_id'], 99)
        self.assertIs(result['source_extras']['ukg-ready']['code_lookup']['items'][0]['future'], False)
        self.assertIs(result['source_extras']['ukg-ready']['future_wrapper'], False)
        self.assertEqual(payload, before)
        json.dumps(result, allow_nan=False)

    def test_supplements_only_are_not_discarded_or_created_as_deductions(self):
        payload = {'code_lookup': {'items': [{'id': None, 'code': '001'}]},
                   'benefits': {'benefits': [{'id': 3}]}}
        with patch.object(adapter, 'MappingEngine') as factory:
            result = adapter.normalize('deduction', payload, {}, employee_id='007')
        self.assertEqual(result['deductions'], [])
        self.assertEqual(result['provider_fields']['ukg-ready'], payload)
        factory.assert_not_called()

    def test_native_sections_preserve_unknowns_and_map_assignments_once(self):
        payload = {'deductions': [{'id': 1}], 'items': [{'id': 2, 'code': '001'}],
                   'benefits': [{'id': 3}], 'future': False}
        result = adapter.normalize('deduction', payload, {}, employee_id='007')
        self.assertEqual([x['deduction_id'] for x in result['deductions']], ['1'])
        fields = result['provider_fields']['ukg-ready']
        self.assertEqual(fields['code_lookup']['items'][0]['id'], 2)
        self.assertEqual(fields['benefits']['benefits'][0]['id'], 3)
        self.assertIs(result['source_extras']['ukg-ready']['future'], False)

    def test_empty_assignment_and_optional_supplement_values_are_preserved(self):
        for payload in [{}, {'assignments': None}, {'assignments': {'deductions': []}},
                        {'code_lookup': None, 'benefits': None}, {'items': []}, {'benefits': []}]:
            with self.subTest(payload=payload):
                result = adapter.normalize('deduction', payload, {}, employee_id='007')
                self.assertEqual(result['deductions'], [])
                if payload.get('assignments') == {'deductions': []}:
                    self.assertEqual(result['provider_fields']['ukg-ready']['unmapped']['assignments'],
                                     {'deductions': []})
