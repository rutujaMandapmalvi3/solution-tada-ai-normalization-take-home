# Direct Deposits — Response Fields

All fields returned by each provider's direct deposit API, matched by meaning across providers.

| Provider | Endpoint | Source | Fields |
| --- | --- | --- | --- |
| PrismHR | `getEmployee` (`options=DirectDeposit`) | Saved response, employee A00576; paths under `employee[]` (last 5 rows are top-level). `achVoucher[]` was empty, so its fields come from schema `AchVoucher` | 36 |
| isolved | `…/employees/{employeeId}/directdeposits` | Saved response, employee 859139; response is a list, so `[]` is dropped | 11 |
| UKG | `…/employees/{aid}/direct-deposits` | `deposits[]` was empty, so fields come from schema `schemas[137]` | 54 |

- `.` marks a nested field; `[]` marks a list.
- PrismHR fields are under `directDeposit.achVoucher[]` and UKG fields under `deposits[]` unless shown otherwise.

## Matched Fields

| Field | PrismHR | isolved | UKG |
|---|---|---|---|
| Deposit ID | — | `id` | `id` |
| Account number | `accountNum` | `accountNumber` | `account_number` |
| Routing number | `transitNum` | `routingNumber` | `routing_number`, `routing_type` |
| Account type | `accountType` | `accountType` | `account_type` |
| Bank name | `bankName` | `bankName` | — |
| Name / description | — | `description` | `name`, `description` |
| Amount | `amount` | `amount` | `amount` |
| Percent | — | `percent` | `percentage` |
| Calculation method | `method` | — | `calc_method.type`, `calc_method.display_name` |
| Order / priority | — | `sequenceNumber` | `sequence` |
| Status | `status` | `status` | `active`, `pre_note_status` |
| Effective dates | — | — | `active_from`, `active_to` |
| Frequency | — | `frequency` | `payroll_frequency.*` (8 fields) |
| Limit | `limit` | — | — |
| Voucher type | `voucherTypeOverride`, `directDeposit.voucherType` | — | — |
| Currency | — | — | `currency` |

## No Match in Other Providers

| Provider | Fields |
|---|---|
| PrismHR | `directDeposit.achStatus`, `directDeposit.suppressAccountPrint`, `directDeposit.directDepositChecksum`; the remaining response fields are unrequested `getEmployee` sections with no content |
| isolved | None |
| UKG | `type`, `cancel_pre_note`, `pre_note_sent_date`, `pre_note_expiration_date`, `arrearage_function`, `last_payroll`, `month_to_date`, `quarter_to_date`, `year_to_date`, `used_in_pay_statement`, `_documents_count`, `_notes_count`, `visible`, `is_paypal`, `deposits[]._links.*` (7), top-level `_links.*` (4), `_total_count`, `_routing_type`, `is_eligible_for_paypal` |

## Related Fields in Other Data Types

| Provider | Field | Data type | Why related |
|---|---|---|---|
| PrismHR | `compensation.payMethod` | Employee full record | Payment method, e.g. check or deposit |
| PrismHR | `compensation.payAllocation[]` | Employee full record | How pay is split |

## Findings

| Finding | Evidence |
|---|---|
| UKG `type` is not a voucher type | UKG values `DIRECT_DEPOSIT` / `RESERVE_LIVE_CHECK` say where pay goes; PrismHR voucher type `R` / `S` / `V` says which paychecks the deposit applies to |

## Matches to Verify

None.