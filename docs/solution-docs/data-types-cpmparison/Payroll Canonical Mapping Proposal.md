# Payroll Canonical Mapping Proposal

Payroll is one entity containing run/period information and employee paycheck information. Paycheck headers, details, earnings, taxes, benefits, deductions and payment lines retain their own record boundaries.

## How to review this proposal

This records names, types and decisions used by the implemented canonical model and mappers. Read the shared-field table first, then the decisions to review. The complete inventory keeps every declared source field, including nested objects, without forcing unrelated fields into one shared value.

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
| `payroll_run_id` (Optional[str]) | `PrismHRBatchList.batchId` (Optional[str])<br>payroll batch identifier | `IsolvedPayrollRunHistoryModel.id` (Optional[int])<br>Id for payroll run history | `UKGReadyPayrollRunResponsePayrollsItem.id` (int)<br>No property description supplied. | UKG run IDs are preserved in its run item model inventory; run number stays separate. |
| `paycheck_id` (Optional[str]) | `PrismHRPayrollVoucher.voucherId` (str)<br>payroll voucher identifier | `IsolvedCheckModel.id` (Optional[int])<br>Unique Object Id | `UKGReadyPaycheckDetails.id` (Optional[int])<br>No property description supplied. | String conversion preserves source identity, not global uniqueness. |
| `employee_id` (Optional[str]) | `PrismHRPayrollVoucher.employeeId` (Optional[str])<br>employee identifier | `IsolvedCheckModel.employeeId` (Optional[int])<br>Employee Id | No verified shared counterpart proposed. | UKG employee.account_id stays separately documented until identity relationship is verified. |
| `net_pay` (Optional[float]) | `PrismHRPayrollVoucher.netPay` (Optional[float])<br>net pay amount from employee's paycheck | `IsolvedCheckModel.netPay` (Optional[float])<br>Net Pay | No verified shared counterpart proposed. | Only add other sources after verifying their documented field meaning; do not infer from checkAmount. |
| `gross_pay` (Optional[float]) | No verified shared counterpart proposed. | `IsolvedCheckModel.grossPay` (Optional[float])<br>Gross Pay | No verified shared counterpart proposed. | Keep grossWages and taxable wages separately. |
| `pay_date` (Optional[date]) | `PrismHRPayrollVoucher.payDate` (Optional[str])<br>date of pay | `IsolvedCheckModel.checkDate` (Optional[str])<br>Check Date | `UKGReadyPaycheckDetails.pay_date` (Optional[str])<br>No property description supplied. | Candidate paycheck date match; preserve run pay date separately. |
| `period_start_date` (Optional[date]) | `PrismHRPayrollVoucher.payPeriodStart` (Optional[str])<br>pay period start date | `IsolvedCheckModel.periodBeginDate` (Optional[str])<br>Period Begin Date | `UKGReadyPaycheckDetails.pay_period_start` (Optional[str])<br>Date needs to be in the format yyyy-mm-dd within the 1900-12-31 and 2079-06-05 date range | Paycheck period boundaries; no timezone or inclusivity inference. |
| `period_end_date` (Optional[date]) | `PrismHRPayrollVoucher.payPeriodEnd` (Optional[str])<br>pay period end date | `IsolvedCheckModel.periodEndDate` (Optional[str])<br>Period End Date | `UKGReadyPaycheckDetails.pay_period_end` (Optional[str])<br>Date needs to be in the format yyyy-mm-dd within the 1900-12-31 and 2079-06-05 date range | Paycheck period boundaries; retain raw values if conversion fails. |
| `check_number` (Optional[str]) | `PrismHRPayrollVoucher.checkNumber` (Optional[str])<br>paycheck number | `IsolvedCheckModel.checkNumber` (Optional[int])<br>Check Number | No verified shared counterpart proposed. | Decided: Prism checkNumber and checkNum both mean paycheck number. Use one check_number when one is supplied or values agree; preserve both originals and report conflicts without overwrite. Keep other voucher identifiers separate. |
| `payroll_run_pay_date` (Optional[date]) | `PrismHRBatchList.payDate` (Optional[str])<br>pay date associated with this batch | `IsolvedPayrollRunHistoryModel.payDate` (Optional[str])<br>Date the pay was paid to the employees | `UKGReadyPayrollRunResponsePayrollsItem.pay_date` (Optional[str])<br>Date needs to be in the format yyyy-mm-dd within the 1900-12-31 and 2079-06-05 date range | Belongs to a run record, distinct from a paycheck date. |

| `payroll_run_period_start_date` (Optional[date]) | `PrismHRBatchByDateResponseBatchListPayGroup.payPeriodStartDate` (Optional[str])<br>start date of the pay period for this batch, per pay-group item | `IsolvedPayrollRunHistoryModel.periodBeginDate` (Optional[str])<br>Date the pay period started | `UKGReadyPayrollRunResponsePayrollsItem.start_date` (Optional[str])<br>Use its documented date format; no descriptive definition of period supplied. | Prism period remains per pay-group; isolved is run-level. UKG is a candidate: retain start_date separately until meaning is verified. |
| `payroll_run_period_end_date` (Optional[date]) | `PrismHRBatchByDateResponseBatchListPayGroup.payPeriodEndDate` (Optional[str])<br>end date of the pay period for this batch, per pay-group item | `IsolvedPayrollRunHistoryModel.periodEndDate` (Optional[str])<br>Date the pay period ended | `UKGReadyPayrollRunResponsePayrollsItem.end_date` (Optional[str])<br>Use its documented date format; no descriptive definition of period supplied. | Same scope policy as start date; no arbitrary collapse across pay groups. |

Use `provider: Literal["prismhr", "isolved", "ukg-ready"]` on normalized records. The common table distinguishes description-backed matches from candidates without property descriptions; all remaining fields have an explicit preservation destination below. A shared field is a candidate semantic match, not a completed enum/unit translation.

## Additional comparison findings

| Concept | Candidate canonical type / placement | Comparison and proposed handling |
|---|---|---|
| Run period | Optional[date] per run/pay-group record | Prism boundaries are per payGroup item, while isolved and UKG expose run boundaries. Do not collapse several Prism pay groups into one arbitrary period. |
| Run status/type | Optional[str] raw code plus provider details | Prism batchStatus/batchType, isolved status/payrollRunType and UKG status/type object are distinct code domains. Keep UKG type.id as a string identifier and display_name separately. |
| Gross earnings | Separate Optional[float] values | Prism totalEarnings is total earnings during the pay period. isolved distinguishes grossPay and grossWages. Retain separately until the desired gross-pay definition is approved. |
| Earnings hours/units | Separate Optional[float] or source numeric values | Prism hoursUnits mixes hours or units and differs from hoursWorked. isolved separates check/current hours and units. UKG hours is int with no supplied unit description. Do not equate or convert by guessing. |
| Earnings rate versus amount | Separate Optional[float] values | Prism payAmount is described as pay per hour or unit; its name alone must not make it a total earning amount. unitRate lacks a description. Keep both separately pending clarification. |
| Tax amounts | Employee and employer component collections | Prism employeeTax/companyTax, isolved taxes with employee/employer classification and UKG ee/er fields need explicit classification rules. Preserve gross/subject wages independently. |
| Check/deposit payments | Separate Optional[float] amounts and payment records | Prism checkAmt/directDeposit, isolved checkAmount/directDepositAmount/directDeposits and UKG payments have different detail levels. A UKG payment type_name requires a verified classification before calling it a deposit. |
| Benefits/contributions | Distinct employee/employer amount fields | Do not merge employee withholding, employer contribution and payroll deduction totals. Retain plan/type/cost-center references and cumulative periods. |

- UKG list and detail routes carry payroll ID in request context. Do not invent a payroll ID in a standalone detail JSON if it was not supplied.
- The cached payroll-list HTML imposes a request date-range constraint. It does not establish an input-JSON validation rule or require live requests from this local normalizer.
- Prism checkNumber and checkNum have identical descriptions, but voucherId remains a separate record identifier. No arithmetic is applied to check numbers.

## Decisions already settled

| Area | Decision | Basis |
|---|---|---|
| Entity scope | Payroll includes payroll-run and paycheck information. Keep run, header/detail and component record boundaries. | Existing five-entity design; paycheck is not another CLI entity. |
| Architecture | Shared Pydantic output, provider YAML rules, common mapping engine/helpers. | Employee/direct-deposit/deduction approach. |
| IDs | Record/reference IDs become strings; no generated identity. Preserve leading zeros; reject fractional numeric IDs. | Existing identifier helper/policy. Counts and sequence numbers remain numeric unless documented as identifiers. |
| Requiredness | Record IDs and required wrapper fields retain current source requiredness/null acceptance. Other fields remain optional. | Existing source-validation policy. |
| Dates | Date fields → optional date / YYYY-MM-DD, retaining originals and conversion issues. Time-only fields stay text; do not infer zones or merge date/time fields. | Existing date helper; preserve documented source semantics. |
| Numbers | Finite float for monetary/rate values; preserve negative/zero values and basis/currency. No currency conversion, guessed scaling or new bounds. | Existing number policy. Numeric strings remain source-specific unless conversion meaning is verified. |
| Totals | Net pay, gross pay, gross wages, total earnings, taxable wages, check amounts and deposit amounts remain distinct. | No verified complete equivalence or reconciliation rule. |
| Component roles | Earnings, deductions, employee taxes, employer taxes/contributions, benefits, payments and accruals retain separate collections/scopes. | Different accounting meanings. No inferred totals or sum of current and cumulative values. |
| Check number aliases | Prism checkNumber/checkNum can share check_number if one is present or values agree; conflicts preserve both and produce an issue. | Both descriptions say paycheck number; reuse the no-silent-overwrite policy. |
| Status/type | Preserve provider run/check status and type domains separately; translate only the exact documented field meanings below. | Same word/code in different contexts is not a crosswalk. |
| Preservation | Provider fields use explicit snake_case; known unmapped fields/record links retain original nesting; unknown extras retain nesting; wrapper data becomes metadata. | Existing engine behavior. |
| Combined input | Retain current named run/paycheck supplemental sections and validate every supplied family. | Existing source models. Do not silently discard either family. |
| Sample gaps | UKG compensation history remains employee supplemental data, not a paycheck substitute. | Previously logged UKG gap; no populated paycheck sample. |
| Verified amount matches | Use common monetary fields only for verified equivalent meanings; otherwise preserve provider-specific amounts/scopes. | Existing universal mapping policy; no new decision required. |
| Uncertain UKG fields | Preserve unclear fields without invented meanings or conversions. | Existing universal preservation policy; no new decision required. |

## Payroll decisions — settled

| Area | Decision | Status |
|---|---|---|
| Output grouping | One payroll output with separate `payroll_runs`, `paycheck_headers` and `paychecks` lists. | Decided; implemented. |
| Missing employee/run associations | Preserve supplied references; leave missing references empty. Do not infer joins or require new CLI context. Missing links remain a gap for later. | Decided; gap deferred. |
| Overlapping supplied records | Preserve every supplied section with provenance, including isolved `results`/`paychecks` and UKG summaries/details. Do not silently merge, discard or total overlapping records. | Decided; implemented. |

## Complete source-to-canonical inventory

Each source class is listed once, including nested classes. Follow an object/list field to its named child class. This represents every declared field without duplicating the same reusable class at every possible parent path. RootModel[List[T]] means a top-level JSON array, not an input object with a root key. A field marked required may still accept null if its annotation is Optional.

Targets below are relative to their run, paycheck or nested component. Use explicit snake_case under `provider_fields.<provider>` with existing object/list boundaries. Child-table target names are relative, not a request to flatten different components into one object. Wrapper fields use source metadata; record links use unmapped preservation. Never overwrite nested IDs, confuse periods, or combine current/cumulative amounts.

### prismhr

#### PrismHRExtension

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_payroll_run.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/Extension).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `any` | Optional[Dict[str, Any]] | Optional presence | object | No property description supplied. | Metadata: `source_metadata.prismhr.response`; retain source field/nesting. |

#### PrismHRBatchByDateResponseBatchListPayGroup

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_payroll_run.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/BatchByDateResponse-BatchList-PayGroup).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `payGroupId` | Optional[str] | Required presence | string | pay group included in payroll batch | Preserve record/reference scope: `provider_fields.prismhr.pay_group_id` (Optional[str]); identifier helper, existing null acceptance. |
| `payPeriodStartDate` | Optional[str] | Optional presence | string | start date of the pay period for this batch | Decided period date within this pay-group record: `payroll_run_period_start_date` (Optional[date]); never collapse multiple pay groups. |
| `payPeriodEndDate` | Optional[str] | Optional presence | string | end date of the pay period for this batch | Decided period date within this pay-group record: `payroll_run_period_end_date` (Optional[date]); never collapse multiple pay groups. |
| `weeksWorked` | Optional[str] | Optional presence | string | number of weeks worked | Preserve separately: `provider_fields.prismhr.weeks_worked`; retain source type and nested scope. |
| `deductPeriod` | Optional[str] | Optional presence | string | deduction period | Preserve separately: `provider_fields.prismhr.deduct_period`; retain source type and nested scope. |

#### PrismHRBatchList

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_payroll_run.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/BatchList).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `batchId` | Optional[str] | Required presence | string | payroll batch identifier | Shared: `payroll_run_id`. Use the agreed helper; preserve converted source originals/issues. |
| `payDate` | Optional[str] | Optional presence | string | pay date associated with this batch | Shared: `payroll_run_pay_date`. Use the agreed helper; preserve converted source originals/issues. |
| `batchType` | Optional[str] | Optional presence | string | type of payroll batch - (R)egular, (M)anual, (S)pecial, or (V)oid | Preserve separately: `provider_fields.prismhr.batch_type` (Optional[str]); verified labels R regular, M manual, S special, V void; originals retained. |
| `batchStatus` | Optional[str] | Optional presence | string | the processing status of the payroll batch | Preserve separately: `provider_fields.prismhr.batch_status`; retain source type and nested scope. |
| `payGroup` | Optional[List[PrismHRBatchByDateResponseBatchListPayGroup]] | Optional presence | array | Pay group information | Preserve separately: `provider_fields.prismhr.pay_group`; retain source type and nested scope. |

