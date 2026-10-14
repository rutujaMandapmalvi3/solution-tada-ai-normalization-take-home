"""UKG Ready payroll run and paycheck source models.

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


class UKGReadyPayrollRunResponse(BaseModel):
    """Cached schema path: 358."""
    model_config = ConfigDict(extra="allow")

    payrolls: List[UKGReadyPayrollRunResponsePayrollsItem]


class UKGReadyPayrollRunResponsePayrollsItem(BaseModel):
    """Cached schema path: 358/payrolls[]."""
    model_config = ConfigDict(extra="allow")

    id: int
    name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    pay_date: Optional[str] = None
    type: Optional[UKGReadyPayrollRunResponsePayrollsItemType] = None
    status: Optional[str] = None
    ein: Optional[UKGReadyPayrollRunResponsePayrollsItemEin] = None
    billable: Optional[bool] = None
    direct_deposit_date: Optional[str] = None
    sch_submit_date_time: Optional[str] = None
    invoice_generator_id: Optional[int] = None
    adjustment_grab_YTD_from_payroll_id: Optional[int] = None
    dflt_pay_statement_type_id: Optional[int] = None
    dflt_pay_stub_note: Optional[str] = None
    links: Optional[UKGReadyPayrollRunResponsePayrollsItemLinks] = Field(default=None, alias="_links")


class UKGReadyPayrollRunResponsePayrollsItemType(BaseModel):
    """Cached schema path: 358/payrolls[]/type."""
    model_config = ConfigDict(extra="allow")

    id: int
    display_name: Optional[str] = None


class UKGReadyPayrollRunResponsePayrollsItemEin(BaseModel):
    """Cached schema path: 358/payrolls[]/ein."""
    model_config = ConfigDict(extra="allow")

    id: int
    ein_name: Optional[str] = None
    ein_tax_id: Optional[str] = None
    # Live-only field; type observed in the saved response.
    ein_country_id: Optional[str] = None


class UKGReadyPayrollRunResponsePayrollsItemLinks(BaseModel):
    """Cached schema path: 358/payrolls[]/_links."""
    model_config = ConfigDict(extra="allow")

    self: Optional[str] = None


class UKGReadyPaycheckListResponse(BaseModel):
    """Cached schema path: 362."""
    model_config = ConfigDict(extra="allow")

    pay_statements: List[UKGReadyPaycheckListResponsePayStatementsItem]


class UKGReadyPaycheckListResponsePayStatementsItem(BaseModel):
    """Cached schema path: 362/pay_statements[]."""
    model_config = ConfigDict(extra="allow")

    # Cached list schema omits the object wrapper; its HTML example confirms employee.account_id.
    employee: Optional[UKGReadyPaycheckListResponsePayStatementsItemEmployee] = None
    id: int
    pay_date: Optional[str] = None
    status: Optional[str] = None
    type: Optional[UKGReadyPaycheckListResponsePayStatementsItemType] = None
    pay_period_start: Optional[str] = None
    pay_period_end: Optional[str] = None
    links: Optional[UKGReadyPaycheckListResponsePayStatementsItemLinks] = Field(default=None, alias="_links")


class UKGReadyPaycheckListResponsePayStatementsItemEmployee(BaseModel):
    """Cached schema path: 362/pay_statements[]/employee."""
    model_config = ConfigDict(extra="allow")

    account_id: Optional[float] = None


class UKGReadyPaycheckListResponsePayStatementsItemType(BaseModel):
    """Cached schema path: 362/pay_statements[]/type."""
    model_config = ConfigDict(extra="allow")

    id: int
    display_name: Optional[str] = None


class UKGReadyPaycheckListResponsePayStatementsItemLinks(BaseModel):
    """Cached schema path: 362/pay_statements[]/_links."""
    model_config = ConfigDict(extra="allow")

    self: Optional[str] = None


class UKGReadyPaycheckDetails(BaseModel):
    """Cached schema path: 364."""
    model_config = ConfigDict(extra="allow")

    employee: Optional[UKGReadyPaycheckDetailsEmployee] = None
    id: Optional[int]
    pay_date: Optional[str] = None
    status: Optional[str] = None
    type: Optional[UKGReadyPaycheckDetailsType] = None
    pay_period_start: Optional[str] = None
    pay_period_end: Optional[str] = None
    earnings: Optional[List[UKGReadyPaycheckDetailsEarningsItem]] = None
    deductions: Optional[List[UKGReadyPaycheckDetailsDeductionsItem]] = None
    taxes: Optional[List[UKGReadyPaycheckDetailsTaxesItem]] = None
    messages: Optional[List[UKGReadyPaycheckDetailsMessagesItem]] = None
    payments: Optional[List[UKGReadyPaycheckDetailsPaymentsItem]] = None


class UKGReadyPaycheckDetailsEmployee(BaseModel):
    """Cached schema path: 364/employee."""
    model_config = ConfigDict(extra="allow")

    account_id: Optional[float] = None


class UKGReadyPaycheckDetailsType(BaseModel):
    """Cached schema path: 364/type."""
    model_config = ConfigDict(extra="allow")

    id: int
    display_name: Optional[str] = None


class UKGReadyPaycheckDetailsEarningsItem(BaseModel):
    """Cached schema path: 364/earnings[]."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    type_name: Optional[str] = None
    batch: Optional[UKGReadyPaycheckDetailsEarningsItemBatch] = None
    date_range_from: Optional[str] = None
    date_range_to: Optional[str] = None
    hours: Optional[int] = None
    base_rate: Optional[float] = None
    quantity: Optional[float] = None
    ee_amount: Optional[float] = None
    workers_comp_code: Optional[UKGReadyPaycheckDetailsEarningsItemWorkersCompCode] = None
    shift: Optional[UKGReadyPaycheckDetailsEarningsItemShift] = None
    cost_centers: Optional[List[UKGReadyPaycheckDetailsEarningsItemCostCentersItem]] = None
    earning: Optional[UKGReadyPaycheckDetailsEarningsItemEarning] = None


