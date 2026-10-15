# Assumptions & Decisions

## Architecture change: contracts, bundles and merge by id

This section supersedes the earlier rows it lists below. Relationship rules are
in [relationship_policies.md](./relationship_policies.md).

| Decision | Reason |
|---|---|
| Validate each response directly against its contract (`src/normalization/contracts.py`); the 18 Pydantic source models are removed. | The contracts are the source of truth. A hand-written copy of every field drifts from them and doubles maintenance. |
| Contract sources: PrismHR OpenAPI 3.0.1, isolved primary Swagger 2.0 only, UKG `reference-schemas.json` (the GET schema of the page named after the endpoint; no HTML is read). | These are the README-approved references. The README says not to mix the two isolved snapshots. |
| `null` counts as "not supplied". A non-null value of the wrong type stops the run (exit 1). Undocumented fields, enum, length and range violations are `contract_drift` warnings in `issues`. `required` is not enforced. | Live data returns null for most fields, and the contracts mark nearly every field required. Only record ids are required, and the id templates enforce them. A wrong type means a record cannot be mapped safely, matching the previous Pydantic behaviour. |
| Four live PrismHR spellings are renamed to the contract names before validation (`payrollVoucher`, `person.employerId`, `person.autoPolicy`, `client.hawaiiMedWaiver`), scoped by parent key. | Replaces the `AliasChoices` in the source models. `clientMaster.employerId` is a real contract field, so the renames are scoped. |
| Fields the live demo returns but the contract does not list are declared once in `contracts.LIVE_FIELDS` (PrismHR company/employee/voucher, isolved pay item `balance`, UKG `ein_name`, payroll `ein.ein_country_id`). | The source models declared these as "live-only". Listing them keeps YAML preflight strict while still allowing these fields to be mapped. |
| The engine maps plain dicts. YAML source paths are preflighted against the contract schema, and unknown names fail at load time. Declared but unmapped fields go to `provider_fields.<p>.unmapped`; undeclared fields go to `source_extras.<p>`. | Same output layout and the same typo protection as before, without model classes. |
| UKG employee list items are mapped with the employee detail schema (route key `schema`). | The list page schema is a cut-down view of the same employee resource. Validation still uses the list schema. |
| Input is one bundle per provider: `{provider, responses: [{endpoint, params, status?, body}]}`. | `endpoint` selects the contract schema. `params` carries owner ids that bodies omit. One run sees company, employees and children together, so it can merge records and check links. |
| `--entity`, `--client-id` and `--employee-id` are removed; owner ids come from each response's `params`. | A flag could silently disagree with the file it is used with. |
| One run writes one document: `companies, employees, direct_deposits, deductions, payroll_runs, paychecks, provider_fields, source_metadata, issues`. | Links can be checked within the same run. |
| Every record gets `id`; children get `company_ref` / `employee_ref` / `payroll_run_ref` (relationship_policies.md, Tables 1–2). Existing source-id fields (`employee_id`, `source_record_id`, …) keep their meaning. | One cross-provider rule for identity and links, without changing the meaning of existing fields. |
| Records with the same `id` merge: missing fields are filled, objects merge, lists join, and differing values keep the first one and add `merge_conflict`. The merged record is validated again. | Several responses describe one record (UKG profile + pay-info + compensation; isolved employee + salaries; UKG statement header + detail). |
| Combined inputs become separate responses. The YAML rules for `salary_history`, `pay_info` and `compensation_history` moved unchanged into `employee_salaries.yaml`, `employee_pay_info.yaml` and `employee_compensation.yaml`; the pipeline wraps the response as `{section: body}` (route key `wrap`). | Keeps the existing mapping rules and output, while each body is validated against its own endpoint. |
| UKG: one company record per `cid` (`source_record_type: company`, `company_root.yaml`). EIN lookup items stay `ein` records, with `company_ref` pointing to it. | UKG employees can then link to a real company, not to an EIN. |
| UKG pay-statement header and detail merge into one paycheck; `paycheck_headers` is removed. | Supersedes "keep distinct roles": both describe the same statement and share its id. |
| isolved company comes from `GET /api/clients/{clientId}/legals` (a list). | The primary snapshot has no single-legal GET. |
| isolved non-deduction pay items, and responses with no canonical type (UKG deduction-code catalog, benefits), are kept under `provider_fields.<p>.filtered_records` / `unrouted_responses`. | Supplied data is never dropped. |
| Each response's wrapper fields (e.g. PrismHR `errorCode`, UKG `_links`) are kept in `source_metadata.<p>.responses[]` together with endpoint and params. Each record lists its `sources`. | Provenance per response and per record. |
| Integral floats (`7.0`) count as integers during contract validation. | Draft 4 alone rejects them; the previous source models and the identifier helper accept them, and UKG fixtures carry ids such as `7.0`. |
| YAML preflight stays as strict as the old engine: a field path cannot walk into a list without `[]`, and a list rule needs a list source. Only untyped or object nodes without listed properties are open. | Keeps the typo and shape protection the Pydantic engine gave. |
| A single-record response without its own id takes it from params before mapping (route key `fill_record`, e.g. UKG statement detail → `pay_statement_id`). | Policy rule 5 in relationship_policies.md; the canonical id field (`paycheck_id`) must be present when the record is mapped. |
| Reference-pack warnings are attached once, at `source_metadata.<p>.reference_pack`. | The output is now a single document instead of per-employee records. |
| Fixtures are three generated bundles (`tests/fixtures/<provider>.bundle.json`) plus reviewed `<provider>.expected.json`. They are validated with the contract layer. | One connected company per provider exercises ids, refs and merges end to end. |

