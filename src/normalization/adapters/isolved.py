# isolved adapter: converts isolved API responses into the canonical model.
# Source validation is implemented for all five entities; canonical mapping is pending.
"""isolved adapter: candidate must discover and implement all source mappings."""
from typing import Any, Dict
from ..source_models.isolved.isolved_source_model_employee import (
    IsolvedEmployeeInput,
)

from ..source_models.isolved.isolved_source_model_direct_deposit import (
    IsolvedEmployeeDirectDepositResponse,
)

from ..source_models.isolved.isolved_source_model_deduction import (
    IsolvedEmployeePayItemResponse,
)

from ..source_models.isolved.isolved_source_model_payroll_run import (
    IsolvedPayrollInput,
)

from ..source_models.isolved.isolved_source_model_company import (
    IsolvedLegalModel,
)


def normalize(entity: str, response: Any, reference: Dict[str, Any]) -> Any:
    """Return the candidate-designed JSON-serializable canonical result.

    Do not infer units, endpoint shapes, or enum meanings from this stub.
    Preserve documented source semantics and define diagnostics in your design.
    """
    if entity == "employee":
        return normalize_employees(response, reference)
    if entity == "direct_deposit":
        return normalize_direct_deposits(response, reference)
    if entity == "deduction":
        return normalize_deductions(response, reference)
    if entity == "payroll":
        return normalize_payroll(response, reference)
    if entity == "company":
        return normalize_company(response, reference)
    raise NotImplementedError("Implement isolved company/employee/payroll mappings from approved evidence.")


def normalize_employees(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate employee detail, paged employees, or salary history."""
    # The main input model validates employees and optional salary history.
    # It also handles existing provider detail/list/salary response formats.
    records = IsolvedEmployeeInput.validate_response(response)

    # No supplied optional collection means nothing to map.
    if not records:
        return []

    # Nested source models validate recursively. Mapping, enum translation,
    # and business rules remain pending; pagination does not trigger API calls.
    raise NotImplementedError(
        "isolved employee source validation passed; canonical mapping is not implemented. "
        f"{len(records)} record(s) supplied."
    )


def normalize_direct_deposits(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate the source account list; canonical mapping is pending."""
    # The endpoint returns a top-level array; each account and its links
    # are validated recursively, including the required-but-nullable record ID.
    validated_response = IsolvedEmployeeDirectDepositResponse.model_validate(response)
    accounts = validated_response.root

    if not accounts:
        return []

    raise NotImplementedError(
        "isolved direct-deposit source validation passed; canonical mapping is not implemented. "
        f"{len(accounts)} account record(s) supplied."
    )


def normalize_deductions(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate pay-item deductions and nested calculation parameters."""
    validated_response = IsolvedEmployeePayItemResponse.model_validate(response)
    deductions = validated_response.root
    if not deductions:
        return []
    raise NotImplementedError(
        "isolved deduction source validation passed; canonical mapping is not implemented. "
        f"{len(deductions)} pay-item record(s) supplied."
    )


def normalize_payroll(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate runs and paychecks through one payroll input model."""
    validated_input = IsolvedPayrollInput.validate_response(response)
    runs = validated_input.payroll_runs or []
    paychecks = validated_input.paychecks or []
    paged_paychecks = validated_input.results or []
    if not runs and not paychecks and not paged_paychecks:
        return []
    # All nested records are already validated. Source associations and
    # pagination remain available for mapping; no joins or API calls occur.
    raise NotImplementedError(
        "isolved payroll source validation passed; canonical mapping is not implemented. "
        f"{len(runs)} run record(s) and "
        f"{len(paychecks) + len(paged_paychecks)} paycheck record(s) supplied."
    )


def normalize_company(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate legal-company information and its nested client data."""
    company = IsolvedLegalModel.model_validate(response)
    # Optional sections may be absent; supplied nested records require their
    # own IDs. Client/company identifiers keep their documented source meaning.
    raise NotImplementedError(
        "isolved company source validation passed; canonical mapping is not implemented."
    )
