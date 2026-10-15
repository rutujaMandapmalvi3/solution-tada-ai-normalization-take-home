# Deduction Canonical Mapping Proposal

Compare employee deduction assignments/setup, separately from paycheck deduction transactions. UKG code catalog and benefit enrollment are supplemental context, not automatically additional employee deductions.

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
| `deduction_id` (Optional[str]) | No verified shared counterpart proposed. | `IsolvedEmployeePayItemModel.id` (Optional[int])<br>Unique Object Id | `UKGReadyDeductionResponseDeductionsItem.id` (int)<br>No property description supplied. | Prism code is not an assignment record ID. |
| `deduction_code` (Optional[str]) | `PrismHREmployeeDeductionsDeduction.deductionCode` (Optional[str])<br>unique ID for the deduction, defined by the service provider | `IsolvedEmployeePayItemModel.payItemCode` (Optional[str])<br>No property description supplied. | `UKGReadyDeductionResponseDeductionsItemDeduction.code` (Optional[str])<br>No property description supplied. | Codes are provider/company-specific; do not translate by matching labels. |
| `description` (Optional[str]) | `PrismHREmployeeDeductionsDeduction.description` (Optional[str])<br>full description of the deduction | No separate description in this source model. | No separate description in this assignment schema. | Preserve the description; do not silently equate a name with a description. |
| `deduction_name` (Optional[str]) | No separate name in this source model. | `IsolvedEmployeePayItemModel.payItemName` (Optional[str])<br>The name of this pay item | `UKGReadyDeductionResponseDeductionsItemDeduction.name` (Optional[str])<br>No property description supplied. | isolved name has descriptive evidence; UKG remains a name/type-based candidate. Catalog names retain catalog scope. |
| `start_date` (Optional[date]) | `PrismHREmployeeDeductionsDeduction.startDate` (Optional[str])<br>date on which deduction starts (if it is for a limited period of time) | `IsolvedEmployeePayItemModel.startDate` (Optional[str])<br>The starting date for this pay item. Start Date field can be set to Null by passing a null value. | `UKGReadyDeductionResponseDeductionsItem.effective_from` (Optional[str])<br>No property description supplied. | Date helper; preserve original invalid/blank data separately. |
| `end_date` (Optional[date]) | `PrismHREmployeeDeductionsDeduction.stopDate` (Optional[str])<br>date on which deduction stops (if it is for a limited period of time) | `IsolvedEmployeePayItemModel.stopDate` (Optional[str])<br>The stopping date for this pay item. Stop Date field can be set to Null by passing a null value. | `UKGReadyDeductionResponseDeductionsItem.effective_to` (Optional[str])<br>No property description supplied. | Do not infer inclusive/exclusive date semantics. |
| `employee_id` (Optional[str]) | No verified shared counterpart proposed. | `IsolvedEmployeePayItemModel.employeeId` (Optional[int])<br>The pay item's owner Employee Id | No verified shared counterpart proposed. | Other providers need supplied context or their actual employee reference. |

Use `provider: Literal["prismhr", "isolved", "ukg-ready"]` on normalized records. The table distinguishes description-backed fields from candidates without property descriptions; all remaining fields have an explicit preservation destination below. UKG matches and isolved payItemCode remain candidates where descriptions are missing; no code/scale equivalence is assumed.

## Additional comparison findings

- The original comparison grouped trackArrears with balance; this proposal separates the Boolean tracking rule from the live isolved integer balance.
- isolved payItemId is explicitly deprecated in favor of id. Preserve the deprecated value if supplied; do not make it a second canonical record ID. auditId is also deprecated.
- The original scheduleOverride/period correspondence can inform a future schedule crosswalk, but matching schedules requires explicit code-to-meaning evidence, not string equality. Keep raw source schedules for now.
- Prism loanOrGarnishId and isolved referenceNumber remain separate: the latter is described only as a reference number. Neither an empty sample nor a similar table row proves equivalence.
- UKG benefits represent enrollment and plan/coverage context, and deduction-codes represent definitions. Neither proves a payroll deduction transaction occurred.
- Paycheck deduction components remain in payroll as well. Sharing their mapping helper later must not duplicate amounts across independently normalized outputs.

## Decisions already settled

