# isolved adapter: converts isolved API responses into the canonical model.
# Source validation covers all entities; employee, deposit, deduction and company mapping are implemented.
"""isolved adapter: candidate must discover and implement all source mappings."""
from importlib.resources import as_file, files
from copy import deepcopy
from ._payroll_mapping import map_payroll
from typing import Any, Dict, Optional

from ..canonical_models.canonical_model_employee import CanonicalEmployee, EmployeeMappingIssue
from ..canonical_models.canonical_model_direct_deposit import (
    CanonicalDirectDeposit, CanonicalDirectDepositResult,
)
from ..canonical_models.canonical_model_company import CanonicalCompany, CanonicalCompanyResult
from ..canonical_models.canonical_model_deduction import CanonicalDeduction, CanonicalDeductionResult
from ..mapping_engine import MappingEngine, load_mapping_config, _plain, _extras, _MISSING
from ..helpers.mapping import identifier
from ..source_models.isolved.isolved_source_model_employee import (
    IsolvedEmployeeInput,
)

from ..source_models.isolved.isolved_source_model_direct_deposit import (
    IsolvedEmployeeDirectDepositResponse,
    IsolvedEmployeeDirectDepositModel,
)

from ..source_models.isolved.isolved_source_model_deduction import (
    IsolvedEmployeePayItemResponse,
    IsolvedEmployeePayItemModel,
)

from ..source_models.isolved.isolved_source_model_payroll_run import (
    IsolvedPayrollInput,
)

from ..source_models.isolved.isolved_source_model_company import (
    IsolvedLegalModel,
)


def normalize(
    entity: str, response: Any, reference: Dict[str, Any], *, employee_id: Optional[str] = None
) -> Any:
    """Return the candidate-designed JSON-serializable canonical result.

    Do not infer units, endpoint shapes, or enum meanings from this stub.
    Preserve documented source semantics and define diagnostics in your design.
    """
    if entity == "employee":
        return normalize_employees(response, reference)
    if entity == "direct_deposit":
        return normalize_direct_deposits(response, reference, employee_id=employee_id)
    if entity == "deduction":
        return normalize_deductions(response, reference, employee_id=employee_id)
    if entity == "payroll":
        return normalize_payroll(response, reference)
    if entity == "company":
        return normalize_company(response, reference)
    raise NotImplementedError("Implement isolved company/employee/payroll mappings from approved evidence.")