**Superseded earlier rows:**
- `--employee-id` / `--client-id` context;
- the UKG/isolved combined-input models;
- separate provider source models;
- `paycheck_headers`;
- per-employee reference warnings;
- the 15 per-entity fixture pairs and `manifest.json`;
- `non_deduction_items` (now `filtered_records`).

**Known gaps of this change:**
- One wrong-typed value still stops the whole run; per-record rejection is part of the planned edge-case work.
- Merging joins lists, so supplying the same response twice duplicates history and lines.
- isolved checks still carry no payroll run id, so they have no `payroll_run_ref`.

## Earlier decisions (before the architecture change)


| Assumption / Decision | Reason |
|---|---|
| Preserve unexpected deduction records separately; do not classify them as deductions or discard them. | Retain supplied information while adapter filtering selects canonical deduction records. |
| Use provider adapter filtering after source validation and before deduction mapping; keep selection out of YAML and the shared engine. | Select deduction records using provider-specific evidence without changing source models. |
| isolved deductions map only verified Deduction items; retain other/unknown item kinds in provider_fields.isolved.non_deduction_items. | Preserve supplied known records without misclassifying earnings/memo items or treating them as unknown extras. |
| Preserve unclear deduction amounts, calculation parameters and field meanings; apply only verified conversions. | Selected parameter descriptions/lookups do not establish a cross-provider calculation rule. |
| Standalone deductions use CLI --employee-id context; preserve/check any source employee ID without silent overwrite. | Explicit employee association, consistent with direct deposits. |
| Direct deposits use CLI --employee-id context for standalone inputs; preserve and check any response employee ID without silent overwrite. | Explicit ownership using the existing CLI-context pattern. |
| Direct-deposit fixed allocation_amount matches Prism F, isolved amount and UKG FLAT_AMOUNT; preserve other Prism methods/limits separately. | Verified fixed/flat meaning; other bases/behavior remain unconfirmed. |
| Preserve UKG direct-deposit type, including RESERVE_LIVE_CHECK, and undocumented values without inferred conversion. | Keep source meaning when descriptions are insufficient. |
| Use one UKG employee input model and YAML for list/detail fields and supplements; keep EIN ID/name separate. | Shared validation and mapping; endpoint-specific field restrictions are relaxed. |
| Canonical identifiers use strings; convert numeric IDs during mapping. | Consistent cross-provider identity without losing string formatting. |
| Use one shared pronoun value; identical inputs appear once, while conflicting source values are retained without silent overwrite. | Avoid duplicate output keys and lost values. |
| Keep ordinary gender, isolved EEO override, and PrismHR designation separate. | They serve different roles. |
| Canonical dates serialize as YYYY-MM-DD; helpers handle invalid, blank, and timezone cases. | Consistent date representation. |
| Compensation values are numeric; retain their documented basis without inferred unit/currency conversions. | Preserve amount meaning. |
| Keep ethnic code, ethnic-origin description, and Hispanic flag separate until a verified crosswalk exists. | Relevant dictionaries and common categories remain unconfirmed. |
| Keep provider-specific fields and unknown extras outside shared business fields. | Preserve data without overwriting shared meanings. |
| UKG combined inputs use employee `pay_info`/`compensation_history`, deduction `assignments`/`code_lookup`/`benefits`, and payroll `payroll_runs`/`paycheck_list`/`paychecks`; reuse native schemas inside sections. | Validate supplemental data together without mixing field meanings or removing required wrapper checks. |
| Keep isolved paycheck models in the payroll source file; combined input uses optional `payroll_runs` and `paychecks`. Native run arrays and paged-check responses remain supported. | Validate complete payroll information without mixing run and paycheck field meanings. |
| Use one main isolved employee input model; keep employee fields at the top level and supplemental salary records under optional `salary_history`. | Validate combined data recursively while keeping employee and salary field meanings separate. |
| Require record IDs and documented required wrapper fields; other fields, including reference IDs, are optional. Keep existing ID null acceptance; nested record IDs are required only when the record is supplied. | JSON input may combine API fields; requiring complete endpoint responses complicates validation. |
| Do not manufacture a company ID when source input omits it; preserve supplied client/legal/EIN references and explicit context. | A required record-ID assumption does not create missing company identity. |
| Build a separate company-related output model with source record type and ID; retain employee associations separately. | Company model and three YAMLs were subsequently requested and built; no global company identity is asserted. |
| Keep the current canonical structure; use class comments to mark README coverage instead of adding category sections. | Documents coverage without restructuring the models. |
| Treat reference metadata gaps as CLI warnings and preserve them in output metadata. | Existing private-upload status and UKG reference format must remain truthful. |
| Add `direct_deposit` and `deduction` entities. | Both are required by the README. |
| Payroll output uses separate `payroll_runs`, `paycheck_headers` and `paychecks` lists; preserve overlapping sections with provenance, without merging or totaling them. | Keep distinct record roles and all supplied information. |
| Payroll preserves supplied employee/run references; missing references stay empty without new CLI requirements. | Mapping can proceed without inferred associations; missing links remain a deferred gap. |
| Payroll YAMLs are split by source record role: run, paycheck, and UKG header. | One source class and one map call per record; one payroll entity/output remains. |
| Preserve all payroll components under their provider scope unless a shared meaning is verified. | Earnings, hours, taxes, deductions, benefits and payments retain their nested source roles; no arithmetic or guessed conversions. |
| Resolve Prism checkNumber/checkNum with identifier_alias; unequal values yield null plus originals and an issue. | Neither alias silently overwrites the other; leading zeros remain significant. |
| Reuse date/identifier/number helpers; preserve unknown status/type domains and ambiguous amounts. | No new lookup meanings, currency conversions or associations are inferred. |
| Emit a payroll result container even for empty collections and preserve wrapper context. | Empty runs/checks must not discard warnings, pagination or source metadata. |
| Add reference-pack warnings at CLI serialization, per employee record or result container. | Adapter mapping stays independent of reference readiness. An empty warned employee list uses an employees: [] container with metadata. |
| Store 15 synthetic CLI fixture pairs and compare complete expected JSON in tests. | One per entity/provider; generated baseline independently checked for semantic rules and preservation before saving. |
| Use the supplied scripts/generate_fixtures.py with explicit source-shaped builders and seed 42. | Generate 15 repeatable, source-validated inputs; record evidence/checksums without treating mapper output as its own expected result. |

