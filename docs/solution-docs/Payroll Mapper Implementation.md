# Payroll mapper implementation

> **Historical:** written before the contracts/bundle change. CLI flags, source models and per-entity outputs described here were replaced; see [DECISIONS.md](./DECISIONS.md) and [relationship_policies.md](./relationship_policies.md).

## Flow

CLI JSON → provider normalize_payroll → existing source validation → shared adapters/_payroll_mapping.py → role-specific YAML + MappingEngine → canonical payroll records → CanonicalPayrollResult → Python dictionary → CLI JSON.

## Files and roles

- canonical_models/canonical_model_payroll.py: strict run, header, detailed paycheck and result schemas; conversions happen in helpers, not these schemas.
- mappings/<provider>/payroll_run.yaml and paycheck.yaml: source-to-output rules. UKG also uses paycheck_header.yaml. Seven YAMLs retain the existing one-source-class-per-engine design.
- adapters/_payroll_mapping.py: builds one engine per populated role/source class, maps records in input order, assembles three separate lists. No API calls or joins.
- helpers/mapping.py: identifier_alias resolves check-number aliases; existing identifier/date/number helpers are reused. Config schema/registry explicitly allow the new helper.

## Decisions and boundaries

- Preserve run, paycheck summary and detailed paycheck roles as payroll_runs, paycheck_headers and paychecks.
- Preserve iSolved paychecks/results independently; each record carries its original section and index. UKG headers/details likewise stay separate. No inferred deduplication, sums or totals.
- Prism voucher batchId and employeeId populate supplied associations. iSolved employeeId is mapped; payrollRunNumber remains a provider sequence, not a manufactured run ID. UKG account_id stays provider-specific.
- Missing employee/run associations stay absent/null. This does not prevent mapping; resolving them later is a documented gap. No additional CLI context is required.
- Shared values follow the verified proposal: source record IDs, documented dates, net_pay/check_amount, iSolved gross_pay, and explicit Prism associations. Unverified UKG meanings remain provider-specific.
- Earnings, hours/rates, deductions, taxes, contributions, benefits, accruals and payments retain provider-specific nested scopes and explicit names. No unit/currency/scaling assumptions or current/cumulative aggregation.
- Source IDs become strings through the existing helper. Sequence/count fields remain numeric. Provider date fields selected in YAML use the date helper; invalid dates retain originals/issues. Other unresolved fields retain source types.
- Prism checkNumber/checkNum: one supplied value is used; equal values are used once; conflicting values output null plus both originals and a mapping issue. Empty strings remain source values; no numeric comparison erases leading zeros.
- Known links use engine fallback with original aliases/nesting. Unknown fields use source_extras. Engine provenance retains all transformed originals. Existing fallback may retain an empty nested object alongside its mapped empty projection; no semantic record is inferred from it.
- Preserve wrapper information and supplied empty/null collection states in metadata where removed collections otherwise have no record. UKG named wrappers retain metadata outside their collections. Native records are preserved by the record engine.
- Existing Prism two-path source validation remains; both supplied batch and voucher collections are validated. Other providers retain their existing combined-input validation classes. No source schemas were changed.

## Reference warnings

__main__.py partitions existing readiness messages. Permission/lookup-status/version/OpenAPI availability/provenance gaps emit stderr warnings and are saved in source_metadata.<provider>.reference_pack with actual distribution status and reference version. The pack is not relabeled as verified. Missing/unreadable/malformed lookup files, wrong provider, invalid lookup container and unknown readiness failures still block before processing.

Result containers receive root metadata; employee lists receive it per record. An empty employee list with warnings is wrapped as {"employees": [], "source_metadata": ...} so a file never loses those warnings. Direct adapter results do not include CLI readiness warnings. check-inputs continues reporting all diagnostic gaps and may return 2.

## Verification and fixtures

279 tests and 3980 subtests passed, including alias conflicts, null/missing owners, overlapping sections, nested component amounts, originals/extras/links, empty output metadata, YAML preflight, strict canonical types and real CLI reference-warning behavior.

The 15 pairs in tests/fixtures cover every provider/entity, with synthetic names/IDs/bank placeholders. manifest.json records separate CLI context. Expected files came from CLI execution and independent semantic assertions checked their IDs, fields, dates, amounts, associations, filtering and preservation before saving. Fixture tests compare full JSON and never regenerate expected files automatically. These examples are a baseline, not proof of exhaustive semantic coverage or live API behavior.