| Area | Decision | Basis |
|---|---|---|
| Architecture | Shared Pydantic output, provider YAML rules, common engine/helpers. | Employee/direct-deposit approach. |
| IDs | String identifiers; use actual assignment/pay-item `id` as `deduction_id`. Prism deductionCode stays a definition code, not a generated assignment ID. | Existing ID policy and available source fields. |
| Identity scope | Required record IDs identify the supplied record, not its employee. Nested IDs stay nested references; existing null acceptance remains. | Existing input assumption and requiredness policy. |
| Employee reference | isolved employeeId → `employee_id` (Optional[str]); employeeNumber → `employee_number` (Optional[str]). | Owner descriptions; names align with the employee canonical model. |
| Names/descriptions | Keep `deduction_name` separate from `description`. | A name is not documented as a full description. |
| Dates | Optional date, serialized YYYY-MM-DD; reuse the date helper and retain originals/issues. | Existing date policy; do not shift calendar dates by timezone. |
| Numbers | Finite float for amount/rate/percentage fields; no guessed scale, basis or currency conversions. | Existing number helper. Preserve zero/false/blank/null handling. |
| Source-specific fields | Explicit snake_case provider fields; known unconsumed fields and record links under unmapped; unknown extras preserve nesting. | Existing engine behavior. |
| Wrappers | Preserve wrapper data in source_metadata; Prism extension presence alone does not mean failure. | Existing validation/metadata policy. |
| Empty input | Optional Prism deduction data absent/null/empty → []; required wrapper and supplied-record checks remain. | Existing deduction decision. Does not remove UKG required native wrapper fields. |
| Record roles | Keep assignment/setup separate from paycheck transactions, catalogs and benefit enrollment. | Different purposes; no inferred joins or withheld amounts. |
| Balances | Keep trackArrears separate from balance and keep accumulation periods distinct. | Boolean tracking rule is not a balance; no invented totals. |
| Unexpected records — decided | Preserve unexpected/non-deduction records separately; never map them as canonical deductions or silently discard them. | User decision. Known records use provider fields; undeclared properties use source_extras. |
| Adapter filtering — decided | Validate first, select deduction records inside each provider adapter, then call the shared mapping engine. No YAML conditions or source-model restructuring. | Explicit provider selection using documented sections or verified item types. |
| isolved item selection | Map only payItemType Deduction. Missing/unknown and other item types are not classified as deductions; preserve them separately. | The saved response contains mixed item types; selection must not silently misclassify them. |
| Amount preservation | Preserve unclear amounts with their parameters/methods; do not infer shared calculation meanings. | Selected isolved paramType/paramValue have no descriptions or applicable lookup dictionary. Prism has some explicit method/basis descriptions; retain these rather than treating all amounts as undocumented. |
| Unclear meanings | Preserve fields whose meaning cannot be established from available descriptions, context or comparisons. | User decision; no invented classifications or conversions. |
| Employee context | Use CLI --employee-id for standalone deduction inputs; preserve/check any supplied source employee ID without silent overwrite. | User chose CLI association. Nested benefit account references do not automatically identify assignment owners. |

## Decisions still to review

| Area | Problem | Proposed solution |
|---|---|---|
| UKG supplemental preservation — settled | Related catalog/benefit information is not a deduction assignment. | Preserve in provider_fields.ukg-ready on the result, including when deductions is empty; follow the existing preservation policy. |

## Complete source-to-canonical inventory

Each source class is listed once, including nested classes. Follow an object/list field to its named child class. This represents every declared field without duplicating the same reusable class at every possible parent path. RootModel[List[T]] means a top-level JSON array, not an input object with a root key. A field marked required may still accept null if its annotation is Optional.

Targets are relative to each assignment, supplement, or payroll record. Use explicit snake_case under `provider_fields.<provider>` while retaining parent object/list boundaries. Paths in child-class tables are relative to that child: catalog/benefit/paycheck IDs must never overwrite assignment IDs. Wrappers use metadata; record links use unmapped preservation.

### prismhr

#### PrismHRExtension

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_deduction.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/Extension).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `any` | Optional[Dict[str, Any]] | Optional presence | object | No property description supplied. | Metadata: `source_metadata.prismhr.response`; retain source field and nesting. |

