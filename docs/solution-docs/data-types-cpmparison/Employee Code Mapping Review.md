# Employee Code Mapping Review

These are source codes for review, not implemented translations. Define a common category list once, then map only relevant providers using verified dictionaries.

## Dictionaries we still need

| Field | Available evidence | Next step |
|---|---|---|
| PrismHR person.ethnicCode | No values in supplied lookup-reference.json; client-specific Ethnic option documented. | Obtain getClientCodes with options=Ethnic for the relevant client. |
| isolved ethnicOrigin | Description only; no categories supplied. | Verify available values before mapping categories. |
| UKG employee ethnicity | No counterpart identified in current employee models. | Leave absent; EEO job classification is not employee ethnicity. |
| PrismHR client.employeeStatus / client.employeeType | Client-defined codes; supplied status dictionaries concern other fields. | Obtain the correct client status/type dictionaries. |
| isolved employmentStatus / employmentCategoryCode / maritalStatus | No matching dictionary in supplied reference. | Obtain documented/client meanings. |
| UKG status / pay_info.employee_type.id / pay_info.pay_type.id | No matching employee dictionaries supplied. | Preserve source values pending lookup meanings. |

## PrismHR codes documented directly in OpenAPI

These tables come from property descriptions, not lookup-reference.json.

| Source field | Code | Documented meaning | Proposed canonical label | Status |
|---|---|---|---|---|
| person.maritalStatus | `S` | Single | `single` | Proposed; isolved dictionary still needed. |
| person.maritalStatus | `M` | Married | `married` | Proposed; isolved dictionary still needed. |
| person.maritalStatus | `D` | Divorced | `divorced` | Proposed; isolved dictionary still needed. |
| person.maritalStatus | `W` | Widowed | `widowed` | Proposed; isolved dictionary still needed. |
| person.maritalStatus | `C` | Civil Union | `civil_union` | Proposed; isolved dictionary still needed. |
| person.maritalStatus | `O` | Other | `other` | Proposed; isolved dictionary still needed. |
| compensation.hourlyPayPeriod | `H` | Hourly | `hour` | Proposed basis labels; no amount conversion. |
| compensation.hourlyPayPeriod | `W` | Weekly | `week` | Proposed basis labels; no amount conversion. |
| compensation.hourlyPayPeriod | `B` | Bi-weekly | `two_weeks` | Proposed basis labels; no amount conversion. |
| compensation.hourlyPayPeriod | `S` | Semi-monthly | `half_month` | Proposed basis labels; no amount conversion. |
| compensation.hourlyPayPeriod | `M` | Monthly | `month` | Proposed basis labels; no amount conversion. |
| compensation.hourlyPayPeriod | `Y` | Yearly | `year` | Proposed basis labels; no amount conversion. |
| person.gender | `M` | Listed without an expanded meaning in this description. | — | Do not guess the label. |
| person.gender | `F` | Listed without an expanded meaning in this description. | — | Do not guess the label. |
| person.gender | `X` | Listed without an expanded meaning in this description. | — | Do not guess the label. |
| person.gender | `D` | Listed without an expanded meaning in this description. | — | Do not guess the label. |


## Supplied lookup-reference tables

The exact source domain matters. Company status, user status, benefit status, and payroll status must not be substituted for employee status. Unrelated API tables are included for reference only.

### prismhr

Source: [lookup-reference.json](../../../contracts/prismhr/lookup-reference.json).

#### client_status_class

Source field: `#/components/schemas/ClientMaster/properties/statusClass`.

Source note: These are status classes. Do not assume a client-defined status identifier is the same as its status class.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"A"` | Active | Preserve in its own domain; no cross-domain translation approved. |
| `"P"` | Pending | Preserve in its own domain; no cross-domain translation approved. |
| `"I"` | Inactive | Preserve in its own domain; no cross-domain translation approved. |
| `"C"` | Client Cancelling, Pre-Termination | Preserve in its own domain; no cross-domain translation approved. |
| `"T"` | Terminated | Preserve in its own domain; no cross-domain translation approved. |

#### client_service_type

Source field: `#/components/schemas/ClientMaster/properties/serviceType`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"ASO"` | Administrative Services Only | Preserve in its own domain; no cross-domain translation approved. |
| `"PEO"` | Professional Employer Services | Preserve in its own domain; no cross-domain translation approved. |
| `"PAY"` | Payroll Processing Only | Preserve in its own domain; no cross-domain translation approved. |
| `"ASA"` | Admin Services/Alt. Billing | Preserve in its own domain; no cross-domain translation approved. |
| `"COR"` | Corporate Payroll | Preserve in its own domain; no cross-domain translation approved. |
| `"HRN"` | HR Services, No Payroll | Preserve in its own domain; no cross-domain translation approved. |

