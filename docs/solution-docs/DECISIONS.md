# Assumptions & Decisions

| Assumption / Decision | Reason |
|---|---|
| UKG combined inputs use employee `pay_info`/`compensation_history`, deduction `assignments`/`code_lookup`/`benefits`, and payroll `payroll_runs`/`paycheck_list`/`paychecks`; reuse native schemas inside sections. | Validate supplemental data together without mixing field meanings or removing required wrapper checks. |
| Keep isolved paycheck models in the payroll source file; combined input uses optional `payroll_runs` and `paychecks`. Native run arrays and paged-check responses remain supported. | Validate complete payroll information without mixing run and paycheck field meanings. |
| Use one main isolved employee input model; keep employee fields at the top level and supplemental salary records under optional `salary_history`. | Validate combined data recursively while keeping employee and salary field meanings separate. |
| Require record IDs and documented required wrapper fields; other fields, including reference IDs, are optional. Keep existing ID null acceptance; nested record IDs are required only when the record is supplied. | JSON input may combine API fields; requiring complete endpoint responses complicates validation. |
| **To be decided:** can the supplied employee input be assumed to include a company ID, even when the raw provider response does not? | |
| **To be decided:** implement a separate company record or retain only the employee’s client association. | |
| Assume PrismHR employee runs always receive `--client-id`, matching the request used to fetch the input file; preserve it as `source_client_id`. CLI support is planned. | The response omits client ID; a CLI argument is the simplest way to retain the client association without changing the raw JSON. |
| Keep the current canonical structure; use class comments to mark README coverage instead of adding category sections. | Documents coverage without restructuring the models. |
| Reconcile readiness checks; isolved and UKG are still blocked. | Current checks conflict with the README-approved pack and UKG's non-OpenAPI format. |
| Add `direct_deposit` and `deduction` entities. | Both are required by the README. |
| Assume employee `errorCode="0"` means success; any other code, including `"1"` and `NOT_FOUND`, means error. | Postman returned employees with `"0"`; other OpenAPI operations define zero as success. The employee schema does not define code meanings. |

## Schemas & Enums
<!-- Why the canonical models and codes are designed this way -->

## Provider Mappings & Gaps
<!-- Per provider: key mappings, missing data, how handled -->

### PrismHR

| Gap | Handling |
|---|---|
| ACH `amount` and `limit` are required in the schema, but descriptions say `amount` must be absent for method `B` and `limit` is allowed only for method `P`. | Keep current schema validation; resolve conditional requirements when implementing business rules. |
| `updateMessage` and `extension` meanings are undocumented; Postman returned null. | Keep it optional; do not treat nonempty values as errors without evidence. |
| Employee fields with insufficient descriptions: `benefitEnrollmentCompleted`; Person: `cobraSSN`, `cobraOnly`, `taxZipCode`, `w2ElecForm`, `w2ElecFormDate`, `legacyEmployeeId`; Client: `typeClass`; Compensation: `longPayTable`, `longBasisDate`, `quartile`, `compaRatio`, `benefitsBasePay`, `taxCreditEmp`, `autoPayCode`, `profitSharing`, `wagePlanCA`, `compReviewNextDate`, `notes`, `electronicPayStub`, `irsLockInDate`, `payPeriodsPerWeek`; PayPeriodInfo: `periodCode`, `periodBase`; EeImage: `masterId`, `verifyDateTime`, `verifyUserId`; I9ImageAudit: `auditDate`, `auditUser`, `auditId`, `auditStep`; LockIns: `stateDate`, `authUser`; SkillsAndEducation: `osha10Certified`; wrapper: `updateMessage`, `extension.any`. | Missing, vague, or conflicting descriptions; meanings, units, or allowed values need clarification before semantic mapping. |

### isolved

| Gap | Handling |
|---|---|
| Mixed-schema employee input: `seasons` belongs to `IsolvedEmployeeSalaryModel`; `IsolvedEmployeeModel` retains it as an extra without validating its contents. | To be decided: validate fields from multiple source schemas in combined input. |

### UKG Ready

| Gap | Handling |
|---|---|
| No populated paycheck responses; compensation history is available from a separate API. | Map compensation history into employee compensation output; validate paychecks from documented schemas and synthetic data. Compensation history does not replace paycheck details. |

## Data Issues
<!-- Unexpected or conflicting data; assumption made and why -->

## Testing
<!-- Fixture and test design choices -->

## Write Path
<!-- Only if built: supported fields, limitations -->

## Open Questions
<!-- Unresolved items for the team -->

## Future Improvements

| Improvement | Reason |
|---|---|
| Combine PrismHR payroll batch and paycheck input models; validate both sections with one model. | Separate validation paths are simpler to implement now; both supplied sections are already validated. |
| Establish a reusable mapper convention or shared mapping framework. | A generic framework adds overhead now; revisit once implemented mappers reveal common patterns. |
