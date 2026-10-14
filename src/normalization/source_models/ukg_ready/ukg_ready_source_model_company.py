"""UKG Ready company source models.
The EIN lookup is not a company-detail endpoint or company-ID mapping.

Generated from cached GET response schemas, not an official OpenAPI contract.
Source names and types are retained. Optional fields accept missing/null;
required presence follows each schema. Unknown live fields are preserved.
Enum translation, numeric/date constraints, units, and business rules are
deferred. Every nested model records its schema index and field path.

Project validation policy: record IDs and documented required wrapper fields
require presence. Other fields accept missing/null; existing ID nullability
is retained. Reference IDs are optional unless they identify this record.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class UKGReadyEinsResponse(BaseModel):
    """Cached schema path: 249."""
    model_config = ConfigDict(extra="allow")

    items: List[UKGReadyEinsResponseItemsItem]


class UKGReadyEinsResponseItemsItem(BaseModel):
    """Cached schema path: 249/items[]."""
    model_config = ConfigDict(extra="allow")

    id: int
    ein_tax_id: Optional[str] = None
    ein_name: Optional[str] = None
    ein_currency_code: Optional[str] = None
    ein_country_id: Optional[str] = None
