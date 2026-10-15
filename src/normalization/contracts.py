# Contract layer: replaces the hand-written Pydantic source models.
# Each provider response is validated against the schema its own contract file
# declares for that endpoint, and the mapping engine reads field names from the
# same schemas. Nothing here maps data; it only prepares and checks it.
"""Validate provider responses directly against the distributed contracts.

Sources (README-approved reference pack):
- PrismHR: OpenAPI 3.0.1, GET 200 response schema of the endpoint path.
- isolved: primary Swagger 2.0 snapshot only, GET 200 response schema.
- UKG Ready: reference-schemas.json; the GET schema extracted from the cached
  page whose name matches the endpoint (no HTML is read).

Validation policy:
- null means "not supplied": a type error on a null value is ignored.
- integral floats (7.0) count as integers.
- a non-null value of the wrong type stops the run (ValueError with its path).
- "required" is not enforced: the contracts mark nearly every field required,
  but real and synthetic responses omit most of them. Only record ids are
  required, and the id templates enforce those (relationship_policies.md).
- every other violation (undocumented field, length, range, enum) is contract
  drift: returned as a warning, mapping continues.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft4Validator, validators
from referencing import Registry
from referencing.jsonschema import DRAFT4

from .references import ROOT

CONTRACTS = ROOT / "contracts"
SPEC_FILES = {
    "prismhr": CONTRACTS / "prismhr" / "openapi" / "prismhr-2025.09.openapi.json",
    "isolved": CONTRACTS / "isolved" / "openapi" / "isolved-v6.swagger.json",
}
UKG_SCHEMAS = CONTRACTS / "ukg-ready" / "reference-schemas.json"

# Field names the live PrismHR demo spells differently from its contract, keyed
# by (parent key, live name); None = top level of the body. Renamed to the
# contract spelling before validation, so validation and YAML only ever see
# contract names. Replaces the AliasChoices the source models used.
LIVE_RENAMES = {
    "prismhr": {
        (None, "payrollVoucher"): "payrollVouchers",
        ("person", "employerId"): "employerIds",
        ("person", "autoPolicy"): "autoPolicies",
        ("client", "hawaiiMedWaiver"): "hawaiiMedWaivers",
    },
}


# Fields the live demo returns that the contract does not list (previously
# declared as "live-only" in the source models). Keyed by provider and endpoint;
# paths are relative to the response body ('[]' = list items). They are added
# to the schema the mapping engine reads, so YAML may map them and unmapped ones
# land in provider_fields...unmapped. Validation still reports them as drift.
LIVE_FIELDS = {
    "prismhr": {
        "/clientMaster/v1/getClientMaster": [
            "clientMaster.commission[].commType", "clientMaster.commission[].targetAmt",
            "clientMaster.eVerify", "clientMaster.enrollOnboardControls.decisionSupport",
            "clientMaster.enrollOnboardControls.onboardVersion", "clientMaster.externalPtoUsed",
            "clientMaster.notificationEmailList", "clientMaster.payrollFinalizationNotification",
            "clientMaster.positionRatesUsed", "clientMaster.reverseWireAccount",
            "clientMaster.taxesToSuppress",
        ],
        "/employee/v1/getEmployee": ["employee[].compensation.payPeriodsPerWeek"],
        "/payroll/v1/getPayrollVoucherForBatch": [
            "payrollVouchers[].hsaPeoMatch", "payrollVouchers[].isManualCheck",
        ],
    },
    "isolved": {
        "/api/clients/{clientId}/legals/{legalId}/employees/{employeeId}/payItems": ["[].balance"],
    },
    "ukg-ready": {
        "/v2/companies/{cid}/employees/{aid}": ["ein_name"],
        "/v2/companies/{cid}/payrolls": ["payrolls[].ein.ein_country_id"],
    },
}


# Draft 4 treats 7.0 as "not an integer"; later drafts and the identifier
# helper accept integral floats, and so did the previous source models.
_TYPES = Draft4Validator.TYPE_CHECKER.redefine(
    "integer",
    lambda checker, value: Draft4Validator.TYPE_CHECKER.is_type(value, "integer")
    or (isinstance(value, float) and value.is_integer()),
)
Validator = validators.extend(Draft4Validator, type_checker=_TYPES)


class Schema:
    """A contract schema node with local $ref and allOf resolved on access.

    A schema without `properties` is open: any field name is accepted and every
    field counts as declared (no split into unmapped/extras below it).
    `path` is the node's position in the response body ('a.b[]'); `live` holds
    LIVE_FIELDS paths for this response, which count as declared properties.
    """

    def __init__(self, node: Any, root: dict, path: str = "", live: frozenset = frozenset()):
        self.root = root
        self.path = path
        self.live = live
        self.wrapped: dict[str, "Schema"] = {}
        self.node = self._resolve(node if isinstance(node, dict) else {})

    def _resolve(self, node):
        seen = 0
        while "$ref" in node:
            ref = node["$ref"]
            if not ref.startswith("#/"):
                raise ValueError(f"Only local schema references are supported: {ref!r}")
            target = self.root
            for part in ref[2:].split("/"):
                target = target[part.replace("~1", "/").replace("~0", "~")]
            node = target
            seen += 1
            if seen > 50:
                raise ValueError(f"Schema reference loop at {ref!r}")
        if "allOf" in node:
            merged = {k: v for k, v in node.items() if k != "allOf"}
            merged.setdefault("properties", {})
            for part in node["allOf"]:
                part = Schema(part, self.root).node
                merged["properties"] = {**merged["properties"], **(part.get("properties") or {})}
            node = merged
        return node

    def _sub(self, node, path):
        return Schema(node, self.root, path, self.live)

    def _live_here(self) -> set[str]:
        prefix = self.path + "." if self.path else ""
        return {p[len(prefix):] for p in self.live
                if p.startswith(prefix) and "." not in p[len(prefix):] and "[" not in p[len(prefix):]}

    def _types(self) -> set:
        kind = self.node.get("type")
        return set(kind) if isinstance(kind, list) else ({kind} if kind else set())

    @property
    def is_open(self) -> bool:
        """An untyped or object node without listed properties accepts any field."""
        if self.node.get("properties") or self.is_array:
            return False
        types = self._types() - {"null"}
        return not types or "object" in types

    @property
    def is_array(self) -> bool:
        kind = self.node.get("type")
        return kind == "array" or (isinstance(kind, list) and "array" in kind) or "items" in self.node

    def declared(self) -> set[str]:
        return set(self.node.get("properties") or {}) | self._live_here()

    def child(self, name: str) -> "Schema":
        """Schema of one property; KeyError when a closed schema does not list it."""
        if name in self.wrapped:
            return self.wrapped[name]
        path = f"{self.path}.{name}" if self.path else name
        if self.is_array or (not self.is_open and not self.node.get("properties")):
            # Lists need '[]' (or a list rule); scalars have no fields.
            raise KeyError(name)
        if self.is_open:
            return self._sub({}, path)
        properties = self.node["properties"]
        if name in properties:
            return self._sub(properties[name], path)
        if name in self._live_here() or any(p.startswith(path + ".") or p.startswith(path + "[")
                                             for p in self.live):
            return self._sub({}, path)  # live-only field: undocumented, so open
        raise KeyError(name)

    def items(self) -> "Schema":
        return self._sub(self.node.get("items") or {}, self.path + "[]")

    def at(self, path: str) -> "Schema":
        """Walk 'a.b[].c' ('[]' steps into list items); KeyError on unknown names."""
        schema = self
        for segment in filter(None, path.split(".")):
            name, brackets = segment.split("[]", 1)[0], segment.count("[]")
            if name:
                schema = schema.child(name)
            for _ in range(brackets):
                schema = schema.items()
        return schema

    def wrap(self, name: str) -> "Schema":
        """Schema of {name: <this body>}: used for section wrappers like salary_history."""
        outer = Schema({"type": "object", "properties": {name: {}}}, self.root)
        outer.wrapped = {name: self}
        return outer


def _escape(segment: str) -> str:
    return segment.replace("~", "~0").replace("/", "~1")


@lru_cache(maxsize=None)
def _spec(provider: str):
    with SPEC_FILES[provider].open(encoding="utf-8") as stream:
        spec = json.load(stream)
    registry = Registry().with_resource("urn:" + provider, DRAFT4.create_resource(spec))
    return spec, registry


@lru_cache(maxsize=None)
def _ukg_pages() -> dict:
    with UKG_SCHEMAS.open(encoding="utf-8") as stream:
        entries = json.load(stream)["schemas"]
    # A cached page can hold a GET response schema plus PUT/POST request
    # schemas; no page has more than one GET schema, so this keeps the GET one.
    return {entry["source_page"].rsplit("/", 1)[-1]: entry["schema"]
            for entry in entries if entry["method"] == "GET"}


def ukg_page(endpoint: str) -> str:
    """'/v2/companies/{cid}/employees/{aid}' -> '__v2__companies__(cid)__employees__(aid).html'."""
    return endpoint.replace("/", "__").replace("{", "(").replace("}", ")") + ".html"


@lru_cache(maxsize=None)
def response_schema(provider: str, endpoint: str) -> Schema:
    """Schema of the GET 200 response body of `endpoint` in the provider contract."""
    if provider == "ukg-ready":
        schema = _ukg_pages().get(ukg_page(endpoint))
        if schema is None:
            raise ValueError(f"No UKG Ready GET schema for endpoint {endpoint!r}")
        return Schema(schema, schema, live=_live(provider, endpoint))
    if provider not in SPEC_FILES:
        raise ValueError(f"Unknown provider {provider!r}")
    spec, _ = _spec(provider)
    response = (spec["paths"].get(endpoint, {}).get("get") or {}).get("responses", {}).get("200")
    if response is None:
        raise ValueError(f"No {provider} GET 200 response for endpoint {endpoint!r}")
    node = response["content"]["application/json"]["schema"] if provider == "prismhr" else response["schema"]
    return Schema(node, spec, live=_live(provider, endpoint))


def _live(provider: str, endpoint: str) -> frozenset:
    return frozenset(LIVE_FIELDS.get(provider, {}).get(endpoint, ()))


@lru_cache(maxsize=None)
def _validator(provider: str, endpoint: str):
    if provider == "ukg-ready":
        schema = dict(response_schema(provider, endpoint).root)
        schema.pop("$id", None)
        schema.pop("$schema", None)
        return Validator(schema)
    response_schema(provider, endpoint)  # raises a clear error for unknown endpoints
    _, registry = _spec(provider)
    pointer = f"#/paths/{_escape(endpoint)}/get/responses/200"
    pointer += "/content/application~1json/schema" if provider == "prismhr" else "/schema"
    return Validator({"$ref": f"urn:{provider}{pointer}"}, registry=registry)


def _rename(provider: str, node: Any, parent: str | None = None) -> Any:
    renames = LIVE_RENAMES.get(provider)
    if not renames:
        return node
    if isinstance(node, dict):
        renamed = {}
        for key, value in node.items():
            name = renames.get((parent, key), key)
            if name != key and name in node:
                name = key  # both spellings supplied: leave the live one as is
            renamed[name] = _rename(provider, value, name)
        return renamed
    if isinstance(node, list):
        return [_rename(provider, item, parent) for item in node]
    return node


def prepare(provider: str, response: dict) -> Any:
    """Checks that must happen before schema validation; returns the body to validate.

    1. HTTP status (optional, default 200): any other status has no usable body.
    2. PrismHR reports failures inside 200 bodies (errorCode != "0").
    3. Live-name renames, so the schema sees contract names.
    """
    endpoint = response.get("endpoint")
    status = response.get("status", 200)
    if status != 200:
        raise ValueError(f"{provider} {endpoint}: HTTP status {status}; nothing to normalize")
    body = response.get("body")
    if provider == "prismhr" and isinstance(body, dict) and "errorCode" in body and str(body["errorCode"]) != "0":
        raise ValueError(
            f"PrismHR {endpoint} failed (errorCode={body['errorCode']}): {body.get('errorMessage')}"
        )
    return _rename(provider, body)


def validate(provider: str, endpoint: str, body: Any) -> list[dict]:
    """Validate a prepared body; return contract-drift warnings, raise on type errors."""
    warnings = []
    for error in _validator(provider, endpoint).iter_errors(body):
        if error.instance is None or error.validator == "required":
            continue  # null = not supplied; requiredness is not enforced (see module doc)
        path = "/".join(str(part) for part in error.absolute_path)
        if error.validator == "type":
            raise ValueError(f"{provider} {endpoint}: {path or '<body>'}: {error.message}")
        warnings.append({"severity": "warning", "code": "contract_drift", "endpoint": endpoint,
                         "path": path, "message": error.message[:300]})
    return warnings
