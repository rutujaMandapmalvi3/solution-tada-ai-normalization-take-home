"""PrismHR paycheck response source models.

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


class PrismHREmployeeTax(BaseModel):
    """Source schema: EmployeeTax."""
    model_config = ConfigDict(extra="allow")

    empTaxDeductCode: Optional[str] = None
    empTaxDeductCodeDesc: Optional[str] = None
    empTaxableAmount: Optional[float] = None
    empTaxAmount: Optional[float] = None
    empOverLimitAmount: Optional[float] = None


class PrismHRWorkerComp(BaseModel):
    """Source schema: WorkerComp."""
    model_config = ConfigDict(extra="allow")

    wcClass: Optional[str] = None
    wcTaxablePay: Optional[float] = None
    wcPremAmount: Optional[float] = None
    wcBillAmount: Optional[float] = None
    wcPremBill: Optional[float] = None


class PrismHREarning(BaseModel):
    """Source schema: Earning."""
    model_config = ConfigDict(extra="allow")

    payCode: Optional[str] = None
    payClass: Optional[str] = None
    payClassDescription: Optional[str] = None
    chargeDate: Optional[str] = None
    hoursUnits: Optional[float] = None
    hoursWorked: Optional[float] = None
    unitRate: Optional[float] = None
    payAmount: Optional[float] = None
    division: Optional[str] = None
    jobCode: Optional[str] = None
    shift: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    glCode: Optional[str] = None
    workComp: Optional[str] = None
    projWork: Optional[str] = None
    projPhase: Optional[str] = None


class PrismHROtherEarningsDetail(BaseModel):
    """Source schema: OtherEarningsDetail."""
    model_config = ConfigDict(extra="allow")

    otherEarnCode: Optional[str] = None
    otherEarnsDesc: Optional[str] = None
    otherEarnAmount: Optional[float] = None


class PrismHRFsaMatch(BaseModel):
    """Source schema: FsaMatch."""
    model_config = ConfigDict(extra="allow")

    code: Optional[str] = None
    description: Optional[str] = None
    matchAmt: Optional[float] = None
    acctType: Optional[str] = None


class PrismHRCompanyTax(BaseModel):
    """Source schema: CompanyTax."""
    model_config = ConfigDict(extra="allow")

    comTaxEntity: Optional[str] = None
    comTaxDeductCode: Optional[str] = None
    comTaxDeductCodeDesc: Optional[str] = None
    comExemptAmount: Optional[float] = None
    comShelteredAmount: Optional[float] = None
    comTaxableAmount: Optional[float] = None
    comTaxType: Optional[str] = None
    comTaxAmount: Optional[float] = None
    comOvrLimit: Optional[float] = None
    comTaxRate: Optional[float] = None
    comClientSutaRpt: Optional[str] = None


class PrismHRDeduction(BaseModel):
    """Source schema: Deduction."""
    model_config = ConfigDict(extra="allow")

    deductCode: Optional[str] = None
    deductDescription: Optional[str] = None
    deductAmount: Optional[float] = None
    deductType: Optional[str] = None
    deductUnionId: Optional[str] = None
    planId: Optional[str] = None


class PrismHROtherDeduction(BaseModel):
    """Source schema: OtherDeduction."""
    model_config = ConfigDict(extra="allow")

    otherDeductCode: Optional[str] = None
    otherDeductDescription: Optional[str] = None
    otherDeductAmount: Optional[float] = None
    otherDeductOneTimeSwitch: Optional[str] = None


class PrismHRBenefit(BaseModel):
    """Source schema: Benefit."""
    model_config = ConfigDict(extra="allow")

    planId: Optional[str] = None
    premiumAmt: Optional[float] = None
    empContrib: Optional[float] = None
    empDeduct: Optional[float] = None
    coveragePeriod: Optional[str] = None
    adjRef: Optional[str] = None
    premiumCost: Optional[float] = None


class PrismHRPayrollVoucherDirectDeposit(BaseModel):
    """Source schema: PayrollVoucher-DirectDeposit."""
    model_config = ConfigDict(extra="allow")

    transitNum: Optional[str] = None
    accountNum: Optional[str] = None
    status: Optional[str] = None
    amount: Optional[float] = None


class PrismHREmployerContribution(BaseModel):
    """Source schema: EmployerContribution."""
    model_config = ConfigDict(extra="allow")

    code: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None


class PrismHRRetirement(BaseModel):
    """Source schema: Retirement."""
    model_config = ConfigDict(extra="allow")

    planId: Optional[str] = None
    planYearPeriod: Optional[str] = None
    baseEarnings: Optional[float] = None
    electiveContributionsPreTax: Optional[float] = None
    catchUpContributionsPreTax: Optional[float] = None
    rothContributionsPostTax: Optional[float] = None
    rothCatchUpContributionsPostTax: Optional[float] = None
    employeeContributionsPostTax: Optional[float] = None
    employerMatchingContributions: Optional[float] = None
    employerNonElectiveContributions: Optional[float] = None
    employerSafeHarborMatchType1: Optional[float] = None
    employerSafeHarborMatchType2: Optional[float] = None
    peoMatchingContribution: Optional[float] = None
    employeeRetirementLoanPayments: Optional[float] = None


class PrismHRDebitSegmentDetail(BaseModel):
    """Source schema: DebitSegmentDetail."""
    model_config = ConfigDict(extra="allow")

    debitSegmentName: Optional[str] = None
    debitSegmentValue: Optional[str] = None


class PrismHRGlDebitData(BaseModel):
    """Source schema: GlDebitData."""
    model_config = ConfigDict(extra="allow")

    glDebitAcct: Optional[str] = None
    glDebitAmount: Optional[float] = None
    debitSegmentDetail: Optional[List[PrismHRDebitSegmentDetail]] = None


class PrismHRCreditSegmentDetail(BaseModel):
    """Source schema: CreditSegmentDetail."""
    model_config = ConfigDict(extra="allow")

    creditSegmentName: Optional[str] = None
    creditSegmentValue: Optional[str] = None


class PrismHRGlCreditData(BaseModel):
    """Source schema: GlCreditData."""
    model_config = ConfigDict(extra="allow")

    glCreditAcct: Optional[str] = None
    glCreditAmount: Optional[float] = None
    creditSegmentDetail: Optional[List[PrismHRCreditSegmentDetail]] = None


class PrismHRGlAcctDistribution(BaseModel):
    """Source schema: GlAcctDistribution."""
    model_config = ConfigDict(extra="allow")

    glTotalDebit: Optional[float] = None
    glTotalCredit: Optional[float] = None
    glDebitData: Optional[List[PrismHRGlDebitData]] = None
    glCreditData: Optional[List[PrismHRGlCreditData]] = None


class PrismHRAsoCredits(BaseModel):
    """Source schema: AsoCredits."""
    model_config = ConfigDict(extra="allow")

    glCreditAcct: Optional[str] = None
    glCreditAcctDesc: Optional[str] = None
    glTotalCredit: Optional[float] = None


class PrismHRAsoDebits(BaseModel):
    """Source schema: AsoDebits."""
    model_config = ConfigDict(extra="allow")

    glDebitAcct: Optional[str] = None
    glDebitAcctDesc: Optional[str] = None
    glTotalDebit: Optional[float] = None


class PrismHRAsoClientGLAcctDistribution(BaseModel):
    """Source schema: AsoClientGLAcctDistribution."""
    model_config = ConfigDict(extra="allow")

    asoCredits: Optional[List[PrismHRAsoCredits]] = None
    asoDebits: Optional[List[PrismHRAsoDebits]] = None


class PrismHRTaxFilingStatus(BaseModel):
    """Source schema: TaxFilingStatus."""
    model_config = ConfigDict(extra="allow")

    taxAuthId: Optional[str] = None
    taxAuthName: Optional[str] = None
    filingStatus: Optional[str] = None
    allowances: Optional[str] = None
    overrideType: Optional[str] = None
    overrideAmount: Optional[str] = None


class PrismHRPayrollVoucherWCInformation(BaseModel):
    """Source schema: PayrollVoucherWCInformation."""
    model_config = ConfigDict(extra="allow")

    wcPolicy: Optional[str] = None
    wcNotEligible: Optional[List[str]] = None
    wcSheltered: Optional[List[str]] = None
    wcOverBillRate: Optional[List[str]] = None
    wcBillIncludeCredit: Optional[List[str]] = None
    wcBillAmtIncludeCredit: Optional[List[str]] = None
    wcWeekEndDate: Optional[str] = None
    wcPolicyYearEnd: Optional[str] = None
    wcPremiumPay: Optional[List[str]] = None
    wcTria: Optional[List[str]] = None
    wcRateTemplate: Optional[str] = None
    wcOverBillAmt: Optional[List[str]] = None
    wcGrossRate: Optional[List[str]] = None
    wcStraightPay: Optional[List[str]] = None
    wcPremAmt: Optional[List[str]] = None
    wcClass: Optional[List[str]] = None
    wcBasePay: Optional[List[str]] = None
    wcBillAmt: Optional[List[str]] = None
    wcTaxablePay: Optional[List[str]] = None
    wcPremiumBill: Optional[List[str]] = None
    wcAccruedAmt: Optional[List[str]] = None
    wcState: Optional[str] = None
    wcHoursWorked: Optional[List[str]] = None
    wcEarnNonComp: Optional[List[str]] = None
    wcPayLocationReg: Optional[List[str]] = None
    wcPayLocationOT: Optional[List[str]] = None
    wcPayLocationBreakCode: Optional[List[str]] = None
    wcRecalcDifference: Optional[List[str]] = None
    wcLocationState: Optional[List[str]] = None
    wcLocationPolicy: Optional[List[str]] = None
    wcLocationYearEndDate: Optional[List[str]] = None
    wcLocationTemplate: Optional[List[str]] = None
    wcPayLocationExp: Optional[List[str]] = None


class PrismHRFromArrears(BaseModel):
    """Source schema: FromArrears."""
    model_config = ConfigDict(extra="allow")

    dedCode: Optional[str] = None
    dedDescription: Optional[str] = None
    arrearsAmt: Optional[str] = None
    arrearsDate: Optional[str] = None
    arrearsRefNo: Optional[str] = None
    coveragePeriod: Optional[str] = None
    planId: Optional[str] = None
    unionId: Optional[str] = None
    loanNo: Optional[str] = None


class PrismHRToArrears(BaseModel):
    """Source schema: ToArrears."""
    model_config = ConfigDict(extra="allow")

    dedCode: Optional[str] = None
    dedDescription: Optional[str] = None
    arrearsAmt: Optional[str] = None
    coveragePeriod: Optional[str] = None
    planId: Optional[str] = None
    unionId: Optional[str] = None
    loanNo: Optional[str] = None


class PrismHRPayrollVoucher(BaseModel):
    """Source schema: PayrollVoucher."""
    model_config = ConfigDict(extra="allow")

    voucherId: str
    status: Optional[str] = None
    type: Optional[str] = None
    voidDate: Optional[str] = None
    checkNumber: Optional[str] = None
    payDate: Optional[str] = None
    employeeId: Optional[str] = None
    payPeriod: Optional[str] = None
    payPeriodStart: Optional[str] = None
    payPeriodEnd: Optional[str] = None
    payGroup: Optional[str] = None
    dateProcessed: Optional[str] = None
    totalEarnings: Optional[float] = None
    employeeTax: Optional[List[PrismHREmployeeTax]] = None
    netPay: Optional[float] = None
    voidVoucherId: Optional[str] = None
    fitTaxableAmount: Optional[float] = None
    earnAmount: Optional[float] = None
    otherEarnAmount: Optional[float] = None
    wcHomeClass: Optional[str] = None
    wcState: Optional[str] = None
    workerComp: Optional[List[PrismHRWorkerComp]] = None
    earning: Optional[List[PrismHREarning]] = None
    otherEarningsDetail: Optional[List[PrismHROtherEarningsDetail]] = None
    fsaMatch: Optional[List[PrismHRFsaMatch]] = None
    companyTax: Optional[List[PrismHRCompanyTax]] = None
    batchId: Optional[str] = None
    deduction: Optional[List[PrismHRDeduction]] = None
    otherDeduction: Optional[List[PrismHROtherDeduction]] = None
    benefit: Optional[List[PrismHRBenefit]] = None
    bankAccount: Optional[str] = None
    checkNum: Optional[str] = None
    checkAmt: Optional[float] = None
    payStubType: Optional[str] = None
    checkAccountACH: Optional[str] = None
    directDeposit: Optional[List[PrismHRPayrollVoucherDirectDeposit]] = None
    employerContributions: Optional[List[PrismHREmployerContribution]] = None
    retirement: Optional[PrismHRRetirement] = None
    glAcctDistribution: Optional[PrismHRGlAcctDistribution] = None
    # Contract-required, but optional under project policy; null observed in the saved response.
    asoClientGLAcctDistribution: Optional[PrismHRAsoClientGLAcctDistribution] = None
    taxFilingStatus: Optional[List[PrismHRTaxFilingStatus]] = None
    wcInformation: Optional[PrismHRPayrollVoucherWCInformation] = None
    fromArrears: Optional[List[PrismHRFromArrears]] = None
    toArrears: Optional[List[PrismHRToArrears]] = None
    importBatchNo: Optional[str] = None
    # Live-only field; type verified from the saved response.
    isManualCheck: Optional[str] = None
    # Live-only field; type verified from the saved response.
    hsaPeoMatch: Optional[str] = None


class PrismHRPayrollResponseWithPagination(BaseModel):
    """Source schema: PayrollResponseWithPagination."""
    model_config = ConfigDict(extra="allow")

    errorCode: str
    errorMessage: str
    extension: Optional[PrismHRExtension] = None
    # Accept the contract name and the observed live name.
    payrollVouchers: Optional[List[PrismHRPayrollVoucher]] = Field(
        default=None, validation_alias=AliasChoices("payrollVouchers", "payrollVoucher")
    )
    total: Optional[int] = None
    startpage: Optional[int] = None
    count: Optional[int] = None
