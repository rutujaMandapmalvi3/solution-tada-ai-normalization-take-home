# Tada AI · Data Normalization: Solution

This tool normalizes company, employee, direct deposit, deduction and payroll data from
**PrismHR, isolved and UKG Ready** into one canonical model. It runs locally and offline.
- Each provider response is validated against that provider's own API contract.
- YAML rules map it into shared canonical records.
- Every record gets a canonical id, so related records (company → employee → deposits,
  deductions, paychecks) are linked and checked in the same run.

- Assignment: [root README](../../README.md)
- Decisions, assumptions and gaps: [DECISIONS.md](./DECISIONS.md)
- Record ids, links and merge rules: [relationship_policies.md](./relationship_policies.md)

## Problem statement

Normalize five data types from three payroll providers into a consistent model while
keeping their meaning, and keep the company–employee relationships so records can be
linked. Discover the provider mappings, design the canonical schemas, and test with
deterministic synthetic data that runs without credentials.

## Approach

### 1. Provider data
The demo sign-in service and the live responses were used only to **discover**
response shapes and codes. The tool itself never calls an API. Its input is a local
**bundle** file holding captured responses (see [Input and output](#input-and-output)).

Endpoints the tool maps, per entity:

| Entity | PrismHR | isolved (`…` = `/api/clients/{clientId}/legals`) | UKG Ready (`…` = `/v2/companies/{cid}`) |
|---|---|---|---|
| Company | `/clientMaster/v1/getClientMaster` | `…` (legal-company list) | `…/lookup/eins` (the cid company + its EINs) |
| Employee | `/employee/v1/getEmployee` | `…/{legalId}/employees`, `…/{legalId}/employees/{id}`, `…/employees/{employeeId}/salaries` | `…/employees`, `…/employees/{aid}`, `…/employees/{aid}/pay-info`, `…/employees/{aid}/compensation/history` |
| Direct deposit | `/employee/v1/getEmployee` (`DirectDeposit` option) | `…/employees/{employeeId}/directdeposits` | `…/employees/{aid}/direct-deposits` |
| Deduction | `/deductions/v1/getDeductions` | `…/employees/{employeeId}/payItems` (Deduction items) | `…/employees/{aid}/deductions` |
| Payroll run | `/payroll/v1/getBatchListByDate` | `…/{legalId}/paygroupId/{paygroupId}/payrollRunHistory[/byDate]` | `…/payrolls` |
| Paycheck | `/payroll/v1/getPayrollVoucherForBatch` | `…/{legalId}/payGroups/{payGroupId}/checks` | `…/payrolls/{id}/pay-statements`, `…/payrolls/{id}/pay-statements/{id}` |

### 2. Discover mappings
Fields and codes were matched using three sources:
- the provider contracts in `contracts/` (PrismHR OpenAPI, isolved Swagger, UKG extracted schemas);
- the lookup references;
- the saved live samples.

Per-field evidence is in the mapping proposals: [employee](./data-types-cpmparison/Employee%20Canonical%20Mapping%20Proposal.md),
[direct deposit](./data-types-cpmparison/Direct%20Deposit%20Canonical%20Mapping%20Proposal.md),
[deduction](./data-types-cpmparison/Deduction%20Canonical%20Mapping%20Proposal.md),
[company](./data-types-cpmparison/Company%20Canonical%20Mapping%20Proposal.md),
[payroll](./data-types-cpmparison/Payroll%20Canonical%20Mapping%20Proposal.md).

### 3. Canonical model
- **Six record types** (strict Pydantic models in `src/normalization/canonical_models/`): company, employee, direct deposit, deduction, payroll run and paycheck.
- **One document per run** holds the six record lists, plus `provider_fields`, `source_metadata` and `issues`.
- **Ids and links:** every record gets a canonical id, `provider:record_type:owner_scope[:employee_key]:record_key`. Child records carry refs (`company_ref`, `employee_ref`, `payroll_run_ref`) that hold the parent's id. See [relationship_policies.md](./relationship_policies.md).

### 4. Fixtures
- **Bundles:** `scripts/generate_fixtures.py` (seed 42) writes three synthetic bundles, `tests/fixtures/<provider>.bundle.json`. Each is one connected company, and every response is checked against its contract before writing.
- **Expected outputs:** the reviewed `<provider>.expected.json` files are golden outputs, compared in full by the tests.
- More detail: [tests/fixtures/README.md](../../tests/fixtures/README.md).

### 5. Transform
```
bundle file ─► CLI: read + deserialize, readiness check
  └► pipeline.normalize_bundle()   (orchestrator)
       per response: contracts.prepare (status, provider error, live renames)
                   → contracts.validate (body vs contract schema)
                   → adapter route table (which records, which YAML, id/ref templates)
                   → MappingEngine + YAML (source record → canonical record)
                   → stamp canonical id + refs
       then: merge records with the same id → re-validate → link check → document
  └► CLI: add reference warnings, write output file
```

### 6. Test
Test suites by layer:
- contracts;
- engine and YAML preflight;
- per-provider field mappings;
- relationships (ids, refs, merges);
- CLI end to end;
- fixture generator;
- reference integrity.

Run with `pytest`. Latest run: 218 tests passed.

### 7. Write path (optional extension)
Not built.

## Setup

Requirements: Python 3.11 or newer. No credentials or network access are needed.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

- **Run from the repo:** run commands from the repository root. The tool reads the provider contracts from `contracts/` in this checkout.
- **Live demo access is optional** and only for discovery. It needs `DEMO_SIGNIN_API_KEY` in a local `.env` file, which is git-ignored; never commit it.

## Usage

```sh
# Normalize one provider bundle into one canonical document
normalization normalize --input tests/fixtures/prismhr.bundle.json --output out/prismhr.json
# (same as: python -m normalization normalize ...)

normalization list-providers          # supported provider names
normalization check-inputs            # report reference-pack readiness per provider
python scripts/generate_fixtures.py   # regenerate the three fixture bundles
pytest                                # run the test suite
```

**Output file:**
- **No overwriting:** the output file must not exist yet; the tool never overwrites a file.
- **Folder must exist:** the parent folder must already exist.
- **Nothing on failure:** no file is written when the run stops.

**Exit codes:**
- `0`: the document was written. It may contain issues.
- `1`: unusable input, e.g. an unreadable file, a bad bundle, a provider error, a wrong type, a missing id or an owner conflict.
- `2`: the reference pack is unreadable or mismatched.

isolved and UKG runs also print a `Warning:` line about reference-pack metadata gaps. That's expected, and the warnings are kept in the output document.

## Input and output

**Input: a bundle.** One JSON file per provider with any file name:

```json
{
  "provider": "prismhr",
  "responses": [
    {"endpoint": "/employee/v1/getEmployee",
     "params": {"clientId": "001", "employeeId": "007"},
     "body": {"errorCode": "0", "employee": [{"id": "007", "firstName": "Alex"}]}}
  ]
}
```

- **`provider`:** selects the provider's adapter.
- **`endpoint`:** the contract path; it selects the schema and the mapping rules.
- **`params`:** the request's owner ids (e.g. `clientId`, `legalId`, `cid`, `employeeId`, `aid`). Response bodies often omit them.
- **`status`:** optional, defaults to 200.

**Output: one canonical document.**

```
provider
companies, employees, direct_deposits, deductions, payroll_runs, paychecks
provider_fields   – unrouted responses and filtered records, kept as-is
source_metadata   – each response's endpoint, params and wrapper fields; reference warnings
issues            – contract_drift, missing_ref, merge_conflict, dangling_link
```

Nothing supplied is dropped:
- fields the contract declares but no rule maps go to the record's `provider_fields.<p>.unmapped`;
- fields the contract doesn't declare go to `source_extras.<p>`;
- each record lists its `sources`.

## Architecture

| Component | Role | Input → output |
|---|---|---|
| `__main__.py` | CLI: file I/O, readiness check, exit codes | bundle file → output file |
| `pipeline.py` | Orchestrator: runs every step for each response; merges and checks links | bundle dict → document dict |
| `contracts.py` | Validates bodies against the provider contracts; live renames | response → prepared body, warnings |
| `adapters/<provider>.py`, `adapters/route.py` | Route tables (data only): endpoint → record type, records path, YAML, id/ref templates; `Route` documents the keys | – |
| `mapping_config.py` | Loads a YAML mapping file and validates its rule structure | YAML file → `MappingConfig` |
| `mapping_validation.py` | Checks rule paths and helpers against the contract and canonical model before mapping | rules → ok or error |
| `mapping_engine.py` + `mappings/` + `helpers/` | Runs the rules and preserves unmapped/undeclared fields | source record → canonical record |
| `canonical_models/` | Strict output models and the document model | data → validated records |
| `references.py` | Reference-pack readiness checks | provider → issues |

## Project structure

```
src/normalization/
  __main__.py  pipeline.py  contracts.py  references.py
  mapping_config.py  mapping_validation.py  mapping_engine.py
  adapters/            route.py  prismhr.py  isolved.py  ukg_ready.py
  mappings/<provider>/ *.yaml
  canonical_models/    *.py
  helpers/             mapping.py
contracts/             provider specs and lookup references (unchanged reference pack)
scripts/               generate_fixtures.py
tests/                 test suites;  tests/fixtures/ bundles + expected outputs
docs/solution-docs/    README (this file), DECISIONS.md, relationship_policies.md, proposals
```

## Limitations

The full list is in [DECISIONS.md → Gaps](./DECISIONS.md#gaps).
- **Run stops on one wrong type:** a single wrong-typed value stops the whole run; per-record rejection is planned.
- **Merging can duplicate list entries:** supplying the same response twice duplicates its list entries.
- **No live capture:** no pagination and no API fetching; bundles must be captured elsewhere.
- **No business-rule checks yet:** e.g. amount vs percent, or date order.
- **UKG:** no company name exists anywhere in the reference material.
- **isolved:** checks carry no payroll run id, so paychecks have no run link.
- **No write path:** writing back to a provider is not built.

## Documentation

- [DECISIONS.md](./DECISIONS.md): decisions, assumptions and gaps, with reasons.
- [relationship_policies.md](./relationship_policies.md): id and ref templates, what happens when values are missing, and merge rules.
- [cli_input_decisions.md](./cli_input_decisions.md): why the CLI takes only `--input` and `--output`.
- [tests/fixtures/README.md](../../tests/fixtures/README.md): fixtures and how to regenerate them.
- Mapping proposals: [docs/solution-docs/data-types-cpmparison/](./data-types-cpmparison/).
