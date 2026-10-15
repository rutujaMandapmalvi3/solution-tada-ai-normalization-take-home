# Direct Deposit Canonical Mapping Proposal

Deposit setup is distinct from money actually paid on a paycheck. HSA settings are excluded. PrismHR EmployeeDirectDeposit, AchVoucher and PayrollVoucher-DirectDeposit are covered; the last belongs to payroll payment information.

## How to review this proposal

This proposes names and types; it does not implement a canonical model or mapper. Read the shared-field table first, then the decisions to review. The complete inventory keeps every declared source field, including nested objects, without forcing unrelated fields into one shared value.

- Source columns show the current Python type and the contract description. Optional accepts null; required presence is shown separately in the inventory.
- IDs become strings when mapped. Keep leading zeros; never truncate fractional identifiers or manufacture an ID when the source has none.
- Proposed date fields use Python date, serialized YYYY-MM-DD. Blank/invalid values and timestamps need the agreed date helper; retain the original when information would be lost.
- Amounts use finite float through the existing number helper, following the employee decision. Do not convert currencies, percentage scales, frequencies or amount bases. Decimal is a future precision improvement, not a blocker here.
- Record-ID and required-wrapper presence rules remain the existing source-validation policy. A proposed shared field does not introduce a new source requirement.
- Known provider fields use explicit snake_case names under `provider_fields.<provider>`; unconsumed known fields and links retain source nesting under `provider_fields.<provider>.unmapped`. Unknown fields retain nesting under `source_extras.<provider>`. Reuse the employee engine preservation rules; extra=allow alone does not map or validate unknown contents.
- Nested model names in types are source classes. Object/list boundaries remain intact; no flattening or joins are implied. Categories below organize this document, not required sections in the eventual canonical model.
- Wrapper codes, messages, paging and wrapper links go in `source_metadata.<provider>.response`. Record links stay in their original nesting under the unmapped fallback. Keep infoMessage, updateMessage and extension without treating their presence alone as failure.

## Proposed shared fields

| Canonical field (Python type) | PrismHR source/type/description | isolved source/type/description | UKG Ready source/type/description | Proposed handling |
|---|---|---|---|---|
| `deposit_id` (Optional[str]) | No verified shared counterpart proposed. | `IsolvedEmployeeDirectDepositModel.id` (Optional[int])<br>Unique Object Id | `UKGReadyDirectDepositResponseDepositsItem.id` (int)<br>No property description supplied. | Prism has no equivalent record ID. |
| `account_number` (Optional[str]) | `PrismHRAchVoucher.accountNum` (Optional[str])<br>the bank account number | `IsolvedEmployeeDirectDepositModel.accountNumber` (Optional[str])<br>Bank account number for the Direct Deposit | `UKGReadyDirectDepositResponseDepositsItem.account_number` (Optional[str])<br>No property description supplied. | Preserve as text, including leading zeros. |
| `routing_number` (Optional[str]) | `PrismHRAchVoucher.transitNum` (Optional[str])<br>the banking system transit number | `IsolvedEmployeeDirectDepositModel.routingNumber` (Optional[str])<br>Bank routing number for the Direct Deposit | `UKGReadyDirectDepositResponseDepositsItem.routing_number` (Optional[str])<br>No property description supplied. | Retain routing_type separately; country/bank-system equivalence is not assumed. |
| `bank_name` (Optional[str]) | `PrismHRAchVoucher.bankName` (Optional[str])<br>name of banking institution | `IsolvedEmployeeDirectDepositModel.bankName` (Optional[str])<br>Bank Name | No counterpart in this schema. | Decided: direct text mapping; no inferred bank lookup. |
| `account_type` (Optional[str]) | `PrismHRAchVoucher.accountType` (Optional[str])<br>For updates, you can only specify 'C' , 'S' or 'IP'. Types that can be returned are 'C' (checking account or pay card), 'S' (savings account), and IP (instant pay). | `IsolvedEmployeeDirectDepositModel.accountType` (Optional[str])<br>Bank Acount Type Description | `UKGReadyDirectDepositResponseDepositsItem.account_type` (Optional[str])<br>No property description supplied. | Use verified full labels below; retain original codes. Prism C is checking or pay card, not a proven checking-only match. |
| `allocation_percentage` (Optional[float]) | No verified shared counterpart proposed. | `IsolvedEmployeeDirectDepositModel.percent` (Optional[float])<br>Direct deposit percentage, may not be specified if an 'Amount' is specified. | `UKGReadyDirectDepositResponseDepositsItem.percentage` (Optional[float])<br>No property description supplied. | Do not infer fraction versus percent scale. |
| `allocation_amount` (Optional[float]) | `PrismHRAchVoucher.amount` (Optional[float]) when `method="F"`<br>Method F is documented as fixed; amount is mandatory except for B. | `IsolvedEmployeeDirectDepositModel.amount` (Optional[float])<br>Direct deposit amount, may not be specified if a 'Percent' is specified. | `UKGReadyDirectDepositResponseDepositsItem.amount` (Optional[float])<br>No property description supplied. | Decided conditional match: Prism F / isolved amount / UKG FLAT_AMOUNT. Retain method and currency; no currency conversion. Other Prism methods remain separate. |
| `sequence` (Optional[int]) | No verified shared counterpart proposed. | `IsolvedEmployeeDirectDepositModel.sequenceNumber` (Optional[int])<br>Direct Deposit sequence. (0 = Net Pay) | `UKGReadyDirectDepositResponseDepositsItem.sequence` (Optional[int])<br>No property description supplied. | Preserve nullable values; priority/order interpretation needs documented rules. |

