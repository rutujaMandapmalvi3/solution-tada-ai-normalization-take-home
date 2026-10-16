# Bundle pipeline. Input: a provider bundle {provider, responses: [{endpoint, params, body}]}. Output: one canonical document dict.
"""Normalize a provider bundle into one canonical document.

Bundle format:
    {"provider": "prismhr",
     "responses": [{"endpoint": "<contract path>", "params": {...}, "status": 200, "body": ...}]}

Per response: contracts.prepare -> contracts.validate -> the provider adapter's
routes for that endpoint -> MappingEngine per record -> id/ref stamping.
Then: merge by id -> canonical re-validation -> link check -> document.
Ids, refs and merges follow docs/solution-docs/DECISIONS.md section 4.
"""
from __future__ import annotations

import json
import re
from copy import deepcopy
from dataclasses import dataclass, field
from importlib.resources import as_file, files
from typing import Any

from . import contracts
from .adapters import ADAPTERS
from .adapters.route import Route
from .canonical_models.canonical_document import COLLECTIONS, MODELS, CanonicalDocument
from .helpers.mapping import identifier
from .mapping_config import load_mapping_config
from .mapping_engine import MappingEngine

_PLACEHOLDER = re.compile(r"\{(params|record|parent)\.([^}]+)\}")
_REFS = ("company_ref", "employee_ref", "payroll_run_ref")


# ---------------------------------------------------------------- templates
# Reads a dotted path from a value; None when missing.
def _get_nested_value(value: Any, dotted_path: str) -> Any:
    for segment in dotted_path.split("."):
        value = value.get(segment) if isinstance(value, dict) else None
    return value


# Fills the {params|record|parent.x} placeholders of a template (id, ref, check, context)
# from template_values; None if any value is missing.
def render(template: str, template_values: dict) -> str | None:
    """Fill {params.x} / {record.x} / {parent.x}; None when any value is missing."""
    missing = False

    # Replaces one placeholder with its value normalized as an identifier.
    def fill(match):
        nonlocal missing
        source_name, dotted_path = match.group(1), match.group(2)
        value = identifier(_get_nested_value(template_values.get(source_name), dotted_path)).value
        if value in (None, ""):
            missing = True
            return ""
        return value

    text = _PLACEHOLDER.sub(fill, template)
    return None if missing else text


# Renders templates in order and returns the first one that succeeds.
def _render_first(templates: str | list[str], template_values: dict) -> str | None:
    for template in templates if isinstance(templates, list) else [templates]:
        value = render(template, template_values)
        if value is not None:
            return value
    return None


# Builds a route's engine context from templates and literal values.
def _mapper_context(route: Route, template_values: dict) -> dict:
    """Route context: templates are rendered, literals (including None) pass through."""
    return {name: render(value, template_values) if isinstance(value, str) and "{" in value else value
            for name, value in (route.get("context") or {}).items()}


# ---------------------------------------------------------------- record paths
# Yields each record, its parent and its JSON path for a route's records path.
def _iter_records(body: Any, records_path: str):
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

    yield from walk(body, [segment for segment in records_path.split(".") if segment], None, ())


# Removes a dotted path from a record copy.
def _remove_nested_field(record: dict, dotted_path: str) -> None:
    *parent_names, field_name = dotted_path.split(".")
    parent = _get_nested_value(record, ".".join(parent_names)) if parent_names else record
    if isinstance(parent, dict):
        parent.pop(field_name, None)


# Returns the body minus its record collections (the response wrapper).
def _response_wrapper(body: dict, records_paths: list[str]) -> dict:
    """Body minus its record collections; every sibling field is kept.

    Each records path is removed up to its outermost list or object that the
    route maps ('employeeDeductions.deduction[]' removes only `deduction`;
    'employee[].directDeposit.achVoucher[]' removes `employee`). A route on the
    whole body ('') leaves no wrapper.
    """
    if any(records_path == "" for records_path in records_paths):
        return {}
    wrapper = deepcopy(body)
    for records_path in records_paths:
        segments = [segment for segment in records_path.split(".") if segment]
        first_list = next((position for position, segment in enumerate(segments) if segment.endswith("[]")),
                          len(segments) - 1)
        *parent_names, collection_name = [segment.removesuffix("[]") for segment in segments[:first_list + 1]]
        parent = _get_nested_value(wrapper, ".".join(parent_names)) if parent_names else wrapper
        if isinstance(parent, dict):
            parent.pop(collection_name, None)
    return wrapper


