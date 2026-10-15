# YAML mapping-rule models. Input: a parsed YAML mapping file (dict). Output: a validated MappingConfig of field/object/list rules.
"""Pydantic schema for mapping configuration loaded from YAML.

This module validates configuration only. It neither loads YAML nor executes
mappings. Source/target paths are relative to the current record or nested item;
list traversal is explicit through ListMapping, never inferred from a path.
Helpers will be resolved from a fixed registry by the future mapping engine.
"""
from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator, model_validator


# Hyphenated keys support provider aliases such as _links.country-fields.
Path = Annotated[str, Field(pattern=r"^[A-Za-z_][A-Za-z0-9_-]*(\.[A-Za-z_][A-Za-z0-9_-]*)*$")]
HelperName = Literal["identifier", "date", "number", "label", "postal_code", "pronouns", "conditional_number", "identifier_alias"]


class ConfigModel(BaseModel):
    """Reject misspelled configuration keys and implicit type conversions."""

    model_config = ConfigDict(extra="forbid", strict=True)


class Transform(ConfigModel):
    """A named helper and its JSON-compatible parameters; never executable code.

    Each helper will validate its own parameters when the engine is built.
    Naming a helper here does not mean its implementation already exists.
    """

    name: HelperName
    arguments: dict[str, JsonValue] = Field(default_factory=dict)


class FieldMapping(ConfigModel):
    """Copy a value, or pass one/multiple source values to a helper.

    A list of source paths is an ordered helper argument list, not array
    traversal. Context values (for example client_id) use source_scope=context.
    """

    kind: Literal["field"]
    source: Union[Path, Annotated[list[Path], Field(min_length=1)]]
    target: Path
    source_scope: Literal["record", "context"] = "record"
    transform: Transform | None = None

    # Rejects a multi-source field rule that has no combining helper.
    @model_validator(mode="after")
    def multiple_sources_need_helper(self) -> FieldMapping:
        if isinstance(self.source, list) and self.transform is None:
            raise ValueError("Multiple source paths require a named transform")
        return self


class ObjectMapping(ConfigModel):
    """Map a supplied nested object using rules relative to that object."""

    kind: Literal["object"]
    source: Path
    target: Path
    fields: list[MappingRule] = Field(min_length=1)

    # Rejects overlapping targets among an object rule's nested rules.
    @model_validator(mode="after")
    def check_destinations(self) -> ObjectMapping:
        _check_destinations(self.fields)
        return self


class ListMapping(ConfigModel):
    """Map a list of records in order, using rules relative to each item.

    Scalar lists can be copied by a FieldMapping instead. Source null/missing
    behavior and original values will follow the employee mapping contract.
    """

    kind: Literal["list"]
    source: Path
    target: Path
    fields: list[MappingRule] = Field(min_length=1)

    # Rejects overlapping targets among a list rule's nested rules.
    @model_validator(mode="after")
    def check_destinations(self) -> ListMapping:
        _check_destinations(self.fields)
        return self


MappingRule = Annotated[
    Union[FieldMapping, ObjectMapping, ListMapping], Field(discriminator="kind")
]


# Raises when two rules write the same or overlapping target.
def _check_destinations(rules: list[MappingRule]) -> None:
    """One rule owns each destination, including its nested subtree."""
    targets: set[str] = set()
    for rule in rules:
        for existing in targets:
            if (rule.target == existing or rule.target.startswith(existing + ".")
                    or existing.startswith(rule.target + ".")):
                raise ValueError(
                    f"Overlapping mapping targets: {existing!r} and {rule.target!r}. "
                    "Use one object/list rule or one multi-source helper instead."
                )
        targets.add(rule.target)


class MappingConfig(ConfigModel):
    """One provider/entity mapping file, applied after source validation.

    Paths and helper names are checked here. Whether a path exists in a source
    or canonical schema is a separate engine preflight check. Extras and source
    metadata preservation are engine responsibilities, not extra YAML rules.
    """

    version: Literal[1]
    provider: Literal["prismhr", "isolved", "ukg-ready"]
    entity: Literal["employee", "company", "direct_deposit", "deduction", "payroll"]
    fields: list[MappingRule] = Field(min_length=1)

    # Accepts only the integer version 1.
    @field_validator("version", mode="before")
    @classmethod
    def integer_version(cls, value: object) -> object:
        if type(value) is not int:
            raise ValueError("version must be the integer 1")
        return value

    # Rejects overlapping targets among a file's top-level rules.
    @model_validator(mode="after")
    def check_destinations(self) -> MappingConfig:
        _check_destinations(self.fields)
        return self


ObjectMapping.model_rebuild()
ListMapping.model_rebuild()
MappingConfig.model_rebuild()
