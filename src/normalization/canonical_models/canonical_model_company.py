# Canonical company models. Input: mapped company data. Output: validated company records.
"""Shared company-related output; source organizational levels stay distinct.

Client, legal-company and EIN lookup records are not interchangeable company
identities. Source validation and mapping perform conversions; these models
only validate the already-converted output. No joins or code inference occurs.
"""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


Provider = Literal["prismhr", "isolved", "ukg-ready"]
CompanySourceRecordType = Literal["client", "legal_company", "ein", "company"]


class CompanyMappingIssue(BaseModel):
    """A source value that could not be converted or resolved safely."""

    model_config = ConfigDict(extra="forbid", strict=True)

    source_path: str
    reason: str


class CompanySourceMetadata(BaseModel):
    """Original values, conversion issues and provider-keyed wrapper/context data."""

    model_config = ConfigDict(extra="allow", strict=True)

    original_values: Dict[str, Any] = Field(default_factory=dict)
    mapping_issues: List[CompanyMappingIssue] = Field(default_factory=list)


# Covers organizational identity, legal/DBA names, tax identifiers and industry code.
class CanonicalCompany(BaseModel):
    """One source-scoped company-related record, without an invented global ID.

    The source record ID requires presence and retains existing null acceptance.
    Parent-client references and settings stay in their provider-specific scope.
    UKG EIN names/tax values do not populate unverified legal/federal fields.
    """

    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)

    provider: Provider
    # Canonical identity and links (docs/solution-docs/relationship_policies.md).
    id: Optional[str] = None
    company_ref: Optional[str] = None
    source_record_type: CompanySourceRecordType
    source_record_id: Optional[str]
    legal_name: Optional[str] = None
    trade_name: Optional[str] = None
    federal_tax_id: Optional[str] = None
    naics_code: Optional[str] = None
    ukg_ein_tax_id: Optional[str] = None
    ukg_ein_name: Optional[str] = None

    # Known provider fields, conversion provenance and undeclared source extras.
    provider_fields: Dict[str, Any] = Field(default_factory=dict)
    source_metadata: CompanySourceMetadata = Field(default_factory=CompanySourceMetadata)
    source_extras: Dict[str, Any] = Field(default_factory=dict)


class CanonicalCompanyResult(BaseModel):
    """Company-related records plus preserved wrapper and supplemental data.

    This output schema does not change adapter return formats by itself.
    """

    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)

    provider: Provider
    companies: List[CanonicalCompany] = Field(default_factory=list)
    provider_fields: Dict[str, Any] = Field(default_factory=dict)
    source_metadata: CompanySourceMetadata = Field(default_factory=CompanySourceMetadata)
    source_extras: Dict[str, Any] = Field(default_factory=dict)
