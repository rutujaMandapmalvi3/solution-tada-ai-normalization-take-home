# Payroll — Response Fields

Part 1: payroll runs. Part 2: paychecks. Fields matched by meaning across providers.

| Provider | Endpoint | Source |
| --- | --- | --- |
| PrismHR | `GET /payroll/v1/getBatchListByDate` (`dateType=PAY`) | Saved response (57 batches); fields under `batchList[]`; schema `BatchByDateResponse` |
| isolved | `GET …/paygroupId/{paygroupId}/payrollRunHistory/byDate` | Schema `PayrollRunHistoryModel` only (endpoint returns 404; no payroll runs in demo account) |
| UKG | `GET …/payrolls` | Saved response (49 payrolls); fields under `payrolls[]`; schema `schemas[358]` |

- `.` marks a nested field; `[]` marks a list.
- † = in the schema but not in the live response.

## Matched Fields

| Field | PrismHR | isolved | UKG |
|---|---|---|---|
| Run ID | `batchId` | `id`† | `id` |
| Run number | — | `runNumber`† | — |
| Run name | — | — | `name` |
| Run type | `batchType` | `payrollRunType`† | `type.id`, `type.display_name` |
| Status | `batchStatus` | `status`† | `status` |
| Pay date | `payDate` | `payDate`† | `pay_date` |
| Scheduled pay date | — | `scheduledPayDate`† | — |
| Period start | `payGroup[].payPeriodStartDate` | `periodBeginDate`† | `start_date` |
| Period end | `payGroup[].payPeriodEndDate` | `periodEndDate`† | `end_date` |
| Pay group | `payGroup[].payGroupId` | — (URL path) | — |
| Run date | — | `runDate`†, `runTime`† | — |
| Scheduled run date | — | `scheduledRunDate`† | `sch_submit_date_time`† |
| Employer / legal entity | — | — (URL path) | `ein.id`, `ein.ein_name`, `ein.ein_tax_id`, `ein.ein_country_id` |
| Related links | — | — | `_links.self` |
| Response status | `errorCode`, `errorMessage`, `extension` | — | — |

## No Match in Other Providers

| Provider | Fields |
|---|---|
| PrismHR | `payGroup[].weeksWorked`, `payGroup[].deductPeriod` |
| isolved | `payOfTheMonth`†, `impoundDate`†, `inputMethod`†, `payPeriod`†, `regularCheckAutoPay`†, `suppressPayStubEmailAlert`†, `submittedBy`†, `submittedDate`†, `submittedTime`†, `processedBy`†, `processApprovedBy`† |
| UKG | `billable`, `direct_deposit_date`†, `invoice_generator_id`†, `adjustment_grab_YTD_from_payroll_id`†, `dflt_pay_statement_type_id`†, `dflt_pay_stub_note`† |

## Findings

| Finding | Evidence |
|---|---|
| PrismHR period dates sit per pay group, not per run | `payGroup[]` holds `payPeriodStartDate`, `payPeriodEndDate`; one batch can list several pay groups |
| UKG returns a field not in the schema | Live `ein.ein_country_id` is not in `schemas[358]` |
| isolved payroll runs have no live data | `payrollRunHistory/byDate` returns 404 |
| PrismHR `deductPeriod` and isolved `payOfTheMonth` differ | PrismHR is a number (0–5); isolved is a schedule description name |
| Scheduled run date cannot be confirmed | isolved `scheduledRunDate` has no live data; UKG `sch_submit_date_time` is not returned and documented only as a date format |

## Matches to Verify

None.
---

# Part 2: Paychecks

| Provider | Endpoint | Source |
| --- | --- | --- |
| PrismHR | `GET /payroll/v1/getPayrollVoucherForBatch` | Saved response, batch 202513 (6 vouchers); fields under `payrollVoucher[]`; schema `PayrollVoucher` |
| isolved | `GET …/payGroups/{payGroupId}/checks` | Schema `CheckModel` only (no checks in demo account); fields under `results[]` |
| UKG | `GET …/payrolls/{id}/pay-statements` + `…/pay-statements/{id}` | Schemas `schemas[362]` (list) and `schemas[364]` (details) only (no pay statements in demo account) |

- PrismHR live data has no † fields; null/empty sections are marked "(null)".
- Deduction lines are mapped in `deductions.md` Part 2; only listed here.

## Matched Fields

