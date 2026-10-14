"""isolved payroll run and paycheck source models from primary Swagger v6.

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


class IsolvedPayrollInput(BaseModel):
    """Project payroll input; runs and paychecks retain separate source fields."""
    model_config = ConfigDict(extra="allow")

    payroll_runs: Optional[List[IsolvedPayrollRunHistoryModel]] = None
    paychecks: Optional[List[IsolvedCheckModel]] = None
    # Native paged-check response fields are also accepted.
    results: Optional[List[IsolvedCheckModel]] = None
    nextPageUrl: Optional[str] = None
    previousPageUrl: Optional[str] = None
    totalItems: Optional[int] = None
    totalPages: Optional[float] = None

    @classmethod
    def validate_response(cls, response: Any) -> IsolvedPayrollInput:
        # The native payroll-run endpoint returns an array.
        if isinstance(response, list):
            return cls.model_validate({"payroll_runs": response})
        return cls.model_validate(response)


class IsolvedPayrollRunHistoryModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.PayrollRunHistoryModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    impoundDate: Optional[str] = None
    inputMethod: Optional[str] = None
    payDate: Optional[str] = None
    payOfTheMonth: Optional[str] = None
    payPeriod: Optional[int] = None
    payrollRunType: Optional[str] = None
    periodBeginDate: Optional[str] = None
    periodEndDate: Optional[str] = None
    processApprovedBy: Optional[str] = None
    processedBy: Optional[str] = None
    regularCheckAutoPay: Optional[bool] = None
    runDate: Optional[str] = None
    runNumber: Optional[int] = None
    runTime: Optional[str] = None
    scheduledPayDate: Optional[str] = None
    scheduledRunDate: Optional[str] = None
    status: Optional[str] = None
    submittedBy: Optional[str] = None
    submittedDate: Optional[str] = None
    submittedTime: Optional[str] = None
    suppressPayStubEmailAlert: Optional[bool] = None


class IsolvedPayrollRunHistoryResponse(RootModel[List[IsolvedPayrollRunHistoryModel]]):
    """The endpoint returns a top-level array, not an object envelope."""


class IsolvedBaseLinkModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.Base.LinkModel."""
    model_config = ConfigDict(extra="allow")

    href: Optional[str] = None
    method: Optional[str] = None
    rel: Optional[str] = None


class IsolvedCheckAccrualModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.CheckAccrualModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    accrualName: Optional[str] = None
    amountAccrued: Optional[float] = None
    amountTaken: Optional[float] = None
    availableBalance: Optional[float] = None
    endingBalance: Optional[float] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedCheckBenefitTypeAccumulationModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.CheckBenefitTypeAccumulationModel."""
    model_config = ConfigDict(extra="allow")

    benefitDescription: Optional[str] = None
    benefitTitle: Optional[str] = None
    checkEligibleWages: Optional[float] = None
    checkEmployeeCatchUp: Optional[float] = None
    checkEmployeeDeduction: Optional[float] = None
    checkEmployerContribution: Optional[float] = None
    checkMatchEligibleWages: Optional[float] = None
    currentEligibleWages: Optional[float] = None
    currentEmployeeCatchUp: Optional[float] = None
    currentEmployeeDeduction: Optional[float] = None
    currentEmployerContribution: Optional[float] = None
    currentMatchEligibleWages: Optional[float] = None
    ftdEligibleWages: Optional[float] = None
    ftdEmployeeCatchUp: Optional[float] = None
    ftdEmployeeDeduction: Optional[float] = None
    ftdEmployerContribution: Optional[float] = None
    ftdMatchEligibleWages: Optional[float] = None
    mtdEligibleWages: Optional[float] = None
    mtdEmployeeCatchUp: Optional[float] = None
    mtdEmployeeDeduction: Optional[float] = None
    mtdEmployerContribution: Optional[float] = None
    mtdMatchEligibleWages: Optional[float] = None
    ptdEligibleWages: Optional[float] = None
    ptdEmployeeCatchUp: Optional[float] = None
    ptdEmployeeDeduction: Optional[float] = None
    ptdEmployerContribution: Optional[float] = None
    ptdMatchEligibleWages: Optional[float] = None
    qtdEligibleWages: Optional[float] = None
    qtdEmployeeCatchUp: Optional[float] = None
    qtdEmployeeDeduction: Optional[float] = None
    qtdEmployerContribution: Optional[float] = None
    qtdMatchEligibleWages: Optional[float] = None
    ytdEligibleWages: Optional[float] = None
    ytdEmployeeCatchUp: Optional[float] = None
    ytdEmployeeDeduction: Optional[float] = None
    ytdEmployerContribution: Optional[float] = None
    ytdMatchEligibleWages: Optional[float] = None


class IsolvedCheckAccumulationModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.CheckAccumulationModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    checkDollars: Optional[float] = None
    currentDollars: Optional[float] = None
    ftdDollars: Optional[float] = None
    itemCode: Optional[str] = None
    itemDescription: Optional[str] = None
    mtdDollars: Optional[float] = None
    ptdDollars: Optional[float] = None
    qtdDollars: Optional[float] = None
    sequence: Optional[int] = None
    ytdDollars: Optional[float] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedCheckDirectDepositAccumulationModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.CheckDirectDepositAccumulationModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    account: Optional[str] = None
    depositAmount: Optional[float] = None
    itemDescription: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedEarningAccumulationLaborDetailModel_LaborFieldDetail(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EarningAccumulationLaborDetailModel_LaborFieldDetail."""
    model_config = ConfigDict(extra="allow")

    laborId: Optional[int] = None
    laborTitle: Optional[str] = None
    laborValue: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None
    organizationId: Optional[int] = None


class IsolvedEarningAccumulationLaborDetailModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EarningAccumulationLaborDetailModel."""
    model_config = ConfigDict(extra="allow")

    dollars: Optional[float] = None
    hours: Optional[float] = None
    laborCode: Optional[str] = None
    labors: Optional[List[IsolvedEarningAccumulationLaborDetailModel_LaborFieldDetail]] = None
    rate: Optional[float] = None


class IsolvedCheckEarningAccumulationModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.CheckEarningAccumulationModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    checkDollars: Optional[float] = None
    checkHours: Optional[float] = None
    checkUnits: Optional[float] = None
    currentDollars: Optional[float] = None
    currentHours: Optional[float] = None
    currentUnits: Optional[float] = None
    ftdDollars: Optional[float] = None
    ftdHours: Optional[float] = None
    ftdUnits: Optional[float] = None
    isMemoEarning: Optional[bool] = None
    itemCode: Optional[str] = None
    itemDescription: Optional[str] = None
    labors: Optional[List[IsolvedEarningAccumulationLaborDetailModel]] = None
    mtdDollars: Optional[float] = None
    mtdHours: Optional[float] = None
    mtdUnits: Optional[float] = None
    ptdDollars: Optional[float] = None
    ptdHours: Optional[float] = None
    ptdUnits: Optional[float] = None
    qtdDollars: Optional[float] = None
    qtdHours: Optional[float] = None
    qtdUnits: Optional[float] = None
    sequence: Optional[int] = None
    ytdDollars: Optional[float] = None
    ytdHours: Optional[float] = None
    ytdUnits: Optional[float] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedEmployeeOrganizationModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeeOrganizationModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    displayOrder: Optional[int] = None
    organizationId: Optional[int] = None
    title: Optional[str] = None
    value: Optional[str] = None
    valueDescription: Optional[str] = None


class IsolvedSystemAlternateCalculationModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.SystemAlternateCalculationModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[str]
    description: Optional[str] = None
    state: Optional[str] = None
    taxCategoryCode: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedSystemFilingStatusModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.SystemFilingStatusModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[str]
    description: Optional[str] = None
    state: Optional[str] = None
    taxCategory: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedSystemStateModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.SystemStateModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[str]
    stateName: Optional[str] = None


class IsolvedCheckTaxCategoryModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.CheckTaxCategoryModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[str]
    additionalAmount: Optional[float] = None
    additionalIncome: Optional[float] = None
    additionalPercent: Optional[float] = None
    alternateCalculation: Optional[IsolvedSystemAlternateCalculationModel] = None
    city: Optional[str] = None
    deductionExemption: Optional[float] = None
    dependentExemption: Optional[float] = None
    description: Optional[str] = None
    exemptionAmount: Optional[float] = None
    filingStatus: Optional[IsolvedSystemFilingStatusModel] = None
    isBlocked: Optional[bool] = None
    isNonResident: Optional[bool] = None
    multipleJobs: Optional[bool] = None
    primaryExemptions: Optional[int] = None
    secondaryExemptions: Optional[int] = None
    state: Optional[IsolvedSystemStateModel] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedCheckTaxAccumulationModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.CheckTaxAccumulationModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    checkDollars: Optional[float] = None
    checkTaxableWages: Optional[float] = None
    currentDollars: Optional[float] = None
    currentTaxableWages: Optional[float] = None
    ftdDollars: Optional[float] = None
    ftdTaxableWages: Optional[float] = None
    isEmployeeTax: Optional[bool] = None
    itemCode: Optional[str] = None
    itemDescription: Optional[str] = None
    mtdDollars: Optional[float] = None
    mtdTaxableWages: Optional[float] = None
    ptdDollars: Optional[float] = None
    ptdTaxableWages: Optional[float] = None
    qtdDollars: Optional[float] = None
    qtdTaxableWages: Optional[float] = None
    sequence: Optional[int] = None
    ytdDollars: Optional[float] = None
    ytdTaxableWages: Optional[float] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedCheckModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.CheckModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    accruals: Optional[List[IsolvedCheckAccrualModel]] = None
    benefits: Optional[List[IsolvedCheckBenefitTypeAccumulationModel]] = None
    checkAmount: Optional[float] = None
    checkDate: Optional[str] = None
    checkNumber: Optional[int] = None
    checkSequence: Optional[int] = None
    checkTypeDescription: Optional[str] = None
    deductions: Optional[List[IsolvedCheckAccumulationModel]] = None
    directDepositAmount: Optional[float] = None
    directDeposits: Optional[List[IsolvedCheckDirectDepositAccumulationModel]] = None
    earnings: Optional[List[IsolvedCheckEarningAccumulationModel]] = None
    employeeAddress1: Optional[str] = None
    employeeAddress2: Optional[str] = None
    employeeCity: Optional[str] = None
    employeeFederalAddlAmountOrPercent: Optional[str] = None
    employeeFederalExemptions: Optional[int] = None
    employeeFederalFilingStatus: Optional[str] = None
    employeeId: Optional[int] = None
    employeeName: Optional[str] = None
    employeeNumber: Optional[str] = None
    employeeOrganizations: Optional[List[IsolvedEmployeeOrganizationModel]] = None
    employeeSSN: Optional[str] = None
    employeeState: Optional[str] = None
    employeeStateAddlAmountOrPercent: Optional[str] = None
    employeeStateExemptions: Optional[int] = None
    employeeStateFilingStatus: Optional[str] = None
    employeeZipCode: Optional[str] = None
    garnishments: Optional[List[IsolvedCheckAccumulationModel]] = None
    grossPay: Optional[float] = None
    grossWages: Optional[float] = None
    isRemoteWorker: Optional[bool] = None
    legalCompanyName: Optional[str] = None
    netPay: Optional[float] = None
    payrollRunNumber: Optional[int] = None
    payrollRunType: Optional[str] = None
    periodBeginDate: Optional[str] = None
    periodEndDate: Optional[str] = None
    reissueCheckDate: Optional[str] = None
    reissueCheckNumber: Optional[int] = None
    taxCategories: Optional[List[IsolvedCheckTaxCategoryModel]] = None
    taxes: Optional[List[IsolvedCheckTaxAccumulationModel]] = None
    vertexResidentGeoCode: Optional[str] = None
    vertexSchoolDistrictCode: Optional[int] = None
    vertexWorkGeoCode: Optional[str] = None
    voucherNumber: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedPagedModelItemListOfCheckModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.PagedModelItemListOfCheckModel."""
    model_config = ConfigDict(extra="allow")

    nextPageUrl: Optional[str] = None
    previousPageUrl: Optional[str] = None
    results: Optional[List[IsolvedCheckModel]] = None
    totalItems: Optional[int] = None
    totalPages: Optional[float] = None
