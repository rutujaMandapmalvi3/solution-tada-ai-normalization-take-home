"""PrismHR company response source models.

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


class PrismHRClientMasterPayCode(BaseModel):
    """Source schema: ClientMaster-PayCode."""
    model_config = ConfigDict(extra="allow")

    payCodeId: Optional[str]
    printOnPayStub: Optional[str] = None


class PrismHRClientMasterDeductionCode(BaseModel):
    """Source schema: ClientMaster-DeductionCode."""
    model_config = ConfigDict(extra="allow")

    deductionCodeId: Optional[str]
    printOnPayStub: Optional[str] = None
    worksiteUserSelectable: Optional[str] = None


class PrismHRArrear(BaseModel):
    """Source schema: Arrear."""
    model_config = ConfigDict(extra="allow")

    loanDeductionCodeId: Optional[str] = None


class PrismHREmployeeType(BaseModel):
    """Source schema: EmployeeType."""
    model_config = ConfigDict(extra="allow")

    typeCodeId: Optional[str]


class PrismHREmployeeStatus(BaseModel):
    """Source schema: EmployeeStatus."""
    model_config = ConfigDict(extra="allow")

    statusCodeId: Optional[str]


class PrismHRReason(BaseModel):
    """Source schema: Reason."""
    model_config = ConfigDict(extra="allow")

    reasonCodeId: Optional[str]


class PrismHRClientMasterMiscGL(BaseModel):
    """Source schema: ClientMaster-MiscGL."""
    model_config = ConfigDict(extra="allow")

    glCode: Optional[str] = None
    miscGLCode: Optional[str] = None


class PrismHRObservedHoliday(BaseModel):
    """Source schema: ObservedHoliday."""
    model_config = ConfigDict(extra="allow")

    name: Optional[str] = None
    description: Optional[str] = None
    holidayDate: Optional[List[str]] = None


class PrismHRAltEmployer(BaseModel):
    """Source schema: AltEmployer."""
    model_config = ConfigDict(extra="allow")

    altEmployerId: str
    altCostCtr: Optional[str] = None
    altCheckingAcct: Optional[str] = None
    altAchAcct: Optional[str] = None
    altDisplayName: Optional[str] = None
    suppressClientAccess: Optional[str] = None


class PrismHRClientRetirementPlanObject(BaseModel):
    """Source schema: ClientRetirementPlanObject."""
    model_config = ConfigDict(extra="allow")

    retirePlan: Optional[str] = None
    thirdPartyPlanId: Optional[str] = None


class PrismHRBillFixed(BaseModel):
    """Source schema: BillFixed."""
    model_config = ConfigDict(extra="allow")

    billFixedSpecRate: Optional[str] = None
    billFixedSpecFrom: Optional[str] = None
    billFixedSpecTo: Optional[str] = None


class PrismHRHolidayPay(BaseModel):
    """Source schema: HolidayPay."""
    model_config = ConfigDict(extra="allow")

    holidayOnDay: Optional[str] = None
    holidayPayOnDay: Optional[str] = None
    holidayPayBefAft: Optional[str] = None


class PrismHRSdiDedn(BaseModel):
    """Source schema: SdiDedn."""
    model_config = ConfigDict(extra="allow")

    sdiTaxCode: Optional[str] = None
    sdiDednCode: Optional[str] = None


class PrismHRClientMasterClientTax(BaseModel):
    """Source schema: ClientMaster-ClientTax."""
    model_config = ConfigDict(extra="allow")

    suiState: Optional[str] = None
    suiStateEmpId: Optional[str] = None
    stateTaxId: Optional[str] = None
    # Contract-required, but optional under project policy; null observed in the saved response.
    ctrStartDate: Optional[str] = None
    # Contract-required, but optional under project policy; null observed in the saved response.
    ctrEndDate: Optional[str] = None
    suiSecondaryId: Optional[str] = None
    miscTaxId: Optional[str] = None
    miscTaxCode: Optional[str] = None


class PrismHRRedir(BaseModel):
    """Source schema: Redir."""
    model_config = ConfigDict(extra="allow")

    redirTaxCode: Optional[str] = None
    redirToTaxCode: Optional[str] = None


class PrismHRRegRebuild(BaseModel):
    """Source schema: RegRebuild."""
    model_config = ConfigDict(extra="allow")

    # Contract says string; the saved response also supplies an integer.
    regRebuildDate: Optional[Union[str, int]] = None
    regRebuildUser: Optional[str] = None
    regRebuildReason: Optional[str] = None
    regRebuildYear: Optional[str] = None


class PrismHRCommission(BaseModel):
    """Source schema: Commission."""
    model_config = ConfigDict(extra="allow")

    commSalesperson: Optional[str] = None
    commDateFrom: Optional[str] = None
    # Contract-required, but optional under project policy; null observed in the saved response.
    commDateTo: Optional[str] = None
    commAmount: Optional[str] = None
    commFlatPct: Optional[bool] = None
    commBasedOn: Optional[str] = None
    commBasedOnPlan: Optional[str] = None
    # Live-only field; type verified from the saved response.
    commType: Optional[str] = None
    # Live-only field; type verified from the saved response.
    targetAmt: Optional[str] = None


class PrismHRBillEvent(BaseModel):
    """Source schema: BillEvent."""
    model_config = ConfigDict(extra="allow")

    billEvtCode: Optional[str] = None
    billEvtRate: Optional[str] = None
    billEvtSpecialRate: Optional[str] = None
    # Contract-required, but optional under project policy; null observed in the saved response.
    billEvtSpecialFrom: Optional[str] = None
    # Contract-required, but optional under project policy; null observed in the saved response.
    billEvtSpecialTo: Optional[str] = None


class PrismHRReportFee(BaseModel):
    """Source schema: ReportFee."""
    model_config = ConfigDict(extra="allow")

    rptCode: Optional[str] = None
    rptFee: Optional[str] = None


class PrismHRMySupportTeamDashboard(BaseModel):
    """Source schema: MySupportTeamDashboard."""
    model_config = ConfigDict(extra="allow")

    dashFieldName: Optional[str] = None
    dashFieldValue: Optional[str] = None


class PrismHREnrollOnboardControls(BaseModel):
    """Source schema: EnrollOnboardControls."""
    model_config = ConfigDict(extra="allow")

    elecBenefitsEnroll: Optional[str] = None
    elecOnboarding: Optional[str] = None
    elecOnboardRehire: Optional[str] = None
    i9businessAddress: Optional[str] = None
    allowUploadDocs: Optional[str] = None
    systemAllowUploadDocs: Optional[str] = None
    completeAllForms: Optional[str] = None
    systemCompleteAllForms: Optional[str] = None
    enableBEAfterFinalSubmit: Optional[str] = None
    systemEnableBEAfterFinalSubmit: Optional[str] = None
    # Live-only field; type verified from the saved response.
    onboardVersion: Optional[str] = None
    # Live-only field; type verified from the saved response.
    decisionSupport: Optional[str] = None


class PrismHRClientMaster(BaseModel):
    """Source schema: ClientMaster."""
    model_config = ConfigDict(extra="allow")

    id: str
    clientName: Optional[str] = None
    costCenter: Optional[str] = None
    subCostCenter: Optional[str] = None
    serviceType: Optional[str] = None
    categoryCode: Optional[str] = None
    stateCode: Optional[str] = None
    zipCode: Optional[str] = None
    legalName: Optional[str] = None
    arClientNumber: Optional[str] = None
    divisionRequired: Optional[bool] = None
    departmentRequired: Optional[bool] = None
    shiftRequired: Optional[bool] = None
    empNumbersUsed: Optional[bool] = None
    autoEmpNumber: Optional[bool] = None
    worksitePayrollApproval: Optional[str] = None
    projectRequired: Optional[bool] = None
    workGroupRequired: Optional[bool] = None
    payrollDate: Optional[str] = None
    statusDate: Optional[str] = None
    status: Optional[str] = None
    deliverChecks: Optional[str] = None
    employerId: Optional[str] = None
    minCheckAmt: Optional[str] = None
    maxCheckAmt: Optional[str] = None
    deliveryMethod: Optional[str] = None
    mainPhoneExt: Optional[str] = None
    addressLine1: Optional[str] = None
    addressLine2: Optional[str] = None
    city: Optional[str] = None
    zipSuffix: Optional[str] = None
    mainPhone: Optional[str] = None
    fax: Optional[str] = None
    websiteUrl: Optional[str] = None
    emailAddress: Optional[str] = None
    businessDescription: Optional[str] = None
    sicCode: Optional[str] = None
    federalIdNumber: Optional[str] = None
    billFormat: Optional[str] = None
    groupCode: Optional[str] = None
    tpaDownloadOptions: Optional[str] = None
    hoursType1: Optional[str] = None
    hoursType2: Optional[str] = None
    hoursType3: Optional[str] = None
    hoursType4: Optional[str] = None
    hoursType5: Optional[str] = None
    hoursType6: Optional[str] = None
    hoursType9: Optional[str] = None
    flatType1: Optional[str] = None
    flatType2: Optional[str] = None
    extraHeading1: Optional[str] = None
    extraHeading2: Optional[str] = None
    corporationType: Optional[str] = None
    controlGroupCompany: Optional[str] = None
    cafeteriaPlan: Optional[str] = None
    hsaPlanId: Optional[str] = None
    glClientNo: Optional[str] = None
    billTemplate: Optional[str] = None
    wcPolicy: Optional[str] = None
    wcPolicyEffDate: Optional[str] = None
    wcLocationBased: Optional[bool] = None
    flsaRuleset: Optional[str] = None
    flsaWeekEnds: Optional[str] = None
    satPayOnDay: Optional[str] = None
    sunPayOnDay: Optional[str] = None
    satPayBefAft: Optional[str] = None
    sunPayBefAft: Optional[str] = None
    contractDate: Optional[str] = None
    benefitParentClient: Optional[str] = None
    payCode: Optional[List[PrismHRClientMasterPayCode]] = None
    deductionCode: Optional[List[PrismHRClientMasterDeductionCode]] = None
    arrear: Optional[List[PrismHRArrear]] = None
    employeeType: Optional[List[PrismHREmployeeType]] = None
    employeeStatus: Optional[List[PrismHREmployeeStatus]] = None
    reason: Optional[List[PrismHRReason]] = None
    miscGL: Optional[List[PrismHRClientMasterMiscGL]] = None
    observedHoliday: Optional[List[PrismHRObservedHoliday]] = None
    abbrvName: Optional[str] = None
    annualHours: Optional[str] = None
    sortField1: Optional[str] = None
    sortField2: Optional[str] = None
    sortField3: Optional[str] = None
    billBySort: Optional[str] = None
    billInvBreakField: Optional[str] = None
    consultant: Optional[str] = None
    salesperson: Optional[str] = None
    payrollRep: Optional[str] = None
    checkIssueAcct: Optional[str] = None
    checkPrintStyle: Optional[str] = None
    invoiceCopies: Optional[str] = None
    remitCopies: Optional[str] = None
    receiptCheckAcct: Optional[str] = None
    adjAchDays: Optional[str] = None
    serviceTermReason: Optional[str] = None
    garnCheckIssueAcct: Optional[str] = None
    directDepositAccount: Optional[str] = None
    manualAccount: Optional[str] = None
    onDemandChecksAccount: Optional[str] = None
    payCardAccount: Optional[str] = None
    nesOffset: Optional[str] = None
    rateOrMarkup: Optional[str] = None
    billAddressLine1: Optional[str] = None
    billAddressLine2: Optional[str] = None
    billZipCode: Optional[str] = None
    billCity: Optional[str] = None
    billStateCode: Optional[str] = None
    billZipSuffix: Optional[str] = None
    billAddrClientId: Optional[str] = None
    newHireAlert: Optional[str] = None
    clientAccountingCode: Optional[str] = None
    garnEftIssueAcct: Optional[str] = None
    definitionId: Optional[str] = None
    cutbackCheckAcct: Optional[str] = None
    broker: Optional[str] = None
    onboardStatus: Optional[str] = None
    nyMctOvrRate: Optional[str] = None
    naicsCode: Optional[str] = None
    benefitRep: Optional[str] = None
    riskManager: Optional[str] = None
    depositType: Optional[str] = None
    depositAmt: Optional[str] = None
    handbookId: Optional[str] = None
    aftPostPreMailThreshold: Optional[str] = None
    achHoldThreshold: Optional[str] = None
    taxCalcOptions: Optional[str] = None
    taxLimitBasis: Optional[str] = None
    glTemplateCode: Optional[str] = None
    nySdiEmployerRate: Optional[str] = None
    wcPolicySubId: Optional[str] = None
    deduct401kOnSupp: Optional[str] = None
    coordinator: Optional[str] = None
    recomputeOvertime: Optional[bool] = None
    jobRates: Optional[bool] = None
    remoteTechSupport: Optional[bool] = None
    processingSchedule: Optional[str] = None
    perDiemRateSource: Optional[bool] = None
    clientAccounting: Optional[bool] = None
    adjTipShortfall: Optional[bool] = None
    suppressAutoBenAdj: Optional[bool] = None
    suppressEmpAch: Optional[bool] = None
    singlePayGroup: Optional[bool] = None
    elecPayStub: Optional[str] = None
    useWcRateTemplate: Optional[bool] = None
    calcWcOn1099Emp: Optional[bool] = None
    wvUseFedMinRate: Optional[bool] = None
    elecW2Form: Optional[bool] = None
    nySdiEmployerCalc: Optional[bool] = None
    pfmlMa1099: Optional[bool] = None
    railRoadEmployer: Optional[bool] = None
    taxGeoCodeOverride: Optional[str] = None
    adjTipsToMin: Optional[bool] = None
    doNotService: Optional[bool] = None
    clientModDiscount: Optional[bool] = None
    aftPostPreMailHold: Optional[bool] = None
    clientHdhp: Optional[bool] = None
    financialInst: Optional[bool] = None
    newHireOnBoard: Optional[bool] = None
    newHireBenEnroll: Optional[bool] = None
    paperlessDelivery: Optional[str] = None
    # Contract-required, but optional under project policy; null observed in the saved response.
    clientAgrmtRecvDate: Optional[str] = None
    # Contract-required, but optional under project policy; null observed in the saved response.
    depositDate: Optional[str] = None
    invoiceNotes: Optional[List[str]] = None
    faxBackNotes: Optional[List[str]] = None
    featureCode: Optional[List[str]] = None
    achStatus: Optional[str] = None
    eligibleBenefitsDeterminant: Optional[str] = None
    wcResidentBased: Optional[bool] = None
    relatedCode: Optional[str] = None
    instantPayAccount: Optional[str] = None
    remoteVerification: Optional[str] = None
    statusClass: Optional[str] = None
    selfServicePayroll: Optional[str] = None
    selfServiceRestrictions: Optional[str] = None
    worksiteTimesheetEntry: Optional[str] = None
    allowFirstPeriodHours: Optional[str] = None
    enableInstantPay: Optional[bool] = None
    nextEmployeeNumber: Optional[str] = None
    altEmployer: Optional[List[PrismHRAltEmployer]] = None
    retire: Optional[List[PrismHRClientRetirementPlanObject]] = None
    billFixed: Optional[List[PrismHRBillFixed]] = None
    holidayPay: Optional[List[PrismHRHolidayPay]] = None
    sdiDedn: Optional[List[PrismHRSdiDedn]] = None
    clientTax: Optional[List[PrismHRClientMasterClientTax]] = None
    redir: Optional[List[PrismHRRedir]] = None
    regRebuild: Optional[List[PrismHRRegRebuild]] = None
    commission: Optional[List[PrismHRCommission]] = None
    billEvent: Optional[List[PrismHRBillEvent]] = None
    reportFee: Optional[List[PrismHRReportFee]] = None
    i9Approver: Optional[str] = None
    printMailUser: Optional[str] = None
    contractorsAllowed1099: Optional[bool] = None
    billPendingLocation: Optional[str] = None
    benefitsGoodThroughDate: Optional[str] = None
    achMax: Optional[str] = None
    checksum: Optional[str] = None
    clientStatusChecksum: Optional[str] = None
    # Contract-required, but optional under project policy; null observed in the saved response.
    mySupportTeamDashboard: Optional[List[PrismHRMySupportTeamDashboard]] = None
    enrollOnboardControls: Optional[PrismHREnrollOnboardControls] = None
    everify: Optional[bool] = None
    # Live-only field; type verified from the saved response.
    reverseWireAccount: Optional[str] = None
    # Live-only field; type verified from the saved response.
    payrollFinalizationNotification: Optional[str] = None
    # Live-only field; type verified from the saved response.
    notificationEmailList: Optional[List[Any]] = None
    # Live-only field; type verified from the saved response.
    positionRatesUsed: Optional[str] = None
    # Live-only field; type verified from the saved response.
    eVerify: Optional[bool] = None
    # Live-only field; type verified from the saved response.
    externalPtoUsed: Optional[bool] = None
    # Live-only field; type verified from the saved response.
    taxesToSuppress: Optional[List[Any]] = None


class PrismHRGetClientMasterResponse(BaseModel):
    """Source schema: GetClientMasterResponse."""
    model_config = ConfigDict(extra="allow")

    errorCode: str
    errorMessage: str
    extension: Optional[PrismHRExtension] = None
    clientMaster: Optional[PrismHRClientMaster] = None
