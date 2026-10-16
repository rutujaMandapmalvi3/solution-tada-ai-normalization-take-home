# Decisions, assumptions and gaps

This log describes the system as it is implemented. Each decision has its reason.
Record ids, refs and merge rules are specified in full in section 4 (Tables 1–3).

Data flow:

```
bundle file → read + deserialize (CLI) → readiness check
  → per response: prepare (status, provider error, live renames) → validate against the contract
  → route lookup → map each record (YAML) → stamp id + refs
→ merge by id → re-validate records → link check → canonical document → write file (CLI)
```

## 1. Input

| Decision | Why |
|---|---|
| The input is one **bundle** file per provider: `{provider, responses: [{endpoint, params, status?, body}]}`. | One run sees a provider's company, employees, deposits, deductions and payroll together. That lets records from different responses be merged and their links checked in the same run. |
| `endpoint` is the contract path, written exactly as in the provider's contract (UKG: the documented resource path). | It selects the contract schema used to validate the body, so no guessing from shapes is needed. Different endpoints for the same entity (e.g. an employee list vs a single employee) have different schemas. |
| `params` holds the request's path and query values (owner ids such as `clientId`, `legalId`, `cid`, `employeeId`, `aid`). | Response bodies often leave out who they belong to: PrismHR deductions have no client or employee id, and isolved deposits and UKG pay-info have no employee id. The request always says who was asked for. |
| `status` is optional and defaults to 200. | It records a failed call as a failure instead of an empty dataset (the isolved demo returned HTTP 404 for payroll). |
| UKG pay-statement paths contain two `{id}` placeholders, so bundles pass them as `payroll_id` and `pay_statement_id`. | A params object cannot hold two keys both named `id`. |
| There are no CLI flags for owner ids; the CLI takes `--input` and `--output` only. | Owner ids live next to the response they describe, so a flag can never disagree with the file. |
| The input is a local file and no API is called. | The README requires local, deterministic runs. Fetching and pagination belong to a separate capture step that writes bundles. |

## 2. Contract validation (`contracts.py`)

| Decision | Why |
|---|---|
| Each response body is validated against the GET 200 response schema of its endpoint in the provider contract. No separate source-model copies of the schemas exist. | The contracts are the source of truth and already describe every field. A second hand-written copy would drift from them and double the maintenance. |
| **Sources:**<ul><li>PrismHR: OpenAPI 3.0.1.</li><li>isolved: the primary Swagger 2.0 snapshot only.</li><li>UKG Ready: `reference-schemas.json`, using the GET schema of the cached page whose name matches the endpoint (`/` → `__`, `{}` → `()`, plus `.html`). No HTML file is read.</li></ul> | These are the README-approved references. The README says not to mix the two isolved snapshots. UKG has no OpenAPI file; its extracted schemas are the closest contract. No UKG page has more than one GET schema. |
| Validation uses JSON Schema Draft 4, with `$ref` resolved inside the spec. | OpenAPI 3.0 and Swagger 2.0 schemas are Draft-4 based, and 401 of the 478 UKG schemas declare Draft 4. |
| Validation runs on the deserialized Python object, once, after `json.load`. | JSON Schema validates dicts and lists. Validating once at this layer means there is no second validation of the same data. |
| `null` counts as "not supplied". | Live PrismHR and isolved return null for most optional fields, but neither contract marks fields nullable. |
| A non-null value of the wrong type stops the run (exit 1), with the JSON path in the message. | Such a record cannot be mapped safely. Rejecting only that record instead is planned edge-case work. |
| `required` is not enforced. | The contracts mark nearly every field required, but real and synthetic responses omit most of them. Only record ids are required, and the id templates enforce them. |
| Undocumented fields, enum, length, range and pattern violations are `contract_drift` warnings in `issues`; mapping continues. | Live data drifts from the documentation in harmless ways. The drift stays visible without blocking the run. |
| Integral floats (`7.0`) count as integers. | Draft 4 alone rejects them, but they are valid ids, and the identifier helper accepts them. |
| The HTTP status and the provider's own failure flag are checked before validation (PrismHR `errorCode` must be `"0"`). | A failed response has no usable body. PrismHR reports failures inside HTTP 200 bodies; isolved and UKG use the HTTP status. |
| Four live PrismHR field spellings are renamed to the contract spelling before validation, scoped by parent key: `payrollVoucher` → `payrollVouchers` (top level), `person.employerId`, `person.autoPolicy`, `client.hawaiiMedWaiver`. If both spellings are supplied, nothing is renamed. | The live demo uses these singular names. Renaming once means validation and YAML only ever see contract names. The scoping matters: `clientMaster.employerId` is a real singular contract field. |
| Fields the live demo returns but the contract does not list are declared in `LIVE_FIELDS`: PrismHR client-master, employee `compensation.payPeriodsPerWeek` and voucher fields, isolved pay-item `balance`, UKG `ein_name` and payroll `ein.ein_country_id`. | YAML may map them and preflight stays strict. Validation still reports them as drift, because the contract does not list them. |