## Assumptions

- CLI employee context identifies the owner of a deduction file when source assignments omit it. Reason: Prism/UKG assignments lack a direct owner; optional isolved source owners are checked when present.

- CLI employee context identifies the owner of a direct-deposit file. Reason: selected isolved/UKG deposit responses contain no employee-owner field to verify it against.
- Prism employee homeLocation is used as work_location_code. Reason: user-confirmed employee work-location role; codes remain provider-scoped.
- Prism employee gender M/F/X/D/U labels follow the user-approved interpretation (including U as unknown), not a newly verified universal dictionary. Reason: preserve the explicitly chosen labels while retaining originals and evidence limits.

- Inputs match the selected provider/entity and include required record IDs; nested IDs identify nested records. Reason: avoid extra input-type configuration; retain existing null acceptance.

- PrismHR `errorCode="0"` means success; other codes mean failure. Reason: Postman success and other OpenAPI operations.
- PrismHR `--client-id` matches the request that produced the file. Reason: the response omits client context.
- UKG `id` supplies canonical `employee_id`; preserve source `employee_id` as `ukg_employee_id`. Reason: the user’s GET test succeeded with `id`, not the other field.

## YAML, canonical-model and adapter implementation choices

These record how the approved design is implemented. Status is separate from approval; a prepared model/YAML does not mean its adapter is connected. Universal preservation rules apply to every entity, not separate new decisions for each provider.

