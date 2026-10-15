# Company Canonical Mapping Proposal

Company canonical models, three YAMLs and adapter connections are implemented. Prism ClientMaster, isolved legal-company/client structures and UKG EIN lookup records represent different organizational levels. This proposal preserves those levels instead of asserting that their IDs mean the same thing.

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
| `source_record_id` (Optional[str]) | `PrismHRClientMaster.id` (str)<br>unique ID code for the client company | `IsolvedLegalModel.id` (Optional[int])<br>Unique Object Id | `UKGReadyEinsResponseItemsItem.id` (int)<br>No property description supplied; identifier of the EIN lookup item. | Preserve each source record ID with provider and proposed record type. This is not a universal company_id or proof that the three organizational levels are equivalent. |
| `legal_name` (Optional[str]) | `PrismHRClientMaster.legalName` (Optional[str])<br>legal business name for client | `IsolvedLegalModel.legalName` (Optional[str])<br>Legal name | No verified shared counterpart proposed. | Do not treat UKG EIN name as proven legal company name. |
| `trade_name` (Optional[str]) | `PrismHRClientMaster.clientName` (Optional[str])<br>doing-business-as client name | `IsolvedLegalModel.dbaName` (Optional[str])<br>DBA Name | No verified shared counterpart proposed. | Preserve documented DBA/trade-name distinction from legal name. |
| `federal_tax_id` (Optional[str]) | `PrismHRClientMaster.federalIdNumber` (Optional[str])<br>Federal Identification Number | `IsolvedLegalModel.federalEIN` (Optional[str])<br>Federal Employer Identification Number | `UKGReadyEinsResponseItemsItem.ein_tax_id` (Optional[str])<br>No property description supplied; preserve as ukg_ein_tax_id, not a confirmed federal_tax_id. | Prism/isolved describe federal identifiers. UKG remains separate until tax jurisdiction/meaning is verified; preserve country and scope. |
| `naics_code` (Optional[str]) | `PrismHRClientMaster.naicsCode` (Optional[str])<br>North American Industrial Classification System code | `IsolvedLegalModel.naicsCode` (Optional[str])<br>North American Industry Classification System Code | No verified shared counterpart proposed. | Preserve the code as text; no lookup label invention. |

Use `provider: Literal["prismhr", "isolved", "ukg-ready"]` on normalized records. The table distinguishes description-backed matches from candidates without descriptions; all remaining fields have an explicit preservation destination below. A shared field is a candidate semantic match, not a completed enum/unit translation.

## Additional comparison findings

- The older company comparison describes a minimal ID/name output and leaves other settings unmapped. This proposal inventories those settings so they can be preserved without promoting settings into shared business fields.
- UKG EIN lookup supplies an EIN record name/tax ID/currency. That does not prove a company-detail response or authorize deriving the API company ID from an EIN ID.
- Sign-in/request company context is outside these entity JSON schemas. A value available during an HTTP workflow is not automatically available to the offline CLI.
- Prism clientName is documented as DBA and legalName as legal business name. isolved dbaName can be null; do not fill it from legalName automatically.
- Preserve provider-specific tax registrations, addresses, payroll settings and code definitions as separate details. A tax ID is a string business identifier, not an integer or a generated company key.

## Decisions already settled

| Area | Decision | Basis |
|---|---|---|
| Architecture | Shared Pydantic output, provider YAML, common engine/helpers. | Existing employee/direct-deposit/deduction/payroll approach. |
| Identifiers | String record/reference IDs, preserving leading zeros and source scope. Never derive company_id from EIN/client/legal ID. | Existing identity policy; different organizational levels. |
| Requiredness | Keep source record IDs and documented required wrappers; other fields optional, existing null acceptance unchanged. | Existing validation policy. |
| Names | Prism legalName / isolved legalName share legal_name; Prism clientName / isolved dbaName share trade_name. Keep display/parent/EIN names separate. | Explicit legal-name and DBA descriptions. No fallback from legal name to DBA. |
| NAICS | Prism naicsCode / isolved naicsCode share naics_code as text. | Both explicitly describe NAICS. No invented classification labels. |
| Federal identifier | Prism federalIdNumber / isolved federalEIN may share federal_tax_id as text. Keep record IDs and UKG tax values separate. | Explicit federal identification descriptions; no UKG jurisdiction crosswalk. |
| Dates/numbers | Reuse date/number helpers where meaning is verified; dates serialize YYYY-MM-DD, monetary/rate values are finite floats without unit/currency scaling. | Existing policy. Source strings with unclear numeric meaning remain preserved, not guessed. |
| Provider-specific settings | Preserve contact/address roles, payroll/tax/service settings, catalog definitions and unmatched fields with explicit snake_case names and nested boundaries. | No company setting becomes an employee assignment. |
| Unknown/links/metadata | Known unmapped fields and record links retain nesting; unknown extras retain nesting; wrappers remain source metadata. | Existing engine behavior. |
| Missing descriptions | Preserve unclear meanings/raw codes; no invented enum or cross-provider equivalence. | Existing preservation decision. |
| Status | Prism statusClass and status remain distinct; use documented class labels only on statusClass. Do not map employee or ACH states as company status. | Exact lookup applicability. |
| Recursive source references | Use finite explicit YAML paths; preserve the remaining supplied finite JSON nesting. Do not expand schema cycles or fetch related records. | isolved client.legalCompanies[].client is recursive in the schema, not a request for recursive joins. |

## Current model scope

- Build the company output model as requested, using the existing proposed source_record_type values client / legal_company / ein and source_record_id. No universal company identity is asserted.
- Preserve employee/client/legal/EIN references in their existing provider scope. No new company CLI parameter or automatic association is introduced by this model.
- No additional business-field assumptions are needed to construct this output schema. Connected adapters supply only their known internal source-record role; no new request-context CLI option is introduced.

## Complete source-to-canonical inventory

Each source class is listed once, including nested classes. Follow an object/list field to its named child class. This represents every declared field without duplicating the same reusable class at every possible parent path. RootModel[List[T]] means a top-level JSON array, not an input object with a root key. A field marked required may still accept null if its annotation is Optional.

Targets are relative to each root or nested record. Explicit snake_case provider fields retain their parent/list scope; child-class tables do not flatten parent-client settings into a legal company or promote nested catalog IDs to company identity. Shared targets apply only to the matching root record. Use the common engine preservation rules and finite mapping paths.

### prismhr

#### PrismHRExtension

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/Extension).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `any` | Optional[Dict[str, Any]] | Optional presence | object | No property description supplied. | Metadata: `source_metadata.prismhr.response`; retain field/nesting. |

#### PrismHRClientMasterPayCode

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/ClientMaster-PayCode).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `payCodeId` | Optional[str] | Required presence | string | pay code identifier | Preserve nested/reference scope: `provider_fields.prismhr.pay_code_id` (Optional[str]); identifier helper, no identity substitution. |
| `printOnPayStub` | Optional[str] | Optional presence | string | rule for printing this code on pay stubs issued by the client; allowed values are 0 (Suppress Printing on Pay Stub), 1 (Print on Pay Stub in All Cases), 2 (Print on Pay Stub Unless YTD Dollar Amount is 0), 3 (Print on Pay Stub Unless Current Dollar Amount is 0), and 4 (Print on Pay Stub under Current Earnings but not under YTD Earnings) | Preserve separately: `provider_fields.prismhr.print_on_pay_stub`; keep source type and nested scope. |

#### PrismHRClientMasterDeductionCode

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/ClientMaster-DeductionCode).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `deductionCodeId` | Optional[str] | Required presence | string | deduction code identifier | Preserve nested/reference scope: `provider_fields.prismhr.deduction_code_id` (Optional[str]); identifier helper, no identity substitution. |
| `printOnPayStub` | Optional[str] | Optional presence | string | rule for printing this code on pay stubs issued by the client; allowed values are 0 (Suppress) or 1 (Print on Pay Stub in All Cases) | Preserve separately: `provider_fields.prismhr.print_on_pay_stub`; keep source type and nested scope. |
| `worksiteUserSelectable` | Optional[str] | Optional presence | string | whether the deduction code is available to worksite users; allowed values are Y (yes) or N (no) | Preserve separately: `provider_fields.prismhr.worksite_user_selectable`; keep source type and nested scope. |

#### PrismHRArrear

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/Arrear).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `loanDeductionCodeId` | Optional[str] | Optional presence | string | deduction code identifier for voluntary or employee loan | Preserve nested/reference scope: `provider_fields.prismhr.loan_deduction_code_id` (Optional[str]); identifier helper, no identity substitution. |

#### PrismHREmployeeType

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/EmployeeType).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `typeCodeId` | Optional[str] | Required presence | string | employee type code identifier | Preserve nested/reference scope: `provider_fields.prismhr.type_code_id` (Optional[str]); identifier helper, no identity substitution. |

#### PrismHREmployeeStatus

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/EmployeeStatus).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `statusCodeId` | Optional[str] | Required presence | string | employee status code identifier | Preserve nested/reference scope: `provider_fields.prismhr.status_code_id` (Optional[str]); identifier helper, no identity substitution. |

#### PrismHRReason

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/Reason).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `reasonCodeId` | Optional[str] | Required presence | string | reason code identifier | Preserve nested/reference scope: `provider_fields.prismhr.reason_code_id` (Optional[str]); identifier helper, no identity substitution. |

#### PrismHRClientMasterMiscGL

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/ClientMaster-MiscGL).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `glCode` | Optional[str] | Optional presence | string | system-generated G/L code associated with the miscGLCode | Preserve separately: `provider_fields.prismhr.gl_code`; keep source type and nested scope. |
| `miscGLCode` | Optional[str] | Optional presence | string | miscellaneous G/L code | Preserve separately: `provider_fields.prismhr.misc_gl_code`; keep source type and nested scope. |

#### PrismHRObservedHoliday

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/ObservedHoliday).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `name` | Optional[str] | Optional presence | string | code identifying the holiday, or collection of holidays | Preserve separately: `provider_fields.prismhr.name`; keep source type and nested scope. |
| `description` | Optional[str] | Optional presence | string | name of the holiday, or collection of holidays | Preserve separately: `provider_fields.prismhr.description`; keep source type and nested scope. |
| `holidayDate` | Optional[List[str]] | Optional presence | array | date of the holiday | Preserve separately: `provider_fields.prismhr.holiday_date`; keep source type and nested scope. |

#### PrismHRAltEmployer

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/AltEmployer).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `altEmployerId` | str | Required presence | string | alternate employer ID | Preserve nested/reference scope: `provider_fields.prismhr.alt_employer_id` (str); identifier helper, no identity substitution. |
| `altCostCtr` | Optional[str] | Optional presence | string | cost center for employees assigned to this alternate employer; if empty, the system defaults to the client's primary cost center | Preserve separately: `provider_fields.prismhr.alt_cost_ctr`; keep source type and nested scope. |
| `altCheckingAcct` | Optional[str] | Optional presence | string | payroll checking account used by the employer | Preserve separately: `provider_fields.prismhr.alt_checking_acct`; keep source type and nested scope. |
| `altAchAcct` | Optional[str] | Optional presence | string | ACH account used by the employer | Preserve separately: `provider_fields.prismhr.alt_ach_acct`; keep source type and nested scope. |
| `altDisplayName` | Optional[str] | Optional presence | string | if suppressClientAccess = "N", this name displays during new hire entry to identify the employer as a selectable option | Preserve separately: `provider_fields.prismhr.alt_display_name`; keep source type and nested scope. |
| `suppressClientAccess` | Optional[str] | Optional presence | string | "Y" or empty = this employer is not displayed or selectable on the New Hire form, "N" = the employer is selectable on the New Hire form | Preserve separately: `provider_fields.prismhr.suppress_client_access`; keep source type and nested scope. |

#### PrismHRClientRetirementPlanObject

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/ClientRetirementPlanObject).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `retirePlan` | Optional[str] | Optional presence | string | retirement plan ID | Preserve separately: `provider_fields.prismhr.retire_plan`; keep source type and nested scope. |
| `thirdPartyPlanId` | Optional[str] | Optional presence | string | third-party administrator plan ID | Preserve nested/reference scope: `provider_fields.prismhr.third_party_plan_id` (Optional[str]); identifier helper, no identity substitution. |

#### PrismHRBillFixed

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/BillFixed).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `billFixedSpecRate` | Optional[str] | Optional presence | string | special billing rate override | Preserve separately: `provider_fields.prismhr.bill_fixed_spec_rate`; keep source type and nested scope. |
| `billFixedSpecFrom` | Optional[str] | Optional presence | string | first date when special rate goes into effect | Preserve separately: `provider_fields.prismhr.bill_fixed_spec_from`; keep source type and nested scope. |
| `billFixedSpecTo` | Optional[str] | Optional presence | string | last date when special rate expires | Preserve separately: `provider_fields.prismhr.bill_fixed_spec_to`; keep source type and nested scope. |

#### PrismHRHolidayPay

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/HolidayPay).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `holidayOnDay` | Optional[str] | Optional presence | string | day of the week on which the holiday must fall to make an adjustment to the pay date | Preserve separately: `provider_fields.prismhr.holiday_on_day`; keep source type and nested scope. |
| `holidayPayOnDay` | Optional[str] | Optional presence | string | day of the week to adjust the pay date to if the holiday falls on the specified holidayOnDay | Preserve separately: `provider_fields.prismhr.holiday_pay_on_day`; keep source type and nested scope. |
| `holidayPayBefAft` | Optional[str] | Optional presence | string | whether the new pay day should be before or after the existing | Preserve separately: `provider_fields.prismhr.holiday_pay_bef_aft`; keep source type and nested scope. |

