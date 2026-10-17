# Tada AI · Data Normalization: Solution

I built a local Python tool that turns saved **PrismHR, isolved and UKG Ready**
responses into one shared format for companies, employees, direct deposits,
deductions and payroll. It keeps the meaning of provider data and the links between
related entries.

- [Decisions, assumptions and gaps](./docs/DECISIONS.md)

## 1. My approach

### 1. Understand the problem

I read the assignment and explored the repository. I found it followed the adapter
design pattern and chose to keep it because it makes adding more providers easier.

### 2. Investigate the data

I identified the APIs needed for each data type and tried them in Postman. I
compared live responses with the contracts and found differences such as changed
field names, missing values and unavailable data. I used PrismHR OpenAPI, the primary
isolved Swagger snapshot, UKG's extracted schemas and the supplied lookup references.

### 3. Design the shared format

Before coding, I created Markdown tables comparing each provider's fields for each
entity. Where meanings matched, I chose a shared name and data type. I also chose
date formats, common labels, conversion rules and how to preserve unmatched fields.

### 4. Choose the implementation

I considered two options:

1. **Process one provider and entity at a time**, selected through CLI options.
2. **Process related responses together in one bundle**, using provider routes,
   YAML rules and a shared engine.

With the first option, connecting information from separate runs and extending the
processing flow would require more coordination and code changes. I chose the
second option to handle relationships in one run and keep provider-specific
changes in routes and mapping rules.

In the chosen design, the CLI reads and deserializes the input file. The program
checks each response against its provider contract. The adapter's routes locate
entries inside that response body and select the YAML file. YAML defines the field
changes, and one shared engine applies them.

### 5. Build the processing flow

The input bundle contains a provider name and saved responses. The output is one
JSON document with six lists of entries: companies, employees, deposits, deductions,
payroll runs and paychecks, plus metadata and issues. “Canonical” means this shared
output format.

```text
Read input
    ↓
Parse JSON
    ↓
Validate
    ↓
Map fields
    ↓
Add IDs and links
    ↓
Merge
    ↓
Revalidate
    ↓
Check links
    ↓
Write output
```

### 6. Verify and document

I checked the complete CLI flow by running normalization and manually comparing
its output with expected results. I documented decisions, assumptions and remaining
gaps. The test data and automated checks are described below.

## 2. How I built it

### Tech stack

Python **3.11+**, Pydantic for output models, jsonschema and referencing for provider
validation, PyYAML for mapping instructions, and pytest for automated tests.

### Code structure

| Part | Purpose |
|---|---|
| `src/normalization/__main__.py` | **CLI entry point** - Read input, check reference readiness, run the pipeline and write output. |
| `pipeline.py` | **Orchestrator** - Process responses, connect and combine entries, and build the document. |
| `contracts.py` | **Provider schema and field validator** - Read provider definitions, prepare responses and validate input. |
| `adapters/` | **Provider route definitions** - Define each endpoint's entries, mapping file, IDs and links. |
| `mapping_config.py` | **YAML loader and configuration validator** - Load YAML and check the instruction structure. |
| `mapping_validation.py` | **Mapping-rule validator** - Check that instructions use valid field paths and helpers. |
| `mapping_engine.py` | **Main mapper** - Execute instructions and preserve remaining data. |
| `helpers/mapping.py` | **Value conversion helpers** - Convert individual values. |
| `canonical_models/` | **Output models and validators** - Define and validate the shared output types. |
| `references.py` | **Reference-pack readiness checker** - Check whether the supplied reference pack is usable. |

All source paths after the first row are inside `src/normalization/`.
Provider definitions are in `contracts/`; mapping rules are in
`src/normalization/mappings/<provider>/`.

### Supported endpoints

| Entity | PrismHR | isolved (`…` = `/api/clients/{clientId}/legals`) | UKG Ready (`…` = `/v2/companies/{cid}`) |
|---|---|---|---|
| Company | `/clientMaster/v1/getClientMaster` | `…` (legal-company list) | `…/lookup/eins` (the cid company + its EINs) |
| Employee | `/employee/v1/getEmployee` | `…/{legalId}/employees`, `…/{legalId}/employees/{id}`, `…/employees/{employeeId}/salaries` | `…/employees`, `…/employees/{aid}`, `…/employees/{aid}/pay-info`, `…/employees/{aid}/compensation/history` |
| Direct deposit | `/employee/v1/getEmployee` (`DirectDeposit` option) | `…/employees/{employeeId}/directdeposits` | `…/employees/{aid}/direct-deposits` |
| Deduction | `/deductions/v1/getDeductions` | `…/employees/{employeeId}/payItems` (Deduction items) | `…/employees/{aid}/deductions` |
| Payroll run | `/payroll/v1/getBatchListByDate` | `…/{legalId}/paygroupId/{paygroupId}/payrollRunHistory[/byDate]` | `…/payrolls` |
| Paycheck | `/payroll/v1/getPayrollVoucherForBatch` | `…/{legalId}/payGroups/{payGroupId}/checks` | `…/payrolls/{id}/pay-statements`, `…/payrolls/{id}/pay-statements/{id}` |