| Choice | Reason / limit | Status |
|---|---|---|
| Shared Pydantic output schemas; separate provider source models. | Validate input types once, then validate mapped output; do not conflate validation with semantic mapping. | Implemented for all five entities. |
| One common MappingEngine with provider/entity YAMLs and an allowlisted helper registry. | Rules stay outside adapters; YAML cannot execute arbitrary functions. Config forbids unknown keys/overlapping targets; loader rejects duplicate keys. | Implemented. |
| One source record per engine.map call; adapters unwrap wrappers and assemble collections/results. | Preserve distinct record roles without requiring a universal API response shape. | All five entities connected for all three providers. |
| IDs are already strings and date values already Python dates in strict canonical models. | Conversion belongs to helpers, not implicit output coercion. Optional business fields remain unset/null when unavailable. | Implemented. |
| Known explicit source-specific values → provider_fields; unused known fields/record links → provider_fields.<provider>.unmapped. | Preserve source meaning, nesting and list positions without false semantic matches. | Implemented common policy. |
| Undeclared properties → source_extras; wrappers → source_metadata.<provider>.response; conversions → original_values/mapping_issues. | Separate unknown data, response context and conversion provenance. | Implemented. Raw provenance starts after source validation. |
| Share business fields only when meanings match; preserve unverified codes/units/bases without inferred conversions. | A similar field name or another field's lookup is insufficient evidence. | Universal policy; per-field evidence lives in linked proposals. |
| Preserve missing/null/empty distinctions with exclude_unset; retain zero/false; use independent mutable defaults. | Do not lose supplied values or manufacture business defaults. | Implemented output/helper convention. |
| Canonical result containers preserve provider data when record lists are empty. | No fabricated account/deduction/company record just to carry supplements. | Deposit/deduction/company results integrated. Employee retains its existing list output. |
| Deposit YAMLs map account setup only; paycheck payments remain payroll and HSA stays outside deposit setup. | Related source schemas have different business roles. | Implemented. |
| conditional_number(value, selector, equals=...) reuses number conversion; condition value belongs in YAML. | Keep provider-specific meanings out of generic Python helper code. A nonmatch returns null only for the shared target. | Prism F / UKG FLAT_AMOUNT implemented; amount/method preservation rules remain active. |
| isolved amount/percent stay separate; Prism P/PN/FS/B and limit remain method-scoped. UKG uncertain percentage/sequence/calculation fields stay provider-specific. | No guessed percentage scale, basis, ordering or insufficient-funds equivalence. | Implemented deposit rules. |
| Require --employee-id for direct_deposit across providers; attach one owner per file. | Supplied request context preserves association; a deposit ID is not an employee ID. | CLI/adapters implemented for deposits and deductions. |
| Prism compares every supplied employee.id to employee context before mapping; isolved/UKG cannot verify owner from their selected deposit schemas. | No silent replacement or ownership inference from bank numbers, links or position. | Implemented; context trust is listed as an assumption. |
| Validate nested account input once and reuse one engine per nonempty input; record source array indexes. | Preserve order/provenance without joins, deduplication or repeated source validation. | Implemented deposit adapters. |
| Preserve Prism wrapper/setup data with remaining/extras traversal outside mapped populated account lists. | Retain known employee/setup fields, empty collections and unknown nesting alongside account output. | Implemented; account extras may also appear in result-level provenance. |
| Deduction owner context is required; selected isolved employeeId must agree when present and otherwise uses supplied context. | No silent source-owner replacement; Prism/UKG assignment ownership remains trusted context when absent from source. | Implemented; unexpected isolved records retain their own source references. |
| Preserve exact non-Deduction/missing/null/unknown isolved types and UKG supplements separately, without canonicalizing their raw IDs as assignment IDs. | Retain source values without false classification or inherited ownership. | Implemented with original source indexes and existing extras traversal. |
| Deduction filtering belongs in provider adapters, not YAML conditions. | Select verified isolved Deduction items, UKG assignments.deductions, Prism employeeDeductions.deduction. | Implemented in all three deduction adapters. |
| Preserve unexpected deduction records separately; UKG code_lookup/benefits use result-level provider_fields, not deduction assignments. | A catalog definition or enrollment is not an assigned deduction or withheld amount. | Implemented; supplemental/unexpected-only input retains result data with deductions=[]. |
| Company needs no new helpers or CLI context: validate native shapes, map with fixed internal role, preserve wrappers and return companies plus metadata. | Existing helpers and source records cover the proposal; no missing identity or joins are invented. | Implemented and integration-tested for all providers. |
| Company source identity is provider + source_record_type + source_record_id. | Prism client, isolved legal_company and UKG ein are distinct scopes, not interchangeable company keys. | Model/three YAMLs/adapters connected. |
| Company adapters supply the fixed source_record_type internally. | It describes the selected source model; no new user input-type CLI option. | Implemented in company adapters; no new CLI option. |
| Company legal/DBA/federal/NAICS matches use verified descriptions; UKG EIN name/tax/country/currency remain separate. | EIN lookup is not proof of legal company name, jurisdiction or API company identity. | Model/YAMLs built. |
| isolved recursive company back-references map nested IDs only; remaining finite input stays in unmapped/extras. | Avoid infinite schema expansion, inferred joins or replacing the root legal company with parent data. | Company YAMLs built. |
| Preserve native input formats: isolved deposits are arrays; UKG deposits use deposits/_links. | Pydantic RootModel.root is an accessor, not a provider envelope. | Implemented; wrappers not invented. |
| CLI reference metadata gaps warn on stderr and persist in source_metadata.<provider>.reference_pack. | Allow normalization with honest provenance; unreadable/malformed lookup files, wrong provider and invalid lookup container still block. | Implemented in __main__.py; references.py and reference packs unchanged. |
| No API fetching, source joins, sums/reconciliation, sorting or deduplication is introduced by mapping. | Offline normalization uses supplied data and explicit context only. | Current implementation boundary. |
| Models → JSON-compatible dictionaries in adapters; dictionaries → JSON text in CLI. | Keep output validation before serialization; refuse output-file overwrite. | Implemented. |

