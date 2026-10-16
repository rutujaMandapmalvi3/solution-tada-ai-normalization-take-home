# Synthetic fixtures

Three provider bundles, each one connected synthetic company. All names, ids and
bank values are invented; no Postman payloads or credentials were copied.

- `<provider>.bundle.json`: input. `{provider, responses: [{endpoint, params, body}]}`.
  `endpoint` is the contract path and selects the schema. `params` holds the
  request's owner ids (PrismHR `clientId`; isolved `clientId`, `legalId`,
  `employeeId`; UKG `cid`, `aid`, `payroll_id`, `pay_statement_id`).
- `<provider>.expected.json`: the reviewed canonical document the CLI produces
  for that bundle.
- `generation_manifest.json`: seed, generator checksum, contract checksums and
  bundle checksums.

Run from the project root:

```sh
.venv/bin/python -m normalization normalize --input tests/fixtures/prismhr.bundle.json --output /tmp/prismhr.json
```

The output file must not already exist. Exit 0 means the document was written;
problems are listed in its `issues`.

The bundles exercise, per provider:
- every record type;
- ids and refs from DECISIONS.md section 4;
- merges (isolved employee + salaries; UKG employee + pay-info + compensation;
  UKG statement header + detail);
- a filtered isolved pay item and unrouted UKG catalog/benefits responses.

`tests/test_bundle_cli.py` compares complete documents with the expected files.
Review any change to an expected file against the YAML and the policies before
accepting it; tests never regenerate it.

## Regenerate the bundles

```sh
.venv/bin/python scripts/generate_fixtures.py
```

This rewrites the three bundles and `generation_manifest.json`, never the
expected files. Seed 42 reproduces the committed bundles byte for byte. Every
response is checked with `contracts.prepare` + `contracts.validate` before
anything is written.

```sh
.venv/bin/python scripts/generate_fixtures.py --seed 43 --output-dir /tmp/tada-fixtures-43
```