### How one response is processed: happy path

The supplied PrismHR fixture includes company `001` and employee `007`. Here are
excerpts showing how the employee's name and pay reach the output.

**1. Read the employee response.** The endpoint is `/employee/v1/getEmployee`;
`params.clientId` is `"001"`. Its body contains:

```json
{
  "errorCode": "0",
  "employee": [{
    "id": "007",
    "firstName": "Alex",
    "compensation": {"hourlyPay": "25.50"}
  }]
}
```

**2. Select the employee route.** After contract validation, the adapter supplies
these settings, among others:

```python
{
    "type": "employee",
    "records": "employee[]",
    "yaml": "employee",
    "id": "{params.clientId}:{record.id}",
    "refs": {"company_ref": ("company", "{params.clientId}")}
}
```

`employee[]` selects each employee from the body. `yaml: employee` selects
`mappings/prismhr/employee.yaml`.

**3. Apply the YAML rules.** These two rules copy the name and convert pay text to
a number:

```yaml
- kind: field
  source: firstName
  target: first_name
- kind: field
  source: compensation.hourlyPay
  target: hourly_rate
  transform:
    name: number
```

The shared engine executes these rules alongside the file's other rules. The
pipeline adds the ID and company link, then saves the employee:

```json
{
  "id": "prismhr:employee:001:007",
  "company_ref": "prismhr:company:001",
  "employee_id": "007",
  "first_name": "Alex",
  "hourly_rate": 25.5
}
```

This is an output excerpt. Original inputs for fields using conversion helpers are kept in
`source_metadata.original_values`, whether conversion succeeds or fails, for later comparison in the output file. The company link resolves because the fixture
includes that company.

The output also includes:

- `provider_fields`: provider-specific and unmapped data, plus filtered or unrouted inputs.
- `source_extras`: entry fields not declared by the provider schema.
- `source_metadata`: input locations, original converted values, conversion issues and reference warnings.
- `issues`: contract differences, merge conflicts and missing or unresolved links.

### Validation rules

Wrong non-null types stop processing. Missing fields and nulls are allowed, but
enough information to build IDs is still required. Other reported contract
differences become `contract_drift` warnings. Canonical output is checked separately
against its strict model.

### Build confidence with synthetic data

1. **Generate inputs:** I used the seeded generator to create one synthetic bundle
   per provider, covering all six output lists. The bundles include related employee
   sections.
2. **Prepare expected outputs:** I created separate expected JSON files for those
   specific bundles. The fixture generator does not create these expected files.
3. **Check the expected answers:** I reviewed them against the input values, provider
   definitions and mapping rules—not just the mapper's output. I checked IDs, links,
   conversions, combined information, preserved data and warnings.
4. **Compare actual results:** I ran normalization through the CLI and compared its
   output with the expected files using automated tests.

The test suite also includes unit tests for helpers and models, integration tests
for connected pipeline steps, and end-to-end tests from file input through CLI
`main()` to output JSON. The CLI tests call `main()` directly rather than starting
a separate terminal process. Test and regeneration commands are in section 5.

## 3. Setup

Requirements: **Python 3.11 or newer**. Run all commands from the repository root,
which contains `pyproject.toml`.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Dependencies are declared in `pyproject.toml`: Pydantic, PyYAML, jsonschema and
referencing; pytest is included by the `dev` extra.

Keep the repository's `contracts/` folder in place: the program reads it at runtime.

## 4. Run the solution

### Normalize a supplied fixture

Create the output folder first. Choose an output filename that does not exist:

```sh
mkdir -p out
python -m normalization normalize \
  --input tests/fixtures/prismhr.bundle.json \
  --output out/prismhr.json
```

The same command accepts the other fixtures:

```sh
python -m normalization normalize --input tests/fixtures/isolved.bundle.json --output out/isolved.json
python -m normalization normalize --input tests/fixtures/ukg-ready.bundle.json --output out/ukg-ready.json
```

The installed `normalization` command is equivalent to `python -m normalization`.
An existing output file is never overwritten. Use a new filename when rerunning;
the parent folder must already exist.

### Understand the input

A bundle has this structure; this example shows one employee response:

```json
{
  "provider": "prismhr",
  "responses": [
    {
      "endpoint": "/employee/v1/getEmployee",
      "params": {"clientId": "001", "employeeId": "007"},
      "body": {
        "errorCode": "0",
        "employee": [{
          "id": "007",
          "firstName": "Alex",
          "compensation": {"hourlyPay": "25.50"}
        }]
      }
    }
  ]
}
```

