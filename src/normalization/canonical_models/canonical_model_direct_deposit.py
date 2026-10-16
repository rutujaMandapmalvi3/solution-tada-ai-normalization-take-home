# Canonical direct-deposit models. Input: mapped deposit data. Output: validated direct-deposit records.
"""Shared direct deposit output for PrismHR, isolved and UKG Ready.

contracts.py validates provider input; these classes validate mapper output only.
No source selection, code translation, ID generation or unit conversion occurs
here. Provider-specific values and unknown extras retain their own nesting.
Deposit setup only; paycheck payments and HSA are separate scopes.
"""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


Provider = Literal["prismhr", "isolved", "ukg-ready"]


class DirectDepositMappingIssue(BaseModel):
    """A source value that could not be converted or resolved safely."""

    model_config = ConfigDict(extra="forbid", strict=True)

    source_path: str
    reason: str


class DirectDepositSourceMetadata(BaseModel):
    """Conversion provenance and provider-keyed wrapper/context information."""

    model_config = ConfigDict(extra="allow", strict=True)

    original_values: Dict[str, Any] = Field(default_factory=dict)
    mapping_issues: List[DirectDepositMappingIssue] = Field(default_factory=list)


# Covers direct-deposit account details and allocation settings.
class CanonicalDirectDeposit(BaseModel):
    """One shared direct deposit record, with already-converted output values.

    deposit_id requires a key but accepts null: Prism supplies no equivalent
    record ID. Other business values remain optional. Mapping performs any
    conversion before constructing this strict output model.
    """

    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)

    provider: Provider
    # Canonical identity and links (docs/solution-docs/relationship_policies.md).
    id: Optional[str] = None
    company_ref: Optional[str] = None
    employee_ref: Optional[str] = None
    deposit_id: Optional[str]
    employee_id: Optional[str] = None
    account_number: Optional[str] = None
    routing_number: Optional[str] = None
    bank_name: Optional[str] = None
    account_type: Optional[str] = None
    allocation_amount: Optional[float] = None
    allocation_percentage: Optional[float] = None
    sequence: Optional[int] = None
    # Known source-specific fields, conversion metadata, and undeclared extras.
    provider_fields: Dict[str, Any] = Field(default_factory=dict)
    source_metadata: DirectDepositSourceMetadata = Field(default_factory=DirectDepositSourceMetadata)
    source_extras: Dict[str, Any] = Field(default_factory=dict)
