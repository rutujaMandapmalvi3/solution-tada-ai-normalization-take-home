"""isolved direct deposit source models from primary Swagger v6.

Source names, types, and required presence follow the primary snapshot.
Observed deviations are noted inline. Optional fields accept missing/null.
Dates remain source strings; enum translation, unit conversion, and additional
business rules are deferred. Unknown fields are preserved.

Project validation policy: record IDs and documented required wrapper fields
require presence. Other fields accept missing/null; existing ID nullability
is retained. Reference IDs are optional unless they identify this record.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, RootModel


class IsolvedBaseLinkModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.Base.LinkModel."""
    model_config = ConfigDict(extra="allow")

    href: Optional[str] = None
    method: Optional[str] = None
    rel: Optional[str] = None


class IsolvedEmployeeDirectDepositModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeeDirectDepositModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    accountNumber: Optional[str] = None
    accountType: Optional[str] = None
    amount: Optional[float] = None
    bankName: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[str] = None
    percent: Optional[float] = None
    routingNumber: Optional[str] = None
    # Required in Swagger but null in the saved response; presence is optional under project policy.
    sequenceNumber: Optional[int] = None
    status: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedEmployeeDirectDepositResponse(RootModel[List[IsolvedEmployeeDirectDepositModel]]):
    """The endpoint returns a top-level array, not an object envelope."""