## 3. Mapping (routes, YAML, engine)

| Decision | Why |
|---|---|
| Each provider adapter is a **route table**: endpoint → one or more routes. A route gives:<ul><li>the canonical record type;</li><li>the path to the records (`""`, `[]`, `employee[]`, `employee[].directDeposit.achVoucher[]`);</li><li>the YAML file;</li><li>context values;</li><li>an optional filter (`where`), ignored paths, owner checks and fallbacks;</li><li>the id and ref templates.</li></ul> | Provider differences are declared as data in one place per provider. The pipeline that runs the routes is shared. |
| Template placeholders are `{params.x}`, `{record.x}` and `{parent.x}` (`parent` = the enclosing record, e.g. the employee around a PrismHR deposit). | Every id part and ref says exactly where its value comes from. |
| One shared `MappingEngine` runs the provider YAML files on plain dict records. | Mapping rules stay declarative and identical in behaviour across providers. The YAML loader rejects duplicate keys, the config rejects unknown keys and overlapping targets, and helpers come from an allowlist. |
| YAML source paths are **preflighted** against the contract schema when an engine is built:<ul><li>unknown field names fail;</li><li>a path cannot walk into a list without `[]`;</li><li>a list rule needs a list source.</li></ul>Only untyped or object nodes without listed properties accept any field. | A typo or a wrong shape is caught at load time, not as silently missing data. |
| Unused source fields are split by the contract: fields the contract declares go to `provider_fields.<p>.unmapped`; fields it does not declare go to `source_extras.<p>`. | Nothing supplied is lost, and known-but-unmapped data stays separate from unknown data. |
| UKG employee list items are mapped with the employee detail schema (route key `schema`). | The list schema is a cut-down view of the same employee resource, and one YAML file covers both. Validation still uses the list schema. |
| Some responses are a **section** of one canonical record: isolved salaries, UKG pay-info, UKG compensation history.<ul><li>The pipeline wraps the body as `{section: body}` (route key `wrap`).</li><li>Each section has its own YAML file: `employee_salaries`, `employee_pay_info`, `employee_compensation`.</li></ul> | Each body is validated against its own endpoint while still mapping into the employee record. The section stays together under `provider_fields`. |
| Records that belong to someone else in the same response are mapped by their own route. The parent route drops that path (route key `ignore`; PrismHR `directDeposit.achVoucher` is dropped from the employee). | The deposit accounts become deposit records and are not duplicated inside the employee. |
| Filters live in routes, not in YAML: isolved pay items map only `payItemType == "Deduction"`. Other items are kept under `provider_fields.isolved.filtered_records` with their path and the reason. | The pay-items endpoint also returns Earning and Memo Calc items. They are not deductions, but supplied data is never dropped. |
| Responses from an endpoint with no route (UKG `lookup/deduction-codes`, `/employees/{aid}/benefits`) are kept verbatim under `provider_fields.<p>.unrouted_responses`. | A code catalog or benefit enrollment is not an assigned deduction, but the data stays available. |
| Each response's wrapper fields (everything except the record list itself, e.g. PrismHR `errorCode`, UKG `_links`, fields beside a nested record list) are kept in `source_metadata.<p>.responses[]` with the endpoint and params. | This is the response-level provenance and context that belongs to no single record. |
| Each record lists its `sources` (response index, endpoint, JSON path). | Every merged record shows which responses built it. |

## 4. Identity and relationships

