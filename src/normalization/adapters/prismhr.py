# PrismHR adapter: converts PrismHR API responses into the canonical model.
# Employee envelope validation is implemented; field mapping is still to be added.
"""PrismHR adapter: candidate must discover and implement all source mappings."""
from typing import Any, Dict, Optional
from ..source_models.prismhr.prismhr_source_model_employee import (
    PrismHREmployee,
    PrismHREmployeeResponse,
)

from ..source_models.prismhr.prismhr_source_model_direct_deposit import (
    PrismHRDirectDepositResponse,
)

from ..source_models.prismhr.prismhr_source_model_deduction import (
    PrismHRDeductionResponse,
)

from ..source_models.prismhr.prismhr_source_model_payroll_run import (
    PrismHRBatchByDateResponse,
)

from ..source_models.prismhr.prismhr_source_model_paycheck import (
    PrismHRPayrollResponseWithPagination,
)

from ..source_models.prismhr.prismhr_source_model_company import (
    PrismHRGetClientMasterResponse,
)

def normalize(
    entity: str, response: Any, reference: Dict[str, Any], *, client_id: Optional[str] = None
) -> Any:
    """Return the candidate-designed JSON-serializable canonical result.

    Do not infer units, endpoint shapes, or enum meanings from this stub.
    Preserve documented source semantics and define diagnostics in your design.
    """
    if entity == "employee":
        return normalize_employees(response, reference, client_id=client_id)
    if entity == "direct_deposit":
        return normalize_direct_deposits(response, reference)
    if entity == "deduction":
        return normalize_deductions(response, reference)
    if entity == "payroll":
        return normalize_payroll(response, reference)
    if entity == "company":
        return normalize_company(response, reference)
    raise NotImplementedError("Implement PrismHR company/employee/payroll mappings from approved evidence.")

#normalization for /employee:
def normalize_employees(
    response: Any, reference: Dict[str, Any], *, client_id: Optional[str] = None
) -> Any:
    # Retain the original request client ID for the future employee mapper.
    if not isinstance(client_id, str) or not client_id.strip():
        raise ValueError("PrismHR employee normalization requires a nonblank client_id")
    #Employee wrapper validation: |---
    envelope = PrismHREmployeeResponse.model_validate(response)

    # Check provider success using the documented zero-success assumption.
    if envelope.errorCode != "0":
        raise ValueError(
            f"PrismHR employee request failed "
            f"(errorCode={envelope.errorCode}): {envelope.errorMessage}"
        )

    # Temporary extraction result; employee validation and mapping come next.
    #return envelope.employee
    #---|
    employee_records = envelope.employee or []
    for employee_record in employee_records:
        #pydentic object for next layer - mapping
        validate_employee = PrismHREmployee.model_validate(employee_record)

#normalization for direct deposits:
def normalize_direct_deposits(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate getEmployee deposit setup; canonical mapping is still pending."""
    # Validates errorCode/errorMessage, optional wrapper fields, employees,
    # and every nested direct-deposit account; no second validation loop needed.
    envelope = PrismHRDirectDepositResponse.model_validate(response)

    if envelope.errorCode != "0":
        raise ValueError(
            f"PrismHR direct-deposit request failed "
            f"(errorCode={envelope.errorCode}): {envelope.errorMessage}"
        )

    employees_with_deposits = []
    for employee_record in envelope.employee or []:
        # Missing/null setup is unavailable, not an invalid employee.
        if employee_record.directDeposit is None:
            continue
        # An empty achVoucher list is valid. Its setup metadata is retained.
        employees_with_deposits.append(employee_record)

    # Null infoMessage/updateMessage/extension and empty errorMessage are valid.
    # Nonempty extension/updateMessage have no documented failure meaning.
    # Paycheck payments require a separate paycheck envelope; mapping can reuse
    # a payment helper later without mixing payments with account setup here.
    raise NotImplementedError(
        "PrismHR direct-deposit source validation passed; canonical mapping is not implemented. "
        f"{len(employees_with_deposits)} employee record(s) contain deposit setup."
    )

def normalize_deductions(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate getDeductions setup; canonical mapping is still pending."""
    # Validates required wrapper fields, extension structure, and every deduction.
    envelope = PrismHRDeductionResponse.model_validate(response)

    if envelope.errorCode != "0":
        raise ValueError(
            f"PrismHR deduction request failed "
            f"(errorCode={envelope.errorCode}): {envelope.errorMessage}"
        )

    deductions = (
        envelope.employeeDeductions.deduction
        if envelope.employeeDeductions is not None else None
    )
    # Missing, null, and empty deduction data have nothing to map.
    if not deductions:
        return []

    # An empty list is valid. Nested deduction fields were validated above.
    # This schema does not declare infoMessage or updateMessage.
    # Extension semantics remain deferred; presence alone is not a failure.
    raise NotImplementedError(
        "PrismHR deduction source validation passed; canonical mapping is not implemented. "
        f"{len(deductions)} deduction record(s) supplied."
    )

def normalize_payroll(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate payroll batches and paycheck vouchers; mapping is pending."""
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

    # Missing, null, and empty sections have nothing to map.
    if not batches and not vouchers:
        return []

    # Nested records were validated recursively; extension presence is not an
    # error. Pagination remains available for mapping; no pages are fetched.
    raise NotImplementedError(
        "PrismHR payroll source validation passed; canonical mapping is not implemented. "
        f"{len(batches)} payroll batch record(s) and {len(vouchers)} payroll voucher record(s) supplied."
    )

def normalize_company(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate client-master information; canonical mapping is still pending."""
    # Validates required wrapper fields, extension, and all nested client data.
    envelope = PrismHRGetClientMasterResponse.model_validate(response)

    if envelope.errorCode != "0":
        raise ValueError(
            f"PrismHR company request failed "
            f"(errorCode={envelope.errorCode}): {envelope.errorMessage}"
        )

    if envelope.clientMaster is None:
        return []

    # Extension presence alone is not a failure. Client identifiers retain
    # their source meaning; no canonical company ID is inferred here.
    raise NotImplementedError(
        "PrismHR company source validation passed; canonical mapping is not implemented."
    )