#### PrismHREmployeeDeductionsDeduction

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_deduction.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/EmployeeDeductions-Deduction).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `deductionCode` | Optional[str] | Optional presence | string | unique ID for the deduction, defined by the service provider | Shared: `deduction_code`. Reuse the agreed helper where needed; preserve conversion originals/issues. |
| `deductionType` | Optional[str] | Optional presence | string | type of deduction, defined by the service provider | Preserve separately: `provider_fields.prismhr.deduction_type`; keep source type and nested scope. |
| `deductionMethod` | Optional[str] | Optional presence | string | calculation method for the deduction | Preserve separately: `provider_fields.prismhr.deduction_method`; keep source type and nested scope. |
| `description` | Optional[str] | Optional presence | string | full description of the deduction | Shared: `description`. Reuse the agreed helper where needed; preserve conversion originals/issues. |
| `usePercent` | Optional[bool] | Optional presence | boolean | indicate a percentage or fixed amount. Valid values are T (True) or F (False). The default is False. | Preserve separately: `provider_fields.prismhr.use_percent`; keep source type and nested scope. |
| `amount` | Optional[float] | Optional presence | number | deduction amount | Preserve separately: `provider_fields.prismhr.amount` (Optional[float]); finite number helper, no inferred units/scale. |
| `period` | Optional[str] | Optional presence | string | period(s) when deduction is taken from employee's earnings | Preserve separately: `provider_fields.prismhr.period`; keep source type and nested scope. |
| `loanOrGarnishId` | Optional[str] | Optional presence | string | ID for the loan or garnishment | Preserve nested/reference scope: `provider_fields.prismhr.loan_or_garnish_id` (Optional[str]); identifier helper, retaining existing nulls. |
| `benefitPlanId` | Optional[str] | Optional presence | string | ID of the company's benefit plan | Preserve nested/reference scope: `provider_fields.prismhr.benefit_plan_id` (Optional[str]); identifier helper, retaining existing nulls. |
| `lastDedPerAdj` | Optional[float] | Optional presence | number | last deduction period adjustment | Preserve separately: `provider_fields.prismhr.last_deduction_period_adjustment` (Optional[float]); finite number helper, no inferred units/scale. |
| `limit` | Optional[float] | Optional presence | number | maximum amount system can deduct in a payroll period | Preserve separately: `provider_fields.prismhr.payroll_period_limit` (Optional[float]); finite number helper, no inferred units/scale. |
| `maximum` | Optional[float] | Optional presence | number | maximum amount system can deduct per month, quarter, year, or lifetime, as specified in basis parameter | Preserve separately: `provider_fields.prismhr.maximum_amount` (Optional[float]); finite number helper, no inferred units/scale. |
| `basis` | Optional[str] | Optional presence | string | basis for maximum amount: 'M' (monthly), + 'Q' (quarterly), 'A' (annually), or 'L' (lifetime) | Preserve separately: `provider_fields.prismhr.maximum_basis`; keep source type and nested scope. |
| `trackArrears` | Optional[bool] | Optional presence | boolean | indicates whether the deduction tracks to arrears | Preserve separately: `provider_fields.prismhr.track_arrears`; keep source type and nested scope. |
| `startDate` | Optional[str] | Optional presence | string / date | date on which deduction starts (if it is for a limited period of time) | Shared: `start_date`. Reuse the agreed helper where needed; preserve conversion originals/issues. |
| `stopDate` | Optional[str] | Optional presence | string / date | date on which deduction stops (if it is for a limited period of time) | Shared: `end_date`. Reuse the agreed helper where needed; preserve conversion originals/issues. |
| `glOverrideAcct` | Optional[str] | Optional presence | string | G/L override account | Preserve separately: `provider_fields.prismhr.general_ledger_override_account`; keep source type and nested scope. |
| `mandatory` | Optional[bool] | Optional presence | boolean | indicates whether the deduction is for goods or services provided to the employee that are a mandatory part of employment | Preserve separately: `provider_fields.prismhr.mandatory`; keep source type and nested scope. |
| `matchMethod` | Optional[str] | Optional presence | string | matching method used to calculate the match: 'F' (flat) or 'P' (percent) | Preserve separately: `provider_fields.prismhr.match_method`; keep source type and nested scope. |
| `matchAmount` | Optional[float] | Optional presence | number | matching amount, either a flat amount or a percentage (depending on the setting in matchMethod) | Preserve separately: `provider_fields.prismhr.match_amount` (Optional[float]); finite number helper, no inferred units/scale. |
| `matchDescription` | Optional[str] | Optional presence | string | description of match that prints on the Batch Match Code Summary report | Preserve separately: `provider_fields.prismhr.match_description`; keep source type and nested scope. |
| `cutbackPayeeCode` | Optional[str] | Optional presence | string | ID of the third-party payee receiving the deduction | Preserve nested/reference scope: `provider_fields.prismhr.third_party_payee_code` (Optional[str]); identifier helper, retaining existing nulls. |
| `rateTableId` | Optional[str] | Optional presence | string | rate table for the employee | Preserve nested/reference scope: `provider_fields.prismhr.rate_table_id` (Optional[str]); identifier helper, retaining existing nulls. |
| `rateTier` | Optional[str] | Optional presence | string | rate tier for the employee | Preserve separately: `provider_fields.prismhr.rate_tier`; keep source type and nested scope. |
| `detailsChecksum` | Optional[str] | Optional presence | string | checksum of the deduction details record which is required for details update | Preserve separately: `provider_fields.prismhr.details_checksum`; keep source type and nested scope. |
| `achOption` | Optional[str] | Optional presence | string | direct deposit account associated with the deduction; this is only returned if the VOLUNTARYDEDACH Custom Feature Code is enabled | Preserve separately: `provider_fields.prismhr.ach_option`; keep source type and nested scope. |

#### PrismHREmployeeDeductions

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_deduction.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/EmployeeDeductions).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `deduction` | Optional[List[PrismHREmployeeDeductionsDeduction]] | Optional presence | array | No property description supplied. | Container: preserve this section and validate/map its own records; do not convert catalogs or benefits into employee assignments. |

#### PrismHRDeductionResponse

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_deduction.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/DeductionResponse).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `errorCode` | str | Required presence | string | No property description supplied. | Metadata: `source_metadata.prismhr.response`; retain source field and nesting. |
| `errorMessage` | str | Required presence | string | No property description supplied. | Metadata: `source_metadata.prismhr.response`; retain source field and nesting. |
| `extension` | Optional[PrismHRExtension] | Optional presence | #/components/schemas/Extension | No property description supplied. | Metadata: `source_metadata.prismhr.response`; retain source field and nesting. |
| `employeeDeductions` | Optional[PrismHREmployeeDeductions] | Optional presence | #/components/schemas/EmployeeDeductions | No property description supplied. | Container: unwrap employeeDeductions.deduction and map each assignment; preserve wrapper separately. |

