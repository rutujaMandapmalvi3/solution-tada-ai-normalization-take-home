# Mapping-rule checks. Input: YAML rules, the contract schema of the source record and the canonical model. Output: nothing, or a ValueError.
"""Check mapping rules before any record is mapped.

Every source path must exist in the contract schema, every target path in the
canonical model, object/list rules need object/list shapes, and helpers must exist.
"""
from __future__ import annotations

import types
from typing import Any, Union, get_args, get_origin

from pydantic import BaseModel

from .contracts import Schema
from .helpers.mapping import validate_helper
from .mapping_config import FieldMapping, ListMapping


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


# Checks field paths, nested rule types and available helpers before mapping.
# Checks every rule's source path, target path and helper before any mapping.
def check_rules(rules, source_schema, target_type, provider, root=False):
    for rule in rules:
        if root and rule.target.split(".")[0] in ("provider", "source_metadata", "source_extras"):
            raise ValueError(f"Engine-owned target cannot be mapped: {rule.target!r}")
        reserved = f"provider_fields.{provider}.unmapped"
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
        check_rules(rule.fields, nested_schema, target_annotation, provider)
