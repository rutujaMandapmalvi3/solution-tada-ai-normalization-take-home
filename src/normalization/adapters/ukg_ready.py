# UKG Ready adapter: validates source inputs; canonical mapping is pending.
"""UKG Ready source validation and provider dispatch."""
from typing import Any, Dict
from ..source_models.ukg_ready.ukg_ready_source_model_employee import UKGReadyEmployeeInput
from ..source_models.ukg_ready.ukg_ready_source_model_direct_deposit import UKGReadyDirectDepositResponse
from ..source_models.ukg_ready.ukg_ready_source_model_deduction import UKGReadyDeductionInput
from ..source_models.ukg_ready.ukg_ready_source_model_payroll_run import UKGReadyPayrollInput
from ..source_models.ukg_ready.ukg_ready_source_model_company import UKGReadyEinsResponse


def normalize(entity: str, response: Any, reference: Dict[str, Any]) -> Any:
    """Validate source data without inferring units, enums, or relationships."""
    if entity == 'employee':
        return normalize_employees(response, reference)
    if entity == 'direct_deposit':
        return normalize_direct_deposits(response, reference)
    if entity == 'deduction':
        return normalize_deductions(response, reference)
    if entity == 'payroll':
        return normalize_payroll(response, reference)
    if entity == 'company':
        return normalize_company(response, reference)
    raise NotImplementedError("Implement UKG Ready mappings from approved evidence.")


def normalize_employees(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate employee records and supplemental pay/compensation data."""
    employees = UKGReadyEmployeeInput.validate_response(response)
    if not employees:
        return []
    raise NotImplementedError(
        "UKG Ready employee source validation passed; canonical mapping is not implemented. "
        f"{len(employees)} employee record(s) supplied."
    )


def normalize_direct_deposits(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate the documented deposit wrapper and every account."""
    envelope = UKGReadyDirectDepositResponse.model_validate(response)
    if not envelope.deposits:
        return []
    raise NotImplementedError(
        "UKG Ready direct-deposit source validation passed; canonical mapping is not implemented. "
        f"{len(envelope.deposits)} deposit record(s) supplied."
    )


def normalize_deductions(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate assignments, code lookups, and benefits in their own sections."""
    envelope = UKGReadyDeductionInput.validate_response(response)
    assignments = envelope.assignments.deductions if envelope.assignments is not None else []
    codes = envelope.code_lookup.items if envelope.code_lookup is not None else []
    benefits = envelope.benefits.benefits if envelope.benefits is not None else []
    if not assignments and not codes and not benefits:
        return []
    raise NotImplementedError(
        "UKG Ready deduction source validation passed; canonical mapping is not implemented. "
        f"{len(assignments)} assignment(s), {len(codes)} code(s), and {len(benefits)} benefit(s) supplied."
    )


def normalize_payroll(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate runs, paycheck headers, and paycheck details together."""
    envelope = UKGReadyPayrollInput.validate_response(response)
    runs = envelope.payroll_runs.payrolls if envelope.payroll_runs is not None else []
    headers = envelope.paycheck_list.pay_statements if envelope.paycheck_list is not None else []
    details = envelope.paychecks or []
    if not runs and not headers and not details:
        return []
    # Preserve source associations; no joins, deduplication, or page fetches.
    raise NotImplementedError(
        "UKG Ready payroll source validation passed; canonical mapping is not implemented. "
        f"{len(runs)} run(s), {len(headers)} paycheck header(s), and {len(details)} detail(s) supplied."
    )


def normalize_company(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate documented EIN lookup records; do not invent company details."""
    envelope = UKGReadyEinsResponse.model_validate(response)
    if not envelope.items:
        return []
    raise NotImplementedError(
        "UKG Ready company source validation passed; canonical mapping is not implemented. "
        f"{len(envelope.items)} EIN record(s) supplied."
    )
