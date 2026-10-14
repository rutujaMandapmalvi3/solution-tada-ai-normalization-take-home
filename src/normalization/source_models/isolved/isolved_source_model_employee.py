"""isolved employee source models from primary Swagger v6.

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


class IsolvedPagedModelItemListOfEmployeeModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.PagedModelItemListOfEmployeeModel."""
    model_config = ConfigDict(extra="allow")

    nextPageUrl: Optional[str] = None
    previousPageUrl: Optional[str] = None
    results: Optional[List[IsolvedEmployeeInput]] = None
    totalItems: Optional[int] = None
    totalPages: Optional[float] = None



class IsolvedEmployeeModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeeModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    acaEmploymentStatus: Optional[str] = None
    activeDutySeparationDate: Optional[str] = None
    adjustedServiceDate: Optional[str] = None
    annualSalary: Optional[float] = None
    assignedManager: Optional[IsolvedReferencedEmployeeModel] = None
    assignedSupervisor: Optional[IsolvedReferencedEmployeeModel] = None
    attachments: Optional[List[IsolvedEmployeeDocumentModel]] = None
    birthDate: Optional[str] = None
    citizenship: Optional[str] = None
    directDeposits: Optional[List[IsolvedEmployeeDirectDepositModel]] = None
    disabilityDescription: Optional[str] = None
    disabilityNotes: Optional[str] = None
    disabled: Optional[bool] = None
    disabledEffectiveDate: Optional[str] = None
    disabledRequiresAccomodation: Optional[bool] = None
    eeoGenderOverride: Optional[str] = None
    eligibleForRehire: Optional[bool] = None
    emailAddress: Optional[str] = None
    employeeNumber: Optional[str] = None
    employmentCategoryCode: Optional[str] = None
    employmentCategoryEffectiveDate: Optional[str] = None
    employmentCategoryFullTimeEquivalent: Optional[float] = None
    employmentStatus: Optional[str] = None
    enableSelfService: Optional[bool] = None
    ethnicOrigin: Optional[str] = None
    gender: Optional[str] = None
    hireDate: Optional[str] = None
    hourlyRate: Optional[float] = None
    i9Documents: Optional[IsolvedEmployeeI9DocumentContainerModel] = None
    # Required in Swagger but absent in saved full-record/list responses.
    idType: Optional[str] = None
    isManager: Optional[bool] = None
    isPending: Optional[bool] = None
    isRecentlySeparatedVeteran: Optional[bool] = None
    isRemoteWorker: Optional[bool] = None
    isSupervisor: Optional[bool] = None
    jobCode: Optional[str] = None
    jobEeoCategory: Optional[str] = None
    jobEffectiveDate: Optional[str] = None
    jobFLSAExempt: Optional[bool] = None
    jobGroup: Optional[str] = None
    jobId: Optional[int] = None
    jobIsSeasonal: Optional[bool] = None
    jobIsUnion: Optional[bool] = None
    jobTitle: Optional[str] = None
    labors: Optional[List[IsolvedEmployeeLaborModel]] = None
    legalCode: Optional[str] = None
    maritalStatus: Optional[str] = None
    messages: Optional[List[IsolvedOptionValueModelOfInt32]] = None
    militaryStatus: Optional[str] = None
    miscDataSets: Optional[List[IsolvedEmployeeMiscDataSetModel]] = None
    miscFields: Optional[List[IsolvedEmployeeMiscFieldModel]] = None
    nameAddress: Optional[IsolvedEmployeeNameAddressModel] = None
    normalHours: Optional[float] = None
    organizations: Optional[List[IsolvedEmployeeOrganizationModel]] = None
    originalHireDate: Optional[str] = None
    overrideAddress: Optional[IsolvedEmployeeW2OverrideAddressModel] = None
    payFrequency: Optional[int] = None
    payGroup: Optional[str] = None
    payRates: Optional[List[IsolvedEmployeePayRateModel]] = None
    payType: Optional[str] = None
    perPaySalary: Optional[float] = None
    personal: Optional[IsolvedEmployeePersonalModel] = None
    previousPunchLabors: Optional[List[IsolvedOptionValueModelOfNullable]] = None
    profilePicture: Optional[str] = None
    protectedVeteran: Optional[bool] = None
    reciprocityRule: Optional[str] = None
    rehireDate: Optional[str] = None
    salaryEffectiveDate: Optional[str] = None
    socCode: Optional[str] = None
    ssn: Optional[str] = None
    statusDate: Optional[str] = None
    taxes: Optional[IsolvedEmployeeTaxInfoModel] = None
    taxExemptStatus: Optional[str] = None
    team: Optional[IsolvedClientTeamModel] = None
    terminationDate: Optional[str] = None
    terminationReason: Optional[str] = None
    terminationType: Optional[str] = None
    timecardPunchStatusDate: Optional[str] = None
    timecardPunchStatusIsIn: Optional[bool] = None
    timeclockId: Optional[str] = None
    tobaccoUse: Optional[bool] = None
    tobaccoUseEffectiveDate: Optional[str] = None
    uniqueId: Optional[str] = None
    updatedDisabledEffectiveDate: Optional[str] = None
    updatedHireDate: Optional[str] = None
    updatedJobEffectiveDate: Optional[str] = None
    updatedSalaryEffectiveDate: Optional[str] = None
    updatedStatusDate: Optional[str] = None
    veteranStatusNotSpecified: Optional[bool] = None
    workersCompCode: Optional[str] = None
    workLocation: Optional[str] = None
    workLocationDashDescription: Optional[str] = None
    wotc: Optional[IsolvedEmployeeModel_WOTCCertificationModel] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedEmployeeInput(IsolvedEmployeeModel):
    """Project employee input; salary_history is our optional container."""

    salary_history: Optional[List[IsolvedEmployeeSalaryModel]] = None

    @classmethod
    def validate_response(cls, response: Any) -> List[Any]:
        """Validate combined records and existing provider response formats."""
        if isinstance(response, list):
            # Compatibility with the documented salary-history array response.
            return IsolvedEmployeeSalaryResponse.model_validate(response).root
        if isinstance(response, dict) and any(
            field in response
            for field in ("results", "nextPageUrl", "previousPageUrl", "totalItems", "totalPages")
        ):
            return IsolvedPagedModelItemListOfEmployeeModel.model_validate(response).results or []
        return [cls.model_validate(response)]



class IsolvedReferencedEmployeeModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ReferencedEmployeeModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    employeeName: Optional[str] = None
    employeeNumber: Optional[str] = None
    jobTitle: Optional[str] = None
    legalId: Optional[int] = None
    payrollEmploymentStatusCode: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None



class IsolvedBaseLinkModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.Base.LinkModel."""
    model_config = ConfigDict(extra="allow")

    href: Optional[str] = None
    method: Optional[str] = None
    rel: Optional[str] = None



class IsolvedEmployeeDocumentModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeeDocumentModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    allowEmployeeAccess: Optional[bool] = None
    allowManagerAccess: Optional[bool] = None
    allowSupervisorAccess: Optional[bool] = None
    clientMessageAttachmentId: Optional[int] = None
    documentCategory: Optional[str] = None
    documentContent: Optional[str] = None
    documentDescription: Optional[str] = None
    documentFileName: Optional[str] = None
    documentMimeType: Optional[str] = None
    documentType: Optional[str] = None
    documentTypeDescription: Optional[str] = None
    documentUploadDate: Optional[str] = None
    fileSubCategory: Optional[IsolvedFileSubCategoryModel] = None
    isSystemGenerated: Optional[bool] = None
    readonlyEmployeeAccess: Optional[bool] = None
    readonlyManagerAccess: Optional[bool] = None
    readonlySupervisorAccess: Optional[bool] = None
    requiresElectronicSignature: Optional[bool] = None
    signedAcknowledgementDocumentType: Optional[str] = None
    systemMessageAttachmentId: Optional[int] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None



class IsolvedFileSubCategoryModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.FileSubCategoryModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    fileCategory: Optional[IsolvedLookupDocumentCategoryModel] = None
    subcategoryDescription: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None



class IsolvedLookupDocumentCategoryModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.LookupDocumentCategoryModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    documentCategoryDescription: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None



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
    # Required in Swagger but null in saved direct-deposit responses.
    sequenceNumber: Optional[int] = None
    status: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None



class IsolvedEmployeeI9DocumentContainerModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeeI9DocumentContainerModel."""
    model_config = ConfigDict(extra="allow")

    documentA: Optional[IsolvedEmployeeI9DocumentModel] = None
    documentB: Optional[IsolvedEmployeeI9DocumentModel] = None
    documentC: Optional[IsolvedEmployeeI9DocumentModel] = None
    i9Completed: Optional[bool] = None
    i9CompletedDate: Optional[str] = None



