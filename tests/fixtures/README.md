# Synthetic CLI fixtures

One populated input/expected-output pair for each of five entities and three providers (15 cases).
All names, IDs and bank values are invented; routing/account strings are placeholders, not real banking details. No Postman payloads or credentials were copied.

- `<provider>/<entity>/input.json`: provider-shaped synthetic input.
- `<provider>/<entity>/expected.json`: complete expected CLI JSON, including reference warnings.
- `manifest.json`: provider, entity and separate CLI context needed by each case.
- `generation_manifest.json`: generator/seed, input checksums and contract/source-model fingerprints.

Example from the project root:

```sh
.venv/bin/python -m normalization normalize --provider prismhr --entity employee --input tests/fixtures/prismhr/employee/input.json --output /tmp/prismhr-employee-example.json --client-id 001
```

Output files must not already exist. Use `--employee-id` from the manifest for direct deposits/deductions. Context is not added to the provider input JSON.

Expected files were captured from CLI execution, then checked against independent semantic assertions for IDs, names, dates, amount roles, association gaps, filtering, extras and reference warnings. They record the reviewed baseline; they are not independent proof of every mapping decision. Review a changed expected file against the YAML/proposal before accepting it. Tests compare complete JSON values and never regenerate the baseline.

Payroll examples keep runs and paychecks separate; UKG also includes a summary. Missing links stay absent, and uncertain UKG amounts remain provider-specific. Other tests cover overlapping inputs and alias conflicts.

Reference warnings appear at result-level `source_metadata.<provider>.reference_pack`, or per employee record because employees currently return a list. For an empty employee result with reference warnings, the CLI emits an `employees: []` container plus metadata so warnings cannot be lost. Direct adapter calls do not add CLI reference warnings.

Run: `.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_sample_fixtures.py`.

## Regenerate inputs

From the project root:

```sh
.venv/bin/python scripts/generate_fixtures.py
```

This replaces the 15 input.json files and the two generation/context manifests. It leaves expected.json and unrelated files untouched. The default seed 42 reproduces the reviewed inputs. It uses explicit synthetic builders based on documented source schemas, then validates the complete set using project source models before any writes. It does not infer business semantics or populate every optional field.

```sh
.venv/bin/python scripts/generate_fixtures.py --seed 43 --output-dir /tmp/tada-fixtures-43
```

A different seed varies selected names, salary and deposit amounts. IDs, placeholder banking strings and zero-valued cases intentionally stay stable. Use a separate output directory for alternate seeds; existing expected outputs only describe seed 42 and must be separately reviewed for changed inputs. The generator does not need or copy Postman data and never runs a mapper to approve expected outputs.
