# Tada AI — Live Data Exploration Log

## Setup

| Provider | Auth header sent on each request | Base URL source | Path added after base URL | Sign-in IDs used in request URLs |
| --- | --- | --- | --- | --- |
| PrismHR | `sessionId: <token>` | Sign-in `base_url` | (none) | `client_id` |
| isolved | `Authorization: Bearer <token>` | Sign-in `base_url` | `/api` | `client_id` + `legal_id` |
| UKG Ready | `Authorization: Bearer <token>` | Sign-in `base_url` | `/rest` | `company_id` |

- Sign-in: `POST https://tada-demo-provider-signin.onrender.com/signin`, header `X-API-Key`, body `{"tenant":"prism|isol|ukg"}`. Limit 30/min.
- Postman environment `TADA`: `api_key`, `<p>_base_url`, `<p>_token`, plus bare IDs `prism_client`, `prism_emp`, `isol_client`, `isol_legal`, `isol_emp`, `ukg_company`, `ukg_emp`, `ukg_prefix`.
- Sign-in post-response scripts refresh base URL and token automatically. They also save the company list as JSON in `prism_company`, `isol_company`, and `ukg_companies`.
- API key lives outside the repo; samples saved to `/Users/rutuja/Downloads/TADA/tada/samples/` (not in Git).

## Endpoint Results

Status = HTTP status. Data = `Has data` / `Empty` (empty body, list, or object). Source = `Saved example` (Postman "TADA collection") or `Log` (earlier manual run, no saved example).

### Employee List

| Provider | Endpoint | Status | Data | Source | Notes |
| --- | --- | --- | --- | --- | --- |
| PrismHR | `GET /employee/v1/getEmployeeList?clientId=` | 200 OK | Has data | Saved example | 16 employee IDs |
| isolved | `GET /api/clients/{clientId}/legals/{legalId}/employees` | 200 OK | Has data | Saved example | 20 employees; `nextPageUrl` null |
| UKG | `GET /rest/v2/companies/{cid}/employees` | 200 OK | Has data | Saved example | 103 employees |

### Employee Full Record

| Provider | Endpoint | Status | Data | Source | Notes |
| --- | --- | --- | --- | --- | --- |
| PrismHR | `GET /employee/v1/getEmployee?clientId=&employeeId=&options=Person,Client,Compensation,ContactInformation` | 200 OK | Has data | Saved example | `person`, `client`, `compensation`, `contactInformation` all populated |
| isolved | `GET /api/clients/{clientId}/legals/{legalId}/employees/{id}` | 200 OK | Has data | Saved example | `payGroup` is a name only ("Monthly") |
| isolved | `GET …/employees/{employeeId}/salaries` | 200 OK | Has data | Saved example | 1 salary record; holds `payGroup.id` (7627) |
| UKG (1 of 2) | `GET /rest/v2/companies/{cid}/employees/{aid}` | Not recorded | Has data | Log | Works after fixing `ukg_company` to bare ID |
| UKG (2 of 2) | `GET …/employees/{aid}/pay-info` | 200 OK | Has data | Saved example | Only IDs/classifications (`employee_type`, `pay_type`, `payroll_classification`); no pay rate |

### Direct Deposits

| Provider | Endpoint | Status | Data | Source | Notes |
| --- | --- | --- | --- | --- | --- |
| PrismHR | `getEmployee` with `options=DirectDeposit` | 200 OK | Empty | Saved example | `directDeposit.achVoucher` is `[]` |
| isolved | `GET …/employees/{employeeId}/directdeposits` | 200 OK | Has data | Saved example | 2 accounts |
| UKG | `GET …/employees/{aid}/direct-deposits` | 200 OK | Empty | Saved example | `deposits` is `[]` |

### Deductions

| Provider | Endpoint | Status | Data | Source | Notes |
| --- | --- | --- | --- | --- | --- |
| PrismHR | `GET /employee/v1/getScheduledDeductions?clientId=&employeeId=` | 200 OK | Has data | Saved example | 1 scheduled deduction (`CHAR`, status `I`) |
| isolved | `GET …/employees/{employeeId}/payItems` | 200 OK | Has data | Saved example | 41 pay items: 19 Deduction, 17 Memo Calc, 5 Earning |
| UKG | `GET …/employees/{aid}/deductions` | 404 Not Found | Empty | Log | "Unresolvable URL"; docs mark it dev |
| UKG | `GET /rest/v2/companies/{cid}/lookup/deduction-codes` | 200 OK | Has data | Saved example | 43 company deduction codes |
| UKG | `GET …/employees/{aid}/benefits` | 200 OK | Empty | Saved example | `benefits` is `[]` |

### Payroll Runs

| Provider | Endpoint | Status | Data | Source | Notes |
| --- | --- | --- | --- | --- | --- |
| PrismHR | `GET /payroll/v1/getBatchListByDate?…&dateType=PAY` | 200 OK | Has data | Saved example | 57 batches (37 COMP); batch 202513 is COMP |
| isolved | `GET …/payGroups/7627/payrolls` | 404 Not Found | Empty | Log | Log also notes it lists scheduled runs only |
| isolved | `GET …/paygroupId/7627/payrollRunHistory` | Not recorded | Empty | Log | No data |
| isolved | `GET …/paygroupId/7627/payrollRunHistory/byDate?startDate=2020-01-01&endDate=2026-12-31` | 404 Not Found | Empty | Saved example | Empty body |
| UKG | `GET /rest/v2/companies/{cid}/payrolls` | 200 OK | Has data | Saved example | 49 runs, all OPEN |

