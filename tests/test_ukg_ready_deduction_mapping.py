"""UKG deductions: assignments mapped; code catalog and benefits kept as unrouted responses."""
import copy
import json
import unittest
from unittest.mock import patch

from bundle_helpers import UKG, UKG_CO, only, response, run, run_one
from normalization import pipeline

DEDUCTIONS = UKG_CO + "/employees/{aid}/deductions"
CODES = UKG_CO + "/lookup/deduction-codes"
BENEFITS = UKG_CO + "/employees/{aid}/benefits"


def unrouted(document):
    return {r["endpoint"]: r["body"]
            for r in document["provider_fields"].get("ukg-ready", {}).get("unrouted_responses", [])}


class DeductionMappingChecks(unittest.TestCase):
    def test_only_assignments_are_mapped_and_supplements_keep_source_scope(self):
        assignments = {'deductions': [{'id': 1, 'deduction': {'code': '001', 'name': 'Example'},
                       'effective_from': '2026-01-02', '_links': {'self': '/synthetic/deduction'},
                       'future': False}]}
        code_lookup = {'items': [{'id': 2, 'code': '001', 'name': 'Catalog', 'future': False}]}
        benefits = {'benefits': [{'id': 3, 'employee': {'account_id': 99},
                    'benefit_plan': {'id': 4}, 'name': 'Enrollment'}]}
        before = copy.deepcopy((assignments, code_lookup, benefits))
        result = run("ukg-ready", response(DEDUCTIONS, assignments, **UKG, aid="007"),
                     response(CODES, code_lookup, **UKG), response(BENEFITS, benefits, **UKG, aid="007"))
        record = only(result, "deductions")
        self.assertEqual(record['id'], 'ukg-ready:deduction:001:007:1')
        self.assertEqual(record['employee_ref'], 'ukg-ready:employee:001:007')
        self.assertEqual(record['deduction_id'], '1')
        self.assertEqual(record['employee_id'], '007')
        self.assertEqual(record['provider_fields']['ukg-ready']['deduction']['code'], '001')
        self.assertEqual(record['provider_fields']['ukg-ready']['unmapped']['_links']['self'], '/synthetic/deduction')
        self.assertIs(record['source_extras']['ukg-ready']['future'], False)
        kept = unrouted(result)
        self.assertEqual(kept[CODES]['items'][0]['id'], 2)
        self.assertIs(kept[CODES]['items'][0]['future'], False)
        self.assertEqual(kept[BENEFITS]['benefits'][0]['employee']['account_id'], 99)
        self.assertEqual((assignments, code_lookup, benefits), before)
        json.dumps(result, allow_nan=False)

    def test_supplements_only_are_not_discarded_or_created_as_deductions(self):
        code_lookup = {'items': [{'id': None, 'code': '001'}]}
        benefits = {'benefits': [{'id': 3}]}
        with patch.object(pipeline, 'MappingEngine') as factory:
            result = run("ukg-ready", response(CODES, code_lookup, **UKG),
                         response(BENEFITS, benefits, **UKG, aid="007"))
        self.assertEqual(result['deductions'], [])
        self.assertEqual(unrouted(result), {CODES: code_lookup, BENEFITS: benefits})
        factory.assert_not_called()

    def test_assignment_wrapper_unknowns_are_preserved(self):
        result = run_one("ukg-ready", DEDUCTIONS, {'deductions': [{'id': 1}], 'future': False}, **UKG, aid="007")
        self.assertEqual([x['deduction_id'] for x in result['deductions']], ['1'])
        self.assertEqual(result['source_metadata']['ukg-ready']['responses'][0]['wrapper'], {'future': False})

    def test_empty_or_null_assignments_map_nothing(self):
        for body in [{}, {'deductions': None}, {'deductions': []}]:
            with self.subTest(body=body):
                result = run_one("ukg-ready", DEDUCTIONS, body, **UKG, aid="007")
                self.assertEqual(result['deductions'], [])

    def test_missing_owner_param_stops_the_run(self):
        with self.assertRaisesRegex(ValueError, "cannot build deduction id"):
            run_one("ukg-ready", DEDUCTIONS, {'deductions': [{'id': 1}]}, **UKG)
