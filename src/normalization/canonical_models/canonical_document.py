# One canonical document per bundle: every record type plus run-level issues.
"""Canonical document produced by pipeline.normalize_bundle.

Records are validated individually against their canonical model before they
are placed here (see pipeline.py), so the collections hold JSON-ready dicts.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .canonical_model_company import CanonicalCompany
from .canonical_model_deduction import CanonicalDeduction
from .canonical_model_direct_deposit import CanonicalDirectDeposit
from .canonical_model_employee import CanonicalEmployee
from .canonical_model_payroll import CanonicalPaycheck, CanonicalPayrollRun

# Canonical record type -> output model / document collection.
MODELS = {
    "company": CanonicalCompany,
    "employee": CanonicalEmployee,
    "direct_deposit": CanonicalDirectDeposit,
    "deduction": CanonicalDeduction,
    "payroll_run": CanonicalPayrollRun,
    "paycheck": CanonicalPaycheck,
}
COLLECTIONS = {
    "company": "companies",
    "employee": "employees",
    "direct_deposit": "direct_deposits",
    "deduction": "deductions",
    "payroll_run": "payroll_runs",
    "paycheck": "paychecks",
}


class CanonicalDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: Literal["prismhr", "isolved", "ukg-ready"]
    companies: list[dict[str, Any]] = Field(default_factory=list)
    employees: list[dict[str, Any]] = Field(default_factory=list)
    direct_deposits: list[dict[str, Any]] = Field(default_factory=list)
    deductions: list[dict[str, Any]] = Field(default_factory=list)
    payroll_runs: list[dict[str, Any]] = Field(default_factory=list)
    paychecks: list[dict[str, Any]] = Field(default_factory=list)
    provider_fields: dict[str, Any] = Field(default_factory=dict)
    source_metadata: dict[str, Any] = Field(default_factory=dict)
    issues: list[dict[str, Any]] = Field(default_factory=list)