Use `provider: Literal["prismhr", "isolved", "ukg-ready"]` on normalized records. The common table deliberately contains only verified candidate matches; all remaining fields have an explicit preservation destination below. PrismHR/isolved bank details have descriptive evidence. UKG fields without descriptions remain name/type-based candidates; their inclusion does not establish percentage scale, sequence semantics, or status equivalence.

## Additional comparison findings

- UKG cached direct-deposit HTML marks this endpoint deprecated as of April 13, 2023. This is a fact about the local reference snapshot; no current live replacement has been verified.
- Prism amount is mandatory except for method B, where it must be absent; limit is permissible only for method P. Those are documented method rules, but enforcing them is a separate business-validation decision. Preserve method-dependent values without inventing percentage scaling.
- isolved sequenceNumber is described as 0 = Net Pay. Retain zero and distinguish this from an absent/null sequence. UKG sequence has no supplied property description, so its exact equivalence remains a candidate.
- Prism achStatus applies to the employee deposit section, while AchVoucher.status applies to an individual account. Preserve both levels. A paycheck line status is a third context.
- The employee envelope can include unrelated HR data. This proposal inventories its wrapper and deposit classes; it does not remap the full employee entity here. Preserve employee.id as employee context and use the employee proposal for the rest.

## Decisions already settled

| Area | Decision | Basis |
|---|---|---|
| Implementation | Shared Pydantic output model, provider YAML rules, common engine/helpers. | Same employee architecture. |
| Record identity | isolved/UKG `id` → string `deposit_id`; Prism has no deposit ID: leave null/unset, never generate one from bank details. | Existing identifier policy and source schemas. |
| Input identity | Assume the selected entity input supplies its required record IDs; nested IDs identify their own records. Existing null acceptance remains. | Existing decision; does not supply a missing employee ID. |
| Bank details | Account/routing numbers stay strings; Prism/isolved bank names share `bank_name`. | Contract descriptions; leading zeros retained. |
| Numbers | Optional finite float; retain amount basis and percentage scale, including zero. | Existing number helper; no inferred conversion. |
| Dates | UKG date fields use optional date / YYYY-MM-DD; preserve source strings and conversion issues. | Existing date helper; no timezone shifting. |
| Missing data | Optional absent/null/empty deposit collections return `[]`; supplied malformed records still fail validation. Required wrappers remain required. | Existing direct-deposit validation policy. |
| Status | Keep employee deposit status, account status, UKG active flag and pre-note status separate. | Different levels and concepts. |
| Preservation | `provider_fields`, `source_extras`, `source_metadata`; retain links at source nesting through fallback. | Existing employee engine behavior. |
| Scope | Deposit setup and paycheck ACH payments remain separate; exclude HSA. | Setup allocation is not an actual payment. |
| Fixed allocation | Prism method F amount, isolved amount and UKG FLAT_AMOUNT amount share allocation_amount. Retain method/currency and original values. | Explicit fixed/flat descriptions and UKG cached example. |
| Other Prism amounts | Preserve method_amount, percentage_method_limit and ach_method for P, PN, FS and unresolved methods; B has no allocation amount. | No complete equivalent basis/behavior crosswalk. FS has a special insufficient-funds rule. |
| Employee context | Use CLI --employee-id for standalone deposit input; preserve/verify an employee ID supplied by the response. One owner per file. Do not overwrite conflicting IDs. | User chose the existing CLI-context pattern; implementation remains pending. |
| UKG destination type | Preserve type including DIRECT_DEPOSIT and RESERVE_LIVE_CHECK; do not discard or reinterpret it. | User decision; exact reserve-check behavior is undocumented. |
| UKG missing descriptions | Preserve values and calculation context; no inferred scale, priority or routing conversion. | User accepted preservation. |

## Decisions still to review

None pending for the questions above. UKG description gaps remain documented limitations handled by preservation, not unresolved conversion decisions. CLI context and conditional fixed-amount mapping still require implementation.

## Complete source-to-canonical inventory

Each source class is listed once, including nested classes. Follow an object/list field to its named child class. This represents every declared field without duplicating the same reusable class at every possible parent path. RootModel[List[T]] means a top-level JSON array, not an input object with a root key. A field marked required may still accept null if its annotation is Optional.

Targets below are relative to the corresponding record. Provider-specific targets use `provider_fields.<provider>` with explicit snake_case names and existing object/list boundaries. Wrapper data uses source metadata; record links use unmapped preservation. Shared fields are emitted from their matching record only. Do not overwrite conflicting values or join unrelated records.