#### PrismHRDeduction

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/Deduction).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `deductCode` | Optional[str] | Optional presence | string | deduction code | Preserve separately: `provider_fields.prismhr.deduct_code`; keep source type and nested scope. |
| `deductDescription` | Optional[str] | Optional presence | string | deduction description | Preserve separately: `provider_fields.prismhr.deduct_description`; keep source type and nested scope. |
| `deductAmount` | Optional[float] | Optional presence | number | deduction amount | Preserve separately: `provider_fields.prismhr.deduct_amount` (Optional[float]); finite number helper, no inferred units/scale. |
| `deductType` | Optional[str] | Optional presence | string | type of deduction | Preserve separately: `provider_fields.prismhr.deduct_type`; keep source type and nested scope. |
| `deductUnionId` | Optional[str] | Optional presence | string | labor union code associated with the deduction | Preserve nested/reference scope: `provider_fields.prismhr.deduct_union_id` (Optional[str]); identifier helper, retaining existing nulls. |
| `planId` | Optional[str] | Optional presence | string | benefit plan ID associated with the deduction; only displays for deductType values \”C\”, \”F\”, and \”K\”, otherwise this field is empty | Preserve nested/reference scope: `provider_fields.prismhr.plan_id` (Optional[str]); identifier helper, retaining existing nulls. |

