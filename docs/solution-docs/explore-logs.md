# Tada AI — Live Data Exploration Log

## Setup

| Provider | Auth header sent on each request | Base URL source | Path added after base URL | Sign-in IDs used in request URLs |
| --- | --- | --- | --- | --- |
| PrismHR | `sessionId: <token>` | Sign-in `base_url` | (none) | `client_id` |
| isolved | `Authorization: Bearer <token>` | Sign-in `base_url` | `/api` | `client_id` + `legal_id` |
| UKG Ready | `Authorization: Bearer <token>` | Sign-in `base_url` | `/rest` | `company_id` |

- Sign-in: `POST https://tada-demo-provider-signin.onrender.com/signin`, header `X-API-Key`, body `{"tenant":"prism|isol|ukg"}`. Limit 30/min.
- Postman environment `TADA`: `api_key`, `<p>_base_url`, `<p>_token`, `<p>_companies`, plus bare IDs `prism_client`, `prism_emp`, `isol_client`, `isol_legal`, `isol_emp`, `ukg_company`, `ukg_emp`, `ukg_prefix`.
- Sign-in post-response scripts refresh base URL and token automatically.
- API key lives outside the repo; samples saved to `/Users/rutuja/Downloads/TADA/tada/samples/` (not in Git).

## Endpoint Results

Results come from the saved examples in the Postman collection "TADA collection". Result = HTTP status; Data = what the body holds; Status = whether the endpoint is used.

### Employee List

| Provider | Endpoint | Result | Data | Status |
| --- | --- | --- | --- | --- |
| PrismHR | `GET /employee/v1/getEmployeeList?clientId=132` | 200 | `employeeList.employeeId`: plain IDs (e.g. `A00576`) | Chosen |
| isolved | `GET /api/clients/4046/legals/5806/employees` | 200 | `results`: 20 employees (1 page) | Chosen |
| UKG | `GET /rest/v2/companies/33704016/employees` | 200 | `employees`: 103 employees | Chosen |

### Employee Full Record

| Provider | Endpoint | Result | Data | Status |
| --- | --- | --- | --- | --- |
| PrismHR | `GET /employee/v1/getEmployee?…&options=Person,Client,Compensation,ContactInformation` | 200 | `employee`: 1 record (A00576) | Chosen |
| isolved | `GET …/employees/{id}` (no flags) | 200 | 1 record (859139); optional sections not returned | Replaced by flagged request |
| isolved | `GET …/employees/{id}?includeOrganizations=true&includeAlternateRates=true&includeLabors=true&includeMiscFields=true&includeMiscDataSets=true` | 200 | 1 record (859139), 94 fields; `organizations[]` returned (Location, Department); `payRates[]` empty | Chosen |
| UKG (1 of 2) | `GET …/employees/{aid}` | 200 | 40 fields; shared in chat (Postman blocked saving: response contains secrets) | Chosen |
| UKG (2 of 2) | `GET …/employees/{aid}/pay-info` | 200 | 7 fields (see Key Findings) | Chosen |

### Compensation

| Provider | Endpoint | Result | Data | Status |
| --- | --- | --- | --- | --- |
| PrismHR | `getEmployee` with `options=Compensation` | 200 | Inside `employee[].compensation` | Chosen |
| isolved | `GET …/employees/{employeeId}/salaries` | 200 | 1 salary record; `payGroup.id` = 7627 | Chosen |
| UKG | `GET …/employees/{aid}/pay-info` | 200 | 7 fields; no pay rate or salary | Replaced by `compensation/history` |
| UKG | `GET …/employees/{aid}/compensation/history` | 200 | 2 entries (`amount`, `hourly_pay`, `amount_period`, `effective_from`) | Chosen |

### Direct Deposits

| Provider | Endpoint | Result | Data | Status |
| --- | --- | --- | --- | --- |
| PrismHR | `getEmployee` with `options=DirectDeposit` | 200 | `directDeposit` present; `achVoucher` empty (no accounts) | Chosen |
| isolved | `GET …/employees/{employeeId}/directdeposits` | 200 | 2 deposit accounts | Chosen |
| UKG | `GET …/employees/{aid}/direct-deposits` | 200 | `deposits` empty | Chosen |

### Deductions

| Provider | Endpoint | Result | Data | Status |
| --- | --- | --- | --- | --- |
| PrismHR | `GET /employee/v1/getScheduledDeductions` | 200 | 1 deduction; one-time or temporary deductions only | Replaced by `getDeductions` |
| PrismHR | `GET /deductions/v1/getDeductions` (employee J00809) | 200 | 11 deductions (e.g. `401k`, `MED`, `LIFE`) | Chosen |
| isolved | `GET …/employees/{employeeId}/payItems` | 200 | 41 pay items (19 deductions, 17 memo, 5 earnings) | Chosen |
| UKG | `GET …/employees/{aid}/deductions` | 404 | "Unresolvable URL"; docs mark it dev | Tried, not available |
| UKG | `GET …/employees/{aid}/benefits` | 200 | `benefits` empty | Tried, no data |
| UKG | `GET …/lookup/deduction-codes` | 200 | 43 company deduction codes | Chosen |