#### user_employee_status_class

Source field: `#/components/schemas/UserLst/properties/employeeStatusClass`.

Source note: The source says this field is returned only for userType E or M. It is not an employee status-code dictionary.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"A"` | Active | Preserve in its own domain; no cross-domain translation approved. |
| `"L"` | On Leave | Preserve in its own domain; no cross-domain translation approved. |
| `"T"` | Terminated | Preserve in its own domain; no cross-domain translation approved. |

#### payroll_history_type

Source field: `#/components/schemas/PayrollHistory/properties/type`.

Source note: All Types is a selector concept in the documented list. Do not assume A is a persisted payroll-batch classification without additional evidence.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"A"` | All Types | Preserve in its own domain; no cross-domain translation approved. |
| `"R"` | Scheduled | Preserve in its own domain; no cross-domain translation approved. |
| `"S"` | Special | Preserve in its own domain; no cross-domain translation approved. |
| `"J"` | Adjustment | Preserve in its own domain; no cross-domain translation approved. |
| `"V"` | Reversal | Preserve in its own domain; no cross-domain translation approved. |
| `"M"` | Manual | Preserve in its own domain; no cross-domain translation approved. |

#### hours_worked_basis

Source field: `#/components/schemas/HoursWorkedByHours/properties/hrsType`.

Source note: The empty string is explicitly documented here; it is not equivalent to a missing/null value in every source field.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `""` | Uses the default: hours worked | Preserve in its own domain; no cross-domain translation approved. |
| `"P"` | Paid | Preserve in its own domain; no cross-domain translation approved. |
| `"W"` | Worked | Preserve in its own domain; no cross-domain translation approved. |

#### hours_worked_position_basis

Source field: `#/components/schemas/HoursWorkedByPosition/properties/hrsType`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `""` | Uses the default: hours worked | Preserve in its own domain; no cross-domain translation approved. |
| `"P"` | Paid | Preserve in its own domain; no cross-domain translation approved. |
| `"W"` | Worked | Preserve in its own domain; no cross-domain translation approved. |

#### benefit_enrollment_status

Source field: `#/components/schemas/BenefitPlan/properties/status`.

Source note: Benefit enrollment status is a different domain from employment status.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"E"` | Eligible Unenrolled | Preserve in its own domain; no cross-domain translation approved. |
| `"A"` | Active Enrollment | Preserve in its own domain; no cross-domain translation approved. |
| `"T"` | Terminated Enrollment | Preserve in its own domain; no cross-domain translation approved. |
| `"C"` | COBRA Enrollment | Preserve in its own domain; no cross-domain translation approved. |
| `"W"` | Waived Enrollment | Preserve in its own domain; no cross-domain translation approved. |

#### deduction_type

Source field: `#/components/schemas/DeductionCodeDetail/properties/deductionType`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"V"` | Voluntary | Preserve in its own domain; no cross-domain translation approved. |
| `"C"` | Section 125 | Preserve in its own domain; no cross-domain translation approved. |
| `"P"` | Post Tax Benefit | Preserve in its own domain; no cross-domain translation approved. |
| `"F"` | Flexible Spending Account | Preserve in its own domain; no cross-domain translation approved. |
| `"G"` | Wage Garnishment | Preserve in its own domain; no cross-domain translation approved. |
| `"L"` | Employee Loan Payment | Preserve in its own domain; no cross-domain translation approved. |
| `"K"` | Pre-Tax Retirement Contribution | Preserve in its own domain; no cross-domain translation approved. |
| `"KC"` | Catch-Up Retirement Contribution | Preserve in its own domain; no cross-domain translation approved. |
| `"KE"` | Post-Tax Retirement Contribution | Preserve in its own domain; no cross-domain translation approved. |
| `"KL"` | Retirement Plan Loan Payment | Preserve in its own domain; no cross-domain translation approved. |
| `"KR"` | Roth 401(k) Contribution | Preserve in its own domain; no cross-domain translation approved. |
| `"KCR"` | Roth 401(k) Catch-Up Contribution | Preserve in its own domain; no cross-domain translation approved. |

### isolved

Source: [lookup-reference.json](../../../contracts/isolved/lookup-reference.json).

#### /paths/~1api~1clients~1{clientId}~1legals~1{legalId}~1employees~1{employeeId}~1scheduleReportByType/get/parameters/4

Source field: `#/paths/~1api~1clients~1{clientId}~1legals~1{legalId}~1employees~1{employeeId}~1scheduleReportByType/get/parameters/4`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"Day"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Week"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Month"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### /definitions/iSolved.Dto.Notification/properties/severity

