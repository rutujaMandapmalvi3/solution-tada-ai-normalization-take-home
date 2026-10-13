# Payroll Runs — Response Fields

All fields from each provider's payroll run API, matched by meaning across providers.

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