"""UKG Ready employee source models.

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

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class UKGReadyEmployeeListResponse(BaseModel):
    """Cached schema path: 104."""
    model_config = ConfigDict(extra="allow")

    employees: List[UKGReadyEmployeeListResponseEmployeesItem]


class UKGReadyEmployeeListResponseEmployeesItem(BaseModel):
    """Cached schema path: 104/employees[]."""
    model_config = ConfigDict(extra="allow")

    id: float
    username: Optional[str] = None
    employee_id: Optional[str] = None
    external_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    primary_account_id: Optional[float] = None
    ein_name: Optional[str] = None
    dates: Optional[UKGReadyEmployeeListResponseEmployeesItemDates] = None
    status: Optional[str] = None
    links: Optional[UKGReadyEmployeeListResponseEmployeesItemLinks] = Field(default=None, alias="_links")


class UKGReadyEmployeeListResponseEmployeesItemDates(BaseModel):
    """Cached schema path: 104/employees[]/dates."""
    model_config = ConfigDict(extra="allow")

    hired: Optional[str] = None
    re_hired: Optional[str] = None
    started: Optional[str] = None
    terminated: Optional[str] = None


class UKGReadyEmployeeListResponseEmployeesItemLinks(BaseModel):
    """Cached schema path: 104/employees[]/_links."""
    model_config = ConfigDict(extra="allow")

    self: Optional[str] = None
    demographics: Optional[str] = None
    pay_info: Optional[str] = Field(default=None, alias="pay-info")
    badges: Optional[str] = None
    profiles: Optional[str] = None
    hcm_profiles: Optional[str] = Field(default=None, alias="hcm-profiles")
    hcm_fields: Optional[str] = Field(default=None, alias="hcm-fields")
    # Live-only field; type observed in the saved response.
    country_fields: Optional[str] = Field(default=None, alias="country-fields")


class UKGReadyEmployee(BaseModel):
    """Cached schema path: 106."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_href: Optional[str] = None
    isPhotoUploaded: Optional[bool] = None
    middle_name: Optional[str] = None
    external_id: Optional[str] = None
    employee_id: Optional[str] = None
    status: Optional[str] = None
    bsn: Optional[str] = None
    address: Optional[UKGReadyEmployeeAddress] = None
    use_separate_mailing_address: Optional[bool] = None
    mailing_address: Optional[UKGReadyEmployeeMailingAddress] = None
    primary_account_id: Optional[float] = None
    ein: Optional[UKGReadyEmployeeEin] = None
    force_change_password: Optional[bool] = None
    locked: Optional[bool] = None
    first_screen: Optional[UKGReadyEmployeeFirstScreen] = None
    phones: Optional[UKGReadyEmployeePhones] = None
    locale: Optional[UKGReadyEmployeeLocale] = None
    managers: Optional[List[UKGReadyEmployeeManagersItem]] = None
    national_insurance: Optional[str] = None
    nickname: Optional[str] = None
    primary_email: Optional[str] = None
    secondary_email: Optional[str] = None
    salutation: Optional[str] = None
    social_insurance: Optional[str] = None
    social_security: Optional[str] = None
    suffix: Optional[str] = None
    timezone: Optional[str] = None
    cost_centers_info: Optional[UKGReadyEmployeeCostCentersInfo] = None
    add_to_new_hire_export: Optional[bool] = None
    dates: Optional[UKGReadyEmployeeDates] = None
    account_extra_fields: Optional[List[UKGReadyEmployeeAccountExtraFieldsItem]] = None
    time_entry_extra_fields: Optional[List[UKGReadyEmployeeTimeEntryExtraFieldsItem]] = None
    links: Optional[UKGReadyEmployeeLinks] = Field(default=None, alias="_links")
    hardware_settings: Optional[UKGReadyEmployeeHardwareSettings] = None
    managed_cost_centers_enabled: Optional[bool] = None
    managed_cost_centers_settings: Optional[UKGReadyEmployeeManagedCostCentersSettings] = None
    national_id_numbers: Optional[List[UKGReadyEmployeeNationalIdNumbersItem]] = None


class UKGReadyEmployeeAddress(BaseModel):
    """Cached schema path: 106/address."""
    model_config = ConfigDict(extra="allow")

    country: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    address_line_3: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    state_code: Optional[str] = None
    zip: Optional[str] = None
    number: Optional[str] = None
    number_addition: Optional[str] = None


