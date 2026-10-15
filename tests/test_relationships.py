"""Record ids, refs and merge-by-id (docs/solution-docs/relationship_policies.md)."""
import json
import unittest
from pathlib import Path

from bundle_helpers import (ISOL, ISOL_EMPLOYEE, ISOL_LEGALS, PRISM, UKG, UKG_CO, codes, only,
                            response, run, run_one)
from normalization.pipeline import normalize_bundle

FIXTURES = Path(__file__).parent / "fixtures"
COLLECTIONS = ("companies", "employees", "direct_deposits", "deductions", "payroll_runs", "paychecks")
REFS = ("company_ref", "employee_ref", "payroll_run_ref")


def load(provider):
    return normalize_bundle(json.loads((FIXTURES / f"{provider}.bundle.json").read_text()))


def ids(document):
    return {record["id"]: record for name in COLLECTIONS for record in document[name]}


class Table1RecordIds(unittest.TestCase):
    """Each fixture produces exactly the ids the policy table prescribes."""

    def test_prismhr(self):
        self.assertEqual(set(ids(load("prismhr"))), {
            "prismhr:company:001",
            "prismhr:employee:001:007",
            "prismhr:direct_deposit:001:007:000000000:000000001",
            "prismhr:deduction:001:007:SYNTHETIC",
            "prismhr:payroll_run:001:001",
            "prismhr:paycheck:001:010",
        })

    def test_isolved(self):
        self.assertEqual(set(ids(load("isolved"))), {
            "isolved:company:4000:1",
            "isolved:employee:4000:1:7",
            "isolved:direct_deposit:4000:1:7:10",
            "isolved:deduction:4000:1:7:10",
            "isolved:payroll_run:4000:1:77:1",
            "isolved:paycheck:4000:1:10",
        })

    def test_ukg(self):
        self.assertEqual(set(ids(load("ukg-ready"))), {
            "ukg-ready:company:001",
            "ukg-ready:company:001:ein:1",
            "ukg-ready:employee:001:7",
            "ukg-ready:direct_deposit:001:7:10",
            "ukg-ready:deduction:001:7:10",
            "ukg-ready:payroll_run:001:1",
            "ukg-ready:paycheck:001:10",
        })


class Table2Refs(unittest.TestCase):
    def test_every_ref_in_every_fixture_resolves(self):
        for provider in ("prismhr", "isolved", "ukg-ready"):
            with self.subTest(provider=provider):
                document = load(provider)
                known = ids(document)
                for record in known.values():
                    for ref in REFS:
                        if record.get(ref):
                            self.assertIn(record[ref], known, f"{record['id']}.{ref}")
                self.assertNotIn("dangling_link", codes(document))

    def test_company_ref_is_on_every_non_company_record(self):
        for provider in ("prismhr", "isolved", "ukg-ready"):
            document = load(provider)
            for name in COLLECTIONS[1:]:
                for record in document[name]:
                    with self.subTest(provider=provider, record=record["id"]):
                        self.assertTrue(record["company_ref"].startswith(f"{provider}:company:"))

    def test_employee_and_run_refs(self):
        prism = ids(load("prismhr"))
        self.assertEqual(prism["prismhr:paycheck:001:010"]["payroll_run_ref"], "prismhr:payroll_run:001:001")
        self.assertEqual(prism["prismhr:direct_deposit:001:007:000000000:000000001"]["employee_ref"],
                         "prismhr:employee:001:007")
        isol = ids(load("isolved"))
        self.assertNotIn("payroll_run_ref", isol["isolved:paycheck:4000:1:10"])  # checks carry no run id
        ukg = ids(load("ukg-ready"))
        self.assertEqual(ukg["ukg-ready:company:001:ein:1"]["company_ref"], "ukg-ready:company:001")
        self.assertEqual(ukg["ukg-ready:paycheck:001:10"]["payroll_run_ref"], "ukg-ready:payroll_run:001:1")


