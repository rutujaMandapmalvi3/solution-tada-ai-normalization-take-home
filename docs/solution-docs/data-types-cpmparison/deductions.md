# Deductions — Response Fields

All fields from each provider's deduction APIs, matched by meaning across providers. The README asks for two parts, mapped separately: **deduction setup** and **deductions recorded in payroll**.

| Part | Provider | Endpoint | Source |
| --- | --- | --- | --- |
| Setup | PrismHR | `GET /deductions/v1/getDeductions` | Saved response, employee J00809; fields under `employeeDeductions.deduction[]`; schema `DeductionResponse` |
| Setup | isolved | `GET …/employees/{employeeId}/payItems` | Saved response, employee 859139; list response; includes earnings and memo items; schema `EmployeePayItemModel` |
| Setup | UKG | `GET …/employees/{aid}/deductions` | Schema `schemas[132]` only (endpoint not available); fields under `deductions[]` |
| Setup | UKG | `GET …/lookup/deduction-codes` | Saved response; fields under `items[]`, prefixed `codes.`; schema `schemas[244]` |
| In payroll | PrismHR | `GET /payroll/v1/getPayrollVoucherForBatch` | Saved response, batch 202513; fields under `payrollVoucher[].deduction[]` and `.otherDeduction[]`; schema `PayrollVoucher` |
| In payroll | isolved | `GET …/employees/{employeeId}/checks/{id}` | Schema `CheckModel` only (no checks in demo account); fields under `deductions[]` |
| In payroll | UKG | `GET …/payrolls/{id}/pay-statements/{id}` | Schema `schemas[364]` only (no pay statements in demo account); fields under `deductions[]` |

- `.` marks a nested field; `[]` marks a list.
- † = in the schema but not in the live response.

## Part 1: Deduction Setup

### Matched Fields

| Field | PrismHR | isolved | UKG |
|---|---|---|---|
| Record ID | — | `id` | `id`† |
| Deduction code | `deductionCode` | `payItemCode` | `deduction.code`†, `codes.code` |
| Deduction catalog ID | — | `payItemId` | `codes.id` |
| Name / description | `description` | `payItemName` | `deduction.name`†, `codes.name` |
| Type | `deductionType` | `payItemType` | — |
| Calculation method | `deductionMethod`, `usePercent`, `basis` | `calcParams[].paramType` | — |
| Amount / rate | `amount` | `calcParams[].paramValue` | — |
| Frequency | `period` | `scheduleOverride` | — |
| Limit / maximum | `limit`†, `maximum`† | — | — |
| Start date | `startDate` | `startDate` | `effective_from`† |
| End date | `stopDate`† | `stopDate` | `effective_to`† |
| Benefit plan | `benefitPlanId` | — | — |
| Loan / garnishment reference | `loanOrGarnishId` | `referenceNumber` | — |
| Balance / arrears | `trackArrears` | `balance` | — |
| Employee link | — (request parameter) | `employeeId`, `employeeNumber`, `firstName`, `lastName` | — (URL path) |
| Related links | — | `links[].href`, `links[].rel`, `links[].method` | `_links.self`† |
| Response status | `errorCode`, `errorMessage`, `extension` | — | — |

### No Match in Other Providers

| Provider | Fields |
|---|---|
| PrismHR | `lastDedPerAdj`, `glOverrideAcct`, `mandatory`, `matchMethod`, `matchDescription`, `matchAmount`†, `detailsChecksum`†, `cutbackPayeeCode`, `rateTableId`, `rateTier`, `achOption` |
| isolved | `auditId`† |
| UKG | `sequence`†, `codes.external_id` |

## Part 2: Deductions Recorded in Payroll

### Matched Fields

| Field | PrismHR | isolved | UKG |
|---|---|---|---|
| Line ID | — | `id`† | `id`† |
| Deduction code | `deductCode`, `otherDeduction[].otherDeductCode`† | `itemCode`† | `deduction.code`† |
| Name / description | `deductDescription`, `otherDeduction[].otherDeductDescription`† | `itemDescription`† | `deduction.name`† |
| Type | `deductType` | — | `type_name`† |
| Employee amount (this paycheck) | `deductAmount`, `otherDeduction[].otherDeductAmount`† | `checkDollars`†, `currentDollars`† | `ee_amount`† |
| Employer amount | — | — | `er_amount`† |
| To-date totals | — | `ptdDollars`†, `mtdDollars`†, `qtdDollars`†, `ytdDollars`†, `ftdDollars`† | — |
| Benefit plan | `planId` | — | — |
| Related links | — | `links[]`† | — |

### No Match in Other Providers

| Provider | Fields |
|---|---|
| PrismHR | `deductUnionId`, `otherDeduction[].otherDeductOneTimeSwitch`† |
| isolved | `sequence`† |
| UKG | `deduction.external_id`†, `date_range_from`†, `date_range_to`†, `quantity`†, `base_rate`†, `batch.id`†, `batch.display_name`†, `vendor.id`†, `vendor.name`†, `cost_centers[].index`†, `cost_centers[].value.id`†, `workers_comp_code.external_id`† |

### Related Fields in Other Data Types

Employee contributions recorded on paychecks for benefits and retirement; they belong to the Paychecks mapping.

| Provider | Fields |
|---|---|
| PrismHR | `benefit[].empDeduct`, `retirement.*` (e.g. `electiveContributionsPreTax`, `rothContributionsPostTax`, `employeeRetirementLoanPayments`) |
| isolved | `benefits[].checkEmployeeDeduction`, `.currentEmployeeDeduction`, `.ptdEmployeeDeduction`, `.mtdEmployeeDeduction`, `.qtdEmployeeDeduction`, `.ytdEmployeeDeduction`, `.ftdEmployeeDeduction` |

## Findings

| Finding | Evidence |
|---|---|
| isolved returns a field not in the schema | Live `balance` is not in `EmployeePayItemModel` |
| UKG deduction codes return a field not in the schema | Live `items[].id` is not in `schemas[244]` |
| isolved and UKG payroll deductions have no live data | No checks or pay statements in the demo accounts |
| isolved `scheduleOverride` codes match PrismHR `period` digits | `GET /api/system/payItemSchedules`: e.g. `K` = 1st–4th pay of month (PrismHR `1234`), `Y` = every pay (PrismHR `12345`) |
| Loan / garnishment reference cannot be confirmed | PrismHR `loanOrGarnishId` and isolved `referenceNumber` are empty in live data; isolved describes it only as "reference number" |
| isolved paycheck deduction amounts are undefined | `checkDollars` and `currentDollars` have no descriptions and no live data |

## Matches to Verify

None.