#### PrismHRBatchByDateResponse

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_payroll_run.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/BatchByDateResponse).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `errorCode` | str | Required presence | string | No property description supplied. | Metadata: `source_metadata.prismhr.response`; retain source field/nesting. |
| `errorMessage` | str | Required presence | string | No property description supplied. | Metadata: `source_metadata.prismhr.response`; retain source field/nesting. |
| `extension` | Optional[PrismHRExtension] | Optional presence | #/components/schemas/Extension | No property description supplied. | Metadata: `source_metadata.prismhr.response`; retain source field/nesting. |
| `batchList` | Optional[List[PrismHRBatchList]] | Optional presence | array | list of all payroll batches within specified date range and/or pay group | Container: validate/map each run or paycheck; preserve the other wrapper fields as metadata. Accept the documented/live voucher alias already in source validation. |

#### PrismHREmployeeTax

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/EmployeeTax).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `empTaxDeductCode` | Optional[str] | Optional presence | string | tax deduction code | Preserve separately: `provider_fields.prismhr.emp_tax_deduct_code`; retain source type and nested scope. |
| `empTaxDeductCodeDesc` | Optional[str] | Optional presence | string | description of the employee's tax deduction code | Preserve separately: `provider_fields.prismhr.emp_tax_deduct_code_desc`; retain source type and nested scope. |
| `empTaxableAmount` | Optional[float] | Optional presence | number | taxable amount | Preserve separately: `provider_fields.prismhr.employee_taxable_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `empTaxAmount` | Optional[float] | Optional presence | number | tax deduction amount | Preserve separately: `provider_fields.prismhr.employee_tax_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `empOverLimitAmount` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.prismhr.emp_over_limit_amount` (Optional[float]); number helper, no inferred basis/scale. |

#### PrismHRWorkerComp

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/WorkerComp).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `wcClass` | Optional[str] | Optional presence | string | workers' compensation class code | Preserve separately: `provider_fields.prismhr.wc_class`; retain source type and nested scope. |
| `wcTaxablePay` | Optional[float] | Optional presence | number | W/C taxable pay | Preserve separately: `provider_fields.prismhr.wc_taxable_pay` (Optional[float]); number helper, no inferred basis/scale. |
| `wcPremAmount` | Optional[float] | Optional presence | number | W/C premium cost amount | Preserve separately: `provider_fields.prismhr.wc_prem_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `wcBillAmount` | Optional[float] | Optional presence | number | W/C amount billed | Preserve separately: `provider_fields.prismhr.wc_bill_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `wcPremBill` | Optional[float] | Optional presence | number | W/C premium billed | Preserve separately: `provider_fields.prismhr.wc_prem_bill` (Optional[float]); number helper, no inferred basis/scale. |

#### PrismHREarning

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/Earning).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `payCode` | Optional[str] | Optional presence | string | pay code for earnings from time sheet | Preserve separately: `provider_fields.prismhr.pay_code`; retain source type and nested scope. |
| `payClass` | Optional[str] | Optional presence | string | pay class for earnings from time sheet | Preserve separately: `provider_fields.prismhr.pay_class`; retain source type and nested scope. |
| `payClassDescription` | Optional[str] | Optional presence | string | description of the pay class for earnings from time sheet | Preserve separately: `provider_fields.prismhr.pay_class_description`; retain source type and nested scope. |
| `chargeDate` | Optional[str] | Optional presence | string | charge date from time sheet | Preserve separately: `provider_fields.prismhr.charge_date` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `hoursUnits` | Optional[float] | Optional presence | number | hours or units paid | Preserve separately: `provider_fields.prismhr.hours_units` (Optional[float]); number helper, no inferred basis/scale. |
| `hoursWorked` | Optional[float] | Optional presence | number | hours worked from time sheet | Preserve separately: `provider_fields.prismhr.hours_worked` (Optional[float]); number helper, no inferred basis/scale. |
| `unitRate` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.prismhr.unit_rate` (Optional[float]); number helper, no inferred basis/scale. |
| `payAmount` | Optional[float] | Optional presence | number | pay per hour or unit | Preserve separately: `provider_fields.prismhr.pay_per_hour_or_unit` (Optional[float]); documented rate, not a total earning amount. |
| `division` | Optional[str] | Optional presence | string | division code associated with earnings | Preserve separately: `provider_fields.prismhr.division`; retain source type and nested scope. |
| `jobCode` | Optional[str] | Optional presence | string | job/position code associated with earnings | Preserve separately: `provider_fields.prismhr.job_code`; retain source type and nested scope. |
| `shift` | Optional[str] | Optional presence | string | shift code associated with earnings | Preserve separately: `provider_fields.prismhr.shift`; retain source type and nested scope. |
| `department` | Optional[str] | Optional presence | string | department code associated with earnings | Preserve separately: `provider_fields.prismhr.department`; retain source type and nested scope. |
| `location` | Optional[str] | Optional presence | string | location code associated with earnings | Preserve separately: `provider_fields.prismhr.location`; retain source type and nested scope. |
| `glCode` | Optional[str] | Optional presence | string | G/L account code from time sheet | Preserve separately: `provider_fields.prismhr.gl_code`; retain source type and nested scope. |
| `workComp` | Optional[str] | Optional presence | string | workers' compensation from time sheet | Preserve separately: `provider_fields.prismhr.work_comp`; retain source type and nested scope. |
| `projWork` | Optional[str] | Optional presence | string | project code associated with earnings | Preserve separately: `provider_fields.prismhr.proj_work`; retain source type and nested scope. |
| `projPhase` | Optional[str] | Optional presence | string | project phase associated with earnings | Preserve separately: `provider_fields.prismhr.proj_phase`; retain source type and nested scope. |

#### PrismHROtherEarningsDetail

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/OtherEarningsDetail).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `otherEarnCode` | Optional[str] | Optional presence | string | other earnings code | Preserve separately: `provider_fields.prismhr.other_earn_code`; retain source type and nested scope. |
| `otherEarnsDesc` | Optional[str] | Optional presence | string | description of the otherEarnCode | Preserve separately: `provider_fields.prismhr.other_earns_desc`; retain source type and nested scope. |
| `otherEarnAmount` | Optional[float] | Optional presence | number | amount associated with the otherEarnCode | Preserve separately: `provider_fields.prismhr.other_earn_amount` (Optional[float]); number helper, no inferred basis/scale. |

#### PrismHRFsaMatch

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/FsaMatch).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `code` | Optional[str] | Optional presence | string | code | Preserve separately: `provider_fields.prismhr.code`; retain source type and nested scope. |
| `description` | Optional[str] | Optional presence | string | description | Preserve separately: `provider_fields.prismhr.description`; retain source type and nested scope. |
| `matchAmt` | Optional[float] | Optional presence | number | match amount | Preserve separately: `provider_fields.prismhr.match_amt` (Optional[float]); number helper, no inferred basis/scale. |
| `acctType` | Optional[str] | Optional presence | string | acctType | Preserve separately: `provider_fields.prismhr.acct_type`; retain source type and nested scope. |

#### PrismHRCompanyTax

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/CompanyTax).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `comTaxEntity` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.prismhr.com_tax_entity`; retain source type and nested scope. |
| `comTaxDeductCode` | Optional[str] | Optional presence | string | tax deduction code | Preserve separately: `provider_fields.prismhr.com_tax_deduct_code`; retain source type and nested scope. |
| `comTaxDeductCodeDesc` | Optional[str] | Optional presence | string | description of the employer's tax deduction code | Preserve separately: `provider_fields.prismhr.com_tax_deduct_code_desc`; retain source type and nested scope. |
| `comExemptAmount` | Optional[float] | Optional presence | number | exempt earnings | Preserve separately: `provider_fields.prismhr.com_exempt_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `comShelteredAmount` | Optional[float] | Optional presence | number | sheltered earnings | Preserve separately: `provider_fields.prismhr.com_sheltered_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `comTaxableAmount` | Optional[float] | Optional presence | number | taxable earnings | Preserve separately: `provider_fields.prismhr.employer_taxable_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `comTaxType` | Optional[str] | Optional presence | string | tax basis | Preserve separately: `provider_fields.prismhr.com_tax_type`; retain source type and nested scope. |
| `comTaxAmount` | Optional[float] | Optional presence | number | taxes withheld | Preserve separately: `provider_fields.prismhr.employer_tax_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `comOvrLimit` | Optional[float] | Optional presence | number | taxable over limit | Preserve separately: `provider_fields.prismhr.com_ovr_limit` (Optional[float]); number helper, no inferred basis/scale. |
| `comTaxRate` | Optional[float] | Optional presence | number | tax rate | Preserve separately: `provider_fields.prismhr.com_tax_rate` (Optional[float]); number helper, no inferred basis/scale. |
| `comClientSutaRpt` | Optional[str] | Optional presence | string | SUTA tax (state unemployment tax), if any | Preserve separately: `provider_fields.prismhr.com_client_suta_rpt`; retain source type and nested scope. |

#### PrismHRDeduction

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/Deduction).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `deductCode` | Optional[str] | Optional presence | string | deduction code | Preserve separately: `provider_fields.prismhr.deduct_code`; retain source type and nested scope. |
| `deductDescription` | Optional[str] | Optional presence | string | deduction description | Preserve separately: `provider_fields.prismhr.deduct_description`; retain source type and nested scope. |
| `deductAmount` | Optional[float] | Optional presence | number | deduction amount | Preserve separately: `provider_fields.prismhr.deduct_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `deductType` | Optional[str] | Optional presence | string | type of deduction | Preserve separately: `provider_fields.prismhr.deduct_type`; retain source type and nested scope. |
| `deductUnionId` | Optional[str] | Optional presence | string | labor union code associated with the deduction | Preserve record/reference scope: `provider_fields.prismhr.deduct_union_id` (Optional[str]); identifier helper, existing null acceptance. |
| `planId` | Optional[str] | Optional presence | string | benefit plan ID associated with the deduction; only displays for deductType values \”C\”, \”F\”, and \”K\”, otherwise this field is empty | Preserve record/reference scope: `provider_fields.prismhr.plan_id` (Optional[str]); identifier helper, existing null acceptance. |

#### PrismHROtherDeduction

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/OtherDeduction).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `otherDeductCode` | Optional[str] | Optional presence | string | other deduction code | Preserve separately: `provider_fields.prismhr.other_deduct_code`; retain source type and nested scope. |
| `otherDeductDescription` | Optional[str] | Optional presence | string | other deduction description | Preserve separately: `provider_fields.prismhr.other_deduct_description`; retain source type and nested scope. |
| `otherDeductAmount` | Optional[float] | Optional presence | number | other deduction amount | Preserve separately: `provider_fields.prismhr.other_deduct_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `otherDeductOneTimeSwitch` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.prismhr.other_deduct_one_time_switch`; retain source type and nested scope. |

#### PrismHRBenefit

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/Benefit).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `planId` | Optional[str] | Optional presence | string | benefit plan identifier | Preserve record/reference scope: `provider_fields.prismhr.plan_id` (Optional[str]); identifier helper, existing null acceptance. |
| `premiumAmt` | Optional[float] | Optional presence | number | benefit premium amount | Preserve separately: `provider_fields.prismhr.premium_amt` (Optional[float]); number helper, no inferred basis/scale. |
| `empContrib` | Optional[float] | Optional presence | number | employee contribution amount | Preserve separately: `provider_fields.prismhr.emp_contrib` (Optional[float]); number helper, no inferred basis/scale. |
| `empDeduct` | Optional[float] | Optional presence | number | amount deducted from paycheck | Preserve separately: `provider_fields.prismhr.emp_deduct` (Optional[float]); number helper, no inferred basis/scale. |
| `coveragePeriod` | Optional[str] | Optional presence | string | coverage period of benefit deduction | Preserve separately: `provider_fields.prismhr.coverage_period`; retain source type and nested scope. |
| `adjRef` | Optional[str] | Optional presence | string | adjustment reference number, if any | Preserve separately: `provider_fields.prismhr.adj_ref`; retain source type and nested scope. |
| `premiumCost` | Optional[float] | Optional presence | number | benefit premium cost amount | Preserve separately: `provider_fields.prismhr.premium_cost` (Optional[float]); number helper, no inferred basis/scale. |

#### PrismHRPayrollVoucherDirectDeposit

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/PayrollVoucher-DirectDeposit).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `transitNum` | Optional[str] | Optional presence | string | transit number for employee's financial institution | Preserve separately: `provider_fields.prismhr.transit_num`; retain source type and nested scope. |
| `accountNum` | Optional[str] | Optional presence | string | employee's account number | Preserve separately: `provider_fields.prismhr.account_num`; retain source type and nested scope. |
| `status` | Optional[str] | Optional presence | string | status of ACH transaction | Preserve separately: `provider_fields.prismhr.status`; retain source type and nested scope. |
| `amount` | Optional[float] | Optional presence | number | amount of ACH transaction | Preserve separately: `provider_fields.prismhr.amount` (Optional[float]); number helper, no inferred basis/scale. |

#### PrismHREmployerContribution

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/EmployerContribution).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `code` | Optional[str] | Optional presence | string | benefit plan identifier | Preserve separately: `provider_fields.prismhr.code`; retain source type and nested scope. |
| `description` | Optional[str] | Optional presence | string | description of the benefit plan | Preserve separately: `provider_fields.prismhr.description`; retain source type and nested scope. |
| `amount` | Optional[float] | Optional presence | number | amount of the employer contribution | Preserve separately: `provider_fields.prismhr.amount` (Optional[float]); number helper, no inferred basis/scale. |