class UKGReadyEmployeeMailingAddress(BaseModel):
    """Cached schema path: 106/mailing_address."""
    model_config = ConfigDict(extra="allow")

    country: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    address_line_3: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    state_code: Optional[str] = None
    zip: Optional[str] = None
    number: Optional[str] = None
    number_addition: Optional[str] = None


class UKGReadyEmployeeEin(BaseModel):
    """Cached schema path: 106/ein."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]


class UKGReadyEmployeeFirstScreen(BaseModel):
    """Cached schema path: 106/first_screen."""
    model_config = ConfigDict(extra="allow")

    id: Optional[str]


class UKGReadyEmployeePhones(BaseModel):
    """Cached schema path: 106/phones."""
    model_config = ConfigDict(extra="allow")

    cell_phone_country_id: Optional[str] = None
    cell_phone_country_code: Optional[str] = None
    cell_phone: Optional[str] = None
    home_phone_country_id: Optional[str] = None
    home_phone_country_code: Optional[str] = None
    home_phone: Optional[str] = None
    work_phone_country_id: Optional[str] = None
    work_phone_country_code: Optional[str] = None
    work_phone: Optional[str] = None
    # Type follows the documented string enum; membership checks are deferred.
    preferred_phone: Optional[str] = None


class UKGReadyEmployeeLocale(BaseModel):
    """Cached schema path: 106/locale."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]


class UKGReadyEmployeeManagersItem(BaseModel):
    """Cached schema path: 106/managers[]."""
    model_config = ConfigDict(extra="allow")

    index: Optional[int] = None
    empl_ref: Optional[UKGReadyEmployeeManagersItemEmplRef] = None


class UKGReadyEmployeeManagersItemEmplRef(BaseModel):
    """Cached schema path: 106/managers[]/empl_ref."""
    model_config = ConfigDict(extra="allow")

    account_id: Optional[float] = None


class UKGReadyEmployeeCostCentersInfo(BaseModel):
    """Cached schema path: 106/cost_centers_info."""
    model_config = ConfigDict(extra="allow")

    defaults: Optional[List[UKGReadyEmployeeCostCentersInfoDefaultsItem]] = None
    limits: Optional[List[UKGReadyEmployeeCostCentersInfoLimitsItem]] = None


class UKGReadyEmployeeCostCentersInfoDefaultsItem(BaseModel):
    """Cached schema path: 106/cost_centers_info/defaults[]."""
    model_config = ConfigDict(extra="allow")

    index: Optional[int] = None
    value: Optional[UKGReadyEmployeeCostCentersInfoDefaultsItemValue] = None


class UKGReadyEmployeeCostCentersInfoDefaultsItemValue(BaseModel):
    """Cached schema path: 106/cost_centers_info/defaults[]/value."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]


class UKGReadyEmployeeCostCentersInfoLimitsItem(BaseModel):
    """Cached schema path: 106/cost_centers_info/limits[]."""
    model_config = ConfigDict(extra="allow")

    index: Optional[int] = None
    values: Optional[List[UKGReadyEmployeeCostCentersInfoLimitsItemValuesItem]] = None


class UKGReadyEmployeeCostCentersInfoLimitsItemValuesItem(BaseModel):
    """Cached schema path: 106/cost_centers_info/limits[]/values[]."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    effective_from: Optional[str] = None
    # Type follows the documented string enum; membership checks are deferred.
    type: Optional[str] = None


class UKGReadyEmployeeDates(BaseModel):
    """Cached schema path: 106/dates."""
    model_config = ConfigDict(extra="allow")

    hired: Optional[str] = None
    deceased: Optional[str] = None
    re_hired: Optional[str] = None
    started: Optional[str] = None
    birthday: Optional[str] = None
    review: Optional[str] = None
    seniority: Optional[str] = None
    frozen_benefit: Optional[str] = None
    benefits: Optional[str] = None
    retired: Optional[str] = None
    terminated: Optional[str] = None
    peo_hired: Optional[str] = None
    custom_dates: Optional[List[UKGReadyEmployeeDatesCustomDatesItem]] = None


