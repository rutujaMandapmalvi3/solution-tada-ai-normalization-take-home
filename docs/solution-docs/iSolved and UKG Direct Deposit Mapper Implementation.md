# iSolved and UKG direct-deposit mapping

> **Historical:** written before the contracts/bundle change. CLI flags, source models and per-entity outputs described here were replaced; see [DECISIONS.md](./DECISIONS.md) and [relationship_policies.md](./relationship_policies.md).

Uses the same record/result models and mapping engine as PrismHR. No new helper implementation was added: UKG reuses conditional_number.

## Input and mapping boundary

| Provider | Source validation | Records passed to YAML | Preserved response data |
|---|---|---|---|
| isolved | IsolvedEmployeeDirectDepositResponse, a RootModel of an array | IsolvedEmployeeDirectDepositModel from validated.root | No invented wrapper. Per-record links remain in unmapped; extras retain their positions. |
| ukg-ready | UKGReadyDirectDepositResponse | UKGReadyDirectDepositResponseDepositsItem from deposits | All supplied fields outside deposits, including _links/counts/routing settings and extras, in result source_metadata.ukg-ready.response. |

RootModel.root is Pydantic's accessor, not a JSON root field. No source-validation shape changed.

## Agreed policy and implementation choices

- --employee-id is now required and nonblank for direct_deposit across all three providers. Direct adapter calls also take keyword-only employee_id. Other entity paths keep their existing behavior.
- Neither selected isolved nor UKG deposit schema declares an employee owner. The supplied CLI context is trusted; ownership cannot be cross-checked from the account response alone. Deposit IDs, account numbers, links and array positions are not used to infer employee IDs.
- One owner applies to this file. The adapter attaches it to each record and the result; it does not join across employees or fetch source data.
- Validate the native response once; map already-validated accounts using one engine per input. Skip engine creation for an empty account list.
- Return CanonicalDirectDepositResult as a JSON-compatible dictionary: provider, employee_id, direct_deposits and preservation fields. Empty lists do not discard wrapper metadata. No bank account or deposit ID is fabricated.
- Maintain input ordering; each record metadata includes source_location.account_index. No sorting, deduplication, summing or reconciliation.
- Preserve unknown fields in source_extras; known provider-specific fields/links retain provider_fields scope. Conversion originals/issues use the common source_metadata format.

## Amounts and types

- isolved amount and percent populate separate allocation_amount/allocation_percentage without scaling. Null sequence and zero sequence remain different; 0 is not discarded.
- isolved account type dictionary contains only verified Checking. Unknown types are retained in original_values with an issue, not guessed.
- UKG allocation_amount is populated only when raw calc_method.type is FLAT_AMOUNT, using the same conditional_number helper as Prism. Its amount remains in provider fields for every method; no percentage conversion occurs.
- UKG percentage, sequence, currency, calculation/frequency details and status values remain provider-specific where interpretation is unverified.
- Preserve UKG type, including RESERVE_LIVE_CHECK. These records are not silently discarded or assumed to describe a bank account merely because they arrived in this collection.
- Source/account record IDs become strings through the existing identifier helper. Existing nullable isolved IDs and non-null UKG record requirements remain source-validation policy.

## Reference readiness and verification

references.py is unchanged. Existing readiness checks still block real CLI execution for isolved/UKG. Tests isolate readiness only to verify actual CLI routing, source validation, YAML mapping, canonical validation and JSON writing; separate tests confirm the real gate remains active.

Regression coverage includes both providers' native shapes, owner requirements, empty results, one source validation/engine, leading zeros, nullable IDs, zero/percentage values, UKG conditional amounts/reserve types, nested reference IDs, wrapper/record links, unknown values/extras, order, serialization and no input mutation.

## Relevant files

- [isolved.py](../../src/normalization/adapters/isolved.py)
- [ukg_ready.py](../../src/normalization/adapters/ukg_ready.py)
- [isolved direct_deposit.yaml](../../src/normalization/mappings/isolved/direct_deposit.yaml)
- [UKG direct_deposit.yaml](../../src/normalization/mappings/ukg_ready/direct_deposit.yaml)
- [Canonical model](../../src/normalization/canonical_models/canonical_model_direct_deposit.py)
- [PrismHR implementation reference](./PrismHR%20Direct%20Deposit%20Mapper%20Implementation.md)
