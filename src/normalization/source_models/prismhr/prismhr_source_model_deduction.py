"""PrismHR deduction response source models.

Types and required fields follow API 2025.09. Explicit live differences
are noted inline. Optional fields accept missing/null values, while
required fields remain required (observed nulls are accepted explicitly).
Dates and numeric strings retain source types. Business rules and mapping
are deliberately outside this module.

Project validation policy: record IDs and documented required wrapper fields
require presence. Other fields accept missing/null; existing ID nullability
is retained. Reference IDs are optional unless they identify this record.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class PrismHRExtension(BaseModel):
    """Source schema: Extension."""
    model_config = ConfigDict(extra="allow")

    any: Optional[Dict[str, Any]] = None


class PrismHREmployeeDeductionsDeduction(BaseModel):
    """Source schema: EmployeeDeductions-Deduction."""
    model_config = ConfigDict(extra="allow")

    deductionCode: Optional[str] = None
    deductionType: Optional[str] = None
    deductionMethod: Optional[str] = None
    description: Optional[str] = None
    usePercent: Optional[bool] = None
    amount: Optional[float] = None
    period: Optional[str] = None
    loanOrGarnishId: Optional[str] = None
    benefitPlanId: Optional[str] = None
    lastDedPerAdj: Optional[float] = None
    limit: Optional[float] = None
    maximum: Optional[float] = None
    basis: Optional[str] = None
    trackArrears: Optional[bool] = None
    startDate: Optional[str] = None
    stopDate: Optional[str] = None
    glOverrideAcct: Optional[str] = None
    mandatory: Optional[bool] = None
    matchMethod: Optional[str] = None
    matchAmount: Optional[float] = None
    matchDescription: Optional[str] = None
    cutbackPayeeCode: Optional[str] = None
    rateTableId: Optional[str] = None
    rateTier: Optional[str] = None
    detailsChecksum: Optional[str] = None
    achOption: Optional[str] = None


class PrismHREmployeeDeductions(BaseModel):
    """Source schema: EmployeeDeductions."""
    model_config = ConfigDict(extra="allow")

    deduction: Optional[List[PrismHREmployeeDeductionsDeduction]] = None


class PrismHRDeductionResponse(BaseModel):
    """Source schema: DeductionResponse."""
    model_config = ConfigDict(extra="allow")

    errorCode: str
    errorMessage: str
    extension: Optional[PrismHRExtension] = None
    employeeDeductions: Optional[PrismHREmployeeDeductions] = None