### Paychecks

| Provider | Endpoint | Status | Data | Source | Notes |
| --- | --- | --- | --- | --- | --- |
| PrismHR | `GET /payroll/v1/getPayrollVouchersForEmployee` | Not recorded | Empty | Log | Empty for tested employee |
| PrismHR | `GET /payroll/v1/getPayrollVoucherForBatch?batchId=202513` | 200 OK | Has data | Saved example | 6 vouchers, 6 employees, all status PRNT |
| isolved | `GET …/employees/{employeeId}/checks?includeDetails=true` | Not recorded | Empty | Log | Empty |
| isolved | `GET …/checks` with `filter.fromDate`/`filter.toDate` | Not recorded | Empty | Log | No data |
| isolved | `GET …/payGroups/7627/checks?filter.fromDate=2020-01-01&filter.toDate=2026-12-31` | 404 Not Found | Empty | Saved example | Empty body |
| UKG | `GET …/payrolls/{id}/pay-statements` | 200 OK | Empty | Saved example | `pay_statements` is `[]`; saved request uses payroll ID 35419520, which is not in the `/payrolls` list |

## Key Findings

| Topic | PrismHR | isolved | UKG Ready |
| --- | --- | --- | --- |
| Hierarchy | Client → Employee | Client → Legal → Employee | Company → Employee |
| URL style | Action-based, IDs in query | REST, IDs in path | REST, IDs in path |
| Payroll run term | Batch | Payroll (pay group) | Payroll |
| Paycheck term | Voucher | Check | Pay statement |
| Direct deposit | `getEmployee` option `DirectDeposit` | Own endpoint | Own endpoint |
| Compensation | `getEmployee` option `Compensation` | `/salaries` | Separate `/pay-info` |

- **PrismHR:** `getEmployee` returns only Person data unless `options` is set; SSN and DOB masked by default.
- **PrismHR:** paychecks come from `getPayrollVoucherForBatch`; the per-employee voucher endpoint was empty.
- **PrismHR:** `getScheduledDeductions` echoes `sessionId` in the response body; redact it before saving samples.
- **isolved:** employee record has `payGroup` as a name only; the ID comes from `/salaries`.
- **isolved:** `/payItems` mixes deductions, earnings, and memo calcs; filter on `payItemType = Deduction`.
- **isolved:** `/payGroups/{id}/payrolls` lists scheduled runs, not history; history is `/paygroupId/{id}/payrollRunHistory`.
- **isolved:** company-wide `/checks` defaults to today's date; date filters are `filter.fromDate` / `filter.toDate`.
- **UKG:** `base_url` already ends in `/ta`; the working prefix before `/v2` is `/rest`.
- **UKG:** `/pay-info` holds type IDs only, not a pay rate.
- **UKG:** deduction code IDs (from lookup) are not the IDs `/deductions/{id}` expects.
- **Postman:** environment variables must hold bare IDs, not JSON lists, or UKG returns "Company not found".

## Gaps to Document

| Provider | Gap | Evidence | Plan |
| --- | --- | --- | --- |
| isolved | No payroll runs | `payrollRunHistory` returns no data; `/byDate` returns 404 for pay group 7627 | Map from `isolved-v6.swagger.json` schemas; synthetic fixtures |
| isolved | No paychecks | Employee `/checks` empty; legal `/checks` no data; pay-group `/checks` with 2020–2026 range returns 404 | Map from schemas; synthetic fixtures |
| UKG | No employee deduction setup | `/employees/{aid}/deductions` returns "Unresolvable URL"; docs mark it dev; `/benefits` empty | Map from docs response sample; use deduction-codes lookup for categories |
| UKG | No pay statements | `/payrolls/{id}/pay-statements` empty; all runs OPEN; saved request used payroll ID 35419520, not in `/payrolls` list | Retry with an ID from `/payrolls`; else map from docs schema; synthetic fixtures |
| UKG | No direct deposits | `/direct-deposits` returns empty `deposits` for tested employee | Try other employees before logging a gap |
| PrismHR | No direct deposits | `getEmployee` `DirectDeposit` returns empty `achVoucher` for tested employee | Try other employees before logging a gap |

## Next Steps

- [x] Run the "Not yet checked" requests: full records, direct deposits, PrismHR and isolved deductions, UKG `pay-info`
- [x] Run PrismHR `getPayrollVoucherForBatch?batchId=202513`
- [x] Try UKG `…/employees/{aid}/benefits` for benefit-related deductions
- [ ] Save a UKG employee full record (part 1) example to the collection
- [ ] Retry UKG `pay-statements` with a payroll ID from `/payrolls`
- [ ] Save every response to `samples/` as `<provider>_<type>.json`
- [ ] Build one field-mapping table per data type (canonical field, PrismHR, isolved, UKG, notes)
- [ ] Copy confirmed gaps into `DECISIONS.md` → Provider Mappings & Gaps