#### PrismHROtherDeduction

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/OtherDeduction).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `otherDeductCode` | Optional[str] | Optional presence | string | other deduction code | Preserve separately: `provider_fields.prismhr.other_deduct_code`; keep source type and nested scope. |
| `otherDeductDescription` | Optional[str] | Optional presence | string | other deduction description | Preserve separately: `provider_fields.prismhr.other_deduct_description`; keep source type and nested scope. |
| `otherDeductAmount` | Optional[float] | Optional presence | number | other deduction amount | Preserve separately: `provider_fields.prismhr.other_deduct_amount` (Optional[float]); finite number helper, no inferred units/scale. |
| `otherDeductOneTimeSwitch` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.prismhr.other_deduct_one_time_switch`; keep source type and nested scope. |

### isolved

#### IsolvedEmployeePayItemCalcParamModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_deduction.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.EmployeePayItemCalcParamModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `paramType` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.param_type`; keep source type and nested scope. |
| `paramValue` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.param_value` (Optional[float]); finite number helper, no inferred units/scale. |

#### IsolvedBaseLinkModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_deduction.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.Base.LinkModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `href` | Optional[str] | Optional presence | string | Hyperlink to linked entity or action | Preserve original nesting: `provider_fields.isolved.unmapped` (record links). |
| `method` | Optional[str] | Optional presence | string | HTTP Method for linked entity or action | Preserve original nesting: `provider_fields.isolved.unmapped` (record links). |
| `rel` | Optional[str] | Optional presence | string | Relationship or purpose of link to enclosing entity | Preserve original nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedEmployeePayItemModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_deduction.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.EmployeePayItemModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Shared: `deduction_id`. Reuse the agreed helper where needed; preserve conversion originals/issues. |
| `auditId` | Optional[int] | Optional presence | integer / int64 | DEPRECATED: do not use. ID of the audit entry. | Preserve nested/reference scope: `provider_fields.isolved.deprecated_audit_id` (Optional[str]); identifier helper, retaining existing nulls. |
| `calcParams` | Optional[List[IsolvedEmployeePayItemCalcParamModel]] | Optional presence | array | A collection of Calculation Parameters for this pay item | Preserve separately: `provider_fields.isolved.calc_params`; keep source type and nested scope. |
| `employeeId` | Optional[int] | Optional presence | integer / int32 | The pay item's owner Employee Id | Shared: `employee_id`. Reuse the agreed helper where needed; preserve conversion originals/issues. |
| `employeeNumber` | Optional[str] | Optional presence | string | The pay item's owner Employee Number | Decided: `employee_number` (Optional[str]); owner employee number, distinct from employee_id. |
| `firstName` | Optional[str] | Optional presence | string | The pay item's owner Employee First Name | Preserve separately: `provider_fields.isolved.first_name`; keep source type and nested scope. |
| `lastName` | Optional[str] | Optional presence | string | The pay item's owner Employee Last Name | Preserve separately: `provider_fields.isolved.last_name`; keep source type and nested scope. |
| `payItemCode` | Optional[str] | Optional presence | string | No property description supplied. | Candidate shared: `deduction_code`. Reuse the agreed helper where needed; preserve conversion originals/issues. Property description is absent. |
| `payItemId` | Optional[int] | Optional presence | integer / int32 | DEPRECATED: do not use. Use the id property for the pay item's unique Identifier. Unique ID for the pay item. | Preserve nested/reference scope: `provider_fields.isolved.deprecated_pay_item_id` (Optional[str]); identifier helper, retaining existing nulls. |
| `payItemName` | Optional[str] | Optional presence | string | The name of this pay item | Decided: `deduction_name` (Optional[str]) for confirmed deduction records; preserve original name. |
| `payItemType` | Optional[str] | Optional presence | string | The Pay Item Type | Preserve separately: `provider_fields.isolved.pay_item_type`; keep source type and nested scope. |
| `referenceNumber` | Optional[str] | Optional presence | string | The reference number for this pay item | Preserve separately: `provider_fields.isolved.reference_number`; keep source type and nested scope. |
| `scheduleOverride` | Optional[str] | Optional presence | string | The Schedule Override for this pay item | Preserve separately: `provider_fields.isolved.schedule_override`; keep source type and nested scope. |
| `startDate` | Optional[str] | Optional presence | string / date-time | The starting date for this pay item. Start Date field can be set to Null by passing a null value. | Shared: `start_date`. Reuse the agreed helper where needed; preserve conversion originals/issues. |
| `stopDate` | Optional[str] | Optional presence | string / date-time | The stopping date for this pay item. Stop Date field can be set to Null by passing a null value. | Shared: `end_date`. Reuse the agreed helper where needed; preserve conversion originals/issues. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve original nesting: `provider_fields.isolved.unmapped` (record links). |
| `balance` | Optional[int] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Preserve separately: `provider_fields.isolved.balance`; keep source type and nested scope. |

#### IsolvedEmployeePayItemResponse

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_deduction.py) · Project input/container; no independent provider schema.

Input shape: `RootModel[List[IsolvedEmployeePayItemModel]]`. No additional declared fields.

#### IsolvedCheckAccumulationModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.CheckAccumulationModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Preserve nested/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, retaining existing nulls. |
| `checkDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.check_dollars` (Optional[float]); finite number helper, no inferred units/scale. |
| `currentDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.current_dollars` (Optional[float]); finite number helper, no inferred units/scale. |
| `ftdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ftd_dollars` (Optional[float]); finite number helper, no inferred units/scale. |
| `itemCode` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.item_code`; keep source type and nested scope. |
| `itemDescription` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.item_description`; keep source type and nested scope. |
| `mtdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.mtd_dollars` (Optional[float]); finite number helper, no inferred units/scale. |
| `ptdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ptd_dollars` (Optional[float]); finite number helper, no inferred units/scale. |
| `qtdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.qtd_dollars` (Optional[float]); finite number helper, no inferred units/scale. |
| `sequence` | Optional[int] | Optional presence | integer / int32 | No property description supplied. | Preserve separately: `provider_fields.isolved.sequence`; keep source type and nested scope. |
| `ytdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ytd_dollars` (Optional[float]); finite number helper, no inferred units/scale. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve original nesting: `provider_fields.isolved.unmapped` (record links). |

### ukg_ready

#### UKGReadyDeductionResponse

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_deduction.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/132/schema).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__employees__%28aid%29__deductions.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `deductions` | List[UKGReadyDeductionResponseDeductionsItem] | Required presence | array | No property description supplied. | Container: preserve this section and validate/map its own records; do not convert catalogs or benefits into employee assignments. |

#### UKGReadyDeductionResponseDeductionsItem

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_deduction.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/132/schema/properties/deductions/items).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__employees__%28aid%29__deductions.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Shared: `deduction_id`. Reuse the agreed helper where needed; preserve conversion originals/issues. |
| `deduction` | Optional[UKGReadyDeductionResponseDeductionsItemDeduction] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.deduction`; keep source type and nested scope. |
| `effective_from` | Optional[str] | Optional presence | string | No property description supplied. | Candidate shared: `start_date`. Reuse the agreed helper where needed; preserve conversion originals/issues. Property description is absent. |
| `effective_to` | Optional[str] | Optional presence | string | No property description supplied. | Candidate shared: `end_date`. Reuse the agreed helper where needed; preserve conversion originals/issues. Property description is absent. |
| `sequence` | Optional[int] | Optional presence | integer | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.sequence`; keep source type and nested scope. |
| `_links` | Optional[UKGReadyDeductionResponseDeductionsItemLinks] | Optional presence | object | No property description supplied. | Preserve original nesting: `provider_fields.ukg-ready.unmapped` (record links). |

#### UKGReadyDeductionResponseDeductionsItemDeduction

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_deduction.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/132/schema/properties/deductions/items/properties/deduction).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__employees__%28aid%29__deductions.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `code` | Optional[str] | Optional presence | string | No property description supplied. | Candidate shared: `deduction_code`. Reuse the agreed helper where needed; preserve conversion originals/issues. Property description is absent. |
| `name` | Optional[str] | Optional presence | string | No property description supplied. | Candidate: `deduction_name` (Optional[str]); keep separate from description and catalog names. |

#### UKGReadyDeductionResponseDeductionsItemLinks

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_deduction.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/132/schema/properties/deductions/items/properties/_links).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__employees__%28aid%29__deductions.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `self` | Optional[str] | Optional presence | string | No property description supplied. | Preserve original nesting: `provider_fields.ukg-ready.unmapped` (record links). |

#### UKGReadyDeductionCodesResponse

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_deduction.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/244/schema).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__lookup__deduction-codes.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `items` | List[UKGReadyDeductionCodesResponseItemsItem] | Required presence | array | No property description supplied. | Container: preserve this section and validate/map its own records; do not convert catalogs or benefits into employee assignments. |

#### UKGReadyDeductionCodesResponseItemsItem

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_deduction.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/244/schema/properties/items/items).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__lookup__deduction-codes.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `code` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.code`; keep source type and nested scope. |
| `external_id` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.external_id`; keep source type and nested scope. |
| `name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.name`; keep source type and nested scope. |
| `id` | Optional[int] | Required presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Preserve nested/reference scope: `provider_fields.ukg-ready.id` (Optional[str]); identifier helper, retaining existing nulls. |

#### UKGReadyBenefitsResponse

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_deduction.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/119/schema).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__employees__%28aid%29__benefits.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `benefits` | List[UKGReadyBenefitsResponseBenefitsItem] | Required presence | array | No property description supplied. | Container: preserve this section and validate/map its own records; do not convert catalogs or benefits into employee assignments. |

#### UKGReadyBenefitsResponseBenefitsItem

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_deduction.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/119/schema/properties/benefits/items).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__employees__%28aid%29__benefits.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Preserve nested/reference scope: `provider_fields.ukg-ready.id` (Optional[str]); identifier helper, retaining existing nulls. |
| `employee` | Optional[UKGReadyBenefitsResponseBenefitsItemEmployee] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.employee`; keep source type and nested scope. |
| `name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.name`; keep source type and nested scope. |
| `coverage_level` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.coverage_level`; keep source type and nested scope. |
| `benefit_plan` | Optional[UKGReadyBenefitsResponseBenefitsItemBenefitPlan] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.benefit_plan`; keep source type and nested scope. |
| `coverage_effective_from` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.coverage_effective_from` (Optional[date]); date helper and source originals. |
| `coverage_effective_to` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.coverage_effective_to` (Optional[date]); date helper and source originals. |

