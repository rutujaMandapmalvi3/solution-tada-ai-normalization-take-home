"""UKG Ready direct deposit source models.

Generated from cached GET response schemas, not an official OpenAPI contract.
Source names and types are retained. Optional fields accept missing/null;
required presence follows each schema. Unknown live fields are preserved.
Enum translation, numeric/date constraints, units, and business rules are
deferred. Every nested model records its schema index and field path.

Project validation policy: record IDs and documented required wrapper fields
require presence. Other fields accept missing/null; existing ID nullability
is retained. Reference IDs are optional unless they identify this record.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class UKGReadyDirectDepositResponse(BaseModel):
    """Cached schema path: 137."""
    model_config = ConfigDict(extra="allow")

    deposits: List[UKGReadyDirectDepositResponseDepositsItem]
    links: UKGReadyDirectDepositResponseLinks = Field(default=..., alias="_links")
    total_count: Optional[int] = Field(default=None, alias="_total_count")
    routing_type: Optional[str] = Field(default=None, alias="_routing_type")
    is_eligible_for_paypal: Optional[bool] = None


class UKGReadyDirectDepositResponseDepositsItem(BaseModel):
    """Cached schema path: 137/deposits[]."""
    model_config = ConfigDict(extra="allow")

    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    sequence: Optional[int] = None
    type: Optional[str] = None
    active_from: Optional[str] = None
    active_to: Optional[str] = None
    active: Optional[bool] = None
    amount: Optional[float] = None
    percentage: Optional[float] = None
    calc_method: Optional[UKGReadyDirectDepositResponseDepositsItemCalcMethod] = None
    account_type: Optional[str] = None
    account_number: Optional[str] = None
    routing_number: Optional[str] = None
    routing_type: Optional[str] = None
    pre_note_status: Optional[str] = None
    cancel_pre_note: Optional[bool] = None
    pre_note_sent_date: Optional[str] = None
    pre_note_expiration_date: Optional[str] = None
    arrearage_function: Optional[str] = None
    payroll_frequency: Optional[UKGReadyDirectDepositResponseDepositsItemPayrollFrequency] = None
    last_payroll: Optional[float] = None
    month_to_date: Optional[float] = None
    quarter_to_date: Optional[float] = None
    year_to_date: Optional[float] = None
    used_in_pay_statement: Optional[bool] = None
    currency: Optional[str] = None
    documents_count: Optional[int] = Field(default=None, alias="_documents_count")
    notes_count: Optional[int] = Field(default=None, alias="_notes_count")
    visible: Optional[bool] = None
    is_paypal: Optional[bool] = None
    links: Optional[UKGReadyDirectDepositResponseDepositsItemLinks] = Field(default=None, alias="_links")


class UKGReadyDirectDepositResponseDepositsItemCalcMethod(BaseModel):
    """Cached schema path: 137/deposits[]/calc_method."""
    model_config = ConfigDict(extra="allow")

    display_name: Optional[str] = None
    type: Optional[str] = None


class UKGReadyDirectDepositResponseDepositsItemPayrollFrequency(BaseModel):
    """Cached schema path: 137/deposits[]/payroll_frequency."""
    model_config = ConfigDict(extra="allow")

    type: Optional[str] = None
    holiday_type: Optional[str] = None
    holiday_profile: Optional[UKGReadyDirectDepositResponseDepositsItemPayrollFrequencyHolidayProfile] = None
    month: Optional[int] = None
    payroll_number: Optional[str] = None
    block_last: Optional[bool] = None
    quarter_month: Optional[int] = None


class UKGReadyDirectDepositResponseDepositsItemPayrollFrequencyHolidayProfile(BaseModel):
    """Cached schema path: 137/deposits[]/payroll_frequency/holiday_profile."""
    model_config = ConfigDict(extra="allow")

    id: int
    display_name: Optional[str] = None


class UKGReadyDirectDepositResponseDepositsItemLinks(BaseModel):
    """Cached schema path: 137/deposits[]/_links."""
    model_config = ConfigDict(extra="allow")

    self: Optional[str] = None
    edit: Optional[str] = None
    delete: Optional[str] = None
    masked: Optional[str] = None
    documents: Optional[str] = None
    upload_document: Optional[str] = None
    add_note: Optional[str] = None
    notes: Optional[str] = None


class UKGReadyDirectDepositResponseLinks(BaseModel):
    """Cached schema path: 137/_links."""
    model_config = ConfigDict(extra="allow")

    add: Optional[str] = None
    reserve_live_check: Optional[str] = None
    cancel_pre_note: Optional[str] = None
    upload_document: Optional[str] = None
