"""PrismHR payroll run response source models.

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


class PrismHRBatchByDateResponseBatchListPayGroup(BaseModel):
    """Source schema: BatchByDateResponse-BatchList-PayGroup."""
    model_config = ConfigDict(extra="allow")

    payGroupId: Optional[str]
    payPeriodStartDate: Optional[str] = None
    payPeriodEndDate: Optional[str] = None
    weeksWorked: Optional[str] = None
    deductPeriod: Optional[str] = None


class PrismHRBatchList(BaseModel):
    """Source schema: BatchList."""
    model_config = ConfigDict(extra="allow")

    batchId: Optional[str]
    payDate: Optional[str] = None
    batchType: Optional[str] = None
    batchStatus: Optional[str] = None
    payGroup: Optional[List[PrismHRBatchByDateResponseBatchListPayGroup]] = None


class PrismHRBatchByDateResponse(BaseModel):
    """Source schema: BatchByDateResponse."""
    model_config = ConfigDict(extra="allow")

    errorCode: str
    errorMessage: str
    extension: Optional[PrismHRExtension] = None
    batchList: Optional[List[PrismHRBatchList]] = None
