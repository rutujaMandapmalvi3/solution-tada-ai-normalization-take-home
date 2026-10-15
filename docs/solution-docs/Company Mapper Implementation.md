# Company mapper implementation

All three company adapters are connected using existing identifier/date/number/label helpers. No new helper, engine behavior, source-model requirement or CLI option was added.

## Flow and record scope

`local JSON → provider source model → validated record(s) → company.yaml + MappingEngine → CanonicalCompany → CanonicalCompanyResult → JSON-compatible dictionary → CLI JSON file`

| Provider | Native input | Mapped source class | Internal role |
|---|---|---|---|
| PrismHR | Wrapper with optional clientMaster | PrismHRClientMaster | client |
| isolved | One legal-company object | IsolvedLegalModel | legal_company |
| UKG Ready | EIN lookup wrapper with items | UKGReadyEinsResponseItemsItem | ein |

source_record_type is supplied internally from the adapter's known source class. It is not a new user input-type flag, company ID, or inferred relationship. Source id becomes source_record_id; no company identity is manufactured or joined across providers.

## Decisions and implementation choices

- Reuse the existing canonical model/YAMLs and common MappingEngine. Source validation runs once; no repeated source-record model_validate calls are added during mapping.
- Create one engine per nonempty input and preserve input order. No fetching, sorting, deduplication or parent-child merging.
- Prism checks its explicit wrapper errorCode; extension presence alone is not failure. Optional missing/null clientMaster gives companies=[], while wrapper metadata remains preserved.
- isolved accepts the existing native legal object and creates one output record, including a nullable source ID where source validation permits it. No fake response wrapper or extra company CLI context is introduced.
- UKG maps each items entry as an EIN record. Empty items keeps wrapper metadata; UKG EIN name/tax data never fills unverified legal_name/federal_tax_id.
- Company results use provider, companies and preservation containers. Individual records retain source_record_type/source_record_id and source_location.record_index provenance.
- Parent-client and nested legal-company data retain their source scope. Recursive back-references project their IDs; other finite supplied values stay in unmapped and extras. They do not overwrite the root company's identity or names.
- Verified shared legal/DBA/federal/NAICS meanings use the proposal's shared fields. Uncertain statuses, tax/code/contact/settings data remain provider-specific, using the universal preservation policy.
- Wrapper fields and wrapper extras go to result source_metadata.<provider>.response (excluding the mapped record collection); record links/unconsumed known fields go to provider_fields.<provider>.unmapped; unknown nested fields go to source_extras.<provider>.
- Metadata/original values begin after existing source validation; the mapper is not a byte-for-byte archive of input JSON.

## Verification and limitations

At connection: 223 tests passed. Tests cover source requiredness/errors, one validation/engine, nullable IDs, nested/recursive source scope, source extras and links, wrapper data with no records, legal/DBA/EIN separation, order, no input mutation and JSON serialization.

PrismHR CLI company normalization runs with the real readiness check. isolved/UKG CLI integration tests isolate only their known readiness gate; separate tests confirm their real reference blockers still apply. references.py and contract metadata were not changed.

## Files

- [PrismHR adapter](../../src/normalization/adapters/prismhr.py)
- [isolved adapter](../../src/normalization/adapters/isolved.py)
- [UKG adapter](../../src/normalization/adapters/ukg_ready.py)
- [Canonical model](../../src/normalization/canonical_models/canonical_model_company.py)
- [Company proposal, evidence and YAML links](./data-types-cpmparison/Company%20Canonical%20Mapping%20Proposal.md)
- [Decision log](./DECISIONS.md)
