"""isolved company source models from primary Swagger v6.

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


class IsolvedBaseLinkModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.Base.LinkModel."""
    model_config = ConfigDict(extra="allow")

    href: Optional[str] = None
    method: Optional[str] = None
    rel: Optional[str] = None


class IsolvedClientPayRateModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientPayRateModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    payRateName: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedOptionValueModelOfString(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.OptionValueModelOfString."""
    model_config = ConfigDict(extra="allow")

    id: Optional[str]
    description: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedClientChangeReasonModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientChangeReasonModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    changeReasonType: Optional[IsolvedOptionValueModelOfString] = None
    code: Optional[str] = None
    description: Optional[str] = None


class IsolvedClientContactModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientContactModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    alternatePhoneNumber: Optional[str] = None
    emailAddress: Optional[str] = None
    faxNumber: Optional[str] = None
    firstName: Optional[str] = None
    inactiveDate: Optional[str] = None
    lastName: Optional[str] = None
    mobilePhoneNumber: Optional[str] = None
    phoneNumber: Optional[str] = None
    profilePicture: Optional[str] = None
    title: Optional[str] = None
    type: Optional[List[str]] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedClientEmploymentCategoryModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientEmploymentCategoryModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    acaEmploymentStatus: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    isInactive: Optional[bool] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedPayrollStatusModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.PayrollStatusModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[str]
    statusDescription: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedClientEmploymentStatusModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientEmploymentStatusModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    code: Optional[str] = None
    payrollStatus: Optional[IsolvedPayrollStatusModel] = None
    statusDescription: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedClientJobModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientJobModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    eeoCategory: Optional[str] = None
    isFLSAExempt: Optional[bool] = None
    isInactive: Optional[bool] = None
    isManagerJob: Optional[bool] = None
    isSeasonal: Optional[bool] = None
    isSupervisorJob: Optional[bool] = None
    isUnion: Optional[bool] = None
    jobCode: Optional[str] = None
    jobGroup: Optional[str] = None
    jobTitle: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedClientLaborFieldLookupModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientLaborFieldLookupModel."""
    model_config = ConfigDict(extra="allow")

    address1: Optional[str] = None
    address2: Optional[str] = None
    beginDate: Optional[str] = None
    city: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    endDate: Optional[str] = None
    isCertified: Optional[bool] = None
    isInactive: Optional[bool] = None
    projectLocation: Optional[str] = None
    projectNumber: Optional[str] = None
    state: Optional[str] = None
    zipCode: Optional[str] = None


class IsolvedClientLaborFieldModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientLaborFieldModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    allowInTimeEntry: Optional[bool] = None
    laborTitle: Optional[str] = None
    lookups: Optional[List[IsolvedClientLaborFieldLookupModel]] = None
    organizationFieldName: Optional[str] = None
    sequenceNumber: Optional[int] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvediSolvedDtoFrontEndOptionValueOfString(BaseModel):
    """Source definition: iSolved.Dto.FrontEnd.OptionValueOfString."""
    model_config = ConfigDict(extra="allow")

    description: Optional[str] = None
    id: Optional[str]


class IsolvedClientMiscEmployeeFieldModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientMiscEmployeeFieldModel."""
    model_config = ConfigDict(extra="allow")

    category: Optional[str] = None
    dataType: Optional[str] = None
    fieldCode: Optional[str] = None
    fieldTitle: Optional[str] = None
    lookups: Optional[List[IsolvediSolvedDtoFrontEndOptionValueOfString]] = None


class IsolvedClientOrganizationFieldLookupModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientOrganizationFieldLookupModel."""
    model_config = ConfigDict(extra="allow")

    code: Optional[str] = None
    description: Optional[str] = None
    isInactive: Optional[bool] = None


class IsolvedClientOrganizationFieldModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientOrganizationFieldModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    displayOrder: Optional[int] = None
    includeInJob: Optional[bool] = None
    isLaborField: Optional[bool] = None
    isRequired: Optional[bool] = None
    isTeam: Optional[bool] = None
    lookups: Optional[List[IsolvedClientOrganizationFieldLookupModel]] = None
    organizationGroupId: Optional[int] = None
    title: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedSecurityServiceGroupModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.SecurityServiceGroupModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    name: Optional[str] = None


class IsolvedClientModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    alternatePayRates: Optional[List[IsolvedClientPayRateModel]] = None
    changeReasons: Optional[List[IsolvedClientChangeReasonModel]] = None
    clientCode: Optional[str] = None
    clientName: Optional[str] = None
    contacts: Optional[List[IsolvedClientContactModel]] = None
    employmentCategories: Optional[List[IsolvedClientEmploymentCategoryModel]] = None
    employmentStatuses: Optional[List[IsolvedClientEmploymentStatusModel]] = None
    jobs: Optional[List[IsolvedClientJobModel]] = None
    labors: Optional[List[IsolvedClientLaborFieldModel]] = None
    legalCompanies: Optional[List[IsolvedLegalModel]] = None
    miscEmployeeFields: Optional[List[IsolvedClientMiscEmployeeFieldModel]] = None
    organizations: Optional[List[IsolvedClientOrganizationFieldModel]] = None
    securityServiceGroup: Optional[IsolvedSecurityServiceGroupModel] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedLegalCompensationPlanModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.LegalCompensationPlanModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    code: Optional[str] = None
    description: Optional[str] = None


class IsolvedClientAddressModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.ClientAddressModel."""
    model_config = ConfigDict(extra="allow")

    addressDescription: Optional[str] = None
    city: Optional[str] = None
    phoneNumber: Optional[str] = None
    state: Optional[str] = None
    streetAddress1: Optional[str] = None
    streetAddress2: Optional[str] = None
    zipCode: Optional[str] = None


class IsolvedSystemPrintCenterModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.SystemPrintCenterModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    allowTaxFilingPrint: Optional[bool] = None
    allowYearEndPrint: Optional[bool] = None
    isChanged: Optional[bool] = None
    isDeleted: Optional[bool] = None
    isLocalPrintCenter: Optional[bool] = None
    isNew: Optional[bool] = None
    printCenterDescription: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedPayGroupModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.PayGroupModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    enableiSolvedPayroll: Optional[bool] = None
    enableiSolvedTime: Optional[bool] = None
    inputMethod: Optional[str] = None
    isInactive: Optional[bool] = None
    legal: Optional[IsolvedLegalModel] = None
    normalHours: Optional[float] = None
    payFrequency: Optional[int] = None
    payGroupName: Optional[str] = None
    payrollType: Optional[str] = None
    printCenter: Optional[IsolvedSystemPrintCenterModel] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedLegalServiceModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.LegalServiceModel."""
    model_config = ConfigDict(extra="allow")

    code: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None


class IsolvedLegalWorkersCompModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.LegalWorkersCompModel."""
    model_config = ConfigDict(extra="allow")

    isInactive: Optional[bool] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None
    state: Optional[str] = None
    workersCompCode: Optional[str] = None
    workersCompDescription: Optional[str] = None
    workersCompId: Optional[int] = None


class IsolvedOptionValueModelOfInt32(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.OptionValueModelOfInt32."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    description: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedLegalWorkLocationModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.LegalWorkLocationModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    address1: Optional[str] = None
    address2: Optional[str] = None
    addressDescription: Optional[str] = None
    city: Optional[str] = None
    existingAddressId: Optional[int] = None
    geoCode: Optional[str] = None
    includeWorkSiteTaxFiling: Optional[bool] = None
    isInactive: Optional[bool] = None
    isRemoteWorkersOnly: Optional[bool] = None
    minimumWageRule: Optional[IsolvedOptionValueModelOfInt32] = None
    overrideTaxCode: Optional[str] = None
    reportingUnitNumber: Optional[int] = None
    schoolDistrictCode: Optional[int] = None
    state: Optional[str] = None
    taxDistrict: Optional[IsolvedOptionValueModelOfInt32] = None
    timeZone: Optional[str] = None
    workLocationCode: Optional[str] = None
    workLocationDescription: Optional[str] = None
    zipCode: Optional[str] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None


class IsolvedLegalModel(BaseModel):
    """Source definition: AOS.PayrollOffice.RestAPI.Models.LegalModel."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    allowRemoteWorkers: Optional[bool] = None
    client: Optional[IsolvedClientModel] = None
    compensationPlans: Optional[List[IsolvedLegalCompensationPlanModel]] = None
    dbaName: Optional[str] = None
    federalEIN: Optional[str] = None
    forceDirectDepositPrenote: Optional[bool] = None
    iSolvedTimeEnabled: Optional[bool] = None
    legalAddress: Optional[IsolvedClientAddressModel] = None
    legalCode: Optional[str] = None
    legalName: Optional[str] = None
    logoData: Optional[str] = None
    naicsCode: Optional[str] = None
    payGroups: Optional[List[IsolvedPayGroupModel]] = None
    services: Optional[List[IsolvedLegalServiceModel]] = None
    status: Optional[str] = None
    workersComps: Optional[List[IsolvedLegalWorkersCompModel]] = None
    workLocations: Optional[List[IsolvedLegalWorkLocationModel]] = None
    links: Optional[List[IsolvedBaseLinkModel]] = None
