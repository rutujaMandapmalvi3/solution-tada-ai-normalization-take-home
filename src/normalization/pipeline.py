# Bundle pipeline. Input: a provider bundle {provider, responses: [{endpoint, params, body}]}. Output: one canonical document dict.
# Bundle pipeline: one input file with many captured provider responses in,
# one canonical document out. Implements docs/solution-docs/relationship_policies.md:
# every record gets a canonical id, children get refs, records sharing an id merge.
"""Normalize a provider bundle into one canonical document.

Bundle format:
    {"provider": "prismhr",
     "responses": [{"endpoint": "<contract path>", "params": {...}, "status": 200, "body": ...}]}

Per response: contracts.prepare -> contracts.validate -> the provider adapter's
routes for that endpoint -> MappingEngine per record -> id/ref stamping.
Then: merge by id -> canonical re-validation -> link check -> document.
"""
from __future__ import annotations

import json
import re
from copy import deepcopy
from importlib.resources import as_file, files
from typing import Any

from . import contracts
from .adapters import ADAPTERS
from .canonical_models.canonical_document import COLLECTIONS, MODELS, CanonicalDocument
from .helpers.mapping import identifier
from .mapping_engine import MappingEngine, load_mapping_config

_PLACEHOLDER = re.compile(r"\{(params|record|parent)\.([^}]+)\}")
_REFS = ("company_ref", "employee_ref", "payroll_run_ref")


# ---------------------------------------------------------------- templates
# Reads a dotted path from a value; None when missing.
def _lookup(value: Any, path: str) -> Any:
    for segment in path.split("."):
        value = value.get(segment) if isinstance(value, dict) else None
    return value


# Fills {params|record|parent.x} placeholders; None if any value is missing.
def render(template: str, scope: dict) -> str | None:
    """Fill {params.x} / {record.x} / {parent.x}; None when any value is missing."""
    missing = False

    # Replaces one placeholder with its value normalized as an identifier.
    def fill(match):
        nonlocal missing
        value = identifier(_lookup(scope.get(match.group(1)), match.group(2))).value
        if value in (None, ""):
            missing = True
            return ""
        return value

    text = _PLACEHOLDER.sub(fill, template)
    return None if missing else text


# Renders templates in order and returns the first one that succeeds.
def _first(templates, scope):
    for template in templates if isinstance(templates, list) else [templates]:
        value = render(template, scope)
        if value is not None:
            return value
    return None


# Builds a route's engine context from templates and literal values.
def _context(route: dict, scope: dict) -> dict:
    """Route context: templates are rendered, literals (including None) pass through."""
    return {name: render(value, scope) if isinstance(value, str) and "{" in value else value
            for name, value in (route.get("context") or {}).items()}


# ---------------------------------------------------------------- record paths
# Yields each record, its parent and its JSON path for a route's records path.
def iterate(body: Any, path: str):
    """Yield (record, parent, json_path) for a records path such as
    '' (the body), '[]' (each item of a list body), 'employee[]' or
    'employee[].directDeposit.achVoucher[]' (parent = the enclosing employee)."""

    # Follows path segments recursively, iterating the lists marked with [].
    def walk(node, segments, parent, json_path):
        if not segments:
            if isinstance(node, dict):
                yield node, parent, json_path
            return
        segment, rest = segments[0], segments[1:]
        name, is_list = segment.removesuffix("[]"), segment.endswith("[]")
        if name:
            node = node.get(name) if isinstance(node, dict) else None
            json_path = json_path + (name,)
        if not is_list:
            yield from walk(node, rest, parent, json_path)
            return
        for index, item in enumerate(node or []):
            # The item becomes the parent of anything iterated below it.
            yield from walk(item, rest, item if rest else parent, json_path + (index,))

    yield from walk(body, [s for s in path.split(".") if s], None, ())


# Removes a dotted path from a record copy.
def _drop(record: dict, path: str) -> None:
    *parents, last = path.split(".")
    for name in parents:
        record = record.get(name) if isinstance(record, dict) else None
    if isinstance(record, dict):
        record.pop(last, None)


