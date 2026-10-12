# Project Files

## 1. Task and docs

| File | What it does |
|---|---|
| `README.md` | The task. Turn employee, direct deposit, deduction and payroll data from 3 providers into one shared format. Also says how to get live demo data and what to submit. |
| `docs/REFERENCE_AUDIT.md` | Says where each provider file came from, if it may be shared, and what was removed (only login secrets). |
| `docs/solution-docs/README.md` | Template for the solution write-up: steps, setup, usage, design. |
| `docs/solution-docs/DECISIONS.md` | Template for assumptions, data gaps and decisions. |

## 2. Reference: PrismHR (input)

| File | What it does |
|---|---|
| `contracts/prismhr/openapi/prismhr-2025.09.openapi.json` | PrismHR's API description: 450 endpoints. Shows how to get companies, employees, bank accounts, deductions and paychecks, and what fields come back. |
| `contracts/prismhr/lookup-reference.json` | List of PrismHR codes and what they mean. Example: `A` = Active, `G` = Wage Garnishment. |
| `contracts/prismhr/NOTICE.md` | Says where the PrismHR file came from and what was changed. |
| `contracts/prismhr/LICENSE.apache-2.0.txt` | The open license that allows sharing the PrismHR file. |

## 3. Reference: isolved (input)

| File | What it does |
|---|---|
| `contracts/isolved/openapi/isolved-v6.swagger.json` | isolved's main API description: 361 endpoints. Use this one. |
| `contracts/isolved/openapi/isolved-v6.alternate.swagger.json` | An older or different copy: 344 endpoints. Only for comparing. Do not mix it with the main one. |
| `contracts/isolved/lookup-reference.json` | 11 lists of allowed values. Example: days of the week, alert levels. Their meanings are not given. |
| `contracts/isolved/SOURCE_MANIFEST.json` | Checksums and source details for the two isolved files. |
| `contracts/isolved/NOTICE.md` | Says where the isolved files came from and what was changed. |

## 4. Reference: UKG Ready (input)

| File | What it does |
|---|---|
| `contracts/ukg-ready/reference-docs/*.html` (guide pages) | Saved UKG help pages: login, headers, limits, errors, versions. |
| `contracts/ukg-ready/reference-docs/res/*.html` (about 360 pages) | One saved page per UKG endpoint. Shows the URL, inputs and returned fields. |
| `contracts/ukg-ready/reference-schemas.json` | 478 field layouts pulled out of those pages. It is not a real API file. |
| `contracts/ukg-ready/lookup-reference.json` | 15 lists of allowed values. Example: payroll status `OPEN`/`CLOSED`, ID type `SSN`. Their meanings are not given. |
| `contracts/ukg-ready/SOURCE_MANIFEST.json` | Checksums and source details for the UKG pages. |
| `contracts/ukg-ready/NOTICE.md` | Says where the UKG pages came from and what was changed. |

## 5. Code (input → output order)

| File | What it does |
|---|---|
| `scripts/generate_fixtures.py` | Empty. Should make fake provider data for testing. |
| `src/normalization/references.py` | Reads a provider's lookup file and checks that it is ready to use. |
| `src/normalization/adapters/__init__.py` | Lists the 3 providers and the data types: `company`, `employee`, `payroll`. |
| `src/normalization/adapters/prismhr.py` | Empty. Should turn PrismHR data into the shared format. |
| `src/normalization/adapters/isolved.py` | Empty. Should turn isolved data into the shared format. |
| `src/normalization/adapters/ukg_ready.py` | Empty. Should turn UKG data into the shared format. |
| `src/normalization/__init__.py` | Marks the folder as a Python package. It has no logic. |
| `src/normalization/__main__.py` | The command-line tool. Reads an input file, runs the provider code, and writes an output file. It never overwrites an existing file. |

## 6. Tests

| File | What it does |
|---|---|
| `tests/test_starter.py` | Checks the basic wiring. Also checks that the provider code is still empty. |
| `tests/test_reference_integrity.py` | Checks that the provider files are not changed or broken. |

## 7. Settings

| File | What it does |
|---|---|
| `.editorconfig` | Formatting rules: spaces, line endings. |
| `.gitignore` | Files Git should not save: secrets, caches. |
