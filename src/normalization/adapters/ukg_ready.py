# UKG Ready adapter: employee/deposit/deduction/company mapping; payroll has source validation.
"""UKG Ready source validation and provider dispatch."""
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
from ..mapping_engine import MappingEngine, load_mapping_config, _plain, _extras, _remaining, _MISSING
from ..source_models.ukg_ready.ukg_ready_source_model_employee import UKGReadyEmployeeInput
from ..source_models.ukg_ready.ukg_ready_source_model_direct_deposit import (
    UKGReadyDirectDepositResponse, UKGReadyDirectDepositResponseDepositsItem,
)
from ..source_models.ukg_ready.ukg_ready_source_model_deduction import (
    UKGReadyDeductionInput, UKGReadyDeductionResponseDeductionsItem,
)
from ..source_models.ukg_ready.ukg_ready_source_model_payroll_run import UKGReadyPayrollInput
from ..source_models.ukg_ready.ukg_ready_source_model_company import (
    UKGReadyEinsResponse, UKGReadyEinsResponseItemsItem,
)


def normalize(
    entity: str, response: Any, reference: Dict[str, Any], *, employee_id: Optional[str] = None
) -> Any:
    """Validate source data without inferring units, enums, or relationships."""
    if entity == 'employee':
        return normalize_employees(response, reference)
    if entity == 'direct_deposit':
        return normalize_direct_deposits(response, reference, employee_id=employee_id)
    if entity == 'deduction':
        return normalize_deductions(response, reference, employee_id=employee_id)
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
    metadata = None
    if isinstance(response, dict) and "employees" in response:
        metadata = {"response": {key: value for key, value in response.items() if key != "employees"}}
    resource = files("normalization").joinpath("mappings/ukg_ready/employee.yaml")
    with as_file(resource) as mapping_path:
        configuration = load_mapping_config(mapping_path)
    engine = MappingEngine(configuration, UKGReadyEmployeeInput, CanonicalEmployee)
    return [engine.map(employee, metadata=metadata).model_dump(mode="json", exclude_unset=True)
            for employee in employees]


def normalize_direct_deposits(
    response: Any, reference: Dict[str, Any], *, employee_id: Optional[str] = None
) -> Any:
    """Validate native deposit input, map accounts, and preserve source information."""
    if not isinstance(employee_id, str) or not employee_id.strip():
        raise ValueError("ukg-ready direct-deposit normalization requires a nonblank employee_id")

    # Nested account types/IDs are validated once by the source response model.
    validated = UKGReadyDirectDepositResponse.model_validate(response)
    accounts = validated.deposits
    mapped_accounts = []
    if accounts:
        resource = files("normalization").joinpath("mappings/ukg_ready/direct_deposit.yaml")
        with as_file(resource) as mapping_path:
            configuration = load_mapping_config(mapping_path)
        engine = MappingEngine(configuration, UKGReadyDirectDepositResponseDepositsItem, CanonicalDirectDeposit)
        for index, account in enumerate(accounts):
            mapped_accounts.append(engine.map(
                account, context={"employee_id": employee_id},
                metadata={"source_location": {"account_index": index}},
            ))

    # Preserve supplied wrapper links/settings/counts/extras, even for zero accounts.
    metadata = {"ukg-ready": {"response": validated.model_dump(
        mode="python", by_alias=True, exclude={"deposits"}, exclude_unset=True,
    )}}
    # No employee owner exists in this source schema; supplied context is retained,
    # not inferred from a deposit ID, bank account, link or collection position.
    result = CanonicalDirectDepositResult(
        provider="ukg-ready", employee_id=employee_id, direct_deposits=mapped_accounts,
        source_metadata=metadata,
    )
    return result.model_dump(mode="json", exclude_unset=True)