#### PrismHRRetirement

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/Retirement).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `planId` | Optional[str] | Optional presence | string | No property description supplied. | Preserve record/reference scope: `provider_fields.prismhr.plan_id` (Optional[str]); identifier helper, existing null acceptance. |
| `planYearPeriod` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.prismhr.plan_year_period`; retain source type and nested scope. |
| `baseEarnings` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.prismhr.base_earnings` (Optional[float]); number helper, no inferred basis/scale. |
| `electiveContributionsPreTax` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.prismhr.elective_contributions_pre_tax` (Optional[float]); number helper, no inferred basis/scale. |
| `catchUpContributionsPreTax` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.prismhr.catch_up_contributions_pre_tax` (Optional[float]); number helper, no inferred basis/scale. |
| `rothContributionsPostTax` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.prismhr.roth_contributions_post_tax` (Optional[float]); number helper, no inferred basis/scale. |
| `rothCatchUpContributionsPostTax` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.prismhr.roth_catch_up_contributions_post_tax` (Optional[float]); number helper, no inferred basis/scale. |
| `employeeContributionsPostTax` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.prismhr.employee_contributions_post_tax` (Optional[float]); number helper, no inferred basis/scale. |
| `employerMatchingContributions` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.prismhr.employer_matching_contributions` (Optional[float]); number helper, no inferred basis/scale. |
| `employerNonElectiveContributions` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.prismhr.employer_non_elective_contributions` (Optional[float]); number helper, no inferred basis/scale. |
| `employerSafeHarborMatchType1` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.prismhr.employer_safe_harbor_match_type1` (Optional[float]); number helper, no inferred basis/scale. |
| `employerSafeHarborMatchType2` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.prismhr.employer_safe_harbor_match_type2` (Optional[float]); number helper, no inferred basis/scale. |
| `peoMatchingContribution` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.prismhr.peo_matching_contribution` (Optional[float]); number helper, no inferred basis/scale. |
| `employeeRetirementLoanPayments` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.prismhr.employee_retirement_loan_payments` (Optional[float]); number helper, no inferred basis/scale. |

#### PrismHRDebitSegmentDetail

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/DebitSegmentDetail).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `debitSegmentName` | Optional[str] | Optional presence | string | name of the debit account G/L segment | Preserve separately: `provider_fields.prismhr.debit_segment_name`; retain source type and nested scope. |
| `debitSegmentValue` | Optional[str] | Optional presence | string | value associated with the debit account segment | Preserve separately: `provider_fields.prismhr.debit_segment_value`; retain source type and nested scope. |

#### PrismHRGlDebitData

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/GlDebitData).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `glDebitAcct` | Optional[str] | Optional presence | string | general ledger account associated with this debit | Preserve separately: `provider_fields.prismhr.gl_debit_acct`; retain source type and nested scope. |
| `glDebitAmount` | Optional[float] | Optional presence | number | amount debited to the G/L account | Preserve separately: `provider_fields.prismhr.gl_debit_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `debitSegmentDetail` | Optional[List[PrismHRDebitSegmentDetail]] | Optional presence | array | description of the debit account G/L segment | Preserve separately: `provider_fields.prismhr.debit_segment_detail`; retain source type and nested scope. |

#### PrismHRCreditSegmentDetail

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/CreditSegmentDetail).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `creditSegmentName` | Optional[str] | Optional presence | string | name of the credit account G/L segment | Preserve separately: `provider_fields.prismhr.credit_segment_name`; retain source type and nested scope. |
| `creditSegmentValue` | Optional[str] | Optional presence | string | value associated with the credit account segment | Preserve separately: `provider_fields.prismhr.credit_segment_value`; retain source type and nested scope. |

