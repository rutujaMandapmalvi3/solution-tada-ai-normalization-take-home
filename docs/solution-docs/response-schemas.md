# Response Schemas — Postman-Tested Endpoints

Each row maps one endpoint tried in Postman to the response schema for its HTTP 200 response in the contract. Rows are grouped by data type so all three providers sit together.

| Provider | Contract file | Where schemas live | Name prefix |
| --- | --- | --- | --- |
| PrismHR | `contracts/prismhr/openapi/prismhr-2025.09.openapi.json` | `components.schemas.<Name>` | `#/components/schemas/` |
| isolved | `contracts/isolved/openapi/isolved-v6.swagger.json` | `definitions.<Name>` | `#/definitions/AOS.PayrollOffice.RestAPI.Models.` (dropped below) |
| UKG Ready | `contracts/ukg-ready/reference-schemas.json` | `schemas[<index>].schema` | None; rows give the list index and source page |

- Shape = what the top level of the response is.
- Fields in `name (Schema)` form point to another schema in the same file.
- Common path prefixes, shortened to `…` in the tables:
  - isolved: `/api/clients/{clientId}/legals/{legalId}`
  - UKG: `/rest/v2/companies/{cid}`; source pages are under `contracts/ukg-ready/reference-docs/res/`

## 1. Employee List

| Provider | Endpoint | Response schema | Shape | Top-level fields |
| --- | --- | --- | --- | --- |
| PrismHR | `GET /employee/v1/getEmployeeList` | `EmployeePendingApprovalResponse` | Object | \*`errorCode`, \*`errorMessage`, `extension (Extension)`, `employeeList (EmployeeList)` |
| isolved | `GET …/employees` | `PagedModelItemListOfEmployeeModel` | Object | `nextPageUrl`, `previousPageUrl`, `results (array of EmployeeModel)`, `totalItems`, `totalPages` |
| UKG | `GET …/employees` | `schemas[104]`, `__v2__companies__(cid)__employees.html` | Object | \*`employees[]` |

## 2. Employee Full Record

| Provider | Endpoint | Response schema | Shape | Top-level fields |
| --- | --- | --- | --- | --- |
| PrismHR | `GET /employee/v1/getEmployee` (`options=Person,Client,Compensation,ContactInformation`) | `EmployeeAndEmployeeBySsnResponse` | Object | \*`errorCode`, \*`errorMessage`, `extension (Extension)`, `employee (array of Employee)`, `infoMessage`, `updateMessage` |
| isolved | `GET …/employees/{id}?includeOrganizations=true&includeAlternateRates=true&includeLabors=true&includeMiscFields=true&includeMiscDataSets=true` | `EmployeeModel` | Object | About 100 fields, e.g. `nameAddress (EmployeeNameAddressModel)`, `personal (EmployeePersonalModel)`, `payRates (array of EmployeePayRateModel)`, `directDeposits (array of EmployeeDirectDepositModel)`, `taxes (EmployeeTaxInfoModel)`, `organizations (array of EmployeeOrganizationModel)` |
| UKG (1 of 2) | `GET …/employees/{aid}` | `schemas[106]`, `__v2__companies__(cid)__employees__(aid).html` | Object | `id`, \*`username`, \*`first_name`, \*`last_name`, `employee_id`, `status`, `address`, `mailing_address`, `ein{}`, `phones{}`, `managers[]`, `primary_email`, `social_security`, … |
| UKG (2 of 2) | `GET …/employees/{aid}/pay-info` | `schemas[159]`, `__v2__companies__(cid)__employees__(aid)__pay-info.html` | Object | `default_job{}`, `job_change_reason_code{}`, `job_last_changed`, `standard_work_day`, `employee_type{}`, `pay_type{}`, `shift_premium{}`, `medical_eligibility`, `dental_eligibility`, `dependent_benefits_eligibility`, `benefit_auto_enrollment_eligibility`, `eeo_classification`, `eeo4_classification`, `eeo4_function`, `workers_comp_code{}`, `union{}`, \*`payroll_classification`, `bank_account_number`, `pay_grade{}`, `gl_codes[]`, `ttoc[]` |

## 3. Compensation