Source field: `#/definitions/iSolved.Dto.Notification/properties/severity`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"Info"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Error"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Warning"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Success"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### /definitions/AOS.BusinessEntities.Payroll.ValidationMessage/properties/severity

Source field: `#/definitions/AOS.BusinessEntities.Payroll.ValidationMessage/properties/severity`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"Information"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Warning"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Error"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"FileFormatError"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### /definitions/AOS.PayrollOffice.RestAPI.Models.ScheduleBulkCopyModel/properties/overlapAction

Source field: `#/definitions/AOS.PayrollOffice.RestAPI.Models.ScheduleBulkCopyModel/properties/overlapAction`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"Cancel"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Skip"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Replace"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### /definitions/AOS.PayrollOffice.RestAPI.Models.ScheduleBulkCopyModel/properties/overlapType

Source field: `#/definitions/AOS.PayrollOffice.RestAPI.Models.ScheduleBulkCopyModel/properties/overlapType`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"Day"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Shift"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### /definitions/AOS.PayrollOffice.RestAPI.Models.ScheduleCopyModel/properties/destinationDays/items

Source field: `#/definitions/AOS.PayrollOffice.RestAPI.Models.ScheduleCopyModel/properties/destinationDays/items`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"Sunday"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Monday"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Tuesday"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Wednesday"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Thursday"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Friday"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Saturday"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### /definitions/AOS.PayrollOffice.RestAPI.Models.ScheduleCopyModel/properties/overlapAction

Source field: `#/definitions/AOS.PayrollOffice.RestAPI.Models.ScheduleCopyModel/properties/overlapAction`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"Skip"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Replace"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### /definitions/AOS.PayrollOffice.RestAPI.Models.ScheduleCopyModel/properties/overlapType

Source field: `#/definitions/AOS.PayrollOffice.RestAPI.Models.ScheduleCopyModel/properties/overlapType`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"Day"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Shift"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### /definitions/AOS.PayrollOffice.RestAPI.Models.TimecardApiPunchModel/properties/timecardPunchMode

Source field: `#/definitions/AOS.PayrollOffice.RestAPI.Models.TimecardApiPunchModel/properties/timecardPunchMode`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"Auto"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"In"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Out"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### /definitions/AOS.PayrollOffice.RestAPI.Models.TimecardApiPunchModel/properties/timecardPunchSource

Source field: `#/definitions/AOS.PayrollOffice.RestAPI.Models.TimecardApiPunchModel/properties/timecardPunchSource`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"Clock"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"ESSWeb"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Mobile"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"TimecardProcessor"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"ESSPunchPage"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Timecard"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"VirtualClock"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### /definitions/AOS.PayrollOffice.RestAPI.Models.TimecardApiPunchModel/properties/timecardPunchType

Source field: `#/definitions/AOS.PayrollOffice.RestAPI.Models.TimecardApiPunchModel/properties/timecardPunchType`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"Normal"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Meal"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Break"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"AutoMeal"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"AutoBreak"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"Allocate"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

### ukg-ready

Source: [lookup-reference.json](../../../contracts/ukg-ready/lookup-reference.json).

#### __v2__companies__(cid)__employees__(aid).html:/properties/phones/properties/preferred_phone

Source field: `reference-schemas.json#/schemas/106/schema/properties/phones/properties/preferred_phone`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"HOME"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"CELL"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"WORK"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"NONE"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### __v2__companies__(cid)__employees__(aid).html:/properties/cost_centers_info/properties/limits/items/properties/values/items/properties/type

Source field: `reference-schemas.json#/schemas/106/schema/properties/cost_centers_info/properties/limits/items/properties/values/items/properties/type`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"ROOT"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"LIST"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### __v2__companies__(cid)__employees__(aid).html:/properties/hardware_settings/properties/in_touch/properties/security_level

Source field: `reference-schemas.json#/schemas/106/schema/properties/hardware_settings/properties/in_touch/properties/security_level`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"EMPLOYEE"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"MANAGER"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### __v2__companies__(cid)__employees__(aid).html:/properties/national_id_numbers/items/properties/type

Source field: `reference-schemas.json#/schemas/106/schema/properties/national_id_numbers/items/properties/type`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"SSN"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"BSN"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"SIN"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"NIN"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"TFN"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"NSS"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"OTHER_1"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"OTHER_2"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"OTHER_3"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"OTHER_4"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"OTHER_5"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"OTHER_6"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"OTHER_7"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"OTHER_8"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"OTHER_9"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"OTHER_10"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"NO_ID_NEEDED"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### __v2__companies__(cid)__employees__(aid)__pay-info.html:/properties/medical_eligibility