class UKGReadyPaycheckDetailsEarningsItemBatch(BaseModel):
    """Cached schema path: 364/earnings[]/batch."""
    model_config = ConfigDict(extra="allow")

    id: int
    display_name: Optional[str] = None


class UKGReadyPaycheckDetailsEarningsItemWorkersCompCode(BaseModel):
    """Cached schema path: 364/earnings[]/workers_comp_code."""
    model_config = ConfigDict(extra="allow")

    external_id: Optional[str] = None


class UKGReadyPaycheckDetailsEarningsItemShift(BaseModel):
    """Cached schema path: 364/earnings[]/shift."""
    model_config = ConfigDict(extra="allow")

    id: int
    name: Optional[str] = None


class UKGReadyPaycheckDetailsEarningsItemCostCentersItem(BaseModel):
    """Cached schema path: 364/earnings[]/cost_centers[]."""
    model_config = ConfigDict(extra="allow")

    index: Optional[int] = None
    value: Optional[UKGReadyPaycheckDetailsEarningsItemCostCentersItemValue] = None


class UKGReadyPaycheckDetailsEarningsItemCostCentersItemValue(BaseModel):
    """Cached schema path: 364/earnings[]/cost_centers[]/value."""
    model_config = ConfigDict(extra="allow")

    id: int


class UKGReadyPaycheckDetailsEarningsItemEarning(BaseModel):
    """Cached schema path: 364/earnings[]/earning."""
    model_config = ConfigDict(extra="allow")

    name: Optional[str] = None
    external_id: Optional[str] = None
    code: Optional[str] = None


class UKGReadyPaycheckDetailsDeductionsItem(BaseModel):
    """Cached schema path: 364/deductions[]."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    type_name: Optional[str] = None
    batch: Optional[UKGReadyPaycheckDetailsDeductionsItemBatch] = None
    date_range_from: Optional[str] = None
    date_range_to: Optional[str] = None
    quantity: Optional[float] = None
    base_rate: Optional[float] = None
    ee_amount: Optional[float] = None
    er_amount: Optional[float] = None
    vendor: Optional[UKGReadyPaycheckDetailsDeductionsItemVendor] = None
    cost_centers: Optional[List[UKGReadyPaycheckDetailsDeductionsItemCostCentersItem]] = None
    workers_comp_code: Optional[UKGReadyPaycheckDetailsDeductionsItemWorkersCompCode] = None
    deduction: Optional[UKGReadyPaycheckDetailsDeductionsItemDeduction] = None


class UKGReadyPaycheckDetailsDeductionsItemBatch(BaseModel):
    """Cached schema path: 364/deductions[]/batch."""
    model_config = ConfigDict(extra="allow")

    id: int
    display_name: Optional[str] = None


class UKGReadyPaycheckDetailsDeductionsItemVendor(BaseModel):
    """Cached schema path: 364/deductions[]/vendor."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    name: Optional[str] = None


class UKGReadyPaycheckDetailsDeductionsItemCostCentersItem(BaseModel):
    """Cached schema path: 364/deductions[]/cost_centers[]."""
    model_config = ConfigDict(extra="allow")

    index: Optional[int] = None
    value: Optional[UKGReadyPaycheckDetailsDeductionsItemCostCentersItemValue] = None


