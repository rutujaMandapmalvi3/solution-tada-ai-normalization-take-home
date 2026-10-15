"""Shared test helpers: run one or more captured responses through the bundle pipeline."""
from normalization.pipeline import normalize_bundle

# Owner params used by the helpers and the generated fixtures.
PRISM = {"clientId": "001"}
ISOL = {"clientId": "4000", "legalId": "1"}
UKG = {"cid": "001"}

ISOL_LEGALS = "/api/clients/{clientId}/legals"
ISOL_EMPLOYEE = ISOL_LEGALS + "/{legalId}/employees/{employeeId}"
UKG_CO = "/v2/companies/{cid}"


def response(endpoint, body, **params):
    return {"endpoint": endpoint, "params": params, "body": body}


def run(provider, *responses):
    """Normalize a bundle built from (endpoint, body, params) responses."""
    return normalize_bundle({"provider": provider, "responses": list(responses)})


def run_one(provider, endpoint, body, **params):
    return run(provider, response(endpoint, body, **params))


def only(document, collection):
    records = document[collection]
    assert len(records) == 1, f"expected one {collection} record, got {len(records)}"
    return records[0]


def codes(document):
    return [issue["code"] for issue in document["issues"]]
