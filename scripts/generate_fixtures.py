"""Generate 15 deterministic, synthetic provider input fixtures.

Explicit builders use the documented structures represented by the project's
source models. This is not an arbitrary OpenAPI example generator: project
requiredness/null policy and named supplemental sections are intentional.
Expected canonical outputs are never generated or overwritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
# Support direct execution from any directory without requiring an editable install.
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from normalization.source_models.prismhr.prismhr_source_model_employee import PrismHREmployeeResponse, PrismHREmployee
from normalization.source_models.prismhr.prismhr_source_model_direct_deposit import PrismHRDirectDepositResponse
from normalization.source_models.prismhr.prismhr_source_model_deduction import PrismHRDeductionResponse
from normalization.source_models.prismhr.prismhr_source_model_company import PrismHRGetClientMasterResponse
from normalization.source_models.prismhr.prismhr_source_model_payroll_run import PrismHRBatchByDateResponse
from normalization.source_models.prismhr.prismhr_source_model_paycheck import PrismHRPayrollResponseWithPagination
from normalization.source_models.isolved.isolved_source_model_employee import IsolvedEmployeeInput
from normalization.source_models.isolved.isolved_source_model_direct_deposit import IsolvedEmployeeDirectDepositResponse
from normalization.source_models.isolved.isolved_source_model_deduction import IsolvedEmployeePayItemResponse
from normalization.source_models.isolved.isolved_source_model_company import IsolvedLegalModel
from normalization.source_models.isolved.isolved_source_model_payroll_run import IsolvedPayrollInput
from normalization.source_models.ukg_ready.ukg_ready_source_model_employee import UKGReadyEmployeeInput
from normalization.source_models.ukg_ready.ukg_ready_source_model_direct_deposit import UKGReadyDirectDepositResponse
from normalization.source_models.ukg_ready.ukg_ready_source_model_deduction import UKGReadyDeductionInput
from normalization.source_models.ukg_ready.ukg_ready_source_model_company import UKGReadyEinsResponse
from normalization.source_models.ukg_ready.ukg_ready_source_model_payroll_run import UKGReadyPayrollInput

DEFAULT_SEED = 42
DEFAULT_OUTPUT = ROOT / "tests" / "fixtures"
CONTRACTS = {
    "prismhr": "contracts/prismhr/openapi/prismhr-2025.09.openapi.json",
    "isolved": "contracts/isolved/openapi/isolved-v6.swagger.json",
    "ukg-ready": "contracts/ukg-ready/reference-schemas.json",
}


# Build documented shapes with invented identities and a small seeded value pool.
def build_cases(seed: int = DEFAULT_SEED) -> dict:
    cases = {'prismhr': {'employee': {'errorCode': '0',
                              'errorMessage': '',
                              'employee': [{'id': '007',
                                            'firstName': 'Alex',
                                            'lastName': 'Example',
                                            'person': {'birthDate': '2000-01-02', 'gender': 'F'},
                                            'compensation': {'hourlyPay': '25.50'},
                                            'fixture_note': False}]},
                 'direct_deposit': {'errorCode': '0',
                                    'errorMessage': '',
                                    'employee': [{'id': '007',
                                                  'directDeposit': {'achVoucher': [{'accountNum': '000000001',
                                                                                    'transitNum': '000000000',
                                                                                    'accountType': 'S',
                                                                                    'method': 'F',
                                                                                    'amount': 25.0}]}}]},
                 'deduction': {'errorCode': '0',
                               'errorMessage': '',
                               'employeeDeductions': {'deduction': [{'deductionCode': 'SYNTHETIC',
                                                                     'description': 'Example '
                                                                                    'deduction',
                                                                     'amount': 0,
                                                                     'startDate': '2026-10-01',
                                                                     'fixture_note': False}]}},
                 'company': {'errorCode': '0',
                             'errorMessage': '',
                             'clientMaster': {'id': '001',
                                              'legalName': 'Example Company',
                                              'clientName': 'Example Trade',
                                              'fixture_note': False}},
                 'payroll': {'errorCode': '0',
                             'errorMessage': '',
                             'batchList': [{'batchId': '001',
                                            'payDate': '2026-10-15',
                                            'payGroup': [{'payGroupId': '01',
                                                          'payPeriodStartDate': '2026-10-01',
                                                          'payPeriodEndDate': '2026-10-14'}]}],
                             'payrollVouchers': [{'voucherId': '010',
                                                  'employeeId': '007',
                                                  'batchId': '001',
                                                  'checkNumber': '0001',
                                                  'checkNum': '0001',
                                                  'netPay': 0.0,
                                                  'checkAmt': 0.0,
                                                  'earning': [{'hoursWorked': 0.0,
                                                               'payAmount': 25.0}],
                                                  'deduction': [{'deductCode': 'SYNTHETIC',
                                                                 'deductAmount': 0.0}],
                                                  'employeeTax': [{'empTaxAmount': 0.0}],
                                                  'benefit': [{'planId': 'SYNTHETIC',
                                                               'empContrib': 0.0}],
                                                  'fixture_note': False}]}},
     'isolved': {'employee': {'results': [{'id': 7,
                                           'nameAddress': {'id': 70,
                                                           'firstName': 'Alex',
                                                           'lastName': 'Example'},
                                           'birthDate': '2000-01-02',
                                           'annualSalary': 50000.0,
                                           'fixture_note': False}],
                              'totalItems': 1,
                              'nextPageUrl': None},
                 'direct_deposit': [{'id': 10,
                                     'accountNumber': '000000001',
                                     'routingNumber': '000000000',
                                     'accountType': 'Checking',
                                     'amount': 25.0,
                                     'percent': None,
                                     'sequenceNumber': 0,
                                     'fixture_note': False}],
                 'deduction': [{'id': 10,
                                'employeeId': 7,
                                'payItemType': 'Deduction',
                                'payItemName': 'Example deduction',
                                'calcParams': [{'paramType': 'Amount', 'paramValue': 0.0}],
                                'fixture_note': False},
                               {'id': 11, 'payItemType': 'Earning'}],
                 'company': {'id': 1,
                             'legalName': 'Example Company',
                             'dbaName': 'Example Trade',
                             'fixture_note': False},
                 'payroll': {'payroll_runs': [{'id': 1, 'runNumber': 2, 'payDate': '2026-10-15'}],
                             'paychecks': [{'id': 10,
                                            'employeeId': 7,
                                            'payrollRunNumber': 2,
                                            'checkNumber': 1,
                                            'netPay': 0.0,
                                            'checkAmount': 0.0,
                                            'earnings': [{'id': 20, 'checkHours': 0.0}],
                                            'deductions': [{'id': 30, 'checkDollars': 0.0}],
                                            'taxes': [{'id': 40, 'checkDollars': 0.0}],
                                            'benefits': [{'checkEmployerContribution': 0.0}],
                                            'fixture_note': False}]}},
     'ukg-ready': {'employee': {'employees': [{'id': 7.0,
                                               'first_name': 'Alex',
                                               'last_name': 'Example',
                                               'dates': {'birthday': '2000-01-02'},
                                               'ein_name': 'Example EIN',
                                               'fixture_note': False}]},
                   'direct_deposit': {'deposits': [{'id': 10,
                                                    'account_number': '000000001',
                                                    'routing_number': '000000000',
                                                    'account_type': 'CHECKING',
                                                    'amount': 25.0,
                                                    'calc_method': {'type': 'FLAT_AMOUNT'},
                                                    'active': False,
                                                    'fixture_note': False}],
                                      '_links': {}},
                   'deduction': {'assignments': {'deductions': [{'id': 10,
                                                                 'deduction': {'code': 'SYNTHETIC',
                                                                               'name': 'Example '
                                                                                       'deduction'},
                                                                 'effective_from': '2026-10-01',
                                                                 'fixture_note': False}]},
                                 'code_lookup': {'items': [{'id': 11, 'code': 'SYNTHETIC'}]},
                                 'benefits': {'benefits': [{'id': 12}]}},
                   'company': {'items': [{'id': 1,
                                          'ein_name': 'Example EIN',
                                          'ein_tax_id': 'SYNTHETIC-TAX-ID',
                                          'fixture_note': False}]},
                   'payroll': {'payroll_runs': {'payrolls': [{'id': 1, 'pay_date': '2026-10-15'}]},
                               'paycheck_list': {'pay_statements': [{'id': 10,
                                                                     'employee': {'account_id': 7.0}}]},
                               'paychecks': [{'id': 10,
                                              'employee': {'account_id': 7.0},
                                              'earnings': [{'id': 20,
                                                            'hours': 0,
                                                            'ee_amount': 0.0}],
                                              'deductions': [{'id': 30,
                                                              'ee_amount': 0.0,
                                                              'er_amount': 0.0}],
                                              'taxes': [{'id': 40, 'ee_amount': 0.0}],
                                              'payments': [{'id': 50, 'ee_amount': 0.0}],
                                              'fixture_note': False}]}}}
    rng = random.Random(seed)
    first_name = rng.choice(["Jamie", "Taylor", "Alex"])
    annual_salary = rng.choice([50000.0, 60000.0, 75000.0])
    allocation_amount = rng.choice([25.0, 50.0, 75.0])
    cases["prismhr"]["employee"]["employee"][0]["firstName"] = first_name
    cases["isolved"]["employee"]["results"][0]["nameAddress"]["firstName"] = first_name
    cases["ukg-ready"]["employee"]["employees"][0]["first_name"] = first_name
    cases["isolved"]["employee"]["results"][0]["annualSalary"] = annual_salary
    cases["prismhr"]["direct_deposit"]["employee"][0]["directDeposit"]["achVoucher"][0]["amount"] = allocation_amount
    cases["isolved"]["direct_deposit"][0]["amount"] = allocation_amount
    cases["ukg-ready"]["direct_deposit"]["deposits"][0]["amount"] = allocation_amount
    return cases


# Validate source structure without calling adapters, mappings or reference readiness.
def validate_case(provider: str, entity: str, payload) -> None:
    if provider == "prismhr" and entity == "employee":
        envelope = PrismHREmployeeResponse.model_validate(payload)
        for record in envelope.employee or []:
            PrismHREmployee.model_validate(record)
        return
    if provider == "prismhr" and entity == "payroll":
        PrismHRBatchByDateResponse.model_validate(payload)
        PrismHRPayrollResponseWithPagination.model_validate(payload)
        return
    validators = {
        ("prismhr", "direct_deposit"): PrismHRDirectDepositResponse.model_validate,
        ("prismhr", "deduction"): PrismHRDeductionResponse.model_validate,
        ("prismhr", "company"): PrismHRGetClientMasterResponse.model_validate,
        ("isolved", "employee"): IsolvedEmployeeInput.validate_response,
        ("isolved", "direct_deposit"): IsolvedEmployeeDirectDepositResponse.model_validate,
        ("isolved", "deduction"): IsolvedEmployeePayItemResponse.model_validate,
        ("isolved", "company"): IsolvedLegalModel.model_validate,
        ("isolved", "payroll"): IsolvedPayrollInput.validate_response,
        ("ukg-ready", "employee"): UKGReadyEmployeeInput.validate_response,
        ("ukg-ready", "direct_deposit"): UKGReadyDirectDepositResponse.model_validate,
        ("ukg-ready", "deduction"): UKGReadyDeductionInput.validate_response,
        ("ukg-ready", "company"): UKGReadyEinsResponse.model_validate,
        ("ukg-ready", "payroll"): UKGReadyPayrollInput.validate_response,
    }
    validators[provider, entity](payload)


# Keep request context separate from provider response fields.
def case_context(provider: str, entity: str) -> dict[str, str]:
    if provider == "prismhr" and entity == "employee":
        return {"client_id": "001"}
    if entity in ("direct_deposit", "deduction"):
        return {"employee_id": "7" if provider == "isolved" else "007"}
    return {}


# Write complete validated inputs and reproducibility metadata, never expected outputs.
def generate(seed: int = DEFAULT_SEED, output_dir: Path = DEFAULT_OUTPUT) -> list[Path]:
    output_dir = Path(output_dir)
    cases = build_cases(seed)
    pending = {}
    manifest = []
    for provider, entities in cases.items():
        for entity, payload in entities.items():
            validate_case(provider, entity, payload)
            relative = Path(provider) / entity / "input.json"
            pending[relative] = json.dumps(payload, indent=2, allow_nan=False) + "\n"
            manifest.append({"provider": provider, "entity": entity,
                             "context": case_context(provider, entity)})
    # All cases and evidence files must validate/read successfully before writing anything.
    evidence = [{"provider": provider, "path": relative,
                 "sha256": hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()}
                for provider, relative in CONTRACTS.items()]
    generation_manifest = {
        "generator_version": 1, "seed": seed, "case_count": len(manifest),
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_model_policy": "Record IDs and documented required wrappers; other fields optional; existing null acceptance.",
        "evidence": evidence,
        "source_models": [{"path": str(path.relative_to(ROOT)),
                           "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                          for path in sorted((ROOT / "src/normalization/source_models").rglob("*.py"))],
        "files": [{"path": str(path), "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
                  for path, text in pending.items()],
    }
    pending[Path("manifest.json")] = json.dumps(manifest, indent=2) + "\n"
    pending[Path("generation_manifest.json")] = json.dumps(generation_manifest, indent=2) + "\n"
    for relative, text in pending.items():
        target = output_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return [output_dir / relative for relative in pending if relative.name == "input.json"]


# Expose repeatable generation through the provided script entry point.
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    try:
        paths = generate(args.seed, args.output_dir)
    except (OSError, ValueError, TypeError) as exc:
        print(f"Fixture generation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Generated {len(paths)} input fixtures in {args.output_dir} (seed {args.seed}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