class UKGReadyPaycheckDetailsDeductionsItemCostCentersItemValue(BaseModel):
    """Cached schema path: 364/deductions[]/cost_centers[]/value."""
    model_config = ConfigDict(extra="allow")

    id: int


class UKGReadyPaycheckDetailsDeductionsItemWorkersCompCode(BaseModel):
    """Cached schema path: 364/deductions[]/workers_comp_code."""
    model_config = ConfigDict(extra="allow")

    external_id: Optional[str] = None


class UKGReadyPaycheckDetailsDeductionsItemDeduction(BaseModel):
    """Cached schema path: 364/deductions[]/deduction."""
    model_config = ConfigDict(extra="allow")

    name: Optional[str] = None
    external_id: Optional[str] = None
    code: Optional[str] = None


class UKGReadyPaycheckDetailsTaxesItem(BaseModel):
    """Cached schema path: 364/taxes[]."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    type_name: Optional[str] = None
    batch: Optional[UKGReadyPaycheckDetailsTaxesItemBatch] = None
    ee_amount: Optional[float] = None
    er_amount: Optional[float] = None
    ee_gross_wage: Optional[float] = None
    ee_subject_wage: Optional[float] = None
    ee_gross_subject_wage: Optional[float] = None
    er_gross_wage: Optional[float] = None
    er_subject_wage: Optional[float] = None
    er_gross_subject_wage: Optional[float] = None
    company_tax: Optional[UKGReadyPaycheckDetailsTaxesItemCompanyTax] = None


class UKGReadyPaycheckDetailsTaxesItemBatch(BaseModel):
    """Cached schema path: 364/taxes[]/batch."""
    model_config = ConfigDict(extra="allow")

    id: int
    display_name: Optional[str] = None


class UKGReadyPaycheckDetailsTaxesItemCompanyTax(BaseModel):
    """Cached schema path: 364/taxes[]/company_tax."""
    model_config = ConfigDict(extra="allow")

    code: Optional[str] = None
    name: Optional[str] = None
    abbrev: Optional[str] = None


class UKGReadyPaycheckDetailsMessagesItem(BaseModel):
    """Cached schema path: 364/messages[]."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    type_name: Optional[str] = None
    message: Optional[UKGReadyPaycheckDetailsMessagesItemMessage] = None
    batch: Optional[UKGReadyPaycheckDetailsMessagesItemBatch] = None


class UKGReadyPaycheckDetailsMessagesItemMessage(BaseModel):
    """Cached schema path: 364/messages[]/message."""
    model_config = ConfigDict(extra="allow")

    text: Optional[str] = None
    severity: Optional[str] = None


class UKGReadyPaycheckDetailsMessagesItemBatch(BaseModel):
    """Cached schema path: 364/messages[]/batch."""
    model_config = ConfigDict(extra="allow")

    id: int
    display_name: Optional[str] = None


class UKGReadyPaycheckDetailsPaymentsItem(BaseModel):
    """Cached schema path: 364/payments[]."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    hours: Optional[int] = None
    quantity: Optional[float] = None
    ee_amount: Optional[float] = None
    type_name: Optional[str] = None
    batch: Optional[UKGReadyPaycheckDetailsPaymentsItemBatch] = None


class UKGReadyPaycheckDetailsPaymentsItemBatch(BaseModel):
    """Cached schema path: 364/payments[]/batch."""
    model_config = ConfigDict(extra="allow")

    id: int
    display_name: Optional[str] = None


class UKGReadyPayrollInput(BaseModel):
    """Project payroll input preserving native run and paycheck schemas."""
    model_config = ConfigDict(extra="allow")

    payroll_runs: Optional[UKGReadyPayrollRunResponse] = None
    paycheck_list: Optional[UKGReadyPaycheckListResponse] = None
    paychecks: Optional[List[UKGReadyPaycheckDetails]] = None

    @classmethod
    def validate_response(cls, response: Any) -> UKGReadyPayrollInput:
        if not isinstance(response, dict):
            return cls.model_validate(response)
        payload = dict(response)
        if "payrolls" in response:
            if "payroll_runs" in response:
                raise ValueError("Supply payroll_runs or native payrolls, not both")
            payload["payroll_runs"] = response
        if "pay_statements" in response:
            if "paycheck_list" in response:
                raise ValueError("Supply paycheck_list or native pay_statements, not both")
            payload["paycheck_list"] = response
        # A native paycheck-detail record has its own ID, without a list wrapper.
        if "id" in response:
            if "paychecks" in response:
                raise ValueError("Supply paychecks or a native paycheck detail, not both")
            payload["paychecks"] = [response]
        return cls.model_validate(payload)