## Schemas & Enums

| Decision | Limit / reason |
|---|---|
| Full readable canonical gender/marital/status-class/pay-basis labels only from approved or verified field dictionaries. | Approved vocabulary is not evidence that every provider uses the same source codes; preserve unmapped values. |
| Rehire is eligible / ineligible / no preference; source absence/null remains unavailable. | Prism Y/N/blank and isolved booleans have explicit rules; do not collapse all unknown/missing cases into false. |
| Preferred pronouns use one supplied/agreed value; conflicts preserve both originals with an issue and null shared value. | No arbitrary precedence. |
| Name parts and source roles stay distinct: preferred name vs nickname, gender vs reporting/designation, separate hire/change dates. | Do not merge fields solely because descriptions or values look similar. |
| State/location codes retain provider scope; ZIP text/suffix uses the documented helper conflict rules. | No global code equivalence, numeric ZIP coercion, or inferred location lookup. |
| Distinct legal/client/EIN references and their list/scalar shape remain separate. | Preserve relationship references without inventing a universal company identifier. |

Exact field destinations/types and accepted code tables are in the proposal index below; they are part of the decision record, not requests to approve every source path again.

## Provider Mappings & Gaps
<!-- Per provider: key mappings, missing data, how handled -->

### PrismHR

| Gap | Handling |
|---|---|
| ACH contract marks amount/limit required but descriptions give method-specific restrictions. | Project requiredness makes non-ID business fields optional. Conditional business validation remains deferred; preserve supplied values. |
| `updateMessage` and `extension` meanings are undocumented; Postman returned null. | Keep it optional; do not treat nonempty values as errors without evidence. |
| Employee fields with insufficient descriptions: `benefitEnrollmentCompleted`; Person: `cobraSSN`, `cobraOnly`, `taxZipCode`, `w2ElecForm`, `w2ElecFormDate`, `legacyEmployeeId`; Client: `typeClass`; Compensation: `longPayTable`, `longBasisDate`, `quartile`, `compaRatio`, `benefitsBasePay`, `taxCreditEmp`, `autoPayCode`, `profitSharing`, `wagePlanCA`, `compReviewNextDate`, `notes`, `electronicPayStub`, `irsLockInDate`, `payPeriodsPerWeek`; PayPeriodInfo: `periodCode`, `periodBase`; EeImage: `masterId`, `verifyDateTime`, `verifyUserId`; I9ImageAudit: `auditDate`, `auditUser`, `auditId`, `auditStep`; LockIns: `stateDate`, `authUser`; SkillsAndEducation: `osha10Certified`; wrapper: `updateMessage`, `extension.any`. | Missing, vague, or conflicting descriptions; meanings, units, or allowed values need clarification before semantic mapping. |

