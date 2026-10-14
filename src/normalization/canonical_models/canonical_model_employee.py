"""PrismHR employee canonical models
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict

# Covers profile/contact, employment status/dates, job/organization, and compensation.
class PrismHREmployee(BaseModel):
    """Canonical schema: Employee."""
    model_config = ConfigDict(extra="allow")

    employee_id: str
    # Client ID supplied with the input; no generated company identifier.
    source_client_id: str
    last_name: str
    first_name: str
    middle_name: str
    preferred_name: str
    personal_details: Optional[PrismHRPerson] = None
    contact_information: Optional[PrismHRContactInformation] = None
    company_employment_information: Optional[PrismHRClient] = None
    compensation_information: Optional[PrismHRCompensation] = None
    direct_deposit_information: Optional[PrismHRDirectDeposit] = None
    health_savings_account_information: Optional[PrismHRHsa] = None
    employee_events: Optional[PrismHREmployeeEvents] = None
    health_information: Optional[PrismHRHealth] = None
    skills_and_education: Optional[PrismHRSkillsAndEducation] = None
    absence_journal_ids: Optional[List[str]] = None
    benefit_enrollment_completed: Optional[bool] = None
    scheduled_deductions: Optional[List[PrismHRScheduledDeduction]] = None
    new_hire_questions: Optional[List[PrismHRNewHireQuestion]] = None
    enrollment_progress: Optional[PrismHREnrollmentInProgress] = None


# Covers employee profile information.
class PrismHRPerson(BaseModel):
    """Canonical fields based on source schema: Person."""
    model_config = ConfigDict(extra="allow")

    ethnicity_code: str
    birth_date: str
    driver_license_number: str
    cobra_ssn: str
    employer_ids: Optional[List[str]] = None
    cobra_only: Optional[bool] = None
    residential_geocode: str
    marital_status: str
    married_date: str
    tobacco_use_status: str
    service_provider_start_date: str
    disability_status: str
    blindness_status: str
    veteran_status: str
    vietnam_veteran_status: str
    disabled_veteran_status: str
    # Required by the contract, but null in the saved employee response.
    hrp_citizenship_country: Optional[str]
    deceased: Optional[bool] = None
    gender: str
    tax_zip_code: str
    highly_compensated: Optional[bool] = None
    key_employee: Optional[bool] = None
    geocode_override: str
    geocode_override_end_date: str
    nickname: str
    death_date: str
    driver_license_issuing_state: str
    driver_license_expiration_date: str
    driver_license_class: str
    ohio_form_c112: Optional[bool] = None
    unincorporated_residence: Optional[bool] = None
    w2_address_line_1: str
    w2_address_line_2: str
    w2_city: str
    w2_state: str
    w2_postal_code: str
    w2_elec_form: Optional[bool] = None
    w2_elec_form_date: str
    legacy_employee_id: str
    hispanic: Optional[bool] = None
    agriculture_worker: Optional[bool] = None
    other_protected_veteran_status: str
    active_duty_badge_veteran_status: str
    recently_separated_veteran_status: str
    service_medal_veteran_status: str
    preferred_language: str
    emergency_contacts: Optional[List[PrismHREmergencyContact]] = None
    employee_portal_user_id: Optional[str] = None
    vehicle_insurance_policies: Optional[List[PrismHRAutoPolicy]] = None
    vehicles: Optional[List[PrismHRVehicleDetails]] = None
    person_checksum: str


# Covers emergency contact information.
class PrismHREmergencyContact(BaseModel):
    """Canonical fields based on source schema: EmergencyContact."""
    model_config = ConfigDict(extra="allow")

    contact_name: str
    contact_information: str
    relationship: str
    contact_information_type: str


class PrismHRAutoPolicy(BaseModel):
    """Canonical fields based on source schema: AutoPolicy."""
    model_config = ConfigDict(extra="allow")

    policy_id: Optional[str] = None
    insurance_carrier_name: Optional[str] = None
    policyholder_name: Optional[str] = None
    policy_start_date: Optional[str] = None
    policy_expiration_date: Optional[str] = None


class PrismHRVehicleDetails(BaseModel):
    """Canonical fields based on source schema: VehicleDetails."""
    model_config = ConfigDict(extra="allow")

    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[str] = None
    added_date: Optional[str] = None
    removed_date: Optional[str] = None
    registration_number: Optional[str] = None


# Covers employee contact information.
class PrismHRContactInformation(BaseModel):
    """Canonical fields based on source schema: ContactInformation."""
    model_config = ConfigDict(extra="allow")

    address_line_1: str
    address_line_2: str
    city: str
    state: str
    postal_code: str
    postal_code_extension: str
    county: str
    school_district_code: str
    home_phone: str
    mobile_phone: str
    email_address: str


# Covers employment status/dates and job/organization details.
class PrismHRClient(BaseModel):
    """Canonical fields based on source schema: Client."""
    model_config = ConfigDict(extra="allow")

    employment_status_code: str
    employment_status_class: str
    employment_status_effective_date: str
    employment_type_code: str
    employment_type_class: str
    employment_type_effective_date: str
    transfers: Optional[List[PrismHRTransferInfo]] = None
    assigned_properties: List[PrismHRProperty]
    hawaii_medical_waivers: List[PrismHRHawaiiMedWaiver]
    job_code: str
    job_start_date: str
    first_hire_date: str
    last_hire_date: str
    flsa_exempt: Optional[bool] = None
    cafeteria_plan_contributions: Optional[List[PrismHRCafeteriaPlan]] = None
    seniority_date: str
    company_officer: Optional[bool] = None
    workers_compensation_officer: Optional[bool] = None
    s_corporation_owner: Optional[bool] = None
    business_owner: Optional[bool] = None
    termination_reason_code: str
    termination_explanation: str
    last_status_change_date: Optional[str] = None
    last_job_change_date: Optional[str] = None
    new_hire_report_date: str
    is_1099_contractor: Optional[bool] = None
    company_employee_number: str
    time_clock_employee_number: str
    primary_email_source: Optional[str] = None
    benefits_email: Optional[str] = None
    rehire_eligibility_code: str
    scheduled_return_date: str
    work_phone: str
    work_phone_extension: str
    probation_date: str
    court_ordered_medical: Optional[bool] = None
    supports_other_spouse_or_child: Optional[bool] = None
    child_spouse_support_arrears: Optional[bool] = None
    alternate_mailing_address_line_1: str
    alternate_mailing_address_line_2: str
    alternate_mailing_city: str
    alternate_mailing_state: str
    alternate_mailing_postal_code: str
    alternate_mailing_postal_code_extension: str
    handbook_sent_date: str
    handbook_received_date: str
    union_code: str
    union_start_date: str
    sub_cost_center: str
    electronically_onboarded: Optional[bool] = None
    electronic_onboarding_date: str
    pto_approver_employee_id: str
    onboarding_in_progress: Optional[bool] = None
    background_check_completed: Optional[bool] = None
    background_check_date: Optional[str] = None
    workers_compensation_exempt: Optional[bool] = None
    gender_designation: Optional[str] = None
    preferred_pronouns: Optional[str] = None
    client_checksum: str
    home_location_code: Optional[str] = None
    home_division_code: Optional[str] = None
    home_department_code: Optional[str] = None
    work_shift: Optional[str] = None
    project_cost_center_code: Optional[str] = None
    work_group_code: Optional[str] = None
    benefit_group: Optional[str] = None
    retirement_benefit_group: Optional[str] = None
    work_email: Optional[str] = None
    electronic_1095c_election: str
    manager_employee_id: str
    disability_self_identification_response: Optional[str] = None
    applicant_id: Optional[str] = None


class PrismHRTransferInfo(BaseModel):
    """Canonical fields based on source schema: TransferInfo."""
    model_config = ConfigDict(extra="allow")

    transfer_source: Optional[str] = None
    transfer_employee_id: Optional[str] = None
    transfer_company_id: Optional[str] = None
    transfer_effective_date: Optional[str] = None


class PrismHRProperty(BaseModel):
    """Canonical fields based on source schema: Property."""
    model_config = ConfigDict(extra="allow")

    property_code: str
    issued_date: str
    serial_number: str
    estimated_value: str
    returned_date: str
    comment: str


class PrismHRHawaiiMedWaiver(BaseModel):
    """Canonical fields based on source schema: HawaiiMedWaiver."""
    model_config = ConfigDict(extra="allow")

    waiver_year: str
    waiver_reason: str


class PrismHRCafeteriaPlan(BaseModel):
    """Canonical fields based on source schema: CafeteriaPlan."""
    model_config = ConfigDict(extra="allow")

    contribution_amount: str
    contribution_effective_date: str


# Covers compensation, with related tax and identity information.
class PrismHRCompensation(BaseModel):
    """Canonical fields based on source schema: Compensation."""
    model_config = ConfigDict(extra="allow")

    ssn: str
    pay_group_code: str
    pay_period_code: str
    pay_period_information: Optional[List[PrismHRPayPeriodInfo]] = None
    default_timesheet_hours: str
    pay_method_code: str
    allocation_template_id: Optional[str] = None
    labor_allocations: Optional[List[PrismHRPayAllocation]] = None
    standard_hours_per_pay_period: str
    state_taxes: Optional[List[PrismHRStateTax]] = None
    hourly_pay: str
    pay_period_salary: str
    work_shift: str
    benefit_contributions_paid_through_date: str
    advance_eic_filing_status: str
    federal_filing_status: str
    federal_withholding_allowances: str
    federal_withholding_override_type: str
    federal_withholding_override_value: str
    federal_tax_calculation_method: str
    federal_multiple_jobs: Optional[bool] = None
    federal_dependent_credit_amount: float
    federal_other_income: float
    federal_deductions: float
    pay_rate_amount: str
    pay_rate_basis: str
    mail_check_to_home: Optional[bool] = None
    automatically_accept_timesheet: Optional[bool] = None
    long_pay_table: str
    long_basis_date: str
    annual_pay: str
    pay_rate_effective_date: str
    local_taxes: Optional[List[PrismHRLocalTax]] = None
    last_pay_rate_change_percentage: str
    last_pay_rate_change_amount: str
    last_pay_date: Optional[str] = None
    quartile: str
    compa_ratio: str
    benefits_base_pay: str
    non_taxable_per_diem_rate: str
    tax_credit_emp: Optional[bool] = None
    auto_pay_code: str
    alternate_pay_rates: Optional[List[str]] = None
    pension_status: str
    profit_sharing: str
    employee_images: Optional[List[PrismHREeImage]] = None
    wage_plan_ca: Optional[bool] = None
    last_performance_review_date: str
    next_performance_review_date: str
    i9_image_audits: Optional[List[PrismHRI9ImageAudit]] = None
    last_performance_review_rating: str
    comp_review_next_date: str
    previous_performance_review_job_title: str
    federal_w5_year: str
    federal_w5_on_file: Optional[bool] = None
    federal_w4_on_file: Optional[bool] = None
    federal_w4_year: str
    lock_ins: Optional[List[PrismHRLockIns]] = None
    i9_on_file: Optional[bool] = None
    i9_renewal_date: str
    notes: str
    fica_exempt: Optional[bool] = None
    benefit_cost_per_hour: str
    performance_agreement: Optional[bool] = None
    alternate_pay_rate_2: str
    alternate_pay_rate_3: str
    alternate_pay_rate_4: str
    last_pay_rate_change_date: str
    work_geocode_override_code: str
    michigan_family_member_status: str
    missouri_trial_employment_code: str
    electronic_pay_stub: Optional[bool] = None
    vermont_health_plan_coverage: Optional[bool] = None
    last_worked_date: str
    irs_lock_in_date: str
    nonresident_alien: Optional[bool] = None
    alien_registration_expiration_date: str
    benefit_salary_override: str
    citizenship_status_code: Optional[str] = None
    first_pay_period_hours: Optional[str] = None
    compensation_checksum: str
    provider_notified_on: Optional[str] = None
    contractor_alternate_id: Optional[str] = None
    w8_on_file: Optional[bool] = None
    # Live-only field: a string in the saved Postman employee response.
    pay_periods_per_week: Optional[str] = None


class PrismHRPayPeriodInfo(BaseModel):
    """Canonical fields based on source schema: PayPeriodInfo."""
    model_config = ConfigDict(extra="allow")

    period_code: str
    period_base: str


class PrismHRPayAllocation(BaseModel):
    """Canonical fields based on source schema: PayAllocation."""
    model_config = ConfigDict(extra="allow")

    location_code: str
    allocation_percentage: str
    job_code: str
    department_code: str
    project_code: str
    division_code: str


class PrismHRStateTax(BaseModel):
    """Canonical fields based on source schema: StateTax."""
    model_config = ConfigDict(extra="allow")

    state_code: str
    nonresident_certificate_filed: Optional[str] = None
    filing_status: Optional[str] = None
    primary_withholding_allowances: Optional[str] = None
    secondary_withholding_allowances: Optional[str] = None
    exempt_amount: Optional[str] = None
    supplemental_exempt_amount: Optional[str] = None
    withholding_override_type: Optional[str] = None
    withholding_override_amount: Optional[str] = None
    reduced_additional_withholding: Optional[str] = None
    fixed_withholding_amount: Optional[str] = None
    alternate_calculation_code: Optional[str] = None
    state_w4_on_file: Optional[str] = None
    state_w4_year: Optional[str] = None
    multiple_jobs: Optional[bool] = None
    dependent_credit_amount: float
    other_income: float
    deductions: float
    nonresident_certificate_year: str


class PrismHRLocalTax(BaseModel):
    """Canonical fields based on source schema: LocalTax."""
    model_config = ConfigDict(extra="allow")

    tax_authority_id: Optional[str] = None
    filing_status: Optional[str] = None
    withholding_allowances: Optional[str] = None
    withholding_certificate_on_file: Optional[str] = None
    additional_withholding_per_pay_period: Optional[str] = None


class PrismHREeImage(BaseModel):
    """Canonical fields based on source schema: EeImage."""
    model_config = ConfigDict(extra="allow")

    master_id: str
    verify_date_time: str
    verify_user_id: str


class PrismHRI9ImageAudit(BaseModel):
    """Canonical fields based on source schema: I9ImageAudit."""
    model_config = ConfigDict(extra="allow")

    audit_date: str
    audit_user: str
    audit_id: str
    audit_step: str


class PrismHRLockIns(BaseModel):
    """Canonical fields based on source schema: LockIns."""
    model_config = ConfigDict(extra="allow")

    state: str
    state_date: str
    auth_user: str


# Covers employee direct-deposit setup.
class PrismHRDirectDeposit(BaseModel):
    """Canonical fields based on source schema: EmployeeDirectDeposit."""
    model_config = ConfigDict(extra="allow")

    ach_status: str
    applicable_voucher_types: str
    suppress_account_information_printing: Optional[bool] = None
    deposit_accounts: List[PrismHRAchVoucher]
    direct_deposit_checksum: str


class PrismHRAchVoucher(BaseModel):
    """Canonical fields based on source schema: AchVoucher."""
    model_config = ConfigDict(extra="allow")

    bank_transit_number: str
    account_number: str
    account_type: str
    calculation_method: str
    allocation_value: float
    percentage_allocation_limit: float
    status: str
    bank_name: str
    voucher_types_override: str


# Covers employee HSA deposit setup.
class PrismHRHsa(BaseModel):
    """Canonical fields based on source schema: Hsa."""
    model_config = ConfigDict(extra="allow")

    deposit_settings: List[PrismHRHsaDepositSettings]
    ach_checksum: str


class PrismHRHsaDepositSettings(BaseModel):
    """Canonical fields based on source schema: EmployeeDirectDeposit-HsaDepositSettings."""
    model_config = ConfigDict(extra="allow")

    bank_transit_number: str
    account_number: str
    account_type: str
    calculation_method: str
    allocation_value: float
    status: str
    bank_name: str
    voucher_types_override: str


# Covers employee event information.
class PrismHREmployeeEvents(BaseModel):
    """Canonical fields based on source schema: EmployeeEvents."""
    model_config = ConfigDict(extra="allow")

    events: Optional[List[PrismHREmployeeEvent]] = None


class PrismHREmployeeEvent(BaseModel):
    """Canonical fields based on source schema: EmployeeEvent."""
    model_config = ConfigDict(extra="allow")

    event_code: str
    effective_date: str
    description: str
    follow_up_action_date: str
    comment: str


# Covers additional employee health information.
class PrismHRHealth(BaseModel):
    """Canonical fields based on source schema: Health."""
    model_config = ConfigDict(extra="allow")

    allergies: Optional[List[str]] = None
    conditions: Optional[List[str]] = None
    programs: Optional[List[str]] = None
    height: str
    weight: str
    blood_type: str
    blood_rh_factor: str
    blood_donor: Optional[bool] = None
    last_blood_donation_date: str
    next_blood_donation_date: str
    drug_test_result: str
    last_drug_test_date: str
    next_drug_test_date: str
    hearing_test_result: str
    last_hearing_test_date: str
    next_hearing_test_date: str
    physical_exam_result: str
    last_physical_exam_date: str
    next_physical_exam_date: str


# Covers employee skills, education, and certifications.
class PrismHRSkillsAndEducation(BaseModel):
    """Canonical fields based on source schema: SkillsAndEducationAndCertification."""
    model_config = ConfigDict(extra="allow")

    skill_checksum: Optional[str] = None
    skills: Optional[List[PrismHRSkill]] = None
    schools: Optional[List[PrismHRSchool]] = None
    osha10_certified: Optional[bool] = None


class PrismHRSkill(BaseModel):
    """Canonical fields based on source schema: Skill."""
    model_config = ConfigDict(extra="allow")

    skill_code: str
    competency_level: str
    last_certification_date: str
    comment: str
    certification_renewal_date: str


class PrismHRSchool(BaseModel):
    """Canonical fields based on source schema: School."""
    model_config = ConfigDict(extra="allow")

    school_name: str
    year_attended: str
    graduated: Optional[bool] = None
    graduation_year: str
    degree_earned: str
    comment: str


class PrismHRScheduledDeduction(BaseModel):
    """Canonical fields based on source schema: ScheduledDeduction."""
    model_config = ConfigDict(extra="allow")

    deduction_code: str
    pay_stub_description: str
    status: str
    deduction_amount: float
    processing_start_date: Optional[str] = None
    processing_stop_date: Optional[str] = None
    designated_payee_code: Optional[str] = None


class PrismHRNewHireQuestion(BaseModel):
    """Canonical fields based on source schema: Employee-NewHireQuestions."""
    model_config = ConfigDict(extra="allow")

    code: Optional[str] = None
    description: Optional[str] = None
    answer: Optional[str] = None


class PrismHREnrollmentInProgress(BaseModel):
    """Canonical fields based on source schema: EnrollmentInProgress."""
    model_config = ConfigDict(extra="allow")

    enrollment_in_progress: Optional[bool] = None
    enrollment_type: Optional[str] = None


class PrismHREmployeeResponse(BaseModel):
    """Canonical fields based on source schema: EmployeeAndEmployeeBySsnResponse."""
    model_config = ConfigDict(extra="allow")

    error_code: str
    error_message: str
    extension: Optional[PrismHRExtension] = None
    # Individual employee validation happens after wrapper checks.
    employees: Optional[List[Any]] = None
    employee_error_messages: Optional[List[str]] = None
    update_message: Optional[str] = None


class PrismHRExtension(BaseModel):
    """Canonical fields based on source schema: Extension."""
    model_config = ConfigDict(extra="allow")

    any: Optional[Dict[str, Any]] = None