class MergeById(unittest.TestCase):
    def test_ukg_employee_from_profile_pay_info_and_compensation(self):
        employee = ids(load("ukg-ready"))["ukg-ready:employee:001:7"]
        endpoints = [s["endpoint"] for s in employee["source_metadata"]["ukg-ready"]["sources"]]
        self.assertEqual(endpoints, [UKG_CO + "/employees", UKG_CO + "/employees/{aid}/pay-info",
                                     UKG_CO + "/employees/{aid}/compensation/history"])
        self.assertEqual(employee["ukg_standard_work_day_milliseconds"], 28800000)
        self.assertIn("compensation_history", employee["provider_fields"]["ukg-ready"])

    def test_isolved_employee_with_salary_history(self):
        employee = ids(load("isolved"))["isolved:employee:4000:1:7"]
        self.assertIn("salary_history", employee["provider_fields"]["isolved"])

    def test_ukg_paycheck_header_and_detail_become_one(self):
        document = load("ukg-ready")
        self.assertEqual(len(document["paychecks"]), 1)
        self.assertEqual(len(document["paychecks"][0]["source_metadata"]["ukg-ready"]["sources"]), 2)

    def test_conflicting_values_keep_first_and_report(self):
        first = {"errorCode": "0", "employee": [{"id": "7", "firstName": "Ada"}]}
        second = {"errorCode": "0", "employee": [{"id": "7", "firstName": "Grace"}]}
        document = run("prismhr", response("/employee/v1/getEmployee", first, **PRISM),
                       response("/employee/v1/getEmployee", second, **PRISM))
        self.assertEqual(only(document, "employees")["first_name"], "Ada")
        self.assertIn("merge_conflict", codes(document))


class WhenValuesDoNotExist(unittest.TestCase):
    def test_missing_owner_param_stops_the_run(self):
        with self.assertRaisesRegex(ValueError, "cannot build employee id"):
            run_one("prismhr", "/employee/v1/getEmployee", {"errorCode": "0", "employee": [{"id": "7"}]})

    def test_missing_record_key_stops_the_run(self):
        with self.assertRaisesRegex(ValueError, "cannot build deduction id"):
            run_one("prismhr", "/deductions/v1/getDeductions",
                    {"errorCode": "0", "employeeDeductions": {"deduction": [{"amount": 1}]}},
                    **PRISM, employeeId="7")

    def test_missing_ref_value_leaves_ref_empty_with_warning(self):
        document = run_one("prismhr", "/payroll/v1/getPayrollVoucherForBatch",
                           {"errorCode": "0", "payrollVouchers": [{"voucherId": "10", "batchId": "1"}]}, **PRISM)
        paycheck = only(document, "paychecks")
        self.assertNotIn("employee_ref", paycheck)
        self.assertIn("missing_ref", codes(document))

    def test_ref_outside_the_bundle_is_reported_not_dropped(self):
        document = run_one("isolved", ISOL_EMPLOYEE + "/directdeposits", [{"id": 1}], **ISOL, employeeId="9")
        self.assertEqual(len(document["direct_deposits"]), 1)
        self.assertIn("dangling_link", codes(document))

    def test_params_owner_conflicting_with_body_stops_the_run(self):
        body = [{"id": 1, "employeeId": 8, "payItemType": "Deduction", "payItemName": "x"}]
        with self.assertRaisesRegex(ValueError, "conflicts with response"):
            run_one("isolved", ISOL_EMPLOYEE + "/payItems", body, **ISOL, employeeId="9")

    def test_fallback_template_used_when_record_id_is_absent(self):
        detail = {"employee": {"account_id": 7}, "type": {"id": 1}}
        document = run_one("ukg-ready", UKG_CO + "/payrolls/{id}/pay-statements/{id}", detail,
                           **UKG, payroll_id="1", pay_statement_id="55")
        self.assertEqual(only(document, "paychecks")["id"], "ukg-ready:paycheck:001:55")


class PreservedNotDropped(unittest.TestCase):
    def test_filtered_and_unrouted_responses_are_kept(self):
        isolved = load("isolved")
        filtered = isolved["provider_fields"]["isolved"]["filtered_records"]
        self.assertEqual(filtered[0]["record"]["payItemType"], "Earning")
        ukg = load("ukg-ready")
        unrouted = {r["endpoint"] for r in ukg["provider_fields"]["ukg-ready"]["unrouted_responses"]}
        self.assertEqual(unrouted, {UKG_CO + "/lookup/deduction-codes", UKG_CO + "/employees/{aid}/benefits"})

    def test_company_from_isolved_legals_list(self):
        document = run_one("isolved", ISOL_LEGALS, [{"id": 1, "legalName": "A"}, {"id": 2, "legalName": "B"}],
                           clientId="4000")
        self.assertEqual({c["id"] for c in document["companies"]}, {"isolved:company:4000:1", "isolved:company:4000:2"})


if __name__ == "__main__":
    unittest.main()