| Field | PrismHR | isolved | UKG |
|---|---|---|---|
| Paycheck ID | `voucherId` | `id`† | `id`† |
| Check number | `checkNumber`, `checkNum` | `checkNumber`† | — |
| Employee link | `employeeId` | `employeeId`†, `employeeNumber`† | `employee.account_id`† |
| Payroll run link | `batchId` | `payrollRunNumber`† + `checkDate`† (pay group from URL) | — (URL path) |
| Pay group | `payGroup` | — (URL path) | — |
| Status | `status` | — | `status`† |
| Type | `type` | `checkTypeDescription`†, `payrollRunType`† | `type.id`†, `type.display_name`† |
| Pay date | `payDate` | `checkDate`† | `pay_date`† |
| Period start | `payPeriodStart` | `periodBeginDate`† | `pay_period_start`† |
| Period end | `payPeriodEnd` | `periodEndDate`† | `pay_period_end`† |
| Gross pay | `totalEarnings` | `grossPay`†, `grossWages`† | — |
| Net pay | `netPay` | `netPay`† | — |
| Paper check amount | `checkAmt` | `checkAmount`† | — |
| Direct deposit total | — | `directDepositAmount`† | — |
| Related links | — | `links[]`† | `_links.self`† |
| Response status / paging | `errorCode`, `errorMessage`, `extension`, `total`, `startpage`, `count` | `nextPageUrl`, `previousPageUrl`, `totalItems`, `totalPages` | — |

## Matched Lists

| List | PrismHR | isolved | UKG |
|---|---|---|---|
| Earnings | `earning[]`, `otherEarningsDetail[]` | `earnings[]`† | `earnings[]`† |
| Employee taxes | `employeeTax[]` | `taxes[]`† (`isEmployeeTax` = true) | `taxes[]`† (`ee_*` fields) |
| Employer taxes | `companyTax[]` | `taxes[]`† (`isEmployeeTax` = false) | `taxes[]`† (`er_*` fields) |
| Deductions | `deduction[]`, `otherDeduction[]` (empty) | `deductions[]`†, `garnishments[]`† | `deductions[]`† |
| Direct deposits | `directDeposit[]` | `directDeposits[]`† | `payments[]`† (`type_name` = "Direct Deposit") |
| Benefits | `benefit[]` | `benefits[]`† | — |
| Employer contributions | `employerContributions[]` (null) | `benefits[].checkEmployerContribution`† | `deductions[].er_amount`† |

### Earnings Lines

| Field | PrismHR | isolved | UKG |
|---|---|---|---|
| Line ID | — | `id`† | `id`† |
| Earning code | `payCode`, `otherEarnCode` | `itemCode`† | `earning.code`† |
| Name / description | `otherEarnsDesc` | `itemDescription`† | `earning.name`† |
| Hours | `hoursUnits`, `hoursWorked` | `checkHours`†, `currentHours`† | `hours`† |
| Rate | `unitRate` | — | `base_rate`† |
| Amount | `payAmount`, `otherEarnAmount` | `checkDollars`†, `currentDollars`† | `ee_amount`† |
| Date | `chargeDate` | — | `date_range_from`†, `date_range_to`† |
| Shift | `shift` | — | `shift.id`†, `shift.name`† |
| Job / org | `jobCode`, `division`, `department`, `location` | `labors[]`† | `cost_centers[]`† |
| Workers' comp code | `workComp` | — | `workers_comp_code.external_id`† |

### Tax Lines

| Field | PrismHR | isolved | UKG |
|---|---|---|---|
| Line ID | — | `id`† | `id`† |
| Tax code | `empTaxDeductCode`, `comTaxDeductCode` | `itemCode`† | `company_tax.code`† |
| Name / description | `empTaxDeductCodeDesc`, `comTaxDeductCodeDesc` | `itemDescription`† | `company_tax.name`†, `company_tax.abbrev`† |
| Tax amount | `empTaxAmount`, `comTaxAmount` | `checkDollars`†, `currentDollars`† | `ee_amount`†, `er_amount`† |
| Taxable wages | `empTaxableAmount`, `comTaxableAmount` | `checkTaxableWages`†, `currentTaxableWages`† | `ee_subject_wage`†, `er_subject_wage`† |

### Direct Deposit Lines

| Field | PrismHR | isolved | UKG |
|---|---|---|---|
| Line ID | — | `id`† | `id`† |
| Account number | `accountNum` (masked) | `account`† | — |
| Routing number | `transitNum` | — | — |
| Amount | `amount` | `depositAmount`† | `ee_amount`† |
| Status / description | `status` | `itemDescription`† | `type_name`† |

## No Match in Other Providers

