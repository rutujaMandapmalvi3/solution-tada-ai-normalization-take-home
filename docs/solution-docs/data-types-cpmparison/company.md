# Company — Response Fields

Company fields from each provider, matched by meaning. Company is a minimal record (ID required, name optional) per `data-source-decisions.md`; other company fields are not mapped.

| Provider | Endpoint | Source |
| --- | --- | --- |
| PrismHR | `GET /clientMaster/v1/getClientMaster?clientId=` | Saved response "prismHR - companyInfo", client 132; fields under `clientMaster`; schema `ClientMaster` |
| isolved | `GET …/legals/{legalId}` | Saved response "isol - companyInfo chosen", legal 5806; schema `LegalModel` |
| UKG | None | Company ID from sign-in `company_id` and request URLs; no endpoint returns company details |

- `.` marks a nested field.

## Matched Fields

| Field | PrismHR | isolved | UKG |
|---|---|---|---|
| Company ID | `id` | `id` (legal company) | `company_id` (sign-in) |
| Legal name | `legalName` | `legalName` | — |
| Doing-business-as name | `clientName` | `dbaName` | — |
| Parent client ID | — | `client.id` | — |
| Parent client name | — | `client.clientName` | — |

## Not Mapped

| Provider | Fields |
|---|---|
| PrismHR | Remaining `clientMaster` fields (205 in total), e.g. `status`, `federalIdNumber`, address |
| isolved | `allowRemoteWorkers`, `compensationPlans`, `federalEIN`, `forceDirectDepositPrenote`, `iSolvedTimeEnabled`, `legalCode`, `payGroups`, `status`, `links`, `client.clientCode`, `client.securityServiceGroup`, `client.links` |
| UKG | EIN lookup (`…/lookup/eins`): `id`, `ein_name`, `ein_tax_id`, `ein_country_id`, `ein_currency_code` |

## Findings

| Finding | Evidence |
|---|---|
| PrismHR `clientName` is the doing-business-as name | Schema: "doing-business-as client name"; `legalName` is "legal business name for client" |
| isolved has two company levels | Legal company (5806, "B J Scrap Metal Inc") sits under a parent client (4046, "Bob's Heating & Air TADA AI DEMO") |
| isolved `dbaName` is empty | Live value is null |
| UKG returns no company name | All 478 UKG schemas checked |

## Matches to Verify

None.