Source field: `reference-schemas.json#/schemas/159/schema/properties/medical_eligibility`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"ELIGIBLE"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"NOT_ELIGIBLE"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### __v2__companies__(cid)__employees__(aid)__pay-info.html:/properties/dental_eligibility

Source field: `reference-schemas.json#/schemas/159/schema/properties/dental_eligibility`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"NOT_ELIGIBLE"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"PAYEE"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"PAYEE_SPOUSE_CHILD"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"PAYEE_SPOUSE"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"PAYEE_CHILD"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### __v2__companies__(cid)__employees__(aid)__pay-info.html:/properties/dependent_benefits_eligibility

Source field: `reference-schemas.json#/schemas/159/schema/properties/dependent_benefits_eligibility`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"ELIGIBLE"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"NOT_ELIGIBLE"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### __v2__companies__(cid)__employees__(aid)__pay-info.html:/properties/benefit_auto_enrollment_eligibility

Source field: `reference-schemas.json#/schemas/159/schema/properties/benefit_auto_enrollment_eligibility`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"ELIGIBLE"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"NOT_ELIGIBLE"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### __v2__companies__(cid)__employees__(aid)__pay-info.html:/properties/eeo_classification

Source field: `reference-schemas.json#/schemas/159/schema/properties/eeo_classification`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"EXECUTIVE_OR_SENIOR_LEVEL_OFFICIALS_AND_MANAGERS"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"FIRST_OR_MID_LEVEL_OFFICIALS_AND_MANAGERS"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"PROFESSIONALS"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"TECHNICIANS"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"SALES_WORKERS"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"ADMINISTRATIVE_SUPPORT_WORKERS"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"CRAFT_WORKERS"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"OPERATIVES"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"LABORERS_AND_HELPERS"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"SERVICE_WORKERS"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### __v2__companies__(cid)__employees__(aid)__pay-info.html:/properties/eeo4_classification

Source field: `reference-schemas.json#/schemas/159/schema/properties/eeo4_classification`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"OFFICIALS"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"PROFESSIONALS"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"TECHNICIANS"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"PROTECTIVE_SERVICE"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"PARAPROFESSIONALS"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"ADMINISTRATIVE_SUPPORT"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"SKILLED_CRAFT"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"SERVICE_MAINTENANCE"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### __v2__companies__(cid)__employees__(aid)__pay-info.html:/properties/eeo4_function

Source field: `reference-schemas.json#/schemas/159/schema/properties/eeo4_function`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"FINANCIAL_ADMINISTRATION"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"STREETS_HIGHWAYS"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"PUBLIC_WELFARE"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"POLICE_PROTECTION"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"FIRE_PROTECTION"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"NATURAL_RESOURCES"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"HOSPITALS"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"HEALTH"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"HOUSING"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"COMMUNITY_DEVELOPMENT"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"CORRECTIONS"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"UTILITY_TRANSPORTATION"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"SANITATION_SEWAGE"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"EMPLOYMENT_SECURITY"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"OTHER"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### __v2__companies__(cid)__employees__(aid)__pay-info.html:/properties/payroll_classification

Source field: `reference-schemas.json#/schemas/159/schema/properties/payroll_classification`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"REGULAR"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"HOUSEHOLD"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"FORM_943"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### __v2__companies__(cid)__payrolls__(id).html:/properties/status

Source field: `reference-schemas.json#/schemas/360/schema/properties/status`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"NEW"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"OPEN"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"OPEN_FAILED"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"CLOSE_FAILED"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"CLOSED"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"SUBMITTED"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"ROLLBACK_FAILED"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"FINALIZE_FAILED"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"FINALIZED"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### __v2__companies__(cid)__payrolls__(id)__pay-statements__(id).html:/properties/status

Source field: `reference-schemas.json#/schemas/364/schema/properties/status`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"INVALID"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"NEW"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"OPEN"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"CLOSED"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"FINALIZED"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

#### __v2__companies__(cid)__time-entries.html:/properties/time_entry_sets/items/properties/time_entries/items/properties/type

Source field: `reference-schemas.json#/schemas/461/schema/properties/time_entry_sets/items/properties/time_entries/items/properties/type`.

| Source code | Documented meaning | Handling for now |
|---|---|---|
| `"TIME"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |
| `"EXTRA_PAY"` | No per-code meaning supplied. | Preserve in its own domain; no cross-domain translation approved. |

## Verification

174 supplied lookup entries are reproduced with their domains. Missing meanings are not invented.
