# Decisions, assumptions and gaps

This log lists the decisions that change the output or how a run behaves, each with its
reason. How the code is organised is in [README.md](./README.md). Record ids, refs and
merge rules are specified in full in section 4 (Tables 1–3).

## 1. Input

| Decision | Why |
|---|---|
| The input is one **bundle** file per provider: `{provider, responses: [{endpoint, params, status?, body}]}`. The provider comes from the bundle's `provider` field; the CLI takes only `--input` and `--output`. | One run sees a provider's company, employees, deposits, deductions and payroll together, so records from different responses merge and their links are checked in the same run. |
| Each response keeps its request `params` (e.g. `clientId`, `employeeId`). | They are used to build each record's composite id: employee `007` of PrismHR client `001` gets `prismhr:employee:001:007`. |
| A response whose status is not 200 stops the run. | A failed call is a failure, not an empty dataset. |
| The input is a local file; no API is called. | The README requires local, deterministic runs. |

## 2. Contract validation

| Decision | Why |
|---|---|
| Each response body is validated against its endpoint's response schema in the provider contract: PrismHR OpenAPI, the primary isolved Swagger snapshot, UKG's extracted reference schemas. | The contracts are the source of truth; a second hand-written copy would drift from them. |
| A value of the wrong type stops the run. `null` counts as "not supplied". `required` is not enforced. | A wrongly typed record cannot be mapped safely. Live data uses null for missing values, and the contracts mark nearly every field required although responses omit most of them. |
| Other differences from the contract are `contract_drift` warnings, not rejections: the value is kept and mapping continues. For example, a value outside an enum (UKG `account_type: "MONEY"`), too long (isolved `routingNumber` with 10 digits), out of range (isolved deposit `percent: 150`), not matching a pattern (isolved `zipCode: "ABC"`), or an undocumented field where the schema forbids them. | Live data drifts from the documentation in harmless ways; the drift stays visible without blocking the run. |
| **Checks are structural only:** types, contract rules and the canonical label sets. No value is checked for plausibility (see Gaps). | The contracts document types and formats, not business rules. |
| Known live PrismHR field spellings are renamed to the contract spelling before validation. | Validation and mapping then only see contract names. |

## 3. Mapping

| Decision | Why |
|---|---|
| Each provider has a route table (which records each endpoint holds) and YAML mapping rules, run by one shared engine. The rules are checked against the contract and the canonical model before any record is mapped. | Provider differences are data, not code, and a typo fails at once instead of silently losing data. |
| **Nothing supplied is lost:** fields no rule maps go to `provider_fields.<p>.unmapped` (declared by the contract) or `source_extras.<p>` (undeclared)| Known-but-unmapped data stays separate from unknown data, and every input value can be found in the output. |
| A value a helper cannot convert (bad date, unknown code) becomes `null` with a `mapping_issue`; only an unusable id stops the run. | One bad field should not lose the whole record. |
| Every record lists its `sources` (response, endpoint, path), and every converted value keeps its original in `original_values`. | Each output value can be traced back to the input. |
| Some responses are a section of one record (e.g. salaries, pay-info) and are mapped into that record; records that belong to another route (e.g. deposit accounts inside an employee) are mapped only by that route. | Each body is validated against its own endpoint, and no data is duplicated. |

## 4. Identity and relationships