def normalize_employees(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate employee input, apply the YAML rules, and return JSON-ready records."""
    # The existing input model validates detail, paging and salary-history shapes.
    records = IsolvedEmployeeInput.validate_response(response)
    if not records:
        return []

    metadata = None
    salary_only = isinstance(response, list)
    if salary_only:
        # Group already-validated salary records without pretending their IDs
        # identify employees. This project container is not new provider input.
        records = [IsolvedEmployeeInput.model_construct(id=None, salary_history=records)]
        metadata = {"input_kind": "standalone_salary_history"}
    elif isinstance(response, dict) and any(
        name in response for name in
        ("results", "nextPageUrl", "previousPageUrl", "totalItems", "totalPages")
    ):
        # The wrapper was validated above; preserve paging/extras, not employees.
        metadata = {"response": {key: value for key, value in response.items() if key != "results"}}

    # Reuse one engine across this input; map() does not repeat source validation.
    resource = files("normalization").joinpath("mappings/isolved/employee.yaml")
    with as_file(resource) as mapping_path:
        configuration = load_mapping_config(mapping_path)
    engine = MappingEngine(configuration, IsolvedEmployeeInput, CanonicalEmployee)

    output = []
    for employee in records:
        canonical = engine.map(employee, metadata=metadata)
        if salary_only:
            # The null employee ID is an unknown-owner marker, not a source value.
            canonical.source_metadata.original_values.pop("id", None)
            canonical.source_metadata.mapping_issues = [
                *canonical.source_metadata.mapping_issues,
                EmployeeMappingIssue(
                    source_path="salary_history",
                    reason="Standalone salary history has no employee identity; employee_id remains null",
                ),
            ]
        output.append(canonical.model_dump(mode="json", exclude_unset=True))
    return output


def normalize_direct_deposits(
    response: Any, reference: Dict[str, Any], *, employee_id: Optional[str] = None
) -> Any:
    """Validate native deposit input, map accounts, and preserve source information."""
    if not isinstance(employee_id, str) or not employee_id.strip():
        raise ValueError("isolved direct-deposit normalization requires a nonblank employee_id")

    # Nested account types/IDs are validated once by the source response model.
    validated = IsolvedEmployeeDirectDepositResponse.model_validate(response)
    accounts = validated.root
    mapped_accounts = []
    if accounts:
        resource = files("normalization").joinpath("mappings/isolved/direct_deposit.yaml")
        with as_file(resource) as mapping_path:
            configuration = load_mapping_config(mapping_path)
        engine = MappingEngine(configuration, IsolvedEmployeeDirectDepositModel, CanonicalDirectDeposit)
        for index, account in enumerate(accounts):
            mapped_accounts.append(engine.map(
                account, context={"employee_id": employee_id},
                metadata={"source_location": {"account_index": index}},
            ))

    # The input is a native array: do not invent response wrapper fields.
    metadata = {}
    # No employee owner exists in this source schema; supplied context is retained,
    # not inferred from a deposit ID, bank account, link or collection position.
    result = CanonicalDirectDepositResult(
        provider="isolved", employee_id=employee_id, direct_deposits=mapped_accounts,
        source_metadata=metadata,
    )
    return result.model_dump(mode="json", exclude_unset=True)


def normalize_deductions(
    response: Any, reference: Dict[str, Any], *, employee_id: Optional[str] = None
) -> Any:
    """Select verified deduction pay items and preserve other supplied records."""
    if not isinstance(employee_id, str) or not employee_id.strip():
        raise ValueError("isolved deduction normalization requires a nonblank employee_id")
    records = IsolvedEmployeePayItemResponse.model_validate(response).root
    selected = [(index, record) for index, record in enumerate(records)
                if record.payItemType == "Deduction"]
    other = [(index, record) for index, record in enumerate(records)
             if record.payItemType != "Deduction"]
    # Only selected assignments inherit CLI ownership; preserved unexpected
    # records retain their supplied employee references without reassignment.
    for index, record in selected:
        if record.employeeId is not None and identifier(record.employeeId).value != employee_id:
            raise ValueError("isolved deduction employee_id context conflicts with a response employee ID")
    mapped = []
    if selected:
        resource = files("normalization").joinpath("mappings/isolved/deduction.yaml")
        with as_file(resource) as mapping_path:
            configuration = load_mapping_config(mapping_path)
        engine = MappingEngine(configuration, IsolvedEmployeePayItemModel, CanonicalDeduction)
        for index, record in selected:
            canonical = engine.map(record, context={"employee_id": employee_id},
                                   metadata={"source_location": {"record_index": index}})
            # Source owner was checked above. Supply the validated CLI owner
            # when the optional source owner is missing/null; retain raw provenance.
            canonical.employee_id = employee_id
            mapped.append(canonical)
    provider_fields = {}
    metadata = {}
    if other:
        provider_fields = {"isolved": {"non_deduction_items": [_plain(record) for _, record in other]}}
        metadata = {"isolved": {"non_deduction_source_indexes": [index for index, _ in other]}}
    extras = _extras(records)
    source_extras = {} if extras is _MISSING else {"isolved": {"records": extras}}
    result = CanonicalDeductionResult(
        provider="isolved", employee_id=employee_id, deductions=mapped,
        provider_fields=provider_fields, source_metadata=metadata, source_extras=source_extras,
    )
    return result.model_dump(mode="json", exclude_unset=True)


def normalize_payroll(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate every supplied payroll family, then map without inferred joins."""
    validated = IsolvedPayrollInput.validate_response(response)
    metadata = deepcopy(response) if isinstance(response, dict) else {}
    for name in ("payroll_runs", "paychecks", "results"):
        if metadata.get(name):
            metadata.pop(name)
    return map_payroll("isolved", [
        ("payroll_run", "payroll_runs", validated.payroll_runs or []),
        ("paycheck", "paychecks", validated.paychecks or []),
        ("paycheck", "results", validated.results or []),
    ], metadata)


def normalize_company(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate company-related source records, map them, and preserve their scope."""
    # Native input is one legal-company object, not a fabricated envelope.
    records = [IsolvedLegalModel.model_validate(response)]
    metadata = {}
    mapped = []
    if records:
        resource = files("normalization").joinpath("mappings/isolved/company.yaml")
        with as_file(resource) as mapping_path:
            configuration = load_mapping_config(mapping_path)
        engine = MappingEngine(configuration, IsolvedLegalModel, CanonicalCompany)
        for index, record in enumerate(records):
            # Internal source role follows this adapter's documented record class;
            # it is not user input, a join or a generated company identifier.
            mapped.append(engine.map(
                record, context={"source_record_type": "legal_company"},
                metadata={"source_location": {"record_index": index}},
            ))

    result = CanonicalCompanyResult(
        provider="isolved", companies=mapped, source_metadata=metadata,
    )
    return result.model_dump(mode="json", exclude_unset=True)