# ---------------------------------------------------------------- merge
# Merges `incoming` into `existing` (the saved record with the same id), in place.
# record_id and issues are for merge_conflict warnings; path_prefix (e.g. "provider_fields.")
# is set only on the recursive calls for nested objects.
def _merge_records(existing: dict, incoming: dict, record_id: str, issues: list[dict], path_prefix: str = "") -> None:
    """Fill missing fields, merge nested objects, join lists, report differing values."""
    for field_name, incoming_value in incoming.items():
        field_path = path_prefix + field_name
        existing_value = existing.get(field_name)
        if field_name not in existing or existing_value is None:
            existing[field_name] = incoming_value
        elif isinstance(existing_value, dict) and isinstance(incoming_value, dict):
            _merge_records(existing_value, incoming_value, record_id, issues, field_path + ".")
        elif isinstance(existing_value, list) and isinstance(incoming_value, list):
            existing[field_name] = existing_value + incoming_value
        elif existing_value != incoming_value and incoming_value is not None:
            issues.append({"severity": "warning", "code": "merge_conflict", "record_id": record_id,
                           "path": field_path,
                           "message": f"Kept {existing_value!r}; another response had {incoming_value!r}."})


# ---------------------------------------------------------------- run state
class _MapperCache:
    # Prepares an engine cache for one provider.
    def __init__(self, provider: str):
        self.provider = provider
        self.directory = "ukg_ready" if provider == "ukg-ready" else provider
        self.cache: dict[tuple, MappingEngine] = {}

    # Returns the engine for a route and endpoint, building it once.
    def get_mapper(self, route: Route, endpoint: str) -> MappingEngine:
        cache_key = (route["yaml"], endpoint, route["records"], route.get("wrap"))
        if cache_key not in self.cache:
            # A route may read its records with another endpoint's record schema
            # (UKG employee list items are summaries of the employee resource).
            schema_endpoint, schema_path = route.get("schema", (endpoint, route["records"]))
            schema = contracts.response_schema(self.provider, schema_endpoint).at(schema_path)
            if route.get("wrap"):
                # Section wrapper (e.g. {"salary_history": [...]}) so the YAML keeps
                # one record shape per canonical employee; the section is the contract body.
                schema = schema.wrap(route["wrap"])
            resource = files("normalization").joinpath(f"mappings/{self.directory}/{route['yaml']}.yaml")
            with as_file(resource) as yaml_path:
                config = load_mapping_config(yaml_path)
            # The engine checks the YAML rules against the schema and the canonical model
            # (MODELS[route["type"]], e.g. CanonicalEmployee) once, when it is built.
            self.cache[cache_key] = MappingEngine(config, schema, MODELS[route["type"]])
        return self.cache[cache_key]


@dataclass
class _RunState:
    """Everything collected while one bundle is normalized."""
    provider: str
    routes: dict[str, list[Route]]                                        # endpoint -> its routes
    mapper_cache: _MapperCache
    records_by_id: dict[str, tuple[str, dict]] = field(default_factory=dict)  # canonical id -> (record type, record)
    issues: list[dict] = field(default_factory=list)
    response_summaries: list[dict] = field(default_factory=list)            # endpoint, params, wrapper per response
    unrouted_responses: list[dict] = field(default_factory=list)            # valid responses no route maps
    filtered_records: list[dict] = field(default_factory=list)              # records a `where` filter rejected


@dataclass(frozen=True)
class _ResponseInfo:
    """Where a record came from."""
    index: int        # position in the bundle's responses list
    endpoint: str
    params: dict


# ---------------------------------------------------------------- orchestrator
# Runs prepare, validate, route, map, stamp, merge, re-validate and link check.
def normalize_bundle(bundle: Any) -> dict:
    run = _start_run(bundle)
    # Responses run in bundle order; index (0, 1, 2...) identifies each in issues and sources.
    for index, response in enumerate(bundle["responses"]):
        _normalize_response(run, index, response)
    records_by_type = _revalidate_records(run)
    _report_dangling_refs(run, records_by_type)
    return _build_output_document(run, records_by_type)


# Checks the bundle shape and returns an empty run for its provider.
def _start_run(bundle: Any) -> _RunState:
    if not isinstance(bundle, dict) or bundle.get("provider") not in ADAPTERS:
        raise ValueError(f"Bundle must be an object with provider in {sorted(ADAPTERS)}")
    if not isinstance(bundle.get("responses"), list):
        raise ValueError("Bundle must contain a 'responses' list")
    provider = bundle["provider"]
    # The provider's adapter supplies the route table.
    return _RunState(provider=provider, routes=ADAPTERS[provider].ROUTES, mapper_cache=_MapperCache(provider))


