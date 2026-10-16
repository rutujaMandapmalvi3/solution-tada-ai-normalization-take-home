# Mapping engine. Input: one source record dict, its contract Schema, YAML rules and context. Output: a validated canonical Pydantic record.
"""Execute validated mapping rules on already-validated source records.

The engine is shared; provider/entity differences belong in YAML and helpers.
Source records are plain dicts checked against their contract schema
(contracts.Schema); output is a canonical Pydantic object, leaving final JSON
serialization to the caller.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
import types
from typing import Any, Union, get_args, get_origin

from pydantic import BaseModel

from .contracts import Schema
import yaml
from yaml.constructor import ConstructorError

from .helpers.mapping import HELPERS, validate_helper
from .mapping_config import FieldMapping, ListMapping, MappingConfig, MappingRule


_MISSING = object()


# Converts a YAML object into a Python dictionary.
class _UniqueKeyLoader(yaml.SafeLoader):
    """Do not silently discard an earlier YAML rule/key."""

    # Converts a YAML object into a dictionary and rejects duplicate keys.
    # Builds a YAML mapping and rejects duplicate keys.
    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in seen
                seen.add(key)
            except TypeError as exc:
                raise ConstructorError(None, None, "Mapping keys must be scalar", key_node.start_mark) from exc
            if duplicate:
                raise ConstructorError(None, None, f"Duplicate YAML key: {key!r}", key_node.start_mark)
        return super().construct_mapping(node, deep=deep)


# Reads the YAML file and checks that its mapping rules are valid.
# Reads a YAML mapping file and validates it as a MappingConfig.
def load_mapping_config(path: str | Path) -> MappingConfig:
    """Safely parse YAML, reject duplicate keys, then validate rule structure."""
    with Path(path).open(encoding="utf-8") as stream:
        payload = yaml.load(stream, Loader=_UniqueKeyLoader)
    return MappingConfig.model_validate(payload)


# Gets the underlying type from an optional type, such as str from str or None.
# Unwraps Optional[X] to X.
def _optional_type(annotation):
    if get_origin(annotation) in (Union, types.UnionType):
        choices = [t for t in get_args(annotation) if t is not type(None)]
        if len(choices) == 1:
            return choices[0]
    return annotation


# Checks whether a type is a Pydantic model.
# True when an annotation is a Pydantic model class.
def _is_model(annotation):
    return isinstance(annotation, type) and issubclass(annotation, BaseModel)


# Checks a nested canonical (target) path and finds the type of its final value.
# Returns the canonical model type at a target path; raises on unknown fields.
def _path_type(annotation, path):
    for segment in path.split("."):
        annotation = _optional_type(annotation)
        if annotation is Any:
            return Any
        if _is_model(annotation):
            annotation.model_rebuild()
            if segment not in annotation.model_fields:
                raise ValueError(f"Unknown declared field {segment!r} on {annotation.__name__}")
            annotation = annotation.model_fields[segment].annotation
        elif get_origin(annotation) is dict:
            args = get_args(annotation)
            annotation = args[1] if args else Any
        else:
            raise ValueError(f"Cannot traverse {path!r}: use explicit object/list rules")
    return _optional_type(annotation)


# Checks a source path against the contract schema of the source record.
# Returns the contract schema at a source path; raises on unknown fields.
def _source_path(schema: Schema, path: str) -> Schema:
    try:
        return schema.at(path)
    except KeyError as exc:
        raise ValueError(f"Source path {path!r}: field {exc.args[0]!r} is not in the contract schema") from None


# Reads a value from a nested path and reports when it was not supplied.
# Reads a dotted path from a record, reporting values that are not supplied.
def _read_path(record, dotted_path):
    value = record
    resolved_path = []
    for segment in dotted_path.split("."):
        if isinstance(value, dict):
            resolved_path.append(segment)
            if segment not in value:
                return _MISSING, tuple(resolved_path)
            value = value[segment]
        elif value is None:
            return _MISSING, tuple(resolved_path)
        else:
            raise ValueError(f"Cannot traverse source path {dotted_path!r}")
    return value, tuple(resolved_path)


# Copies a supplied source value into an independent plain structure.
# Returns an independent copy of a source value.
def _copy_value(value):
    return deepcopy(value)


# Returns a property's schema, or None when no schema limits the fields.
def _child(schema, key):
    return None if schema is None else schema.child(key)


# True when the contract declares this field (or no schema limits it).
def _declared(schema, key):
    return schema is None or schema.is_open or key in schema.declared()


# Collects contract-declared source fields that the mapping rules have not used.
# Collects declared source fields that no rule consumed, keeping their nesting.
def _collect_unmapped(value, consumed_paths, schema=None, path=()):
    """Retain declared, unconsumed fields in original nesting (schema None = all declared)."""
    if path in consumed_paths:
        return _MISSING
    if isinstance(value, dict):
        result = {}
        for key, child in value.items():
            if not _declared(schema, key):
                continue  # undeclared fields belong to _collect_undeclared
            child = _collect_unmapped(child, consumed_paths, _child(schema, key), path + (key,))
            if child is not _MISSING:
                result[key] = child
        return result if result or not value else _MISSING
    if isinstance(value, list):
        items = None if schema is None else schema.items()
        children = [_collect_unmapped(child, consumed_paths, items, path + (index,))
                    for index, child in enumerate(value)]
        if value and all(child is _MISSING for child in children):
            return _MISSING
        return [{} if child is _MISSING else child for child in children]
    return deepcopy(value)


# Collects source fields the contract does not declare, keeping nesting and list positions.
# Collects source fields the contract does not declare, keeping their nesting.
def _collect_undeclared(value, schema=None):
    """Undeclared fields per the contract schema; open schemas declare everything."""
    if schema is None:
        return _MISSING
    if isinstance(value, dict):
        if schema.is_open:
            return _MISSING
        result = {}
        for key, child in value.items():
            if key not in schema.declared():
                result[key] = deepcopy(child)
                continue
            child = _collect_undeclared(child, schema.child(key))
            if child is not _MISSING:
                result[key] = child
        return result if result else _MISSING
    if isinstance(value, list):
        children = [_collect_undeclared(child, schema.items()) for child in value]
        if all(child is _MISSING for child in children):
            return _MISSING
        return [{} if child is _MISSING else child for child in children]
    return _MISSING


# Writes a value at an output path without overwriting an existing value.
# Writes a value at a dotted output path, refusing to overwrite.
def _write_path(output, dotted_path, value):
    segments = dotted_path.split(".")
    for segment in segments[:-1]:
        existing = output.setdefault(segment, {})
        if not isinstance(existing, dict):
            raise ValueError(f"Target path collision at {dotted_path!r}")
        output = existing
    if segments[-1] in output:
        raise ValueError(f"Target path already populated: {dotted_path!r}")
    output[segments[-1]] = value


@dataclass
class _MappingState:
    """What one map() call collects while its rules run."""
    context: dict                                                 # values rules read with source_scope: context
    consumed_paths: set = field(default_factory=set)              # source paths a rule used
    original_values: dict = field(default_factory=dict)           # source value before each transform
    issues: list = field(default_factory=list)                    # helper conversion issues


class MappingEngine:
    """Preflight rule paths/helpers, then map one validated source record.

    Remaining contract-declared fields live at provider_fields.<provider>.unmapped
    and undeclared fields at source_extras.<provider>, both with source nesting.
    """

    # Sets up the engine and checks the rules against the source schema and output model.
    # Stores the rules, source schema and output model, then preflights the rules.
    def __init__(self, config: MappingConfig, source_schema: Schema,
                 output_model: type[BaseModel]):
        self.config = config.model_copy(deep=True)
        self.source_schema = source_schema
        self.output_model = output_model
        self.output_model.model_rebuild()
        self._check_rules(self.config.fields, source_schema, output_model, root=True)

    # Checks field paths, nested rule types and available helpers before mapping.
    # Checks every rule's source path, target path and helper before any mapping.
    def _check_rules(self, rules, source_schema, target_type, root=False):
        for rule in rules:
            if root and rule.target.split(".")[0] in ("provider", "source_metadata", "source_extras"):
                raise ValueError(f"Engine-owned target cannot be mapped: {rule.target!r}")
            reserved = f"provider_fields.{self.config.provider}.unmapped"
            if root and (rule.target == reserved or rule.target.startswith(reserved + ".")):
                raise ValueError(f"Reserved preservation target: {rule.target!r}")
            target_annotation = _path_type(target_type, rule.target)
            if isinstance(rule, FieldMapping):
                source_paths = rule.source if isinstance(rule.source, list) else [rule.source]
                if rule.source_scope == "record":
                    for source_path in source_paths:
                        _source_path(source_schema, source_path)
                if rule.transform is not None:
                    validate_helper(rule.transform.name, len(source_paths), rule.transform.arguments)
                continue
            nested_schema = _source_path(source_schema, rule.source)
            if isinstance(rule, ListMapping):
                if not nested_schema.is_array and not nested_schema.is_open:
                    raise ValueError(f"List rule requires a list source: {rule.source!r}")
                nested_schema = nested_schema.items()
                if target_annotation is not Any:
                    if get_origin(target_annotation) is not list:
                        raise ValueError(f"List rule requires a list target: {rule.target!r}")
                    target_annotation = get_args(target_annotation)[0]
            if (target_annotation is not Any and not _is_model(target_annotation)
                    and get_origin(target_annotation) is not dict):
                raise ValueError("Object/list item rules require an object-shaped target")
            self._check_rules(rule.fields, nested_schema, target_annotation)

    # Maps one validated source record (a dict) and returns a validated canonical object.
    # Maps one record: applies rules, adds unmapped/extras/metadata, validates the output.
    def map(self, source: dict, *, context: dict[str, Any] | None = None,
            metadata: dict[str, Any] | None = None) -> BaseModel:
        if not isinstance(source, dict):
            raise TypeError("Expected a source record object (dict)")
        output = {"provider": self.config.provider}
        state = _MappingState(context=context or {})
        self._apply_rules(self.config.fields, source, output, state)
        unmapped = _collect_unmapped(source, state.consumed_paths, self.source_schema)
        if unmapped is not _MISSING:
            _write_path(output, f"provider_fields.{self.config.provider}.unmapped", unmapped)
        undeclared = _collect_undeclared(source, self.source_schema)
        if undeclared is not _MISSING:
            output["source_extras"] = {self.config.provider: undeclared}
        source_metadata = {}
        if metadata is not None:
            source_metadata[self.config.provider] = deepcopy(metadata)
        if state.original_values:
            source_metadata["original_values"] = state.original_values
        if state.issues:
            source_metadata["mapping_issues"] = state.issues
        if source_metadata:
            output["source_metadata"] = source_metadata
        return self.output_model.model_validate(output)

    # Applies each rule in order: field rules directly, object/list rules recursively.
    def _apply_rules(self, rules, source, output, state: _MappingState, path_prefix=()):
        for rule in rules:
            if isinstance(rule, FieldMapping):
                self._apply_field_rule(rule, source, output, state, path_prefix)
            else:
                self._apply_nested_rule(rule, source, output, state, path_prefix)

    # Reads the rule's source value(s), runs its helper if any and writes the target.
    def _apply_field_rule(self, rule, source, output, state: _MappingState, path_prefix):
        use_context = rule.source_scope == "context"
        read_from = state.context if use_context else source
        source_paths = rule.source if isinstance(rule.source, list) else [rule.source]
        reads = [_read_path(read_from, source_path) for source_path in source_paths]
        if all(value is _MISSING for value, relative_path in reads):
            return
        source_values = []
        display_paths = []
        for source_path, (value, relative_path) in zip(source_paths, reads):
            full_path = path_prefix + relative_path
            # Use the full configured path even if an ancestor is missing.
            display_path = ("context." + source_path if use_context else
                            ".".join(str(part) for part in path_prefix + tuple(source_path.split("."))))
            display_paths.append(display_path)
            if value is _MISSING:
                source_values.append(None)
                continue
            if not use_context:
                state.consumed_paths.add(full_path)
            copied = _copy_value(value)
            source_values.append(copied)
            if rule.transform:
                state.original_values[display_path] = deepcopy(copied)
        mapped_value = source_values[0]
        if rule.transform:
            try:
                conversion = HELPERS[rule.transform.name](
                    *source_values, **rule.transform.arguments
                )
            except ValueError as exc:
                raise ValueError(f"{display_paths[0]}: {exc}") from exc
            mapped_value = conversion.value
            if conversion.issue:
                state.issues.append({"source_path": display_paths[0], "reason": conversion.issue})
        _write_path(output, rule.target, mapped_value)

    # Maps an object or list rule by applying its sub-rules to the nested value (each item for a list).
    def _apply_nested_rule(self, rule, source, output, state: _MappingState, path_prefix):
        value, relative_path = _read_path(source, rule.source)
        if value is _MISSING:
            return
        full_path = path_prefix + relative_path
        display_path = ".".join(str(part) for part in full_path)
        if value is None:
            state.consumed_paths.add(full_path)
            _write_path(output, rule.target, None)
        elif isinstance(rule, ListMapping):
            if not isinstance(value, list):
                raise ValueError(f"Expected source list at {display_path}")
            mapped_items = []
            for index, item in enumerate(value):
                mapped_object = {}
                self._apply_rules(rule.fields, item, mapped_object, state, full_path + (index,))
                mapped_items.append(mapped_object)
            _write_path(output, rule.target, mapped_items)
            if not value:
                state.consumed_paths.add(full_path)
        else:
            mapped_object = {}
            self._apply_rules(rule.fields, value, mapped_object, state, full_path)
            _write_path(output, rule.target, mapped_object)