| Provider | Endpoint | Response schema | Shape | Top-level fields |
| --- | --- | --- | --- | --- |
| PrismHR | `GET /employee/v1/getEmployee` (`options=Compensation`) | `EmployeeAndEmployeeBySsnResponse` | Object | Same as Employee Full Record; data sits in `employee[].compensation` |
| isolved | `GET …/employees/{employeeId}/salaries` | `EmployeeSalaryModel` | Array | `id`, `changeReason`, `comments`, \*`effectiveDate`, \*`frequency`, `hourlyRate`, `isInactive`, `lifeEvent`, `normalHours`, \*`payGroup`, \*`payType`, `perPaySalary`, `seasons`, `links` |
| UKG | `GET …/employees/{aid}/compensation/history` | `schemas[122]`, `__v2__companies__(cid)__employees__(aid)__compensation__history.html` | Object | \*`compensations[]` (each: `id`, \*`employee`, \*`effective_from`, \*`amount`, `hourly_pay`, \*`amount_period`, \*`time`, \*`time_period`, `num_pp_in_year`, \*`currency`, `_links`) |

## 4. Direct Deposits

| Provider | Endpoint | Response schema | Shape | Top-level fields |
| --- | --- | --- | --- | --- |
| PrismHR | `GET /employee/v1/getEmployee` (`options=DirectDeposit`) | `EmployeeAndEmployeeBySsnResponse` | Object | Same as Employee Full Record; data sits in `employee[].directDeposit` |
| isolved | `GET …/employees/{employeeId}/directdeposits` | `EmployeeDirectDepositModel` | Array | `id`, \*`accountNumber`, \*`accountType`, `amount`, `bankName`, `description`, \*`frequency`, `percent`, \*`routingNumber`, \*`sequenceNumber`, \*`status`, `links` |
| UKG | `GET …/employees/{aid}/direct-deposits` | `schemas[137]`, `__v2__companies__(cid)__employees__(aid)__direct-deposits.html` | Object | \*`deposits[]`, \*`_links{}`, `_total_count`, `_routing_type`, `is_eligible_for_paypal` |

## 5. Deductions

| Provider | Endpoint | Response schema | Shape | Top-level fields |
| --- | --- | --- | --- | --- |
| PrismHR (setup) | `GET /deductions/v1/getDeductions` | `DeductionResponse` | Object | \*`errorCode`, \*`errorMessage`, `extension (Extension)`, `employeeDeductions (EmployeeDeductions)`, which holds `deduction[]` |
| PrismHR (taken in payroll) | `GET /payroll/v1/getPayrollVoucherForBatch` | `PayrollResponseWithPagination` | Object | See Paychecks; each voucher lists `deduction[]` |
| isolved | `GET …/employees/{employeeId}/payItems` | `EmployeePayItemModel` | Array | `id`, `auditId`, `calcParams (array of EmployeePayItemCalcParamModel)`, `employeeId`, `employeeNumber`, `firstName`, `lastName`, `payItemCode`, `payItemId`, \*`payItemName`, `payItemType`, `referenceNumber`, `scheduleOverride`, `startDate`, `stopDate`, `links` |
| isolved (taken in payroll) | `GET …/employees/{employeeId}/checks/{id}` | `CheckModel` | Object | Check details; deductions sit in `deductions[]` |
| UKG (taken in payroll) | `GET …/payrolls/{id}/pay-statements/{id}` | `schemas[364]`, `__v2__companies__(cid)__payrolls__(id)__pay-statements__(id).html` | Object | Pay statement details; deductions sit in `deductions[]` |
| UKG | `GET …/employees/{aid}/deductions` | `schemas[132]`, `__v2__companies__(cid)__employees__(aid)__deductions.html` | Object | \*`deductions[]` |
| UKG | `GET …/employees/{aid}/benefits` | `schemas[119]`, `__v2__companies__(cid)__employees__(aid)__benefits.html` | Object | \*`benefits[]` |
| UKG | `GET …/lookup/deduction-codes` | `schemas[244]`, `__v2__companies__(cid)__lookup__deduction-codes.html` | Object | \*`items[]` |

## 6. Payroll Runs