#### PrismHRGlCreditData

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/GlCreditData).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `glCreditAcct` | Optional[str] | Optional presence | string | general ledger account associated with this credit | Preserve separately: `provider_fields.prismhr.gl_credit_acct`; retain source type and nested scope. |
| `glCreditAmount` | Optional[float] | Optional presence | number | amount credited to the G/L account | Preserve separately: `provider_fields.prismhr.gl_credit_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `creditSegmentDetail` | Optional[List[PrismHRCreditSegmentDetail]] | Optional presence | array | description of the credit account G/L segment | Preserve separately: `provider_fields.prismhr.credit_segment_detail`; retain source type and nested scope. |

#### PrismHRGlAcctDistribution

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/GlAcctDistribution).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `glTotalDebit` | Optional[float] | Optional presence | number | total G/L debits associated with the voucher | Preserve separately: `provider_fields.prismhr.gl_total_debit` (Optional[float]); number helper, no inferred basis/scale. |
| `glTotalCredit` | Optional[float] | Optional presence | number | total G/L credits associated with the voucher | Preserve separately: `provider_fields.prismhr.gl_total_credit` (Optional[float]); number helper, no inferred basis/scale. |
| `glDebitData` | Optional[List[PrismHRGlDebitData]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.prismhr.gl_debit_data`; retain source type and nested scope. |
| `glCreditData` | Optional[List[PrismHRGlCreditData]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.prismhr.gl_credit_data`; retain source type and nested scope. |

#### PrismHRAsoCredits

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/AsoCredits).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `glCreditAcct` | Optional[str] | Optional presence | string | client accounting credit account code | Preserve separately: `provider_fields.prismhr.gl_credit_acct`; retain source type and nested scope. |
| `glCreditAcctDesc` | Optional[str] | Optional presence | string | client accounting credit account description | Preserve separately: `provider_fields.prismhr.gl_credit_acct_desc`; retain source type and nested scope. |
| `glTotalCredit` | Optional[float] | Optional presence | number | client accounting credit amount | Preserve separately: `provider_fields.prismhr.gl_total_credit` (Optional[float]); number helper, no inferred basis/scale. |

#### PrismHRAsoDebits

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/AsoDebits).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `glDebitAcct` | Optional[str] | Optional presence | string | client accounting debit account code | Preserve separately: `provider_fields.prismhr.gl_debit_acct`; retain source type and nested scope. |
| `glDebitAcctDesc` | Optional[str] | Optional presence | string | client accounting debit account description | Preserve separately: `provider_fields.prismhr.gl_debit_acct_desc`; retain source type and nested scope. |
| `glTotalDebit` | Optional[float] | Optional presence | number | client accounting debit amount | Preserve separately: `provider_fields.prismhr.gl_total_debit` (Optional[float]); number helper, no inferred basis/scale. |

#### PrismHRAsoClientGLAcctDistribution

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/AsoClientGLAcctDistribution).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `asoCredits` | Optional[List[PrismHRAsoCredits]] | Optional presence | array | client accounting credits | Preserve separately: `provider_fields.prismhr.aso_credits`; retain source type and nested scope. |
| `asoDebits` | Optional[List[PrismHRAsoDebits]] | Optional presence | array | client accounting debits | Preserve separately: `provider_fields.prismhr.aso_debits`; retain source type and nested scope. |

#### PrismHRTaxFilingStatus

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/TaxFilingStatus).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `taxAuthId` | Optional[str] | Optional presence | string | tax authority identifier | Preserve record/reference scope: `provider_fields.prismhr.tax_auth_id` (Optional[str]); identifier helper, existing null acceptance. |
| `taxAuthName` | Optional[str] | Optional presence | string | name or description of tax authority | Preserve separately: `provider_fields.prismhr.tax_auth_name`; retain source type and nested scope. |
| `filingStatus` | Optional[str] | Optional presence | string | employee tax filing status for this authority | Preserve separately: `provider_fields.prismhr.filing_status`; retain source type and nested scope. |
| `allowances` | Optional[str] | Optional presence | string | allowances taken by the employee | Preserve separately: `provider_fields.prismhr.allowances`; retain source type and nested scope. |
| `overrideType` | Optional[str] | Optional presence | string | type of tax calculation override for this employee, such as adding a fixed amount, multiplying by a different percentage, or blocking the withholding calculation. | Preserve separately: `provider_fields.prismhr.override_type`; retain source type and nested scope. |
| `overrideAmount` | Optional[str] | Optional presence | string | amount to use in the tax calculation override. The role of this amount is different depending on the overrideType. | Preserve separately: `provider_fields.prismhr.override_amount`; retain source type and nested scope. |

#### PrismHRPayrollVoucherWCInformation

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/PayrollVoucherWCInformation).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `wcPolicy` | Optional[str] | Optional presence | string | Workers' Compensation policy ID | Preserve separately: `provider_fields.prismhr.wc_policy`; retain source type and nested scope. |
| `wcNotEligible` | Optional[List[str]] | Optional presence | array | indicates whether an employee is not eligible for Workers' Compensation | Preserve separately: `provider_fields.prismhr.wc_not_eligible`; retain source type and nested scope. |
| `wcSheltered` | Optional[List[str]] | Optional presence | array | Workers' Compensation sheltered payments | Preserve separately: `provider_fields.prismhr.wc_sheltered`; retain source type and nested scope. |
| `wcOverBillRate` | Optional[List[str]] | Optional presence | array | Workers' Compensation payments above the bill rate | Preserve separately: `provider_fields.prismhr.wc_over_bill_rate`; retain source type and nested scope. |
| `wcBillIncludeCredit` | Optional[List[str]] | Optional presence | array | regular pay amount if the earning code is set to bill/credit back | Preserve separately: `provider_fields.prismhr.wc_bill_include_credit`; retain source type and nested scope. |
| `wcBillAmtIncludeCredit` | Optional[List[str]] | Optional presence | array | wc credit premium amount | Preserve separately: `provider_fields.prismhr.wc_bill_amt_include_credit`; retain source type and nested scope. |
| `wcWeekEndDate` | Optional[str] | Optional presence | string | date when the Workers' Compensation policy week ends | Preserve separately: `provider_fields.prismhr.wc_week_end_date` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `wcPolicyYearEnd` | Optional[str] | Optional presence | string | end date of the Workers' Compensation policy year | Preserve separately: `provider_fields.prismhr.wc_policy_year_end` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `wcPremiumPay` | Optional[List[str]] | Optional presence | array | Workers' Compensation premium payments | Preserve separately: `provider_fields.prismhr.wc_premium_pay`; retain source type and nested scope. |
| `wcTria` | Optional[List[str]] | Optional presence | array | compensation that is covered by the Terrorism Risk Insurance Act (TRIA), if applicable | Preserve separately: `provider_fields.prismhr.wc_tria`; retain source type and nested scope. |
| `wcRateTemplate` | Optional[str] | Optional presence | string | rate template associated with the W/C plan | Preserve separately: `provider_fields.prismhr.wc_rate_template`; retain source type and nested scope. |
| `wcOverBillAmt` | Optional[List[str]] | Optional presence | array | Workers' Compensation amount over the amount billed | Preserve separately: `provider_fields.prismhr.wc_over_bill_amt`; retain source type and nested scope. |
| `wcGrossRate` | Optional[List[str]] | Optional presence | array | gross Workers' Compensation calculation rate | Preserve separately: `provider_fields.prismhr.wc_gross_rate`; retain source type and nested scope. |
| `wcStraightPay` | Optional[List[str]] | Optional presence | array | Workers' Compensation straight payments | Preserve separately: `provider_fields.prismhr.wc_straight_pay`; retain source type and nested scope. |
| `wcPremAmt` | Optional[List[str]] | Optional presence | array | Workers' Compensation premium amount | Preserve separately: `provider_fields.prismhr.wc_prem_amt`; retain source type and nested scope. |
| `wcClass` | Optional[List[str]] | Optional presence | array | employee Workers' Compensation class | Preserve separately: `provider_fields.prismhr.wc_class`; retain source type and nested scope. |
| `wcBasePay` | Optional[List[str]] | Optional presence | array | Workers' Compensation base pay | Preserve separately: `provider_fields.prismhr.wc_base_pay`; retain source type and nested scope. |
| `wcBillAmt` | Optional[List[str]] | Optional presence | array | amount to bill for Workers' Compensation | Preserve separately: `provider_fields.prismhr.wc_bill_amt`; retain source type and nested scope. |
| `wcTaxablePay` | Optional[List[str]] | Optional presence | array | Workers' Compensation pay that is taxable | Preserve separately: `provider_fields.prismhr.wc_taxable_pay`; retain source type and nested scope. |
| `wcPremiumBill` | Optional[List[str]] | Optional presence | array | amount billed for Workers' Compensation premium | Preserve separately: `provider_fields.prismhr.wc_premium_bill`; retain source type and nested scope. |
| `wcAccruedAmt` | Optional[List[str]] | Optional presence | array | total amount of Workers' Compensation payments accrued | Preserve separately: `provider_fields.prismhr.wc_accrued_amt`; retain source type and nested scope. |
| `wcState` | Optional[str] | Optional presence | string | Workers' Compensation state | Preserve separately: `provider_fields.prismhr.wc_state`; retain source type and nested scope. |
| `wcHoursWorked` | Optional[List[str]] | Optional presence | array | Workers' Compensation hours worked | Preserve separately: `provider_fields.prismhr.wc_hours_worked`; retain source type and nested scope. |
| `wcEarnNonComp` | Optional[List[str]] | Optional presence | array | Workers' Compensation hours worked | Preserve separately: `provider_fields.prismhr.wc_earn_non_comp`; retain source type and nested scope. |
| `wcPayLocationReg` | Optional[List[str]] | Optional presence | array | regular pay location | Preserve separately: `provider_fields.prismhr.wc_pay_location_reg`; retain source type and nested scope. |
| `wcPayLocationOT` | Optional[List[str]] | Optional presence | array | overtime pay location | Preserve separately: `provider_fields.prismhr.wc_pay_location_ot`; retain source type and nested scope. |
| `wcPayLocationBreakCode` | Optional[List[str]] | Optional presence | array | identifies department and pay code based billing when calculating premiums. Breaks will be separated by a period and include pay code, job code, price level and work department | Preserve separately: `provider_fields.prismhr.wc_pay_location_break_code`; retain source type and nested scope. |
| `wcRecalcDifference` | Optional[List[str]] | Optional presence | array | difference between original and recalculated Workers' Compensation | Preserve separately: `provider_fields.prismhr.wc_recalc_difference`; retain source type and nested scope. |
| `wcLocationState` | Optional[List[str]] | Optional presence | array | W/C state associated with the location | Preserve separately: `provider_fields.prismhr.wc_location_state`; retain source type and nested scope. |
| `wcLocationPolicy` | Optional[List[str]] | Optional presence | array | W/C policy associated with the location | Preserve separately: `provider_fields.prismhr.wc_location_policy`; retain source type and nested scope. |
| `wcLocationYearEndDate` | Optional[List[str]] | Optional presence | array | W/C year end date associated with the location | Preserve separately: `provider_fields.prismhr.wc_location_year_end_date`; retain source type and nested scope. |
| `wcLocationTemplate` | Optional[List[str]] | Optional presence | array | W/C rate template associated with the location | Preserve separately: `provider_fields.prismhr.wc_location_template`; retain source type and nested scope. |
| `wcPayLocationExp` | Optional[List[str]] | Optional presence | array | regular pay amount related to wcPayLocationBreakCode | Preserve separately: `provider_fields.prismhr.wc_pay_location_exp`; retain source type and nested scope. |

#### PrismHRFromArrears

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/FromArrears).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `dedCode` | Optional[str] | Optional presence | string | arrears deduction code | Preserve separately: `provider_fields.prismhr.ded_code`; retain source type and nested scope. |
| `dedDescription` | Optional[str] | Optional presence | string | description of the arrears deduction code | Preserve separately: `provider_fields.prismhr.ded_description`; retain source type and nested scope. |
| `arrearsAmt` | Optional[str] | Optional presence | string | amount in arrears | Preserve separately: `provider_fields.prismhr.arrears_amt`; retain source type and nested scope. |
| `arrearsDate` | Optional[str] | Optional presence | string | date of arrears transaction (format: YYYY-MM-DD) | Preserve separately: `provider_fields.prismhr.arrears_date` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `arrearsRefNo` | Optional[str] | Optional presence | string | payroll reference number | Preserve separately: `provider_fields.prismhr.arrears_ref_no`; retain source type and nested scope. |
| `coveragePeriod` | Optional[str] | Optional presence | string | benefit plan coverage period, if applicable | Preserve separately: `provider_fields.prismhr.coverage_period`; retain source type and nested scope. |
| `planId` | Optional[str] | Optional presence | string | benefit plan ID associated with arrears, if applicable | Preserve record/reference scope: `provider_fields.prismhr.plan_id` (Optional[str]); identifier helper, existing null acceptance. |
| `unionId` | Optional[str] | Optional presence | string | associated union code, if applicable | Preserve record/reference scope: `provider_fields.prismhr.union_id` (Optional[str]); identifier helper, existing null acceptance. |
| `loanNo` | Optional[str] | Optional presence | string | ID of the employee loan in arrears, if applicable | Preserve separately: `provider_fields.prismhr.loan_no`; retain source type and nested scope. |

#### PrismHRToArrears

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/ToArrears).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `dedCode` | Optional[str] | Optional presence | string | arrears deduction code | Preserve separately: `provider_fields.prismhr.ded_code`; retain source type and nested scope. |
| `dedDescription` | Optional[str] | Optional presence | string | description of the arrears deduction code | Preserve separately: `provider_fields.prismhr.ded_description`; retain source type and nested scope. |
| `arrearsAmt` | Optional[str] | Optional presence | string | amount in arrears | Preserve separately: `provider_fields.prismhr.arrears_amt`; retain source type and nested scope. |
| `coveragePeriod` | Optional[str] | Optional presence | string | benefit plan coverage period, if applicable | Preserve separately: `provider_fields.prismhr.coverage_period`; retain source type and nested scope. |
| `planId` | Optional[str] | Optional presence | string | benefit plan ID associated with arrears, if applicable | Preserve record/reference scope: `provider_fields.prismhr.plan_id` (Optional[str]); identifier helper, existing null acceptance. |
| `unionId` | Optional[str] | Optional presence | string | associated union code, if applicable | Preserve record/reference scope: `provider_fields.prismhr.union_id` (Optional[str]); identifier helper, existing null acceptance. |
| `loanNo` | Optional[str] | Optional presence | string | ID of the employee loan in arrears, if applicable | Preserve separately: `provider_fields.prismhr.loan_no`; retain source type and nested scope. |

#### PrismHRPayrollVoucher

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/PayrollVoucher).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `voucherId` | str | Required presence | string | payroll voucher identifier | Shared: `paycheck_id`. Use the agreed helper; preserve converted source originals/issues. |
| `status` | Optional[str] | Optional presence | string | voucher status, such as printed | Preserve separately: `provider_fields.prismhr.status`; retain source type and nested scope. |
| `type` | Optional[str] | Optional presence | string | voucher type: 'R' (Regular), 'V' (Vacation), or 'S' (Supplemental), 'A' (Arrears), 'J' (Adjustment) | Preserve separately: `provider_fields.prismhr.type`; retain source type and nested scope. |
| `voidDate` | Optional[str] | Optional presence | string | date on which voucher was voided, if applicable | Preserve separately: `provider_fields.prismhr.void_date` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `checkNumber` | Optional[str] | Optional presence | string | paycheck number | Decided shared: `check_number` (Optional[str]); use one supplied/agreed value, preserve both originals and report conflicts. |
| `payDate` | Optional[str] | Optional presence | string | date of pay | Shared: `pay_date`. Use the agreed helper; preserve converted source originals/issues. |
| `employeeId` | Optional[str] | Optional presence | string | employee identifier | Shared: `employee_id`. Use the agreed helper; preserve converted source originals/issues. |
| `payPeriod` | Optional[str] | Optional presence | string | the period for which the employee was paid | Preserve separately: `provider_fields.prismhr.pay_period`; retain source type and nested scope. |
| `payPeriodStart` | Optional[str] | Optional presence | string | pay period start date | Shared: `period_start_date`. Use the agreed helper; preserve converted source originals/issues. |
| `payPeriodEnd` | Optional[str] | Optional presence | string | pay period end date | Shared: `period_end_date`. Use the agreed helper; preserve converted source originals/issues. |
| `payGroup` | Optional[str] | Optional presence | string | pay group | Preserve separately: `provider_fields.prismhr.pay_group`; retain source type and nested scope. |
| `dateProcessed` | Optional[str] | Optional presence | string | date on which the payroll voucher was processed | Preserve separately: `provider_fields.prismhr.date_processed` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `totalEarnings` | Optional[float] | Optional presence | number | total earnings during the pay period | Preserve separately: `provider_fields.prismhr.total_earnings` (Optional[float]); number helper, no inferred basis/scale. |
| `employeeTax` | Optional[List[PrismHREmployeeTax]] | Optional presence | array | taxes deducted from employee's paycheck | Preserve separately: `provider_fields.prismhr.employee_tax`; retain source type and nested scope. |
| `netPay` | Optional[float] | Optional presence | number | net pay amount from employee's paycheck | Shared: `net_pay`. Use the agreed helper; preserve converted source originals/issues. |
| `voidVoucherId` | Optional[str] | Optional presence | string | void voucher identifier, if any | Preserve record/reference scope: `provider_fields.prismhr.void_voucher_id` (Optional[str]); identifier helper, existing null acceptance. |
| `fitTaxableAmount` | Optional[float] | Optional presence | number | federal income taxable amount | Preserve separately: `provider_fields.prismhr.fit_taxable_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `earnAmount` | Optional[float] | Optional presence | number | time sheet earnings amount | Preserve separately: `provider_fields.prismhr.earn_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `otherEarnAmount` | Optional[float] | Optional presence | number | other earnings amount | Preserve separately: `provider_fields.prismhr.other_earn_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `wcHomeClass` | Optional[str] | Optional presence | string | workers' compensation classification code | Preserve separately: `provider_fields.prismhr.wc_home_class`; retain source type and nested scope. |
| `wcState` | Optional[str] | Optional presence | string | workers' compensation state code | Preserve separately: `provider_fields.prismhr.wc_state`; retain source type and nested scope. |
| `workerComp` | Optional[List[PrismHRWorkerComp]] | Optional presence | array | workers' compensation information for this voucher | Preserve separately: `provider_fields.prismhr.worker_comp`; retain source type and nested scope. |
| `earning` | Optional[List[PrismHREarning]] | Optional presence | array | pay information from time sheet | Preserve separately: `provider_fields.prismhr.earning`; retain source type and nested scope. |
| `otherEarningsDetail` | Optional[List[PrismHROtherEarningsDetail]] | Optional presence | array | other earnings list | Preserve separately: `provider_fields.prismhr.other_earnings_detail`; retain source type and nested scope. |
| `fsaMatch` | Optional[List[PrismHRFsaMatch]] | Optional presence | array | fsa matches list | Preserve separately: `provider_fields.prismhr.fsa_match`; retain source type and nested scope. |
| `companyTax` | Optional[List[PrismHRCompanyTax]] | Optional presence | array | tax information for this voucher | Preserve separately: `provider_fields.prismhr.company_tax`; retain source type and nested scope. |
| `batchId` | Optional[str] | Optional presence | string | payroll batch identifier | Preserve record/reference scope: `provider_fields.prismhr.batch_id` (Optional[str]); identifier helper, existing null acceptance. |
| `deduction` | Optional[List[PrismHRDeduction]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.prismhr.deduction`; retain source type and nested scope. |
| `otherDeduction` | Optional[List[PrismHROtherDeduction]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.prismhr.other_deduction`; retain source type and nested scope. |
| `benefit` | Optional[List[PrismHRBenefit]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.prismhr.benefit`; retain source type and nested scope. |
| `bankAccount` | Optional[str] | Optional presence | string | account identifier for the financial institution from which the paycheck was drawn | Preserve separately: `provider_fields.prismhr.bank_account`; retain source type and nested scope. |
| `checkNum` | Optional[str] | Optional presence | string | paycheck number | Decided shared: `check_number` (Optional[str]); use one supplied/agreed value, preserve both originals and report conflicts. |
| `checkAmt` | Optional[float] | Optional presence | number | paycheck amount | Preserve separately: `provider_fields.prismhr.check_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `payStubType` | Optional[str] | Optional presence | string | type of pay stub: Paper or Electronic | Preserve separately: `provider_fields.prismhr.pay_stub_type`; retain source type and nested scope. |
| `checkAccountACH` | Optional[str] | Optional presence | string | account identifier for the financial institution from which the direct deposit (ACH) was drawn | Preserve record/reference scope: `provider_fields.prismhr.check_account_ach` (Optional[str]); identifier helper, existing null acceptance. |
| `directDeposit` | Optional[List[PrismHRPayrollVoucherDirectDeposit]] | Optional presence | array | direct deposit | Preserve separately: `provider_fields.prismhr.direct_deposit`; retain source type and nested scope. |
| `employerContributions` | Optional[List[PrismHREmployerContribution]] | Optional presence | array | an array of objects showing the benefit plan code, description, and amount of employer contributions | Preserve separately: `provider_fields.prismhr.employer_contributions`; retain source type and nested scope. |
| `retirement` | Optional[PrismHRRetirement] | Optional presence | #/components/schemas/Retirement | No property description supplied. | Preserve separately: `provider_fields.prismhr.retirement`; retain source type and nested scope. |
| `glAcctDistribution` | Optional[PrismHRGlAcctDistribution] | Optional presence | #/components/schemas/GlAcctDistribution | No property description supplied. | Preserve separately: `provider_fields.prismhr.gl_acct_distribution`; retain source type and nested scope. |
| `asoClientGLAcctDistribution` | Optional[PrismHRAsoClientGLAcctDistribution] | Optional presence | #/components/schemas/AsoClientGLAcctDistribution | No property description supplied. | Preserve separately: `provider_fields.prismhr.aso_client_gl_acct_distribution`; retain source type and nested scope. |
| `taxFilingStatus` | Optional[List[PrismHRTaxFilingStatus]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.prismhr.tax_filing_status`; retain source type and nested scope. |
| `wcInformation` | Optional[PrismHRPayrollVoucherWCInformation] | Optional presence | #/components/schemas/PayrollVoucherWCInformation | No property description supplied. | Preserve separately: `provider_fields.prismhr.wc_information`; retain source type and nested scope. |
| `fromArrears` | Optional[List[PrismHRFromArrears]] | Optional presence | array | from Arrears For Voucher | Preserve separately: `provider_fields.prismhr.from_arrears`; retain source type and nested scope. |
| `toArrears` | Optional[List[PrismHRToArrears]] | Optional presence | array | to Arrears For Voucher | Preserve separately: `provider_fields.prismhr.to_arrears`; retain source type and nested scope. |
| `importBatchNo` | Optional[str] | Optional presence | string | identifier for pre-existing, imported payroll batches that were processed outside of PrismHR; takes the place of the batchId assigned to internal batches | Preserve record/reference scope: `provider_fields.prismhr.import_batch_no` (Optional[str]); identifier helper, existing null acceptance. |
| `isManualCheck` | Optional[str] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Preserve separately: `provider_fields.prismhr.is_manual_check`; retain source type and nested scope. |
| `hsaPeoMatch` | Optional[str] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Preserve separately: `provider_fields.prismhr.hsa_peo_match`; retain source type and nested scope. |

#### PrismHRPayrollResponseWithPagination

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_paycheck.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/PayrollResponseWithPagination).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `errorCode` | str | Required presence | string | No property description supplied. | Metadata: `source_metadata.prismhr.response`; retain source field/nesting. |
| `errorMessage` | str | Required presence | string | No property description supplied. | Metadata: `source_metadata.prismhr.response`; retain source field/nesting. |
| `extension` | Optional[PrismHRExtension] | Optional presence | #/components/schemas/Extension | No property description supplied. | Metadata: `source_metadata.prismhr.response`; retain source field/nesting. |
| `payrollVouchers`; accepted aliases: payrollVouchers, payrollVoucher | Optional[List[PrismHRPayrollVoucher]] | Optional presence | array | payrollVoucher | Container: map each paycheck; preserve paging/wrapper fields separately. Source validation accepts payrollVouchers and live payrollVoucher. |
| `total` | Optional[int] | Optional presence | integer | total vouchers returned | Metadata: `source_metadata.prismhr.response`; retain source field/nesting. |
| `startpage` | Optional[int] | Optional presence | integer | pagination startpage location | Metadata: `source_metadata.prismhr.response`; retain source field/nesting. |
| `count` | Optional[int] | Optional presence | integer | number of vouchers returned per page | Metadata: `source_metadata.prismhr.response`; retain source field/nesting. |

### isolved

#### IsolvedPayrollInput

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · Project input/container; no independent provider schema.

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `payroll_runs` | Optional[List[IsolvedPayrollRunHistoryModel]] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Container: validate/map this supplied record family separately; preserve scope and originals. |
| `paychecks` | Optional[List[IsolvedCheckModel]] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Container: validate/map this supplied record family separately; preserve scope and originals. |
| `results` | Optional[List[IsolvedCheckModel]] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Container: validate/map this supplied record family separately; preserve scope and originals. |
| `nextPageUrl` | Optional[str] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Metadata: `source_metadata.isolved.response`; retain paging without fetching pages. |
| `previousPageUrl` | Optional[str] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Metadata: `source_metadata.isolved.response`; retain paging without fetching pages. |
| `totalItems` | Optional[int] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Metadata: `source_metadata.isolved.response`; retain paging without fetching pages. |
| `totalPages` | Optional[float] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Metadata: `source_metadata.isolved.response`; retain paging without fetching pages. |

#### IsolvedPayrollRunHistoryModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.PayrollRunHistoryModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Id for payroll run history | Shared: `payroll_run_id`. Use the agreed helper; preserve converted source originals/issues. |
| `impoundDate` | Optional[str] | Optional presence | string / date-time | Date Tax liability are deducted | Preserve separately: `provider_fields.isolved.impound_date` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `inputMethod` | Optional[str] | Optional presence | string | Method which the payroll was input | Preserve separately: `provider_fields.isolved.input_method`; retain source type and nested scope. |
| `payDate` | Optional[str] | Optional presence | string / date-time | Date the pay was paid to the employees | Shared: `payroll_run_pay_date`. Use the agreed helper; preserve converted source originals/issues. |
| `payOfTheMonth` | Optional[str] | Optional presence | string | Schedule description name for the payroll | Preserve separately: `provider_fields.isolved.pay_of_the_month`; retain source type and nested scope. |
| `payPeriod` | Optional[int] | Optional presence | integer / int32 | Pay period sequence number | Preserve separately: `provider_fields.isolved.pay_period`; retain source type and nested scope. |
| `payrollRunType` | Optional[str] | Optional presence | string | Type of payroll that was run | Preserve separately: `provider_fields.isolved.payroll_run_type`; retain source type and nested scope. |
| `periodBeginDate` | Optional[str] | Optional presence | string / date-time | Date the pay period started | Decided run-level: `payroll_run_period_start_date` (Optional[date]); date helper and originals. |
| `periodEndDate` | Optional[str] | Optional presence | string / date-time | Date the pay period ended | Decided run-level: `payroll_run_period_end_date` (Optional[date]); date helper and originals. |
| `processApprovedBy` | Optional[str] | Optional presence | string | Name of the person who approved the payroll | Preserve separately: `provider_fields.isolved.process_approved_by`; retain source type and nested scope. |
| `processedBy` | Optional[str] | Optional presence | string | Name of the person who processed the payroll | Preserve separately: `provider_fields.isolved.processed_by`; retain source type and nested scope. |
| `regularCheckAutoPay` | Optional[bool] | Optional presence | boolean | Boolean flag to show if this is a regular auto paying check | Preserve separately: `provider_fields.isolved.regular_check_auto_pay`; retain source type and nested scope. |
| `runDate` | Optional[str] | Optional presence | string / date-time | Date when the payroll was run | Preserve separately: `provider_fields.isolved.run_date` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `runNumber` | Optional[int] | Optional presence | integer / int32 | Run sequence number | Preserve separately: `provider_fields.isolved.run_number`; retain source type and nested scope. |
| `runTime` | Optional[str] | Optional presence | string | Time when the payroll was run | Preserve separately: `provider_fields.isolved.run_time`; retain source type and nested scope. |
| `scheduledPayDate` | Optional[str] | Optional presence | string / date-time | Date pay is scheduled to be paid out to employee | Preserve separately: `provider_fields.isolved.scheduled_pay_date` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `scheduledRunDate` | Optional[str] | Optional presence | string / date-time | Date payroll was scheduled to run | Preserve separately: `provider_fields.isolved.scheduled_run_date` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `status` | Optional[str] | Optional presence | string | Status of the payroll | Preserve separately: `provider_fields.isolved.status`; retain source type and nested scope. |
| `submittedBy` | Optional[str] | Optional presence | string | Name of the person who submitted the payroll | Preserve separately: `provider_fields.isolved.submitted_by`; retain source type and nested scope. |
| `submittedDate` | Optional[str] | Optional presence | string / date-time | Date when the payroll was submitted | Preserve separately: `provider_fields.isolved.submitted_date` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `submittedTime` | Optional[str] | Optional presence | string | Time when the payroll was submitted | Preserve separately: `provider_fields.isolved.submitted_time`; retain source type and nested scope. |
| `suppressPayStubEmailAlert` | Optional[bool] | Optional presence | boolean | Boolean flag to show is email alerts are suppressed | Preserve separately: `provider_fields.isolved.suppress_pay_stub_email_alert`; retain source type and nested scope. |

#### IsolvedCheckModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.CheckModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int64 | Unique Object Id | Shared: `paycheck_id`. Use the agreed helper; preserve converted source originals/issues. |
| `accruals` | Optional[List[IsolvedCheckAccrualModel]] | Optional presence | array | Accruals | Preserve separately: `provider_fields.isolved.accruals`; retain source type and nested scope. |
| `benefits` | Optional[List[IsolvedCheckBenefitTypeAccumulationModel]] | Optional presence | array | Benefits | Preserve separately: `provider_fields.isolved.benefits`; retain source type and nested scope. |
| `checkAmount` | Optional[float] | Optional presence | number / double | Check Amount | Preserve separately: `provider_fields.isolved.check_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `checkDate` | Optional[str] | Optional presence | string / date-time | Check Date | Shared: `pay_date`. Use the agreed helper; preserve converted source originals/issues. |
| `checkNumber` | Optional[int] | Optional presence | integer / int32 | Check Number | Shared: `check_number`. Use the agreed helper; preserve converted source originals/issues. |
| `checkSequence` | Optional[int] | Optional presence | integer / int32 | Check Sequence | Preserve separately: `provider_fields.isolved.check_sequence`; retain source type and nested scope. |
| `checkTypeDescription` | Optional[str] | Optional presence | string | Check Type Description | Preserve separately: `provider_fields.isolved.check_type_description`; retain source type and nested scope. |
| `deductions` | Optional[List[IsolvedCheckAccumulationModel]] | Optional presence | array | Deductions | Preserve separately: `provider_fields.isolved.deductions`; retain source type and nested scope. |
| `directDepositAmount` | Optional[float] | Optional presence | number / double | Direct Deposit Amount | Preserve separately: `provider_fields.isolved.direct_deposit_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `directDeposits` | Optional[List[IsolvedCheckDirectDepositAccumulationModel]] | Optional presence | array | Direct Deposits | Preserve separately: `provider_fields.isolved.direct_deposits`; retain source type and nested scope. |
| `earnings` | Optional[List[IsolvedCheckEarningAccumulationModel]] | Optional presence | array | Earnings | Preserve separately: `provider_fields.isolved.earnings`; retain source type and nested scope. |
| `employeeAddress1` | Optional[str] | Optional presence | string | Employee Address Line 1 | Preserve separately: `provider_fields.isolved.employee_address1`; retain source type and nested scope. |
| `employeeAddress2` | Optional[str] | Optional presence | string | Employee Address Line 2 | Preserve separately: `provider_fields.isolved.employee_address2`; retain source type and nested scope. |
| `employeeCity` | Optional[str] | Optional presence | string | Employee City | Preserve separately: `provider_fields.isolved.employee_city`; retain source type and nested scope. |
| `employeeFederalAddlAmountOrPercent` | Optional[str] | Optional presence | string | Employee Federal Additional Amount or Percent | Preserve separately: `provider_fields.isolved.employee_federal_addl_amount_or_percent`; retain source type and nested scope. |
| `employeeFederalExemptions` | Optional[int] | Optional presence | integer / int32 | Employee Federal Exemptions | Preserve separately: `provider_fields.isolved.employee_federal_exemptions`; retain source type and nested scope. |
| `employeeFederalFilingStatus` | Optional[str] | Optional presence | string | Employee Federal Filing Status | Preserve separately: `provider_fields.isolved.employee_federal_filing_status`; retain source type and nested scope. |
| `employeeId` | Optional[int] | Optional presence | integer / int32 | Employee Id | Shared: `employee_id`. Use the agreed helper; preserve converted source originals/issues. |
| `employeeName` | Optional[str] | Optional presence | string | Employee Name | Preserve separately: `provider_fields.isolved.employee_name`; retain source type and nested scope. |
| `employeeNumber` | Optional[str] | Optional presence | string | Employee Number | Preserve separately: `provider_fields.isolved.employee_number`; retain source type and nested scope. |
| `employeeOrganizations` | Optional[List[IsolvedEmployeeOrganizationModel]] | Optional presence | array | Employee Organizations | Preserve separately: `provider_fields.isolved.employee_organizations`; retain source type and nested scope. |
| `employeeSSN` | Optional[str] | Optional presence | string | Employee Social Security Number | Preserve separately: `provider_fields.isolved.employee_ssn`; retain source type and nested scope. |
| `employeeState` | Optional[str] | Optional presence | string | Employee State | Preserve separately: `provider_fields.isolved.employee_state`; retain source type and nested scope. |
| `employeeStateAddlAmountOrPercent` | Optional[str] | Optional presence | string | Employee State Additional Amount or Percent | Preserve separately: `provider_fields.isolved.employee_state_addl_amount_or_percent`; retain source type and nested scope. |
| `employeeStateExemptions` | Optional[int] | Optional presence | integer / int32 | Employee State Exemptions | Preserve separately: `provider_fields.isolved.employee_state_exemptions`; retain source type and nested scope. |
| `employeeStateFilingStatus` | Optional[str] | Optional presence | string | Employee State Filing Status | Preserve separately: `provider_fields.isolved.employee_state_filing_status`; retain source type and nested scope. |
| `employeeZipCode` | Optional[str] | Optional presence | string | Employee Zip Code | Preserve separately: `provider_fields.isolved.employee_zip_code`; retain source type and nested scope. |
| `garnishments` | Optional[List[IsolvedCheckAccumulationModel]] | Optional presence | array | Garnishments | Preserve separately: `provider_fields.isolved.garnishments`; retain source type and nested scope. |
| `grossPay` | Optional[float] | Optional presence | number / double | Gross Pay | Shared: `gross_pay`. Use the agreed helper; preserve converted source originals/issues. |
| `grossWages` | Optional[float] | Optional presence | number / double | Gross Wages | Preserve separately: `provider_fields.isolved.gross_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `isRemoteWorker` | Optional[bool] | Optional presence | boolean | Remote Worker Indicator | Preserve separately: `provider_fields.isolved.is_remote_worker`; retain source type and nested scope. |
| `legalCompanyName` | Optional[str] | Optional presence | string | Legal Company Name | Preserve separately: `provider_fields.isolved.legal_company_name`; retain source type and nested scope. |
| `netPay` | Optional[float] | Optional presence | number / double | Net Pay | Shared: `net_pay`. Use the agreed helper; preserve converted source originals/issues. |
| `payrollRunNumber` | Optional[int] | Optional presence | integer / int32 | Payroll Run Number | Preserve separately: `provider_fields.isolved.payroll_run_number`; retain source type and nested scope. |
| `payrollRunType` | Optional[str] | Optional presence | string | Payroll Run Type | Preserve separately: `provider_fields.isolved.payroll_run_type`; retain source type and nested scope. |
| `periodBeginDate` | Optional[str] | Optional presence | string / date-time | Period Begin Date | Shared: `period_start_date`. Use the agreed helper; preserve converted source originals/issues. |
| `periodEndDate` | Optional[str] | Optional presence | string / date-time | Period End Date | Shared: `period_end_date`. Use the agreed helper; preserve converted source originals/issues. |
| `reissueCheckDate` | Optional[str] | Optional presence | string / date-time | Reissue Check Date | Preserve separately: `provider_fields.isolved.reissue_check_date` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `reissueCheckNumber` | Optional[int] | Optional presence | integer / int32 | Reissue Check Number | Preserve record/reference scope: `provider_fields.isolved.reissue_check_number` (Optional[str]); identifier helper, existing null acceptance. |
| `taxCategories` | Optional[List[IsolvedCheckTaxCategoryModel]] | Optional presence | array | Tax Categories | Preserve separately: `provider_fields.isolved.tax_categories`; retain source type and nested scope. |
| `taxes` | Optional[List[IsolvedCheckTaxAccumulationModel]] | Optional presence | array | Taxes | Preserve separately: `provider_fields.isolved.taxes`; retain source type and nested scope. |
| `vertexResidentGeoCode` | Optional[str] | Optional presence | string | Vertex Resident Geo Code | Preserve separately: `provider_fields.isolved.vertex_resident_geo_code`; retain source type and nested scope. |
| `vertexSchoolDistrictCode` | Optional[int] | Optional presence | integer / int32 | Vertex School District Code | Preserve separately: `provider_fields.isolved.vertex_school_district_code`; retain source type and nested scope. |
| `vertexWorkGeoCode` | Optional[str] | Optional presence | string | Vertex Work Geo Code | Preserve separately: `provider_fields.isolved.vertex_work_geo_code`; retain source type and nested scope. |
| `voucherNumber` | Optional[str] | Optional presence | string | Voucher Number | Preserve separately: `provider_fields.isolved.voucher_number`; retain source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedCheckAccrualModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.CheckAccrualModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Preserve record/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, existing null acceptance. |
| `accrualName` | Optional[str] | Optional presence | string | Accrual Name | Preserve separately: `provider_fields.isolved.accrual_name`; retain source type and nested scope. |
| `amountAccrued` | Optional[float] | Optional presence | number / double | Amount Accrued | Preserve separately: `provider_fields.isolved.amount_accrued` (Optional[float]); number helper, no inferred basis/scale. |
| `amountTaken` | Optional[float] | Optional presence | number / double | Amount Taken | Preserve separately: `provider_fields.isolved.amount_taken` (Optional[float]); number helper, no inferred basis/scale. |
| `availableBalance` | Optional[float] | Optional presence | number / double | Available Balance | Preserve separately: `provider_fields.isolved.available_balance` (Optional[float]); number helper, no inferred basis/scale. |
| `endingBalance` | Optional[float] | Optional presence | number / double | Ending Balance | Preserve separately: `provider_fields.isolved.ending_balance` (Optional[float]); number helper, no inferred basis/scale. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedBaseLinkModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.Base.LinkModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `href` | Optional[str] | Optional presence | string | Hyperlink to linked entity or action | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |
| `method` | Optional[str] | Optional presence | string | HTTP Method for linked entity or action | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |
| `rel` | Optional[str] | Optional presence | string | Relationship or purpose of link to enclosing entity | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedCheckBenefitTypeAccumulationModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.CheckBenefitTypeAccumulationModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `benefitDescription` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.benefit_description`; retain source type and nested scope. |
| `benefitTitle` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.benefit_title`; retain source type and nested scope. |
| `checkEligibleWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.check_eligible_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `checkEmployeeCatchUp` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.check_employee_catch_up` (Optional[float]); number helper, no inferred basis/scale. |
| `checkEmployeeDeduction` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.check_employee_deduction` (Optional[float]); number helper, no inferred basis/scale. |
| `checkEmployerContribution` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.check_employer_contribution` (Optional[float]); number helper, no inferred basis/scale. |
| `checkMatchEligibleWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.check_match_eligible_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `currentEligibleWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.current_eligible_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `currentEmployeeCatchUp` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.current_employee_catch_up` (Optional[float]); number helper, no inferred basis/scale. |
| `currentEmployeeDeduction` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.current_employee_deduction` (Optional[float]); number helper, no inferred basis/scale. |
| `currentEmployerContribution` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.current_employer_contribution` (Optional[float]); number helper, no inferred basis/scale. |
| `currentMatchEligibleWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.current_match_eligible_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `ftdEligibleWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ftd_eligible_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `ftdEmployeeCatchUp` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ftd_employee_catch_up` (Optional[float]); number helper, no inferred basis/scale. |
| `ftdEmployeeDeduction` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ftd_employee_deduction` (Optional[float]); number helper, no inferred basis/scale. |
| `ftdEmployerContribution` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ftd_employer_contribution` (Optional[float]); number helper, no inferred basis/scale. |
| `ftdMatchEligibleWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ftd_match_eligible_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `mtdEligibleWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.mtd_eligible_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `mtdEmployeeCatchUp` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.mtd_employee_catch_up` (Optional[float]); number helper, no inferred basis/scale. |
| `mtdEmployeeDeduction` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.mtd_employee_deduction` (Optional[float]); number helper, no inferred basis/scale. |
| `mtdEmployerContribution` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.mtd_employer_contribution` (Optional[float]); number helper, no inferred basis/scale. |
| `mtdMatchEligibleWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.mtd_match_eligible_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `ptdEligibleWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ptd_eligible_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `ptdEmployeeCatchUp` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ptd_employee_catch_up` (Optional[float]); number helper, no inferred basis/scale. |
| `ptdEmployeeDeduction` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ptd_employee_deduction` (Optional[float]); number helper, no inferred basis/scale. |
| `ptdEmployerContribution` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ptd_employer_contribution` (Optional[float]); number helper, no inferred basis/scale. |
| `ptdMatchEligibleWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ptd_match_eligible_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `qtdEligibleWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.qtd_eligible_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `qtdEmployeeCatchUp` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.qtd_employee_catch_up` (Optional[float]); number helper, no inferred basis/scale. |
| `qtdEmployeeDeduction` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.qtd_employee_deduction` (Optional[float]); number helper, no inferred basis/scale. |
| `qtdEmployerContribution` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.qtd_employer_contribution` (Optional[float]); number helper, no inferred basis/scale. |
| `qtdMatchEligibleWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.qtd_match_eligible_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `ytdEligibleWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ytd_eligible_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `ytdEmployeeCatchUp` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ytd_employee_catch_up` (Optional[float]); number helper, no inferred basis/scale. |
| `ytdEmployeeDeduction` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ytd_employee_deduction` (Optional[float]); number helper, no inferred basis/scale. |
| `ytdEmployerContribution` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ytd_employer_contribution` (Optional[float]); number helper, no inferred basis/scale. |
| `ytdMatchEligibleWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ytd_match_eligible_wages` (Optional[float]); number helper, no inferred basis/scale. |

#### IsolvedCheckAccumulationModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.CheckAccumulationModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Preserve record/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, existing null acceptance. |
| `checkDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.check_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `currentDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.current_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `ftdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ftd_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `itemCode` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.item_code`; retain source type and nested scope. |
| `itemDescription` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.item_description`; retain source type and nested scope. |
| `mtdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.mtd_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `ptdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ptd_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `qtdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.qtd_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `sequence` | Optional[int] | Optional presence | integer / int32 | No property description supplied. | Preserve separately: `provider_fields.isolved.sequence`; retain source type and nested scope. |
| `ytdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ytd_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedCheckDirectDepositAccumulationModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.CheckDirectDepositAccumulationModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Preserve record/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, existing null acceptance. |
| `account` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.account`; retain source type and nested scope. |
| `depositAmount` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.deposit_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `itemDescription` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.item_description`; retain source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedCheckEarningAccumulationModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.CheckEarningAccumulationModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Preserve record/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, existing null acceptance. |
| `checkDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.check_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `checkHours` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.check_hours` (Optional[float]); number helper, no inferred basis/scale. |
| `checkUnits` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.check_units` (Optional[float]); number helper, no inferred basis/scale. |
| `currentDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.current_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `currentHours` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.current_hours` (Optional[float]); number helper, no inferred basis/scale. |
| `currentUnits` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.current_units` (Optional[float]); number helper, no inferred basis/scale. |
| `ftdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ftd_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `ftdHours` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ftd_hours` (Optional[float]); number helper, no inferred basis/scale. |
| `ftdUnits` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ftd_units` (Optional[float]); number helper, no inferred basis/scale. |
| `isMemoEarning` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.isolved.is_memo_earning`; retain source type and nested scope. |
| `itemCode` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.item_code`; retain source type and nested scope. |
| `itemDescription` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.item_description`; retain source type and nested scope. |
| `labors` | Optional[List[IsolvedEarningAccumulationLaborDetailModel]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.isolved.labors`; retain source type and nested scope. |
| `mtdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.mtd_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `mtdHours` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.mtd_hours` (Optional[float]); number helper, no inferred basis/scale. |
| `mtdUnits` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.mtd_units` (Optional[float]); number helper, no inferred basis/scale. |
| `ptdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ptd_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `ptdHours` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ptd_hours` (Optional[float]); number helper, no inferred basis/scale. |
| `ptdUnits` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ptd_units` (Optional[float]); number helper, no inferred basis/scale. |
| `qtdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.qtd_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `qtdHours` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.qtd_hours` (Optional[float]); number helper, no inferred basis/scale. |
| `qtdUnits` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.qtd_units` (Optional[float]); number helper, no inferred basis/scale. |
| `sequence` | Optional[int] | Optional presence | integer / int32 | No property description supplied. | Preserve separately: `provider_fields.isolved.sequence`; retain source type and nested scope. |
| `ytdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ytd_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `ytdHours` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ytd_hours` (Optional[float]); number helper, no inferred basis/scale. |
| `ytdUnits` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ytd_units` (Optional[float]); number helper, no inferred basis/scale. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedEarningAccumulationLaborDetailModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.EarningAccumulationLaborDetailModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `dollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `hours` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.hours` (Optional[float]); number helper, no inferred basis/scale. |
| `laborCode` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.labor_code`; retain source type and nested scope. |
| `labors` | Optional[List[IsolvedEarningAccumulationLaborDetailModel_LaborFieldDetail]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.isolved.labors`; retain source type and nested scope. |
| `rate` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.rate` (Optional[float]); number helper, no inferred basis/scale. |

#### IsolvedEarningAccumulationLaborDetailModel_LaborFieldDetail

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.EarningAccumulationLaborDetailModel_LaborFieldDetail).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `laborId` | Optional[int] | Optional presence | integer / int32 | No property description supplied. | Preserve record/reference scope: `provider_fields.isolved.labor_id` (Optional[str]); identifier helper, existing null acceptance. |
| `laborTitle` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.labor_title`; retain source type and nested scope. |
| `laborValue` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.labor_value`; retain source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | No property description supplied. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |
| `organizationId` | Optional[int] | Optional presence | integer / int32 | No property description supplied. | Preserve record/reference scope: `provider_fields.isolved.organization_id` (Optional[str]); identifier helper, existing null acceptance. |

#### IsolvedEmployeeOrganizationModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.EmployeeOrganizationModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique employee organization Id | Preserve record/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, existing null acceptance. |
| `displayOrder` | Optional[int] | Optional presence | integer / int32 | Client organization field display order | Preserve separately: `provider_fields.isolved.display_order`; retain source type and nested scope. |
| `organizationId` | Optional[int] | Optional presence | integer / int32 | Id of the client organization field. Can be used for creating and updating employee organizations | Preserve record/reference scope: `provider_fields.isolved.organization_id` (Optional[str]); identifier helper, existing null acceptance. |
| `title` | Optional[str] | Optional presence | string | Title of the client organization field. Can be used for creating and updating employee organizations | Preserve separately: `provider_fields.isolved.title`; retain source type and nested scope. |
| `value` | Optional[str] | Optional presence | string | Organization field value for the employee which matches the lookup code of the client organization field | Preserve separately: `provider_fields.isolved.value`; retain source type and nested scope. |
| `valueDescription` | Optional[str] | Optional presence | string | The description of the organization value specified for this employee | Preserve separately: `provider_fields.isolved.value_description`; retain source type and nested scope. |

#### IsolvedCheckTaxCategoryModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.CheckTaxCategoryModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[str] | Required presence | string | Unique Object Id | Preserve record/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, existing null acceptance. |
| `additionalAmount` | Optional[float] | Optional presence | number / double | Additional Amount | Preserve separately: `provider_fields.isolved.additional_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `additionalIncome` | Optional[float] | Optional presence | number / double | Additional Income | Preserve separately: `provider_fields.isolved.additional_income` (Optional[float]); number helper, no inferred basis/scale. |
| `additionalPercent` | Optional[float] | Optional presence | number / double | Additional Percent | Preserve separately: `provider_fields.isolved.additional_percent` (Optional[float]); number helper, no inferred basis/scale. |
| `alternateCalculation` | Optional[IsolvedSystemAlternateCalculationModel] | Optional presence | #/definitions/AOS.PayrollOffice.RestAPI.Models.SystemAlternateCalculationModel | Alternate Calculation | Preserve separately: `provider_fields.isolved.alternate_calculation`; retain source type and nested scope. |
| `city` | Optional[str] | Optional presence | string | City | Preserve separately: `provider_fields.isolved.city`; retain source type and nested scope. |
| `deductionExemption` | Optional[float] | Optional presence | number / double | Deduction Exemption | Preserve separately: `provider_fields.isolved.deduction_exemption` (Optional[float]); number helper, no inferred basis/scale. |
| `dependentExemption` | Optional[float] | Optional presence | number / double | Dependent Exemption | Preserve separately: `provider_fields.isolved.dependent_exemption` (Optional[float]); number helper, no inferred basis/scale. |
| `description` | Optional[str] | Optional presence | string | Tax Description | Preserve separately: `provider_fields.isolved.description`; retain source type and nested scope. |
| `exemptionAmount` | Optional[float] | Optional presence | number / double | Exemption Amount | Preserve separately: `provider_fields.isolved.exemption_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `filingStatus` | Optional[IsolvedSystemFilingStatusModel] | Optional presence | #/definitions/AOS.PayrollOffice.RestAPI.Models.SystemFilingStatusModel | Filing Status | Preserve separately: `provider_fields.isolved.filing_status`; retain source type and nested scope. |
| `isBlocked` | Optional[bool] | Optional presence | boolean | A flag that indicates this item is blocked | Preserve separately: `provider_fields.isolved.is_blocked`; retain source type and nested scope. |
| `isNonResident` | Optional[bool] | Optional presence | boolean | Is Non Resident | Preserve separately: `provider_fields.isolved.is_non_resident`; retain source type and nested scope. |
| `multipleJobs` | Optional[bool] | Optional presence | boolean | A flag that indicates multiple jobs | Preserve separately: `provider_fields.isolved.multiple_jobs`; retain source type and nested scope. |
| `primaryExemptions` | Optional[int] | Optional presence | integer / int32 | Primary Exemptions | Preserve separately: `provider_fields.isolved.primary_exemptions`; retain source type and nested scope. |
| `secondaryExemptions` | Optional[int] | Optional presence | integer / int32 | Secondary Exemptions | Preserve separately: `provider_fields.isolved.secondary_exemptions`; retain source type and nested scope. |
| `state` | Optional[IsolvedSystemStateModel] | Optional presence | #/definitions/AOS.PayrollOffice.RestAPI.Models.SystemStateModel | State | Preserve separately: `provider_fields.isolved.state`; retain source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedSystemAlternateCalculationModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.SystemAlternateCalculationModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[str] | Required presence | string | Unique Object Id | Preserve record/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, existing null acceptance. |
| `description` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.description`; retain source type and nested scope. |
| `state` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.state`; retain source type and nested scope. |
| `taxCategoryCode` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.tax_category_code`; retain source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedSystemFilingStatusModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.SystemFilingStatusModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[str] | Required presence | string | Unique Object Id | Preserve record/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, existing null acceptance. |
| `description` | Optional[str] | Optional presence | string | Civil Status | Preserve separately: `provider_fields.isolved.description`; retain source type and nested scope. |
| `state` | Optional[str] | Optional presence | string | State from US | Preserve separately: `provider_fields.isolved.state`; retain source type and nested scope. |
| `taxCategory` | Optional[str] | Optional presence | string | Tax Category | Preserve separately: `provider_fields.isolved.tax_category`; retain source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedSystemStateModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.SystemStateModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[str] | Required presence | string | No property description supplied. | Preserve record/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, existing null acceptance. |
| `stateName` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.state_name`; retain source type and nested scope. |

#### IsolvedCheckTaxAccumulationModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.CheckTaxAccumulationModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Preserve record/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, existing null acceptance. |
| `checkDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.check_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `checkTaxableWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.check_taxable_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `currentDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.current_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `currentTaxableWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.current_taxable_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `ftdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ftd_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `ftdTaxableWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ftd_taxable_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `isEmployeeTax` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.isolved.is_employee_tax`; retain source type and nested scope. |
| `itemCode` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.item_code`; retain source type and nested scope. |
| `itemDescription` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.item_description`; retain source type and nested scope. |
| `mtdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.mtd_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `mtdTaxableWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.mtd_taxable_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `ptdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ptd_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `ptdTaxableWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ptd_taxable_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `qtdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.qtd_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `qtdTaxableWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.qtd_taxable_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `sequence` | Optional[int] | Optional presence | integer / int32 | No property description supplied. | Preserve separately: `provider_fields.isolved.sequence`; retain source type and nested scope. |
| `ytdDollars` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ytd_dollars` (Optional[float]); number helper, no inferred basis/scale. |
| `ytdTaxableWages` | Optional[float] | Optional presence | number / double | No property description supplied. | Preserve separately: `provider_fields.isolved.ytd_taxable_wages` (Optional[float]); number helper, no inferred basis/scale. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedPayrollRunHistoryResponse

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · Project input/container; no independent provider schema.

Input shape: `RootModel[List[IsolvedPayrollRunHistoryModel]]`. No additional declared fields.

#### IsolvedPagedModelItemListOfCheckModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.PagedModelItemListOfCheckModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `nextPageUrl` | Optional[str] | Optional presence | string | A hyperlink to request the next page of result data, if applicable | Metadata: `source_metadata.isolved.response`; retain paging without fetching pages. |
| `previousPageUrl` | Optional[str] | Optional presence | string | A hyperlink to request the previous page of result data, if applicable | Metadata: `source_metadata.isolved.response`; retain paging without fetching pages. |
| `results` | Optional[List[IsolvedCheckModel]] | Optional presence | array | A listing of results for the currently requested page of data | Container: validate/map this supplied record family separately; preserve scope and originals. |
| `totalItems` | Optional[int] | Optional presence | integer / int32 | The total number of items being returned in this result | Metadata: `source_metadata.isolved.response`; retain paging without fetching pages. |
| `totalPages` | Optional[float] | Optional presence | number / double | The total number of pages of result data | Metadata: `source_metadata.isolved.response`; retain paging without fetching pages. |

### ukg_ready

#### UKGReadyPayrollRunResponse

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/358/schema).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `payrolls` | List[UKGReadyPayrollRunResponsePayrollsItem] | Required presence | array | No property description supplied. | Container: validate/map this supplied record family separately; preserve scope and originals. |

#### UKGReadyPayrollRunResponsePayrollsItem

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/358/schema/properties/payrolls/items).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Shared: `payroll_run_id`. Use the agreed helper; preserve converted source originals/issues. |
| `name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.name`; retain source type and nested scope. |
| `start_date` | Optional[str] | Optional presence | string | Date needs to be in the format yyyy-mm-dd within the 1900-12-31 and 2079-06-05 date range | Preserve separately: `provider_fields.ukg-ready.start_date` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `end_date` | Optional[str] | Optional presence | string | Date needs to be in the format yyyy-mm-dd within the 1900-12-31 and 2079-06-05 date range | Preserve separately: `provider_fields.ukg-ready.end_date` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `pay_date` | Optional[str] | Optional presence | string | Date needs to be in the format yyyy-mm-dd within the 1900-12-31 and 2079-06-05 date range | Candidate shared: `payroll_run_pay_date`. Use the agreed helper; preserve converted source originals/issues. Keep missing semantic descriptions explicit. |
| `type` | Optional[UKGReadyPayrollRunResponsePayrollsItemType] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.type`; retain source type and nested scope. |
| `status` | Optional[str] | Optional presence | string | No property description supplied. Documented enum: ["NEW", "OPEN", "OPEN_FAILED", "CLOSE_FAILED", "CLOSED", "SUBMITTED", "ROLLBACK_FAILED", "FINALIZE_FAILED", "FINALIZED"]. | Preserve separately: `provider_fields.ukg-ready.status`; retain source type and nested scope. |
| `ein` | Optional[UKGReadyPayrollRunResponsePayrollsItemEin] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.ein`; retain source type and nested scope. |
| `billable` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.billable`; retain source type and nested scope. |
| `direct_deposit_date` | Optional[str] | Optional presence | string | Date needs to be in the format yyyy-mm-dd within the 1900-12-31 and 2079-06-05 date range | Preserve separately: `provider_fields.ukg-ready.direct_deposit_date` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `sch_submit_date_time` | Optional[str] | Optional presence | string | Date needs to be in the format yyyy-mm-dd within the 1900-12-31 and 2079-06-05 date range | Preserve separately: `provider_fields.ukg-ready.sch_submit_date_time`; retain source type and nested scope. |
| `invoice_generator_id` | Optional[int] | Optional presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.invoice_generator_id` (Optional[str]); identifier helper, existing null acceptance. |
| `adjustment_grab_YTD_from_payroll_id` | Optional[int] | Optional presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.adjustment_grab_ytd_from_payroll_id` (Optional[str]); identifier helper, existing null acceptance. |
| `dflt_pay_statement_type_id` | Optional[int] | Optional presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.dflt_pay_statement_type_id` (Optional[str]); identifier helper, existing null acceptance. |
| `dflt_pay_stub_note` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.dflt_pay_stub_note`; retain source type and nested scope. |
| `_links` | Optional[UKGReadyPayrollRunResponsePayrollsItemLinks] | Optional presence | object | No property description supplied. | Preserve source nesting: `provider_fields.ukg-ready.unmapped` (record links). |

#### UKGReadyPayrollRunResponsePayrollsItemType

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/358/schema/properties/payrolls/items/properties/type).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.id` (str); identifier helper, existing null acceptance. |
| `display_name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.display_name`; retain source type and nested scope. |

#### UKGReadyPayrollRunResponsePayrollsItemEin

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/358/schema/properties/payrolls/items/properties/ein).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.id` (str); identifier helper, existing null acceptance. |
| `ein_name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.ein_name`; retain source type and nested scope. |
| `ein_tax_id` | Optional[str] | Optional presence | string | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.ein_tax_id` (Optional[str]); identifier helper, existing null acceptance. |
| `ein_country_id` | Optional[str] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Preserve record/reference scope: `provider_fields.ukg-ready.ein_country_id` (Optional[str]); identifier helper, existing null acceptance. |

#### UKGReadyPayrollRunResponsePayrollsItemLinks

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/358/schema/properties/payrolls/items/properties/_links).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `self` | Optional[str] | Optional presence | string | No property description supplied. | Preserve source nesting: `provider_fields.ukg-ready.unmapped` (record links). |

#### UKGReadyPaycheckListResponse

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/362/schema).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `pay_statements` | List[UKGReadyPaycheckListResponsePayStatementsItem] | Required presence | array | No property description supplied. | Container: validate/map this supplied record family separately; preserve scope and originals. |

#### UKGReadyPaycheckListResponsePayStatementsItem

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/362/schema/properties/pay_statements/items).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `employee` | Optional[UKGReadyPaycheckListResponsePayStatementsItemEmployee] | Optional presence | Not supplied at this path | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.employee`; retain source type and nested scope. |
| `id` | int | Required presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.id` (str); identifier helper, existing null acceptance. |
| `pay_date` | Optional[str] | Optional presence | string | Date needs to be in the format yyyy-mm-dd within the 1900-12-31 and 2079-06-05 date range | Preserve separately: `provider_fields.ukg-ready.pay_date` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `status` | Optional[str] | Optional presence | string | No property description supplied. Documented enum: ["INVALID", "NEW", "OPEN", "CLOSED", "FINALIZED"]. | Preserve separately: `provider_fields.ukg-ready.status`; retain source type and nested scope. |
| `type` | Optional[UKGReadyPaycheckListResponsePayStatementsItemType] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.type`; retain source type and nested scope. |
| `pay_period_start` | Optional[str] | Optional presence | string | Date needs to be in the format yyyy-mm-dd within the 1900-12-31 and 2079-06-05 date range | Preserve separately: `provider_fields.ukg-ready.pay_period_start` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `pay_period_end` | Optional[str] | Optional presence | string | Date needs to be in the format yyyy-mm-dd within the 1900-12-31 and 2079-06-05 date range | Preserve separately: `provider_fields.ukg-ready.pay_period_end` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `_links` | Optional[UKGReadyPaycheckListResponsePayStatementsItemLinks] | Optional presence | object | No property description supplied. | Preserve source nesting: `provider_fields.ukg-ready.unmapped` (record links). |

#### UKGReadyPaycheckListResponsePayStatementsItemEmployee

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/362/schema/properties/pay_statements/items/properties/employee).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `account_id` | Optional[float] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Preserve record/reference scope: `provider_fields.ukg-ready.account_id` (Optional[str]); identifier helper, existing null acceptance. |

#### UKGReadyPaycheckListResponsePayStatementsItemType

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/362/schema/properties/pay_statements/items/properties/type).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.id` (str); identifier helper, existing null acceptance. |
| `display_name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.display_name`; retain source type and nested scope. |

#### UKGReadyPaycheckListResponsePayStatementsItemLinks

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/362/schema/properties/pay_statements/items/properties/_links).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `self` | Optional[str] | Optional presence | string | No property description supplied. | Preserve source nesting: `provider_fields.ukg-ready.unmapped` (record links). |

#### UKGReadyPaycheckDetails

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `employee` | Optional[UKGReadyPaycheckDetailsEmployee] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.employee`; retain source type and nested scope. |
| `id` | Optional[int] | Required presence | integer | No property description supplied. | Shared: `paycheck_id`. Use the agreed helper; preserve converted source originals/issues. |
| `pay_date` | Optional[str] | Optional presence | string | No property description supplied. | Candidate shared: `pay_date`. Use the agreed helper; preserve converted source originals/issues. Keep missing semantic descriptions explicit. |
| `status` | Optional[str] | Optional presence | string | No property description supplied. Documented enum: ["INVALID", "NEW", "OPEN", "CLOSED", "FINALIZED"]. | Preserve separately: `provider_fields.ukg-ready.status`; retain source type and nested scope. |
| `type` | Optional[UKGReadyPaycheckDetailsType] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.type`; retain source type and nested scope. |
| `pay_period_start` | Optional[str] | Optional presence | string | Date needs to be in the format yyyy-mm-dd within the 1900-12-31 and 2079-06-05 date range | Candidate shared: `period_start_date`. Use the agreed helper; preserve converted source originals/issues. Keep missing semantic descriptions explicit. |
| `pay_period_end` | Optional[str] | Optional presence | string | Date needs to be in the format yyyy-mm-dd within the 1900-12-31 and 2079-06-05 date range | Candidate shared: `period_end_date`. Use the agreed helper; preserve converted source originals/issues. Keep missing semantic descriptions explicit. |
| `earnings` | Optional[List[UKGReadyPaycheckDetailsEarningsItem]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.earnings`; retain source type and nested scope. |
| `deductions` | Optional[List[UKGReadyPaycheckDetailsDeductionsItem]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.deductions`; retain source type and nested scope. |
| `taxes` | Optional[List[UKGReadyPaycheckDetailsTaxesItem]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.taxes`; retain source type and nested scope. |
| `messages` | Optional[List[UKGReadyPaycheckDetailsMessagesItem]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.messages`; retain source type and nested scope. |
| `payments` | Optional[List[UKGReadyPaycheckDetailsPaymentsItem]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.payments`; retain source type and nested scope. |

#### UKGReadyPaycheckDetailsEmployee

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/employee).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `account_id` | Optional[float] | Optional presence | number / long | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.account_id` (Optional[str]); identifier helper, existing null acceptance. |

#### UKGReadyPaycheckDetailsType

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/type).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.id` (str); identifier helper, existing null acceptance. |
| `display_name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.display_name`; retain source type and nested scope. |

#### UKGReadyPaycheckDetailsEarningsItem

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/earnings/items).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.id` (Optional[str]); identifier helper, existing null acceptance. |
| `type_name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.type_name`; retain source type and nested scope. |
| `batch` | Optional[UKGReadyPaycheckDetailsEarningsItemBatch] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.batch`; retain source type and nested scope. |
| `date_range_from` | Optional[str] | Optional presence | string | Date needs to be in the format yyyy-mm-dd within the 1900-12-31 and 2079-06-05 date range | Preserve separately: `provider_fields.ukg-ready.date_range_from` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `date_range_to` | Optional[str] | Optional presence | string | Date needs to be in the format yyyy-mm-dd within the 1900-12-31 and 2079-06-05 date range | Preserve separately: `provider_fields.ukg-ready.date_range_to` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `hours` | Optional[int] | Optional presence | integer | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.hours`; retain source type and nested scope. |
| `base_rate` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.base_rate` (Optional[float]); number helper, no inferred basis/scale. |
| `quantity` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.quantity` (Optional[float]); number helper, no inferred basis/scale. |
| `ee_amount` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.ee_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `workers_comp_code` | Optional[UKGReadyPaycheckDetailsEarningsItemWorkersCompCode] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.workers_comp_code`; retain source type and nested scope. |
| `shift` | Optional[UKGReadyPaycheckDetailsEarningsItemShift] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.shift`; retain source type and nested scope. |
| `cost_centers` | Optional[List[UKGReadyPaycheckDetailsEarningsItemCostCentersItem]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.cost_centers`; retain source type and nested scope. |
| `earning` | Optional[UKGReadyPaycheckDetailsEarningsItemEarning] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.earning`; retain source type and nested scope. |

#### UKGReadyPaycheckDetailsEarningsItemBatch

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/earnings/items/properties/batch).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.id` (str); identifier helper, existing null acceptance. |
| `display_name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.display_name`; retain source type and nested scope. |

#### UKGReadyPaycheckDetailsEarningsItemWorkersCompCode

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/earnings/items/properties/workers_comp_code).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `external_id` | Optional[str] | Optional presence | string | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.external_id` (Optional[str]); identifier helper, existing null acceptance. |

#### UKGReadyPaycheckDetailsEarningsItemShift

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/earnings/items/properties/shift).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.id` (str); identifier helper, existing null acceptance. |
| `name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.name`; retain source type and nested scope. |

