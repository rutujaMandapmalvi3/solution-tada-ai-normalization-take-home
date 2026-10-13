# Decisions & Assumptions — So Far
Which provider APIs this solution uses and why, plus related decisions, assumptions and findings.
## Chosen APIs

| Data type | Provider | Endpoint | Why chosen |
| --- | --- | --- | --- |
| Employee list | PrismHR | `GET /employee/v1/getEmployeeList` | Returns all employee IDs for a client |
| Employee list | isolved | `GET …/employees` | Returns all employees for a company, with full details |
| Employee list | UKG | `GET …/employees` | Returns all employees for a company |
| Employee full record | PrismHR | `GET /employee/v1/getEmployee` (`options=Person,Client,Compensation,ContactInformation`) | Returns one employee's full record when these options are set |
| Employee full record | isolved | `GET …/employees/{id}?includeOrganizations=true&includeAlternateRates=true&includeLabors=true&includeMiscFields=true&includeMiscDataSets=true` | Returns one employee's full record; the flags add organization, extra pay rate, labor and custom fields |
| Employee full record | UKG | `GET …/employees/{aid}` + `…/pay-info` | Together return the employee's profile and job details |
| Compensation | PrismHR | `getEmployee` (`options=Compensation`) | Returns the employee's pay details |
| Compensation | isolved | `GET …/employees/{employeeId}/salaries` | Returns the employee's pay rates and pay group |
| Compensation | UKG | `GET …/employees/{aid}/compensation/history` | Returns the employee's pay details history |
| Direct deposits | PrismHR | `getEmployee` (`options=DirectDeposit`) | Returns the employee's direct deposit setup |
| Direct deposits | isolved | `GET …/employees/{employeeId}/directdeposits` | Returns the employee's direct deposit accounts |
| Direct deposits | UKG | `GET …/employees/{aid}/direct-deposits` | Returns the employee's direct deposit accounts |
| Deductions (setup) | PrismHR | `GET /deductions/v1/getDeductions` | Returns the rules for the employee's payroll deductions |
| Deductions (taken in payroll) | PrismHR | `GET /payroll/v1/getPayrollVoucherForBatch` | Paychecks list the deductions taken from each payment |
| Deductions | isolved | `GET …/employees/{employeeId}/payItems` | Returns the employee's deductions and other pay items |
| Deductions | UKG | `GET …/lookup/deduction-codes` | Employee deductions are not available; returns the company's deduction types |
| Payroll runs | PrismHR | `GET /payroll/v1/getBatchListByDate` (`dateType=PAY`) | Returns payroll runs within a pay date range |
| Payroll runs | isolved | `GET …/paygroupId/{paygroupId}/payrollRunHistory/byDate` | Returns completed payroll runs for a pay group within a date range |
| Payroll runs | UKG | `GET …/payrolls` | Returns the company's payroll runs |
| Paychecks | PrismHR | `GET /payroll/v1/getPayrollVoucherForBatch` | Returns all paychecks for a payroll run |
| Paychecks | isolved | `GET …/payGroups/{payGroupId}/checks` (`filter.fromDate`, `filter.toDate`) | Returns all paychecks for a pay group within a date range |
| Paychecks | UKG | `GET …/payrolls/{id}/pay-statements` | Returns all paychecks for a payroll run |

`…` = `/api/clients/{clientId}/legals/{legalId}` (isolved) or `/rest/v2/companies/{cid}` (UKG).

## Other Decisions

| Decision | Reason |
| --- | --- |
| Use the base URL returned by sign-in | It points to the demo environment |
| Skip isolved endpoints built for third-party partners | They return less data than the standard endpoints |
| Map data types with no live data from the documentation | Some demo accounts have no data for them |
| Request the isolved full record with organization, extra pay rate, labor and custom field flags | Without them, those sections are not returned |
| Keep only isolved pay items whose `payItemType` is `Deduction` | The endpoint also returns earnings and memo items (sample: 19 deductions, 17 memo, 5 earnings) |

## Assumptions

| Assumption | Basis |
| --- | --- |
| PrismHR "voucher" is a paycheck | `components.schemas.PayrollVoucher` field descriptions: `checkNumber` "paycheck number", `checkAmt` "paycheck amount", `netPay` "net pay amount from employee's paycheck" |
| isolved "check" is a paycheck | `definitions.AOS.PayrollOffice.RestAPI.Models.CheckModel`: described as "Represents a Check"; fields `checkNumber`, `checkAmount`, `grossPay`, `netPay` |
| UKG "pay statement" is a paycheck | `reference-schemas.json` `schemas[362]` (pay-statements page): one record per `employee` per `pay_date`, with `pay_period_start` and `pay_period_end` |
| PrismHR "batch" is a payroll run | `components.schemas.BatchList` field descriptions: `batchId` "payroll batch identifier", `payDate` "pay date associated with this batch" |
| isolved "payroll run history" is a payroll run | `definitions.AOS.PayrollOffice.RestAPI.Models.PayrollRunHistoryModel` field descriptions: `runDate` "Date when the payroll was run", `status` "Status of the payroll" |
| UKG "payroll" is a payroll run | `reference-schemas.json` `schemas[358]` (payrolls page): fields `pay_date`, `start_date`, `end_date`, `status`; its pay statements sit under `/payrolls/{id}/pay-statements` |
| Missing payroll data reflects the demo account, not an API error | The requests succeeded but returned no records |

## Findings

| Finding | Evidence |
| --- | --- |
| UKG's employee deductions endpoint is not available | Returns "not found"; documentation marks it as in development |
| Live responses differ from the documentation | PrismHR returns `payrollVoucher`, not `payrollVouchers`, and `employerId[]`, `autoPolicy[]`, `hawaiiMedWaiver[]` instead of the documented plural names; UKG `pay-info` returns 7 of 21 documented fields; UKG employee record returns `ein_name` and `_links.country-fields`, which are not documented |
| PrismHR `getScheduledDeductions` returns only one-time or temporary deductions | Its description excludes standard deductions and garnishments |
| UKG `pay-info` has no pay rate or salary | Live response has 7 fields, none with pay amounts |
| isolved employee payrolls endpoint returns no data | `…/employees/{employeeId}/payroll` returns 404 |
| The isolved demo account has no paychecks | Company-wide, pay-group and per-employee check requests return "not found"; paycheck details are mapped from the documentation |