class UKGReadyEmployeeDatesCustomDatesItem(BaseModel):
    """Cached schema path: 106/dates/custom_dates[]."""
    model_config = ConfigDict(extra="allow")

    index: Optional[int] = None
    date: Optional[str] = None


class UKGReadyEmployeeAccountExtraFieldsItem(BaseModel):
    """Cached schema path: 106/account_extra_fields[]."""
    model_config = ConfigDict(extra="allow")

    index: Optional[int] = None
    values: Optional[List[UKGReadyEmployeeAccountExtraFieldsItemValuesItem]] = None


class UKGReadyEmployeeAccountExtraFieldsItemValuesItem(BaseModel):
    """Cached schema path: 106/account_extra_fields[]/values[]."""
    model_config = ConfigDict(extra="allow")

    value: Optional[str] = None
    effective_from: Optional[str] = None


class UKGReadyEmployeeTimeEntryExtraFieldsItem(BaseModel):
    """Cached schema path: 106/time_entry_extra_fields[]."""
    model_config = ConfigDict(extra="allow")

    index: Optional[int] = None
    value: Optional[str] = None


class UKGReadyEmployeeLinks(UKGReadyEmployeeListResponseEmployeesItemLinks):
    """Cached schema path: 106/_links."""
    model_config = ConfigDict(extra="allow")

    self: Optional[str] = None
    demographics: Optional[str] = None
    pay_info: Optional[str] = Field(default=None, alias="pay-info")
    badges: Optional[str] = None
    profiles: Optional[str] = None
    hcm_profiles: Optional[str] = Field(default=None, alias="hcm-profiles")
    hcm_fields: Optional[str] = Field(default=None, alias="hcm-fields")


class UKGReadyEmployeeHardwareSettings(BaseModel):
    """Cached schema path: 106/hardware_settings."""
    model_config = ConfigDict(extra="allow")

    in_touch: Optional[UKGReadyEmployeeHardwareSettingsInTouch] = None


class UKGReadyEmployeeHardwareSettingsInTouch(BaseModel):
    """Cached schema path: 106/hardware_settings/in_touch."""
    model_config = ConfigDict(extra="allow")

    # Type follows the documented string enum; membership checks are deferred.
    security_level: Optional[str] = None
    pin: Optional[int] = None


class UKGReadyEmployeeManagedCostCentersSettings(BaseModel):
    """Cached schema path: 106/managed_cost_centers_settings."""
    model_config = ConfigDict(extra="allow")

    allow_save_others_cost_centers: Optional[bool] = None


class UKGReadyEmployeeNationalIdNumbersItem(BaseModel):
    """Cached schema path: 106/national_id_numbers[]."""
    model_config = ConfigDict(extra="allow")

    type: Optional[str] = None
    value: Optional[str] = None
    primary: Optional[bool] = None


class UKGReadyEmployeePayInfo(BaseModel):
    """Cached schema path: 159."""
    model_config = ConfigDict(extra="allow")

    default_job: Optional[UKGReadyEmployeePayInfoDefaultJob] = None
    job_change_reason_code: Optional[UKGReadyEmployeePayInfoJobChangeReasonCode] = None
    job_last_changed: Optional[str] = None
    standard_work_day: Optional[int] = None
    employee_type: Optional[UKGReadyEmployeePayInfoEmployeeType] = None
    pay_type: Optional[UKGReadyEmployeePayInfoPayType] = None
    shift_premium: Optional[UKGReadyEmployeePayInfoShiftPremium] = None
    medical_eligibility: Optional[str] = None
    dental_eligibility: Optional[str] = None
    dependent_benefits_eligibility: Optional[str] = None
    benefit_auto_enrollment_eligibility: Optional[str] = None
    eeo_classification: Optional[str] = None
    eeo4_classification: Optional[str] = None
    eeo4_function: Optional[str] = None
    workers_comp_code: Optional[UKGReadyEmployeePayInfoWorkersCompCode] = None
    union: Optional[UKGReadyEmployeePayInfoUnion] = None
    payroll_classification: Optional[str] = None
    bank_account_number: Optional[str] = None
    pay_grade: Optional[UKGReadyEmployeePayInfoPayGrade] = None
    gl_codes: Optional[List[UKGReadyEmployeePayInfoGlCodesItem]] = None
    ttoc: Optional[List[UKGReadyEmployeePayInfoTtocItem]] = None