#### UKGReadyBenefitsResponseBenefitsItemEmployee

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_deduction.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/119/schema/properties/benefits/items/properties/employee).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__employees__%28aid%29__benefits.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `account_id` | Optional[float] | Optional presence | number / long | No property description supplied. | Preserve nested/reference scope: `provider_fields.ukg-ready.account_id` (Optional[str]); identifier helper, retaining existing nulls. |

#### UKGReadyBenefitsResponseBenefitsItemBenefitPlan

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_deduction.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/119/schema/properties/benefits/items/properties/benefit_plan).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__employees__%28aid%29__benefits.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Preserve nested/reference scope: `provider_fields.ukg-ready.id` (Optional[str]); identifier helper, retaining existing nulls. |
| `currency` | Optional[str] | Optional presence | Not supplied at this path | No property description supplied. Documented enum: ["USD", "GBP", "EUR", "CAD", "AUD", "NZD", "MXN", "CNY", "SEK", "BRL", "INR", "SGD", "HKD", "CHF", "CRC", "UAH", "MOP", "DKK", "XXX"]. | Preserve separately: `provider_fields.ukg-ready.currency`; keep source type and nested scope. |

#### UKGReadyDeductionInput

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_deduction.py) · Project input/container; no independent provider schema.

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `assignments` | Optional[UKGReadyDeductionResponse] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Container: preserve this section and validate/map its own records; do not convert catalogs or benefits into employee assignments. |
| `code_lookup` | Optional[UKGReadyDeductionCodesResponse] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Container: preserve this section and validate/map its own records; do not convert catalogs or benefits into employee assignments. |
| `benefits` | Optional[UKGReadyBenefitsResponse] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Container: preserve this section and validate/map its own records; do not convert catalogs or benefits into employee assignments. |