# Prepares and validates one response, then maps every record its routes describe.
def _normalize_response(run: _RunState, index: int, response: Any) -> None:
    if not isinstance(response, dict) or not isinstance(response.get("endpoint"), str):
        raise ValueError(f"Response {index}: needs an 'endpoint' string")
    endpoint = response["endpoint"]
    params = response.get("params") or {}
    if not isinstance(params, dict):
        raise ValueError(f"Response {index} ({endpoint}): 'params' must be an object")
    # Status and provider error checks, live renames.
    body = contracts.prepare(run.provider, response)
    # Schema validation: a wrong type stops the run; other drift (enum, length...) becomes warnings.
    run.issues += [{**warning, "response": index} for warning in contracts.validate(run.provider, endpoint, body)]

    # One route per record type the endpoint holds (e.g. employee and direct deposit).
    routes_for_endpoint = run.routes.get(endpoint)
    if not routes_for_endpoint:
        # Valid contract response with no canonical record type (e.g. UKG
        # deduction-code catalog): preserved verbatim, never dropped.
        run.unrouted_responses.append({"response": index, "endpoint": endpoint, "params": params, "body": body})
        return
    response_summary = {"response": index, "endpoint": endpoint, "params": params}
    if isinstance(body, dict):
        # The body's non-record fields (the wrapper) are kept in source_metadata.
        wrapper = _response_wrapper(body, [route["records"] for route in routes_for_endpoint])
        if wrapper:
            response_summary["wrapper"] = wrapper
    run.response_summaries.append(response_summary)

    response_info = _ResponseInfo(index=index, endpoint=endpoint, params=params)
    for route in routes_for_endpoint:
        mapper = run.mapper_cache.get_mapper(route, endpoint)
        for record, parent, json_path in _find_records(route, body):
            _normalize_record(run, route, mapper, response_info, record, parent, json_path)


# Yields the records a route maps: the whole body for a wrapped section, else each item on its records path.
def _find_records(route: Route, body: Any):
    # A wrapped section (e.g. the salaries list) is one record as a whole; otherwise
    # _iter_records yields each record with its parent record and JSON path.
    if route.get("wrap"):
        return [(body, None, ())]
    return _iter_records(body, route["records"])


# Runs the record steps in order: filter, owner check, fill id, id key, map, id/refs, save or merge.
def _normalize_record(run: _RunState, route: Route, mapper: MappingEngine, response_info: _ResponseInfo,
                      record: dict, parent: Any, json_path: tuple) -> None:
    # e.g. "employee/0": where the record sits in the body, used in messages and sources.
    record_path = "/".join(str(part) for part in json_path) or "<body>"
    # What templates can read: the response params, the record and its parent record.
    template_values = {"params": response_info.params, "record": record, "parent": parent}
    if not _matches_route_filter(route, record):
        # Records of another type are kept in provider_fields, never dropped.
        run.filtered_records.append({"response": response_info.index, "endpoint": response_info.endpoint,
                                     "path": record_path, "reason": f"not a {route['type']} record",
                                     "record": record})
        return
    _ensure_owner_matches(route, template_values, response_info, record_path)
    record = _fill_missing_source_fields(route, record, template_values)
    template_values["record"] = record
    id_key = _build_id_key(route, template_values, response_info, record_path)
    canonical_record = _map_to_canonical(route, mapper, record, template_values, response_info, record_path)
    record_id = _attach_id_and_refs(run, route, canonical_record, id_key, template_values)
    _save_or_merge_record(run, route["type"], record_id, canonical_record)


# True when the record passes the route's `where` filter (or the route has none).
def _matches_route_filter(route: Route, record: dict) -> bool:
    return all(_get_nested_value(record, field_path) == expected
               for field_path, expected in (route.get("where") or {}).items())


# Stops the run when a params owner id disagrees with the owner id in the body.
def _ensure_owner_matches(route: Route, template_values: dict, response_info: _ResponseInfo,
                          record_path: str) -> None:
    # e.g. "check": [("{record.id}", "{params.clientId}")]
    for body_template, params_template in route.get("check") or []:
        body_owner = render(body_template, template_values)
        params_owner = render(params_template, template_values)
        if body_owner is not None and params_owner is not None and body_owner != params_owner:
            raise ValueError(f"{response_info.endpoint} {record_path}: params owner {params_template} = "
                             f"{params_owner!r} conflicts with response {body_template} = {body_owner!r}")


# Fills fields the record lacks (e.g. its own id) from params, as the route's `fill_record` says.
def _fill_missing_source_fields(route: Route, record: dict, template_values: dict) -> dict:
    # Policy rule 5: a single-record response without its own id takes
    # it from params (e.g. UKG statement detail -> pay_statement_id).
    filled_fields = {field_name: render(template, template_values)
                     for field_name, template in (route.get("fill_record") or {}).items()
                     if record.get(field_name) in (None, "")}
    if not filled_fields:
        return record
    return {**record, **{field_name: value for field_name, value in filled_fields.items() if value is not None}}


