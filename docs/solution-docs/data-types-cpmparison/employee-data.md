# Employee Full Record — Response Fields

All fields from each provider's employee full record API, matched by meaning across providers.

| Provider | Endpoint | Source |
| --- | --- | --- |
| PrismHR | `getEmployee` (`options=Person,Client,Compensation,ContactInformation`) | Saved response, employee A00576 (258 fields); paths under `employee[]`; empty lists filled from schema `Employee` |
| isolved | `…/employees/{id}?includeOrganizations=true&includeAlternateRates=true&includeLabors=true&includeMiscFields=true&includeMiscDataSets=true` | Saved response "isol - employeeFullRecord-new", employee 859139 (94 fields); fields not returned filled from schema `EmployeeModel` |
| UKG | `…/employees/{aid}` + `…/employees/{aid}/pay-info` | `employees/{aid}`: live response shared in chat (40 fields, SSN masked); `pay-info`: saved response (7 fields); fields not returned filled from `schemas[106]` and `schemas[159]` |

- `.` marks a nested field; `[]` marks a list.
- † = in the schema but not in the live response (empty or not set for this employee).
- UKG fields prefixed `pay-info.` come from the `pay-info` API.
- Live field names are used where they differ from the schema (see Findings).

## Matched Fields

| Group | Field | PrismHR | isolved | UKG |
|---|---|---|---|---|
| Identity | Employee ID | `id` | `id` | `id`, `primary_account_id` |
| Identity | Employee number | `client.clientEmployeeId` | `employeeNumber` | `employee_id` |
| Identity | External / unique ID | — | `uniqueId` | `external_id`† |
| Identity | User login | `person.userId` | — | `username` |
| Name | First name | `firstName` | `nameAddress.firstName` | `first_name` |
| Name | Middle name | `middleInitial` | `nameAddress.middleName` | `middle_name` |
| Name | Last name | `lastName` | `nameAddress.lastName` | `last_name` |
| Name | Preferred name / nickname | `preferredName`, `person.nickname` | `nameAddress.preferredName` | `nickname`† |
| Name | Prefix / salutation | — | `nameAddress.prefix` | `salutation`† |
| Name | Suffix | — | `nameAddress.suffix` | `suffix`† |
| Name | Pronouns | `client.preferredPronoun` | `nameAddress.preferredPronouns`, `personal.preferredPronouns` | — |
| Personal | Birth date | `person.birthDate` | `birthDate` | `dates.birthday` |
| Personal | Gender | `person.gender`, `client.genderDesignation` | `gender`, `eeoGenderOverride`† | — |
| Personal | Ethnicity | `person.ethnicCode`, `person.hispanic` | `ethnicOrigin` | — |
| Personal | Marital status | `person.maritalStatus` | `maritalStatus` | — |
| Personal | SSN / national ID | `compensation.ssn` | `ssn` | `social_security`, `national_id_numbers[].type`, `.value`, `.primary`, `bsn`†, `national_insurance`†, `social_insurance`† |
| Personal | Citizenship | `person.hrpCitizenshipCountry`, `compensation.citizenshipStatus` | `citizenship` | — |
| Personal | Tobacco use | `person.smoker` | `tobaccoUse`, `tobaccoUseEffectiveDate`† | — |
| Personal | Disability | `person.handicapped`, `client.selfIdDisabilityForm` | `disabled`†, `disabledEffectiveDate`†, `disabilityDescription`†, `disabilityNotes`†, `disabledRequiresAccomodation`† | — |
| Personal | Veteran status | `person.veteran`, `.vietnamVet`, `.disabledVet`, `.otherProtectedVet`, `.activeDutyBadgeVet`, `.serviceMedalVet` | `protectedVeteran`, `militaryStatus`, `veteranStatusNotSpecified`, `activeDutySeparationDate`† | — |
| Personal | Recently separated veteran | `person.recentlySeparatedVet` | `isRecentlySeparatedVeteran` | — |
| Personal | Deceased date | `person.deceased`, `person.deceasedDate` | — | `dates.deceased`† |
| Personal | Preferred language / locale | `person.preferredLanguage` | — | `locale.id`† |
| Personal | Emergency contacts | `person.emergencyContact[]` (`contactName`†, `contactInfo`†, `contactRelationship`†, `contactType`†) | — | — |
| Contact | Address line 1 | `contactInformation.addressLine1` | `nameAddress.address1` | `address.address_line_1` |
| Contact | Address line 2 | `contactInformation.addressLine2` | `nameAddress.address2` | — |
| Contact | City | `contactInformation.city` | `nameAddress.city` | `address.city` |
| Contact | State | `contactInformation.state` | `nameAddress.state` | `address.state`, `address.state_code` |
| Contact | ZIP | `contactInformation.zipcode`, `.zipSuffix` | `nameAddress.zipCode` | `address.zip` |
| Contact | Country | — | — | `address.country` |
| Contact | County | `contactInformation.county` | — | — |
| Contact | School district | `contactInformation.schoolDistrict` | `nameAddress.schoolDistrictCode`† | — |
| Contact | Tax geo code | `person.geoCode` | `nameAddress.residentGeoCode` | — |
| Contact | Alternate / mailing address | `client.addressLine1`, `.addressLine2`, `.city`, `.state`, `.zip`, `.zipSuffix` | `overrideAddress.*`† (13), `nameAddress.overrideAddress.*`† (13) | `use_separate_mailing_address`, `mailing_address`† |
| Contact | Primary email | `contactInformation.emailAddress` | `emailAddress` | `primary_email`† |
| Contact | Work email | `client.workEmail` | — | — |
| Contact | Personal email | — | `personal.personalEmailAddress` | — |
| Contact | Home phone | `contactInformation.homePhone` | `personal.homePhone` | `phones.home_phone`†, `_country_id`†, `_country_code`† |
| Contact | Mobile phone | `contactInformation.mobilePhone` | `personal.mobilePhone` | `phones.cell_phone`†, `_country_id`†, `_country_code`† |
| Contact | Work phone | `client.workPhone`, `client.workPhoneExt` | `personal.officePhone` | `phones.work_phone`†, `_country_id`†, `_country_code`† |
| Employment | Employment status | `client.employeeStatus`, `client.statusClass` | `employmentStatus` | `status` |
| Employment | Status date | `client.statusDate`, `client.lastStatusChangeDate` | `statusDate`, `updatedStatusDate`† | — |
| Employment | Employee type | `client.employeeType`, `.typeClass`, `.typeDate` | `employmentCategoryCode`, `employmentCategoryEffectiveDate` | `pay-info.employee_type.id` |
| Employment | Original hire date | `client.firstHireDate` | `originalHireDate` | `dates.hired` |
| Employment | Latest hire / rehire date | `client.lastHireDate` | `hireDate`, `rehireDate`†, `updatedHireDate`† | — |
| Employment | Seniority date | `client.seniorityDate` | `adjustedServiceDate`† | `dates.seniority`† |
| Employment | PEO start date | `person.peoStartDate` | — | `dates.peo_hired`† |
| Employment | Termination date | — | `terminationDate` | `dates.terminated`† |
| Employment | Termination reason | `client.termReasonCode`, `client.termExplanation` | `terminationReason`, `terminationType` | — |
| Employment | Eligible for rehire | `client.rehireOk` | `eligibleForRehire` | — |
| Employment | Next review date | `compensation.perfReviewNextDate` | — | `dates.review`† |
| Employment | I-9 completed | `compensation.formI9Filed` | `i9Documents.i9Completed`, `.i9CompletedDate` | — |
| Job & org | Job code | `client.jobCode` | `jobCode`, `jobId` | `pay-info.default_job.id`† |
| Job & org | Job title | — | `jobTitle` | — |
| Job & org | Job start date | `client.jobStartDate`, `client.lastJobChangeDate` | `jobEffectiveDate`, `updatedJobEffectiveDate`† | `pay-info.job_last_changed`† |
| Job & org | FLSA exempt | `client.flsaExempt` | `jobFLSAExempt` | — |
| Job & org | EEO classification | — | `jobEeoCategory` | `pay-info.eeo_classification`†, `pay-info.eeo4_classification`, `pay-info.eeo4_function` |
| Job & org | Union | `client.unionCode`, `client.unionDate` | `jobIsUnion` | `pay-info.union.id`† |
| Job & org | Workers' comp code | — | `workersCompCode`† | `pay-info.workers_comp_code.external_id`† |
| Job & org | Employer / legal entity | `person.employerId[]` | `legalCode` | `ein.id`, `ein_name` |
| Job & org | Work location | `client.homeLocation` | `workLocation`, `workLocationDashDescription`, `organizations[]` (title "Location") | — |
| Job & org | Division / department | `client.homeDivision`, `client.homeDepartment` | `organizations[]` (title "Department"): `id`, `displayOrder`, `organizationId`, `title`, `value`, `valueDescription` | — |
| Job & org | Cost center | `client.projCostCenter`, `client.subCostCenter` | — | `cost_centers_info.defaults[]…`†, `cost_centers_info.limits[]…`† (6 fields) |
| Job & org | Manager / supervisor | `client.manager`, `client.reportsTo` | `assignedManager.*`† (9), `assignedSupervisor.*`† (9) | `managers[].index`†, `managers[].empl_ref.account_id`† |
| Job & org | Time clock ID | `client.clockNum` | `timeclockId` | — |
| Compensation | Pay group | `compensation.payGroup` | `payGroup` | — |
| Compensation | Pay frequency | `compensation.payPeriod`, `.payPeriodsPerWeek`, `.payPeriodInfo[].periodCode`, `.periodBase` | `payFrequency` | — |
| Compensation | Pay type | — | `payType` | `pay-info.pay_type.id` |
| Compensation | Annual salary | `compensation.annualPay`, `compensation.salary` | `annualSalary` | — |
| Compensation | Per-pay salary | — | `perPaySalary` | — |
| Compensation | Hourly rate | `compensation.hourlyPay`, `.hourlyPayRate`, `.hourlyPayPeriod` | `hourlyRate` | — |
| Compensation | Alternate pay rates | `compensation.altPayRate[]`, `.payRate2`, `.payRate3`, `.payRate4` | `payRates[]` (`payRateName`†, `rateValue`†) | — |
| Compensation | Standard hours | `compensation.standardHours`, `compensation.defaultHours` | `normalHours` | `pay-info.standard_work_day` |
| Compensation | Pay effective date | `compensation.effectiveDate` | `salaryEffectiveDate`, `updatedSalaryEffectiveDate`† | — |
| Metadata | Related links | — | `links[]…`, `nameAddress.id`, `nameAddress.links[]…`, `personal.id`, `personal.links[]…` | `_links.self`, `.country-fields`, `.demographics`, `.pay-info`, `.badges`, `.profiles`, `.hcm-profiles`†, `.hcm-fields`† |
| Metadata | Response status | `errorCode`, `errorMessage`, `infoMessage`, `updateMessage`, `extension` | — | — |