| Provider | Endpoint | Response schema | Shape | Top-level fields |
| --- | --- | --- | --- | --- |
| PrismHR | `GET /payroll/v1/getBatchListByDate` | `BatchByDateResponse` | Object | \*`errorCode`, \*`errorMessage`, `extension (Extension)`, `batchList (array of BatchList)` |
| isolved (scheduled) | `GET …/payGroups/{payGroupId}/payrolls` | `PayGroupPayrollSummaryModel` | Array | `id`, `impoundDate`, `payDate`, `payOfMonth`, `payrollType`, `periodBeginDate`, `periodEndDate`, `periodNumber`, `runDate`, `scheduledPayDate`, `scheduledRunDate` |
| isolved (history) | `GET …/paygroupId/{paygroupId}/payrollRunHistory` | `PayrollRunHistoryModel` | Array | `id`, `impoundDate`, `inputMethod`, `payDate`, `payOfTheMonth`, `payPeriod`, `payrollRunType`, `periodBeginDate`, `periodEndDate`, `processApprovedBy`, `processedBy`, `regularCheckAutoPay`, `runDate`, `runNumber`, `runTime`, `scheduledPayDate`, `scheduledRunDate`, `status`, `submittedBy`, `submittedDate`, `submittedTime`, `suppressPayStubEmailAlert` |
| isolved (history) | `GET …/paygroupId/{paygroupId}/payrollRunHistory/byDate` | `PayrollRunHistoryModel` | Array | Same as above |
| isolved (employee) | `GET …/employees/{employeeId}/payroll` | `Payroll.PayrollModel` | Array | `id`, `calculatedPayDate`, `payDate`, `payrollHistoryDescription`, `payrollTypeDescription`, `periodBeginDate`, `periodEndDate`, `runDate`, `runNumber`, `scheduledPayDate`, `scheduledRunDate`, `links` |
| UKG | `GET …/payrolls` | `schemas[358]`, `__v2__companies__(cid)__payrolls.html` | Object | \*`payrolls[]` |

## 7. Paychecks

| Provider | Endpoint | Response schema | Shape | Top-level fields |
| --- | --- | --- | --- | --- |
| PrismHR | `GET /payroll/v1/getPayrollVoucherForBatch` | `PayrollResponseWithPagination` | Object | \*`errorCode`, \*`errorMessage`, `extension (Extension)`, `payrollVouchers (array of PayrollVoucher)`, `total`, `startpage`, `count` |
| PrismHR | `GET /payroll/v1/getPayrollVouchersForEmployee` | `PayrollResponseWithPagination` | Object | Same as above |
| isolved | `GET …/employees/{employeeId}/checks` | `PagedModelItemListOfCheckModel` | Object | `nextPageUrl`, `previousPageUrl`, `results (array of CheckModel)`, `totalItems`, `totalPages` |
| isolved | `GET …/checks` | `PagedModelItemListOfCheckModel` | Object | Same as above |
| isolved | `GET …/payGroups/{payGroupId}/checks` | `PagedModelItemListOfCheckModel` | Object | Same as above |
| UKG | `GET …/payrolls/{id}/pay-statements` | `schemas[362]`, `__v2__companies__(cid)__payrolls__(id)__pay-statements.html` | Object | \*`pay_statements[]` |

## Contract vs Live Mismatches

| Provider | Endpoint | Contract says | Live sample has |
| --- | --- | --- | --- |
| PrismHR | `getPayrollVoucherForBatch` | `payrollVouchers` (plural) | `payrollVoucher` (singular) |
| PrismHR | `getEmployeeList` | Items are "employee ID and the pending change to employee's status" | Plain IDs, e.g. `"A00576"` |
| PrismHR | `getEmployee` | `employerIds[]`, `autoPolicies[]`, `hawaiiMedWaivers[]` | `employerId[]`, `autoPolicy[]`, `hawaiiMedWaiver[]` |
| UKG | `…/employees/{aid}` | No `ein_name` or `_links.country-fields` | Both present |
| UKG | `…/employees/{aid}/pay-info` | 21 fields incl. `default_job`, `pay_grade`, eligibility flags | 7 fields (`standard_work_day`, `employee_type`, `pay_type`, `eeo4_classification`, `eeo4_function`, `ttoc`, `payroll_classification`) |