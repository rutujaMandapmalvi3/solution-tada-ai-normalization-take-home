# Route type. Input: none. Output: Route, the keys one adapter route may set.
"""One route: how records of one canonical type are found in a response and mapped.

Templates use {params.x} (request params), {record.x} (the source record) and
{parent.x} (the enclosing record). A route is a plain dict; this type only documents it.
"""
from __future__ import annotations

from typing import TypedDict


class _RequiredRouteKeys(TypedDict):
    type: str                     # canonical record type, e.g. "employee"
    records: str                  # records path in the body, e.g. "employee[]", "" = the whole body
    yaml: str                     # mapping file name in mappings/<provider>/
    id: str | list[str]           # id-key template(s); the first one that renders is used


class Route(_RequiredRouteKeys, total=False):
    schema: tuple[str, str]       # (endpoint, records path) whose schema describes the records
    wrap: str                     # map the whole body as {wrap: body} (a section such as salaries)
    context: dict                 # extra values the YAML reads with source_scope: context
    ignore: list[str]             # record fields removed before mapping (mapped by another route)
    where: dict                   # field path -> required value; other records are filtered out
    check: list[tuple[str, str]]  # (body template, params template) owner pairs that must agree
    fill_record: dict             # record field -> template, filled from params when missing
    defaults: dict                # canonical field -> template, used when mapping left it empty
    refs: dict                    # ref name -> (parent record type, id-key template)
