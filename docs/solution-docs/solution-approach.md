# Solution Approach

This is a local, file-based normalization pipeline for PrismHR, isolved, and UKG Ready. Keep the starter repository's provider modules and shared `normalize(entity, response, reference)` function interface. No abstract target, adapter classes, or result contract from the removed `base.py` are part of this approach.

## Stack and boundaries

- Python for the CLI and provider-specific transformation functions.
- Pydantic for source and canonical model validation. Models are still to be implemented.
- pytest for deterministic, offline transformation tests.
- No database or web framework for this stage. Canonical JSON records carry their relationships as IDs.
- Live responses and the local Postman collection inform discovery and manual checks. Submitted fixtures must be synthetic and must not require credentials or live services.

## What exists today

| File | Current responsibility and status |
|---|---|
| `src/normalization/__main__.py` | Parses CLI arguments, checks reference readiness, reads and deserializes JSON, selects a provider module, calls `normalize`, serializes the returned value, and writes one output file without overwriting an existing file. |
| `src/normalization/adapters/__init__.py` | Registers provider modules. The original GitHub starter accepts `company`, `employee`, and `payroll`; the local implementation has also added `direct_deposit` and `deduction`. |
| `src/normalization/adapters/prismhr.py` | Contains the unimplemented PrismHR `normalize` function. |
| `src/normalization/adapters/isolved.py` | Contains the unimplemented isolved `normalize` function. |
| `src/normalization/adapters/ukg_ready.py` | Contains the unimplemented UKG Ready `normalize` function. |
| `src/normalization/references.py` | Loads provider lookup references and checks reference metadata. Its current readiness rules block isolved and UKG normalization. |
| `scripts/generate_fixtures.py` | Fixture-generation stub. |
| `tests/test_starter.py` | Tests starter wiring and currently expects provider transformations to be unimplemented. |
| `tests/test_reference_integrity.py` | Checks the distributed reference artifacts, checksums, and citations. |

The CLI logic is implemented, not a placeholder: it performs the file-processing and dispatch steps described above. Normalization is not working end to end yet because the provider functions remain stubs and readiness checks block isolved and UKG. Canonical models, source models, record mapping, and transformation tests are not implemented yet. The design below describes the work to build, not functionality already available.

## Runtime flow

```text
CLI (__main__.py)
  Parse arguments
  Check provider reference readiness
  Open the input file
  Read and deserialize JSON with json.load
  Select the provider module from ADAPTERS
  Load its lookup reference
  Call normalize(entity, response, reference)

Provider module
  Dispatch to an entity-specific transformation function
  Validate the response envelope and check provider-reported errors
  Extract the records
  For each record:
    Validate the source record
    Resolve IDs and owner relationships
    Map fields and normalize documented values
    Validate the canonical record
    Build the canonical output
  Return a JSON-serializable value (return annotation remains Any)

CLI (__main__.py)
  Serialize the result
  Write the output file
```

The adapter receives an already-deserialized Python object. It does not reopen the input file or write output files. JSON deserialization and source-model validation are separate operations.

## Provider functions

Keep `normalize` as the public entry point in each provider module. Use small internal functions for entity-specific work, such as `normalize_employees` and `normalize_company`, rather than placing every mapping in one large function.

Each provider handles its own response shapes. For example, PrismHR employees are under `employee[]`, isolved employee lists use `results[]` while an individual employee response is an object, and UKG uses entity-specific envelopes such as `deposits[]` and `payrolls[]`.

Check the envelope before validating records individually. A malformed envelope or provider-reported failure must not be treated as an empty dataset. A valid empty collection is different from a failure. Whether to reject the operation or preserve valid records when one record is invalid remains an implementation decision; no partial-result policy is fixed yet.

Keep the existing entry-point signature:

```python
def normalize(entity: str, response: Any, reference: Dict[str, Any]) -> Any:
```

- `entity` selects the transformation.
- `response` is the already-deserialized provider response.
- `reference` contains provider lookup information loaded by the CLI.

The return annotation stays `Any`. Leave the exact output structure open while implementing. There is no required `data`/`errors`/`metadata` wrapper and no prescribed normalization status enum. Canonical fields should remain consistent across providers once defined.

The returned value must still be JSON-serializable because the CLI uses `json.dumps(result, indent=2, allow_nan=False)`. Convert any internal Pydantic models, dates, Decimal values, or other custom objects into JSON-compatible values before returning. If using Pydantic internally, `model_dump(mode="json")` can perform that conversion.

The current CLI does not inspect the return value for record errors or statuses. If normalization returns normally and the file is written, it exits with `0`. It catches `OSError`, `ValueError`, `TypeError`, and `NotImplementedError`, prints the exception to stderr, and exits with `1` without writing the normalization output. Reference-readiness failures exit with `2`. These process exit codes are separate from HTTP status codes or any future normalization status.

## Models and mappings

Build models alongside the first transformation rather than defining all providers up front.

- Source models retain provider field names and validate one record at a time. Preserve additional fields, including additional fields in nested objects.
- Canonical models use the same names and meanings across providers. Define company, employee, direct-deposit setup, deduction setup, payroll-run, and paycheck records as those transformations are implemented.
- Required fields are those needed for identity and valid relationships. Other fields may be absent depending on the provider and response.
- Preserve provider-specific or unmapped information in `provider_extras`; do not silently discard it.
- Translate codes only when their meanings are supported by the lookup reference or field documentation. Preserve unknown and tenant-configured source codes without guessing their meaning.
- Preserve distinctions such as union membership versus union ID, deduction balance versus arrears tracking, and paper-check amount versus net pay.
- Use Decimal for monetary values internally and choose an explicit JSON representation. Use documented date and duration semantics; UKG `standard_work_day` is documented in milliseconds and cannot be copied directly into an hours field.
- Do not impose blanket nonnegative constraints on payroll amounts without checking whether adjustments or reversals are allowed.

