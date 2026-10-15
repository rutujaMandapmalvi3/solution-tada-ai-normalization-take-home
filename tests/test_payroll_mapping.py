"""Shared payroll mapping contracts, preservation and alias conflict behavior."""
import copy
import json
from pathlib import Path
import pytest
from normalization.adapters import prismhr, isolved, ukg_ready
from normalization.helpers.mapping import identifier_alias, validate_helper
from normalization.canonical_models.canonical_model_payroll import CanonicalPayrollResult
from normalization.mapping_engine import MappingEngine, load_mapping_config
from normalization.source_models.prismhr import prismhr_source_model_payroll_run as pr, prismhr_source_model_paycheck as pc
from normalization.source_models.isolved import isolved_source_model_payroll_run as iso
from normalization.source_models.ukg_ready import ukg_ready_source_model_payroll_run as ukg


@pytest.mark.parametrize("left,right,expected,conflict", [
    (None,"0001","0001",False), ("0001",None,"0001",False),
    ("0001","0001","0001",False), (None,None,None,False),
    ("0001","1",None,True), ("", "", "",False), (7,7.0,"7",False),
])
def test_identifier_alias(left,right,expected,conflict):
    converted=identifier_alias(left,right)
    assert converted.value==expected
    assert bool(converted.issue)==conflict
    validate_helper("identifier_alias",2,{})


def test_prism_combined_records_and_alias_conflict_preserve_every_value():
    payload={"errorCode":"0","errorMessage":"","infoMessage":["Informational"],
      "extension":{"any":{"flag":False}},
      "batchList":[{"batchId":"001","payGroup":[{"payGroupId":"01", "payPeriodStartDate":"2026-10-01"}]}],
      "payrollVouchers":[{"voucherId":"002","checkNumber":"0001","checkNum":"1",
        "netPay":0.0,"checkAmt":-2.0,"earning":[{"hoursUnits":2.0,"hoursWorked":0.0,"future":False}],
        "deduction":[{"deductAmount":3.0}],"future":{"flag":False}}]}
    before=copy.deepcopy(payload)
    result=prismhr.normalize("payroll",payload,{})
    run=result["payroll_runs"][0]; check=result["paychecks"][0]
    assert run["payroll_run_id"]=="001"
    assert run["provider_fields"]["prismhr"]["pay_group"][0]["pay_period_start_date"]=="2026-10-01"
    assert check["check_number"] is None
    assert check["source_metadata"]["original_values"]["checkNumber"]=="0001"
    assert check["source_metadata"]["original_values"]["checkNum"]=="1"
    assert check["source_metadata"]["mapping_issues"]
    assert check["net_pay"]==0.0 and check["check_amount"]==-2.0
    assert "employee_id" not in check and "payroll_run_id" not in check
    assert check["source_extras"]["prismhr"]["earning"][0]["future"] is False
    assert check["provider_fields"]["prismhr"]["deduction"][0]["deduct_amount"]==3.0
    assert result["source_metadata"]["prismhr"]["response"]["infoMessage"]==["Informational"]
    assert payload==before
    json.dumps(result,allow_nan=False)


def test_isolved_overlapping_sections_preserve_both_records_and_provenance():
    record={"id":10,"employeeId":7,"payrollRunNumber":2,"netPay":0.0,
            "benefits":[{"checkEmployerContribution":5.0}], "links":[{"href":"/synthetic/check"}]}
    payload={"payroll_runs":[{"id":1,"runNumber":2}],"paychecks":[record],"results":[record],"totalItems":1}
    before=copy.deepcopy(payload)
    result=isolved.normalize("payroll",payload,{})
    first,second=result["paychecks"]
    assert first["paycheck_id"]==second["paycheck_id"]=="10"
    assert first["employee_id"]=="7" and "payroll_run_id" not in first
    assert first["provider_fields"]["isolved"]["payroll_run_number"]==2
    assert first["provider_fields"]["isolved"]["benefits"][0]["check_employer_contribution"]==5.0
    assert first["provider_fields"]["isolved"]["unmapped"]["links"][0]["href"]=="/synthetic/check"
    assert first["source_metadata"]["isolved"]["source_location"]["section"]=="paychecks"
    assert second["source_metadata"]["isolved"]["source_location"]["section"]=="results"
    assert result["source_metadata"]["isolved"]["response"]["totalItems"]==1
    assert before==payload


