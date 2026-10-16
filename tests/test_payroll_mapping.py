"""Shared payroll mapping: runs and paychecks through the bundle pipeline, preservation, alias conflicts."""
import copy
import json

import pytest

from bundle_helpers import ISOL, ISOL_LEGALS, PRISM, UKG, UKG_CO, codes, only, response, run, run_one
from normalization import contracts
from normalization.adapters import ADAPTERS
from normalization.canonical_models.canonical_document import CanonicalDocument
from normalization.helpers.mapping import identifier_alias, validate_helper
from normalization.pipeline import _MapperCache

BATCHES = "/payroll/v1/getBatchListByDate"
VOUCHERS = "/payroll/v1/getPayrollVoucherForBatch"
ISOL_RUNS = ISOL_LEGALS + "/{legalId}/paygroupId/{paygroupId}/payrollRunHistory/byDate"
ISOL_CHECKS = ISOL_LEGALS + "/{legalId}/payGroups/{payGroupId}/checks"
UKG_RUNS = UKG_CO + "/payrolls"
UKG_LIST = UKG_CO + "/payrolls/{id}/pay-statements"
UKG_DETAIL = UKG_CO + "/payrolls/{id}/pay-statements/{id}"


@pytest.mark.parametrize("left,right,expected,conflict", [
    (None, "0001", "0001", False), ("0001", None, "0001", False),
    ("0001", "0001", "0001", False), (None, None, None, False),
    ("0001", "1", None, True), ("", "", "", False), (7, 7.0, "7", False),
])
def test_identifier_alias(left, right, expected, conflict):
    converted = identifier_alias(left, right)
    assert converted.value == expected
    assert bool(converted.issue) == conflict
    validate_helper("identifier_alias", 2, {})


def test_prism_runs_vouchers_and_alias_conflict_preserve_every_value():
    wrapper = {"errorCode": "0", "errorMessage": "", "infoMessage": ["Informational"],
               "extension": {"any": {"flag": False}}}
    batches = {**wrapper, "batchList": [{"batchId": "001", "payGroup": [{"payGroupId": "01",
                                                                         "payPeriodStartDate": "2026-10-01"}]}]}
    vouchers = {**wrapper, "payrollVouchers": [{"voucherId": "002", "checkNumber": "0001", "checkNum": "1",
        "netPay": 0.0, "checkAmt": -2.0, "earning": [{"hoursUnits": 2.0, "hoursWorked": 0.0, "future": False}],
        "deduction": [{"deductAmount": 3.0}], "future": {"flag": False}}]}
    before = copy.deepcopy((batches, vouchers))
    result = run("prismhr", response(BATCHES, batches, **PRISM), response(VOUCHERS, vouchers, **PRISM))
    run_record, check = only(result, "payroll_runs"), only(result, "paychecks")
    assert run_record["payroll_run_id"] == "001"
    assert run_record["provider_fields"]["prismhr"]["pay_group"][0]["pay_period_start_date"] == "2026-10-01"
    assert check["check_number"] is None
    assert check["source_metadata"]["original_values"]["checkNumber"] == "0001"
    assert check["source_metadata"]["original_values"]["checkNum"] == "1"
    assert check["source_metadata"]["mapping_issues"]
    assert check["net_pay"] == 0.0 and check["check_amount"] == -2.0
    assert "employee_id" not in check and "payroll_run_id" not in check
    # No employeeId / batchId in the voucher: refs stay empty and are reported.
    assert "employee_ref" not in check and "payroll_run_ref" not in check
    assert codes(result).count("missing_ref") == 2
    assert check["source_extras"]["prismhr"]["earning"][0]["future"] is False
    assert check["provider_fields"]["prismhr"]["deduction"][0]["deduct_amount"] == 3.0
    responses = result["source_metadata"]["prismhr"]["responses"]
    assert responses[1]["wrapper"]["infoMessage"] == ["Informational"]
    assert (batches, vouchers) == before
    json.dumps(result, allow_nan=False)


def test_isolved_check_fields_and_same_check_from_two_responses_merges():
    record = {"id": 10, "employeeId": 7, "payrollRunNumber": 2, "netPay": 0.0,
              "benefits": [{"checkEmployerContribution": 5.0}], "links": [{"href": "/synthetic/check"}]}
    body = {"results": [record], "totalItems": 1}
    before = copy.deepcopy(body)
    result = run("isolved", response(ISOL_RUNS, [{"id": 1, "runNumber": 2}], **ISOL, paygroupId="77"),
                 response(ISOL_CHECKS, body, **ISOL, payGroupId="77"))
    check = only(result, "paychecks")
    assert check["paycheck_id"] == "10" and check["id"] == "isolved:paycheck:4000:1:10"
    assert check["employee_id"] == "7" and "payroll_run_id" not in check
    assert check["employee_ref"] == "isolved:employee:4000:1:7"
    assert "payroll_run_ref" not in check  # a check carries no run id
    assert check["provider_fields"]["isolved"]["payroll_run_number"] == 2
    assert check["provider_fields"]["isolved"]["benefits"][0]["check_employer_contribution"] == 5.0
    assert check["provider_fields"]["isolved"]["unmapped"]["links"][0]["href"] == "/synthetic/check"
    assert check["source_metadata"]["isolved"]["sources"][0]["path"] == "results/0"
    assert result["source_metadata"]["isolved"]["responses"][1]["wrapper"]["totalItems"] == 1
    assert body == before
    # The same check captured twice (e.g. two overlapping date ranges) is one record with both sources.
    twice = run("isolved", response(ISOL_CHECKS, body, **ISOL, payGroupId="77"),
                response(ISOL_CHECKS, body, **ISOL, payGroupId="77"))
    merged = only(twice, "paychecks")
    assert [s["response"] for s in merged["source_metadata"]["isolved"]["sources"]] == [0, 1]