class IsolvedEmployeeI9DocumentModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeeI9DocumentModel."""
    model_config = ConfigDict(extra="allow")

    allowEmployeeAccess: Optional[bool] = None
    allowManagerAccess: Optional[bool] = None
    allowSupervisorAccess: Optional[bool] = None
    documentCode: Optional[str] = None
    documentContent: Optional[str] = None
    documentDescription: Optional[str] = None
    documentFileName: Optional[str] = None
    documentNumber: Optional[str] = None
    expirationDate: Optional[str] = None
    issuingAuthority: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None



class IsolvedEmployeeLaborModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeeLaborModel."""
    model_config = ConfigDict(extra="allow")

    laborDescription: Optional[str] = None
    laborField: Optional[str] = None
    laborFieldId: Optional[int] = None
    laborValue: Optional[str] = None



class IsolvedOptionValueModelOfInt32(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.OptionValueModelOfInt32."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    description: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None



class IsolvedEmployeeMiscDataSetModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeeMiscDataSetModel."""
    model_config = ConfigDict(extra="allow")

    fields: Optional[List[IsolvedEmployeeMiscDataSetFieldModel]] = None
    id: Optional[int]
    isDeleted: Optional[bool] = None
    miscFieldCategory: Optional[IsolvedClientMiscFieldCategoryModel] = None



class IsolvedEmployeeMiscDataSetFieldModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeeMiscDataSetFieldModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[IsolvedClientMiscEmployeeFieldModel]
    miscValue: Optional[str] = None



class IsolvedClientMiscEmployeeFieldModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientMiscEmployeeFieldModel."""
    model_config = ConfigDict(extra="allow")

    category: Optional[str] = None
    dataType: Optional[str] = None
    fieldCode: Optional[str] = None
    fieldTitle: Optional[str] = None
    lookups: Optional[List[IsolvediSolvedDtoFrontEndOptionValueOfString]] = None



class IsolvediSolvedDtoFrontEndOptionValueOfString(BaseModel):
    """Source definition: iSolved.Dto.FrontEnd.OptionValueOfString."""
    model_config = ConfigDict(extra="allow")

    description: Optional[str] = None
    id: Optional[str]



class IsolvedClientMiscFieldCategoryModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientMiscFieldCategoryModel."""
    model_config = ConfigDict(extra="allow")

    categoryTitle: Optional[str] = None
    id: Optional[int]
    isDataSet: Optional[bool] = None



class IsolvedEmployeeMiscFieldModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeeMiscFieldModel."""
    model_config = ConfigDict(extra="allow")

    title: Optional[str] = None
    value: Optional[str] = None



class IsolvedEmployeeNameAddressModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeeNameAddressModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    middleName: Optional[str] = None
    overrideAddress: Optional[IsolvedEmployeeW2OverrideAddressModel] = None
    preferredName: Optional[str] = None
    preferredPronouns: Optional[str] = None
    prefix: Optional[str] = None
    residentGeoCode: Optional[str] = None
    schoolDistrictCode: Optional[int] = None
    state: Optional[str] = None
    suffix: Optional[str] = None
    zipCode: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None



class IsolvedEmployeeW2OverrideAddressModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeeW2OverrideAddressModel."""
    model_config = ConfigDict(extra="allow")

    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    deleteAddress: Optional[bool] = None
    foreignPostalCode: Optional[str] = None
    foreignStateProvince: Optional[str] = None
    militaryCity: Optional[str] = None
    militaryState: Optional[str] = None
    state: Optional[str] = None
    useForPaychecks: Optional[bool] = None
    useForTaxForms: Optional[bool] = None
    zipCode: Optional[str] = None



class IsolvedEmployeeOrganizationModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeeOrganizationModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    displayOrder: Optional[int] = None
    organizationId: Optional[int] = None
    title: Optional[str] = None
    value: Optional[str] = None
    valueDescription: Optional[str] = None



class IsolvedEmployeePayRateModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeePayRateModel."""
    model_config = ConfigDict(extra="allow")

    payRateName: Optional[str] = None
    rateValue: Optional[float] = None



class IsolvedEmployeePersonalModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeePersonalModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    faxNumber: Optional[str] = None
    homePhone: Optional[str] = None
    mobilePhone: Optional[str] = None
    officePhone: Optional[str] = None
    personalEmailAddress: Optional[str] = None
    preferredPronouns: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None



class IsolvedOptionValueModelOfNullable(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.OptionValueModelOfNullable."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    description: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None



class IsolvedEmployeeTaxInfoModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeeTaxInfoModel."""
    model_config = ConfigDict(extra="allow")

    federal: Optional[IsolvedEmployeeTaxCategoryModel] = None
    nonResidentCity: Optional[IsolvedEmployeeTaxCategoryModel] = None
    nonResidentState: Optional[IsolvedEmployeeTaxCategoryModel] = None
    residentCity: Optional[IsolvedEmployeeTaxCategoryModel] = None
    residentState: Optional[IsolvedEmployeeTaxCategoryModel] = None



class IsolvedEmployeeTaxCategoryModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeeTaxCategoryModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    additionalAmount: Optional[float] = None
    additionalIncomeAmount: Optional[float] = None
    additionalPercent: Optional[float] = None
    alternateCalculation: Optional[str] = None
    deductionExemptionAmount: Optional[float] = None
    dependantExemptionAmount: Optional[float] = None
    exemptionAmount: Optional[float] = None
    filingStatus: Optional[str] = None
    isBlocked: Optional[bool] = None
    multipleJobsOrSpouseWorks: Optional[bool] = None
    primaryExemptions: Optional[int] = None
    secondaryExemptions: Optional[int] = None
    taxCategoryId: Optional[str] = None
    taxDescription: Optional[str] = None
    taxState: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None



class IsolvedClientTeamModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientTeamModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    calendarRule: Optional[IsolvedClientCalendarRuleModel] = None
    organizationField: Optional[str] = None
    organizationValues: Optional[List[IsolvedClientOrganizationFieldLookupModel]] = None
    teamDescription: Optional[str] = None
    teamName: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None



class IsolvedClientCalendarRuleModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientCalendarRuleModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    restrictedAbsencePolicies: Optional[List[IsolvedClientAbsenceModel]] = None
    ruleDescription: Optional[str] = None
    ruleName: Optional[str] = None
    timeOffRestrictionDates: Optional[List[IsolvedClientCalendarRuleModel_RestrictionDateRange]] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None



class IsolvedClientAbsenceModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientAbsenceModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    absenceName: Optional[str] = None
    accrual: Optional[IsolvedClientAccrualModel] = None
    allowEmployeeAccess: Optional[bool] = None
    allowManagerAccess: Optional[bool] = None
    allowSupervisorAccess: Optional[bool] = None
    allowTimeOffRequest: Optional[bool] = None
    defaultHours: Optional[float] = None
    isEarningPayItem: Optional[bool] = None
    maximumHours: Optional[float] = None
    minimumHours: Optional[float] = None
    timeOffRequestBalanceLimit: Optional[float] = None
    timeOffRequestDurationLimitDays: Optional[int] = None
    validHourValues: Optional[List[float]] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None



class IsolvedClientAccrualModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientAccrualModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    accrualDescription: Optional[str] = None
    accrualName: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None



class IsolvedClientCalendarRuleModel_RestrictionDateRange(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientCalendarRuleModel_RestrictionDateRange."""
    model_config = ConfigDict(extra="allow")

    endDate: Optional[str] = None
    startDate: Optional[str] = None



class IsolvedClientOrganizationFieldLookupModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientOrganizationFieldLookupModel."""
    model_config = ConfigDict(extra="allow")

    code: Optional[str] = None
    description: Optional[str] = None
    isInactive: Optional[bool] = None



class IsolvedEmployeeModel_WOTCCertificationModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeeModel_WOTCCertificationModel."""
    model_config = ConfigDict(extra="allow")

    applicationDate: Optional[str] = None
    includeCertification: Optional[bool] = None
    jobAcceptedDate: Optional[str] = None
    jobOfferedDate: Optional[str] = None



class IsolvedEmployeeSalaryModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeeSalaryModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    changeReason: Optional[IsolvedOptionValueModelOfInt32] = None
    comments: Optional[str] = None
    effectiveDate: Optional[str] = None
    frequency: Optional[IsolvedOptionValueModelOfInt32] = None
    hourlyRate: Optional[float] = None
    isInactive: Optional[bool] = None
    lifeEvent: Optional[bool] = None
    normalHours: Optional[float] = None
    payGroup: Optional[IsolvedOptionValueModelOfInt32] = None
    payType: Optional[IsolvedOptionValueModelOfString] = None
    perPaySalary: Optional[float] = None
    seasons: Optional[List[IsolvedEmployeeSalarySeasonModel]] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None



class IsolvedOptionValueModelOfString(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.OptionValueModelOfString."""
    model_config = ConfigDict(extra="allow")

    id: Optional[str]
    description: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None



class IsolvedEmployeeSalarySeasonModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.EmployeeSalarySeasonModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    description: Optional[str] = None
    isSelected: Optional[bool] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None



class IsolvedEmployeeSalaryResponse(RootModel[List[IsolvedEmployeeSalaryModel]]):
    """The endpoint returns a top-level array, not an object envelope."""

