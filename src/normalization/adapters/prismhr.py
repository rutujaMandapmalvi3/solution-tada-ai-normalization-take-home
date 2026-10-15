# PrismHR adapter: converts PrismHR API responses into the canonical model.
# All five entities use source validation and canonical mapping.
"""PrismHR adapter: candidate must discover and implement all source mappings."""
from importlib.resources import as_file, files
from copy import deepcopy
from ._payroll_mapping import map_payroll
from typing import Any, Dict, Optional

from ..canonical_models.canonical_model_employee import CanonicalEmployee
from ..canonical_models.canonical_model_direct_deposit import (
    CanonicalDirectDeposit, CanonicalDirectDepositResult,
)
from ..canonical_models.canonical_model_company import CanonicalCompany, CanonicalCompanyResult
from ..canonical_models.canonical_model_deduction import CanonicalDeduction, CanonicalDeductionResult
from ..mapping_engine import MappingEngine, load_mapping_config, _extras, _remaining, _MISSING
from ..source_models.prismhr.prismhr_source_model_employee import (
    PrismHREmployee,
    PrismHREmployeeResponse,
)

from ..source_models.prismhr.prismhr_source_model_direct_deposit import (
    PrismHRDirectDepositResponse,
    PrismHRAchVoucher,
)

from ..source_models.prismhr.prismhr_source_model_deduction import (
    PrismHRDeductionResponse,
    PrismHREmployeeDeductionsDeduction,
)

from ..source_models.prismhr.prismhr_source_model_payroll_run import (
    PrismHRBatchByDateResponse,
)

from ..source_models.prismhr.prismhr_source_model_paycheck import (
    PrismHRPayrollResponseWithPagination,
)

from ..source_models.prismhr.prismhr_source_model_company import (
    PrismHRGetClientMasterResponse,
    PrismHRClientMaster,
)

def normalize(
    entity: str, response: Any, reference: Dict[str, Any], *, client_id: Optional[str] = None,
    employee_id: Optional[str] = None
) -> Any:
    """Return the candidate-designed JSON-serializable canonical result.

    Do not infer units, endpoint shapes, or enum meanings from this stub.
    Preserve documented source semantics and define diagnostics in your design.
    """
    if entity == "employee":
        return normalize_employees(response, reference, client_id=client_id)
    if entity == "direct_deposit":
        return normalize_direct_deposits(response, reference, employee_id=employee_id)
    if entity == "deduction":
        return normalize_deductions(response, reference, employee_id=employee_id)
    if entity == "payroll":
        return normalize_payroll(response, reference)
    if entity == "company":
        return normalize_company(response, reference)
    raise NotImplementedError("Implement PrismHR company/employee/payroll mappings from approved evidence.")

#normalization for /employee:
def normalize_employees(
    response: Any, reference: Dict[str, Any], *, client_id: Optional[str] = None
) -> Any:
    """Validate employees, apply the PrismHR YAML, and return JSON-ready records."""
    if not isinstance(client_id, str) or not client_id.strip():
        raise ValueError("PrismHR employee normalization requires a nonblank client_id")

    # Validate the wrapper and reject the provider's explicit failure code.
    envelope = PrismHREmployeeResponse.model_validate(response)
    if envelope.errorCode != "0":
        raise ValueError(
            f"PrismHR employee request failed "
            f"(errorCode={envelope.errorCode}): {envelope.errorMessage}"
        )

    # The wrapper holds raw records; validate each employee once before mapping.
    employees = [PrismHREmployee.model_validate(record) for record in envelope.employee or []]
    if not employees:
        return []

    # Load the packaged YAML and create one engine for all employees in this input.
    resource = files("normalization").joinpath("mappings/prismhr/employee.yaml")
    with as_file(resource) as mapping_path:
        configuration = load_mapping_config(mapping_path)
    engine = MappingEngine(configuration, PrismHREmployee, CanonicalEmployee)

    # Keep supplied wrapper metadata, including extras, without copying employees.
    metadata = {"response": envelope.model_dump(
        mode="python", by_alias=True, exclude={"employee"}, exclude_unset=True
    )}

    # Map validated objects, then return dictionaries; the CLI writes JSON text.
    return [
        engine.map(employee, context={"client_id": client_id}, metadata=metadata)
        .model_dump(mode="json", exclude_unset=True)
        for employee in employees
    ]