### Payroll Runs

| Provider | Endpoint | Result | Data | Status |
| --- | --- | --- | --- | --- |
| PrismHR | `GET /payroll/v1/getBatchListByDate?…&dateType=PAY` (2025-01-01 to 2026-10-11) | 200 | 57 batches; statuses `COMP`, `INITCOMP`, `INITFAIL`, `TS.READY`, `TSOKCOMP` | Chosen |
| isolved | `GET …/payGroups/7627/payrolls` | 404 | Scheduled runs only, not history | Replaced by `payrollRunHistory/byDate` |
| isolved | `GET …/paygroupId/7627/payrollRunHistory/byDate` (2020–2026) | 404 | Empty body | Chosen |
| isolved | `GET …/employees/{employeeId}/payroll` | 404 | Empty body | Tried, no data |
| UKG | `GET …/payrolls` | 200 | 49 payrolls; all `OPEN` | Chosen |

### Paychecks

| Provider | Endpoint | Result | Data | Status |
| --- | --- | --- | --- | --- |
| PrismHR | `GET /payroll/v1/getPayrollVouchersForEmployee` (employee A00576) | 200 | `payrollVoucher` empty | Replaced by `getPayrollVoucherForBatch` |
| PrismHR | `GET /payroll/v1/getPayrollVoucherForBatch?batchId=202513` | 200 | 6 vouchers (key is `payrollVoucher`, singular) | Chosen |
| isolved | `GET …/employees/{employeeId}/checks?includeDetails=true` | 200 | `results` empty | Replaced by pay-group `/checks` |
| isolved | `GET …/checks` (`filter.fromDate`, `filter.toDate`, 2020–2026) | 404 | No data | Tried, no data |
| isolved | `GET …/payGroups/7627/checks` (2020–2026) | 404 | Empty body | Chosen |
| isolved | `GET …/employees/{employeeId}/checks/years` (10 employees) | 404 | No checks for any employee tried | Tried, no data |
| UKG | `GET …/payrolls/35419520/pay-statements` | 200 | `pay_statements` empty | Chosen |

## Key Findings

| Topic | PrismHR | isolved | UKG Ready |
| --- | --- | --- | --- |
| Hierarchy | Client → Employee | Client → Legal → Employee | Company → Employee |
| URL style | Action-based, IDs in query | REST, IDs in path | REST, IDs in path |
| Payroll run term | Batch | Payroll (pay group) | Payroll |
| Paycheck term | Voucher | Check | Pay statement |
| Direct deposit | `getEmployee` option `DirectDeposit` | Own endpoint | Own endpoint |
| Compensation | `getEmployee` option `Compensation` | `/salaries` | `/compensation/history` |

- **PrismHR:** `getEmployee` returns only Person data unless `options` is set; SSN and DOB masked by default.
- **isolved:** employee record has `payGroup` as a name only; the ID comes from `/salaries`.
- **isolved:** `/payGroups/{id}/payrolls` lists scheduled runs, not history; history is `/paygroupId/{id}/payrollRunHistory`.
- **isolved:** company-wide `/checks` defaults to today's date; date filters are `filter.fromDate` / `filter.toDate`.
- **UKG:** `base_url` already ends in `/ta`; the working prefix before `/v2` is `/rest`.
- **UKG:** deduction code IDs (from lookup) are not the IDs `/deductions/{id}` expects.
- **Postman:** environment variables must hold bare IDs, not JSON lists, or UKG returns "Company not found".

## Gaps to Document

| Provider | Gap | Evidence | Plan |
| --- | --- | --- | --- |
| isolved | No payroll runs | `payrollRunHistory/byDate` (pay group 7627) and employee `/payroll` return 404 | Map from `isolved-v6.swagger.json`; synthetic fixtures |
| isolved | No paychecks | Company-wide, pay-group and per-employee check requests (10 employees) return 404 | Map from `isolved-v6.swagger.json`; synthetic fixtures |
| UKG | No employee deduction setup | `/employees/{aid}/deductions` returns 404 "Unresolvable URL"; `/benefits` empty | Map from docs sample; deduction-codes lookup for categories |
| UKG | No pay statements | `pay-statements` empty; all 49 payrolls `OPEN` | Map from docs schema; synthetic fixtures |
| UKG | No direct deposits for tested employee | `deposits` empty | Try another employee; else map from docs schema |
| PrismHR | No direct deposit accounts for tested employee | `achVoucher` empty | Try another employee; else map from schema |

## Next Steps

- [x] Save the UKG employee full record (1 of 2) response
- [ ] Try one more employee for PrismHR and UKG direct deposits
- [ ] Build one field-mapping table per data type (canonical field, PrismHR, isolved, UKG, notes), starting with Employee
- [ ] Copy confirmed gaps into `DECISIONS.md` → Provider Mappings & Gaps