### isolved

| Gap | Handling |
|---|---|
| Deposit response has no employee-owner field. | Trust required CLI employee context; do not claim response-based verification. |
| Pay items include Deduction/Earning/Memo Calc; parameter meanings such as Amount2/Rate lack sufficient descriptions. | Filter in adapter when integrated, preserve other records/parameters; no guessed calculations. |
| employmentCategoryCode has no verified field dictionary. | Preserve raw employment_category_code; no guessed full-time/part-time label. |
| Employee and salary records both use `id`; a bare object containing only a salary ID can be interpreted as an employee record. | Keep `salary_only` for standalone salary arrays so salary IDs are not mapped as employee IDs. Bare-object identity remains ambiguous; combined input uses employee `id` with nested `salary_history`. |
| Flat employee-root `seasons` is not a declared employee field. | Supported salary data belongs in salary_history[].seasons and is validated there. Flat undeclared fields stay extras; arbitrary flattened schema merging is not supported. |

### UKG Ready

| Gap | Handling |
|---|---|
| Many deposit/deduction/company properties lack descriptions; saved deposits/benefits/paycheck list are empty. | Use only verified matches; preserve uncertain values. Synthetic tests verify structure, not live semantic completeness. |
| Deposit owner is absent; RESERVE_LIVE_CHECK behavior is undocumented. | Trust supplied owner context and preserve type; do not reinterpret reserve records as bank deposits. |
| EIN lookup is not company detail or a mapping to the API company ID. | Preserve EIN record identity/name/tax/currency/country separately. |
| No populated paycheck responses; compensation history is available from a separate API. | Map compensation history into employee compensation output; validate paychecks from documented schemas and synthetic data. Compensation history does not replace paycheck details. |

## Data Issues

| Gap / deferred review | Handling |
|---|---|
| Prism Postman/OpenAPI field-name differences (employerId/employerIds, autoPolicy/autoPolicies, hawaiiMedWaiver/hawaiiMedWaivers). | Existing aliases remain; audit conflicting simultaneous names later. |
| Generic id alone does not prove entity/owner, and arbitrary flattened mixes lack a declared schema. | Use selected entity plus supported native/named sections; preserve unclassified values, not inferred identities. |
| Payroll checks may lack employee/run references. | Preserve supplied references; leave missing links empty. Resolve associations later without guessing. |
| Conditional business rules, invalid/negative amounts, duplicates and mixed-validity input need later review. | Existing structural/source checks and helper diagnostics only; do not invent limits/reconciliation rules. |