#normalization for direct deposits:
def normalize_direct_deposits(
    response: Any, reference: Dict[str, Any], *, employee_id: Optional[str] = None
) -> Any:
    """Validate deposit setup, map accounts, and preserve response/setup data."""
    if not isinstance(employee_id, str) or not employee_id.strip():
        raise ValueError("PrismHR direct-deposit normalization requires a nonblank employee_id")

    # Validate the wrapper, all employees and nested accounts once.
    envelope = PrismHRDirectDepositResponse.model_validate(response)
    if envelope.errorCode != "0":
        raise ValueError(
            f"PrismHR direct-deposit request failed "
            f"(errorCode={envelope.errorCode}): {envelope.errorMessage}"
        )

    # One CLI owner applies to this file; never silently replace a source ID.
    employees = envelope.employee or []
    for employee in employees:
        if employee.id != employee_id:
            raise ValueError("PrismHR direct-deposit employee_id context conflicts with a response employee ID")

    accounts = [
        (employee_index, account_index, account)
        for employee_index, employee in enumerate(employees)
        if employee.directDeposit is not None
        for account_index, account in enumerate(employee.directDeposit.achVoucher or [])
    ]
    mapped_accounts = []
    if accounts:
        # Reuse one engine for already-validated accounts from this input.
        resource = files("normalization").joinpath("mappings/prismhr/direct_deposit.yaml")
        with as_file(resource) as mapping_path:
            configuration = load_mapping_config(mapping_path)
        engine = MappingEngine(configuration, PrismHRAchVoucher, CanonicalDirectDeposit)
        for employee_index, account_index, account in accounts:
            mapped_accounts.append(engine.map(
                account, context={"employee_id": employee_id, "deposit_id": None},
                metadata={"source_location": {
                    "employee_index": employee_index, "ach_voucher_index": account_index,
                }},
            ))

    # Keep supplied wrapper fields/messages, including extras, without employees.
    metadata = {"prismhr": {"response": envelope.model_dump(
        mode="python", by_alias=True, exclude={"employee"}, exclude_unset=True,
    )}}
    provider_fields = {}
    source_extras = {}
    if "employee" in envelope.model_fields_set:
        # Reuse engine preservation utilities for known fields and unknown extras.
        # Remove only populated account lists already mapped above; null/empty
        # account collections and every other supplied employee/setup field remain.
        consumed = {
            (index, "directDeposit", "achVoucher")
            for index, employee in enumerate(employees)
            if employee.directDeposit is not None and employee.directDeposit.achVoucher
        }
        remaining = _remaining(envelope.employee, consumed)
        if remaining is not _MISSING:
            provider_fields = {"prismhr": {"unmapped": {"employee": remaining}}}
        extras = _extras(envelope.employee)
        if extras is not _MISSING:
            source_extras = {"prismhr": {"employee": extras}}

    # Empty record lists still retain supplied wrappers, settings and extras.
    result = CanonicalDirectDepositResult(
        provider="prismhr", employee_id=employee_id, direct_deposits=mapped_accounts,
        provider_fields=provider_fields, source_metadata=metadata, source_extras=source_extras,
    )
    return result.model_dump(mode="json", exclude_unset=True)