#### UKGReadyPaycheckDetailsEarningsItemCostCentersItem

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/earnings/items/properties/cost_centers/items).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `index` | Optional[int] | Optional presence | integer | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.index`; retain source type and nested scope. |
| `value` | Optional[UKGReadyPaycheckDetailsEarningsItemCostCentersItemValue] | Optional presence | ['object', 'null'] | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.value`; retain source type and nested scope. |

#### UKGReadyPaycheckDetailsEarningsItemCostCentersItemValue

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/earnings/items/properties/cost_centers/items/properties/value).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.id` (str); identifier helper, existing null acceptance. |

#### UKGReadyPaycheckDetailsEarningsItemEarning

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/earnings/items/properties/earning).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.name`; retain source type and nested scope. |
| `external_id` | Optional[str] | Optional presence | string | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.external_id` (Optional[str]); identifier helper, existing null acceptance. |
| `code` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.code`; retain source type and nested scope. |

#### UKGReadyPaycheckDetailsDeductionsItem

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/deductions/items).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.id` (Optional[str]); identifier helper, existing null acceptance. |
| `type_name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.type_name`; retain source type and nested scope. |
| `batch` | Optional[UKGReadyPaycheckDetailsDeductionsItemBatch] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.batch`; retain source type and nested scope. |
| `date_range_from` | Optional[str] | Optional presence | string | Date needs to be in the format yyyy-mm-dd within the 1900-12-31 and 2079-06-05 date range | Preserve separately: `provider_fields.ukg-ready.date_range_from` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `date_range_to` | Optional[str] | Optional presence | string | Date needs to be in the format yyyy-mm-dd within the 1900-12-31 and 2079-06-05 date range | Preserve separately: `provider_fields.ukg-ready.date_range_to` (Optional[date]); date helper, retain source text/issues; no inferred calendar restrictions. |
| `quantity` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.quantity` (Optional[float]); number helper, no inferred basis/scale. |
| `base_rate` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.base_rate` (Optional[float]); number helper, no inferred basis/scale. |
| `ee_amount` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.ee_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `er_amount` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.er_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `vendor` | Optional[UKGReadyPaycheckDetailsDeductionsItemVendor] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.vendor`; retain source type and nested scope. |
| `cost_centers` | Optional[List[UKGReadyPaycheckDetailsDeductionsItemCostCentersItem]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.cost_centers`; retain source type and nested scope. |
| `workers_comp_code` | Optional[UKGReadyPaycheckDetailsDeductionsItemWorkersCompCode] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.workers_comp_code`; retain source type and nested scope. |
| `deduction` | Optional[UKGReadyPaycheckDetailsDeductionsItemDeduction] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.deduction`; retain source type and nested scope. |