| Provider | Fields |
|---|---|
| PrismHR | `payPeriod`, `dateProcessed`, `voidDate`, `voidVoucherId`, `fitTaxableAmount`, `earnAmount`, `otherEarnAmount`, `bankAccount`, `checkAccountACH`, `payStubType`, `isManualCheck`, `hsaPeoMatch`, `importBatchNo`, `wcHomeClass`, `wcState`, `workerComp[]` (5), `fsaMatch[]` (empty), `retirement` (null), `glAcctDistribution` (null), `asoClientGLAcctDistribution` (null), `taxFilingStatus` (null), `wcInformation` (null), `fromArrears` (null), `toArrears` (null), `earning[].payClass`, `.payClassDescription`, `.glCode`, `.projWork`, `.projPhase`, `employeeTax[].empOverLimitAmount`, `companyTax[].comTaxEntity`, `.comExemptAmount`, `.comShelteredAmount`, `.comTaxType`, `.comOvrLimit`, `.comTaxRate`, `.comClientSutaRpt`, `benefit[].premiumAmt`, `.empContrib`, `.coveragePeriod`, `.adjRef`, `.premiumCost` |
| isolved | `checkSequence`†, `voucherNumber`†, `reissueCheckDate`†, `reissueCheckNumber`†, `employeeName`†, `employeeSSN`†, `employeeAddress1`†, `employeeAddress2`†, `employeeCity`†, `employeeState`†, `employeeZipCode`†, `employeeFederalFilingStatus`†, `employeeFederalExemptions`†, `employeeFederalAddlAmountOrPercent`†, `employeeStateFilingStatus`†, `employeeStateExemptions`†, `employeeStateAddlAmountOrPercent`†, `employeeOrganizations[]`†, `isRemoteWorker`†, `legalCompanyName`†, `vertexResidentGeoCode`†, `vertexWorkGeoCode`†, `vertexSchoolDistrictCode`†, `accruals[]`† (6), `taxCategories[]`† (17), to-date totals on earnings/taxes (`ptd*`, `mtd*`, `qtd*`, `ytd*`, `ftd*`)†, `earnings[].isMemoEarning`†, `.sequence`†, `taxes[].sequence`† |
| UKG | `messages[]`† (`id`, `type_name`, `message.text`, `message.severity`, `batch.*`), `payments[].hours`†, `.quantity`†, `.batch.*`†, `earnings[].type_name`†, `.quantity`†, `.batch.*`†, `taxes[].type_name`†, `.batch.*`†, `.ee_gross_wage`†, `.ee_gross_subject_wage`†, `.er_gross_wage`†, `.er_gross_subject_wage`† |

## Findings

| Finding | Evidence |
|---|---|
| PrismHR live fields not in schema | `isManualCheck`, `hsaPeoMatch` |
| PrismHR `checkAmt` is the paper check amount only | `0` when paid by direct deposit; `761.74` (= `netPay`) for voucher 003152, which has no `directDeposit[]` |
| PrismHR `checkNum` is null | Check number is in `checkNumber` |
| PrismHR deposit account numbers are masked | Live `accountNum` = `***********` |
| PrismHR voucher carries the employee and run links | `employeeId`, `batchId` in each voucher |
| isolved check has no payroll run ID | Only `payrollRunNumber`; pay group comes from the URL |
| UKG list endpoint returns only the paycheck header | `schemas[362]`: `id`, `employee`, `pay_date`, `status`, `type`, period dates; earnings, taxes, deductions only in `schemas[364]` |
| UKG pay statement has no gross pay, net pay or check number | Not in `schemas[362]` or `schemas[364]` |
| isolved and UKG paychecks have no live data | No checks or pay statements in the demo accounts |
| isolved run number is not unique alone | `PayrollRunHistoryModel.runNumber` = "Run sequence number"; link = pay group + `checkDate` + `payrollRunNumber` → run `payDate` + `runNumber` |
| isolved pay-group checks may not include details | `…/payGroups/{id}/checks` has no `includeDetails` parameter; `…/employees/{id}/checks` has it ("will include deductions and earning") |
| UKG `payments[]` = how the paycheck was paid | XML sample (`…/pay-statements/{id}` page): `type_name` "Check" and "Direct Deposit" (`ee_amount` 76.92) |
| UKG `ee_subject_wage` = taxable wages | XML sample, FIT line: `ee_gross_wage` 100, `ee_subject_wage` 85 |

## Matches to Verify

| Item | Why |
|---|---|
| isolved `checkDollars` vs `currentDollars` | No description anywhere in `isolved-v6.swagger.json`; needs an assumption (same open item as `deductions.md`) |