#### PrismHRSdiDedn

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/SdiDedn).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `sdiTaxCode` | Optional[str] | Optional presence | string | state disability insurance tax code | Preserve separately: `provider_fields.prismhr.sdi_tax_code`; keep source type and nested scope. |
| `sdiDednCode` | Optional[str] | Optional presence | string | state disability insurance deduction code | Preserve separately: `provider_fields.prismhr.sdi_dedn_code`; keep source type and nested scope. |

#### PrismHRClientMasterClientTax

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/ClientMaster-ClientTax).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `suiState` | Optional[str] | Optional presence | string | two-character state postal code | Preserve separately: `provider_fields.prismhr.sui_state`; keep source type and nested scope. |
| `suiStateEmpId` | Optional[str] | Optional presence | string | state unemployment insurance employer ID | Preserve nested/reference scope: `provider_fields.prismhr.sui_state_emp_id` (Optional[str]); identifier helper, no identity substitution. |
| `stateTaxId` | Optional[str] | Optional presence | string | client state tax ID | Preserve nested/reference scope: `provider_fields.prismhr.state_tax_id` (Optional[str]); identifier helper, no identity substitution. |
| `ctrStartDate` | Optional[str] | Optional presence | string / date | client reporting start date | Preserve separately: `provider_fields.prismhr.ctr_start_date` (Optional[date]); date helper, source originals/issues retained. |
| `ctrEndDate` | Optional[str] | Optional presence | string / date | client reporting end date | Preserve separately: `provider_fields.prismhr.ctr_end_date` (Optional[date]); date helper, source originals/issues retained. |
| `suiSecondaryId` | Optional[str] | Optional presence | string | secondary state unemployment insurance employer ID for states such as Kansas and Missouri | Preserve nested/reference scope: `provider_fields.prismhr.sui_secondary_id` (Optional[str]); identifier helper, no identity substitution. |
| `miscTaxId` | Optional[str] | Optional presence | string | miscellaneous tax identifier for this state | Preserve nested/reference scope: `provider_fields.prismhr.misc_tax_id` (Optional[str]); identifier helper, no identity substitution. |
| `miscTaxCode` | Optional[str] | Optional presence | string | miscellaneous tax code associated with the miscTaxId | Preserve separately: `provider_fields.prismhr.misc_tax_code`; keep source type and nested scope. |

#### PrismHRRedir

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/Redir).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `redirTaxCode` | Optional[str] | Optional presence | string | tax code to redirect from | Preserve separately: `provider_fields.prismhr.redir_tax_code`; keep source type and nested scope. |
| `redirToTaxCode` | Optional[str] | Optional presence | string | tax code to redirect to | Preserve separately: `provider_fields.prismhr.redir_to_tax_code`; keep source type and nested scope. |

#### PrismHRRegRebuild

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/RegRebuild).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `regRebuildDate` | Optional[Union[str, int]] | Optional presence | string / date-time | date/time for register rebuild | Preserve separately: `provider_fields.prismhr.reg_rebuild_date`; keep source type and nested scope. |
| `regRebuildUser` | Optional[str] | Optional presence | string | rebuild register user ID | Preserve separately: `provider_fields.prismhr.reg_rebuild_user`; keep source type and nested scope. |
| `regRebuildReason` | Optional[str] | Optional presence | string | reason for register rebuild | Preserve separately: `provider_fields.prismhr.reg_rebuild_reason`; keep source type and nested scope. |
| `regRebuildYear` | Optional[str] | Optional presence | string | year for the register rebuild | Preserve separately: `provider_fields.prismhr.reg_rebuild_year`; keep source type and nested scope. |

#### PrismHRCommission

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/Commission).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `commSalesperson` | Optional[str] | Optional presence | string | user ID of the sales representative associated with the client | Preserve separately: `provider_fields.prismhr.comm_salesperson`; keep source type and nested scope. |
| `commDateFrom` | Optional[str] | Optional presence | string / date | date on which the commission level goes into effect | Preserve separately: `provider_fields.prismhr.comm_date_from` (Optional[date]); date helper, source originals/issues retained. |
| `commDateTo` | Optional[str] | Optional presence | string / date | date on which the commission level expires | Preserve separately: `provider_fields.prismhr.comm_date_to` (Optional[date]); date helper, source originals/issues retained. |
| `commAmount` | Optional[str] | Optional presence | string | amount of the commission, either flat or percentage | Preserve separately: `provider_fields.prismhr.comm_amount`; keep source type and nested scope. |
| `commFlatPct` | Optional[bool] | Optional presence | boolean | indicates whether the commission is a flat rate (F) or a percentage (P) | Preserve separately: `provider_fields.prismhr.comm_flat_pct`; keep source type and nested scope. |
| `commBasedOn` | Optional[str] | Optional presence | string | indicates what the commission is based on: 'GW' (Gross Wages), 'ADM' (Admin Fees), 'WC' (Workers Comp), 'AL' (Average Lives), 'GP' (Gross Profit), 'TP' (Tax Profit), 'FG1' (Fixed Amount Group 1), 'FG2' (Fixed Amount Group 2), 'FG3' (Fixed Amount Group 3), 'FG4' (Fixed Amount Group 4), 'FG5' (Fixed Amount Group 5), or 'FPE' (Fixed per Paid Employee). | Preserve separately: `provider_fields.prismhr.comm_based_on`; keep source type and nested scope. |
| `commBasedOnPlan` | Optional[str] | Optional presence | string | If the service provider uses a complex commission structure, this is the commission plan ID. Do not use commAmount, commFlatPct, or commBasedOn. | Preserve separately: `provider_fields.prismhr.comm_based_on_plan`; keep source type and nested scope. |
| `commType` | Optional[str] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Preserve separately: `provider_fields.prismhr.comm_type`; keep source type and nested scope. |
| `targetAmt` | Optional[str] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Preserve separately: `provider_fields.prismhr.target_amt`; keep source type and nested scope. |

#### PrismHRBillEvent

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/BillEvent).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `billEvtCode` | Optional[str] | Optional presence | string | billing event code | Preserve separately: `provider_fields.prismhr.bill_evt_code`; keep source type and nested scope. |
| `billEvtRate` | Optional[str] | Optional presence | string | billing rate | Preserve separately: `provider_fields.prismhr.bill_evt_rate`; keep source type and nested scope. |
| `billEvtSpecialRate` | Optional[str] | Optional presence | string | special billing rate | Preserve separately: `provider_fields.prismhr.bill_evt_special_rate`; keep source type and nested scope. |
| `billEvtSpecialFrom` | Optional[str] | Optional presence | string / date | first date when special rate goes into effect | Preserve separately: `provider_fields.prismhr.bill_evt_special_from`; keep source type and nested scope. |
| `billEvtSpecialTo` | Optional[str] | Optional presence | string / date | last date when special rate expires | Preserve separately: `provider_fields.prismhr.bill_evt_special_to`; keep source type and nested scope. |

#### PrismHRReportFee

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/ReportFee).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `rptCode` | Optional[str] | Optional presence | string | report code to include or exclude in payroll for the client | Preserve separately: `provider_fields.prismhr.rpt_code`; keep source type and nested scope. |
| `rptFee` | Optional[str] | Optional presence | string | report fee to charge for the client, or -9.99 to exclude a standard report | Preserve separately: `provider_fields.prismhr.rpt_fee`; keep source type and nested scope. |

#### PrismHRMySupportTeamDashboard

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/MySupportTeamDashboard).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `dashFieldName` | Optional[str] | Optional presence | string | name of the custom dashboard field, if this feature is enabled | Preserve separately: `provider_fields.prismhr.dash_field_name`; keep source type and nested scope. |
| `dashFieldValue` | Optional[str] | Optional presence | string | value stored by this field, if the custom dashboard feature is enabled | Preserve separately: `provider_fields.prismhr.dash_field_value`; keep source type and nested scope. |

#### PrismHREnrollOnboardControls

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/EnrollOnboardControls).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `elecBenefitsEnroll` | Optional[str] | Optional presence | string | whether employees use PrismHR benefits enrollment. "G" denotes employees use PrismHR benefits enrollment | Preserve separately: `provider_fields.prismhr.elec_benefits_enroll`; keep source type and nested scope. |
| `elecOnboarding` | Optional[str] | Optional presence | string | whether new employees use electronic onboarding. Values are (A)lways, P(rompt), and N(ever)/empty string. If P, the New Hire form prompts users to indicate where onboarding information will be submitted | Preserve separately: `provider_fields.prismhr.elec_onboarding`; keep source type and nested scope. |
| `elecOnboardRehire` | Optional[str] | Optional presence | string | whether client rehires automatically use PrismHR onboarding. Values are (A)lways, P(rompt), and N(ever)/empty string. If P, the New Hire form prompts users to indicate where onboarding information will be submitted | Preserve separately: `provider_fields.prismhr.elec_onboard_rehire`; keep source type and nested scope. |
| `i9businessAddress` | Optional[str] | Optional presence | string | whether the system uses the (E)mployer or C(lient) address. If C, the system uses the client's "doing-business-as" (DBA) address | Preserve separately: `provider_fields.prismhr.i9business_address`; keep source type and nested scope. |
| `allowUploadDocs` | Optional[str] | Optional presence | string | whether the system allows employees of this client to upload supporting Form I-9 documents during the I-9 workflow. Values are Y (Enabled), N (Disabled), and empty string (System Default - defaults to the value stored in systemAllowUploadDocs) | Preserve separately: `provider_fields.prismhr.allow_upload_docs`; keep source type and nested scope. |
| `systemAllowUploadDocs` | Optional[str] | Optional presence | string | global equivalent to allowUploadDocs, located on the Onboarding Options form. This determines the system-level logic for I-9 document uploads unless a client-level override exists | Preserve separately: `provider_fields.prismhr.system_allow_upload_docs`; keep source type and nested scope. |
| `completeAllForms` | Optional[str] | Optional presence | string | whether the system allows employees of this client to be added to a payroll before all onboarding forms are complete (specifically: employee completion of I-9 Section 1 and manager completion of I-9 Section 2). Values are Y (Enabled), N (Disabled), and empty string (System Default - defaults to the value stored in systemCompleteAllForms) | Preserve separately: `provider_fields.prismhr.complete_all_forms`; keep source type and nested scope. |
| `systemCompleteAllForms` | Optional[str] | Optional presence | string | global equivalent to completeAllForms, located on the Onboarding Options form. This determines the system-level logic for inclusion of employees on payrolls before all onboarding documents are complete | Preserve separately: `provider_fields.prismhr.system_complete_all_forms`; keep source type and nested scope. |
| `enableBEAfterFinalSubmit` | Optional[str] | Optional presence | string | whether employees of this client can access their benefit enrollment workflow through Onboarding after submitting all onboarding-related forms. Values are Y (Enabled), N (Disabled), and empty string (System Default - defaults to the value stored in systemEnableBEAfterFinalSubmit) | Preserve separately: `provider_fields.prismhr.enable_be_after_final_submit`; keep source type and nested scope. |
| `systemEnableBEAfterFinalSubmit` | Optional[str] | Optional presence | string | global equivalent to enableBEAfterFinalSubmit, located on the Onboarding Options form. This determines the system-level logic for the accessibility of benefit enrollment workflows after completing onboarding. | Preserve separately: `provider_fields.prismhr.system_enable_be_after_final_submit`; keep source type and nested scope. |
| `onboardVersion` | Optional[str] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Preserve separately: `provider_fields.prismhr.onboard_version`; keep source type and nested scope. |
| `decisionSupport` | Optional[str] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Preserve separately: `provider_fields.prismhr.decision_support`; keep source type and nested scope. |