#### UKGReadyPaycheckDetailsDeductionsItemBatch

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/deductions/items/properties/batch).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.id` (str); identifier helper, existing null acceptance. |
| `display_name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.display_name`; retain source type and nested scope. |

#### UKGReadyPaycheckDetailsDeductionsItemVendor

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/deductions/items/properties/vendor).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.id` (Optional[str]); identifier helper, existing null acceptance. |
| `name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.name`; retain source type and nested scope. |

#### UKGReadyPaycheckDetailsDeductionsItemCostCentersItem

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/deductions/items/properties/cost_centers/items).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `index` | Optional[int] | Optional presence | integer | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.index`; retain source type and nested scope. |
| `value` | Optional[UKGReadyPaycheckDetailsDeductionsItemCostCentersItemValue] | Optional presence | ['object', 'null'] | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.value`; retain source type and nested scope. |

#### UKGReadyPaycheckDetailsDeductionsItemCostCentersItemValue

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/deductions/items/properties/cost_centers/items/properties/value).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.id` (str); identifier helper, existing null acceptance. |

#### UKGReadyPaycheckDetailsDeductionsItemWorkersCompCode

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/deductions/items/properties/workers_comp_code).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `external_id` | Optional[str] | Optional presence | string | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.external_id` (Optional[str]); identifier helper, existing null acceptance. |

