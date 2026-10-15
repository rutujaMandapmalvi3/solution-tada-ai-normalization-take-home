# Relationship policies: record ids, refs and merge

## Terms
- **Record:** one item that becomes one canonical output entry, for example one employee, one deposit account, one deduction, or one paycheck. Every item in a response's record list is a record.
- **Record id (`id`):** a string that identifies a record uniquely across all providers and record types.
- **Ref (`company_ref`, `employee_ref`, `payroll_run_ref`):** a foreign key. It holds another record's `id`.
- **Owner scope:** the company a record belongs to.
  - PrismHR: `clientId`
  - isolved: `clientId:legalId`
  - UKG Ready: `cid`
- **Sources:**
  - **P** = the response's request `params` in the input bundle;
  - **R** = the record itself;
  - **Par** = the record that encloses it (e.g. the PrismHR employee around a deposit).

## Id policy
1. **Format:** `provider:record_type:owner_scope[:employee_key]:record_key`.
2. **Every record gets an id:** every item of every record list.
3. **Owner scope** comes from **P**, because response bodies usually leave it out.
4. **Employee key:** records that belong to an employee (deposits, deductions) also include the employee's key.
5. **Record key:** the provider's own id for the record, from **R**. Two exceptions:
   - The response is about one record and its body has no id (pay-info, compensation, salaries): use the id from **P**.
   - The provider has no id for this record at all: use the smallest set of fields that identifies it and stays stable, never fields that change over time such as amounts or methods.
6. **Ids are computed independently in each response.** The same real-world record yields the same id everywhere, and that equality is what connects responses.

## Table 1: record ids
| Entity | PrismHR | isolved | UKG Ready |
|---|---|---|---|
| company | `prismhr:company:{P.clientId}` | `isolved:company:{P.clientId}:{R.id}` (R.id = legal id) | `ukg-ready:company:{P.cid}`; EIN: `ukg-ready:company:{P.cid}:ein:{R.id}` |
| employee | `prismhr:employee:{P.clientId}:{R.id}` | `isolved:employee:{P.clientId}:{P.legalId}:{R.id}`; salaries: `…:{P.employeeId}` | `ukg-ready:employee:{P.cid}:{R.id}`; pay-info and compensation: `…:{P.aid}` |
| direct_deposit | `prismhr:direct_deposit:{P.clientId}:{Par.id}:{R.transitNum}:{R.accountNum}` | `isolved:direct_deposit:{P.clientId}:{P.legalId}:{P.employeeId}:{R.id}` | `ukg-ready:direct_deposit:{P.cid}:{P.aid}:{R.id}` |
| deduction | `prismhr:deduction:{P.clientId}:{P.employeeId}:{R.deductionCode}` | `isolved:deduction:{P.clientId}:{P.legalId}:{P.employeeId}:{R.id}` | `ukg-ready:deduction:{P.cid}:{P.aid}:{R.id}` |
| payroll_run | `prismhr:payroll_run:{P.clientId}:{R.batchId}` | `isolved:payroll_run:{P.clientId}:{P.legalId}:{P.paygroupId}:{R.id}` | `ukg-ready:payroll_run:{P.cid}:{R.id}` |
| paycheck | `prismhr:paycheck:{P.clientId}:{R.voucherId}` | `isolved:paycheck:{P.clientId}:{P.legalId}:{R.id}` | `ukg-ready:paycheck:{P.cid}:{R.id}`; detail without id: `…:{P.pay_statement_id}` |

**Where no provider id exists:**
- **PrismHR deposit:** the key is routing + account number. These identify the bank account and don't change when the amount or method changes.
- **PrismHR deduction:** the key is the deduction code.

## Ref policy
1. A ref is the parent's `id`, built with the parent's own Table 1 template from values available in the current response. Nothing is looked up.
2. Refs are stored on **every output record**, not once per file.
3. `company_ref` is on every non-company record, and on UKG EIN records (pointing to their company).
4. `employee_ref` is on deposits, deductions and paychecks.
5. `payroll_run_ref` is on paychecks, where the run id is available.

## Table 2: refs
| Ref | PrismHR | isolved | UKG Ready |
|---|---|---|---|
| company_ref | `{P.clientId}` | `{P.clientId}:{P.legalId}` | `{P.cid}` |
| employee_ref (deposit) | `{Par.id}` | `{P.employeeId}` | `{P.aid}` |
| employee_ref (deduction) | `{P.employeeId}` | `{P.employeeId}` | `{P.aid}` |
| employee_ref (paycheck) | `{R.employeeId}` | `{R.employeeId}` | `{R.employee.account_id}` |
| payroll_run_ref (paycheck) | `{R.batchId}` | none: checks carry no run id | `{P.payroll_id}` |

Each value is the key part; the full ref is `provider:record_type:` + the scoped key from Table 1.

## What if they don't exist
| Situation | Behaviour |
|---|---|
| Owner-scope param missing from **P** (e.g. no `clientId`) | No id can be built. The run stops with an error naming the response, the template and the missing value. |
| Record key missing from **R** (e.g. an employee without `id`) | The fallback in Table 1 is used if there is one (UKG pay-statement detail → `P.pay_statement_id`). Otherwise the run stops with the same error. |
| No provider id by design (PrismHR deposit, PrismHR deduction) | The natural key in Table 1 is used. If any of its fields is missing, the run stops with the same error. |
| Two different records produce the same id | They are merged. Differing values keep the first one and add a `merge_conflict` issue. If this happens for real, the key needs another stable field (e.g. PrismHR `voucherTypeOverride`). |
| A value needed for a ref is missing (e.g. a paycheck without `employeeId`) | The ref stays empty, a `missing_ref` warning is added, and the record is still output. |
| A ref by design has no source (isolved `payroll_run_ref`) | The ref stays empty, with no issue. This is documented as a known gap. |
| A ref points to a record not in the bundle | The record is kept and a `dangling_link` info issue is added. A partial bundle is normal. |
| A **P** owner id disagrees with the body (e.g. `P.employeeId` ≠ the body's employee id) | The run stops with an error. The source is never silently overwritten. |

## Merge policy
- Records with the same `id` from different responses become one record. Examples:
  - a UKG employee from profile + pay-info + compensation;
  - an isolved employee from the employee record + salaries;
  - a UKG paycheck from the statement header + detail.
- **Rules:**
  - a missing field is filled from the other record;
  - nested objects merge field by field;
  - lists are joined;
  - a differing value keeps the first one and adds a `merge_conflict` issue.
- The merged record is validated again against its canonical model.
