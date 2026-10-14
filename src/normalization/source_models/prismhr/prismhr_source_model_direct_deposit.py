"""Source models for regular deposit setup and paycheck deposit payments.

EmployeeDirectDeposit and AchVoucher are reused from the employee source file.
PayrollVoucher-DirectDeposit is reused from the paycheck source file.
Paycheck payments have their own structure; they do not use the employee envelope.
HSA deposit settings are excluded from this module.
No canonical mapping, unit conversion, or business-rule validation occurs here.

Project validation policy: record IDs and documented required wrapper fields
require presence. Other fields accept missing/null; existing ID nullability
is retained. Reference IDs are optional unless they identify this record.
"""
from typing import List, Optional

from .prismhr_source_model_employee import (
    PrismHRAchVoucher,
    PrismHRDirectDeposit,
    PrismHREmployee,
    PrismHREmployeeResponse,
    PrismHRExtension,
)

from .prismhr_source_model_paycheck import PrismHRPayrollVoucherDirectDeposit


class PrismHRDirectDepositResponse(PrismHREmployeeResponse):
    """Employee envelope with typed records, including their deposit setup."""

    employee: Optional[List[PrismHREmployee]] = None


__all__ = [
    "PrismHRDirectDepositResponse",
    "PrismHRDirectDeposit",
    "PrismHRAchVoucher",
    "PrismHRPayrollVoucherDirectDeposit",
]
