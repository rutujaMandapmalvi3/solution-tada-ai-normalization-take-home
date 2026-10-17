# Decisions, assumptions and gaps

I turn saved payroll data from PrismHR, isolved and UKG Ready into one shared
format. The [README](../README.md) explains how to run the program.

Here, an **entry** means one company, employee, deposit, deduction, payroll run or
paycheck. **Mapping** means copying, renaming or converting its fields.

## 1. Input

| Choice | Reason |
|---|---|
| One bundle file per provider, which include provider name, endpoints,and params with its saved responses together. | Related information can be combined and checked in one run. |
| Keep request details (`params`) beside each response. | Returned data often omits company or employee IDs. |
| Read local files; do not call provider APIs. | The program runs without credentials or network access. |
| Stop on a failed response; a missing HTTP status means 200. | A failed request should not look like an empty result. |

## 2. Contract validation

| Choice | Reason |
|---|---|
| Check incoming data against the supplied provider definitions. | Avoid maintaining a second copy of the provider's field rules. |
| Stop on wrong types, but allow null and omitted fields. | Real responses omit many fields that the documentation calls required. IDs still need enough information to be built. |
| Warn about other detected differences and continue. | A longer-than-allowed value or an unfamiliar code should stay visible without losing everything else. |
| Fix known field-name differences before checking and mapping. | The rest of the code can use one spelling. |

The references used are PrismHR OpenAPI, the **primary** isolved Swagger file, and
UKG's extracted schemas. These checks do not decide whether values make business sense.

## 3. Mapping

| Choice | Reason |
|---|---|
| Use provider routes to find entries and YAML files to describe field changes. | One shared engine can handle all providers. |
| Keep fields that are not mapped. | Unused data should not disappear. |
| Save where each entry came from and the original inputs for converted fields. | Output can be traced back to the input. |
| Combine extra employee information, such as salary history, into that employee. | The same employee should not appear as several separate entries. |

For example, `hourlyPay: "abc"` becomes `hourly_rate: null`; other fields still map.
The output keeps `"abc"` in `source_metadata.original_values` and the reason in
`source_metadata.mapping_issues`. Bad IDs or structural errors can still stop the run.

Unused fields go in `provider_fields`; unexpected fields go in `source_extras`.
Deposit accounts are mapped separately, not duplicated inside employees.

Unused: the provider may supply useful information I haven’t mapped yet, “Unused” means an input field that no mapping rule uses.

## 4. Identity and relationships

| Choice | Reason |
|---|---|
| Build an ID from:<br>- Provider name<br>- Entity name<br>- Company ID from `params`<br>- Employee ID, when needed<br>- Provider ID or stable identifying fields<br>Format: `provider_name:entity_name:company_id[:employee_id]:entry_key`. | Identify each entry across providers and companies, and combine information about the same entry. |
| Use refs such as `company_ref` to hold another entry's ID. | Connect employees, companies and paychecks. |
| Combine entries with matching IDs: fill missing values, join lists, and keep the first conflicting value with a warning. | Several responses can describe the same employee or paycheck. |
| Stop if an ID cannot be built; warn if a link or linked entry is missing. | IDs are needed to combine entries; partial links can still be useful. |
| Stop if a checked ID in the same response’s body differs from its matching ID in `params`. | Avoid attaching data to the wrong company or employee. |
| For PrismHR, identify deposits by routing and account numbers, and deductions by their code. | These entries have no provider ID; changing amounts should not change their identity. |

## 5. Canonical output

“Canonical” means my shared output format. One document holds six lists, preserved
data and warnings. Check output types before and after combining entries.

Keep zero and false; do not invent missing business values. Some helpers turn blank
text into null. Share fields only when their meanings match.

General warnings go in `issues`. Conversion warnings stay with the affected entry
in `source_metadata.mapping_issues`.

## 7. CLI and run control

- Never overwrite an existing output file. Finish processing before writing starts.
- Exit codes: 0, 1, 2
**Exit 0:** means success even with warnings
**Exit 1:** prints the error reason, such as “file already exists” or an invalid field type.
**Exit 2:** prints JSON describing the blocking reference-pack problems.
- Known reference metadata gaps produce warnings instead of blocking the approved reference pack.

## Assumptions

| Assumption | Basis |
|---|---|
| I assume the person running the tool has permission to view and process sensitive employee data, such as SSNs and birth dates; the tool does not mask these values. | API access alone does not prove admin access or legal permission. |
| The bundle names the correct provider and contains accurate request parameters. | These select the mapping rules and identify who the data belongs to. |
| The supplied contracts and accepted field meanings are reliable enough for mapping. | They guide validation and determine which fields can share one meaning. |
| IDs identify entries consistently across responses. | Matching IDs allow information to combine and related entries to connect. |
| Responses with the same ID describe information that can be combined. | The program does not distinguish separate historical versions automatically. |
| Request `params` match the request that produced the response. | Returned data often omits the owner IDs. |
| PrismHR gender codes M/F/X/D/U mean male/female/non-binary/declined/unknown. | My interpretation; the contract lists codes without meanings. Originals are kept. |
| UKG `id` identifies the employee; its separate `employee_id` stays as `ukg_employee_id`. | The demo employee request worked with `id`. |
| Use UKG paycheck `employee.account_id` to link the paycheck to an employee. | I assume accounts and employees have a one-to-one relationship, so the account ID can identify the employee. Not verified with live data - Because the UKG demo returned no pay statements |

## Gaps

- PrismHR employee requests accept a list of employee IDs, but this tool rejects lists in `params.employeeId`; current fixtures use single IDs or omit this parameter.

Tests cover happy paths, selected edge cases and error paths, including missing values, failed conversions, conflicting IDs and existing output files; they do not cover every possible case.

- A response missing its `body` can produce no entries without an error or warning.
- UKG pay-statement details are accepted even when the body’s statement ID differs from `params.pay_statement_id`; the program does not check that they match.
- No checks for believable dates, sensible amounts or conflicting business values.
- Failed field conversions can leave null values in otherwise successful output.
  - Example: `hourlyPay: "abc"` becomes `hourly_rate: null`; the original value and conversion issue are saved in the output.
- ID parts containing `:` can produce the same combined ID: `A:B` + `C` and `A` + `B:C` both become `A:B:C`.
- Repeating a response combines matching entries but repeats their list items. For example, employee `007` with one salary-history item, supplied twice, becomes one employee with that same history item listed twice. Repeated paycheck responses can similarly duplicate earnings, tax or deduction lines.
- A storage error during writing can leave an incomplete output file.
- Some fields, such as isolved deduction parameter `Amount2`, have no verified meaning; I preserve them without guessing a shared meaning or calculation.
- The system cannot link two entries when the data provides no direct ID connection and requires a lookup using other fields.
  - Example: isolved payroll—paychecks provide a run number, but the code does not match it to a payroll run ID.
- isolved payroll and UKG deduction, deposit and pay-statement mappings lack live examples; I checked them using the supplied contracts and synthetic test data.
- UKG’s `/employees/{aid}/direct-deposits` endpoint is deprecated; I map saved responses using its cached definition because no replacement has been verified.