## No Match in Other Providers

| Provider | Section | Fields |
|---|---|---|
| PrismHR | `person` | `driverLicenseId`, `cobraSSN`, `cobraOnly`, `marriedDate`, `blind`, `taxZipCode`, `highlyCompensated`, `keyEmployee`, `overrideGeoCode`, `overrideGeoEndDate`, `driverState`, `driverLicenseExpireDate`, `driverLicenseClass`, `ohioFormC112`, `unincorporatedResidence`, `w2AddressLine1`, `w2AddressLine2`, `w2City`, `w2State`, `w2PostalCode`, `w2ElecForm`, `w2ElecFormDate`, `legacyEmployeeId`, `agricultureWorker`, `autoPolicy[]` (`autoInsurancePolicyId`†, `autoInsuranceCarrierName`†, `autoInsuranceHolderName`†, `autoInsurancePolicyStartDate`†, `autoInsurancePolicyExpDate`†), `vehicleDetails[]` (`vehicleMake`†, `vehicleModel`†, `vehicleYear`†, `vehicleAddDate`†, `vehicleRemoveDate`†, `vehicleRegNo`†), `personChecksum` |
| | `client` | `transferInfo[]` (`transferStatus`†, `transferEmployeeId`†, `transferClientId`†, `transferDate`†), `property[]` (`propertyCode`†, `propertyIssueDate`†, `propertySerialNumber`†, `propertyValue`†, `propertyReturnDate`†, `propertyComment`†), `hawaiiMedWaiver[]` (`medWaiverYear`†, `medWaiverReason`†), `cafeteriaPlan[]` (`planAmt`†, `planEffectiveDate`†), `officer`, `workCompOfficer`, `scorpOwner`, `businessOwner`, `newHireReportDate`, `employee1099`, `primaryEmailSource`, `benefitEmail`, `returnDate`, `probationDate`, `courtOrderMedical`, `childSpouseSupport`, `childSpouseArrears`, `handbookMailDate`, `handbookRecvDate`, `electronicOnboard`, `electronicOnboardDate`, `onboardInProgress`, `backgroundTest`, `backgroundTestDate`, `workersCompExempt`, `clientChecksum`, `workShift`, `workGroupCode`, `benefitGroup`, `retirementBenefitGroup`, `electronic1095C`, `applicantId` |
| | `compensation` | `payMethod`, `allocationTemplateId`, `payAllocation[]` (`locationCode`†, `percent`†, `job`†, `deptCode`†, `project`†, `division`†), `stateTax[]` (19 fields: `stateCode`, `nonResCertFiled`, `filingStatus`, `primaryAllowance`, `secondaryAllowance`, `exemptAmount`, `supplExemptAmount`, `overrideType`, `overrideAmount`, `reduceAddlWithholding`, `fixedWithholding`, `alternateCalc`, `stateW4Filed`, `stateW4Year`, `multipleJobs`, `dependents`, `otherIncome`, `deductions`, `nonResCertYear`), `localTax[]` (`authId`†, `filingStatus`†, `primaryAllowance`†, `nonResCert`†, `addlWithheld`†), `workShift`, `paidThruDate`, `eicFileStatus`, `fedFilingStatus`, `fedWithholdAllowance`, `fedOverrideType`, `fedOverrideAmt`, `fedTaxCalc`, `fedMultipleJobs`, `fedDependents`, `fedOtherIncome`, `fedDeductions`, `deliverCheckHome`, `autoAcceptTimeSheet`, `longPayTable`, `longBasisDate`, `lastChangePct`, `lastChangeAmt`, `lastPayDate`, `quartile`, `compaRatio`, `benefitsBasePay`, `perDiemPay`, `taxCreditEmp`, `autoPayCode`, `pensionStatus`, `profitSharing`, `eeImage[]` (`masterId`†, `verifyDateTime`†, `verifyUserId`†), `wagePlanCA`, `perfReviewLastDate`, `i9imageAudit[]` (`auditDate`†, `auditUser`†, `auditId`†, `auditStep`†), `perfReviewLastRating`, `compReviewNextDate`, `perfReviewLastTitle`, `fedW5Year`, `fedW5Filed`, `fedW4Filed`, `fedW4Year`, `lockIns[]` (`state`†, `stateDate`†, `authUser`†), `formI9RenewDate`, `notes`, `ficaExempt`, `benefitsPerHour`, `perfAgreement`, `payChangeLastDate`, `overrideWorkGeocode`, `familyMemberMI`, `probationCodeMO`, `electronicPayStub`, `healthInsVT`, `lastWorkedDate`, `irsLockInDate`, `nonResAlien`, `alienRegExpDate`, `benefitSalary`, `firstPayPeriodHours`, `compensationChecksum`, `providerNotifiedOn`, `alternateId`, `w8Filed` |
| | top level | `directDeposit`, `hsa`, `employeeEvents`, `health`, `skillsAndEducation`, `absenceJournalId`, `benefitEnrollmentCompleted`, `scheduledDeduction`, `newHireQuestions`, `enrollmentInProgress` (sections not requested in `options`; no content) |
| isolved | top level | `acaEmploymentStatus`, `employmentCategoryFullTimeEquivalent`, `enableSelfService`, `isManager`, `isRemoteWorker`, `isSupervisor`, `jobIsSeasonal`, `previousPunchLabors` (`id`†, `description`†, `links[]`†), `reciprocityRule`, `timecardPunchStatusDate`, `timecardPunchStatusIsIn`, `idType`†, `isPending`†, `jobGroup`†, `socCode`†, `taxExemptStatus`†, `updatedDisabledEffectiveDate`† |
| | `personal` | `faxNumber` |
| | lists and sections | `labors[]`† (4), `miscFields[]`† (2), `miscDataSets[]`† (6), `messages[]`† (3), `attachments[]`† (25), `team.*`† (16), `wotc.*`† (4), `directDeposits[]`† (12; same data as the direct deposit API) |
| UKG | top level | `photo_href`, `isPhotoUploaded`, `force_change_password`, `locked`, `timezone`, `add_to_new_hire_export`, `managed_cost_centers_enabled`, `managed_cost_centers_settings.allow_save_others_cost_centers`†, `secondary_email`† |
| | `first_screen` | `id` |
| | `phones` | `preferred_phone`† |
| | `dates` | `re_hired`† (optional), `started`, `frozen_benefit`†, `benefits`†, `retired`†, `custom_dates[].index`†, `custom_dates[].date`† |
| | `account_extra_fields[]` | `index`†, `values[].value`†, `values[].effective_from`† |
| | `time_entry_extra_fields[]` | `index`†, `value`† |
| | `hardware_settings` | `in_touch.security_level`, `in_touch.pin` |
| | `pay-info` | `ttoc[]`, `payroll_classification`, `job_change_reason_code.display_name`†, `shift_premium.id`†, `medical_eligibility`†, `dental_eligibility`†, `dependent_benefits_eligibility`†, `benefit_auto_enrollment_eligibility`†, `bank_account_number`†, `pay_grade.id`†, `pay_grade.parent.id`†, `.code`†, `.name`†, `gl_codes[].index`†, `gl_codes[].value`† |

## Findings

| Finding | Evidence |
|---|---|
| PrismHR live names differ from schema | Live `person.employerId[]`, `autoPolicy[]`, `client.hawaiiMedWaiver[]`; schema `employerIds[]`, `autoPolicies[]`, `hawaiiMedWaivers[]`; `compensation.payPeriodsPerWeek` is live only |
| UKG live fields not in schema | `ein_name`, `_links.country-fields` |
| UKG `address` is an object | Live sub-fields: `address_line_1`, `city`, `state`, `state_code`, `zip`, `country` |
| isolved organizations hold location and department | Live `organizations[]` titles: "Location", "Department" |
| UKG `employee_id` is the employee number | Live value `"1"`, separate from `id` |

## Matches to Verify

None.