def test_ukg_headers_details_preserve_separate_roles_and_uncertain_amounts():
    payload={"payroll_runs":{"payrolls":[{"id":1}],"future_wrapper":False},
        "paycheck_list":{"pay_statements":[{"id":2,"employee":{"account_id":7.0}}]},
        "paychecks":[{"id":2,"employee":{"account_id":7.0},
           "earnings":[{"id":3,"hours":0,"ee_amount":12.0,"future":False}],
           "deductions":[{"id":4,"er_amount":2.0}],"taxes":[{"id":5,"ee_amount":1.0}]}]}
    before=copy.deepcopy(payload)
    result=ukg_ready.normalize("payroll",payload,{})
    assert len(result["paycheck_headers"])==len(result["paychecks"])==1
    check=result["paychecks"][0]
    assert check["paycheck_id"]=="2"
    assert "employee_id" not in check and "payroll_run_id" not in check
    provider=check["provider_fields"]["ukg-ready"]
    assert provider["employee"]["account_id"]=="7"
    assert provider["earnings"][0]["ee_amount"]==12.0
    assert provider["earnings"][0]["hours"]==0
    assert check["source_extras"]["ukg-ready"]["earnings"][0]["future"] is False
    assert result["source_metadata"]["ukg-ready"]["response"]["payroll_runs"]["future_wrapper"] is False
    assert before==payload


@pytest.mark.parametrize("adapter,payload",[(prismhr,{"errorCode":"0","errorMessage":"","extension":{"any":{"flag":False}}}),
    (isolved,{"totalItems":0,"future":False}),(ukg_ready,{"payrolls":[],"future":False})])
def test_empty_results_keep_container_and_wrapper(adapter,payload):
    result=adapter.normalize("payroll",payload,{})
    assert not any(result[key] for key in ("payroll_runs","paycheck_headers","paychecks"))
    assert result["source_metadata"]
    CanonicalPayrollResult.model_validate(result)
    json.dumps(result,allow_nan=False)


def test_all_payroll_yaml_paths_preflight_and_cover_every_declared_field():
    from normalization.canonical_models.canonical_model_payroll import CanonicalPayrollRun,CanonicalPaycheck,CanonicalPaycheckHeader
    specs=[("prismhr","payroll_run",pr.PrismHRBatchList,CanonicalPayrollRun),
      ("prismhr","paycheck",pc.PrismHRPayrollVoucher,CanonicalPaycheck),
      ("isolved","payroll_run",iso.IsolvedPayrollRunHistoryModel,CanonicalPayrollRun),
      ("isolved","paycheck",iso.IsolvedCheckModel,CanonicalPaycheck),
      ("ukg_ready","payroll_run",ukg.UKGReadyPayrollRunResponsePayrollsItem,CanonicalPayrollRun),
      ("ukg_ready","paycheck_header",ukg.UKGReadyPaycheckListResponsePayStatementsItem,CanonicalPaycheckHeader),
      ("ukg_ready","paycheck",ukg.UKGReadyPaycheckDetails,CanonicalPaycheck)]
    root=Path(__file__).parents[1]/"src/normalization/mappings"
    for directory,role,source,target in specs:
        config=load_mapping_config(root/directory/(role+".yaml"))
        MappingEngine(config,source,target)
        paths={path for rule in config.fields for path in (rule.source if isinstance(rule.source,list) else [rule.source])}
        assert paths=={field.alias or name for name,field in source.model_fields.items() if name not in ("links", "_links")}


def test_invalid_date_and_alias_single_value_keep_originals():
    result=prismhr.normalize("payroll", {"errorCode":"0","errorMessage":"",
        "payrollVoucher":[{"voucherId":"001","checkNum":"0007","payDate":"invalid"}]}, {})
    record=result["paychecks"][0]
    assert record["check_number"]=="0007"
    assert record["pay_date"] is None
    assert record["source_metadata"]["original_values"]["payDate"]=="invalid"
    assert record["source_metadata"]["mapping_issues"]
    assert record["source_metadata"]["prismhr"]["source_location"]["section"]=="payrollVoucher"


def test_strict_payroll_output_rejects_unconverted_values():
    from normalization.canonical_models.canonical_model_payroll import CanonicalPaycheck
    from pydantic import ValidationError
    for supplied in ({"paycheck_id":1}, {"paycheck_id":"1","net_pay":"25"},
                     {"paycheck_id":"1","net_pay":float("inf")},
                     {"paycheck_id":"1","pay_date":"2026-10-15"}):
        with pytest.raises(ValidationError):
            CanonicalPaycheck(provider="prismhr",**supplied)
