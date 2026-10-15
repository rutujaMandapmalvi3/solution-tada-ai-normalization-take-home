"""Execute validated mapping rules on already-validated source records.

The engine is shared; provider/entity differences belong in YAML and helpers.
It returns a canonical Pydantic object, leaving final JSON serialization to the
caller. Adapter integration and full entity mapping files are separate steps.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import types
from typing import Any, Union, get_args, get_origin

from pydantic import BaseModel
import yaml
from yaml.constructor import ConstructorError

from .helpers.mapping import HELPERS, validate_helper
from .mapping_config import FieldMapping, ListMapping, MappingConfig, MappingRule


_MISSING = object()


# Converts a YAML object into a Python dictionary.
class _UniqueKeyLoader(yaml.SafeLoader):
    """Do not silently discard an earlier YAML rule/key."""

    # Converts a YAML object into a dictionary and rejects duplicate keys.
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
def load_mapping_config(path: str | Path) -> MappingConfig:
    """Safely parse YAML, reject duplicate keys, then validate rule structure."""
    with Path(path).open(encoding="utf-8") as stream:
        payload = yaml.load(stream, Loader=_UniqueKeyLoader)
    return MappingConfig.model_validate(payload)


# Gets the underlying type from an optional type, such as str from str or None.
def _optional_type(annotation):
    if get_origin(annotation) in (Union, types.UnionType):
        choices = [t for t in get_args(annotation) if t is not type(None)]
        if len(choices) == 1:
            return choices[0]
    return annotation


# Checks whether a type is a Pydantic model.
def _is_model(annotation):
    return isinstance(annotation, type) and issubclass(annotation, BaseModel)


# Finds the declared model field matching a name or alias.
def _field_name(model, segment):
    """Resolve declared Python names and JSON aliases, never object attributes."""
    if segment in model.model_fields:
        return segment
    for name, field in model.model_fields.items():
        aliases = [field.alias, field.serialization_alias]
        validation_alias = field.validation_alias
        if isinstance(validation_alias, str):
            aliases.append(validation_alias)
        aliases.extend(getattr(validation_alias, "choices", []))
        if segment in aliases:
            return name
    raise ValueError(f"Unknown declared field {segment!r} on {model.__name__}")


# Checks a nested field path and finds the type of its final value.
def _path_type(annotation, path):
    for segment in path.split("."):
        annotation = _optional_type(annotation)
        if annotation is Any:
            return Any
        if _is_model(annotation):
            annotation.model_rebuild()
            annotation = annotation.model_fields[_field_name(annotation, segment)].annotation
        elif get_origin(annotation) is dict:
            args = get_args(annotation)
            annotation = args[1] if args else Any
        else:
            raise ValueError(f"Cannot traverse {path!r}: use explicit object/list rules")
    return _optional_type(annotation)


# Reads a value from a nested path and reports when it was not supplied.
def _read(record, path):
    resolved = []
    for segment in path.split("."):
        if isinstance(record, BaseModel):
            name = _field_name(type(record), segment)
            resolved.append(name)
            if name not in record.model_fields_set:
                return _MISSING, tuple(resolved)
            record = getattr(record, name)
        elif isinstance(record, dict):
            resolved.append(segment)
            if segment not in record:
                return _MISSING, tuple(resolved)
            record = record[segment]
        elif record is None:
            return _MISSING, tuple(resolved)
        else:
            raise ValueError(f"Cannot traverse source path {path!r}")
    return record, tuple(resolved)


# Copies supplied values into ordinary Python structures without including model extras.
def _plain(value):
    """Copy declared, supplied source values; extras are preserved separately."""
    if isinstance(value, BaseModel):
        return {(field.alias or name): _plain(getattr(value, name))
                for name, field in type(value).model_fields.items()
                if name in value.model_fields_set}
    if isinstance(value, dict):
        return {key: _plain(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_plain(child) for child in value]
    return deepcopy(value)


# Collects known source fields that the mapping rules have not used.
def _remaining(value, consumed, path=()):
    """Retain declared fields not consumed by rules, in original nesting."""
    if path in consumed:
        return _MISSING
    if isinstance(value, BaseModel):
        result = {}
        for name, field in type(value).model_fields.items():
            if name not in value.model_fields_set:
                continue
            child = _remaining(getattr(value, name), consumed, path + (name,))
            if child is not _MISSING:
                result[field.alias or name] = child
        return result if result or not value.model_fields_set else _MISSING
    if isinstance(value, dict):
        result = {}
        for key, child in value.items():
            child = _remaining(child, consumed, path + (key,))
            if child is not _MISSING:
                result[key] = child
        return result if result or not value else _MISSING
    if isinstance(value, list):
        children = [_remaining(child, consumed, path + (index,))
                    for index, child in enumerate(value)]
        if value and all(child is _MISSING for child in children):
            return _MISSING
        return [{} if child is _MISSING else child for child in children]
    return deepcopy(value)


# Collects unknown source fields while keeping their nesting and list positions.
def _extras(value):
    """Retain recursively declared model_extra values and list-item positions."""
    if isinstance(value, BaseModel):
        result = deepcopy(value.model_extra or {})
        for name, field in type(value).model_fields.items():
            if name not in value.model_fields_set:
                continue
            child = _extras(getattr(value, name))
            if child is not _MISSING:
                key = field.alias or name
                if key in result:
                    raise ValueError(f"Extra-field collision at {key!r}")
                result[key] = child
        return result if result else _MISSING
    if isinstance(value, dict):
        result = {key: child for key, item in value.items()
                  if (child := _extras(item)) is not _MISSING}
        return result if result else _MISSING
    if isinstance(value, list):
        children = [_extras(child) for child in value]
        if all(child is _MISSING for child in children):
            return _MISSING
        return [{} if child is _MISSING else child for child in children]
    return _MISSING


# Writes a value at an output path without overwriting an existing value.
def _put(output, path, value):
    segments = path.split(".")
    for segment in segments[:-1]:
        existing = output.setdefault(segment, {})
        if not isinstance(existing, dict):
            raise ValueError(f"Target path collision at {path!r}")
        output = existing
    if segments[-1] in output:
        raise ValueError(f"Target path already populated: {path!r}")
    output[segments[-1]] = value


class MappingEngine:
    """Preflight rule paths/helpers, then map one validated source record.

    Remaining known fields live at provider_fields.<provider>.unmapped with
    their source nesting. This reserved branch avoids mixing original names
    with explicitly renamed provider fields. No adapters are called here.
    """

    # Sets up the engine and checks the rules against the source and output models.
    def __init__(self, config: MappingConfig, source_model: type[BaseModel],
                 output_model: type[BaseModel]):
        self.config = config.model_copy(deep=True)
        self.source_model = source_model
        self.output_model = output_model
        # Resolve source/canonical forward annotations before inspecting paths.
        # This builds schemas; it does not validate the input record again.
        self.source_model.model_rebuild()
        self.output_model.model_rebuild()
        self._preflight(self.config.fields, source_model, output_model, root=True)

    # Checks field paths, nested rule types and available helpers before mapping.
    def _preflight(self, rules, source_type, target_type, root=False):
        for rule in rules:
            if root and rule.target.split(".")[0] in ("provider", "source_metadata", "source_extras"):
                raise ValueError(f"Engine-owned target cannot be mapped: {rule.target!r}")
            reserved = f"provider_fields.{self.config.provider}.unmapped"
            if root and (rule.target == reserved or rule.target.startswith(reserved + ".")):
                raise ValueError(f"Reserved preservation target: {rule.target!r}")
            target_annotation = _path_type(target_type, rule.target)
            if isinstance(rule, FieldMapping):
                paths = rule.source if isinstance(rule.source, list) else [rule.source]
                if rule.source_scope == "record":
                    for path in paths:
                        _path_type(source_type, path)
                if rule.transform is not None:
                    validate_helper(rule.transform.name, len(paths), rule.transform.arguments)
                continue
            source_annotation = _path_type(source_type, rule.source)
            if isinstance(rule, ListMapping):
                if get_origin(source_annotation) is not list:
                    raise ValueError(f"List rule requires a list source: {rule.source!r}")
                source_annotation = get_args(source_annotation)[0]
                if target_annotation is not Any:
                    if get_origin(target_annotation) is not list:
                        raise ValueError(f"List rule requires a list target: {rule.target!r}")
                    target_annotation = get_args(target_annotation)[0]
            for annotation in (source_annotation, target_annotation):
                if annotation is not Any and not _is_model(annotation) and get_origin(annotation) is not dict:
                    raise ValueError("Object/list item rules require object-shaped source and target")
            self._preflight(rule.fields, source_annotation, target_annotation)

    # Maps one validated source record and returns a validated canonical object.
    def map(self, source: BaseModel, *, context: dict[str, Any] | None = None,
            metadata: dict[str, Any] | None = None) -> BaseModel:
        if not isinstance(source, self.source_model):
            raise TypeError(f"Expected validated {self.source_model.__name__}")
        output = {"provider": self.config.provider}
        consumed = set()
        original = {}
        issues = []
        self._apply(self.config.fields, source, output, context or {}, consumed,
                    original, issues)
        remaining = _remaining(source, consumed)
        if remaining is not _MISSING:
            _put(output, f"provider_fields.{self.config.provider}.unmapped", remaining)
        extras = _extras(source)
        if extras is not _MISSING:
            output["source_extras"] = {self.config.provider: extras}
        source_metadata = {}
        if metadata is not None:
            source_metadata[self.config.provider] = deepcopy(metadata)
        if original:
            source_metadata["original_values"] = original
        if issues:
            source_metadata["mapping_issues"] = issues
        if source_metadata:
            output["source_metadata"] = source_metadata
        return self.output_model.model_validate(output)

    # Applies each rule, calls its helper if needed and handles nested objects or lists.
    def _apply(self, rules, source, output, context, consumed, original, issues, prefix=()):
        for rule in rules:
            use_context = isinstance(rule, FieldMapping) and rule.source_scope == "context"
            record = context if use_context else source
            if isinstance(rule, FieldMapping):
                paths = rule.source if isinstance(rule.source, list) else [rule.source]
                reads = [_read(record, source_path) for source_path in paths]
                if all(value is _MISSING for value, relative in reads):
                    continue
                values = []
                source_paths = []
                for source_path, (value, relative) in zip(paths, reads):
                    absolute = prefix + relative
                    # Use the full configured path even if an ancestor is missing.
                    path = ("context." + source_path if use_context else
                            ".".join(str(part) for part in prefix + tuple(source_path.split("."))))
                    source_paths.append(path)
                    if value is _MISSING:
                        values.append(None)
                        continue
                    if not use_context:
                        consumed.add(absolute)
                    plain = _plain(value)
                    values.append(plain)
                    if rule.transform:
                        original[path] = deepcopy(plain)
                mapped = values[0]
                if rule.transform:
                    try:
                        conversion = HELPERS[rule.transform.name](
                            *values, **rule.transform.arguments
                        )
                    except ValueError as exc:
                        raise ValueError(f"{source_paths[0]}: {exc}") from exc
                    mapped = conversion.value
                    if conversion.issue:
                        issues.append({"source_path": source_paths[0], "reason": conversion.issue})
                _put(output, rule.target, mapped)
                continue
            value, relative = _read(record, rule.source)
            if value is _MISSING:
                continue
            absolute = prefix + relative
            path = ".".join(str(part) for part in absolute)
            if value is None:
                consumed.add(absolute)
                _put(output, rule.target, None)
            elif isinstance(rule, ListMapping):
                if not isinstance(value, list):
                    raise ValueError(f"Expected source list at {path}")
                items = []
                for index, item in enumerate(value):
                    mapped = {}
                    self._apply(rule.fields, item, mapped, context, consumed, original,
                                issues, absolute + (index,))
                    items.append(mapped)
                _put(output, rule.target, items)
                if not value:
                    consumed.add(absolute)
            else:
                mapped = {}
                self._apply(rule.fields, value, mapped, context, consumed, original,
                            issues, absolute)
                _put(output, rule.target, mapped)