| Decision | Why |
|---|---|
| Every record gets `id = provider:record_type:owner_scope[:employee_key]:record_key` (Table 1 below). | One unambiguous key across providers and record types. Source ids repeat across owners (e.g. PrismHR employee ids per client), and some records have no source id. |
| **Owner scope:** PrismHR `clientId`, isolved `clientId:legalId`, UKG `cid`. It always comes from `params`. | That is the level at which provider ids are unique, and bodies rarely carry it. |
| The record key is the provider's own id. When a response is about one record and has no id, the key comes from `params` (route key `fill_record`, e.g. UKG statement detail → `pay_statement_id`). When the provider has no id at all, the smallest stable natural key is used:<ul><li>PrismHR deposit: routing + account number;</li><li>PrismHR deduction: deduction code.</li></ul> | A key must identify the record and stay the same when its settings change. That is why amounts and methods are never part of a key. |
| Refs are foreign keys holding another record's id, built from values in the same response, with the parent's own template. Nothing is looked up.<ul><li>`company_ref` is on every non-company record and on UKG EIN records.</li><li>`employee_ref` is on deposits, deductions and paychecks.</li><li>`payroll_run_ref` is on paychecks where the run id is available.</li></ul> | A link is then a plain equality check that works the same way for every provider. |
| Refs are stored on every output record, not once per file. | Each record stands alone in the output. |
| Existing source-id fields (`employee_id`, `deposit_id`, `source_record_id`, `payroll_run_id`, …) keep their source meaning next to the canonical `id`. | Consumers can still see and search by the provider's own ids. |
| Records with the same `id` from different responses **merge**:<ul><li>a missing field is filled from the other record;</li><li>objects merge field by field;</li><li>lists are joined;</li><li>a differing value keeps the first one and adds a `merge_conflict` warning.</li></ul>The merged record is validated again against its canonical model. | Several responses describe one record: an isolved employee and its salaries; a UKG employee, its pay-info and its compensation history; a UKG statement header and its detail. Re-validation catches merged fragments that are not a valid record together. |
| The UKG company is the `cid` (`source_record_type: company`), built from the EIN lookup response. EIN items stay separate `ein` company records with `company_ref` pointing to it. | UKG has no company-profile endpoint. Employees belong to a `cid`, not to an EIN. |
| A `params` owner id that disagrees with the owner id in the body stops the run. Checked for: PrismHR client master and employees/deposits, isolved employee detail and deductions, UKG employee detail. | The source is never silently overwritten. |
| **When values are missing:**<ul><li>a missing id part stops the run, naming the template;</li><li>a missing ref part leaves the ref empty and adds a `missing_ref` warning;</li><li>a ref whose target is not in the bundle adds a `dangling_link` info issue.</li></ul> | An id is required for merging; a missing link is information. Partial bundles are normal. |

In the tables, **P** is the response's request `params`, **R** the record itself, and
**Par** the enclosing record (e.g. the PrismHR employee around a deposit). Ids are
computed independently in each response, so the same real-world record gets the same
id everywhere; that equality is what connects responses.

**Table 1: record ids**

| Entity | PrismHR | isolved | UKG Ready |
|---|---|---|---|
| company | `prismhr:company:{P.clientId}` | `isolved:company:{P.clientId}:{R.id}` (R.id = legal id) | `ukg-ready:company:{P.cid}`; EIN: `ukg-ready:company:{P.cid}:ein:{R.id}` |
| employee | `prismhr:employee:{P.clientId}:{R.id}` | `isolved:employee:{P.clientId}:{P.legalId}:{R.id}`; salaries: `…:{P.employeeId}` | `ukg-ready:employee:{P.cid}:{R.id}`; pay-info and compensation: `…:{P.aid}` |
| direct_deposit | `prismhr:direct_deposit:{P.clientId}:{Par.id}:{R.transitNum}:{R.accountNum}` | `isolved:direct_deposit:{P.clientId}:{P.legalId}:{P.employeeId}:{R.id}` | `ukg-ready:direct_deposit:{P.cid}:{P.aid}:{R.id}` |
| deduction | `prismhr:deduction:{P.clientId}:{P.employeeId}:{R.deductionCode}` | `isolved:deduction:{P.clientId}:{P.legalId}:{P.employeeId}:{R.id}` | `ukg-ready:deduction:{P.cid}:{P.aid}:{R.id}` |
| payroll_run | `prismhr:payroll_run:{P.clientId}:{R.batchId}` | `isolved:payroll_run:{P.clientId}:{P.legalId}:{P.paygroupId}:{R.id}` | `ukg-ready:payroll_run:{P.cid}:{R.id}` |
| paycheck | `prismhr:paycheck:{P.clientId}:{R.voucherId}` | `isolved:paycheck:{P.clientId}:{P.legalId}:{R.id}` | `ukg-ready:paycheck:{P.cid}:{R.id}`; detail without id: `…:{P.pay_statement_id}` |