| Decision | Why |
|---|---|
| Every record gets `id = provider:record_type:owner_scope[:employee_key]:record_key` (Table 1). The owner scope always comes from `params`: PrismHR `clientId`, isolved `clientId:legalId`, UKG `cid`. | Source ids repeat across owners, and bodies rarely carry the owner. |
| The record key is the provider's own id. Without one, the smallest stable natural key is used: PrismHR deposit = routing + account number, PrismHR deduction = deduction code. | A key must stay the same when settings change, so amounts and methods are never part of it. |
| Refs hold the parent's id, built from values in the same response with the parent's own template (Table 2). Nothing is looked up. | A link is a plain equality check, the same for every provider. |
| Records with the same `id` **merge**: missing fields are filled, objects merge, lists are joined, and a differing value keeps the first one with a `merge_conflict` warning. The merged record is validated again. | Several responses describe one record (e.g. a UKG employee from profile, pay-info and compensation). |
| The UKG company is the `cid`; EINs are separate `ein` company records linked to it. | UKG has no company-profile endpoint, and employees belong to a `cid`. |
| A `params` owner id that disagrees with the body stops the run. | The source is never silently overwritten. |

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
| An id or ref value is a bool, decimal number or object | The run stops. |
| Two different records produce the same id | They are merged. Differing values keep the first one and add a `merge_conflict` issue. |
| A value needed for a ref is missing (e.g. a paycheck without `employeeId`) | The ref stays empty, a `missing_ref` warning is added, and the record is still output. |
| A ref by design has no source (isolved `payroll_run_ref`) | The ref stays empty, with no issue. This is a known gap. |
| A ref points to a record not in the bundle | The record is kept and a `dangling_link` info issue is added. A partial bundle is normal. |
| A **P** owner id disagrees with the body (e.g. `P.employeeId` ≠ the body's employee id) | The run stops with an error. |

## 5. Canonical output

| Decision | Why |
|---|---|
| One run writes one document: `provider`; `companies`, `employees`, `direct_deposits`, `deductions`, `payroll_runs`, `paychecks`; `provider_fields`, `source_metadata`, `issues`. | All entities and their links can be checked together. |
| Canonical models are strict: unknown fields are rejected, ids are strings, dates are dates, labels come from fixed sets. Values are converted only by the mapping helpers. | Wrong output types are bugs to catch, not values to coerce. |
| Unset, null and empty stay distinct. Zero and `false` are kept. No business defaults are invented. | Supplied values are not lost, and missing ones are not made up. |
| Business fields are shared only when meanings match. Unverified codes, units and bases stay provider-scoped. | A similar field name or another field's lookup table is not evidence of the same meaning. |
| Problems that don't stop the run are machine-readable `issues` (severity, code, record id, path, message): `contract_drift`, `missing_ref`, `merge_conflict`, `dangling_link`. | Callers can filter and act on them. |

## 6. Entity mapping choices

| Decision | Why |
|---|---|
| **Company:** client (PrismHR), legal company (isolved), company and EIN (UKG) are distinct organisational levels; names and tax ids are mapped only where the descriptions match. | Different levels must not be merged, and an EIN lookup does not prove the legal company name. |
| **Employee:** fields that look alike but serve different roles stay separate (e.g. gender vs EEO override, preferred name vs nickname); codes are decoded only with documented meanings, and conflicting sources give `null` with both originals kept. | No guessed crosswalk and no arbitrary precedence. |
| **Direct deposit:** only a fixed amount is shared (PrismHR method `F`, UKG `FLAT_AMOUNT`); percentages, ordering and other methods stay provider-scoped. Only account setup is mapped. | Only the fixed-amount meaning is verified across providers. |
| **Deduction:** amounts, parameters and schedule codes whose meaning is unclear are kept raw, without calculation. | No cross-provider calculation or schedule rule is documented. |
| **Payroll:** runs and paychecks are separate records; earnings, hours, taxes, deductions, benefits and payments stay provider-scoped unless a shared meaning is verified. | No arithmetic or guessed equivalence. |

## 7. CLI and run control

| Decision | Why |
|---|---|
| The output is written only to the given path, in create-only mode: an existing file stops the run and stays untouched, and no file is written when the run stops. | Never overwrite results. |
| Exit codes: 0 = document written (even with issues); 1 = unusable input; 2 = unreadable or mismatched reference pack. | Callers can tell "processed with notes" from "nothing usable". |
| Reference-pack metadata gaps are printed as warnings and recorded in the output, without blocking the run. | The README approves using the pack; the gaps cannot be fixed in code but stay visible. |

## Assumptions

- **Request parameters are correct.** The bundle's `params` are the values used in the request that produced each body. *Reason:* bodies omit owner ids; where a body carries one, it is checked against `params`.
- **PrismHR gender labels.** `M`/`F`/`X`/`D`/`U` map to male / female / non-binary / declined / unknown. *Reason:* the contract lists the codes without meanings, so this is our interpretation; originals are kept.
- **UKG employee id.** UKG `id` is the employee id; UKG `employee_id` is kept as `ukg_employee_id`. *Reason:* the demo GET by employee succeeded with `id`.
- **UKG paycheck employee.** A pay statement's `employee.account_id` is the employee's `aid`, so it builds `employee_ref`. *Reason:* it is the only employee identifier on the statement; not verified with live data.

## Gaps

**General**
- **No plausibility or business-rule checks.** Values are checked for type and format only. Nothing rejects or flags a birth or hire date in the future, a negative age or amount, an end date before a start date, amount vs percent conflicts, PrismHR method-specific amount/limit rules, or duplicate ids inside one response.
- **Values that break contract rules are accepted.** Enum, length, range and pattern violations only add a `contract_drift` warning; the value still reaches the canonical output (e.g. a 150% deposit allocation, a 10-digit routing number, `postal_code: "ABC"`). PrismHR's contract declares none of these rules for the endpoints used, so PrismHR values are never checked this way.
- **One bad response stops the whole run.** A wrong type, a failed status (e.g. the isolved demo's 404 for payroll) or a provider error in any response means no output for the bundle, instead of skipping that response or record.
- **Differently written ids split a record.** Ids use values exactly as written, so employee `"7"` in one response and `"007"` in another (or UKG `aid` `7` vs `"007"`) become two employee records with no warning; refs point to only one of them.
- **Merging can duplicate list entries.** Supplying the same response twice doubles its list entries (history, paycheck earnings, deductions, taxes, benefits) with no issue.
- **Duplicate ids inside one response are merged**, with a `merge_conflict` for differing values, not rejected.
- **Id parts are not escaped.** A value containing `:` is accepted (e.g. `prismhr:deduction:001:007:A:B`), so two different ids could look alike.
- **Repeated warnings.** A merged record can carry the same `missing_ref` warning once per fragment (e.g. a UKG paycheck header and detail without `payroll_id`).
- **An empty bundle** (`responses: []`) exits 0 with an empty document and no issue.
- **No pagination or live capture.** Paged responses are mapped page by page; bundles must be captured elsewhere.
- **Output is create-only but not atomic.** An I/O error during the write could leave a partial file.
- **No write path** back to a provider.

**PrismHR**
- **Masked account numbers.** Live deposits return `accountNum` masked (`***********`), so all deposits at one bank share one id and merge with a `merge_conflict`. Two deposits on the same account (e.g. different `voucherTypeOverride`) do the same.
- Fields with missing, vague or conflicting descriptions (e.g. `benefitEnrollmentCompleted`, `annualPay`, many compensation and audit fields) are kept in PrismHR-specific fields, never in shared canonical ones.

**isolved**
- **No run link on checks.** Checks carry no payroll run id, and the run number is not unique without pay group and date, so paychecks have no `payroll_run_ref`.
- **No live payroll data.** Payroll history and checks returned 404 in the demo; payroll is mapped from the contract and synthetic data only.
- **Undocumented pay-item parameters.** `Amount2`, `Rate` and `employmentCategoryCode` have no verified meaning and are kept raw.
- **Flat `seasons`** at the employee root is not a declared employee field, so it stays in `source_extras`.

**UKG Ready**
- **No company name.** No company-profile endpoint exists, so the cid company has no name.
- **EIN links.** EINs are linked to the company, but `ein` on employees is documented only for multi-EIN companies.
- **Deprecated deposit endpoint.** The cached direct-deposits page is marked deprecated; no replacement is verified. `RESERVE_LIVE_CHECK` behaviour is undocumented.
- **Live data was empty or unavailable.** Employee deductions returned 404, and deposits, benefits and pay statements were empty, so these are mapped from the contract and synthetic data only.
- **Undocumented link.** `_links.country-fields` on employees stays in `source_extras`.
- **Employee list schema is thinner than the detail.** It does not declare `dates.birthday`, so a list response with a birthday gets a `contract_drift` warning even though the field is mapped (with the detail schema).

## See also

- [Synthetic fixture guide](../../tests/fixtures/README.md)