def test_ukg_header_and_detail_merge_and_uncertain_amounts_stay_provider_scoped():
    runs = {"payrolls": [{"id": 1}], "future_wrapper": False}
    header = {"pay_statements": [{"id": 2, "employee": {"account_id": 7.0}}]}
    detail = {"id": 2, "employee": {"account_id": 7.0},
              "earnings": [{"id": 3, "hours": 0, "ee_amount": 12.0, "future": False}],
              "deductions": [{"id": 4, "er_amount": 2.0}], "taxes": [{"id": 5, "ee_amount": 1.0}]}
    before = copy.deepcopy((runs, header, detail))
    result = run("ukg-ready", response(UKG_RUNS, runs, **UKG),
                 response(UKG_LIST, header, **UKG, payroll_id="1"),
                 response(UKG_DETAIL, detail, **UKG, payroll_id="1", pay_statement_id="2"))
    check = only(result, "paychecks")  # header and detail are one paycheck now
    assert len(check["source_metadata"]["ukg-ready"]["sources"]) == 2
    assert check["paycheck_id"] == "2"
    assert "employee_id" not in check and "payroll_run_id" not in check
    assert check["employee_ref"] == "ukg-ready:employee:001:7"
    assert check["payroll_run_ref"] == "ukg-ready:payroll_run:001:1"
    provider = check["provider_fields"]["ukg-ready"]
    assert provider["employee"]["account_id"] == "7"
    assert provider["earnings"][0]["ee_amount"] == 12.0
    assert provider["earnings"][0]["hours"] == 0
    assert check["source_extras"]["ukg-ready"]["earnings"][0]["future"] is False
    assert result["source_metadata"]["ukg-ready"]["responses"][0]["wrapper"]["future_wrapper"] is False
    assert "merge_conflict" not in codes(result)
    assert (runs, header, detail) == before


@pytest.mark.parametrize("provider,endpoint,params,body", [
    ("prismhr", VOUCHERS, PRISM, {"errorCode": "0", "errorMessage": "", "extension": {"any": {"flag": False}}}),
    ("isolved", ISOL_CHECKS, {**ISOL, "payGroupId": "77"}, {"totalItems": 0, "future": False}),
    ("ukg-ready", UKG_RUNS, UKG, {"payrolls": [], "future": False}),
])
def test_empty_results_keep_wrapper(provider, endpoint, params, body):
    result = run_one(provider, endpoint, body, **params)
    assert not result["payroll_runs"] and not result["paychecks"]
    assert result["source_metadata"][provider]["responses"][0]["wrapper"]
    CanonicalDocument.model_validate(result)
    json.dumps(result, allow_nan=False)


PAYROLL_ROUTES = [(provider, endpoint, route)
                  for provider, adapter in ADAPTERS.items()
                  for endpoint, routes in adapter.ROUTES.items()
                  for route in routes if route["type"] in ("payroll_run", "paycheck")]


@pytest.mark.parametrize("provider,endpoint,route", PAYROLL_ROUTES,
                         ids=[f"{p}:{r['yaml']}:{e.rsplit('/', 1)[-1]}" for p, e, r in PAYROLL_ROUTES])
def test_all_payroll_yaml_paths_preflight_and_cover_every_declared_field(provider, endpoint, route):
    engine = _MapperCache(provider).get_mapper(route, endpoint)  # preflight against the contract schema
    paths = {path.split(".")[0] for rule in engine.config.fields
             for path in (rule.source if isinstance(rule.source, list) else [rule.source])}
    declared = contracts.response_schema(provider, endpoint).at(route["records"]).declared()
    assert declared - {"links", "_links"} == paths - {"links", "_links"}


def test_invalid_date_and_alias_single_value_keep_originals():
    result = run_one("prismhr", VOUCHERS, {"errorCode": "0", "errorMessage": "",
        "payrollVoucher": [{"voucherId": "001", "checkNum": "0007", "payDate": "invalid"}]}, **PRISM)
    record = only(result, "paychecks")
    assert record["check_number"] == "0007"
    assert record["pay_date"] is None
    assert record["source_metadata"]["original_values"]["payDate"] == "invalid"
    assert record["source_metadata"]["mapping_issues"]
    # The live singular key is renamed to the contract name before mapping.
    assert record["source_metadata"]["prismhr"]["sources"][0]["path"] == "payrollVouchers/0"


def test_strict_payroll_output_rejects_unconverted_values():
    from normalization.canonical_models.canonical_model_payroll import CanonicalPaycheck
    from pydantic import ValidationError
    for supplied in ({"paycheck_id": 1}, {"paycheck_id": "1", "net_pay": "25"},
                     {"paycheck_id": "1", "net_pay": float("inf")},
                     {"paycheck_id": "1", "pay_date": "2026-10-15"}):
        with pytest.raises(ValidationError):
            CanonicalPaycheck(provider="prismhr", **supplied)
