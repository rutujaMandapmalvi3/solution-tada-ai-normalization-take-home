# Decisions

`…` = `/api/clients/{clientId}/legals/{legalId}` (isolved) or `/rest/v2/companies/{cid}` (UKG).

## Data Sources

| Decision | Why |
|---|---|
| Company: PrismHR `getClientMaster`; isolved `…` (legal company); UKG ID from sign-in | Only sources of company ID and name |
| Employee: PrismHR `getEmployee` (Person, Client, Compensation, ContactInformation); isolved `…/employees/{id}`; UKG `…/employees/{aid}` + `…/pay-info` | Return each provider's full employee record |
| Compensation: PrismHR `getEmployee` (Compensation); isolved `…/employees/{id}/salaries`; UKG `…/employees/{aid}/compensation/history` | Return pay amounts; UKG `pay-info` has none |
| Direct deposits: PrismHR `getEmployee` (DirectDeposit); isolved `…/employees/{id}/directdeposits`; UKG `…/employees/{aid}/direct-deposits` | PrismHR has no separate read endpoint |
| Deduction setup: PrismHR `getDeductions`; isolved `…/employees/{id}/payItems`; UKG `…/lookup/deduction-codes` | PrismHR `getScheduledDeductions` covers only one-time deductions; UKG employee deductions endpoint is not available |
| Deductions taken in payroll: from paychecks (PrismHR vouchers, isolved check details, UKG pay statement details) | README asks for deductions recorded in payroll |
| Payroll runs: PrismHR `getBatchListByDate`; isolved `…/paygroupId/{id}/payrollRunHistory/byDate`; UKG `…/payrolls` | isolved `/payrolls` lists only scheduled runs |
| Paychecks: PrismHR `getPayrollVoucherForBatch`; isolved `…/payGroups/{id}/checks`; UKG `…/payrolls/{id}/pay-statements` | Keeps paychecks linked to their run |
| Request isolved full record with organization, extra pay rate, labor and custom field flags | Those sections are not returned otherwise |
| Use the base URL returned by sign-in | It points to the demo environment |
| Skip isolved endpoints built for third-party partners | They return less data |
| Map data types with no live data from the documentation | Some demo accounts have no data for them |
| Gap: compensation APIs (isolved `…/employees/{id}/salaries`, UKG `…/employees/{aid}/compensation/history`) not implemented for now; compensation mapped only from the employee record | They need extra input files per employee; kept out of scope for now. Result: UKG employees have no pay amounts (`pay-info` has none) |

## Field Mapping

| Decision | Why |
|---|---|
| Use live field names where they differ from the documentation | Code reads live responses |
| IDs and links required; all other fields optional | Every provider is missing some fields |
| Provider-only fields that fit a README category → optional standard fields; the rest → `provider_extras` | Complete data without losing anything |
| Keep disability, emergency contacts and county as optional fields | Standard profile and contact data |
| Split email into work email and personal email; PrismHR benefits email and UKG secondary email unmatched | They mean different things |
| UKG `dates.re_hired` optional and unmatched | No value or description to confirm it |
| UKG deposit `type` not matched to PrismHR voucher type | Different meanings |
| PrismHR `deductPeriod` and isolved `payOfTheMonth` unmatched | Number vs text |
| Keep only isolved pay items with `payItemType` = `Deduction` | The endpoint also returns earnings and memo items |
| Convert isolved schedule codes to PrismHR-style digits (e.g. `K` → `1234`) | Same meaning, different format |
| Company: ID required, name optional (not available from UKG) | README requires company–employee links, not company data |

## Architecture

| Decision | Why |
|---|---|
| Python + Pydantic; no web framework | Task is a data conversion; Pydantic covers validation and JSON |
| No database; records linked by IDs in JSON | README needs links and local runs, not storage |
| Adapter pattern: one adapter per provider, same methods | A new provider needs only one new class |
| Target as an abstract base class (ABC) with 6 abstract methods, not a regular class or Protocol | A missing method fails when the adapter is created, without a type checker; the base can hold shared code |
| One Target for all three adapters; shared code in the base only when identical across providers | Every provider serves all 6 data types (UKG deductions from company codes, company from sign-in ID); the CLI never special-cases a provider |
| One standard schema per record type, shared by all providers; one mapper per provider per record type (6 × 3) | Same output for every provider |
| Every record gets an ID built from provider + record type + its own key; provider's ID kept as `source_id` | One ID rule for all providers; works when a provider has no ID |
| Owner link from the request (Method 1) or from a field in the record (Method 4) | Some responses do not include the owner's ID |
| Two validations: incoming provider data and outgoing standard data | Catch bad input and bad output separately |
| CLI: `--provider`, `--type`, `--input`, `--output` (folder) | Picks adapter and mapper; writes per-type files |
| Output: one file per provider and record type, plus an errors file | Easier to read and test; nothing lost |
| Tests on synthetic fixtures with pytest | README requires offline tests without credentials |