def normalize_deductions(
    response: Any, reference: Dict[str, Any], *, employee_id: Optional[str] = None
) -> Any:
    """Map typed deduction assignments; retain wrapper and optional source data."""
    if not isinstance(employee_id, str) or not employee_id.strip():
        raise ValueError("PrismHR deduction normalization requires a nonblank employee_id")
    envelope = PrismHRDeductionResponse.model_validate(response)
    if envelope.errorCode != "0":
        raise ValueError(
            f"PrismHR deduction request failed "
            f"(errorCode={envelope.errorCode}): {envelope.errorMessage}"
        )
    # This documented section already identifies assignments; no type-code guess.
    section = envelope.employeeDeductions
    records = (section.deduction or []) if section is not None else []
    mapped = []
    if records:
        resource = files("normalization").joinpath("mappings/prismhr/deduction.yaml")
        with as_file(resource) as mapping_path:
            configuration = load_mapping_config(mapping_path)
        engine = MappingEngine(configuration, PrismHREmployeeDeductionsDeduction, CanonicalDeduction)
        mapped = [engine.map(record, context={"employee_id": employee_id, "deduction_id": None},
                             metadata={"source_location": {"deduction_index": index}})
                  for index, record in enumerate(records)]

    metadata = {"prismhr": {"response": envelope.model_dump(
        mode="python", by_alias=True, exclude={"employeeDeductions"}, exclude_unset=True,
    )}}
    provider_fields = {}
    source_extras = {}
    if "employeeDeductions" in envelope.model_fields_set:
        remaining = _remaining(section, {("deduction",)} if records else set())
        if remaining is not _MISSING:
            provider_fields = {"prismhr": {"unmapped": {"employeeDeductions": remaining}}}
        extras = _extras(section)
        if extras is not _MISSING:
            source_extras = {"prismhr": {"employeeDeductions": extras}}
    result = CanonicalDeductionResult(
        provider="prismhr", employee_id=employee_id, deductions=mapped,
        provider_fields=provider_fields, source_metadata=metadata, source_extras=source_extras,
    )
    return result.model_dump(mode="json", exclude_unset=True)


def normalize_payroll(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate and map payroll batches and paycheck vouchers."""
    has_batches = isinstance(response, dict) and "batchList" in response
    has_paychecks = isinstance(response, dict) and any(
        field in response
        for field in ("payrollVouchers", "payrollVoucher", "total", "startpage", "count")
    )

    batches = []
    vouchers = []

    # Batch responses (or wrapper-only input) use the batch source model.
    if has_batches or not has_paychecks:
        envelope = PrismHRBatchByDateResponse.model_validate(response)
        if envelope.errorCode != "0":
            raise ValueError(
                f"PrismHR payroll request failed "
                f"(errorCode={envelope.errorCode}): {envelope.errorMessage}"
            )
        batches = envelope.batchList or []

    # Paycheck responses use their own source model, including pagination.
    # When both sections are supplied, both validation paths run.
    if has_paychecks:
        paycheck_envelope = PrismHRPayrollResponseWithPagination.model_validate(response)
        if paycheck_envelope.errorCode != "0":
            raise ValueError(
                f"PrismHR payroll request failed "
                f"(errorCode={paycheck_envelope.errorCode}): {paycheck_envelope.errorMessage}"
            )
        vouchers = paycheck_envelope.payrollVouchers or []

    # Wrapper information stays outside mapped records; retain supplied aliases in provenance.
    metadata = deepcopy(response)
    voucher_section = "payrollVouchers" if "payrollVouchers" in response else "payrollVoucher"
    for name in ("batchList", voucher_section):
        if metadata.get(name):
            metadata.pop(name)
    return map_payroll("prismhr", [
        ("payroll_run", "batchList", batches),
        ("paycheck", voucher_section, vouchers),
    ], metadata)


def normalize_company(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate company-related source records, map them, and preserve their scope."""
    # Validate wrapper and all supplied client-master sections once.
    validated = PrismHRGetClientMasterResponse.model_validate(response)
    if validated.errorCode != "0":
        raise ValueError(
            f"PrismHR company request failed "
            f"(errorCode={validated.errorCode}): {validated.errorMessage}"
        )
    records = [] if validated.clientMaster is None else [validated.clientMaster]
    metadata = {"prismhr": {"response": validated.model_dump(
        mode="python", by_alias=True, exclude={"clientMaster"}, exclude_unset=True,
    )}}
    mapped = []
    if records:
        resource = files("normalization").joinpath("mappings/prismhr/company.yaml")
        with as_file(resource) as mapping_path:
            configuration = load_mapping_config(mapping_path)
        engine = MappingEngine(configuration, PrismHRClientMaster, CanonicalCompany)
        for index, record in enumerate(records):
            # Internal source role follows this adapter's documented record class;
            # it is not user input, a join or a generated company identifier.
            mapped.append(engine.map(
                record, context={"source_record_type": "client"},
                metadata={"source_location": {"record_index": index}},
            ))

    result = CanonicalCompanyResult(
        provider="prismhr", companies=mapped, source_metadata=metadata,
    )
    return result.model_dump(mode="json", exclude_unset=True)