#### UKGReadyPaycheckDetailsDeductionsItem

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/deductions/items).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer | No property description supplied. | Preserve nested/reference scope: `provider_fields.ukg-ready.id` (Optional[str]); identifier helper, retaining existing nulls. |
| `type_name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.type_name`; keep source type and nested scope. |
| `batch` | Optional[UKGReadyPaycheckDetailsDeductionsItemBatch] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.batch`; keep source type and nested scope. |
| `date_range_from` | Optional[str] | Optional presence | string | Date needs to be in the format yyyy-mm-dd within the 1900-12-31 and 2079-06-05 date range | Preserve separately: `provider_fields.ukg-ready.date_range_from` (Optional[date]); date helper and source originals. |
| `date_range_to` | Optional[str] | Optional presence | string | Date needs to be in the format yyyy-mm-dd within the 1900-12-31 and 2079-06-05 date range | Preserve separately: `provider_fields.ukg-ready.date_range_to` (Optional[date]); date helper and source originals. |
| `quantity` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.quantity` (Optional[float]); finite number helper, no inferred units/scale. |
| `base_rate` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.base_rate` (Optional[float]); finite number helper, no inferred units/scale. |
| `ee_amount` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.ee_amount` (Optional[float]); finite number helper, no inferred units/scale. |
| `er_amount` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.er_amount` (Optional[float]); finite number helper, no inferred units/scale. |
| `vendor` | Optional[UKGReadyPaycheckDetailsDeductionsItemVendor] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.vendor`; keep source type and nested scope. |
| `cost_centers` | Optional[List[UKGReadyPaycheckDetailsDeductionsItemCostCentersItem]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.cost_centers`; keep source type and nested scope. |
| `workers_comp_code` | Optional[UKGReadyPaycheckDetailsDeductionsItemWorkersCompCode] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.workers_comp_code`; keep source type and nested scope. |
| `deduction` | Optional[UKGReadyPaycheckDetailsDeductionsItemDeduction] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.deduction`; keep source type and nested scope. |

#### UKGReadyPaycheckDetailsDeductionsItemBatch

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/deductions/items/properties/batch).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Preserve nested/reference scope: `provider_fields.ukg-ready.id` (Optional[str]); identifier helper, retaining existing nulls. |
| `display_name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.display_name`; keep source type and nested scope. |

#### UKGReadyPaycheckDetailsDeductionsItemVendor

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/deductions/items/properties/vendor).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer | No property description supplied. | Preserve nested/reference scope: `provider_fields.ukg-ready.id` (Optional[str]); identifier helper, retaining existing nulls. |
| `name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.name`; keep source type and nested scope. |

#### UKGReadyPaycheckDetailsDeductionsItemCostCentersItem

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/deductions/items/properties/cost_centers/items).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `index` | Optional[int] | Optional presence | integer | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.index`; keep source type and nested scope. |
| `value` | Optional[UKGReadyPaycheckDetailsDeductionsItemCostCentersItemValue] | Optional presence | ['object', 'null'] | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.value`; keep source type and nested scope. |

#### UKGReadyPaycheckDetailsDeductionsItemCostCentersItemValue

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/deductions/items/properties/cost_centers/items/properties/value).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Preserve nested/reference scope: `provider_fields.ukg-ready.id` (Optional[str]); identifier helper, retaining existing nulls. |

#### UKGReadyPaycheckDetailsDeductionsItemWorkersCompCode

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/deductions/items/properties/workers_comp_code).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `external_id` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.external_id`; keep source type and nested scope. |

#### UKGReadyPaycheckDetailsDeductionsItemDeduction

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/deductions/items/properties/deduction).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.name`; keep source type and nested scope. |
| `external_id` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.external_id`; keep source type and nested scope. |
| `code` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.code`; keep source type and nested scope. |

## Code and lookup review

Use full descriptive labels only where the meaning is verified for that exact source field. Preserve original codes and unknown values using the existing label-helper policy. Do not borrow gender, employee-status or unrelated benefit eligibility dictionaries.

| Exact source field | Verified values / meaning | Handling |
|---|---|---|
| Prism assignment `basis` | M → monthly; Q → quarterly; A → annually; L → lifetime | Label `maximum_basis`; applies to maximum, not the deduction schedule. |
| Prism assignment `matchMethod` | F → flat; P → percent | Label the match method; retain matchAmount and basis together. No scaling. |
| Prism assignment `usePercent` | Boolean; description says percentage versus fixed, default False | Preserve supplied boolean; do not manufacture False when missing. |
| isolved `payItemType` | Deduction, Earning, Memo Calc observed | Sample proves mixed item kinds, not a complete enum. No arbitrary other type is classified. |
| isolved `calcParams[].paramType` | Amount, Amount2, Percent, Rate observed | Names are not sufficient definitions of calculation/scaling; preserve each with paramValue. |
| Prism catalog `DeductionCodeDetail.deductionType` | V → Voluntary; C → Section 125; P → Post Tax Benefit; F → Flexible Spending Account; G → Wage Garnishment; L → Employee Loan Payment; K → Pre-Tax Retirement Contribution; KC → Catch-Up Retirement Contribution; KE → Post-Tax Retirement Contribution; KL → Retirement Plan Loan Payment; KR → Roth 401(k) Contribution; KCR → Roth 401(k) Catch-Up Contribution | Lookup applies to this catalog field. No verified link to assignment deductionType or paycheck deductType; retain their raw values. |

The isolved and UKG lookup files do not provide a verified deduction-assignment type, schedule or calculation-parameter crosswalk. UKG code_lookup is a supplied definition catalog, not an enum dictionary establishing cross-provider equivalence. Do not apply Prism benefit_enrollment_status or UKG pay-info eligibility values to these records.

## Saved Postman evidence

Request names and saved response structure only are shown below. No personal/account values or credentials are copied. A request with no saved JSON response provides no live response proof. Samples supplement the contract; they do not define every accepted input shape.

| Request | Saved JSON response evidence |
|---|---|
| prismHR - GetDeductions chosen | 200 object; keys: employeeDeductions, errorCode, errorMessage, extension; 200 object; keys: employeeDeductions, errorCode, errorMessage, extension |
| prismHR - deductions not used | 200 object; keys: checksum, clientId, employeeId, errorCode, errorMessage, extension, scheduledDeduction, sessionId |
| isol - deductions chosen | 200 array; keys: balance, calcParams, employeeId, employeeNumber, firstName, id, lastName, links, payItemCode, payItemId, payItemName, payItemType, referenceNumber, scheduleOverride, startDate, stopDate |
| isol - payItemSchedules support | 200 array; keys: allowForAccruals, allowForBenefits, allowForBilling, allowForDeductions, allowForDirectDeposit, allowForEarnings, allowForReports, description, id, process1stPayOfMonth, process2ndPayOfMonth, process3rdPayOfMonth, process4thPayOfMonth, process5thPayOfMonth |
| ukg - DeductionCodes support | 200 object; keys: items |
| ukg - DeductionBenefits not used | 200 object; keys: benefits |

## References and verification

- [Original comparison](./deductions.md) (unchanged; disagreements should be resolved using the contract evidence above).
- [Decisions](../DECISIONS.md) and [README](../../../README.md).
- [PrismHR OpenAPI](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json), [isolved Swagger](../../../contracts/isolved/openapi/isolved-v6.swagger.json), [UKG schemas](../../../contracts/ukg-ready/reference-schemas.json).
- Lookup references: [PrismHR](../../../contracts/prismhr/lookup-reference.json), [isolved](../../../contracts/isolved/lookup-reference.json), [UKG Ready](../../../contracts/ukg-ready/lookup-reference.json).

Declared source-field coverage (reused classes counted once per provider): prismhr 42, isolved 34, ukg_ready 53.

Fields with absent/vague-by-absence property descriptions or undocumented source additions: prismhr 7, isolved 14, ukg_ready 51. Every such field is explicitly marked; a source name is not treated as a verified meaning. Coverage counts prove inventory inclusion, not business equivalence or live API completeness.

Before mapper implementation: use the existing provider-field preservation policy for supplemental-only input. ID/date/number helpers and preservation rules are already decided. Test missing/null/empty, zero/false, unknown codes, extras and conflicting supplements during implementation. This review changes this proposal only; source models, canonical models, YAMLs and adapters are unchanged.

## Review update — start here

- Decided: shared architecture, string IDs, date/number helpers, preservation, wrapper handling and separate record roles.
- Changed: owner reference uses employee_id; deduction_name and description stay separate.
- Verified sample: isolved includes earnings/memo items as well as deductions; balance is observed int/null and remains source-specific.
- Still needs review: UKG supplemental-only output placement. Other review decisions above are settled; source requiredness is unchanged.

## Amount evidence recheck

- Selected isolved EmployeePayItemCalcParamModel.paramType / paramValue have types only, no descriptions, enums or scale/basis definitions. Available lookup-reference domains do not cover them.
- ClientPayItemCalcParamModel only describes paramType as the type name; Corestream parameter fields only say Parameter type/value. These do not establish meanings for Amount2, Rate, or a common percentage basis in the selected employee-pay-item response. Other benefit calculation schemas are not evidence of an equivalent pay-item calculation rule.
- Prism documents limit as a payroll-period maximum; maximum uses basis M/Q/A/L, and matchAmount uses matchMethod F/P. Preserve these explicit meanings. Its amount/usePercent supplies amount-versus-percentage context but not a complete cross-provider calculation/scaling rule.
- Existing number/label helpers remain usable for verified types/labels; no new calculation helper is justified by this evidence. This is a decision about semantic conversions, not removal of numeric validation.
- Decisions logged: filter/preserve non-deduction items, preserve uncertain amounts/fields, and use CLI employee context. Implementation is unchanged.

## Adapter-filtering implementation boundary — decided

Assumption: callers selecting the deduction entity supply deduction-related input. Selection still checks known mixed-response formats; an id or amount alone does not establish record kind.

`JSON input → existing source validation → adapter selects deduction records → shared engine → canonical deductions`

| Adapter | Records selected for mapping |
|---|---|
| isolved normalize_deductions | Validated pay items whose payItemType is exactly Deduction. |
| ukg_ready normalize_deductions | Validated assignments.deductions; code_lookup and benefits are not assignment records. |
| prismhr normalize_deductions | Validated employeeDeductions.deduction. |

- Source models retain their existing validation role; the shared engine and YAML rule structure stay unchanged.
- Genuinely empty optional deduction input returns [] under existing policy. Nonempty unsupported input is not silently treated as empty.
- Unexpected records are preserved separately (decided). UKG supplemental-only output placement remains open.
- This update records the implementation plan; filtering code and deduction mapping are not implemented by this document edit.

## Latest review decision

- Unexpected deduction inputs: preserve separately, do not reject solely for being a non-deduction record, and do not misclassify them. Existing source-type/required-field validation still applies.
- UKG code_lookup contains available deduction definitions; benefits contains enrollment/plan context. Neither is an assignment or proof of a withheld amount. Only their output placement remains open.

## Canonical output model implemented

- [canonical_model_deduction.py](../../../src/normalization/canonical_models/canonical_model_deduction.py) defines CanonicalDeduction for one record and CanonicalDeductionResult for deductions plus result-level provider_fields/source_extras/source_metadata.
- Shared business fields follow the table above. Record-ID presence is required but nullable; no Prism ID is invented. Employee context is optional in the output schema; CLI sourcing is not implemented here.
- Known provider-specific fields retain their scope in provider_fields; no new unit, calculation, status or identity meanings are introduced. Metadata includes typed conversion issues and original values.
- Result-level preservation supports empty record lists without fabricated records. Models alone do not change adapter return formats.
- YAMLs, adapter filtering/integration and CLI context remain separate implementation steps.

## Record YAMLs created — helpers unchanged

- Per-provider deduction.yaml files now map one validated record to the canonical record model. Existing identifier/date/number/label helpers are reused; no helper, engine or adapter code was added in this step.
- Wrappers, parent settings, supplemental collections and filtered unexpected records remain adapter/result-level preservation responsibilities; these files do not create records for them.
- Prism has no equivalent record ID: the future adapter must supply explicit null record-ID context. Employee context sourcing/conflict checks are still adapter work.
- Verified against each configured source class: every declared record path is explicitly mapped or retained by the existing link fallback; populated and sparse synthetic records serialize successfully.
- Adapter filtering still selects assignments only. UKG uncertain assignment meanings stay provider-specific, and code_lookup/benefits must be retained at result level.

## Deduction adapters connected — current status

All three adapters now select assignments using the agreed provider rules and map their existing YAMLs. Unexpected isolved records and UKG code_lookup/benefits remain preserved in the result even with deductions=[]. CLI employee context, selected isolved owner conflict checks/fallback, wrapper/section preservation and end-to-end tests are implemented. No new helper or readiness-check change was added.

[Deduction Mapper Implementation](../Deduction%20Mapper%20Implementation.md) records exact selection fields, why filtering is needed, output/preservation placement, context/identity choices, native-shape behavior, verification and deferred work. Earlier pending notes describe prior stages; this section is current.