### prismhr

#### PrismHRDirectDepositResponse

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_direct_deposit.py) · Project input/container; no independent provider schema.

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `errorCode` | str | Required presence | string | No property description supplied. | Metadata: `source_metadata.prismhr.response`; retain source field and nesting. |
| `errorMessage` | str | Required presence | string | No property description supplied. | Metadata: `source_metadata.prismhr.response`; retain source field and nesting. |
| `extension` | Optional[PrismHRExtension] | Optional presence | #/components/schemas/Extension | No property description supplied. | Metadata: `source_metadata.prismhr.response`; retain source field and nesting. |
| `employee` | Optional[List[PrismHREmployee]] | Optional presence | array | No property description supplied. | Container: validate and map deposit records individually; do not copy the full employee entity into each deposit. |
| `infoMessage` | Optional[List[str]] | Optional presence | array | Error message detail for the failed Employees | Metadata: `source_metadata.prismhr.response`; retain source field and nesting. |
| `updateMessage` | Optional[str] | Optional presence | string | update messages | Metadata: `source_metadata.prismhr.response`; retain source field and nesting. |

#### PrismHRExtension

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_payroll_run.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/Extension).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `any` | Optional[Dict[str, Any]] | Optional presence | object | No property description supplied. | Metadata: `source_metadata.prismhr.response`; retain source field and nesting. |

#### PrismHRDirectDeposit

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_employee.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/EmployeeDirectDeposit).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `achStatus` | Optional[str] | Optional presence | string | must be one of 'A' (active) or 'I' (inactive) | Preserve separately: `provider_fields.prismhr.employee_deposit_status`; retain nested scope and source type. |
| `voucherType` | Optional[str] | Optional presence | string | must be one or more voucher types: 'R' (Regular), 'S' (Supplemental), 'V' (Vacation), or a combination of these (for example, RV for regular and vacation or RVS for all three types) | Preserve separately: `provider_fields.prismhr.voucher_types`; retain nested scope and source type. |
| `suppressAccountPrint` | Optional[bool] | Optional presence | boolean | 'true' suppresses printing of employee's account information on the deposit advice | Preserve separately: `provider_fields.prismhr.suppress_account_print`; retain nested scope and source type. |
| `achVoucher` | Optional[List[PrismHRAchVoucher]] | Optional presence | array | information on accounts to which deposits are made; this is best described as the employee's direct deposit record | Preserve separately: `provider_fields.prismhr.accounts`; retain nested scope and source type. |
| `directDepositChecksum` | Optional[str] | Optional presence | string | the direct deposit checksum to use for updates | Preserve separately: `provider_fields.prismhr.direct_deposit_checksum`; retain nested scope and source type. |

