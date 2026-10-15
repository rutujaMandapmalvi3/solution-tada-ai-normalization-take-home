# Canonical employee model. Input: mapped employee data. Output: validated employee records.
"""Shared employee output for PrismHR, isolved and UKG Ready.

contracts.py validates provider input. These models define mapper output only:
no source-code translation, date parsing, joins or unit conversion occurs here.
Provider-specific structures retain their nesting in provider_fields; unknown
source fields belong in source_extras, never undeclared employee attributes.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


Provider = Literal["prismhr", "isolved", "ukg-ready"]
Gender = Literal["male", "female", "non-binary", "declined", "unknown", ""]
MaritalStatus = Literal[
    "single", "married", "divorced", "widowed", "civil union", "other", ""
]
RehireEligibility = Literal["eligible", "ineligible", "no preference"]
EmploymentStatusClass = Literal["active", "on leave", "terminated", ""]
PayRateBasis = Literal[
    "hourly", "weekly", "bi-weekly", "semi-monthly", "monthly", "yearly", ""
]


class EmployeeMappingIssue(BaseModel):
    """A source value the mapper could not convert or resolve safely."""

    model_config = ConfigDict(extra="forbid", strict=True)

    source_path: str
    reason: str


class EmployeeSourceMetadata(BaseModel):
    """Conversion provenance plus provider wrappers, messages, paging and links.

    Provider-keyed metadata is intentionally open; its contents retain their
    source shape instead of pretending to share a provider-independent schema.
    """

    model_config = ConfigDict(extra="allow", strict=True)

    original_values: Dict[str, Any] = Field(default_factory=dict)
    mapping_issues: List[EmployeeMappingIssue] = Field(default_factory=list)


# Covers profile/contact, employment status/dates, job/organization and compensation.
class CanonicalEmployee(BaseModel):
    """One employee in the common output format.

    employee_id must be supplied, but may be null under the existing source-ID
    policy. Identifiers must already be strings and dates Python date objects;
    conversion is the mapper's job. Optional business values are not invented.
    """

    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)

    provider: Provider
    # Canonical identity and links (docs/solution-docs/relationship_policies.md).
    id: Optional[str] = None
    company_ref: Optional[str] = None
    employee_id: Optional[str]
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    preferred_name: Optional[str] = None
    prismhr_ethnic_code: Optional[str] = None
    birth_date: Optional[date] = None
    prismhr_employer_ids: Optional[list[str]] = None
    marital_status: Optional[MaritalStatus] = None
    prismhr_smoker_code: Optional[str] = None
    peo_start_date: Optional[date] = None
    is_deceased: Optional[bool] = None
    gender: Optional[Gender] = None
    nickname: Optional[str] = None
    deceased_date: Optional[date] = None
    is_hispanic: Optional[bool] = None
    prismhr_portal_user_id: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state_code: Optional[str] = None
    postal_code: Optional[str] = None
    home_phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    primary_email: Optional[str] = None
    employment_status: Optional[str] = None
    prismhr_employment_status_class: Optional[EmploymentStatusClass] = None
    employment_type: Optional[str] = None
    prismhr_employment_type_class: Optional[str] = None
    job_start_date: Optional[date] = None
    original_hire_date: Optional[date] = None
    latest_hire_date: Optional[date] = None
    seniority_date: Optional[date] = None
    prismhr_last_job_change_date: Optional[date] = None
    employee_number: Optional[str] = None
    eligible_for_rehire: Optional[RehireEligibility] = None
    work_phone: Optional[str] = None
    prismhr_gender_designation: Optional[str] = None
    preferred_pronouns: Optional[str] = None
    work_location_code: Optional[str] = None
    work_email: Optional[str] = None
    prismhr_default_timesheet_hours: Optional[float] = None
    standard_hours_per_pay_period: Optional[float] = None
    hourly_rate: Optional[float] = None
    per_pay_salary: Optional[float] = None
    other_pay_rate: Optional[float] = None
    other_pay_rate_basis: Optional[PayRateBasis] = None
    prismhr_annual_pay: Optional[float] = None
    next_review_date: Optional[date] = None
    annual_salary: Optional[float] = None
    isolved_eeo_gender_override: Optional[str] = None
    isolved_ethnic_origin_description: Optional[str] = None
    hire_date: Optional[date] = None
    job_effective_date: Optional[date] = None
    isolved_legal_code: Optional[str] = None
    name_prefix: Optional[str] = None
    name_suffix: Optional[str] = None
    personal_email: Optional[str] = None
    rehire_date: Optional[date] = None
    termination_date: Optional[date] = None
    isolved_tobacco_use: Optional[bool] = None
    isolved_derived_employee_unique_id: Optional[str] = None
    isolved_updated_hire_date: Optional[date] = None
    isolved_updated_job_effective_date: Optional[date] = None
    isolved_work_location_display: Optional[str] = None
    ukg_username: Optional[str] = None
    ukg_external_id: Optional[str] = None
    ukg_employee_id: Optional[str] = None
    ukg_country: Optional[str] = None
    ukg_state_value: Optional[str] = None
    ukg_primary_account_id: Optional[str] = None
    ukg_ein_id: Optional[str] = None
    ukg_standard_work_day_milliseconds: Optional[int] = None
    ukg_employee_type_id: Optional[str] = None
    ukg_ein_name: Optional[str] = None

    # Request context is separate from employer/legal/EIN references.
    prismhr_client_id: Optional[str] = None

    # Known provider fields and unknown extras keep their original nested shape.
    provider_fields: Dict[str, Any] = Field(default_factory=dict)
    source_metadata: EmployeeSourceMetadata = Field(default_factory=EmployeeSourceMetadata)
    source_extras: Dict[str, Any] = Field(default_factory=dict)