## Testing

- Verify canonical strict types and helper rules, then source/YAML/output compatibility and adapter/CLI integration.
- Use synthetic fixtures for edge cases; saved samples supply evidence but do not establish exhaustive enum or response coverage.
- Cover missing/null/empty, zero/false, source preservation, unknown codes/extras, nested scope, context conflicts and no input mutation.
- Test real readiness blocking separately from isolated CLI integration tests. Latest completed full run: 284 tests and 3980 subtests passed.

## Write Path

- Only local JSON input/output; no provider requests or output-file overwrite.
- CLI employee client context is required for Prism employees; CLI employee owner is required for direct-deposit and deduction providers.
- All five entity adapters map all providers; payroll uses separate run/header/detail lists.

## Open Questions

- Reference metadata gaps now warn and persist in output; verification/permission evidence remains unresolved and is not relabeled.
- Payroll mapping is implemented; missing employee/run associations remain a deferred gap.
- Review remaining business edge cases and additional mappings only when evidence or implementation requires them. Universal preservation is already decided.


### Reference metadata gaps — warnings during normalization

These checks still report gaps; normalize emits stderr warnings and records them in output. check-inputs remains diagnostic and returns nonzero for these gaps. No reference metadata or permission status was changed.

| Provider | Failed condition | Current metadata / artifact |
|---|---|---|
| isolved, UKG Ready | distribution.status must equal verified | user_approved_private_upload; evidence reference is present. |
| UKG Ready | openapi.status must equal verified | not_available; actual references are cached HTML/extracted JSON schemas. |
| UKG Ready | openapi.relative_path must name an OpenAPI file | null; no approved OpenAPI filename. |
| UKG Ready | OpenAPI version/source/sha256 must all be present | source is present; version and sha256 are null. |

PrismHR passes. CLI normalization continues for the listed metadata gaps. Unreadable/invalid lookup JSON, wrong provider, invalid lookup container and unrecognized readiness failures still block. OpenAPI availability/provenance limitations are warnings; they do not assert that an artifact exists or permissions are verified.

## Future Improvements

| Improvement | Reason |
|---|---|
| Combine PrismHR payroll batch and paycheck input models; validate both sections with one model. | Separate validation paths are simpler to implement now; both supplied sections are already validated. |
| Extend the implemented shared YAML engine only for demonstrated new requirements. | Shared engine/config/helper registry already exist; avoid adding unused mapping features. |

## Detailed decision and implementation index

These documents retain per-field evidence and implementation detail; this log records the shared decisions and current status. Keep this index and the relevant log rows current with future YAML/model/adapter changes.

- [Employee proposal and implementation contract](./data-types-cpmparison/Employee%20Canonical%20Mapping%20Proposal.md)
- [Employee code review](./data-types-cpmparison/Employee%20Code%20Mapping%20Review.md)
- [Direct-deposit proposal](./data-types-cpmparison/Direct%20Deposit%20Canonical%20Mapping%20Proposal.md)
- [Deduction proposal](./data-types-cpmparison/Deduction%20Canonical%20Mapping%20Proposal.md)
- [Company proposal](./data-types-cpmparison/Company%20Canonical%20Mapping%20Proposal.md)
- [Payroll proposal](./data-types-cpmparison/Payroll%20Canonical%20Mapping%20Proposal.md)
- [PrismHR deposit implementation choices](./PrismHR%20Direct%20Deposit%20Mapper%20Implementation.md)
- [isolved/UKG deposit implementation choices](./iSolved%20and%20UKG%20Direct%20Deposit%20Mapper%20Implementation.md)

- [Company adapter implementation choices](./Company%20Mapper%20Implementation.md)

- [Deduction adapter implementation choices](./Deduction%20Mapper%20Implementation.md)

- [Payroll mapper implementation](./Payroll%20Mapper%20Implementation.md)
- [Synthetic fixture guide](../../tests/fixtures/README.md)