class UKGReadyEmployeePayInfoDefaultJob(BaseModel):
    """Cached schema path: 159/default_job."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]


class UKGReadyEmployeePayInfoJobChangeReasonCode(BaseModel):
    """Cached schema path: 159/job_change_reason_code."""
    model_config = ConfigDict(extra="allow")

    display_name: Optional[str] = None


class UKGReadyEmployeePayInfoEmployeeType(BaseModel):
    """Cached schema path: 159/employee_type."""
    model_config = ConfigDict(extra="allow")

    id: Optional[float]


class UKGReadyEmployeePayInfoPayType(BaseModel):
    """Cached schema path: 159/pay_type."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]


class UKGReadyEmployeePayInfoShiftPremium(BaseModel):
    """Cached schema path: 159/shift_premium."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]


class UKGReadyEmployeePayInfoWorkersCompCode(BaseModel):
    """Cached schema path: 159/workers_comp_code."""
    model_config = ConfigDict(extra="allow")

    external_id: Optional[str] = None


class UKGReadyEmployeePayInfoUnion(BaseModel):
    """Cached schema path: 159/union."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]


class UKGReadyEmployeePayInfoPayGrade(BaseModel):
    """Cached schema path: 159/pay_grade."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    parent: Optional[UKGReadyEmployeePayInfoPayGradeParent] = None


class UKGReadyEmployeePayInfoPayGradeParent(BaseModel):
    """Cached schema path: 159/pay_grade/parent."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    code: Optional[int] = None
    name: Optional[str] = None


class UKGReadyEmployeePayInfoGlCodesItem(BaseModel):
    """Cached schema path: 159/gl_codes[]."""
    model_config = ConfigDict(extra="allow")

    index: Optional[int] = None
    value: Optional[str] = None


class UKGReadyEmployeePayInfoTtocItem(BaseModel):
    """Cached schema path: 159/ttoc[]."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    display_name: Optional[str] = None
    effective_from: Optional[str] = None


class UKGReadyCompensationHistoryResponse(BaseModel):
    """Cached schema path: 122."""
    model_config = ConfigDict(extra="allow")

    compensations: List[UKGReadyCompensationHistoryResponseCompensationsItem]


class UKGReadyCompensationHistoryResponseCompensationsItem(BaseModel):
    """Cached schema path: 122/compensations[]."""
    model_config = ConfigDict(extra="allow")

    id: Optional[int]
    employee: Optional[UKGReadyCompensationHistoryResponseCompensationsItemEmployee] = None
    effective_from: Optional[str] = None
    amount: Optional[float] = None
    hourly_pay: Optional[float] = None
    currency: Optional[str] = None
    amount_period: Optional[str] = None
    time: Optional[int] = None
    time_period: Optional[str] = None
    num_pp_in_year: Optional[int] = None
    links: Optional[UKGReadyCompensationHistoryResponseCompensationsItemLinks] = Field(default=None, alias="_links")


class UKGReadyCompensationHistoryResponseCompensationsItemEmployee(BaseModel):
    """Cached schema path: 122/compensations[]/employee."""
    model_config = ConfigDict(extra="allow")

    account_id: Optional[float] = None


class UKGReadyCompensationHistoryResponseCompensationsItemLinks(BaseModel):
    """Cached schema path: 122/compensations[]/_links."""
    model_config = ConfigDict(extra="allow")

    self: Optional[str] = None


class UKGReadyEmployeeInput(UKGReadyEmployee):
    """Shared list/detail record with optional supplemental response sections."""
    # List IDs are numbers; detail IDs are nullable integers.
    id: Optional[Union[int, float]]
    ein_name: Optional[str] = None
    pay_info: Optional[UKGReadyEmployeePayInfo] = None
    compensation_history: Optional[UKGReadyCompensationHistoryResponse] = None

    @classmethod
    def validate_response(cls, response: Any) -> List[Any]:
        if isinstance(response, dict) and "employees" in response:
            return UKGReadyCombinedEmployeeListResponse.model_validate(response).employees
        return [cls.model_validate(response)]


class UKGReadyCombinedEmployeeListResponse(UKGReadyEmployeeListResponse):
    employees: List[UKGReadyEmployeeInput]
