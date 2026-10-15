# PrismHR direct-deposit mapper: implementation reference

This describes the implemented connection, not an additional design proposal.

## Files and flow

`CLI JSON → PrismHRDirectDepositResponse → owner check → each PrismHRAchVoucher → direct_deposit.yaml + MappingEngine → CanonicalDirectDeposit → CanonicalDirectDepositResult → Python dictionary → CLI JSON file`

| File | Responsibility |
|---|---|
| [__main__.py](../../src/normalization/__main__.py) | Parse CLI/context, deserialize input, check references, call provider, serialize output; refuse overwrite. |
| [prismhr.py](../../src/normalization/adapters/prismhr.py) | Dispatch and normalize_direct_deposits: validate once, check ownership, unwrap accounts, invoke engine, assemble preserved result. |
| [Direct-deposit source models](../../src/normalization/source_models/prismhr/prismhr_source_model_direct_deposit.py) | Reuse typed employee/setup/account models; validate required wrappers and supplied nested types. |
| [direct_deposit.yaml](../../src/normalization/mappings/prismhr/direct_deposit.yaml) | Map one validated AchVoucher, including documented labels and source-specific values. |
| [helpers/mapping.py](../../src/normalization/helpers/mapping.py) | Existing ID/number/label conversions; conditional_number selects a numeric value using a YAML condition. |
| [mapping_config.py](../../src/normalization/mapping_config.py) | Validate rule syntax, registered helper name and argument shape. |
| [mapping_engine.py](../../src/normalization/mapping_engine.py) | Read declared fields, apply rules/helpers, preserve known/unknown fields and validate canonical output. |
| [canonical_model_direct_deposit.py](../../src/normalization/canonical_models/canonical_model_direct_deposit.py) | Strict account and result output schemas; nullable deposit ID, optional business fields, preservation containers. |

## Agreed decisions and verified source facts

| Rule | Origin |
|---|---|
| Employee ownership comes from CLI context and must not overwrite a conflicting response ID. | User-approved employee-association approach. |
| No deposit ID is manufactured; deposit_id is explicitly null for Prism. | AchVoucher has no equivalent record ID. |
| Only raw method F promotes amount to allocation_amount; every other amount remains preserved. | Method F means fixed; user-approved conditional mapping. |
| Account/routing numbers remain strings, including leading zeros. | Existing identifier and source-semantic policy. |
| C means checking or pay card, S savings, IP instant pay. | AchVoucher property description, not guessed bank-type equivalence. |
| Unknown labels, methods and values are retained; no unit/currency/percentage scaling. | Universal preservation policy. |
| Missing/null deposit setup and empty accounts are valid; supplied malformed records still fail source validation. | Existing source-validation policy. |
| Wrapper errorCode 0 means success; other codes fail. | Existing documented project assumption. |
| infoMessage/updateMessage/extension are preserved; their presence alone is not treated as failure. | Previously agreed wrapper policy. |
| Paycheck ACH transactions and HSA are not account-setup records. | Existing entity/scope decision. |

## Implementation choices made explicit

- CLI --employee-id is required and nonblank for PrismHR direct_deposit only at this stage. Direct adapter calls require the same keyword argument. Other entity/provider signatures remain as before.
- One context owner applies to the input file. Every supplied employee id must match exactly, including employee records without deposit setup. A mismatch raises ValueError before mapping; records are never silently reassigned. Several records for the same owner remain allowed and are not deduplicated.
- Source validation runs once through PrismHRDirectDepositResponse. Nested accounts are already typed; the mapper does not revalidate each source account.
- One MappingEngine instance is reused across all supplied accounts. It is not created when there are no accounts.
- The YAML receives one PrismHRAchVoucher plus employee_id and explicit null deposit_id context. It does not parse an HTTP response, fetch data, infer an endpoint, or invent request context.
- Output is a result dictionary with provider, employee_id and direct_deposits, not the former validation stub. Empty data means direct_deposits is [], while wrapper/settings/extras remain available. This uses the already-built result model instead of returning a bare [] that loses metadata.
- The adapter reuses the engine's existing _remaining/_extras preservation utilities for data outside the account mapping. No new selection, formatting or preservation framework was introduced.
- Account order is input employee order, then achVoucher order. Each output account records source_location.employee_index and ach_voucher_index. No join, aggregation, deduplication or accounting reconciliation is performed.

## YAML rules and conditional helper

| Source | Output |
|---|---|
| accountNum / transitNum | account_number / routing_number, unchanged text |
| bankName | bank_name |
| accountType | account_type using only documented full labels; raw value retained |
| method | provider_fields.prismhr.ach_method, descriptive label; raw value retained |
| amount | provider_fields.prismhr.method_amount using number helper |
| amount + method | allocation_amount through conditional_number with equals F |
| limit | provider_fields.prismhr.percentage_method_limit |
| status | provider_fields.prismhr.account_status using its exact dictionary |
| voucherTypeOverride | provider_fields.prismhr.voucher_type_override, raw combinations |

conditional_number is generic: when selector equals the YAML-supplied value, reuse number(value); otherwise return null. No Prism code meaning is embedded in Python. The separate amount-preservation rule stays active for every method.

Example: amount=10, method=P produces allocation_amount=null and method_amount=10, plus ach_method=percentage. Metadata retains the original raw method P and the validated source amount. Conversion provenance begins after existing Pydantic source validation; it is not a byte-for-byte copy of the original JSON file.

## Where retained data goes

| Data | Location |
|---|---|
| Canonical account values | direct_deposits[] |
| Account-specific methods/limits and known values | direct_deposits[].provider_fields.prismhr |
| Raw converted account values/issues | direct_deposits[].source_metadata.original_values / mapping_issues |
| Account unknown properties | direct_deposits[].source_extras.prismhr |
| Wrapper fields, messages, extension and wrapper extras | source_metadata.prismhr.response, excluding employee |
| Known employee/setup fields outside mapped populated account arrays | provider_fields.prismhr.unmapped.employee[], retaining original names/nesting |
| Unknown employee/setup/account fields at original input positions | source_extras.prismhr.employee[] |

Account extras can appear both with their canonical account and in result-level original employee nesting. This is preservation/provenance, not additional deposit records. Null/empty account collections remain in the retained setup; populated account lists are represented by mapped records rather than copied wholesale. Missing versus explicit null/empty employee/setup fields is retained.

## Local usage

```sh
python -m normalization normalize --provider prismhr --entity direct_deposit \
  --employee-id 007 --input input.json --output output.json
```

The source employee id must be 007 in this example. --input reads a local JSON file; no provider API request is made. --client-id is not newly required for this path, and no company relationship is inferred from employee_id.

## Verification and remaining limits

At implementation: 195 tests passed. Coverage includes actual CLI serialization/refusal to overwrite, required context, ownership conflicts, wrapper errors/types, one source validation/engine, empty/null inputs, unknown fields, account order/location, no input mutation, fixed zero amounts and percentage-value preservation.

Business amount bounds, method/limit conditional restrictions, reconciliation and further interpretation of messages/extensions remain deferred under the existing policy. This integration changes only PrismHR direct deposits; other providers/entities retain their current implementation stage.