# Returns the body minus its record collections (the response wrapper).
def _wrapper(body: dict, record_paths: list[str]) -> dict:
    """Body minus its record collections; every sibling field is kept.

    Each records path is removed up to its outermost list or object that the
    route maps ('employeeDeductions.deduction[]' removes only `deduction`;
    'employee[].directDeposit.achVoucher[]' removes `employee`). A route on the
    whole body ('') leaves no wrapper.
    """
    if any(path == "" for path in record_paths):
        return {}
    wrapper = deepcopy(body)
    for path in record_paths:
        segments = [s for s in path.split(".") if s]
        cut = next((i for i, s in enumerate(segments) if s.endswith("[]")), len(segments) - 1)
        *parents, last = [s.removesuffix("[]") for s in segments[:cut + 1]]
        node = wrapper
        for name in parents:
            node = node.get(name) if isinstance(node, dict) else None
        if isinstance(node, dict):
            node.pop(last, None)
    return wrapper


# ---------------------------------------------------------------- merge
# Merges a record into the existing one with the same id, reporting conflicts.
# inputs - target: The record already saved in records, which gets updated in place
# incoming: The new record with the same id (data)
# record_id: That shared id, used only in conflict messages
# issues: The run's issue list, where merge_conflict warnings are added
# prefix: Used internally when it calls itself for nested dicts ("provider_fields."); empty on the first call
def _merge(target: dict, incoming: dict, record_id: str, issues: list, prefix: str = "") -> None:
    """Fill missing fields, merge nested objects, join lists, report differing values."""
    for key, value in incoming.items():
        path = prefix + key
        current = target.get(key)
        if key not in target or current is None:
            target[key] = value
        elif isinstance(current, dict) and isinstance(value, dict):
            _merge(current, value, record_id, issues, path + ".")
        elif isinstance(current, list) and isinstance(value, list):
            target[key] = current + value
        elif current != value and value is not None:
            issues.append({"severity": "warning", "code": "merge_conflict", "record_id": record_id,
                           "path": path, "message": f"Kept {current!r}; another response had {value!r}."})


# ---------------------------------------------------------------- pipeline
class _Engines:
    # Prepares an engine cache for one provider.
    def __init__(self, provider: str):
        self.provider = provider
        self.directory = "ukg_ready" if provider == "ukg-ready" else provider
        self.cache = {}

    # Returns the engine for a route and endpoint, building it once.
    def get(self, route: dict, endpoint: str) -> MappingEngine:
        key = (route["yaml"], endpoint, route["records"], route.get("wrap"))
        if key not in self.cache:
            # A route may read its records with another endpoint's record schema
            # (UKG employee list items are summaries of the employee resource).
            schema_endpoint, schema_path = route.get("schema", (endpoint, route["records"]))
            schema = contracts.response_schema(self.provider, schema_endpoint).at(schema_path)
            if route.get("wrap"):
                # Section wrapper (e.g. {"salary_history": [...]}) so the YAML keeps
                # one record shape per canonical employee; the section is the contract body.
                schema = schema.wrap(route["wrap"])
            resource = files("normalization").joinpath(f"mappings/{self.directory}/{route['yaml']}.yaml")
            with as_file(resource) as path:
                config = load_mapping_config(path)
            self.cache[key] = MappingEngine(config, schema, MODELS[route["type"]])
        return self.cache[key]