#### PrismHRAchVoucher

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_employee.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/AchVoucher).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `transitNum` | Optional[str] | Optional presence | string | the banking system transit number | Shared: `routing_number`. Use the agreed helper where needed; retain originals for conversions. |
| `accountNum` | Optional[str] | Optional presence | string | the bank account number | Shared: `account_number`. Use the agreed helper where needed; retain originals for conversions. |
| `accountType` | Optional[str] | Optional presence | string | For updates, you can only specify 'C' , 'S' or 'IP'. Types that can be returned are 'C' (checking account or pay card), 'S' (savings account), and IP (instant pay). | Descriptive `account_type` (Optional[str]); only verified labels below. Preserve raw source in original_values. |
| `method` | Optional[str] | Optional presence | string | must be one of: 'F' (fixed), 'P' (percentage), 'FS' (fixed, skip if can't take full amount), 'PN' (percentage of net after fixed), or 'B' (remaining balance; can be used for only one of a specific voucher type (R, V, or S) that is set to Deposit Active) | Preserve separately: `provider_fields.prismhr.ach_method`; retain nested scope and source type. |
| `amount` | Optional[float] | Optional presence | number | precision 2 (##.##); mandatory for all methods except 'B', for which it must not be specified | Conditional shared: `allocation_amount` (Optional[float]) only when method is F; otherwise preserve `provider_fields.prismhr.method_amount`. Retain method and original amount; no scaling. |
| `limit` | Optional[float] | Optional presence | number | precision 2 (##.##); permissible only when method is 'P' | Preserve separately: `provider_fields.prismhr.percentage_method_limit`; retain nested scope and source type. |
| `status` | Optional[str] | Optional presence | string | must be one of: 'P' (Pre-notification), 'D' (Deposit Active), or 'I' (Deposit Inactive) | Preserve separately: `provider_fields.prismhr.account_status`; retain nested scope and source type. |
| `bankName` | Optional[str] | Optional presence | string | name of banking institution | Decided shared: `bank_name` (Optional[str]); direct text mapping. |
| `voucherTypeOverride` | Optional[str] | Optional presence | string | must be a subset of the voucherType attribute, or else empty/unspecified | Preserve separately: `provider_fields.prismhr.voucher_type_override`; retain nested scope and source type. |

#### PrismHRPayrollVoucherDirectDeposit

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/PayrollVoucher-DirectDeposit).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `transitNum` | Optional[str] | Optional presence | string | transit number for employee's financial institution | Payroll payment field: `routing_number` (Optional[str]); preserve payment scope, not setup allocation. |
| `accountNum` | Optional[str] | Optional presence | string | employee's account number | Payroll payment field: `account_number` (Optional[str]); preserve payment scope, not setup allocation. |
| `status` | Optional[str] | Optional presence | string | status of ACH transaction | Payroll payment field: `ach_transaction_status` (Optional[str]); preserve payment scope, not setup allocation. |
| `amount` | Optional[float] | Optional presence | number | amount of ACH transaction | Payroll payment field: `payment_amount` (Optional[float]); preserve payment scope, not setup allocation. |

### isolved

#### IsolvedBaseLinkModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_direct_deposit.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.Base.LinkModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `href` | Optional[str] | Optional presence | string | Hyperlink to linked entity or action | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |
| `method` | Optional[str] | Optional presence | string | HTTP Method for linked entity or action | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |
| `rel` | Optional[str] | Optional presence | string | Relationship or purpose of link to enclosing entity | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedEmployeeDirectDepositModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_direct_deposit.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.EmployeeDirectDepositModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Shared: `deposit_id`. Use the agreed helper where needed; retain originals for conversions. |
| `accountNumber` | Optional[str] | Optional presence | string | Bank account number for the Direct Deposit | Shared: `account_number`. Use the agreed helper where needed; retain originals for conversions. |
| `accountType` | Optional[str] | Optional presence | string | Bank Acount Type Description | Descriptive `account_type` (Optional[str]); only verified labels below. Preserve raw source in original_values. |
| `amount` | Optional[float] | Optional presence | number / double | Direct deposit amount, may not be specified if a 'Percent' is specified. | Shared: `allocation_amount`. Use the agreed helper where needed; retain originals for conversions. |
| `bankName` | Optional[str] | Optional presence | string | Bank Name | Decided shared: `bank_name` (Optional[str]); direct text mapping. |
| `description` | Optional[str] | Optional presence | string | Direct deposit description | Preserve separately: `provider_fields.isolved.description`; retain nested scope and source type. |
| `frequency` | Optional[str] | Optional presence | string | Direct Deposit Frequency Description | Preserve separately: `provider_fields.isolved.frequency`; retain nested scope and source type. |
| `percent` | Optional[float] | Optional presence | number / double | Direct deposit percentage, may not be specified if an 'Amount' is specified. | Shared: `allocation_percentage`. Use the agreed helper where needed; retain originals for conversions. |
| `routingNumber` | Optional[str] | Optional presence | string | Bank routing number for the Direct Deposit | Shared: `routing_number`. Use the agreed helper where needed; retain originals for conversions. |
| `sequenceNumber` | Optional[int] | Optional presence | integer / int32 | Direct Deposit sequence. (0 = Net Pay) | Shared: `sequence`. Use the agreed helper where needed; retain originals for conversions. |
| `status` | Optional[str] | Optional presence | string | Direct Deposit Status Description | Preserve separately: `provider_fields.isolved.status`; retain nested scope and source type. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped.links` (record links). |

#### IsolvedEmployeeDirectDepositResponse

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_direct_deposit.py) · Project input/container; no independent provider schema.

Input shape: `RootModel[List[IsolvedEmployeeDirectDepositModel]]`. No additional declared fields.

### ukg_ready

#### UKGReadyDirectDepositResponse

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_direct_deposit.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/137/schema).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__employees__%28aid%29__direct-deposits.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `deposits` | List[UKGReadyDirectDepositResponseDepositsItem] | Required presence | array | No property description supplied. | Container: validate and map deposit records individually; do not copy the full employee entity into each deposit. |
| `_links` | UKGReadyDirectDepositResponseLinks | Required presence | object | No property description supplied. | Metadata: `source_metadata.ukg-ready.response`; retain source field and nesting. |
| `_total_count` | Optional[int] | Optional presence | integer | No property description supplied. | Metadata: `source_metadata.ukg-ready.response`; retain source field and nesting. |
| `_routing_type` | Optional[str] | Optional presence | string | No property description supplied. Documented enum: ["ABA", "BSB", "NA"]. | Metadata: `source_metadata.ukg-ready.response`; retain source field and nesting. |
| `is_eligible_for_paypal` | Optional[bool] | Optional presence | boolean | No property description supplied. | Metadata: `source_metadata.ukg-ready.response`; retain source field and nesting. |

#### UKGReadyDirectDepositResponseDepositsItem

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_direct_deposit.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/137/schema/properties/deposits/items).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__employees__%28aid%29__direct-deposits.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Shared: `deposit_id`. Use the agreed helper where needed; retain originals for conversions. |
| `name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.name`; retain nested scope and source type. |
| `description` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.description`; retain nested scope and source type. |
| `sequence` | Optional[int] | Optional presence | integer | No property description supplied. | Candidate shared: `sequence`. Use the agreed helper where needed; retain originals for conversions. Missing description; see review table. |
| `type` | Optional[str] | Optional presence | string | No property description supplied. Documented enum: ["DIRECT_DEPOSIT", "RESERVE_LIVE_CHECK"]. | Preserve separately: `provider_fields.ukg-ready.type`; retain nested scope and source type. |
| `active_from` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.active_from` (Optional[date]); existing date helper and original value. |
| `active_to` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.active_to` (Optional[date]); existing date helper and original value. |
| `active` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.active`; retain nested scope and source type. |
| `amount` | Optional[float] | Optional presence | number | No property description supplied. | Conditional shared: `allocation_amount` (Optional[float]) for calc_method.type FLAT_AMOUNT; preserve method/currency. Other contexts remain provider-specific; no inferred behavior. |
| `percentage` | Optional[float] | Optional presence | number | No property description supplied. | Candidate shared: `allocation_percentage`. Use the agreed helper where needed; retain originals for conversions. Missing description; see review table. |
| `calc_method` | Optional[UKGReadyDirectDepositResponseDepositsItemCalcMethod] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.calc_method`; retain nested scope and source type. |
| `account_type` | Optional[str] | Optional presence | string | No property description supplied. Documented enum: ["CHECKING", "SAVINGS"]. | Descriptive `account_type` (Optional[str]); only verified labels below. Preserve raw source in original_values. |
| `account_number` | Optional[str] | Optional presence | string | No property description supplied. | Candidate shared: `account_number`. Use the agreed helper where needed; retain originals for conversions. Missing description; see review table. |
| `routing_number` | Optional[str] | Optional presence | string | No property description supplied. | Candidate shared: `routing_number`. Use the agreed helper where needed; retain originals for conversions. Missing description; see review table. |
| `routing_type` | Optional[str] | Optional presence | string | No property description supplied. Documented enum: ["ABA", "BSB", "NA"]. | Preserve separately: `provider_fields.ukg-ready.routing_type`; retain nested scope and source type. |
| `pre_note_status` | Optional[str] | Optional presence | string | No property description supplied. Documented enum: ["INVALID", "READY_TO_SEND", "SENT", "CANCELED", "COMPLETE_OK", "COMPLETE_EXPIRED", "NA"]. | Preserve separately: `provider_fields.ukg-ready.pre_note_status`; retain nested scope and source type. |
| `cancel_pre_note` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.cancel_pre_note`; retain nested scope and source type. |
| `pre_note_sent_date` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.pre_note_sent_date` (Optional[date]); existing date helper and original value. |
| `pre_note_expiration_date` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.pre_note_expiration_date` (Optional[date]); existing date helper and original value. |
| `arrearage_function` | Optional[str] | Optional presence | string | No property description supplied. Documented enum: ["UNKNOWN", "DISCARD_UNDERFUNDED_AMOUNT", "DISCARD_ENTIRE_DIRECT_DEPOSIT", "ARREAR_UNDERFUNDED", "ARREAR_ENTIRE_DIRECT_DEPOSIT"]. | Preserve separately: `provider_fields.ukg-ready.arrearage_function`; retain nested scope and source type. |
| `payroll_frequency` | Optional[UKGReadyDirectDepositResponseDepositsItemPayrollFrequency] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.payroll_frequency`; retain nested scope and source type. |
| `last_payroll` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.last_payroll`; retain nested scope and source type. |
| `month_to_date` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.month_to_date`; retain nested scope and source type. |
| `quarter_to_date` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.quarter_to_date`; retain nested scope and source type. |
| `year_to_date` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.year_to_date`; retain nested scope and source type. |
| `used_in_pay_statement` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.used_in_pay_statement`; retain nested scope and source type. |
| `currency` | Optional[str] | Optional presence | string | No property description supplied. Documented enum: ["USD", "GBP", "EUR", "CAD", "AUD", "NZD", "MXN", "CNY", "SEK", "BRL", "INR", "SGD", "HKD", "CHF", "CRC", "UAH", "MOP", "DKK", "XXX"]. | Preserve separately: `provider_fields.ukg-ready.currency`; retain nested scope and source type. |
| `_documents_count` | Optional[int] | Optional presence | integer | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.documents_count`; retain nested scope and source type. |
| `_notes_count` | Optional[int] | Optional presence | integer | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.notes_count`; retain nested scope and source type. |
| `visible` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.visible`; retain nested scope and source type. |
| `is_paypal` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.is_paypal`; retain nested scope and source type. |
| `_links` | Optional[UKGReadyDirectDepositResponseDepositsItemLinks] | Optional presence | object | No property description supplied. | Preserve source nesting: `provider_fields.ukg-ready.unmapped._links` (record links). |

#### UKGReadyDirectDepositResponseDepositsItemCalcMethod

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_direct_deposit.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/137/schema/properties/deposits/items/properties/calc_method).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__employees__%28aid%29__direct-deposits.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `display_name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.display_name`; retain nested scope and source type. |
| `type` | Optional[str] | Optional presence | string | No property description supplied. Documented enum: ["FULL", "FLAT_AMOUNT", "GROSS_EARNING", "NET_PAY", "DIRECT_DEPOSIT_PER_OF_REMAINDER"]. | Preserve separately: `provider_fields.ukg-ready.type`; retain nested scope and source type. |

#### UKGReadyDirectDepositResponseDepositsItemPayrollFrequency

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_direct_deposit.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/137/schema/properties/deposits/items/properties/payroll_frequency).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__employees__%28aid%29__direct-deposits.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `type` | Optional[str] | Optional presence | string | No property description supplied. Documented enum: ["MANUAL", "ANNUAL", "EVERY_OTHER_SCHEDULED_PAY", "EVERY_PAY", "EVERY_SCHEDULED_PAY", "EVERY_SCHEDULED_MONTH_ODD_PAY", "EVERY_SCHEDULED_MONTH_EVEN_PAY", "MONTHLY", "QUARTERLY", "HOLIDAY_TABLE", "BENEFIT_PLAN"]. | Preserve separately: `provider_fields.ukg-ready.type`; retain nested scope and source type. |
| `holiday_type` | Optional[str] | Optional presence | string | No property description supplied. Documented enum: ["EMPLOYEE_HOLIDAY_PROFILE", "SPECIFIC_HOLIDAY_PROFILE"]. | Preserve separately: `provider_fields.ukg-ready.holiday_type`; retain nested scope and source type. |
| `holiday_profile` | Optional[UKGReadyDirectDepositResponseDepositsItemPayrollFrequencyHolidayProfile] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.holiday_profile`; retain nested scope and source type. |
| `month` | Optional[int] | Optional presence | integer | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.month`; retain nested scope and source type. |
| `payroll_number` | Optional[str] | Optional presence | string | No property description supplied. Documented enum: ["FIRST", "SECOND", "THIRD", "FOURTH", "LAST"]. | Preserve separately: `provider_fields.ukg-ready.payroll_number`; retain nested scope and source type. |
| `block_last` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.block_last`; retain nested scope and source type. |
| `quarter_month` | Optional[int] | Optional presence | integer | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.quarter_month`; retain nested scope and source type. |

#### UKGReadyDirectDepositResponseDepositsItemPayrollFrequencyHolidayProfile

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_direct_deposit.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/137/schema/properties/deposits/items/properties/payroll_frequency/properties/holiday_profile).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__employees__%28aid%29__direct-deposits.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Nested reference: `provider_fields.ukg-ready.payroll_frequency.holiday_profile.id` (str); identifier helper, no company/employee identity inference. |
| `display_name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.display_name`; retain nested scope and source type. |

#### UKGReadyDirectDepositResponseDepositsItemLinks

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_direct_deposit.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/137/schema/properties/deposits/items/properties/_links).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__employees__%28aid%29__direct-deposits.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `self` | Optional[str] | Optional presence | string | No property description supplied. | Preserve source nesting: `provider_fields.ukg-ready.unmapped` (record links). |
| `edit` | Optional[str] | Optional presence | string | No property description supplied. | Preserve source nesting: `provider_fields.ukg-ready.unmapped` (record links). |
| `delete` | Optional[str] | Optional presence | string | No property description supplied. | Preserve source nesting: `provider_fields.ukg-ready.unmapped` (record links). |
| `masked` | Optional[str] | Optional presence | string | No property description supplied. | Preserve source nesting: `provider_fields.ukg-ready.unmapped` (record links). |
| `documents` | Optional[str] | Optional presence | string | No property description supplied. | Preserve source nesting: `provider_fields.ukg-ready.unmapped` (record links). |
| `upload_document` | Optional[str] | Optional presence | string | No property description supplied. | Preserve source nesting: `provider_fields.ukg-ready.unmapped` (record links). |
| `add_note` | Optional[str] | Optional presence | string | No property description supplied. | Preserve source nesting: `provider_fields.ukg-ready.unmapped` (record links). |
| `notes` | Optional[str] | Optional presence | string | No property description supplied. | Preserve source nesting: `provider_fields.ukg-ready.unmapped` (record links). |

#### UKGReadyDirectDepositResponseLinks

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_direct_deposit.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/137/schema/properties/_links).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__employees__%28aid%29__direct-deposits.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `add` | Optional[str] | Optional presence | string | No property description supplied. | Metadata: `source_metadata.ukg-ready.response`; retain source field and nesting. |
| `reserve_live_check` | Optional[str] | Optional presence | string | No property description supplied. | Metadata: `source_metadata.ukg-ready.response`; retain source field and nesting. |
| `cancel_pre_note` | Optional[str] | Optional presence | string | No property description supplied. | Metadata: `source_metadata.ukg-ready.response`; retain source field and nesting. |
| `upload_document` | Optional[str] | Optional presence | string | No property description supplied. | Metadata: `source_metadata.ukg-ready.response`; retain source field and nesting. |

## Code and lookup review

The three lookup-reference files contain no direct-deposit-specific domain. The following evidence comes from the referenced property descriptions, UKG schema enums, and the saved isolved response. Labels express documented meanings; they do not make different status concepts equivalent.

| Field | Provider / source | Verified value → full label | Handling |
|---|---|---|---|
| Account type | Prism `accountType` | C → checking or pay card; S → savings; IP → instant pay | Retain the C ambiguity; never label it checking only. |
| Account type | isolved `accountType` | Checking → checking (saved response) | Other undocumented values remain raw with a mapping issue; no invented dictionary. |
| Account type | UKG `account_type` | CHECKING → checking; SAVINGS → savings | Schema enum supplies these labels. |
| Employee deposit status | Prism `achStatus` | A → active; I → inactive | Separate employee-level field. |
| Account status | Prism ACH `status` | P → pre-notification; D → deposit active; I → deposit inactive | Separate account-level field; not payroll transaction status. |
| ACH method | Prism `method` | F → fixed; P → percentage; FS → fixed, skip if full amount unavailable; PN → percentage of net after fixed; B → remaining balance | Keep method and amount together; no inferred scaling. |
| Voucher selection | Prism `voucherType` / override | R → regular; S → supplemental; V → vacation | Combinations are allowed; preserve raw combinations until token/list handling is chosen. |
| Deposit status | isolved `status` | Inactive → inactive (saved response) | Preserve source status separately; no assumption it equals pre-note status. |
| Frequency | isolved `frequency` | Every Pay (saved response) | Preserve text; no unverified UKG scheduling crosswalk. |

UKG enum tokens remain provider-specific where no crosswalk is verified:

| Source field | Documented values |
|---|---|
| `type` | DIRECT_DEPOSIT, RESERVE_LIVE_CHECK |
| `routing_type` / wrapper `_routing_type` | ABA, BSB, NA |
| `calc_method.type` | FULL, FLAT_AMOUNT, GROSS_EARNING, NET_PAY, DIRECT_DEPOSIT_PER_OF_REMAINDER |
| `pre_note_status` | INVALID, READY_TO_SEND, SENT, CANCELED, COMPLETE_OK, COMPLETE_EXPIRED, NA |
| `arrearage_function` | UNKNOWN, DISCARD_UNDERFUNDED_AMOUNT, DISCARD_ENTIRE_DIRECT_DEPOSIT, ARREAR_UNDERFUNDED, ARREAR_ENTIRE_DIRECT_DEPOSIT |
| `payroll_frequency.type` | MANUAL, ANNUAL, EVERY_OTHER_SCHEDULED_PAY, EVERY_PAY, EVERY_SCHEDULED_PAY, EVERY_SCHEDULED_MONTH_ODD_PAY, EVERY_SCHEDULED_MONTH_EVEN_PAY, MONTHLY, QUARTERLY, HOLIDAY_TABLE, BENEFIT_PLAN |
| `payroll_frequency.holiday_type` | EMPLOYEE_HOLIDAY_PROFILE, SPECIFIC_HOLIDAY_PROFILE |
| `payroll_frequency.payroll_number` | FIRST, SECOND, THIRD, FOURTH, LAST |

Unknown values remain preserved. Blank/null values follow the existing helper policy; no meaning is invented for NA, UNKNOWN, or an undocumented code. Currency stays its documented source code without conversion.

## Saved Postman evidence

Request names and saved response structure only are shown below. No personal/account values or credentials are copied. A request with no saved JSON response provides no live response proof. Samples supplement the contract; they do not define every accepted input shape.

| Request | Saved JSON response evidence |
|---|---|
| prismHR - DirectDeposits chosen | 200 object; keys: employee, errorCode, errorMessage, extension, infoMessage, updateMessage |
| isol - DirectDeposits chosen | 200 array; keys: accountNumber, accountType, amount, bankName, description, frequency, id, percent, routingNumber, sequenceNumber, status |
| ukg - directDeposits chosen | 200 object; keys: _links, _routing_type, deposits |

## References and verification

- [Original comparison](./direct-deposit.md) (unchanged; disagreements should be resolved using the contract evidence above).
- [Decisions](../DECISIONS.md) and [README](../../../README.md).
- [PrismHR OpenAPI](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json), [isolved Swagger](../../../contracts/isolved/openapi/isolved-v6.swagger.json), [UKG schemas](../../../contracts/ukg-ready/reference-schemas.json).
- Lookup references: [PrismHR](../../../contracts/prismhr/lookup-reference.json), [isolved](../../../contracts/isolved/lookup-reference.json), [UKG Ready](../../../contracts/ukg-ready/lookup-reference.json).

Declared source-field coverage (reused classes counted once per provider): prismhr 25, isolved 15, ukg_ready 60.

Fields with absent/vague-by-absence property descriptions or undocumented source additions: prismhr 5, isolved 0, ukg_ready 60. Every such field is explicitly marked; a source name is not treated as a verified meaning. Coverage counts prove inventory inclusion, not business equivalence or live API completeness.

Before implementation: follow the confirmed decisions above and retain the documented UKG description limitations. Identifier/date/number helpers and preservation rules are already decided. Verify missing/null/empty, zero/false, unknown codes, extras and conflicting values when implementing. This review changes this proposal only; source models, canonical models, YAMLs and adapters are unchanged.

## Amount comparison and confirmed decisions — start here

| Prism field / method | Other-provider evidence | Decision |
|---|---|---|
| amount with F (fixed) | isolved amount is a deposit amount, mutually exclusive with percent; UKG example pairs amount with FLAT_AMOUNT / “Flat Amount”. | Shared allocation_amount; retain raw method, currency and originals. |
| amount with FS | Prism adds “skip if cannot take full amount”; no verified identical rule elsewhere. | Preserve separately with method. |
| amount with P | Prism says percentage without defining the earnings basis or scale; isolved percent is 0–100; UKG example percentage uses GROSS_EARNING / “% Of Gross Earnings”. | Do not equate bases/scales; preserve Prism method_amount. |
| amount with PN | Prism specifies percentage of net after fixed; no verified same-basis description elsewhere. | Preserve separately. |
| B (remaining balance) | UKG example FULL displays “Entire/Remainder”, but complete ordering/behavior equivalence is unverified; Prism says amount must be absent. | Preserve method; do not manufacture a numerical allocation. |
| limit | Prism permits it only for P; neither other selected deposit schema exposes a verified matching limit. | Preserve percentage_method_limit. |

Evidence: [Prism AchVoucher](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/AchVoucher), [isolved deposit model](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.EmployeeDirectDepositModel), [UKG cached JSON example and schema](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__employees__%28aid%29__direct-deposits.html). Example labels support the specific matches above, not complete enum coverage.

- Decided: use CLI --employee-id context; preserve UKG destination types and undocumented values.
- Conditional mapping is a proposal rule; CLI, YAMLs, models and adapters have not changed in this update.

## Canonical output model implemented

- [canonical_model_direct_deposit.py](../../../src/normalization/canonical_models/canonical_model_direct_deposit.py) defines CanonicalDirectDeposit for one record and CanonicalDirectDepositResult for direct_deposits plus result-level provider_fields/source_extras/source_metadata.
- Shared business fields follow the table above. Record-ID presence is required but nullable; no Prism ID is invented. Employee context is optional in the output schema; CLI sourcing is not implemented here.
- Known provider-specific fields retain their scope in provider_fields; no new unit, calculation, status or identity meanings are introduced. Metadata includes typed conversion issues and original values.
- Result-level preservation supports empty record lists without fabricated records. Models alone do not change adapter return formats.
- YAMLs, adapter filtering/integration and CLI context remain separate implementation steps.

## Record YAMLs created — helpers unchanged

- Per-provider direct_deposit.yaml files now map one validated record to the canonical record model. Existing identifier/date/number/label helpers are reused; no helper, engine or adapter code was added in this step.
- Wrappers, parent settings, supplemental collections and filtered unexpected records remain adapter/result-level preservation responsibilities; these files do not create records for them.
- Prism has no equivalent record ID: the future adapter must supply explicit null record-ID context. Employee context sourcing/conflict checks are still adapter work.
- Verified against each configured source class: every declared record path is explicitly mapped or retained by the existing link fallback; populated and sparse synthetic records serialize successfully.
- Pending helper discussion: conditional allocation_amount promotion for Prism F and UKG FLAT_AMOUNT. Current rules preserve those amounts/methods separately; no unverified unconditional promotion. Voucher combinations remain raw.

## Prism fixed-amount helper implemented

- Prism direct_deposit.yaml now uses conditional_number(amount, method, equals="F") to populate allocation_amount only for fixed method F.
- Existing method_amount and ach_method preservation mappings remain; non-fixed values are not discarded. Source originals remain in conversion metadata.
- The helper reuses number validation; no scaling/calculation or provider-code dictionary is embedded in Python. The equals value is configured in YAML.
- UKG conditional amount mapping is unchanged and remains for the next helper discussion. No adapter or CLI integration changed.

## PrismHR adapter connection completed

- normalize_direct_deposits now uses the packaged YAML and common engine with required employee-id context, preserving wrapper/setup data and unknown fields in the canonical result.
- Full behavior, verified facts, project assumptions, implementation choices and tests are documented in [PrismHR Direct Deposit Mapper Implementation](../PrismHR%20Direct%20Deposit%20Mapper%20Implementation.md).
- PrismHR direct-deposit mapping is connected through the CLI. Other providers remain separate work.

## iSolved and UKG adapter connections completed

Both deposit adapters now use their existing YAMLs and CanonicalDirectDepositResult with required employee-id context. UKG uses the already-implemented conditional_number for FLAT_AMOUNT while preserving every original amount/method/type. Helpers and references.py were not changed in this step.

See [iSolved and UKG implementation reference](../iSolved%20and%20UKG%20Direct%20Deposit%20Mapper%20Implementation.md). Real CLI execution remains blocked by their deferred reference-readiness checks.