**Table 2: refs** (the key part; the full ref is `provider:record_type:` + the parent's key from Table 1)

| Ref | PrismHR | isolved | UKG Ready |
|---|---|---|---|
| company_ref | `{P.clientId}` | `{P.clientId}:{P.legalId}` | `{P.cid}` |
| employee_ref (deposit) | `{Par.id}` | `{P.employeeId}` | `{P.aid}` |
| employee_ref (deduction) | `{P.employeeId}` | `{P.employeeId}` | `{P.aid}` |
| employee_ref (paycheck) | `{R.employeeId}` | `{R.employeeId}` | `{R.employee.account_id}` |
| payroll_run_ref (paycheck) | `{R.batchId}` | none: checks carry no run id | `{P.payroll_id}` |

**Table 3: when values are missing or disagree**

| Situation | Behaviour |
|---|---|
| Owner-scope param missing from **P** (e.g. no `clientId`) | No id can be built. The run stops with an error naming the response, the template and the missing value. |
| Record key missing from **R** (e.g. an employee without `id`) | The fallback in Table 1 is used if there is one (UKG pay-statement detail → `P.pay_statement_id`). Otherwise the run stops with the same error. |
| No provider id by design (PrismHR deposit, PrismHR deduction) | The natural key in Table 1 is used. If any of its fields is missing, the run stops with the same error. |
| Two different records produce the same id | They are merged. Differing values keep the first one and add a `merge_conflict` issue. If this happens for real, the key needs another stable field (e.g. PrismHR `voucherTypeOverride`). |
| A value needed for a ref is missing (e.g. a paycheck without `employeeId`) | The ref stays empty, a `missing_ref` warning is added, and the record is still output. |
| A ref by design has no source (isolved `payroll_run_ref`) | The ref stays empty, with no issue. This is a known gap. |
| A ref points to a record not in the bundle | The record is kept and a `dangling_link` info issue is added. A partial bundle is normal. |
| A **P** owner id disagrees with the body (e.g. `P.employeeId` ≠ the body's employee id) | The run stops with an error. The source is never silently overwritten. |

## 5. Canonical output

| Decision | Why |
|---|---|
| One run writes one document:<ul><li>`provider`;</li><li>`companies`, `employees`, `direct_deposits`, `deductions`, `payroll_runs`, `paychecks`;</li><li>`provider_fields`, `source_metadata`, `issues`.</li></ul> | All entities and their links can be checked together, and the document is written even when a list is empty. |
| A UKG pay-statement header and its detail are one paycheck. | Both describe the same statement and share its id. |
| Canonical models are strict Pydantic models with `extra="forbid"`: ids are strings and dates are dates. Conversion happens in YAML helpers, never by implicit coercion. Merged records are re-validated through a JSON round trip. | Wrong output types are bugs to catch, not values to coerce silently. |
| Unset, null and empty stay distinct (`exclude_unset`). Zero and `false` are kept. No business defaults are invented. | Supplied values are not lost, and missing ones are not made up. |
| Business fields are shared only when meanings match. Unverified codes, units and bases stay provider-scoped, and source values are kept in `original_values` with a `mapping_issue` when a conversion fails. | A similar field name or another field's lookup table is not evidence of the same meaning. |
| Issues have a severity (`warning` or `info`), a code, a path and a message: `contract_drift`, `missing_ref`, `merge_conflict`, `dangling_link`. | Problems that do not stop the run stay machine-readable in the output. |

## 6. Entity mapping choices

| Decision | Why |
|---|---|
| **Company:**<ul><li>Identity is `source_record_type` + `source_record_id`. The types are `client` (PrismHR), `legal_company` (isolved), `company` and `ein` (UKG).</li><li>isolved companies come from `GET /api/clients/{clientId}/legals` (a list).</li></ul> | These are distinct organisational levels and must not be merged. The primary isolved snapshot has no single-legal-company GET. |
| **Company fields:**<ul><li>Legal, DBA, federal-id and NAICS values are mapped only where the descriptions match.</li><li>UKG EIN name, tax id, country and currency stay EIN-specific.</li><li>Recursive isolved back-references keep only nested ids.</li></ul> | An EIN lookup does not prove the legal company name. Recursive structures must not be expanded without limit. |
| **Employee:** gender, isolved EEO override and PrismHR gender designation stay separate. So do preferred name vs nickname, and the separate hire and change dates. | They serve different roles. |
| **Employee:** pronouns use one supplied value; conflicting sources keep both originals, an issue, and a null shared value. | No arbitrary precedence. |
| **Employee:** rehire is `eligible` / `ineligible` / `no preference`; absent or null stays unavailable. | PrismHR Y/N/blank and isolved booleans have explicit rules. Unknown is not "no". |
| **Employee:** state and location codes stay provider-scoped; ZIP text and suffix follow the helper's conflict rules. Ethnic code, ethnic-origin description and the Hispanic flag stay separate. | No crosswalk or global code table is verified. |
| **Direct deposit:** a canonical fixed `allocation_amount` comes only from PrismHR method `F` and UKG `FLAT_AMOUNT` (via `conditional_number`). PrismHR `P`/`PN`/`FS`/`B` and limits, isolved amount and percent, and UKG percentage, sequence and calculation fields stay provider-scoped. | Only the fixed-amount meaning is verified across providers. Percentage scale, basis and ordering are not. |
| **Direct deposit:** only account setup is mapped. Paycheck payments stay in payroll, HSA stays outside, and UKG `RESERVE_LIVE_CHECK` keeps its type. | These have different business roles. |
| **Deduction:** isolved deductions take `employee_id` from the record, falling back to `params.employeeId`. The request owner is also kept as `provider_fields.isolved.request_employee_id`. | Ownership is explicit and provenance is kept. |
| **Deduction:** unclear amounts and calculation parameters (e.g. isolved `Amount2`) are kept without calculation. | No cross-provider calculation rule is documented. |
| **Payroll:** runs and paychecks are separate records, and all components (earnings, hours, taxes, deductions, benefits, payments) stay in provider scope unless a shared meaning is verified. | No arithmetic or guessed equivalence. |
| **Payroll:** PrismHR `checkNumber` and `checkNum` are resolved with `identifier_alias`; unequal values give null, keep both originals, and add an issue. | Neither alias overwrites the other, and leading zeros stay significant. |

## 7. CLI and reference pack

| Decision | Why |
|---|---|
| `normalize --input <bundle> --output <file>`. The provider comes from the bundle's `provider` field; there are no `--provider` or `--entity` flags, because record types come from each endpoint's routes. | One source of truth for the provider, and one run normalizes every entity in the bundle, so records merge and links are checked together. |
| The output is written only to the given path, in create-only mode. An existing file stops the run (exit 1) and stays untouched. The parent folder must exist. No file is written when the run stops. | Never overwrite results; no partial output. |
| Exit codes:<ul><li>0 = document written, even with issues;</li><li>1 = unusable input (unreadable file, bad bundle shape, provider failure, wrong type, unknown endpoint, missing id, owner conflict);</li><li>2 = unreadable or mismatched reference pack.</li></ul> | Callers can tell "processed with notes" from "nothing usable". |
| Reference-pack metadata gaps are printed as warnings and recorded once in `source_metadata.<p>.reference_pack`. These gaps are the unverified isolved/UKG distribution permission and the missing UKG OpenAPI artifact. `check-inputs` still reports them and exits 2. | The README approves using the pack, and these gaps cannot be fixed in code. They stay visible without blocking normalization. |

## 8. Fixtures and tests

| Decision | Why |
|---|---|
| Fixtures are three generated bundles, `tests/fixtures/<provider>.bundle.json`, each one connected synthetic company. They are produced by `scripts/generate_fixtures.py` with seed 42 and checked with the same contract layer before writing. | Ids, refs and merges are exercised end to end, and the generator reproduces the bundles byte for byte. |
| The reviewed `<provider>.expected.json` files are compared in full by `test_bundle_cli.py`. Tests never regenerate them. | Any change to the output must be reviewed deliberately. |
| Test suites by layer:<ul><li>contracts;</li><li>engine and YAML preflight;</li><li>per-provider field mapping;</li><li>relationships (Table 1 ids, Table 2 refs, merges, missing values);</li><li>CLI;</li><li>generator;</li><li>reference integrity.</li></ul>Latest full run: 216 tests, 3,337 subtests passed. | Each layer's rules are tested where they live. |

## Assumptions

- **Request parameters are correct.** The bundle's `params` are the values used in the request that produced each body. *Reason:* bodies omit owner ids; where a body does carry one, it is checked against `params`.
- **PrismHR success code.** `errorCode == "0"` means success. *Reason:* the saved demo responses and the OpenAPI operations.
- **PrismHR work location.** PrismHR `client.homeLocation` is the employee's work location (`work_location_code`). *Reason:* confirmed role; codes stay provider-scoped.
- **PrismHR gender labels.** PrismHR gender `M`/`F`/`X`/`D`/`U` map to male / female / non-binary / declined / unknown by the approved interpretation, not a verified provider dictionary. *Reason:* the contract lists the codes without meanings; originals are kept.
- **UKG employee id.** UKG `id` is the employee id; UKG `employee_id` is kept as `ukg_employee_id`. *Reason:* the demo GET by employee succeeded with `id`.
- **UKG compensation time.** UKG compensation `time` and `standard_work_day` are in milliseconds. *Reason:* stated in the cached schema text for those fields only; no other field's unit is inferred.

## Gaps

**General**
- **Wrong types stop the whole run.** One wrong-typed value stops the run instead of rejecting only its record.
- **Merging can duplicate list entries.** Merging joins lists, so supplying the same response twice duplicates list entries (history, paycheck lines).
- **No pagination.** Paged responses are mapped page by page, and their page metadata is only kept in the wrapper.
- **No business-rule checks yet.** Conditional rules are not checked: amount vs percent, PrismHR method-specific amount/limit, negative amounts, duplicate ids inside one response. These are planned edge cases.

**PrismHR**
- Fields with missing, vague or conflicting descriptions are kept without semantic mapping:
  - `benefitEnrollmentCompleted`;
  - Person: `cobraSSN`, `cobraOnly`, `taxZipCode`, `w2ElecForm`, `w2ElecFormDate`, `legacyEmployeeId`;
  - Client: `typeClass`;
  - Compensation: `longPayTable`, `longBasisDate`, `quartile`, `compaRatio`, `benefitsBasePay`, `taxCreditEmp`, `autoPayCode`, `profitSharing`, `wagePlanCA`, `compReviewNextDate`, `notes`, `electronicPayStub`, `irsLockInDate`, `payPeriodsPerWeek`;
  - PayPeriodInfo: `periodCode`, `periodBase`;
  - EeImage: `masterId`, `verifyDateTime`, `verifyUserId`;
  - I9ImageAudit: `auditDate`, `auditUser`, `auditId`, `auditStep`;
  - LockIns: `stateDate`, `authUser`;
  - SkillsAndEducation: `osha10Certified`;
  - wrapper: `updateMessage`, `extension`.
- **Same account twice.** Two deposits on the same routing + account number (e.g. with different `voucherTypeOverride`) share one id and merge, with a `merge_conflict`.

**isolved**
- **No run link on checks.** Checks carry no payroll run id, so paychecks have no `payroll_run_ref`.
- **Undocumented pay-item parameters.** Pay-item parameters such as `Amount2` and `Rate` are undocumented, and `employmentCategoryCode` has no verified dictionary. Both are kept raw.
- **Flat `seasons` is not a salary field.** A `seasons` field at the employee root is not a declared employee field, so it stays in `source_extras`. Salary seasons belong to the salaries response.

**UKG Ready**
- **No company name.** No company-profile endpoint exists, so the cid company has no name.
- **EIN links.** EINs are linked to the company, but `ein` on employees is documented only for multi-EIN companies.
- **Thin descriptions.** Many deposit, deduction and company properties lack descriptions. `RESERVE_LIVE_CHECK` behaviour is undocumented.
- **Live data was empty or unavailable.** The live employee-deductions endpoint returned 404, and the saved deposits, benefits and pay statements were empty. These are mapped from the contract and synthetic data only.
- **Undocumented link.** `_links.country-fields` on employees is undocumented, so it stays in `source_extras`.

**Reference pack** (reported, not blocking)

| Provider | Gap | Current metadata |
|---|---|---|
| isolved, UKG Ready | `distribution.status` is not `verified` | `user_approved_private_upload`; evidence reference present |
| UKG Ready | no OpenAPI artifact | `openapi.status: not_available`; the references are cached HTML and extracted JSON schemas |
| UKG Ready | OpenAPI version and checksum | `null` |

## Open items

- **Edge-case validation:** per-record rejection, business-rule checks, de-duplication on merge (planned).
- **Live capture:** a capture step that fetches and paginates provider APIs into bundles (not built).
- **Write path:** writing canonical data back to a provider (not built).

## See also

- [Synthetic fixture guide](../../tests/fixtures/README.md)
