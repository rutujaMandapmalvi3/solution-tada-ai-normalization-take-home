# Builds the synthetic fixture bundles. Input: a seed (default 42) and an output folder. Output: <provider>.bundle.json files and generation_manifest.json.
"""Generate three deterministic, synthetic provider bundles.

Each bundle holds every captured response for one provider as
{endpoint, params, body} (see src/normalization/pipeline.py). The explicit
builders below invent identities and values; a seeded value pool varies a few
of them. Every response body is checked against its contract with the same
contract layer the pipeline uses before anything is written. Expected
canonical outputs are never generated or overwritten.
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

from normalization import contracts  # noqa: E402

DEFAULT_SEED = 42
DEFAULT_OUTPUT = ROOT / "tests" / "fixtures"
CONTRACTS = {
    "prismhr": "contracts/prismhr/openapi/prismhr-2025.09.openapi.json",
    "isolved": "contracts/isolved/openapi/isolved-v6.swagger.json",
    "ukg-ready": "contracts/ukg-ready/reference-schemas.json",
}


# Build documented shapes with invented identities and a small seeded value pool.
# Builds the seeded synthetic response bodies for each provider and entity.
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


# Owner ids used in params, shared by every response of a provider so the
# bundle forms one connected company (relationship_policies.md).
PRISM = {"clientId": "001"}
ISOL = {"clientId": "4000", "legalId": "1"}
UKG = {"cid": "001"}
ISOL_LEGAL = "/api/clients/{clientId}/legals"
UKG_CO = "/v2/companies/{cid}"


# Wraps one body with its contract endpoint and request params.
def _response(endpoint: str, params: dict, body) -> dict:
    return {"endpoint": endpoint, "params": params, "body": body}


# Split each provider's cases into the contract responses they came from.
# Splits the synthetic cases into per-provider bundles of {endpoint, params, body} responses.
def build_bundles(seed: int = DEFAULT_SEED) -> dict:
    cases = build_cases(seed)
    p, i, u = cases["prismhr"], cases["isolved"], cases["ukg-ready"]
    prism_employee = p["employee"]["employee"][0]["id"]
    payroll = p["payroll"]
    isol_employee = str(i["employee"]["results"][0]["id"])
    ukg_employee = "7"
    return {
        "prismhr": {"provider": "prismhr", "responses": [
            _response("/clientMaster/v1/getClientMaster", PRISM, p["company"]),
            _response("/employee/v1/getEmployee", PRISM, p["employee"]),
            _response("/employee/v1/getEmployee", {**PRISM, "employeeId": prism_employee,
                                                   "options": "DirectDeposit"}, p["direct_deposit"]),
            _response("/deductions/v1/getDeductions", {**PRISM, "employeeId": prism_employee},
                      p["deduction"]),
            _response("/payroll/v1/getBatchListByDate",
                      {**PRISM, "startDate": "2026-10-01", "endDate": "2026-10-31", "dateType": "PAY"},
                      {k: v for k, v in payroll.items() if k != "payrollVouchers"}),
            _response("/payroll/v1/getPayrollVoucherForBatch", {**PRISM, "batchId": "001"},
                      {k: v for k, v in payroll.items() if k != "batchList"}),
        ]},
        "isolved": {"provider": "isolved", "responses": [
            _response(ISOL_LEGAL, {"clientId": ISOL["clientId"]}, [i["company"]]),
            _response(ISOL_LEGAL + "/{legalId}/employees", ISOL, i["employee"]),
            # Salary history merges into the employee above by canonical id.
            _response(ISOL_LEGAL + "/{legalId}/employees/{employeeId}/salaries",
                      {**ISOL, "employeeId": isol_employee},
                      [{"id": 90, "effectiveDate": "2026-01-01T00:00:00",
                        "payType": {"id": "2", "description": "Salary"},
                        "frequency": {"id": 26, "description": "Biweekly"}}]),
            _response(ISOL_LEGAL + "/{legalId}/employees/{employeeId}/directdeposits",
                      {**ISOL, "employeeId": isol_employee}, i["direct_deposit"]),
            _response(ISOL_LEGAL + "/{legalId}/employees/{employeeId}/payItems",
                      {**ISOL, "employeeId": isol_employee}, i["deduction"]),
            _response(ISOL_LEGAL + "/{legalId}/paygroupId/{paygroupId}/payrollRunHistory/byDate",
                      {**ISOL, "paygroupId": "77", "startDate": "2026-10-01", "endDate": "2026-10-31"},
                      i["payroll"]["payroll_runs"]),
            _response(ISOL_LEGAL + "/{legalId}/payGroups/{payGroupId}/checks",
                      {**ISOL, "payGroupId": "77"}, {"results": i["payroll"]["paychecks"]}),
        ]},
        "ukg-ready": {"provider": "ukg-ready", "responses": [
            _response(UKG_CO + "/lookup/eins", UKG, u["company"]),
            _response(UKG_CO + "/employees", UKG, u["employee"]),
            # pay-info and compensation history merge into the employee by canonical id.
            _response(UKG_CO + "/employees/{aid}/pay-info", {**UKG, "aid": ukg_employee},
                      {"standard_work_day": 28800000, "payroll_classification": "REGULAR"}),
            _response(UKG_CO + "/employees/{aid}/compensation/history", {**UKG, "aid": ukg_employee},
                      {"compensations": [{"id": 91, "employee": {"account_id": 7},
                                          "effective_from": "2026-01-01", "amount": 95000,
                                          "amount_period": "YEAR", "time": 7488000000,
                                          "time_period": "YEAR", "currency": "USD"}]}),
            _response(UKG_CO + "/employees/{aid}/direct-deposits", {**UKG, "aid": ukg_employee},
                      u["direct_deposit"]),
            _response(UKG_CO + "/employees/{aid}/deductions", {**UKG, "aid": ukg_employee},
                      u["deduction"]["assignments"]),
            # Catalog and benefits have no canonical record type: kept as unrouted responses.
            _response(UKG_CO + "/lookup/deduction-codes", UKG, u["deduction"]["code_lookup"]),
            _response(UKG_CO + "/employees/{aid}/benefits", {**UKG, "aid": ukg_employee},
                      u["deduction"]["benefits"]),
            _response(UKG_CO + "/payrolls", UKG, u["payroll"]["payroll_runs"]),
            _response(UKG_CO + "/payrolls/{id}/pay-statements", {**UKG, "payroll_id": "1"},
                      u["payroll"]["paycheck_list"]),
            _response(UKG_CO + "/payrolls/{id}/pay-statements/{id}",
                      {**UKG, "payroll_id": "1", "pay_statement_id": "10"},
                      u["payroll"]["paychecks"][0]),
        ]},
    }


# Check every response against its contract (type errors raise ValueError).
# Checks every response in a bundle against its contract; raises ValueError on type errors.
def validate_bundle(bundle: dict) -> None:
    for response in bundle["responses"]:
        body = contracts.prepare(bundle["provider"], response)
        contracts.validate(bundle["provider"], response["endpoint"], body)


# Write validated bundles and reproducibility metadata, never expected outputs.
# Validates and writes the bundles plus the generation manifest; returns the bundle paths.
def generate(seed: int = DEFAULT_SEED, output_dir: Path = DEFAULT_OUTPUT) -> list[Path]:
    output_dir = Path(output_dir)
    pending = {}
    for provider, bundle in build_bundles(seed).items():
        validate_bundle(bundle)
        pending[Path(f"{provider}.bundle.json")] = json.dumps(bundle, indent=2, allow_nan=False) + "\n"
    # All bundles and evidence files must validate/read successfully before writing anything.
    evidence = [{"provider": provider, "path": relative,
                 "sha256": hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()}
                for provider, relative in CONTRACTS.items()]
    generation_manifest = {
        "generator_version": 2, "seed": seed, "bundle_count": len(pending),
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "validation": "contracts.prepare + contracts.validate (null = not supplied; required not enforced)",
        "evidence": evidence,
        "files": [{"path": str(path), "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
                  for path, text in pending.items()],
    }
    pending[Path("generation_manifest.json")] = json.dumps(generation_manifest, indent=2) + "\n"
    for relative, text in pending.items():
        target = output_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return [output_dir / relative for relative in pending if relative.name.endswith(".bundle.json")]


# Expose repeatable generation through the provided script entry point.
# Command-line entry: reads --seed/--output-dir and runs generate.
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
    print(f"Generated {len(paths)} bundles in {args.output_dir} (seed {args.seed}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