The comparison documents are mapping research. Check the cited contract and saved response as each field is implemented; a shared table row does not by itself prove that all fields have identical meanings.

## IDs and input context

PrismHR employee responses already include employer IDs in `person.employerId[]` (contract name: `person.employerIds[]`). These may identify companies, but their relationship to client/company IDs is unconfirmed; verify before using them for company links.

Canonical records must retain source IDs and link company, employee, and payroll records consistently. Include the owner scope needed to avoid collisions when constructing IDs. For isolved, distinguish the parent client from the legal company.

The existing signature does not receive request context. Some responses omit company, employee, pay-group, or run IDs that were present only in the request. Inspect the first employee transformation for missing owner IDs and determine which IDs can be obtained from the supplied response. A context file, extra CLI arguments, or an additional function parameter are possible options, not agreed interface changes. Keep the current signature until a concrete mapping requires a decision. Do not guess missing owner IDs or read them from lookup metadata.

For records without source IDs, choose and test a deterministic key rule using the relevant owner scope. For isolved paychecks, a run number alone does not identify a payroll run; the documented matching proposal also needs pay group and pay date, with ambiguity reported rather than silently choosing a run.

## Multiple responses and payroll

The current CLI accepts one input JSON file per invocation. It does not merge responses or fetch additional pages.

- UKG employee coverage needs profile, pay-info, and compensation responses. Define how these are supplied and joined by employee before claiming full employee coverage.
- isolved salary responses provide additional compensation and pay-group information. The earlier proposal to defer these endpoints remains a coverage gap, not a completed mapping.
- UKG paycheck lists contain headers; statement details are needed for earnings, taxes, and deductions. isolved pay-group checks may also need separate detail responses.
- Keep employee deduction setup separate from deductions taken on a paycheck. UKG company deduction codes are catalog entries and cannot substitute for employee deduction rules.
- Payroll runs and paychecks are distinct canonical records. The current `payroll` CLI entity needs an explicit way to select them, or an explicitly defined combined input, when payroll is implemented.
- Offline normalization processes supplied data. How to preserve pagination information in the output remains open; following pagination links belongs to a future data-fetching layer.

## Start implementing: PrismHR employees

The first implementation goes in `src/normalization/adapters/prismhr.py`, behind the existing `normalize` function's `employee` branch.

1. Inspect the saved `prismHR - employeeFullRecord` response and the contract's `Employee` schema. Use the employee comparison table as the field inventory.
2. Start the `employee` branch in the existing `normalize(entity, response, reference) -> Any` function. Build the employee mapping and any needed source/canonical models alongside it. Leave the overall output format open and identify any missing company context.
3. Validate the PrismHR envelope and success code, then extract `employee[]`.
4. Validate and map employee records: build IDs and links, map identity/contact/employment/job/compensation fields, preserve extras, and validate the output. Decide how invalid records are handled when implementing this step.
5. Create synthetic inputs and tests for normal records, missing optional fields, unknown codes, invalid fields, mixed valid and invalid records, an empty employee collection, and a provider error.
6. Run the transformation through the existing CLI and inspect the JSON result. Expand the employee mapping until it covers the available fields before declaring it complete.

After that first path works, implement the remaining PrismHR entities, then reuse the canonical schemas for isolved and UKG Ready. Refine schemas where the next provider exposes a meaningful distinction.

## Local collection and validation

The collection is stored outside the implementation repository at `/Users/rutuja/Downloads/TADA/tada/samples/TADA collection.postman_collection.json`. Inspect saved response bodies and their saved request URLs, not just example names. In the current collection, UKG compensation is saved under a pay-info request, the UKG profile request has no saved response, and the example attached to the pay-statement-details request is an empty benefits response. isolved payroll-run and paycheck examples are HTTP 404 responses with empty bodies, not successful empty datasets.

Use these observations to guide manual investigation. Do not copy credentials or live records into synthetic fixtures or the submission.

Replace tests that assert `NotImplementedError` as each transformation is implemented. Keep reference-integrity tests. Add deterministic fixture generation incrementally and verify mappings and relationships, not just output shapes.

## CLI usage and remaining integration work

The current command shape is:

```sh
python -m normalization normalize --provider prismhr --entity employee --input <input.json> --output <output.json>
```

The installed `normalization` command invokes the same entry point. `--output` is a file, not a folder. Its parent directory must exist, and the file must not already exist because the CLI opens it in mode `"x"`. NaN and infinity are rejected during serialization. The CLI writes the entire returned value; it does not require status or error fields.

Before all three providers can run end to end, reconcile the readiness gate with the distributed reference pack and the README. It currently enforces metadata that blocks isolved and UKG and assumes an OpenAPI artifact, although UKG supplies cached documentation and extracted schemas. Preserve reference provenance and integrity checks while addressing local runtime readiness. This behavior has not been changed yet.

Review context input, payroll selection, multi-response input, and error handling as their transformations require them; none is a reason to recreate the removed target or fix an output wrapper now. Update the final README and decisions to describe the implemented behavior. Live API fetching and the optional provider write path are later work.
