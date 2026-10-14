"""PrismHR employee source models from API 2025.09 and saved Postman responses.

These validate source field types and required presence. Dates and numeric
strings retain their documented source types; business rules are added later.
Optional fields accept missing/null values. Live naming differences are
handled explicitly; unknown fields are preserved rather than discarded.

TODO: add rules that are not just structural - eg, -ve values, age limit, -ve distance


Project validation policy: record IDs and documented required wrapper fields
require presence. Other fields accept missing/null; existing ID nullability
is retained. Reference IDs are optional unless they identify this record.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

class PrismHREmployeeResponse(BaseModel):
    """Source schema: EmployeeAndEmployeeBySsnResponse."""
    model_config = ConfigDict(extra="allow")

    errorCode: str
    errorMessage: str
    extension: Optional[PrismHRExtension] = None
    # Individual employee validation happens after wrapper checks.
    employee: Optional[List[Any]] = None
    infoMessage: Optional[List[str]] = None
    updateMessage: Optional[str] = None



class PrismHREmployee(BaseModel):
    """Source schema: Employee."""
    model_config = ConfigDict(extra="allow")

    id: str
    lastName: Optional[str] = None
    firstName: Optional[str] = None
    middleInitial: Optional[str] = None
    preferredName: Optional[str] = None
    person: Optional[PrismHRPerson] = None
    contactInformation: Optional[PrismHRContactInformation] = None
    client: Optional[PrismHRClient] = None
    compensation: Optional[PrismHRCompensation] = None
    directDeposit: Optional[PrismHRDirectDeposit] = None
    hsa: Optional[PrismHRHsa] = None
    employeeEvents: Optional[PrismHREmployeeEvents] = None
    health: Optional[PrismHRHealth] = None
    skillsAndEducation: Optional[PrismHRSkillsAndEducation] = None
    absenceJournalId: Optional[List[str]] = None
    benefitEnrollmentCompleted: Optional[bool] = None
    scheduledDeduction: Optional[List[PrismHRScheduledDeduction]] = None
    newHireQuestions: Optional[List[PrismHRNewHireQuestion]] = None
    enrollmentInProgress: Optional[PrismHREnrollmentInProgress] = None


class PrismHRPerson(BaseModel):
    """Source schema: Person."""
    model_config = ConfigDict(extra="allow")

    ethnicCode: Optional[str] = None
    birthDate: Optional[str] = None
    driverLicenseId: Optional[str] = None
    cobraSSN: Optional[str] = None
    # Accept both the contract name and the live response name.
    employerIds: Optional[List[str]] = Field(
        default=None, validation_alias=AliasChoices("employerIds", "employerId")
    )
    cobraOnly: Optional[bool] = None
    geoCode: Optional[str] = None
    maritalStatus: Optional[str] = None
    marriedDate: Optional[str] = None
    smoker: Optional[str] = None
    peoStartDate: Optional[str] = None
    handicapped: Optional[str] = None
    blind: Optional[str] = None
    veteran: Optional[str] = None
    vietnamVet: Optional[str] = None
    disabledVet: Optional[str] = None
    # Contract-required, but optional under project policy; null observed in the saved employee response.
    hrpCitizenshipCountry: Optional[str] = None
    deceased: Optional[bool] = None
    gender: Optional[str] = None
    taxZipCode: Optional[str] = None
    highlyCompensated: Optional[bool] = None
    keyEmployee: Optional[bool] = None
    overrideGeoCode: Optional[str] = None
    overrideGeoEndDate: Optional[str] = None
    nickname: Optional[str] = None
    deceasedDate: Optional[str] = None
    driverState: Optional[str] = None
    driverLicenseExpireDate: Optional[str] = None
    driverLicenseClass: Optional[str] = None
    ohioFormC112: Optional[bool] = None
    unincorporatedResidence: Optional[bool] = None
    w2AddressLine1: Optional[str] = None
    w2AddressLine2: Optional[str] = None
    w2City: Optional[str] = None
    w2State: Optional[str] = None
    w2PostalCode: Optional[str] = None
    w2ElecForm: Optional[bool] = None
    w2ElecFormDate: Optional[str] = None
    legacyEmployeeId: Optional[str] = None
    hispanic: Optional[bool] = None
    agricultureWorker: Optional[bool] = None
    otherProtectedVet: Optional[str] = None
    activeDutyBadgeVet: Optional[str] = None
    recentlySeparatedVet: Optional[str] = None
    serviceMedalVet: Optional[str] = None
    preferredLanguage: Optional[str] = None
    emergencyContact: Optional[List[PrismHREmergencyContact]] = None
    userId: Optional[str] = None
    # Accept both the contract name and the live response name.
    autoPolicies: Optional[List[PrismHRAutoPolicy]] = Field(
        default=None, validation_alias=AliasChoices("autoPolicies", "autoPolicy")
    )
    vehicleDetails: Optional[List[PrismHRVehicleDetails]] = None
    personChecksum: Optional[str] = None


class PrismHREmergencyContact(BaseModel):
    """Source schema: EmergencyContact."""
    model_config = ConfigDict(extra="allow")

    contactName: Optional[str] = None
    contactInfo: Optional[str] = None
    contactRelationship: Optional[str] = None
    contactType: Optional[str] = None


class PrismHRAutoPolicy(BaseModel):
    """Source schema: AutoPolicy."""
    model_config = ConfigDict(extra="allow")

    autoInsurancePolicyId: Optional[str]
    autoInsuranceCarrierName: Optional[str] = None
    autoInsuranceHolderName: Optional[str] = None
    autoInsurancePolicyStartDate: Optional[str] = None
    autoInsurancePolicyExpDate: Optional[str] = None


class PrismHRVehicleDetails(BaseModel):
    """Source schema: VehicleDetails."""
    model_config = ConfigDict(extra="allow")

    vehicleMake: Optional[str] = None
    vehicleModel: Optional[str] = None
    vehicleYear: Optional[str] = None
    vehicleAddDate: Optional[str] = None
    vehicleRemoveDate: Optional[str] = None
    vehicleRegNo: Optional[str] = None


class PrismHRContactInformation(BaseModel):
    """Source schema: ContactInformation."""
    model_config = ConfigDict(extra="allow")

    addressLine1: Optional[str] = None
    addressLine2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None
    zipSuffix: Optional[str] = None
    county: Optional[str] = None
    schoolDistrict: Optional[str] = None
    homePhone: Optional[str] = None
    mobilePhone: Optional[str] = None
    emailAddress: Optional[str] = None


class PrismHRClient(BaseModel):
    """Source schema: Client."""
    model_config = ConfigDict(extra="allow")

    employeeStatus: Optional[str] = None
    statusClass: Optional[str] = None
    statusDate: Optional[str] = None
    employeeType: Optional[str] = None
    typeClass: Optional[str] = None
    typeDate: Optional[str] = None
    transferInfo: Optional[List[PrismHRTransferInfo]] = None
    property: Optional[List[PrismHRProperty]] = None
    # Accept both the contract name and the live response name.
    hawaiiMedWaivers: Optional[List[PrismHRHawaiiMedWaiver]] = Field(
        default=None, validation_alias=AliasChoices("hawaiiMedWaivers", "hawaiiMedWaiver")
    )
    jobCode: Optional[str] = None
    jobStartDate: Optional[str] = None
    firstHireDate: Optional[str] = None
    lastHireDate: Optional[str] = None
    flsaExempt: Optional[bool] = None
    cafeteriaPlan: Optional[List[PrismHRCafeteriaPlan]] = None
    seniorityDate: Optional[str] = None
    officer: Optional[bool] = None
    workCompOfficer: Optional[bool] = None
    scorpOwner: Optional[bool] = None
    businessOwner: Optional[bool] = None
    termReasonCode: Optional[str] = None
    termExplanation: Optional[str] = None
    lastStatusChangeDate: Optional[str] = None
    lastJobChangeDate: Optional[str] = None
    newHireReportDate: Optional[str] = None
    employee1099: Optional[bool] = None
    clientEmployeeId: Optional[str] = None
    clockNum: Optional[str] = None
    primaryEmailSource: Optional[str] = None
    benefitEmail: Optional[str] = None
    rehireOk: Optional[str] = None
    returnDate: Optional[str] = None
    workPhone: Optional[str] = None
    workPhoneExt: Optional[str] = None
    probationDate: Optional[str] = None
    courtOrderMedical: Optional[bool] = None
    childSpouseSupport: Optional[bool] = None
    childSpouseArrears: Optional[bool] = None
    addressLine1: Optional[str] = None
    addressLine2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    zipSuffix: Optional[str] = None
    handbookMailDate: Optional[str] = None
    handbookRecvDate: Optional[str] = None
    unionCode: Optional[str] = None
    unionDate: Optional[str] = None
    subCostCenter: Optional[str] = None
    electronicOnboard: Optional[bool] = None
    electronicOnboardDate: Optional[str] = None
    reportsTo: Optional[str] = None
    onboardInProgress: Optional[bool] = None
    backgroundTest: Optional[bool] = None
    backgroundTestDate: Optional[str] = None
    workersCompExempt: Optional[bool] = None
    genderDesignation: Optional[str] = None
    preferredPronoun: Optional[str] = None
    clientChecksum: Optional[str] = None
    homeLocation: Optional[str] = None
    homeDivision: Optional[str] = None
    homeDepartment: Optional[str] = None
    workShift: Optional[str] = None
    projCostCenter: Optional[str] = None
    workGroupCode: Optional[str] = None
    benefitGroup: Optional[str] = None
    retirementBenefitGroup: Optional[str] = None
    workEmail: Optional[str] = None
    electronic1095C: Optional[str] = None
    manager: Optional[str] = None
    selfIdDisabilityForm: Optional[str] = None
    applicantId: Optional[str] = None


class PrismHRTransferInfo(BaseModel):
    """Source schema: TransferInfo."""
    model_config = ConfigDict(extra="allow")

    transferStatus: Optional[str] = None
    transferEmployeeId: Optional[str] = None
    transferClientId: Optional[str] = None
    transferDate: Optional[str] = None


class PrismHRProperty(BaseModel):
    """Source schema: Property."""
    model_config = ConfigDict(extra="allow")

    propertyCode: Optional[str] = None
    propertyIssueDate: Optional[str] = None
    propertySerialNumber: Optional[str] = None
    propertyValue: Optional[str] = None
    propertyReturnDate: Optional[str] = None
    propertyComment: Optional[str] = None


class PrismHRHawaiiMedWaiver(BaseModel):
    """Source schema: HawaiiMedWaiver."""
    model_config = ConfigDict(extra="allow")

    medWaiverYear: Optional[str] = None
    medWaiverReason: Optional[str] = None


class PrismHRCafeteriaPlan(BaseModel):
    """Source schema: CafeteriaPlan."""
    model_config = ConfigDict(extra="allow")

    planAmt: Optional[str] = None
    planEffectiveDate: Optional[str] = None


class PrismHRCompensation(BaseModel):
    """Source schema: Compensation."""
    model_config = ConfigDict(extra="allow")

    ssn: Optional[str] = None
    payGroup: Optional[str] = None
    payPeriod: Optional[str] = None
    payPeriodInfo: Optional[List[PrismHRPayPeriodInfo]] = None
    defaultHours: Optional[str] = None
    payMethod: Optional[str] = None
    allocationTemplateId: Optional[str] = None
    payAllocation: Optional[List[PrismHRPayAllocation]] = None
    standardHours: Optional[str] = None
    stateTax: Optional[List[PrismHRStateTax]] = None
    hourlyPay: Optional[str] = None
    salary: Optional[str] = None
    workShift: Optional[str] = None
    paidThruDate: Optional[str] = None
    eicFileStatus: Optional[str] = None
    fedFilingStatus: Optional[str] = None
    fedWithholdAllowance: Optional[str] = None
    fedOverrideType: Optional[str] = None
    fedOverrideAmt: Optional[str] = None
    fedTaxCalc: Optional[str] = None
    fedMultipleJobs: Optional[bool] = None
    fedDependents: Optional[float] = None
    fedOtherIncome: Optional[float] = None
    fedDeductions: Optional[float] = None
    hourlyPayRate: Optional[str] = None
    hourlyPayPeriod: Optional[str] = None
    deliverCheckHome: Optional[bool] = None
    autoAcceptTimeSheet: Optional[bool] = None
    longPayTable: Optional[str] = None
    longBasisDate: Optional[str] = None
    annualPay: Optional[str] = None
    effectiveDate: Optional[str] = None
    localTax: Optional[List[PrismHRLocalTax]] = None
    lastChangePct: Optional[str] = None
    lastChangeAmt: Optional[str] = None
    lastPayDate: Optional[str] = None
    quartile: Optional[str] = None
    compaRatio: Optional[str] = None
    benefitsBasePay: Optional[str] = None
    perDiemPay: Optional[str] = None
    taxCreditEmp: Optional[bool] = None
    autoPayCode: Optional[str] = None
    altPayRate: Optional[List[str]] = None
    pensionStatus: Optional[str] = None
    profitSharing: Optional[str] = None
    eeImage: Optional[List[PrismHREeImage]] = None
    wagePlanCA: Optional[bool] = None
    perfReviewLastDate: Optional[str] = None
    perfReviewNextDate: Optional[str] = None
    i9imageAudit: Optional[List[PrismHRI9ImageAudit]] = None
    perfReviewLastRating: Optional[str] = None
    compReviewNextDate: Optional[str] = None
    perfReviewLastTitle: Optional[str] = None
    fedW5Year: Optional[str] = None
    fedW5Filed: Optional[bool] = None
    fedW4Filed: Optional[bool] = None
    fedW4Year: Optional[str] = None
    lockIns: Optional[List[PrismHRLockIns]] = None
    formI9Filed: Optional[bool] = None
    formI9RenewDate: Optional[str] = None
    notes: Optional[str] = None
    ficaExempt: Optional[bool] = None
    benefitsPerHour: Optional[str] = None
    perfAgreement: Optional[bool] = None
    payRate2: Optional[str] = None
    payRate3: Optional[str] = None
    payRate4: Optional[str] = None
    payChangeLastDate: Optional[str] = None
    overrideWorkGeocode: Optional[str] = None
    familyMemberMI: Optional[str] = None
    probationCodeMO: Optional[str] = None
    electronicPayStub: Optional[bool] = None
    healthInsVT: Optional[bool] = None
    lastWorkedDate: Optional[str] = None
    irsLockInDate: Optional[str] = None
    nonResAlien: Optional[bool] = None
    alienRegExpDate: Optional[str] = None
    benefitSalary: Optional[str] = None
    citizenshipStatus: Optional[str] = None
    firstPayPeriodHours: Optional[str] = None
    compensationChecksum: Optional[str] = None
    providerNotifiedOn: Optional[str] = None
    alternateId: Optional[str] = None
    w8Filed: Optional[bool] = None
    # Live-only field: a string in the saved Postman employee response.
    payPeriodsPerWeek: Optional[str] = None


class PrismHRPayPeriodInfo(BaseModel):
    """Source schema: PayPeriodInfo."""
    model_config = ConfigDict(extra="allow")

    periodCode: Optional[str] = None
    periodBase: Optional[str] = None


class PrismHRPayAllocation(BaseModel):
    """Source schema: PayAllocation."""
    model_config = ConfigDict(extra="allow")

    locationCode: Optional[str] = None
    percent: Optional[str] = None
    job: Optional[str] = None
    deptCode: Optional[str] = None
    project: Optional[str] = None
    division: Optional[str] = None


class PrismHRStateTax(BaseModel):
    """Source schema: StateTax."""
    model_config = ConfigDict(extra="allow")

    stateCode: Optional[str] = None
    nonResCertFiled: Optional[str] = None
    filingStatus: Optional[str] = None
    primaryAllowance: Optional[str] = None
    secondaryAllowance: Optional[str] = None
    exemptAmount: Optional[str] = None
    supplExemptAmount: Optional[str] = None
    overrideType: Optional[str] = None
    overrideAmount: Optional[str] = None
    reduceAddlWithholding: Optional[str] = None
    fixedWithholding: Optional[str] = None
    alternateCalc: Optional[str] = None
    stateW4Filed: Optional[str] = None
    stateW4Year: Optional[str] = None
    multipleJobs: Optional[bool] = None
    dependents: Optional[float] = None
    otherIncome: Optional[float] = None
    deductions: Optional[float] = None
    nonResCertYear: Optional[str] = None


class PrismHRLocalTax(BaseModel):
    """Source schema: LocalTax."""
    model_config = ConfigDict(extra="allow")

    authId: Optional[str] = None
    filingStatus: Optional[str] = None
    primaryAllowance: Optional[str] = None
    nonResCert: Optional[str] = None
    addlWithheld: Optional[str] = None


class PrismHREeImage(BaseModel):
    """Source schema: EeImage."""
    model_config = ConfigDict(extra="allow")

    masterId: Optional[str] = None
    verifyDateTime: Optional[str] = None
    verifyUserId: Optional[str] = None


class PrismHRI9ImageAudit(BaseModel):
    """Source schema: I9ImageAudit."""
    model_config = ConfigDict(extra="allow")

    auditDate: Optional[str] = None
    auditUser: Optional[str] = None
    auditId: str
    auditStep: Optional[str] = None


class PrismHRLockIns(BaseModel):
    """Source schema: LockIns."""
    model_config = ConfigDict(extra="allow")

    state: Optional[str] = None
    stateDate: Optional[str] = None
    authUser: Optional[str] = None


class PrismHRDirectDeposit(BaseModel):
    """Source schema: EmployeeDirectDeposit."""
    model_config = ConfigDict(extra="allow")

    achStatus: Optional[str] = None
    voucherType: Optional[str] = None
    suppressAccountPrint: Optional[bool] = None
    achVoucher: Optional[List[PrismHRAchVoucher]] = None
    directDepositChecksum: Optional[str] = None


class PrismHRAchVoucher(BaseModel):
    """Source schema: AchVoucher."""
    model_config = ConfigDict(extra="allow")

    transitNum: Optional[str] = None
    accountNum: Optional[str] = None
    accountType: Optional[str] = None
    method: Optional[str] = None
    amount: Optional[float] = None
    limit: Optional[float] = None
    status: Optional[str] = None
    bankName: Optional[str] = None
    voucherTypeOverride: Optional[str] = None


class PrismHRHsa(BaseModel):
    """Source schema: Hsa."""
    model_config = ConfigDict(extra="allow")

    hsaDepositSettings: Optional[List[PrismHRHsaDepositSettings]] = None
    achChecksum: Optional[str] = None


class PrismHRHsaDepositSettings(BaseModel):
    """Source schema: EmployeeDirectDeposit-HsaDepositSettings."""
    model_config = ConfigDict(extra="allow")

    transitNum: Optional[str] = None
    accountNum: Optional[str] = None
    accountType: Optional[str] = None
    method: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    bankName: Optional[str] = None
    voucherTypeOverride: Optional[str] = None


class PrismHREmployeeEvents(BaseModel):
    """Source schema: EmployeeEvents."""
    model_config = ConfigDict(extra="allow")

    employeeEvent: Optional[List[PrismHREmployeeEvent]] = None


class PrismHREmployeeEvent(BaseModel):
    """Source schema: EmployeeEvent."""
    model_config = ConfigDict(extra="allow")

    eventCode: Optional[str] = None
    effectiveDate: Optional[str] = None
    description: Optional[str] = None
    actionDate: Optional[str] = None
    comment: Optional[str] = None


class PrismHRHealth(BaseModel):
    """Source schema: Health."""
    model_config = ConfigDict(extra="allow")

    allergy: Optional[List[str]] = None
    condition: Optional[List[str]] = None
    program: Optional[List[str]] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    bloodType: Optional[str] = None
    bloodRh: Optional[str] = None
    bloodDonor: Optional[bool] = None
    donateDateLast: Optional[str] = None
    donateDateNext: Optional[str] = None
    drugTestResult: Optional[str] = None
    drugTestDateLast: Optional[str] = None
    drugTestDateNext: Optional[str] = None
    audioTestResult: Optional[str] = None
    audioTestDateLast: Optional[str] = None
    audioTestDateNext: Optional[str] = None
    physExamResult: Optional[str] = None
    physExamDateLast: Optional[str] = None
    physExamDateNext: Optional[str] = None


class PrismHRSkillsAndEducation(BaseModel):
    """Source schema: SkillsAndEducationAndCertification."""
    model_config = ConfigDict(extra="allow")

    skillChecksum: Optional[str] = None
    skill: Optional[List[PrismHRSkill]] = None
    school: Optional[List[PrismHRSchool]] = None
    osha10Certified: Optional[bool] = None


class PrismHRSkill(BaseModel):
    """Source schema: Skill."""
    model_config = ConfigDict(extra="allow")

    skillCode: Optional[str] = None
    competencyLevel: Optional[str] = None
    certifyDate: Optional[str] = None
    skillComment: Optional[str] = None
    renewDate: Optional[str] = None


class PrismHRSchool(BaseModel):
    """Source schema: School."""
    model_config = ConfigDict(extra="allow")

    schoolName: Optional[str] = None
    schoolYear: Optional[str] = None
    graduated: Optional[bool] = None
    gradYear: Optional[str] = None
    degreeEarned: Optional[str] = None
    schoolComment: Optional[str] = None


class PrismHRScheduledDeduction(BaseModel):
    """Source schema: ScheduledDeduction."""
    model_config = ConfigDict(extra="allow")

    deductionCode: Optional[str] = None
    checkStubDescription: Optional[str] = None
    status: Optional[str] = None
    amount: Optional[float] = None
    startDate: Optional[str] = None
    stopDate: Optional[str] = None
    cutbackPayeeCode: Optional[str] = None


class PrismHRNewHireQuestion(BaseModel):
    """Source schema: Employee-NewHireQuestions."""
    model_config = ConfigDict(extra="allow")

    code: Optional[str] = None
    description: Optional[str] = None
    answer: Optional[str] = None


class PrismHREnrollmentInProgress(BaseModel):
    """Source schema: EnrollmentInProgress."""
    model_config = ConfigDict(extra="allow")

    enrollmentInProgress: Optional[bool] = None
    enrollmentType: Optional[str] = None


class PrismHRExtension(BaseModel):
    """Source schema: Extension."""
    model_config = ConfigDict(extra="allow")

    any: Optional[Dict[str, Any]] = None
