# Deduction mapper implementation

> **Historical:** written before the contracts/bundle change. CLI flags, source models and per-entity outputs described here were replaced; see [DECISIONS.md](./DECISIONS.md) and [relationship_policies.md](./relationship_policies.md).

All three deduction adapters now validate, select, map and preserve supplied data using existing source models, canonical schemas, YAMLs and helpers. references.py and payroll remain unchanged.

## Why selection is in adapters

Source validation checks record structure; it does not establish that every structurally valid pay item is a deduction. Adapters know the selected provider/entity and select assignments before invoking the provider-independent engine. YAML conditions are not used to classify records.

| Provider | Selection | Preserved related/unexpected data |
|---|---|---|
| PrismHR | employeeDeductions.deduction | Wrapper/extension; remaining section fields and unknown nested values. No extra deduction-type test. |
| isolved | Exact payItemType == Deduction | Earning, Memo Calc, missing/null/unknown/other types in provider_fields.isolved.non_deduction_items; original indexes in metadata. |
| UKG Ready | assignments.deductions after existing native-section adaptation | code_lookup and benefits in result provider_fields.ukg-ready; no supplement becomes an assignment. |

Unexpected records must still pass existing source validation. Filtering does not bypass required IDs/types or silently accept malformed known fields.

## Context and identities

- --employee-id is required and nonblank for deduction across providers, matching the established deposit convention. Direct normalize_deductions calls take the same keyword-only argument. It is separate request context, not an inline comment or generated source property.
- Prism/UKG selected assignment schemas omit a direct employee owner, so their context is trusted. Nested UKG benefit employee.account_id is preserved in that benefit scope, not borrowed as assignment ownership.
- For selected isolved deductions, employeeId is converted using the existing identifier helper and must equal supplied context when present. A mismatch raises ValueError before mapping. Missing/null source ownership uses CLI context in canonical output; source null/absence provenance and request_employee_id remain available.
- Unexpected isolved records are preserved with their own supplied source ownership; they are not relabeled or assigned the selected deduction owner's identity.
- Assignment IDs become canonical strings. Prism has no equivalent assignment record ID: context supplies explicit null deduction_id. A definition code is never substituted for it.
- Preserved supplements/unexpected records retain source values and IDs rather than being presented as canonical assignments; no join, matching, deduplication, amount aggregation or generated record occurs.

## Flow and output

`CLI JSON → existing source validation → adapter selects assignments → one shared engine per selected collection → canonical records → CanonicalDeductionResult → JSON-compatible dictionary → CLI JSON text`

- Nested records are validated once through the source response model; the adapter does not repeat record model_validate calls before mapping.
- No engine is created when no assignments are selected. The result still contains deductions=[] plus any preserved source data.
- Preserve source order. Per-record source_location records the original deduction/array index, so filtered list positions remain traceable.
- Result output is a dictionary with provider, employee_id, deductions and preservation fields. A bare [] would lose source information on supplemental-only/unexpected-only input.
- Record-specific known fields/links use provider_fields; unknown properties use source_extras; helper conversions retain originals/issues. Labels and units follow existing verified dictionaries/preservation policy.
- Prism wrappers are retained in result source_metadata.prismhr.response, excluding employeeDeductions. Unmapped section fields/null/empty collections retain source shape; unknown section/record fields retain their original positions in result extras as well as record-level extras.
- isolved native arrays have no fabricated response wrapper. Known unexpected fields use _plain; unknown fields use existing _extras at source indexes. Unknown properties can also be present with their selected canonical record; this is provenance, not another deduction record.
- UKG known supplemental fields use _plain in their original code_lookup/benefits containers; undeclared properties use source_extras. Empty/null assignment/supplement sections are retained. Existing native adaptation may retain original native fields in extras; they are not mapped again as assignments.
- UKG uncertain code/name/effective-date meanings retain provider scope under the existing YAML. Native wrappers and named sections remain accepted; conflicting representations still fail existing source validation.

## Amount rules

No new calculation helper was added. Prism amount/usePercent/method/limit/maximum/matching fields stay together in provider scope; documented basis/match labels use existing label rules. isolved calcParams keeps paramType and paramValue without guessing Amount2/Rate meanings. Balance and zero values remain preserved. Enrollment/catalog information does not generate a withheld amount.

## Verification and remaining work

At connection: 238 tests passed. Tests cover mixed item types (including missing/null/case differences), no-selection preservation, supplemental-only and native UKG inputs, empty/null/absent sections, context requirements/conflicts/fallback, record IDs, wrapper errors, one source validation/engine, extras/links, dates/zero amounts, order, no input mutation and actual CLI output.

Prism CLI integration uses real readiness checks. isolved/UKG CLI mapping tests isolate only the deferred gate; separate tests confirm real readiness still blocks. Those reference blockers remain for the end as requested. Payroll mapping and deferred business edge cases remain separate work.

## Relevant files

- [PrismHR adapter](../../src/normalization/adapters/prismhr.py)
- [isolved adapter](../../src/normalization/adapters/isolved.py)
- [UKG adapter](../../src/normalization/adapters/ukg_ready.py)
- [Canonical model](../../src/normalization/canonical_models/canonical_model_deduction.py)
- [Deduction proposal and per-field YAML evidence](./data-types-cpmparison/Deduction%20Canonical%20Mapping%20Proposal.md)
- [Decision log](./DECISIONS.md)