# Renders the route's id template into the record's id key; stops the run when a value is missing.
def _build_id_key(route: Route, template_values: dict, response_info: _ResponseInfo, record_path: str) -> str:
    id_key = _render_first(route["id"], template_values)
    if id_key is None:
        raise ValueError(f"{response_info.endpoint} {record_path}: cannot build {route['type']} id from "
                         f"{route['id']!r}; a required value is missing")
    return id_key


# Maps a copy of the record through the route's YAML and returns the canonical record as a dict.
def _map_to_canonical(route: Route, mapper: MappingEngine, record: dict, template_values: dict,
                      response_info: _ResponseInfo, record_path: str) -> dict:
    source = deepcopy(record)
    for ignore_path in route.get("ignore") or []:
        _remove_nested_field(source, ignore_path)
    if route.get("wrap"):
        source = {route["wrap"]: source}
    # context: route values the YAML reads with source_scope: context; metadata: where the record came from.
    canonical_model = mapper.map(source, context=_mapper_context(route, template_values), metadata={
        "sources": [{"response": response_info.index, "endpoint": response_info.endpoint, "path": record_path}]})
    canonical_record = canonical_model.model_dump(mode="json", exclude_unset=True)
    for field_name, template in (route.get("defaults") or {}).items():
        if canonical_record.get(field_name) is None:
            canonical_record[field_name] = render(template, template_values)
    return canonical_record


# Adds the canonical id and the refs to the record; a ref with a missing value becomes a warning.
def _attach_id_and_refs(run: _RunState, route: Route, canonical_record: dict, id_key: str,
                        template_values: dict) -> str:
    record_id = f"{run.provider}:{route['type']}:{id_key}"
    canonical_record["id"] = record_id
    for ref_name, (ref_type, template) in (route.get("refs") or {}).items():
        ref_id_key = render(template, template_values)
        if ref_id_key is None:
            run.issues.append({"severity": "warning", "code": "missing_ref", "record_id": record_id,
                               "path": ref_name, "message": f"No value for {template}; ref left empty."})
            continue
        canonical_record[ref_name] = f"{run.provider}:{ref_type}:{ref_id_key}"
    return record_id


# Saves a record under its id, or merges it into the record already saved under that id.
def _save_or_merge_record(run: _RunState, record_type: str, record_id: str, canonical_record: dict) -> None:
    if record_id in run.records_by_id:
        _merge_records(run.records_by_id[record_id][1], canonical_record, record_id, run.issues)
    else:
        run.records_by_id[record_id] = (record_type, canonical_record)


# ---------------------------------------------------------------- output
# Re-validates every saved record against its canonical model and groups the records by collection.
def _revalidate_records(run: _RunState) -> dict[str, list[dict]]:
    # Merged records are validated again: fragments must still form a valid record.
    # JSON round trip, because the strict models accept dates only as JSON strings.
    records_by_type = {collection_name: [] for collection_name in COLLECTIONS.values()}
    for record_type, canonical_record in run.records_by_id.values():
        canonical_model = MODELS[record_type].model_validate_json(json.dumps(canonical_record))
        records_by_type[COLLECTIONS[record_type]].append(canonical_model.model_dump(mode="json", exclude_unset=True))
    return records_by_type


# Assembles the canonical document from the grouped records and everything the run kept.
def _build_output_document(run: _RunState, records_by_type: dict[str, list[dict]]) -> dict:
    provider_fields = {}
    if run.unrouted_responses:
        provider_fields["unrouted_responses"] = run.unrouted_responses
    if run.filtered_records:
        provider_fields["filtered_records"] = run.filtered_records
    document = CanonicalDocument(
        provider=run.provider, **records_by_type,
        provider_fields={run.provider: provider_fields} if provider_fields else {},
        source_metadata={run.provider: {"responses": run.response_summaries}},
        issues=run.issues,
    )
    return document.model_dump(mode="json", exclude_unset=True)


# Adds a dangling_link issue for every ref whose target id is not in this bundle.
def _report_dangling_refs(run: _RunState, records_by_type: dict[str, list[dict]]) -> None:
    known_ids = set(run.records_by_id)
    for records in records_by_type.values():
        for canonical_record in records:
            for ref_name in _REFS:
                ref_id = canonical_record.get(ref_name)
                if ref_id and ref_id not in known_ids:
                    run.issues.append({"severity": "info", "code": "dangling_link",
                                       "record_id": canonical_record["id"], "path": ref_name,
                                       "message": f"{ref_id} is not in this bundle."})