| Input | Meaning |
|---|---|
| `provider` | `prismhr`, `isolved` or `ukg-ready`. |
| `responses` | Saved responses to process in order. |
| `endpoint` | The exact contract path; selects the schema and routes. |
| `params` | Request values identifying the company, employee or payroll. |
| `body` | The returned provider data. |
| `status` | Optional HTTP status, defaulting to 200. |

### Understand the output

The input above produces this complete output document:

```json
{
  "provider": "prismhr",
  "companies": [],
  "employees": [
    {
      "provider": "prismhr",
      "id": "prismhr:employee:001:007",
      "company_ref": "prismhr:company:001",
      "employee_id": "007",
      "first_name": "Alex",
      "hourly_rate": 25.5,
      "prismhr_client_id": "001",
      "provider_fields": {
        "prismhr": {
          "compensation": {}
        }
      },
      "source_metadata": {
        "original_values": {
          "id": "007",
          "compensation.hourlyPay": "25.50",
          "context.client_id": "001"
        },
        "prismhr": {
          "sources": [
            {
              "response": 0,
              "endpoint": "/employee/v1/getEmployee",
              "path": "employee/0"
            }
          ]
        }
      }
    }
  ],
  "direct_deposits": [],
  "deductions": [],
  "payroll_runs": [],
  "paychecks": [],
  "provider_fields": {},
  "source_metadata": {
    "prismhr": {
      "responses": [
        {
          "response": 0,
          "endpoint": "/employee/v1/getEmployee",
          "params": {
            "clientId": "001",
            "employeeId": "007"
          },
          "wrapper": {
            "errorCode": "0"
          }
        }
      ]
    }
  },
  "issues": [
    {
      "severity": "info",
      "code": "dangling_link",
      "record_id": "prismhr:employee:001:007",
      "path": "company_ref",
      "message": "prismhr:company:001 is not in this bundle."
    }
  ]
}
```

The original `"25.50"` is kept in `source_metadata.original_values` inside the
employee. The `dangling_link` info issue means the employee's company is not
included in this small input. The supplied full fixture includes that company.

| Output | Meaning |
|---|---|
| `provider` | Which provider the bundle belongs to. |
| `companies`, `employees`, `direct_deposits`, `deductions`, `payroll_runs`, `paychecks` | The six entry lists, including empty lists. |
| `provider_fields` | Provider-specific data, filtered entries and responses with no mapping route. Also appears inside entries for their own provider details and unused known fields. |
| `source_metadata` | Response information; entries also keep their input locations, original converted values and conversion issues here. |
| `source_extras` | Unexpected fields inside individual entries. |
| `issues` | Document warnings about contract differences, conflicting values and missing links. |

### Other commands and exit codes

List the providers supported by the tool:

```sh
python -m normalization list-providers
```

Check each provider's reference pack and report missing or unverified metadata:

```sh
python -m normalization check-inputs
```

| Exit code | Meaning |
|---|---|
| `0` | Output was written; it may still contain warnings. |
| `1` | An input, processing or output-file error stopped the run. |
| `2` | A blocking reference-pack problem stopped normalization. `check-inputs` also returns 2 when it reports metadata gaps. |

The code is not printed automatically. Run `echo $?` immediately after a command
to see it. isolved and UKG normalization can print known reference metadata
warnings and still succeed; those warnings are saved in the output.

Processing and serialization finish before the file is created. A storage error
while writing can still leave an incomplete new file.

## 5. Run tests and regenerate fixtures

```sh
pytest
```

Tests cover successful mappings, selected edge cases and errors: missing/null
values, conversion failures, incorrect types, conflicting IDs, merge behavior,
missing links and attempts to overwrite output. They also check YAML rules,
provider references, the generator and end-to-end CLI output. They do not cover
every possible edge case.

Fixture files in `tests/fixtures/`:

| File | Purpose |
|---|---|
| `<provider>.bundle.json` | Generated synthetic input. |
| `<provider>.expected.json` | Reviewed expected output used by end-to-end tests. |
| `generation_manifest.json` | Seed and checksums for the generator, contracts and bundles. |

To regenerate bundles with the default seed, 42:

```sh
python scripts/generate_fixtures.py
```

This rewrites bundles and the manifest, not expected outputs. Each response is
checked through the contract layer before writing. The default seed reproduces
the committed bundles. Review output changes before updating any expected file.

To generate another set without changing committed fixtures:

```sh
python scripts/generate_fixtures.py --seed 43 --output-dir out/fixtures-43
```

## 6. Scope, assumptions and limitations

The implemented path reads saved responses and writes local JSON. It does not
fetch API pages or create/update employees in provider systems; the optional
write-back extension is not built.

The reasons for mapping choices, assumptions and known gaps are in
[DECISIONS.md](./docs/DECISIONS.md). These include missing business checks, repeated
list items when inputs repeat, and links that cannot be built from direct IDs.
