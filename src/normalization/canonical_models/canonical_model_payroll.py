"""Shared payroll output; runs, summaries and detailed checks retain distinct roles."""
from datetime import date
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

Provider = Literal["prismhr", "isolved", "ukg-ready"]


class PayrollMappingIssue(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    source_path: str
    reason: str


class PayrollSourceMetadata(BaseModel):
    model_config = ConfigDict(extra="allow", strict=True)
    original_values: dict[str, Any] = Field(default_factory=dict)
    mapping_issues: list[PayrollMappingIssue] = Field(default_factory=list)


class PayrollRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)
    provider: Provider
    # Canonical identity and links (docs/solution-docs/relationship_policies.md).
    id: str | None = None
    company_ref: str | None = None
    provider_fields: dict[str, Any] = Field(default_factory=dict)
    source_metadata: PayrollSourceMetadata = Field(default_factory=PayrollSourceMetadata)
    source_extras: dict[str, Any] = Field(default_factory=dict)


# Covers payroll-run identity, pay date and documented run-level period dates.
class CanonicalPayrollRun(PayrollRecord):
    payroll_run_id: str | None
    payroll_run_pay_date: date | None = None
    payroll_run_period_start_date: date | None = None
    payroll_run_period_end_date: date | None = None


# Covers employee paycheck summaries, associations, dates and verified amounts.
class CanonicalPaycheckHeader(PayrollRecord):
    paycheck_id: str | None
    employee_ref: str | None = None
    payroll_run_ref: str | None = None
    employee_id: str | None = None
    payroll_run_id: str | None = None
    pay_date: date | None = None
    period_start_date: date | None = None
    period_end_date: date | None = None


# Covers detailed earnings/hours, taxes, deductions, benefits and payments in provider scope.
class CanonicalPaycheck(CanonicalPaycheckHeader):
    check_number: str | None = None
    net_pay: float | None = None
    gross_pay: float | None = None
    check_amount: float | None = None


class CanonicalPayrollResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)
    provider: Provider
    payroll_runs: list[CanonicalPayrollRun] = Field(default_factory=list)
    paycheck_headers: list[CanonicalPaycheckHeader] = Field(default_factory=list)
    paychecks: list[CanonicalPaycheck] = Field(default_factory=list)
    provider_fields: dict[str, Any] = Field(default_factory=dict)
    source_metadata: PayrollSourceMetadata = Field(default_factory=PayrollSourceMetadata)
    source_extras: dict[str, Any] = Field(default_factory=dict)