# Runs prepare, validate, route, map, stamp, merge, re-validate and link check.
def normalize_bundle(bundle: Any) -> dict:
    if not isinstance(bundle, dict) or bundle.get("provider") not in ADAPTERS:
        raise ValueError(f"Bundle must be an object with provider in {sorted(ADAPTERS)}")
    if not isinstance(bundle.get("responses"), list):
        raise ValueError("Bundle must contain a 'responses' list")
    provider = bundle["provider"]
    routes = ADAPTERS[provider].ROUTES
    engines = _Engines(provider)

    records: dict[str, tuple[str, dict]] = {}
    issues: list[dict] = []
    responses_meta, unrouted, filtered = [], [], []

    for index, response in enumerate(bundle["responses"]):
        if not isinstance(response, dict) or not isinstance(response.get("endpoint"), str):
            raise ValueError(f"Response {index}: needs an 'endpoint' string")
        endpoint = response["endpoint"]
        params = response.get("params") or {}
        if not isinstance(params, dict):
            raise ValueError(f"Response {index} ({endpoint}): 'params' must be an object")
        body = contracts.prepare(provider, response)
        issues += [{**warning, "response": index} for warning in contracts.validate(provider, endpoint, body)]

        endpoint_routes = routes.get(endpoint)
        if not endpoint_routes:
            # Valid contract response with no canonical record type (e.g. UKG
            # deduction-code catalog): preserved verbatim, never dropped.
            unrouted.append({"response": index, "endpoint": endpoint, "params": params, "body": body})
            continue
        meta = {"response": index, "endpoint": endpoint, "params": params}
        if isinstance(body, dict):
            wrapper = _wrapper(body, [route["records"] for route in endpoint_routes])
            if wrapper:
                meta["wrapper"] = wrapper
        #stored parts of the body that are not records
        responses_meta.append(meta)

        for route in endpoint_routes:
            engine = engines.get(route, endpoint)
            # A wrapped section (e.g. the salaries list) is one record as a whole.
            found = [(body, None, ())] if route.get("wrap") else iterate(body, route["records"])
            for record, parent, json_path in found:
                where = "/".join(str(part) for part in json_path) or "<body>"
                scope = {"params": params, "record": record, "parent": parent}
                if any(_lookup(record, path) != expected for path, expected in (route.get("where") or {}).items()):
                    #sets aside the values that are unrelated to the entity data type
                    filtered.append({"response": index, "endpoint": endpoint, "path": where,
                                     "reason": f"not a {route['type']} record", "record": record})
                    continue
                for left, right in route.get("check") or []:
                    a, b = render(left, scope), render(right, scope)
                    if a is not None and b is not None and a != b:
                        raise ValueError(f"{endpoint} {where}: params owner {right} = {b!r} "
                                         f"conflicts with response {left} = {a!r}")
                # Policy rule 5: a single-record response without its own id takes
                # it from params (e.g. UKG statement detail -> pay_statement_id).
                filled = {field: render(template, scope)
                          for field, template in (route.get("fill_record") or {}).items()
                          if record.get(field) in (None, "")}
                if filled:
                    record = {**record, **{k: v for k, v in filled.items() if v is not None}}
                    scope["record"] = record
                key = _first(route["id"], scope)
                if key is None:
                    raise ValueError(f"{endpoint} {where}: cannot build {route['type']} id from "
                                     f"{route['id']!r}; a required value is missing")
                source = deepcopy(record)
                for path in route.get("ignore") or []:
                    _drop(source, path)
                if route.get("wrap"):
                    source = {route["wrap"]: source}
                #source - deepcopy, context - extra values that aren't in the body, metadata - error response, endpoint, path where the record is found
                canonical = engine.map(source, context=_context(route, scope), metadata={
                    "sources": [{"response": index, "endpoint": endpoint, "path": where}]})
                data = canonical.model_dump(mode="json", exclude_unset=True)
                for field, template in (route.get("defaults") or {}).items():
                    if data.get(field) is None:
                        data[field] = render(template, scope)
                record_id = f"{provider}:{route['type']}:{key}"
                data["id"] = record_id
                for ref, (ref_type, template) in (route.get("refs") or {}).items():
                    ref_key = render(template, scope)
                    if ref_key is None:
                        issues.append({"severity": "warning", "code": "missing_ref", "record_id": record_id,
                                       "path": ref, "message": f"No value for {template}; ref left empty."})
                        continue
                    data[ref] = f"{provider}:{ref_type}:{ref_key}"
                # checks if the id exists in records(meaning if the python dict for it exists or not)
                # if yes, dont save it in the records dict again, instead merge it, if no - save it
                if record_id in records:
                    _merge(records[record_id][1], data, record_id, issues)
                else:
                    records[record_id] = (route["type"], data)

    # Merged records are validated again: fragments must still form a valid record.
    # JSON round trip, because the strict models accept dates only as JSON strings.
    collections = {name: [] for name in COLLECTIONS.values()}
    for record_id, (record_type, data) in records.items():
        model = MODELS[record_type].model_validate_json(json.dumps(data))
        collections[COLLECTIONS[record_type]].append(model.model_dump(mode="json", exclude_unset=True))

    known = set(records)
    for collection in collections.values():
        for record in collection:
            for ref in _REFS:
                if record.get(ref) and record[ref] not in known:
                    issues.append({"severity": "info", "code": "dangling_link", "record_id": record["id"],
                                   "path": ref, "message": f"{record[ref]} is not in this bundle."})

    provider_fields = {}
    if unrouted:
        provider_fields["unrouted_responses"] = unrouted
    if filtered:
        provider_fields["filtered_records"] = filtered
    document = CanonicalDocument(
        provider=provider, **collections,
        provider_fields={provider: provider_fields} if provider_fields else {},
        source_metadata={provider: {"responses": responses_meta}},
        issues=issues,
    )
    return document.model_dump(mode="json", exclude_unset=True)
