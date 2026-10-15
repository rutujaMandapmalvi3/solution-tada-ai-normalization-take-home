"""Shared deduction output for PrismHR, isolved and UKG Ready.

Source models validate input; these classes validate mapper output only.
No source selection, code translation, ID generation or unit conversion occurs
here. Provider-specific values and unknown extras retain their own nesting.
Employee deduction assignments only; payroll transactions stay in payroll.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


Provider = Literal["prismhr", "isolved", "ukg-ready"]


class DeductionMappingIssue(BaseModel):
    """A source value that could not be converted or resolved safely."""

    model_config = ConfigDict(extra="forbid", strict=True)

    source_path: str
    reason: str


class DeductionSourceMetadata(BaseModel):
    """Conversion provenance and provider-keyed wrapper/context information."""

    model_config = ConfigDict(extra="allow", strict=True)

    original_values: Dict[str, Any] = Field(default_factory=dict)
    mapping_issues: List[DeductionMappingIssue] = Field(default_factory=list)


# Covers deduction identity, employee association and effective dates.
class CanonicalDeduction(BaseModel):
    """One shared deduction record, with already-converted output values.

    deduction_id requires a key but accepts null: Prism supplies no equivalent
    record ID. Other business values remain optional. Mapping performs any
    conversion before constructing this strict output model.
    """

    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)

    provider: Provider
    deduction_id: Optional[str]
    employee_id: Optional[str] = None
    employee_number: Optional[str] = None
    deduction_code: Optional[str] = None
    deduction_name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    # Known source-specific fields, conversion metadata, and undeclared extras.
    provider_fields: Dict[str, Any] = Field(default_factory=dict)
    source_metadata: DeductionSourceMetadata = Field(default_factory=DeductionSourceMetadata)
    source_extras: Dict[str, Any] = Field(default_factory=dict)


class CanonicalDeductionResult(BaseModel):
    """Records plus preserved data even when no canonical records are supplied.

    The adapter may assemble this container without inventing a record merely
    to hold supplements, settings, unexpected items or response metadata.
    This schema does not change the current adapter return format by itself.
    """

    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)

    provider: Provider
    employee_id: Optional[str] = None
    deductions: List[CanonicalDeduction] = Field(default_factory=list)
    provider_fields: Dict[str, Any] = Field(default_factory=dict)
    source_metadata: DeductionSourceMetadata = Field(default_factory=DeductionSourceMetadata)
    source_extras: Dict[str, Any] = Field(default_factory=dict)
