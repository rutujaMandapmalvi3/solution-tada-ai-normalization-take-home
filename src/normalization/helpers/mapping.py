# YAML transform helpers. Input: source values plus helper arguments from YAML. Output: Conversion(value, issue) results.
"""Reusable value conversions selected by YAML mapping rules.

No provider-specific field names, lookup meanings or API calls belong here.
"""
from dataclasses import dataclass
from datetime import date, datetime
import math
import re
from typing import Any, Callable


@dataclass(frozen=True)
class Conversion:
    value: Any
    issue: str | None = None


# Converts an id to text, keeping text ids and integral numbers.
def identifier(value: Any) -> Conversion:
    """Keep text IDs; stringify integral numbers without losing leading zeros."""
    if value is None or isinstance(value, str):
        return Conversion(value)
    if type(value) is int:
        return Conversion(str(value))
    if type(value) is float and math.isfinite(value) and value.is_integer():
        return Conversion(format(value, ".0f"))
    raise ValueError("Identifier must be text, an integral finite number, or null")


# Parses a source date into a date, or returns an issue.
def date_value(value: Any) -> Conversion:
    """Retain the written calendar date; never shift an offset to another zone."""
    if value is None:
        return Conversion(None)
    if isinstance(value, datetime):
        return Conversion(value.date())
    if isinstance(value, date):
        return Conversion(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return Conversion(None)
        try:
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
                return Conversion(date.fromisoformat(text))
            if re.match(r"^\d{4}-\d{2}-\d{2}[Tt ]", text):
                return Conversion(datetime.fromisoformat(text).date())
        except ValueError:
            pass
    return Conversion(None, "Invalid ISO date/datetime; original value retained")


# Converts a numeric value to a number, or returns an issue.
def number(value: Any) -> Conversion:
    if value is None:
        return Conversion(None)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return Conversion(None)
        if not re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", text):
            return Conversion(None, "Invalid numeric text; original value retained")
        value = text
    elif type(value) not in (int, float):
        return Conversion(None, "Expected numeric text or number; original value retained")
    try:
        converted = float(value)
        if math.isfinite(converted):
            return Conversion(converted)
    except (ValueError, OverflowError):
        pass
    return Conversion(None, "Nonfinite or invalid number; original value retained")


# Returns the number only when the selector equals the configured value.
def conditional_number(value: Any, selector: Any, *, equals: str) -> Conversion:
    """Select a verified numeric meaning; other values are preserved by mapping rules."""
    if selector == equals:
        return number(value)
    return Conversion(None)


# Translates a code through the YAML label table; unknown codes give an issue.
def label(value: Any, *, labels: dict[str, str]) -> Conversion:
    if value is None:
        return Conversion(None)
    # YAML dictionary keys are text; preserve Boolean meaning without treating 0/1 as flags.
    if type(value) is bool:
        key = "true" if value else "false"
        if key in labels:
            return Conversion(labels[key])
        return Conversion(None, "Unmapped Boolean label; original value retained")
    if isinstance(value, str):
        if value in labels:
            return Conversion(labels[value])
        if not value.strip():
            return Conversion(value)
        # Descriptive labels may differ in case; source codes are matched exactly.
        for meaning in labels.values():
            if value.casefold() == meaning.casefold():
                return Conversion(meaning)
    return Conversion(None, "Unmapped label/code; original value retained")


# Combines ZIP and ZIP+4 suffix as text, flagging conflicts.
def postal_code(zipcode: Any, suffix: Any) -> Conversion:
    if zipcode is not None and not isinstance(zipcode, str):
        return Conversion(None, "ZIP must be text; original components retained")
    if suffix is not None and not isinstance(suffix, str):
        return Conversion(zipcode, "ZIP suffix must be text; original components retained")
    if not zipcode or not zipcode.strip():
        issue = "ZIP suffix supplied without a base ZIP; original components retained" if suffix and suffix.strip() else None
        return Conversion(zipcode, issue)
    if not suffix or not suffix.strip():
        return Conversion(zipcode)
    if "-" in zipcode:
        if zipcode.rsplit("-", 1)[1] == suffix:
            return Conversion(zipcode)
        return Conversion(zipcode, "Conflicting ZIP suffix; original components retained")
    return Conversion(zipcode + "-" + suffix)


# Resolves one pronoun value from two fields, flagging conflicts.
def pronouns(first: Any, second: Any) -> Conversion:
    if any(value is not None and not isinstance(value, str) for value in (first, second)):
        return Conversion(None, "Invalid pronoun value; originals retained")
    meaningful = [value for value in (first, second)
                  if isinstance(value, str) and value.strip()]
    if len(meaningful) == 2 and meaningful[0] != meaningful[1]:
        return Conversion(None, "Conflicting pronoun values; both originals retained")
    if meaningful:
        return Conversion(meaningful[0])
    # Keep explicitly supplied blanks distinct from missing/null values.
    return Conversion(first if first is not None else second)


# Resolves two alias id fields to one value; null plus issue when they differ.
def identifier_alias(first: Any, second: Any) -> Conversion:
    left, right = identifier(first).value, identifier(second).value
    if left is None:
        return Conversion(right)
    if right is None or left == right:
        return Conversion(left)
    return Conversion(None, "Conflicting identifier aliases; both originals retained")


# Checks that a YAML transform names a known helper with valid arguments.
def validate_helper(name: str, source_count: int, arguments: dict[str, Any]) -> None:
    if name not in HELPERS:
        raise ValueError(f"Helper not implemented yet: {name}")
    expected_count = 2 if name in ("postal_code", "pronouns", "conditional_number", "identifier_alias") else 1
    if source_count != expected_count:
        raise ValueError(f"Helper {name!r} requires {expected_count} source path(s)")
    expected_arguments = ({"labels"} if name == "label" else
                          {"equals"} if name == "conditional_number" else set())
    if set(arguments) != expected_arguments:
        raise ValueError(f"Helper {name!r} expects arguments: {sorted(expected_arguments)}")
    if name == "conditional_number" and not isinstance(arguments["equals"], str):
        raise ValueError("conditional_number requires a string equals value")
    if name == "label":
        labels = arguments["labels"]
        if not isinstance(labels, dict) or any(not isinstance(k, str) or not isinstance(v, str)
                                                for k, v in labels.items()):
            raise ValueError("label requires a dictionary of string codes to string meanings")


# YAML selects only these functions; it cannot execute arbitrary Python code.
HELPERS: dict[str, Callable[..., Conversion]] = {
    "identifier": identifier,
    "identifier_alias": identifier_alias,
    "date": date_value,
    "number": number,
    "conditional_number": conditional_number,
    "label": label,
    "postal_code": postal_code,
    "pronouns": pronouns,
}
