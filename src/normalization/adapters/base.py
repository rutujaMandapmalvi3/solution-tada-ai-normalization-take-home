# Target of the adapter pattern: the interface every provider adapter implements.
# The CLI calls only these methods, so it never needs to know which provider it has.
# Each method reads one provider response file and returns a Result, because a
# response can hold many records and some of them can fail while others succeed.
"""ProviderAdapter Target with its RequestContext input and Result output."""
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, computed_field


class RequestContext(BaseModel):
    """IDs used in the provider request; links records whose response omits them."""
    company_id: str  # PrismHR client ID, isolved client ID, or UKG company ID
    legal_id: Optional[str] = None  # isolved legal company ID
    employee_id: Optional[str] = None
    pay_group_id: Optional[str] = None
    payroll_run_id: Optional[str] = None


class ErrorCode(str, Enum):
    INPUT_ERROR = "INPUT_ERROR"  # file missing, unreadable or not JSON
    PROVIDER_ERROR = "PROVIDER_ERROR"  # provider reported an error in the response
    RECORD_ERROR = "RECORD_ERROR"  # one record could not be parsed or mapped


class RecordError(BaseModel):
    code: ErrorCode
    message: str
    record_index: Optional[int] = None  # position of the failed record in the response


class Status(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class Result(BaseModel):
    data: List[Any] = Field(default_factory=list)
    errors: List[RecordError] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None

    @computed_field
    @property
    def status(self) -> Status:
        # Derived, so it can never disagree with data and errors.
        if not self.errors:
            return Status.SUCCESS
        return Status.PARTIAL if self.data else Status.FAILED


class ProviderAdapter(ABC):
    """Turn one provider's raw API responses into normalized records."""

    def __init__(self, reference: Dict[str, Any]):
        # The provider's contracts/<provider>/lookup-reference.json, for documented code meanings.
        self.reference = reference

    @abstractmethod
    def company(self, path: Path, context: RequestContext) -> Result:
        """Company record from a company response file."""

    @abstractmethod
    def employees(self, path: Path, context: RequestContext) -> Result:
        """Employee records from an employee full-record response file."""

    @abstractmethod
    def direct_deposits(self, path: Path, context: RequestContext) -> Result:
        """Direct deposit records from a direct deposit response file."""

    @abstractmethod
    def deductions(self, path: Path, context: RequestContext) -> Result:
        """Deduction setup records from a deduction response file."""

    @abstractmethod
    def payroll_runs(self, path: Path, context: RequestContext) -> Result:
        """Payroll run records from a payroll run response file."""

    @abstractmethod
    def paychecks(self, path: Path, context: RequestContext) -> Result:
        """Paycheck records from a paycheck response file."""
