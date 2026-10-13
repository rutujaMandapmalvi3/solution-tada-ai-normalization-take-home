# Solution Approach

How the platform turns provider responses into canonical records.

## Stack

| Choice | Use | Reason |
|---|---|---|
| Python + Pydantic | Provider models, canonical models, validation, serialization | The task is a transformation pipeline; Pydantic covers validation and JSON in/out |
| Plain Python functions | Mapping provider → canonical | No framework needed |
| pytest | Tests on synthetic fixtures | Tests must run offline without credentials |
| Django | Not used | Its ORM, database and admin are not needed |
| FastAPI | Optional, later | Only if an API or the write path is added; built on Pydantic, so no rewrite |

## Flow

```
Provider response
  → Pick adapter (PrismHR / isolved / UKG)
  → Deserialize (response → Python objects; check incoming data)
  → Map (→ our standard format)
  → Validate (check our standard format)
  → Serialize (→ JSON)
  → Output (one file per provider and record type + errors file)

RUN:  python -m normalizer --provider <name> --type <record type> --input <file> --output <folder>
TEST: synthetic fixtures → adapter (deserialize + map) → validate → serialize → pytest compares with expected standard JSON
```

## Database

| Decision | Reason |
|---|---|
| No database | The README requires linked records and local runs, not storage or queries |

- Records are linked by ID fields in the JSON output, which play the role of foreign keys:

```
company_id ← employee.company_id
employee_id ← deposit.employee_id, deduction.employee_id, paycheck.employee_id
payroll_run_id ← paycheck.payroll_run_id
```

- SQLite can be added later without changing the pipeline.

## Deep Dive

### Step 1: Input

The input is a file of provider JSON. The CLI is given the provider and data type, so it picks the right model and mapper.

| Source | Used for |
|---|---|
| Synthetic fixtures (provider response shape) | Tests |
| Saved live responses (kept outside Git) | Manual runs on real data |
| Live API calls (optional, later) | Fetching data directly |

### Pick Adapter

Chooses the code for the provider given in `--provider`.

```python
ADAPTERS = {"prismhr": PrismHRAdapter, "isolved": IsolvedAdapter, "ukg": UKGAdapter}
adapter = ADAPTERS[provider]()
```

- All adapters have the same methods: `company()`, `employees()`, `direct_deposits()`, `deductions()`, `payroll_runs()`, `paychecks()`.
- The rest of the program calls these methods without knowing the provider.
- Unknown provider name → stop with a message listing valid names.
- New provider → write one adapter class, add one line to `ADAPTERS`.

### Step 2: Deserialize (inside the adapter)

```
JSON text → json.loads → Python dict → model_validate → provider object
```

**Unwrap the envelope first**

| Provider | Unwrap |
|---|---|
| PrismHR | Check `errorCode == "0"`, take `employee[]` |
| isolved | Take `results[]`; follow `nextPageUrl` for more pages |
| UKG | Use the response directly |

**Provider model rules**

- One Pydantic model per JSON object level, nested the same way as the response:
  - nested JSON object → nested model
  - JSON list → `list[Model]`
- Provider's exact field names; only fields in the field mapping documents.
- Fields optional (`None`) except IDs needed for linking.
- `extra="allow"`: unmapped fields kept in `model_extra`, later `provider_extras`.
- No renaming or converting; that is the mapping step.

**How `model_validate` works**

- Field by field: take the value → check the declared type (convert when safe, e.g. `"12"` → `12`) → keep it.
- Object is built only after every field passes.
- Any failure → no object; one error listing all failed fields.
- Errors are caught per record: log it, skip it, continue with the rest.

### Step 3: Map (inside the adapter)

Turns provider objects into our standard records.

- One mapper per record type per provider: 6 types (company, employee, direct deposit, deduction, payroll run, paycheck) × 3 providers = 18.
- All three providers' mappers fill the same standard schema per record type.

| Job | Example |
|---|---|
| Rename fields | `firstName` / `nameAddress.firstName` / `first_name` → `first_name` |
| Translate codes | PrismHR status `A` → `ACTIVE` |
| One format for dates and money | dates → `YYYY-MM-DD`; money → decimal |
| Build IDs | record ID = provider + record type + record's own key; provider's ID kept as `source_id` |
| Build owner links | from the request (Method 1) or from a field in the record (Method 4) |
| Combine APIs | UKG name (API 1) + job info (API 2) → one employee |
| Keep the rest | unmapped fields → `provider_extras` |

- Mapper handles meaning (codes, combining); Pydantic handles types (text → date, text → number).

### Step 4: Validate

Checks each finished standard record.

| Check | How |
|---|---|
| Required fields present (IDs, links) | Declared in the schema |
| Right types | Declared in the schema |
| Allowed coded values | Enums |
| Simple limits (e.g. amount ≥ 0) | `Field(ge=0)` |
| Rules using two fields (e.g. amount or percent) | Small validator function |

- Failed record → noted with reason → skipped → run continues (`try/except`).
- First validation checks provider data coming in; this one checks our data going out.

### Step 5: Serialize

Turns standard records into JSON: `record.model_dump_json()`.

- Dates → `"2025-03-28"`; coded values → `"ACTIVE"`; nested records → nested JSON.
- Open choices: keep empty fields as `null` or leave them out; money as number or text.

### Step 6: Output

| Output | Location |
|---|---|
| Good records | `<folder>/<provider>/<record type>.json` |
| Failed records + reasons | `<folder>/<provider>/errors.json` |
| Summary on screen | e.g. "PrismHR employees: 20 saved, 1 failed" |