#### PrismHRClientMaster

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/ClientMaster).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | str | Required presence | string | unique ID code for the client company | Shared: `source_record_id`. Use the agreed helper where needed; retain conversion originals/issues. |
| `clientName` | Optional[str] | Optional presence | string | doing-business-as client name | Shared: `trade_name`. Use the agreed helper where needed; retain conversion originals/issues. |
| `costCenter` | Optional[str] | Optional presence | string | cost center for processing accounting transactions | Preserve separately: `provider_fields.prismhr.cost_center`; keep source type and nested scope. |
| `subCostCenter` | Optional[str] | Optional presence | string | sub-cost center for processing accounting transactions | Preserve separately: `provider_fields.prismhr.sub_cost_center`; keep source type and nested scope. |
| `serviceType` | Optional[str] | Optional presence | string | Service provided to client: 'ASO' (Administrative Services Only), 'PEO' (Professional Employer Services), 'PAY' (Payroll Processing Only), 'ASA' (Admin Services/Alt. Billing), 'COR' (Corporate Payroll), or 'HRN' (HR Services, No Payroll). | Preserve separately: `provider_fields.prismhr.service_type` (Optional[str]); exact documented labels below; originals retained. |
| `categoryCode` | Optional[str] | Optional presence | string | industry in which the client does business | Preserve separately: `provider_fields.prismhr.category_code`; keep source type and nested scope. |
| `stateCode` | Optional[str] | Optional presence | string | delivery/mailing address state two-character code | Preserve separately: `provider_fields.prismhr.state_code`; keep source type and nested scope. |
| `zipCode` | Optional[str] | Optional presence | string | delivery/mailing address ZIP code | Preserve separately: `provider_fields.prismhr.zip_code`; keep source type and nested scope. |
| `legalName` | Optional[str] | Optional presence | string | legal business name for client | Shared: `legal_name`. Use the agreed helper where needed; retain conversion originals/issues. |
| `arClientNumber` | Optional[str] | Optional presence | string | client ID to use for billing, if not this client | Preserve separately: `provider_fields.prismhr.ar_client_number`; keep source type and nested scope. |
| `divisionRequired` | Optional[bool] | Optional presence | boolean | indicates whether employees must be assigned to a division for time sheets/labor allocation | Preserve separately: `provider_fields.prismhr.division_required`; keep source type and nested scope. |
| `departmentRequired` | Optional[bool] | Optional presence | boolean | indicates whether employees must be assigned to a department for time sheets/labor allocation | Preserve separately: `provider_fields.prismhr.department_required`; keep source type and nested scope. |
| `shiftRequired` | Optional[bool] | Optional presence | boolean | indicates whether employees must be assigned to a shift for time sheets/labor allocation | Preserve separately: `provider_fields.prismhr.shift_required`; keep source type and nested scope. |
| `empNumbersUsed` | Optional[bool] | Optional presence | boolean | indicates whether to assign employees an employee number unique to the client organization | Preserve separately: `provider_fields.prismhr.emp_numbers_used`; keep source type and nested scope. |
| `autoEmpNumber` | Optional[bool] | Optional presence | boolean | indicates whether to generate employee numbers automatically | Preserve separately: `provider_fields.prismhr.auto_emp_number`; keep source type and nested scope. |
| `worksitePayrollApproval` | Optional[str] | Optional presence | string | determine the payroll approval process for the client. N (Disabled), Y (Standard) (default), M (Multistep) | Preserve separately: `provider_fields.prismhr.worksite_payroll_approval`; keep source type and nested scope. |
| `projectRequired` | Optional[bool] | Optional presence | boolean | indicates whether employees must be assigned to a project for time sheets/labor allocation | Preserve separately: `provider_fields.prismhr.project_required`; keep source type and nested scope. |
| `workGroupRequired` | Optional[bool] | Optional presence | boolean | indicates whether the workgroup is required | Preserve separately: `provider_fields.prismhr.work_group_required`; keep source type and nested scope. |
| `payrollDate` | Optional[str] | Optional presence | string / date | first payroll date processed for this client | Preserve separately: `provider_fields.prismhr.payroll_date` (Optional[date]); date helper, source originals/issues retained. |
| `statusDate` | Optional[str] | Optional presence | string / date | date of status | Preserve separately: `provider_fields.prismhr.status_date` (Optional[date]); date helper, source originals/issues retained. |
| `status` | Optional[str] | Optional presence | string | client status code,corresponding to one of the following status classes: “A” (Active), “P” (Pending), “I” (Inactive), “C” (Client Cancelling, Pre-Termination) and “T” (Terminated) | Preserve separately: `provider_fields.prismhr.status`; keep source type and nested scope. |
| `deliverChecks` | Optional[str] | Optional presence | string | location to deliver payroll checks 'H' (employees' homes), 'L' (worksite locations), 'M' (main client location), 'P' (paperless), or 'U' (client will pick up the checks) | Preserve separately: `provider_fields.prismhr.deliver_checks`; keep source type and nested scope. |
| `employerId` | Optional[str] | Optional presence | string | employer ID to which to assign this client's employees | Preserve nested/reference scope: `provider_fields.prismhr.employer_id` (Optional[str]); identifier helper, no identity substitution. |
| `minCheckAmt` | Optional[str] | Optional presence | string | minimum check amount that requires validation | Preserve separately: `provider_fields.prismhr.min_check_amt`; keep source type and nested scope. |
| `maxCheckAmt` | Optional[str] | Optional presence | string | maximum check amount that requires validation | Preserve separately: `provider_fields.prismhr.max_check_amt`; keep source type and nested scope. |
| `deliveryMethod` | Optional[str] | Optional presence | string | method for delivering payroll to client | Preserve separately: `provider_fields.prismhr.delivery_method`; keep source type and nested scope. |
| `mainPhoneExt` | Optional[str] | Optional presence | string | Extension of main company phone number; should just be the extension number, no alpha characters such as 'x' or 'ext' | Preserve separately: `provider_fields.prismhr.main_phone_ext`; keep source type and nested scope. |
| `addressLine1` | Optional[str] | Optional presence | string | delivery/mailing address line 1 | Preserve separately: `provider_fields.prismhr.address_line1`; keep source type and nested scope. |
| `addressLine2` | Optional[str] | Optional presence | string | delivery/mailing address line 2 | Preserve separately: `provider_fields.prismhr.address_line2`; keep source type and nested scope. |
| `city` | Optional[str] | Optional presence | string | delivery/mailing address city | Preserve separately: `provider_fields.prismhr.city`; keep source type and nested scope. |
| `zipSuffix` | Optional[str] | Optional presence | string | delivery/mailing address ZIP+4 suffix | Preserve separately: `provider_fields.prismhr.zip_suffix`; keep source type and nested scope. |
| `mainPhone` | Optional[str] | Optional presence | string | area code and local number for the client's primary telephone number | Preserve separately: `provider_fields.prismhr.main_phone`; keep source type and nested scope. |
| `fax` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.prismhr.fax`; keep source type and nested scope. |
| `websiteUrl` | Optional[str] | Optional presence | string | URL for client's website | Preserve separately: `provider_fields.prismhr.website_url`; keep source type and nested scope. |
| `emailAddress` | Optional[str] | Optional presence | string | primary email address used to contact the client | Preserve separately: `provider_fields.prismhr.email_address`; keep source type and nested scope. |
| `businessDescription` | Optional[str] | Optional presence | string | short description of client's business | Preserve separately: `provider_fields.prismhr.business_description`; keep source type and nested scope. |
| `sicCode` | Optional[str] | Optional presence | string | Standard Industrial Classification code | Preserve separately: `provider_fields.prismhr.sic_code`; keep source type and nested scope. |
| `federalIdNumber` | Optional[str] | Optional presence | string | Federal Identification Number | Shared: `federal_tax_id`. Use the agreed helper where needed; retain conversion originals/issues. |
| `billFormat` | Optional[str] | Optional presence | string | client's bill format code | Preserve separately: `provider_fields.prismhr.bill_format`; keep source type and nested scope. |
| `groupCode` | Optional[str] | Optional presence | string | used to allow selection and grouping of clients | Preserve separately: `provider_fields.prismhr.group_code`; keep source type and nested scope. |
| `tpaDownloadOptions` | Optional[str] | Optional presence | string | the type of third-party administrator download options used for the client | Preserve separately: `provider_fields.prismhr.tpa_download_options`; keep source type and nested scope. |
| `hoursType1` | Optional[str] | Optional presence | string | Pay Code 1 in the PrismHR UI | Preserve separately: `provider_fields.prismhr.hours_type1`; keep source type and nested scope. |
| `hoursType2` | Optional[str] | Optional presence | string | Pay Code 2 in the PrismHR UI | Preserve separately: `provider_fields.prismhr.hours_type2`; keep source type and nested scope. |
| `hoursType3` | Optional[str] | Optional presence | string | Pay Code 3 in the PrismHR UI | Preserve separately: `provider_fields.prismhr.hours_type3`; keep source type and nested scope. |
| `hoursType4` | Optional[str] | Optional presence | string | Pay Code 4 in the PrismHR UI | Preserve separately: `provider_fields.prismhr.hours_type4`; keep source type and nested scope. |
| `hoursType5` | Optional[str] | Optional presence | string | Pay Code 5 in the PrismHR UI | Preserve separately: `provider_fields.prismhr.hours_type5`; keep source type and nested scope. |
| `hoursType6` | Optional[str] | Optional presence | string | Pay Code 6 in the PrismHR UI | Preserve separately: `provider_fields.prismhr.hours_type6`; keep source type and nested scope. |
| `hoursType9` | Optional[str] | Optional presence | string | Pay Code 9 in the PrismHR UI | Preserve separately: `provider_fields.prismhr.hours_type9`; keep source type and nested scope. |
| `flatType1` | Optional[str] | Optional presence | string | Pay Code 7 in the PrismHR UI | Preserve separately: `provider_fields.prismhr.flat_type1`; keep source type and nested scope. |
| `flatType2` | Optional[str] | Optional presence | string | Pay Code 8 in the PrismHR UI | Preserve separately: `provider_fields.prismhr.flat_type2`; keep source type and nested scope. |
| `extraHeading1` | Optional[str] | Optional presence | string | Pay Code 10 in the PrismHR UI | Preserve separately: `provider_fields.prismhr.extra_heading1`; keep source type and nested scope. |
| `extraHeading2` | Optional[str] | Optional presence | string | Not Used | Preserve separately: `provider_fields.prismhr.extra_heading2`; keep source type and nested scope. |
| `corporationType` | Optional[str] | Optional presence | string | must be one of the following single-character values: 'L' (Limited Liability Corporation), 'S' (S-Corporation), 'C' (C-Corporation), 'I' (Individual/Sole Proprieter), 'P' (Partnership), 'A' (Limited Partnership), 'M' (Limited Liability Partnership), 'R' (Professional Corporation), 'V' (Personal Service Corporation), 'B' (Board Owned), 'J' (Joint Venture), 'T' (Tax Exempt), 'U' (Trust), 'H' (Church Organization), 'N' (Not for Profit), or 'O' (Other). | Preserve separately: `provider_fields.prismhr.corporation_type`; keep source type and nested scope. |
| `controlGroupCompany` | Optional[str] | Optional presence | string | ID of the client that will act as the Master Client ID for the 401(k) Control Group | Preserve separately: `provider_fields.prismhr.control_group_company`; keep source type and nested scope. |
| `cafeteriaPlan` | Optional[str] | Optional presence | string | Section 125 Plan ID | Preserve separately: `provider_fields.prismhr.cafeteria_plan`; keep source type and nested scope. |
| `hsaPlanId` | Optional[str] | Optional presence | string | Health Savings Account Plan ID | Preserve nested/reference scope: `provider_fields.prismhr.hsa_plan_id` (Optional[str]); identifier helper, no identity substitution. |
| `glClientNo` | Optional[str] | Optional presence | string | company designation used to build the general ledger account number | Preserve separately: `provider_fields.prismhr.gl_client_no`; keep source type and nested scope. |
| `billTemplate` | Optional[str] | Optional presence | string | billing template used to compute client billing | Preserve separately: `provider_fields.prismhr.bill_template`; keep source type and nested scope. |
| `wcPolicy` | Optional[str] | Optional presence | string | worker's compensation insurance policy that covers the client's employees | Preserve separately: `provider_fields.prismhr.wc_policy`; keep source type and nested scope. |
| `wcPolicyEffDate` | Optional[str] | Optional presence | string / date | effective date for client's workers compensation insurance coverage | Preserve separately: `provider_fields.prismhr.wc_policy_eff_date` (Optional[date]); date helper, source originals/issues retained. |
| `wcLocationBased` | Optional[bool] | Optional presence | boolean | if true, indicates that the W/C Calculation Option field is set to Time Sheet Location Based; the system associates the employee with their time sheet worksite location during Workers' Compensation calculations | Preserve separately: `provider_fields.prismhr.wc_location_based`; keep source type and nested scope. |
| `flsaRuleset` | Optional[str] | Optional presence | string | FLSA ruleset used to process the payroll | Preserve separately: `provider_fields.prismhr.flsa_ruleset`; keep source type and nested scope. |
| `flsaWeekEnds` | Optional[str] | Optional presence | string | Day of the week on which the FLSA work week ends: 1 - Monday, 2 - Tuesday, 3 - Wednesday, 4 - Thursday, 5 - Friday, 6 - Saturday, or7 - Sunday. | Preserve separately: `provider_fields.prismhr.flsa_week_ends`; keep source type and nested scope. |
| `satPayOnDay` | Optional[str] | Optional presence | string | Day of week to adjust pay date if scheduled pay date is a Saturday: 1 - Monday, 2 - Tuesday, 3 - Wednesday, 4 - Thursday, 5 - Friday, or blank - no change; pay date on Saturday. | Preserve separately: `provider_fields.prismhr.sat_pay_on_day`; keep source type and nested scope. |
| `sunPayOnDay` | Optional[str] | Optional presence | string | Day of week to adjust pay date if scheduled pay date is a Sunday: 1 - Monday, 2 - Tuesday, 3 - Wednesday, 4 - Thursday, 5 - Friday, or blank - no change; pay date on Sunday. | Preserve separately: `provider_fields.prismhr.sun_pay_on_day`; keep source type and nested scope. |
| `satPayBefAft` | Optional[str] | Optional presence | string | indicates whether to pay before or after when the pay date falls on Saturday | Preserve separately: `provider_fields.prismhr.sat_pay_bef_aft`; keep source type and nested scope. |
| `sunPayBefAft` | Optional[str] | Optional presence | string | indicates whether to pay before or after when the pay date falls on a Sunday | Preserve separately: `provider_fields.prismhr.sun_pay_bef_aft`; keep source type and nested scope. |
| `contractDate` | Optional[str] | Optional presence | string / date | date on which the contract was signed | Preserve separately: `provider_fields.prismhr.contract_date` (Optional[date]); date helper, source originals/issues retained. |
| `benefitParentClient` | Optional[str] | Optional presence | string | ID of another client that acts as the 'parent' to this client, for benefits purposes | Preserve separately: `provider_fields.prismhr.benefit_parent_client`; keep source type and nested scope. |
| `payCode` | Optional[List[PrismHRClientMasterPayCode]] | Optional presence | array | pay codes used for this client; leave blank to make all available | Preserve separately: `provider_fields.prismhr.pay_code`; keep source type and nested scope. |
| `deductionCode` | Optional[List[PrismHRClientMasterDeductionCode]] | Optional presence | array | deduction codes used for this client; leave blank to make all available | Preserve separately: `provider_fields.prismhr.deduction_code`; keep source type and nested scope. |
| `arrear` | Optional[List[PrismHRArrear]] | Optional presence | array | arrears array | Preserve separately: `provider_fields.prismhr.arrear`; keep source type and nested scope. |
| `employeeType` | Optional[List[PrismHREmployeeType]] | Optional presence | array | employee type code array | Preserve separately: `provider_fields.prismhr.employee_type`; keep source type and nested scope. |
| `employeeStatus` | Optional[List[PrismHREmployeeStatus]] | Optional presence | array | employee status code array | Preserve separately: `provider_fields.prismhr.employee_status`; keep source type and nested scope. |
| `reason` | Optional[List[PrismHRReason]] | Optional presence | array | reason code array | Preserve separately: `provider_fields.prismhr.reason`; keep source type and nested scope. |
| `miscGL` | Optional[List[PrismHRClientMasterMiscGL]] | Optional presence | array | GL Misc code array | Preserve separately: `provider_fields.prismhr.misc_gl`; keep source type and nested scope. |
| `observedHoliday` | Optional[List[PrismHRObservedHoliday]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.prismhr.observed_holiday`; keep source type and nested scope. |
| `abbrvName` | Optional[str] | Optional presence | string | abbreviated version of client name | Preserve separately: `provider_fields.prismhr.abbrv_name`; keep source type and nested scope. |
| `annualHours` | Optional[str] | Optional presence | string | annual hours worked in a year by an employee, typically 2080 (52 weeks x 40 hours) | Preserve separately: `provider_fields.prismhr.annual_hours`; keep source type and nested scope. |
| `sortField1` | Optional[str] | Optional presence | string | check print sort field number 1 | Preserve separately: `provider_fields.prismhr.sort_field1`; keep source type and nested scope. |
| `sortField2` | Optional[str] | Optional presence | string | check print sort field number 2 | Preserve separately: `provider_fields.prismhr.sort_field2`; keep source type and nested scope. |
| `sortField3` | Optional[str] | Optional presence | string | check print sort field number 3 | Preserve separately: `provider_fields.prismhr.sort_field3`; keep source type and nested scope. |
| `billBySort` | Optional[str] | Optional presence | string | Sort order to use for billings, which causes subtotals: 'DV' (Division), 'LC' (Location), 'DP' (Department), 'SH' (Shift), or it can be a combination, concatenated with periods. | Preserve separately: `provider_fields.prismhr.bill_by_sort`; keep source type and nested scope. |
| `billInvBreakField` | Optional[str] | Optional presence | string | segment of the billBySort that causes an invoice break | Preserve separately: `provider_fields.prismhr.bill_inv_break_field`; keep source type and nested scope. |
| `consultant` | Optional[str] | Optional presence | string | ID of the consultant assigned to this client | Preserve separately: `provider_fields.prismhr.consultant`; keep source type and nested scope. |
| `salesperson` | Optional[str] | Optional presence | string | ID of the user responsible for sales to the client | Preserve separately: `provider_fields.prismhr.salesperson`; keep source type and nested scope. |
| `payrollRep` | Optional[str] | Optional presence | string | ID of the user responsible for processing the client's payroll | Preserve separately: `provider_fields.prismhr.payroll_rep`; keep source type and nested scope. |
| `checkIssueAcct` | Optional[str] | Optional presence | string | ID of the checking account from which to draw checks to pay employees | Preserve separately: `provider_fields.prismhr.check_issue_acct`; keep source type and nested scope. |
| `checkPrintStyle` | Optional[str] | Optional presence | string | Code for the special check style to use for the client; if blank, system uses standard check style. | Preserve separately: `provider_fields.prismhr.check_print_style`; keep source type and nested scope. |
| `invoiceCopies` | Optional[str] | Optional presence | string | number of invoices to print for the client during processing | Preserve separately: `provider_fields.prismhr.invoice_copies`; keep source type and nested scope. |
| `remitCopies` | Optional[str] | Optional presence | string | number of remittance copies to print during payroll processing | Preserve separately: `provider_fields.prismhr.remit_copies`; keep source type and nested scope. |
| `receiptCheckAcct` | Optional[str] | Optional presence | string | account for ACH or credit card receipts | Preserve separately: `provider_fields.prismhr.receipt_check_acct`; keep source type and nested scope. |
| `adjAchDays` | Optional[str] | Optional presence | string | Number of days (which can be negative) by which to adjust the processing of the ACH. Please note this only avoids weekends, not bank holidays. | Preserve separately: `provider_fields.prismhr.adj_ach_days`; keep source type and nested scope. |
| `serviceTermReason` | Optional[str] | Optional presence | string | reason the client was terminated | Preserve separately: `provider_fields.prismhr.service_term_reason`; keep source type and nested scope. |
| `garnCheckIssueAcct` | Optional[str] | Optional presence | string | ID of the checking account from which to draw garnishment checks | Preserve separately: `provider_fields.prismhr.garn_check_issue_acct`; keep source type and nested scope. |
| `directDepositAccount` | Optional[str] | Optional presence | string | Account from which direct deposit (ACH) amounts are drawn. If left blank, the Payroll Account (checkIssueAcct) is used | Preserve separately: `provider_fields.prismhr.direct_deposit_account`; keep source type and nested scope. |
| `manualAccount` | Optional[str] | Optional presence | string | Account from which manual checks are drawn. A value is required in this field if manual checks are entered with the Pay Check Calculator | Preserve separately: `provider_fields.prismhr.manual_account`; keep source type and nested scope. |
| `onDemandChecksAccount` | Optional[str] | Optional presence | string | Account from which manual checks are drawn for On Demand Check processing | Preserve separately: `provider_fields.prismhr.on_demand_checks_account`; keep source type and nested scope. |
| `payCardAccount` | Optional[str] | Optional presence | string | Account used to pay cards/debit cards | Preserve separately: `provider_fields.prismhr.pay_card_account`; keep source type and nested scope. |
| `nesOffset` | Optional[str] | Optional presence | string | Number of days to delay billing the New Employee Setup fees. If used, a termination before this date reverses the NES. | Preserve separately: `provider_fields.prismhr.nes_offset`; keep source type and nested scope. |
| `rateOrMarkup` | Optional[str] | Optional presence | string | indicates whether amount will be a rate or a markup factor for job rate clients | Preserve separately: `provider_fields.prismhr.rate_or_markup`; keep source type and nested scope. |
| `billAddressLine1` | Optional[str] | Optional presence | string | billing address line 1 | Preserve separately: `provider_fields.prismhr.bill_address_line1`; keep source type and nested scope. |
| `billAddressLine2` | Optional[str] | Optional presence | string | billing address line 2 | Preserve separately: `provider_fields.prismhr.bill_address_line2`; keep source type and nested scope. |
| `billZipCode` | Optional[str] | Optional presence | string | billing address ZIP code | Preserve separately: `provider_fields.prismhr.bill_zip_code`; keep source type and nested scope. |
| `billCity` | Optional[str] | Optional presence | string | billing address city | Preserve separately: `provider_fields.prismhr.bill_city`; keep source type and nested scope. |
| `billStateCode` | Optional[str] | Optional presence | string | billing address state two-character code | Preserve separately: `provider_fields.prismhr.bill_state_code`; keep source type and nested scope. |
| `billZipSuffix` | Optional[str] | Optional presence | string | billing address ZIP+4 suffix | Preserve separately: `provider_fields.prismhr.bill_zip_suffix`; keep source type and nested scope. |
| `billAddrClientId` | Optional[str] | Optional presence | string | client ID of the client company whose billing address should be used in place of this client's address (e.g., parent company) | Preserve nested/reference scope: `provider_fields.prismhr.bill_addr_client_id` (Optional[str]); identifier helper, no identity substitution. |
| `newHireAlert` | Optional[str] | Optional presence | string | Indicates who should receive the Web New Hire alert message: 'P' (Payroll Representative), 'H' or blank (H/R Consultant), 'S' (Salesperson), or it can be a combination. | Preserve separately: `provider_fields.prismhr.new_hire_alert`; keep source type and nested scope. |
| `clientAccountingCode` | Optional[str] | Optional presence | string | standard client account to use for the client, unless overridden at location | Preserve separately: `provider_fields.prismhr.client_accounting_code`; keep source type and nested scope. |
| `garnEftIssueAcct` | Optional[str] | Optional presence | string | ID of the checking account from which to draw CS EFT direct deposits | Preserve separately: `provider_fields.prismhr.garn_eft_issue_acct`; keep source type and nested scope. |
| `definitionId` | Optional[str] | Optional presence | string | ID of the import definition | Preserve nested/reference scope: `provider_fields.prismhr.definition_id` (Optional[str]); identifier helper, no identity substitution. |
| `cutbackCheckAcct` | Optional[str] | Optional presence | string | ID of the checking account from which to draw cutback checks | Preserve separately: `provider_fields.prismhr.cutback_check_acct`; keep source type and nested scope. |
| `broker` | Optional[str] | Optional presence | string | Broker code for the client. Brokers must be defined in the Internal Staff Codes as a Position Code K. | Preserve separately: `provider_fields.prismhr.broker`; keep source type and nested scope. |
| `onboardStatus` | Optional[str] | Optional presence | string | Deprecated. Instead, please use the attributes in enrollOnboardControls. | Preserve separately: `provider_fields.prismhr.onboard_status`; keep source type and nested scope. |
| `nyMctOvrRate` | Optional[str] | Optional presence | string | Rate based on total company payroll expense. If blank, system uses default rate to calculate the tax. | Preserve separately: `provider_fields.prismhr.ny_mct_ovr_rate`; keep source type and nested scope. |
| `naicsCode` | Optional[str] | Optional presence | string | North American Industrial Classification System code | Shared: `naics_code`. Use the agreed helper where needed; retain conversion originals/issues. |
| `benefitRep` | Optional[str] | Optional presence | string | ID of the client's benefits representative | Preserve separately: `provider_fields.prismhr.benefit_rep`; keep source type and nested scope. |
| `riskManager` | Optional[str] | Optional presence | string | ID of the client's risk manager | Preserve separately: `provider_fields.prismhr.risk_manager`; keep source type and nested scope. |
| `depositType` | Optional[str] | Optional presence | string | client deposit type, if any | Preserve separately: `provider_fields.prismhr.deposit_type`; keep source type and nested scope. |
| `depositAmt` | Optional[str] | Optional presence | string | deposit amount, if any | Preserve separately: `provider_fields.prismhr.deposit_amt`; keep source type and nested scope. |
| `handbookId` | Optional[str] | Optional presence | string | document number or code for the handbook used by the client | Preserve nested/reference scope: `provider_fields.prismhr.handbook_id` (Optional[str]); identifier helper, no identity substitution. |
| `aftPostPreMailThreshold` | Optional[str] | Optional presence | string | invoice total threshold required to place payroll on hold for the client | Preserve separately: `provider_fields.prismhr.aft_post_pre_mail_threshold`; keep source type and nested scope. |
| `achHoldThreshold` | Optional[str] | Optional presence | string | invoice total threshold required to place all ACH credits on hold for the client | Preserve separately: `provider_fields.prismhr.ach_hold_threshold`; keep source type and nested scope. |
| `taxCalcOptions` | Optional[str] | Optional presence | string | special tax calculation options | Preserve separately: `provider_fields.prismhr.tax_calc_options`; keep source type and nested scope. |
| `taxLimitBasis` | Optional[str] | Optional presence | string | Determines the taxable limit basis used for client billing: 'E' (Employer) or 'C' (Client). This overrides the flag at the global level. | Preserve separately: `provider_fields.prismhr.tax_limit_basis`; keep source type and nested scope. |
| `glTemplateCode` | Optional[str] | Optional presence | string | G/L template code used by client | Preserve separately: `provider_fields.prismhr.gl_template_code`; keep source type and nested scope. |
| `nySdiEmployerRate` | Optional[str] | Optional presence | string | premium rate (per employee/per month) paid by the employer for New York disability insurance | Preserve separately: `provider_fields.prismhr.ny_sdi_employer_rate`; keep source type and nested scope. |
| `wcPolicySubId` | Optional[str] | Optional presence | string | memo field indicating a 'sub ID' policy ID for the client | Preserve nested/reference scope: `provider_fields.prismhr.wc_policy_sub_id` (Optional[str]); identifier helper, no identity substitution. |
| `deduct401kOnSupp` | Optional[str] | Optional presence | string | indicates whether to take a 401(k) deferral on supplemental pay | Preserve separately: `provider_fields.prismhr.deduct401k_on_supp`; keep source type and nested scope. |
| `coordinator` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.prismhr.coordinator`; keep source type and nested scope. |
| `recomputeOvertime` | Optional[bool] | Optional presence | boolean | indicates whether the system recomputes overtime when fixed payment amounts such as bonuses or commission are paid in Regularly Scheduled batches | Preserve separately: `provider_fields.prismhr.recompute_overtime`; keep source type and nested scope. |
| `jobRates` | Optional[bool] | Optional presence | boolean | indicates whether the client's bill rates and pay rates are set by job code (position) | Preserve separately: `provider_fields.prismhr.job_rates`; keep source type and nested scope. |
| `remoteTechSupport` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.prismhr.remote_tech_support`; keep source type and nested scope. |
| `processingSchedule` | Optional[str] | Optional presence | string | payroll processing schedule assigned to the client | Preserve separately: `provider_fields.prismhr.processing_schedule`; keep source type and nested scope. |
| `perDiemRateSource` | Optional[bool] | Optional presence | boolean | Source record of the rate to use for Per Diems calculated using the Percentage Method: 'J' (Job Record), or 'D' or blank (Departments). | Preserve separately: `provider_fields.prismhr.per_diem_rate_source`; keep source type and nested scope. |
| `clientAccounting` | Optional[bool] | Optional presence | boolean | Indicates whether this client is getting accounting. If set to Yes, initializations will fail if all revenues are not accounted for. | Preserve separately: `provider_fields.prismhr.client_accounting`; keep source type and nested scope. |
| `adjTipShortfall` | Optional[bool] | Optional presence | boolean | indicates whether to adjust taxes to cover cash shortfall | Preserve separately: `provider_fields.prismhr.adj_tip_shortfall`; keep source type and nested scope. |
| `suppressAutoBenAdj` | Optional[bool] | Optional presence | boolean | indicates whether to suppress automatic calculation of benefit adjustments | Preserve separately: `provider_fields.prismhr.suppress_auto_ben_adj`; keep source type and nested scope. |
| `suppressEmpAch` | Optional[bool] | Optional presence | boolean | indicates whether to suppress the creation of any ACH credit transactions for any of the client's employees | Preserve separately: `provider_fields.prismhr.suppress_emp_ach`; keep source type and nested scope. |
| `singlePayGroup` | Optional[bool] | Optional presence | boolean | indicates whether to create separate payroll batches for multiple pay groups that are paid on the same day | Preserve separately: `provider_fields.prismhr.single_pay_group`; keep source type and nested scope. |
| `elecPayStub` | Optional[str] | Optional presence | string | Electronic pay stubs are 'N' not used, 'Y' employee may not unenroll, 'E' employee may unenroll | Preserve separately: `provider_fields.prismhr.elec_pay_stub`; keep source type and nested scope. |
| `useWcRateTemplate` | Optional[bool] | Optional presence | boolean | indicates whether to use table-based rate templates instead of the traditional method when calculating worker's comp for this client | Preserve separately: `provider_fields.prismhr.use_wc_rate_template`; keep source type and nested scope. |
| `calcWcOn1099Emp` | Optional[bool] | Optional presence | boolean | indicates whether to calculate worker's comp for 1099 employees | Preserve separately: `provider_fields.prismhr.calc_wc_on1099_emp`; keep source type and nested scope. |
| `wvUseFedMinRate` | Optional[bool] | Optional presence | boolean | indicates whether the client is subject only to the federal minimum wage; only applies to West Virginia work states | Preserve separately: `provider_fields.prismhr.wv_use_fed_min_rate`; keep source type and nested scope. |
| `elecW2Form` | Optional[bool] | Optional presence | boolean | indicates whether all employees will receive electronic W-2 forms | Preserve separately: `provider_fields.prismhr.elec_w2_form`; keep source type and nested scope. |
| `nySdiEmployerCalc` | Optional[bool] | Optional presence | boolean | indicates whether the system should calculate employer-paid New York disability tax for each employee | Preserve separately: `provider_fields.prismhr.ny_sdi_employer_calc`; keep source type and nested scope. |
| `pfmlMa1099` | Optional[bool] | Optional presence | boolean | whether the employee is a 1099 contractor in Massachusetts and therefore subject to paid family and medical leave (PFML) tax withholdings; if true, the system accrues and bills these taxes to the employer | Preserve separately: `provider_fields.prismhr.pfml_ma1099`; keep source type and nested scope. |
| `railRoadEmployer` | Optional[bool] | Optional presence | boolean | whether the client is a railroad employer, which significantly affects tax calculation; see the PrismHR documentation for details | Preserve separately: `provider_fields.prismhr.rail_road_employer`; keep source type and nested scope. |
| `taxGeoCodeOverride` | Optional[str] | Optional presence | string | indicates the Vertex GeoCode the system will use for tax calculations instead of the default; allowed options are empty string (no override), "R" (Override Work GeoCode with Resident GeoCode), "H" (Override Work Geocode with Home Location GeoCode), "T" (Override T/S GeoCode with Resident GeoCode); see the PrismHR help for details | Preserve separately: `provider_fields.prismhr.tax_geo_code_override`; keep source type and nested scope. |
| `adjTipsToMin` | Optional[bool] | Optional presence | boolean | indicates whether the system should adjust reported tips to meet minimum wage level | Preserve separately: `provider_fields.prismhr.adj_tips_to_min`; keep source type and nested scope. |
| `doNotService` | Optional[bool] | Optional presence | boolean | indicates whether to disable payroll processing | Preserve separately: `provider_fields.prismhr.do_not_service`; keep source type and nested scope. |
| `clientModDiscount` | Optional[bool] | Optional presence | boolean | indicates whether to use the W/C Accrual Modifiers found at the client level when calculating worker's comp liability | Preserve separately: `provider_fields.prismhr.client_mod_discount`; keep source type and nested scope. |
| `aftPostPreMailHold` | Optional[bool] | Optional presence | boolean | indicates whether to hold items based on aftPostPreMailThreshold | Preserve separately: `provider_fields.prismhr.aft_post_pre_mail_hold`; keep source type and nested scope. |
| `clientHdhp` | Optional[bool] | Optional presence | boolean | indicates whether the client maintains HDHP for their employees, and whether to suppress the system's validation when setting up an employee HSA | Preserve separately: `provider_fields.prismhr.client_hdhp`; keep source type and nested scope. |
| `financialInst` | Optional[bool] | Optional presence | boolean | indicates whether the client is a financial institution | Preserve separately: `provider_fields.prismhr.financial_inst`; keep source type and nested scope. |
| `newHireOnBoard` | Optional[bool] | Optional presence | boolean | Deprecated. Instead, please use the attributes in enrollOnboardControls. indicates whether new hire electronic onboarding is available | Preserve separately: `provider_fields.prismhr.new_hire_on_board`; keep source type and nested scope. |
| `newHireBenEnroll` | Optional[bool] | Optional presence | boolean | Deprecated. Instead, please use the attributes in enrollOnboardControls. indicates whether electronic benefits enrollment is available | Preserve separately: `provider_fields.prismhr.new_hire_ben_enroll`; keep source type and nested scope. |
| `paperlessDelivery` | Optional[str] | Optional presence | string | indicates whether the client receives hard-copy checks or invoices/reports; must be one of these values: 'N' = Inactive (no paperless delivery; print everything for the client (default value for new clients), 'Y' = All payroll output (client receives all payroll output (invoices, reports, etc.) electronically, therefore do not specify deliveryMethod), 'C' = Checks/advices only (client receives checks and advices electronically, and printed invoices and reports), 'R' = Invoice/reports only (client receives invoices(s) and reports electronically and printed checks and advices), 'D' = All Payroll Output, Delivery Sheet only. | Preserve separately: `provider_fields.prismhr.paperless_delivery`; keep source type and nested scope. |
| `clientAgrmtRecvDate` | Optional[str] | Optional presence | string / date | the date when the client agreement was received | Preserve separately: `provider_fields.prismhr.client_agrmt_recv_date` (Optional[date]); date helper, source originals/issues retained. |
| `depositDate` | Optional[str] | Optional presence | string / date | the date of the deposit | Preserve separately: `provider_fields.prismhr.deposit_date` (Optional[date]); date helper, source originals/issues retained. |
| `invoiceNotes` | Optional[List[str]] | Optional presence | array | notes to print on each invoice | Preserve separately: `provider_fields.prismhr.invoice_notes`; keep source type and nested scope. |
| `faxBackNotes` | Optional[List[str]] | Optional presence | array | notes specific to the client that should print on each Fax Back Report | Preserve separately: `provider_fields.prismhr.fax_back_notes`; keep source type and nested scope. |
| `featureCode` | Optional[List[str]] | Optional presence | array | custom feature codes that apply to the client | Preserve separately: `provider_fields.prismhr.feature_code`; keep source type and nested scope. |
| `achStatus` | Optional[str] | Optional presence | string | indicates the ACH (direct deposit) status for the client: A (active), I (inactive), L (ACH by client location; set up in PrismHR), D (ACH by client division; set up in PrismHR), W (wire transfer client), P (prenote; ACH not yet active), or E (EDI client; specialized usage) | Preserve separately: `provider_fields.prismhr.ach_status`; keep source type and nested scope. |
| `eligibleBenefitsDeterminant` | Optional[str] | Optional presence | string | indicates whether to make benefits available to an employee based on department (“D”), division (“V”), location (“L”), or benefit group (“B”). If this field is empty then All Plans are Eligible. Based on this determining factor, the system checks which benefits employees are eligible for. | Preserve separately: `provider_fields.prismhr.eligible_benefits_determinant`; keep source type and nested scope. |
| `wcResidentBased` | Optional[bool] | Optional presence | boolean | if true, indicates that the W/C Calculation Option field is set to Resident State Based; if the employee’s Worksite Location is marked as a “Remote Location”, the system associates the employee with their resident GeoCode during Workers' Compensation calculations | Preserve separately: `provider_fields.prismhr.wc_resident_based`; keep source type and nested scope. |
| `relatedCode` | Optional[str] | Optional presence | string | corresponds to the Related Code field in the Other tab of Client Details | Preserve separately: `provider_fields.prismhr.related_code`; keep source type and nested scope. |
| `instantPayAccount` | Optional[str] | Optional presence | string | checking account that is configured to use the ACH originator associated with the Instant Pay format; required if Instant Pay features are enabled for this client | Preserve separately: `provider_fields.prismhr.instant_pay_account`; keep source type and nested scope. |
| `remoteVerification` | Optional[str] | Optional presence | string | whether to enable Form I-9 remote verification for this client | Preserve separately: `provider_fields.prismhr.remote_verification`; keep source type and nested scope. |
| `statusClass` | Optional[str] | Optional presence | string | client status class, associated with the client status; “A” (Active), “P” (Pending), “I” (Inactive), “C” (Client Cancelling, Pre-Termination) and “T” (Terminated) | Preserve separately: `provider_fields.prismhr.status_class` (Optional[str]); exact documented class labels below; originals retained. |
| `selfServicePayroll` | Optional[str] | Optional presence | string | whether the client processes its own payrolls ("Y" or "N"); "Y" is not allowed if worksiteTimeSheetEntry = "Y" | Preserve separately: `provider_fields.prismhr.self_service_payroll`; keep source type and nested scope. |
| `selfServiceRestrictions` | Optional[str] | Optional presence | string | indicates the payroll actions the client cannot perform; valid values are "1" (Print) and "2" (Finalize and Print); this field can only be updated if selfServicePayroll = "Y" | Preserve separately: `provider_fields.prismhr.self_service_restrictions`; keep source type and nested scope. |
| `worksiteTimesheetEntry` | Optional[str] | Optional presence | string | "Y" if users at the worksite location enter time sheet information; "N" or empty otherwise. "Y" is not allowed if selfServicePayroll = "Y". | Preserve separately: `provider_fields.prismhr.worksite_timesheet_entry`; keep source type and nested scope. |
| `allowFirstPeriodHours` | Optional[str] | Optional presence | string | whether you can enter prorated hours for new hire employees with start dates that fall within the current pay period; the First Period Hours feature must be enabled in System Parameters in order to update this field; allowed values are empty string (use system default), "E" (enabled), and "D" (disabled) | Preserve separately: `provider_fields.prismhr.allow_first_period_hours`; keep source type and nested scope. |
| `enableInstantPay` | Optional[bool] | Optional presence | boolean | indicates if Instant Pay feature is enabled for the client | Preserve separately: `provider_fields.prismhr.enable_instant_pay`; keep source type and nested scope. |
| `nextEmployeeNumber` | Optional[str] | Optional presence | string | the next ID number to automatically assign to a new hire for this client; updates are only allowed if autoEmpNumber = "Y" | Preserve separately: `provider_fields.prismhr.next_employee_number`; keep source type and nested scope. |
| `altEmployer` | Optional[List[PrismHRAltEmployer]] | Optional presence | array | object containing information on alternate employer(s), if any | Preserve separately: `provider_fields.prismhr.alt_employer`; keep source type and nested scope. |
| `retire` | Optional[List[PrismHRClientRetirementPlanObject]] | Optional presence | array | object containing retirement details | Preserve separately: `provider_fields.prismhr.retire`; keep source type and nested scope. |
| `billFixed` | Optional[List[PrismHRBillFixed]] | Optional presence | array | billing rate override | Preserve separately: `provider_fields.prismhr.bill_fixed`; keep source type and nested scope. |
| `holidayPay` | Optional[List[PrismHRHolidayPay]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.prismhr.holiday_pay`; keep source type and nested scope. |
| `sdiDedn` | Optional[List[PrismHRSdiDedn]] | Optional presence | array | state disability insurance tax deduction information | Preserve separately: `provider_fields.prismhr.sdi_dedn`; keep source type and nested scope. |
| `clientTax` | Optional[List[PrismHRClientMasterClientTax]] | Optional presence | array | client tax settings | Preserve separately: `provider_fields.prismhr.client_tax`; keep source type and nested scope. |
| `redir` | Optional[List[PrismHRRedir]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.prismhr.redir`; keep source type and nested scope. |
| `regRebuild` | Optional[List[PrismHRRegRebuild]] | Optional presence | array | No property description supplied. | Preserve separately: `provider_fields.prismhr.reg_rebuild`; keep source type and nested scope. |
| `commission` | Optional[List[PrismHRCommission]] | Optional presence | array | client commission information | Preserve separately: `provider_fields.prismhr.commission`; keep source type and nested scope. |
| `billEvent` | Optional[List[PrismHRBillEvent]] | Optional presence | array | billing events | Preserve separately: `provider_fields.prismhr.bill_event`; keep source type and nested scope. |
| `reportFee` | Optional[List[PrismHRReportFee]] | Optional presence | array | special reports to print for the client, or standard report to omit | Preserve separately: `provider_fields.prismhr.report_fee`; keep source type and nested scope. |
| `i9Approver` | Optional[str] | Optional presence | string | Id of the user responsible for I9 approval | Preserve separately: `provider_fields.prismhr.i9_approver`; keep source type and nested scope. |
| `printMailUser` | Optional[str] | Optional presence | string | Print/Mail User ID; user must be a Service Provider with Account Management Role “PN”; in addition, the “Separate Print/Ship Functions” setting must be enabled at the system level | Preserve separately: `provider_fields.prismhr.print_mail_user`; keep source type and nested scope. |
| `contractorsAllowed1099` | Optional[bool] | Optional presence | boolean | indicates whether client employs 1099 contractors | Preserve separately: `provider_fields.prismhr.contractors_allowed1099`; keep source type and nested scope. |
| `billPendingLocation` | Optional[str] | Optional presence | string | worksite location ID for client bill pending | Preserve separately: `provider_fields.prismhr.bill_pending_location`; keep source type and nested scope. |
| `benefitsGoodThroughDate` | Optional[str] | Optional presence | string | expiration date for the benefit rules set up for the client | Preserve separately: `provider_fields.prismhr.benefits_good_through_date` (Optional[date]); date helper, source originals/issues retained. |
| `achMax` | Optional[str] | Optional presence | string | the maximum allowable ACH amount to enforce a threshold amount requiring ACH approval | Preserve separately: `provider_fields.prismhr.ach_max`; keep source type and nested scope. |
| `checksum` | Optional[str] | Optional presence | string | checksum to use for updates | Preserve separately: `provider_fields.prismhr.checksum`; keep source type and nested scope. |
| `clientStatusChecksum` | Optional[str] | Optional presence | string | checksum to use for client status updates | Preserve separately: `provider_fields.prismhr.client_status_checksum`; keep source type and nested scope. |
| `mySupportTeamDashboard` | Optional[List[PrismHRMySupportTeamDashboard]] | Optional presence | array | Custom functionality. Details the client's support team member responsibilities with user-configured field names. | Preserve separately: `provider_fields.prismhr.my_support_team_dashboard`; keep source type and nested scope. |
| `enrollOnboardControls` | Optional[PrismHREnrollOnboardControls] | Optional presence | #/components/schemas/EnrollOnboardControls | No property description supplied. | Preserve separately: `provider_fields.prismhr.enroll_onboard_controls`; keep source type and nested scope. |
| `everify` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.prismhr.everify`; keep source type and nested scope. |
| `reverseWireAccount` | Optional[str] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Preserve separately: `provider_fields.prismhr.reverse_wire_account`; keep source type and nested scope. |
| `payrollFinalizationNotification` | Optional[str] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Preserve separately: `provider_fields.prismhr.payroll_finalization_notification`; keep source type and nested scope. |
| `notificationEmailList` | Optional[List[Any]] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Preserve separately: `provider_fields.prismhr.notification_email_list`; keep source type and nested scope. |
| `positionRatesUsed` | Optional[str] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Preserve separately: `provider_fields.prismhr.position_rates_used`; keep source type and nested scope. |
| `eVerify` | Optional[bool] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Preserve separately: `provider_fields.prismhr.e_verify`; keep source type and nested scope. |
| `externalPtoUsed` | Optional[bool] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Preserve separately: `provider_fields.prismhr.external_pto_used`; keep source type and nested scope. |
| `taxesToSuppress` | Optional[List[Any]] | Optional presence | Not supplied at this path | Project container or live/sample addition; not documented at this schema path. | Preserve separately: `provider_fields.prismhr.taxes_to_suppress`; keep source type and nested scope. |

#### PrismHRGetClientMasterResponse

[Source model](../../../src/normalization/source_models/prismhr/prismhr_source_model_company.py) · [Contract schema](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json#/components/schemas/GetClientMasterResponse).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `errorCode` | str | Required presence | string | No property description supplied. | Metadata: `source_metadata.prismhr.response`; retain field/nesting. |
| `errorMessage` | str | Required presence | string | No property description supplied. | Metadata: `source_metadata.prismhr.response`; retain field/nesting. |
| `extension` | Optional[PrismHRExtension] | Optional presence | #/components/schemas/Extension | No property description supplied. | Metadata: `source_metadata.prismhr.response`; retain field/nesting. |
| `clientMaster` | Optional[PrismHRClientMaster] | Optional presence | #/components/schemas/ClientMaster | No property description supplied. | Container: validate/map each supplied source record; preserve other wrapper fields separately. |

### isolved

#### IsolvedBaseLinkModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_payroll_run.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.Base.LinkModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `href` | Optional[str] | Optional presence | string | Hyperlink to linked entity or action | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |
| `method` | Optional[str] | Optional presence | string | HTTP Method for linked entity or action | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |
| `rel` | Optional[str] | Optional presence | string | Relationship or purpose of link to enclosing entity | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedClientPayRateModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.ClientPayRateModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Preserve nested/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, no identity substitution. |
| `payRateName` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.pay_rate_name`; keep source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedOptionValueModelOfString

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_employee.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.OptionValueModelOfString).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[str] | Required presence | string | Unique Object Id | Preserve nested/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, no identity substitution. |
| `description` | Optional[str] | Optional presence | string | Description of the option value. | Preserve separately: `provider_fields.isolved.description`; keep source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedClientChangeReasonModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.ClientChangeReasonModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique identifier of the change reason. | Preserve nested/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, no identity substitution. |
| `changeReasonType` | Optional[IsolvedOptionValueModelOfString] | Optional presence | #/definitions/AOS.PayrollOffice.RestAPI.Models.OptionValueModelOfString | Change reason type. | Preserve separately: `provider_fields.isolved.change_reason_type`; keep source type and nested scope. |
| `code` | Optional[str] | Optional presence | string | Change reason code | Preserve separately: `provider_fields.isolved.code`; keep source type and nested scope. |
| `description` | Optional[str] | Optional presence | string | Change reason description. | Preserve separately: `provider_fields.isolved.description`; keep source type and nested scope. |

#### IsolvedClientContactModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.ClientContactModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Preserve nested/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, no identity substitution. |
| `alternatePhoneNumber` | Optional[str] | Optional presence | string | Contact Alternate Phone Number | Preserve separately: `provider_fields.isolved.alternate_phone_number`; keep source type and nested scope. |
| `emailAddress` | Optional[str] | Optional presence | string | Contact Email Address | Preserve separately: `provider_fields.isolved.email_address`; keep source type and nested scope. |
| `faxNumber` | Optional[str] | Optional presence | string | Contact Fax Number | Preserve separately: `provider_fields.isolved.fax_number`; keep source type and nested scope. |
| `firstName` | Optional[str] | Optional presence | string | Contact First Name | Preserve separately: `provider_fields.isolved.first_name`; keep source type and nested scope. |
| `inactiveDate` | Optional[str] | Optional presence | string / date-time | Contact inactive date | Preserve separately: `provider_fields.isolved.inactive_date` (Optional[date]); date helper, source originals/issues retained. |
| `lastName` | Optional[str] | Optional presence | string | Contact Last Name | Preserve separately: `provider_fields.isolved.last_name`; keep source type and nested scope. |
| `mobilePhoneNumber` | Optional[str] | Optional presence | string | Contact Mobile Phone Number | Preserve separately: `provider_fields.isolved.mobile_phone_number`; keep source type and nested scope. |
| `phoneNumber` | Optional[str] | Optional presence | string | Contact Phone Number | Preserve separately: `provider_fields.isolved.phone_number`; keep source type and nested scope. |
| `profilePicture` | Optional[str] | Optional presence | string / byte | Contact Profile Picture | Preserve separately: `provider_fields.isolved.profile_picture`; keep source type and nested scope. |
| `title` | Optional[str] | Optional presence | string | Contact Title | Preserve separately: `provider_fields.isolved.title`; keep source type and nested scope. |
| `type` | Optional[List[str]] | Optional presence | array | Array of contact types for this contact | Preserve separately: `provider_fields.isolved.type`; keep source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedClientEmploymentCategoryModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.ClientEmploymentCategoryModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Preserve nested/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, no identity substitution. |
| `acaEmploymentStatus` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.aca_employment_status`; keep source type and nested scope. |
| `code` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.code`; keep source type and nested scope. |
| `description` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.description`; keep source type and nested scope. |
| `isInactive` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.isolved.is_inactive`; keep source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedPayrollStatusModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.PayrollStatusModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[str] | Required presence | string | Unique Object Id | Preserve nested/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, no identity substitution. |
| `statusDescription` | Optional[str] | Optional presence | string | A short title for payroll status | Preserve separately: `provider_fields.isolved.status_description`; keep source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedClientEmploymentStatusModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.ClientEmploymentStatusModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Preserve nested/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, no identity substitution. |
| `code` | Optional[str] | Optional presence | string | Unique code for client employment status | Preserve separately: `provider_fields.isolved.code`; keep source type and nested scope. |
| `payrollStatus` | Optional[IsolvedPayrollStatusModel] | Optional presence | #/definitions/AOS.PayrollOffice.RestAPI.Models.PayrollStatusModel | An object that holds a system's payroll status | Preserve separately: `provider_fields.isolved.payroll_status`; keep source type and nested scope. |
| `statusDescription` | Optional[str] | Optional presence | string | A short title for client employment status | Preserve separately: `provider_fields.isolved.status_description`; keep source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedClientJobModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.ClientJobModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Preserve nested/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, no identity substitution. |
| `eeoCategory` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.eeo_category`; keep source type and nested scope. |
| `isFLSAExempt` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.isolved.is_flsa_exempt`; keep source type and nested scope. |
| `isInactive` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.isolved.is_inactive`; keep source type and nested scope. |
| `isManagerJob` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.isolved.is_manager_job`; keep source type and nested scope. |
| `isSeasonal` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.isolved.is_seasonal`; keep source type and nested scope. |
| `isSupervisorJob` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.isolved.is_supervisor_job`; keep source type and nested scope. |
| `isUnion` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.isolved.is_union`; keep source type and nested scope. |
| `jobCode` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.job_code`; keep source type and nested scope. |
| `jobGroup` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.job_group`; keep source type and nested scope. |
| `jobTitle` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.job_title`; keep source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedClientLaborFieldLookupModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.ClientLaborFieldLookupModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `address1` | Optional[str] | Optional presence | string | Optional lookup street address line 1 | Preserve separately: `provider_fields.isolved.address1`; keep source type and nested scope. |
| `address2` | Optional[str] | Optional presence | string | Optional lookup street address line 2 | Preserve separately: `provider_fields.isolved.address2`; keep source type and nested scope. |
| `beginDate` | Optional[str] | Optional presence | string / date-time | Optional begin date of the lookup | Preserve separately: `provider_fields.isolved.begin_date` (Optional[date]); date helper, source originals/issues retained. |
| `city` | Optional[str] | Optional presence | string | Optional lookup street address city | Preserve separately: `provider_fields.isolved.city`; keep source type and nested scope. |
| `code` | Optional[str] | Optional presence | string | Lookup item code | Preserve separately: `provider_fields.isolved.code`; keep source type and nested scope. |
| `description` | Optional[str] | Optional presence | string | Lookup item description | Preserve separately: `provider_fields.isolved.description`; keep source type and nested scope. |
| `endDate` | Optional[str] | Optional presence | string / date-time | Optional end date of the lookup | Preserve separately: `provider_fields.isolved.end_date` (Optional[date]); date helper, source originals/issues retained. |
| `isCertified` | Optional[bool] | Optional presence | boolean | A flag indicating if the lookup is certified | Preserve separately: `provider_fields.isolved.is_certified`; keep source type and nested scope. |
| `isInactive` | Optional[bool] | Optional presence | boolean | A flag indicating if the lookup is marked as inactive | Preserve separately: `provider_fields.isolved.is_inactive`; keep source type and nested scope. |
| `projectLocation` | Optional[str] | Optional presence | string | Optional project location associated with the lookup | Preserve separately: `provider_fields.isolved.project_location`; keep source type and nested scope. |
| `projectNumber` | Optional[str] | Optional presence | string | Optional project number associated with the lookup | Preserve separately: `provider_fields.isolved.project_number`; keep source type and nested scope. |
| `state` | Optional[str] | Optional presence | string | Optional lookup street address state code | Preserve separately: `provider_fields.isolved.state`; keep source type and nested scope. |
| `zipCode` | Optional[str] | Optional presence | string | Optional lookup street address zip code | Preserve separately: `provider_fields.isolved.zip_code`; keep source type and nested scope. |

#### IsolvedClientLaborFieldModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.ClientLaborFieldModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Preserve nested/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, no identity substitution. |
| `allowInTimeEntry` | Optional[bool] | Optional presence | boolean | The allow in time entry field | Preserve separately: `provider_fields.isolved.allow_in_time_entry`; keep source type and nested scope. |
| `laborTitle` | Optional[str] | Optional presence | string | The title of the labor field | Preserve separately: `provider_fields.isolved.labor_title`; keep source type and nested scope. |
| `lookups` | Optional[List[IsolvedClientLaborFieldLookupModel]] | Optional presence | array | A listing of lookup items for the labor field | Preserve separately: `provider_fields.isolved.lookups`; keep source type and nested scope. |
| `organizationFieldName` | Optional[str] | Optional presence | string | If the labor field is linked to an organization field, the name of the linked organization field | Preserve separately: `provider_fields.isolved.organization_field_name`; keep source type and nested scope. |
| `sequenceNumber` | Optional[int] | Optional presence | integer / int32 | The display sequence of the labor field | Preserve separately: `provider_fields.isolved.sequence_number`; keep source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvediSolvedDtoFrontEndOptionValueOfString

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_employee.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/iSolved.Dto.FrontEnd.OptionValueOfString).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `description` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.description`; keep source type and nested scope. |
| `id` | Optional[str] | Required presence | string | No property description supplied. | Preserve nested/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, no identity substitution. |

#### IsolvedClientMiscEmployeeFieldModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_employee.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.ClientMiscEmployeeFieldModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `category` | Optional[str] | Optional presence | string | The category of the misc field | Preserve separately: `provider_fields.isolved.category`; keep source type and nested scope. |
| `dataType` | Optional[str] | Optional presence | string | The type of the data misc field holds | Preserve separately: `provider_fields.isolved.data_type`; keep source type and nested scope. |
| `fieldCode` | Optional[str] | Optional presence | string | The alternate id to identify the misc field | Preserve separately: `provider_fields.isolved.field_code`; keep source type and nested scope. |
| `fieldTitle` | Optional[str] | Optional presence | string | The title of misc field | Preserve separately: `provider_fields.isolved.field_title`; keep source type and nested scope. |
| `lookups` | Optional[List[IsolvediSolvedDtoFrontEndOptionValueOfString]] | Optional presence | array | The lookup values a misc field may have, provided the {AOS.PayrollOffice.RestAPI.Models.ClientMiscEmployeeFieldModel.DataType} is of 'Table Lookup' type | Preserve separately: `provider_fields.isolved.lookups`; keep source type and nested scope. |

#### IsolvedClientOrganizationFieldLookupModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_employee.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.ClientOrganizationFieldLookupModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `code` | Optional[str] | Optional presence | string | The unique identifier for the organization field lookup | Preserve separately: `provider_fields.isolved.code`; keep source type and nested scope. |
| `description` | Optional[str] | Optional presence | string | Organization Field Lookup Description | Preserve separately: `provider_fields.isolved.description`; keep source type and nested scope. |
| `isInactive` | Optional[bool] | Optional presence | boolean | A flag indicating whether or not the organization field lookup is currently inactivate | Preserve separately: `provider_fields.isolved.is_inactive`; keep source type and nested scope. |

#### IsolvedClientOrganizationFieldModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.ClientOrganizationFieldModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Preserve nested/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, no identity substitution. |
| `displayOrder` | Optional[int] | Optional presence | integer / int32 | The display order of the organization field | Preserve separately: `provider_fields.isolved.display_order`; keep source type and nested scope. |
| `includeInJob` | Optional[bool] | Optional presence | boolean | A flag indicating whether or not the organization field is included in the job table | Preserve separately: `provider_fields.isolved.include_in_job`; keep source type and nested scope. |
| `isLaborField` | Optional[bool] | Optional presence | boolean | A flag indicating whether or not the organization field is also a labor field | Preserve separately: `provider_fields.isolved.is_labor_field`; keep source type and nested scope. |
| `isRequired` | Optional[bool] | Optional presence | boolean | A flag indicating the organization field is required | Preserve separately: `provider_fields.isolved.is_required`; keep source type and nested scope. |
| `isTeam` | Optional[bool] | Optional presence | boolean | A flag indicating whether or not the organization field is also a team | Preserve separately: `provider_fields.isolved.is_team`; keep source type and nested scope. |
| `lookups` | Optional[List[IsolvedClientOrganizationFieldLookupModel]] | Optional presence | array | An array of organization field lookup values | Preserve separately: `provider_fields.isolved.lookups`; keep source type and nested scope. |
| `organizationGroupId` | Optional[int] | Optional presence | integer / int32 | The Id of the organization group | Preserve nested/reference scope: `provider_fields.isolved.organization_group_id` (Optional[str]); identifier helper, no identity substitution. |
| `title` | Optional[str] | Optional presence | string | The organization field title | Preserve separately: `provider_fields.isolved.title`; keep source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedSecurityServiceGroupModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.SecurityServiceGroupModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | The ID of the security service group | Preserve nested/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, no identity substitution. |
| `name` | Optional[str] | Optional presence | string | Name of the security service group | Preserve separately: `provider_fields.isolved.name`; keep source type and nested scope. |

#### IsolvedClientModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.ClientModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Preserve nested/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, no identity substitution. |
| `alternatePayRates` | Optional[List[IsolvedClientPayRateModel]] | Optional presence | array | Listing of alternate pay rates defined for this client | Preserve separately: `provider_fields.isolved.alternate_pay_rates`; keep source type and nested scope. |
| `changeReasons` | Optional[List[IsolvedClientChangeReasonModel]] | Optional presence | array | Listing of change reasons for this client | Preserve separately: `provider_fields.isolved.change_reasons`; keep source type and nested scope. |
| `clientCode` | Optional[str] | Optional presence | string | Client Code | Preserve separately: `provider_fields.isolved.client_code`; keep source type and nested scope. |
| `clientName` | Optional[str] | Optional presence | string | The name of the client | Preserve separately: `provider_fields.isolved.client_name`; keep source type and nested scope. |
| `contacts` | Optional[List[IsolvedClientContactModel]] | Optional presence | array | Listing of contacts for this client | Preserve separately: `provider_fields.isolved.contacts`; keep source type and nested scope. |
| `employmentCategories` | Optional[List[IsolvedClientEmploymentCategoryModel]] | Optional presence | array | Listing of employment categories defined for this client | Preserve separately: `provider_fields.isolved.employment_categories`; keep source type and nested scope. |
| `employmentStatuses` | Optional[List[IsolvedClientEmploymentStatusModel]] | Optional presence | array | Listing of employment statuses defined for this client | Preserve separately: `provider_fields.isolved.employment_statuses`; keep source type and nested scope. |
| `jobs` | Optional[List[IsolvedClientJobModel]] | Optional presence | array | Listing of jobs defined defined for this client | Preserve separately: `provider_fields.isolved.jobs`; keep source type and nested scope. |
| `labors` | Optional[List[IsolvedClientLaborFieldModel]] | Optional presence | array | Listing of client labor fields for this client | Preserve separately: `provider_fields.isolved.labors`; keep source type and nested scope. |
| `legalCompanies` | Optional[List[IsolvedLegalModel]] | Optional presence | array | Listing of legal companies within this client | Preserve separately: `provider_fields.isolved.legal_companies`; keep source type and nested scope. |
| `miscEmployeeFields` | Optional[List[IsolvedClientMiscEmployeeFieldModel]] | Optional presence | array | Listing of misc employee fields for this client | Preserve separately: `provider_fields.isolved.misc_employee_fields`; keep source type and nested scope. |
| `organizations` | Optional[List[IsolvedClientOrganizationFieldModel]] | Optional presence | array | Listing of client organization fields for this client | Preserve separately: `provider_fields.isolved.organizations`; keep source type and nested scope. |
| `securityServiceGroup` | Optional[IsolvedSecurityServiceGroupModel] | Optional presence | #/definitions/AOS.PayrollOffice.RestAPI.Models.SecurityServiceGroupModel | The security service group of the client | Preserve separately: `provider_fields.isolved.security_service_group`; keep source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedLegalModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.LegalModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Shared: `source_record_id`. Use the agreed helper where needed; retain conversion originals/issues. |
| `allowRemoteWorkers` | Optional[bool] | Optional presence | boolean | Does the legal company allow remote workers. | Preserve separately: `provider_fields.isolved.allow_remote_workers`; keep source type and nested scope. |
| `client` | Optional[IsolvedClientModel] | Optional presence | #/definitions/AOS.PayrollOffice.RestAPI.Models.ClientModel | Parent client entity | Preserve separately: `provider_fields.isolved.client`; keep source type and nested scope. |
| `compensationPlans` | Optional[List[IsolvedLegalCompensationPlanModel]] | Optional presence | array | Compensations plans for the legal. | Preserve separately: `provider_fields.isolved.compensation_plans`; keep source type and nested scope. |
| `dbaName` | Optional[str] | Optional presence | string | DBA Name | Shared: `trade_name`. Use the agreed helper where needed; retain conversion originals/issues. |
| `federalEIN` | Optional[str] | Optional presence | string | Federal Employer Identification Number | Shared: `federal_tax_id`. Use the agreed helper where needed; retain conversion originals/issues. |
| `forceDirectDepositPrenote` | Optional[bool] | Optional presence | boolean | A flag that indicates forcing a prenote for new or changed direct deposits | Preserve separately: `provider_fields.isolved.force_direct_deposit_prenote`; keep source type and nested scope. |
| `iSolvedTimeEnabled` | Optional[bool] | Optional presence | boolean | A flag that indicates the isolved time service is enabled | Preserve separately: `provider_fields.isolved.i_solved_time_enabled`; keep source type and nested scope. |
| `legalAddress` | Optional[IsolvedClientAddressModel] | Optional presence | #/definitions/AOS.PayrollOffice.RestAPI.Models.ClientAddressModel | Legal company address | Preserve separately: `provider_fields.isolved.legal_address`; keep source type and nested scope. |
| `legalCode` | Optional[str] | Optional presence | string | Legal Code (Alternate Id) | Preserve separately: `provider_fields.isolved.legal_code`; keep source type and nested scope. |
| `legalName` | Optional[str] | Optional presence | string | Legal name | Shared: `legal_name`. Use the agreed helper where needed; retain conversion originals/issues. |
| `logoData` | Optional[str] | Optional presence | string / byte | Legal logo data (Byte Array) | Preserve separately: `provider_fields.isolved.logo_data`; keep source type and nested scope. |
| `naicsCode` | Optional[str] | Optional presence | string | North American Industry Classification System Code | Shared: `naics_code`. Use the agreed helper where needed; retain conversion originals/issues. |
| `payGroups` | Optional[List[IsolvedPayGroupModel]] | Optional presence | array | Listing of pay groups defined within this legal company | Preserve separately: `provider_fields.isolved.pay_groups`; keep source type and nested scope. |
| `services` | Optional[List[IsolvedLegalServiceModel]] | Optional presence | array | List of active legal services for the current legal. This property is read-only. | Preserve separately: `provider_fields.isolved.services`; keep source type and nested scope. |
| `status` | Optional[str] | Optional presence | string | Current Legal Company Status | Preserve separately: `provider_fields.isolved.status`; keep source type and nested scope. |
| `workersComps` | Optional[List[IsolvedLegalWorkersCompModel]] | Optional presence | array | Listing of configured Workers Compensation codes defined within this legal company | Preserve separately: `provider_fields.isolved.workers_comps`; keep source type and nested scope. |
| `workLocations` | Optional[List[IsolvedLegalWorkLocationModel]] | Optional presence | array | Listing of work locations defined within this legal company | Preserve separately: `provider_fields.isolved.work_locations`; keep source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedLegalCompensationPlanModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.LegalCompensationPlanModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique identifier for the compensation plan. | Preserve nested/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, no identity substitution. |
| `code` | Optional[str] | Optional presence | string | Code for the compensation plan. | Preserve separately: `provider_fields.isolved.code`; keep source type and nested scope. |
| `description` | Optional[str] | Optional presence | string | Description of the compensation plan. | Preserve separately: `provider_fields.isolved.description`; keep source type and nested scope. |

#### IsolvedClientAddressModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.ClientAddressModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `addressDescription` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.address_description`; keep source type and nested scope. |
| `city` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.city`; keep source type and nested scope. |
| `phoneNumber` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.phone_number`; keep source type and nested scope. |
| `state` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.state`; keep source type and nested scope. |
| `streetAddress1` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.street_address1`; keep source type and nested scope. |
| `streetAddress2` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.street_address2`; keep source type and nested scope. |
| `zipCode` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.zip_code`; keep source type and nested scope. |

#### IsolvedPayGroupModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.PayGroupModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Preserve nested/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, no identity substitution. |
| `enableiSolvedPayroll` | Optional[bool] | Optional presence | boolean | A flag that indicates iSolved Payroll is enabled | Preserve separately: `provider_fields.isolved.enablei_solved_payroll`; keep source type and nested scope. |
| `enableiSolvedTime` | Optional[bool] | Optional presence | boolean | A flag that indicates iSolved Time is enabled | Preserve separately: `provider_fields.isolved.enablei_solved_time`; keep source type and nested scope. |
| `inputMethod` | Optional[str] | Optional presence | string | Payroll Input Method | Preserve separately: `provider_fields.isolved.input_method`; keep source type and nested scope. |
| `isInactive` | Optional[bool] | Optional presence | boolean | A flag that indicates the paygroup is inactive | Preserve separately: `provider_fields.isolved.is_inactive`; keep source type and nested scope. |
| `legal` | Optional[IsolvedLegalModel] | Optional presence | #/definitions/AOS.PayrollOffice.RestAPI.Models.LegalModel | The parent legal company of this pay group | Preserve separately: `provider_fields.isolved.legal`; keep source type and nested scope. |
| `normalHours` | Optional[float] | Optional presence | number / double | Default normal work hours | Preserve separately: `provider_fields.isolved.normal_hours` (Optional[float]); finite number helper, retain basis/currency. |
| `payFrequency` | Optional[int] | Optional presence | integer / int32 | Pay Frequency | Preserve separately: `provider_fields.isolved.pay_frequency`; keep source type and nested scope. |
| `payGroupName` | Optional[str] | Optional presence | string | Pay Group Name | Preserve separately: `provider_fields.isolved.pay_group_name`; keep source type and nested scope. |
| `payrollType` | Optional[str] | Optional presence | string | Payroll Type | Preserve separately: `provider_fields.isolved.payroll_type`; keep source type and nested scope. |
| `printCenter` | Optional[IsolvedSystemPrintCenterModel] | Optional presence | #/definitions/AOS.PayrollOffice.RestAPI.Models.SystemPrintCenterModel | The specified print center for this pay group | Preserve separately: `provider_fields.isolved.print_center`; keep source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedSystemPrintCenterModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.SystemPrintCenterModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Preserve nested/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, no identity substitution. |
| `allowTaxFilingPrint` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.isolved.allow_tax_filing_print`; keep source type and nested scope. |
| `allowYearEndPrint` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.isolved.allow_year_end_print`; keep source type and nested scope. |
| `isChanged` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.isolved.is_changed`; keep source type and nested scope. |
| `isDeleted` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.isolved.is_deleted`; keep source type and nested scope. |
| `isLocalPrintCenter` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.isolved.is_local_print_center`; keep source type and nested scope. |
| `isNew` | Optional[bool] | Optional presence | boolean | No property description supplied. | Preserve separately: `provider_fields.isolved.is_new`; keep source type and nested scope. |
| `printCenterDescription` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.isolved.print_center_description`; keep source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedLegalServiceModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.LegalServiceModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `code` | Optional[str] | Optional presence | string | Unique identifier for the service. | Preserve separately: `provider_fields.isolved.code`; keep source type and nested scope. |
| `startDate` | Optional[str] | Optional presence | string / date-time | Date in which the legal service was made active. If this date is in the future the service is not active. | Preserve separately: `provider_fields.isolved.start_date` (Optional[date]); date helper, source originals/issues retained. |
| `endDate` | Optional[str] | Optional presence | string / date-time | Date in which the legal service will no longer be active. If not provided the service will remain active indefinitely. | Preserve separately: `provider_fields.isolved.end_date` (Optional[date]); date helper, source originals/issues retained. |

#### IsolvedLegalWorkersCompModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.LegalWorkersCompModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `isInactive` | Optional[bool] | Optional presence | boolean | If the worker's compensation is inactive. | Preserve separately: `provider_fields.isolved.is_inactive`; keep source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Links | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |
| `state` | Optional[str] | Optional presence | string | State | Preserve separately: `provider_fields.isolved.state`; keep source type and nested scope. |
| `workersCompCode` | Optional[str] | Optional presence | string | Workers compensation code | Preserve separately: `provider_fields.isolved.workers_comp_code`; keep source type and nested scope. |
| `workersCompDescription` | Optional[str] | Optional presence | string | Workers compensation description | Preserve separately: `provider_fields.isolved.workers_comp_description`; keep source type and nested scope. |
| `workersCompId` | Optional[int] | Optional presence | integer / int32 | Unique identifier of the system worker's compensation code. | Preserve nested/reference scope: `provider_fields.isolved.workers_comp_id` (Optional[str]); identifier helper, no identity substitution. |

#### IsolvedLegalWorkLocationModel

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_company.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.LegalWorkLocationModel).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Preserve nested/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, no identity substitution. |
| `address1` | Optional[str] | Optional presence | string | Address Line One | Preserve separately: `provider_fields.isolved.address1`; keep source type and nested scope. |
| `address2` | Optional[str] | Optional presence | string | Address Line 2 | Preserve separately: `provider_fields.isolved.address2`; keep source type and nested scope. |
| `addressDescription` | Optional[str] | Optional presence | string | Address Description | Preserve separately: `provider_fields.isolved.address_description`; keep source type and nested scope. |
| `city` | Optional[str] | Optional presence | string | Address City Name | Preserve separately: `provider_fields.isolved.city`; keep source type and nested scope. |
| `existingAddressId` | Optional[int] | Optional presence | integer / int32 | Existing Client Address Id to be used for POST if applicable. | Preserve nested/reference scope: `provider_fields.isolved.existing_address_id` (Optional[str]); identifier helper, no identity substitution. |
| `geoCode` | Optional[str] | Optional presence | string | Vertex Geo Code (Tax Location Code in the UI) | Preserve separately: `provider_fields.isolved.geo_code`; keep source type and nested scope. |
| `includeWorkSiteTaxFiling` | Optional[bool] | Optional presence | boolean | Include Worksite for Tax Filing Flag | Preserve separately: `provider_fields.isolved.include_work_site_tax_filing`; keep source type and nested scope. |
| `isInactive` | Optional[bool] | Optional presence | boolean | A Flag Indicating If This Work Location Is Inactive | Preserve separately: `provider_fields.isolved.is_inactive`; keep source type and nested scope. |
| `isRemoteWorkersOnly` | Optional[bool] | Optional presence | boolean | Worksite for Remote Workers only Flag | Preserve separately: `provider_fields.isolved.is_remote_workers_only`; keep source type and nested scope. |
| `minimumWageRule` | Optional[IsolvedOptionValueModelOfInt32] | Optional presence | #/definitions/AOS.PayrollOffice.RestAPI.Models.OptionValueModelOfInt32 | Minimum Wage Rule | Preserve separately: `provider_fields.isolved.minimum_wage_rule`; keep source type and nested scope. |
| `overrideTaxCode` | Optional[str] | Optional presence | string | Override Tax Code | Preserve separately: `provider_fields.isolved.override_tax_code`; keep source type and nested scope. |
| `reportingUnitNumber` | Optional[int] | Optional presence | integer / int32 | Reporting Unit Number | Preserve separately: `provider_fields.isolved.reporting_unit_number`; keep source type and nested scope. |
| `schoolDistrictCode` | Optional[int] | Optional presence | integer / int32 | School District Code | Preserve separately: `provider_fields.isolved.school_district_code`; keep source type and nested scope. |
| `state` | Optional[str] | Optional presence | string | Address State Id | Preserve separately: `provider_fields.isolved.state`; keep source type and nested scope. |
| `taxDistrict` | Optional[IsolvedOptionValueModelOfInt32] | Optional presence | #/definitions/AOS.PayrollOffice.RestAPI.Models.OptionValueModelOfInt32 | Tax District | Preserve separately: `provider_fields.isolved.tax_district`; keep source type and nested scope. |
| `timeZone` | Optional[str] | Optional presence | string | Timezone | Preserve separately: `provider_fields.isolved.time_zone`; keep source type and nested scope. |
| `workLocationCode` | Optional[str] | Optional presence | string | Work Location Code (Location ID in the UI) | Preserve separately: `provider_fields.isolved.work_location_code`; keep source type and nested scope. |
| `workLocationDescription` | Optional[str] | Optional presence | string | Description | Preserve separately: `provider_fields.isolved.work_location_description`; keep source type and nested scope. |
| `zipCode` | Optional[str] | Optional presence | string | Address Zip Code | Preserve separately: `provider_fields.isolved.zip_code`; keep source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