def normalize_deductions(
    response: Any, reference: Dict[str, Any], *, employee_id: Optional[str] = None
) -> Any:
    """Map assignment records, retaining catalogs/benefits in their source sections."""
    if not isinstance(employee_id, str) or not employee_id.strip():
        raise ValueError("UKG Ready deduction normalization requires a nonblank employee_id")
    envelope = UKGReadyDeductionInput.validate_response(response)
    assignments = envelope.assignments
    records = assignments.deductions if assignments is not None else []
    mapped = []
    if records:
        resource = files("normalization").joinpath("mappings/ukg_ready/deduction.yaml")
        with as_file(resource) as mapping_path:
            configuration = load_mapping_config(mapping_path)
        engine = MappingEngine(configuration, UKGReadyDeductionResponseDeductionsItem, CanonicalDeduction)
        mapped = [engine.map(record, context={"employee_id": employee_id},
                             metadata={"source_location": {"deduction_index": index}})
                  for index, record in enumerate(records)]

    # Preserve known supplements without inventing assignment records, joins or
    # withheld amounts. Their IDs/values stay source data, not canonical IDs.
    preserved = {}
    for name in ("code_lookup", "benefits"):
        if name in envelope.model_fields_set:
            preserved[name] = _plain(getattr(envelope, name))
    # Native compatibility wraps sections during source validation; all unknown
    # values (including retained native fields) remain in original nested extras.
    extras = _extras(envelope)
    source_extras = {} if extras is _MISSING else {"ukg-ready": extras}
    metadata = {}
    if assignments is not None:
        wrapper = assignments.model_dump(mode="python", by_alias=True,
                                         exclude={"deductions"}, exclude_unset=True)
        if wrapper:
            metadata = {"ukg-ready": {"assignments_response": wrapper}}
    if "assignments" in envelope.model_fields_set:
        remaining = _remaining(assignments, {("deductions",)} if records else set())
        if remaining is not _MISSING:
            preserved["unmapped"] = {"assignments": remaining}
    result = CanonicalDeductionResult(
        provider="ukg-ready", employee_id=employee_id, deductions=mapped,
        provider_fields={"ukg-ready": preserved} if preserved else {},
        source_metadata=metadata, source_extras=source_extras,
    )
    return result.model_dump(mode="json", exclude_unset=True)


def normalize_payroll(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate runs, summaries and detailed checks; preserve every supplied family."""
    validated = UKGReadyPayrollInput.validate_response(response)
    metadata = deepcopy(response)
    # Preserve wrapper fields, including empty/null section states, without copying records.
    for name, collection in (("payroll_runs", "payrolls"), ("paycheck_list", "pay_statements")):
        if isinstance(metadata.get(name), dict):
            metadata[name] = {key: value for key, value in metadata[name].items()
                              if key != collection}
    for name in ("payrolls", "pay_statements", "paychecks"):
        if metadata.get(name):
            metadata.pop(name)
    if "id" in response:
        metadata = {}  # Native detail fields are preserved by the record mapping itself.
    return map_payroll("ukg-ready", [
        ("payroll_run", "payroll_runs" if "payroll_runs" in response else "payrolls",
         validated.payroll_runs.payrolls if validated.payroll_runs is not None else []),
        ("paycheck_header", "paycheck_list" if "paycheck_list" in response else "pay_statements",
         validated.paycheck_list.pay_statements if validated.paycheck_list is not None else []),
        ("paycheck", "native_detail" if "id" in response else "paychecks", validated.paychecks or []),
    ], metadata)


def normalize_company(response: Any, reference: Dict[str, Any]) -> Any:
    """Validate company-related source records, map them, and preserve their scope."""
    # EIN lookup items remain EIN records, not inferred API company IDs.
    validated = UKGReadyEinsResponse.model_validate(response)
    records = validated.items
    metadata = {"ukg-ready": {"response": validated.model_dump(
        mode="python", by_alias=True, exclude={"items"}, exclude_unset=True,
    )}}
    mapped = []
    if records:
        resource = files("normalization").joinpath("mappings/ukg_ready/company.yaml")
        with as_file(resource) as mapping_path:
            configuration = load_mapping_config(mapping_path)
        engine = MappingEngine(configuration, UKGReadyEinsResponseItemsItem, CanonicalCompany)
        for index, record in enumerate(records):
            # Internal source role follows this adapter's documented record class;
            # it is not user input, a join or a generated company identifier.
            mapped.append(engine.map(
                record, context={"source_record_type": "ein"},
                metadata={"source_location": {"record_index": index}},
            ))

    result = CanonicalCompanyResult(
        provider="ukg-ready", companies=mapped, source_metadata=metadata,
    )
    return result.model_dump(mode="json", exclude_unset=True)
