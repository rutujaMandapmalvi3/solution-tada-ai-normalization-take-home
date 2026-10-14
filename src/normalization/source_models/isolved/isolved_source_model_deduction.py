"""isolved deduction source models from primary Swagger v6.

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


class IsolvedEmployeePayItemCalcParamModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeePayItemCalcParamModel."""
    model_config = ConfigDict(extra="allow")

    paramType: Optional[str] = None
    paramValue: Optional[float] = None


class IsolvedBaseLinkModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.Base.LinkModel."""
    model_config = ConfigDict(extra="allow")

    href: Optional[str] = None
    method: Optional[str] = None
    rel: Optional[str] = None


class IsolvedEmployeePayItemModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeePayItemModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    auditId: Optional[int] = None
    calcParams: Optional[List[IsolvedEmployeePayItemCalcParamModel]] = None
    employeeId: Optional[int] = None
    employeeNumber: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    payItemCode: Optional[str] = None
    payItemId: Optional[int] = None
    payItemName: Optional[str] = None
    payItemType: Optional[str] = None
    referenceNumber: Optional[str] = None
    scheduleOverride: Optional[str] = None
    startDate: Optional[str] = None
    stopDate: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None
    # Live-only field; integer in the saved pay-item response.
    balance: Optional[int] = None


class IsolvedEmployeePayItemResponse(RootModel[List[IsolvedEmployeePayItemModel]]):
    """The endpoint returns a top-level array, not an object envelope."""