#### IsolvedOptionValueModelOfInt32

[Source model](../../../src/normalization/source_models/isolved/isolved_source_model_employee.py) · [Contract schema](../../../contracts/isolved/openapi/isolved-v6.swagger.json#/definitions/AOS.PayrollOffice.RestAPI.Models.OptionValueModelOfInt32).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | Optional[int] | Required presence | integer / int32 | Unique Object Id | Preserve nested/reference scope: `provider_fields.isolved.id` (Optional[str]); identifier helper, no identity substitution. |
| `description` | Optional[str] | Optional presence | string | Description of the option value. | Preserve separately: `provider_fields.isolved.description`; keep source type and nested scope. |
| `links` | Optional[List[IsolvedBaseLinkModel]] | Optional presence | array | Listing of hyperlink references within the API that are related to or describe actions that can be taken on the current object. | Preserve source nesting: `provider_fields.isolved.unmapped` (record links). |

### ukg_ready

#### UKGReadyEinsResponse

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_company.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/249/schema).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__lookup__eins.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `items` | List[UKGReadyEinsResponseItemsItem] | Required presence | array | No property description supplied. | Container: validate/map each supplied source record; preserve other wrapper fields separately. |

#### UKGReadyEinsResponseItemsItem

[Source model](../../../src/normalization/source_models/ukg_ready/ukg_ready_source_model_company.py) · [Contract schema](../../../contracts/ukg-ready/reference-schemas.json#/schemas/249/schema/properties/items/items).

[Cached HTML reference](../../../contracts/ukg-ready/reference-docs/res/__v2__companies__%28cid%29__lookup__eins.html).

| Source field | Current Python type | Presence | Contract type / format | Description and documented values | Proposed target / handling |
|---|---|---|---|---|---|
| `id` | int | Required presence | integer | No property description supplied. | Proposed shared source_record_id (str), with source_record_type ein; not API company_id. |
| `ein_tax_id` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `ukg_ein_tax_id` (Optional[str]); no inferred federal jurisdiction or shared tax meaning. |
| `ein_name` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `ukg_ein_name` (Optional[str]); not a verified legal or DBA name. |
| `ein_currency_code` | Optional[str] | Optional presence | string | No property description supplied. | Preserve separately: `provider_fields.ukg-ready.ein_currency_code`; keep source type and nested scope. |
| `ein_country_id` | Optional[str] | Optional presence | string | No property description supplied. | Preserve nested/reference scope: `provider_fields.ukg-ready.ein_country_id` (Optional[str]); identifier helper, no identity substitution. |

## Code and lookup review

Use verified full labels only on the exact documented source field. Label helpers retain originals and report unknown meanings; blank/null values follow the existing helper policy.

| Exact field | Verified labels | Applicability |
|---|---|---|
| Prism ClientMaster.statusClass | A → Active; P → Pending; I → Inactive; C → Client Cancelling, Pre-Termination; T → Terminated | Apply only to this field; retain originals and unknown values. |
| Prism ClientMaster.serviceType | ASO → Administrative Services Only; PEO → Professional Employer Services; PAY → Payroll Processing Only; ASA → Admin Services/Alt. Billing; COR → Corporate Payroll; HRN → HR Services, No Payroll | Apply only to this field; retain originals and unknown values. |

- Prism ClientMaster.status is a client-configured status code associated with a class; the class dictionary is not a complete dictionary for that raw status field. Keep status and statusClass separate.
- isolved LegalModel.status has only “Current Legal Company Status”; no field-specific dictionary is supplied by the selected Swagger/lookup files. Preserve its source text.
- UKG EIN lookup fields contain no supplied value dictionaries. Preserve country/currency codes without inventing labels, tax jurisdiction, or conversions.
- Company ACH status and print/service/worksite rules are separate settings; their field descriptions remain in the inventory. Do not reuse employee, payroll, or direct-deposit account status labels across these fields.

## Saved Postman evidence

Request names and saved response structure only are shown below. No personal/account values or credentials are copied. A request with no saved JSON response provides no live response proof. Samples supplement the contract; they do not define every accepted input shape.

| Request | Saved JSON response evidence |
|---|---|
| prismHR - companyInfo chosen | 200 object; keys: clientMaster, errorCode, errorMessage, extension |
| isol - companyInfo chosen | 200 object; keys: allowRemoteWorkers, client, compensationPlans, federalEIN, forceDirectDepositPrenote, iSolvedTimeEnabled, id, legalCode, legalName, links, payGroups, status |

## References and verification

- [Original comparison](./company.md) (unchanged; disagreements should be resolved using the contract evidence above).
- [Decisions](../DECISIONS.md) and [README](../../../README.md).
- [PrismHR OpenAPI](../../../contracts/prismhr/openapi/prismhr-2025.09.openapi.json), [isolved Swagger](../../../contracts/isolved/openapi/isolved-v6.swagger.json), [UKG schemas](../../../contracts/ukg-ready/reference-schemas.json).
- Lookup references: [PrismHR](../../../contracts/prismhr/lookup-reference.json), [isolved](../../../contracts/isolved/lookup-reference.json), [UKG Ready](../../../contracts/ukg-ready/lookup-reference.json).

Declared source-field coverage (reused classes counted once per provider): prismhr 285, isolved 192, ukg_ready 6.

Fields with absent/vague-by-absence property descriptions or undocumented source additions: prismhr 25, isolved 31, ukg_ready 6. Every such field is explicitly marked; a source name is not treated as a verified meaning. Coverage counts prove inventory inclusion, not business equivalence or live API completeness.

Before mapper implementation: follow the current model scope above. Existing ID/date/number, requiredness and preservation policies remain settled. Verify sparse records, nested IDs, legal/parent-name separation, unknown codes, extras and finite recursive source nesting. The canonical company output model is now implemented; source models, YAMLs and adapters are unchanged by this step.

## Review update — start here

- Settled rules applied: shared architecture, string IDs, date/number helpers, requiredness, explicit provider fields, links/extras/metadata preservation.
- Verified shared meanings: Prism/isolved legal name, DBA name, federal identifier and NAICS code.
- UKG EIN name/tax/country/currency remain explicit source values; EIN record identity is not API company identity.
- Parent-client data/settings retain their own scope; recursive schema references do not trigger automatic joins or schema expansion.
- Model implemented from the existing proposal. Company adapters now map these records; additional request-context integration is not required or inferred.

## Canonical output model implemented

[canonical_model_company.py](../../../src/normalization/canonical_models/canonical_model_company.py) defines CanonicalCompany and CanonicalCompanyResult using the same strict typing, optional business fields and provider_fields/source_extras/source_metadata conventions as the other canonical models.

- Verified shared fields: legal_name, trade_name, federal_tax_id and naics_code.
- Source identity: provider + source_record_type + source_record_id; identifiers are strings and source null acceptance remains.
- UKG-specific roots: ukg_ein_name and ukg_ein_tax_id; currency/country and other settings remain provider-specific.
- No generated company IDs, inferred parent/employee joins, new helpers or adapter changes. Payroll stays deferred.

## Three company YAMLs created

- [PrismHR company.yaml](../../../src/normalization/mappings/prismhr/company.yaml): one ClientMaster record, source_record_type client.
- [isolved company.yaml](../../../src/normalization/mappings/isolved/company.yaml): one LegalModel record, source_record_type legal_company. Parent-client and nested legal-company scopes remain separate.
- [UKG company.yaml](../../../src/normalization/mappings/ukg_ready/company.yaml): one EIN lookup item, source_record_type ein. EIN name/tax values remain UKG-specific.
- The future adapter supplies the fixed source_record_type as internal mapper context; no new user CLI input-type option was added. Wrappers are outside per-record YAMLs.
- Existing helpers only; company adapters are not connected by this step. Model names, shared meanings and preservation policies follow the existing proposal.
- Recursive isolved back-references map their nested ID only; remaining fields are preserved by the existing unmapped fallback, with unknown extras retained separately. No infinite YAML/schema expansion or source join is introduced.
- Verified all three configurations through source-path/output-schema preflight and execution with populated nested synthetic data, including source identity, unknown fields, legal/DBA separation, recursive references and UKG-specific fields.

## Company adapters connected — current status

All three normalize_company methods now validate native inputs once and map their prepared YAMLs using existing helpers. They return CanonicalCompanyResult as a JSON-compatible dictionary, retaining wrappers when companies is empty. No new helper, CLI context option or source schema was added.

[Company Mapper Implementation](../Company%20Mapper%20Implementation.md) records source roles, wrapper/record preservation, recursion behavior, tests and the unchanged isolved/UKG readiness limitation. Earlier model/YAML-only status notes describe prior stages; this section is current.