#### UKGReadyPaycheckDetailsDeductionsItemDeduction

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/deductions/items/properties/deduction).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.name`; retain source type and nested scope. |
| `external_id` | Optional[str] | Optional presence | string | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.external_id` (Optional[str]); identifier helper, existing null acceptance. |
| `code` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.code`; retain source type and nested scope. |

#### UKGReadyPaycheckDetailsTaxesItem

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/taxes/items).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.id` (Optional[str]); identifier helper, existing null acceptance. |
| `type_name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.type_name`; retain source type and nested scope. |
| `batch` | Optional[UKGReadyPaycheckDetailsTaxesItemBatch] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.batch`; retain source type and nested scope. |
| `ee_amount` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.ee_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `er_amount` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.er_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `ee_gross_wage` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.ee_gross_wage` (Optional[float]); number helper, no inferred basis/scale. |
| `ee_subject_wage` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.ee_subject_wage` (Optional[float]); number helper, no inferred basis/scale. |
| `ee_gross_subject_wage` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.ee_gross_subject_wage` (Optional[float]); number helper, no inferred basis/scale. |
| `er_gross_wage` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.er_gross_wage` (Optional[float]); number helper, no inferred basis/scale. |
| `er_subject_wage` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.er_subject_wage` (Optional[float]); number helper, no inferred basis/scale. |
| `er_gross_subject_wage` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.er_gross_subject_wage` (Optional[float]); number helper, no inferred basis/scale. |
| `company_tax` | Optional[UKGReadyPaycheckDetailsTaxesItemCompanyTax] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.company_tax`; retain source type and nested scope. |

#### UKGReadyPaycheckDetailsTaxesItemBatch

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/taxes/items/properties/batch).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.id` (str); identifier helper, existing null acceptance. |
| `display_name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.display_name`; retain source type and nested scope. |

#### UKGReadyPaycheckDetailsTaxesItemCompanyTax

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/taxes/items/properties/company_tax).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `code` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.code`; retain source type and nested scope. |
| `name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.name`; retain source type and nested scope. |
| `abbrev` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.abbrev`; retain source type and nested scope. |

#### UKGReadyPaycheckDetailsMessagesItem

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/messages/items).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.id` (Optional[str]); identifier helper, existing null acceptance. |
| `type_name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.type_name`; retain source type and nested scope. |
| `message` | Optional[UKGReadyPaycheckDetailsMessagesItemMessage] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.message`; retain source type and nested scope. |
| `batch` | Optional[UKGReadyPaycheckDetailsMessagesItemBatch] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.batch`; retain source type and nested scope. |

#### UKGReadyPaycheckDetailsMessagesItemMessage

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/messages/items/properties/message).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `text` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.text`; retain source type and nested scope. |
| `severity` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.severity`; retain source type and nested scope. |

#### UKGReadyPaycheckDetailsMessagesItemBatch

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/messages/items/properties/batch).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.id` (str); identifier helper, existing null acceptance. |
| `display_name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.display_name`; retain source type and nested scope. |

#### UKGReadyPaycheckDetailsPaymentsItem

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/payments/items).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.id` (Optional[str]); identifier helper, existing null acceptance. |
| `hours` | Optional[int] | Optional presence | integer | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.hours`; retain source type and nested scope. |
| `quantity` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.quantity` (Optional[float]); number helper, no inferred basis/scale. |
| `ee_amount` | Optional[float] | Optional presence | number | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.ee_amount` (Optional[float]); number helper, no inferred basis/scale. |
| `type_name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.type_name`; retain source type and nested scope. |
| `batch` | Optional[UKGReadyPaycheckDetailsPaymentsItemBatch] | Optional presence | object | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.batch`; retain source type and nested scope. |

#### UKGReadyPaycheckDetailsPaymentsItemBatch

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/364/schema/properties/payments/items/properties/batch).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__payrolls__%28id%29__pay-statements__%28id%29.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Preserve record/reference scope: `provider_fields.ukg-ready.id` (str); identifier helper, existing null acceptance. |
| `display_name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.display_name`; retain source type and nested scope. |

#### UKGReadyPayrollInput

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_payroll_run.py) · Project input/container; no independent provider schema.

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `payroll_runs` | Optional[UKGReadyPayrollRunResponse] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Container: validate/map this supplied record family separately; preserve scope and originals. |
| `paycheck_list` | Optional[UKGReadyPaycheckListResponse] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Container: validate/map this supplied record family separately; preserve scope and originals. |
| `paychecks` | Optional[List[UKGReadyPaycheckDetails]] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Container: validate/map this supplied record family separately; preserve scope and originals. |

## Code and lookup review

Only exact source-field meanings are eligible for label conversion. Unknown values stay preserved with the existing conversion issue policy. Do not interpret a status as a failure merely because it contains FAILED, INVALID or VOID: these are payroll business states, not wrapper errors.

| Exact field / evidence | Verified values | Handling |
|---|---|---|
| Prism BatchList.batchType, property description | R → regular; M → manual; S → special; V → void | Descriptive provider batch_type; keep separate from other provider type domains. |
| Prism BatchList.batchStatus | Description says processing status; no value dictionary. | Preserve raw batch_status; do not borrow PayrollHistory.type. |
| UKG run status, schema 358/payrolls[]/status | NEW, OPEN, OPEN_FAILED, CLOSE_FAILED, CLOSED, SUBMITTED, ROLLBACK_FAILED, FINALIZE_FAILED, FINALIZED | Preserve documented tokens in run scope; no cross-provider status equivalence. |
| UKG paycheck list/detail status, schemas 362 and 364 | INVALID, NEW, OPEN, CLOSED, FINALIZED | Preserve paycheck status separately from run status. |
| UKG run/check type | Object with id and display_name | String identifier plus original display name; no universal type meaning inferred. |
| isolved status/payrollRunType/checkTypeDescription | String descriptions; no closed dictionary in these models/lookups. | Preserve field meaning and text; no invented codes or classifications. |

The Prism lookup domains payroll_history_type (PayrollHistory.type) and hours_worked_basis / hours_worked_position_basis (HoursWorkedByHours.hrsType / HoursWorkedByPosition.hrsType) apply to other schema fields, not BatchList.batchType or paycheck hours. They are not a crosswalk here. isolved scheduling, validation-severity and timecard lookup domains, and UKG employee pay-info payroll_classification, are unrelated to the selected payroll fields and have been removed from the applicability table.

Field-specific enum arrays and descriptions remain in the full inventory. The UKG lookup run-status pointer references detail schema 360; run-list schema 358 independently contains the same enum values. The paycheck-status lookup points to schema 364, and schema 362 independently lists the same values.

## Saved Postman evidence

Request names and saved response structure only are shown below. No personal/account values or credentials are copied. A request with no saved JSON response provides no live response proof. Samples supplement the contract; they do not define every accepted input shape.

| Request | Saved JSON response evidence |
|---|---|
| prismHR - payrollRuns chosen | 200 object; keys: batchList, errorCode, errorMessage, extension |
| prismHR - paychecks chosen | 200 object; keys: count, errorCode, errorMessage, extension, payrollVoucher, startpage, total |
| isol - payrollRuns chosen | No saved JSON response. |
| isol - paychecks chosen | No saved JSON response. |
| ukg - payrollRuns chosen | 200 object; keys: payrolls |
| ukg - paychecks chosen | 200 object; keys: pay_statements |

## References and verification

- [Original comparison](./payroll.md) (unchanged; disagreements should be resolved using the contract evidence above).
- [Decisions](../DECISIONS.md) and [README](../../../README.md).
- [PrismHR OpenAPI](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json), [isolved Swagger](../../../contracts/isolved/openapi/isolved-v6.swagger.json), [UKG schemas](../../../contracts/ukg-ready/reference-schemas.json).
- Lookup references: [PrismHR](../../../contracts/prismhr/lookup-reference.json), [isolved](../../../contracts/isolved/lookup-reference.json), [UKG Ready](../../../contracts/ukg-ready/lookup-reference.json).

Declared source-field coverage (reused classes counted once per provider): prismhr 229, isolved 239, ukg_ready 136.

Fields with absent/vague-by-absence property descriptions or undocumented source additions: prismhr 37, isolved 116, ukg_ready 122. Every such field is explicitly marked; a source name is not treated as a verified meaning. Coverage counts prove inventory inclusion, not business equivalence or live API completeness.

The three payroll decisions above are implemented; missing associations remain a deferred gap. Identifier/date/number helpers, requiredness and preservation policies are already settled. Test both run and paycheck families together, sparse/empty records, negative/zero amounts, unknown codes, extras, alias conflicts and overlapping collections. This review changes this proposal only; source models, canonical models, YAMLs and adapters are unchanged.

## Review update — start here

- Decided: common mapper architecture, string IDs, date/number helpers, source preservation and separate run/paycheck/component scopes.
- Confirmed: Prism checkNumber/checkNum share a meaning; conflicts must retain originals. Earning.payAmount is a rate, not total earnings.
- Corrected: unrelated lookups are excluded; lookup applicability is checked against exact fields.
- Samples: populated Prism runs/vouchers and UKG runs; UKG saved paycheck list is empty; isolved payroll/check requests have no saved JSON responses.
- Decided: separate output lists, preserve overlapping sections, and leave missing associations empty as a deferred gap. No implementation changed.

## Verified paycheck amount matches

| Canonical field | PrismHR evidence | isolved evidence | Handling |
|---|---|---|---|
| net_pay (Optional[float]) | PayrollVoucher.netPay: net pay amount from employee paycheck | CheckModel.netPay: Net Pay | Shared paycheck amount, no conversion of currency/basis. |
| check_amount (Optional[float]) | PayrollVoucher.checkAmt: paycheck amount | CheckModel.checkAmount: Check Amount | Shared check amount; not net pay or an individual deposit amount. |

Evidence: the linked PrismHR PayrollVoucher and isolved CheckModel contracts in the inventory. Prism individual ACH amounts are not automatically equivalent to an isolved deposit total. Preserve all unverified amounts separately under the universal policy.

## Implementation completed

- Shared `canonical_model_payroll.py` defines separate run/header/detail records and one payroll result container.
- Seven YAMLs: each provider has payroll_run/paycheck; UKG also has paycheck_header. Source-specific components remain nested under provider_fields; links use engine fallback and extras retain source paths.
- UKG dates and amounts lacking verified semantic matches stay provider-specific. Existing date helpers normalize documented date fields with originals/issues; raw status/type values remain distinct.
- Prism check-number aliases use identifier_alias. Conflicts preserve both originals, output null, and report an issue.
- Adapters validate before mapping, preserve overlapping inputs with section/index provenance, and do not infer missing ownership/run links, deduplicate or aggregate.
- Payroll returns a container even when empty. Missing references remain unset/null, never manufactured from sequences or request assumptions.
- CLI reference gaps now warn and survive in output source_metadata; packs and references.py remain unchanged.
- Fifteen real CLI fixture pairs cover all five entities/providers, including populated payroll examples.
- Verification: 279 tests and 3980 subtests passed. See [implementation details](../Payroll%20Mapper%20Implementation.md).
