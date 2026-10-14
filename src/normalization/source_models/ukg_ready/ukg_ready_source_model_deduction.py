"""UKG Ready deduction source models.

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


class UKGReadyDeductionResponse(BaseModel):
    """Cached schema path: 132."""
    model_config = ConfigDict(extra="allow")

    deductions: List[UKGReadyDeductionResponseDeductionsItem]


class UKGReadyDeductionResponseDeductionsItem(BaseModel):
    """Cached schema path: 132/deductions[]."""
    model_config = ConfigDict(extra="allow")

    id: int
    deduction: Optional[UKGReadyDeductionResponseDeductionsItemDeduction] = None
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    sequence: Optional[int] = None
    links: Optional[UKGReadyDeductionResponseDeductionsItemLinks] = Field(default=None, alias="_links")


class UKGReadyDeductionResponseDeductionsItemDeduction(BaseModel):
    """Cached schema path: 132/deductions[]/deduction."""
    model_config = ConfigDict(extra="allow")

    code: Optional[str] = None
    name: Optional[str] = None


class UKGReadyDeductionResponseDeductionsItemLinks(BaseModel):
    """Cached schema path: 132/deductions[]/_links."""
    model_config = ConfigDict(extra="allow")

    self: Optional[str] = None


class UKGReadyDeductionCodesResponse(BaseModel):
    """Cached schema path: 244."""
    model_config = ConfigDict(extra="allow")

    items: List[UKGReadyDeductionCodesResponseItemsItem]


class UKGReadyDeductionCodesResponseItemsItem(BaseModel):
    """Cached schema path: 244/items[]."""
    model_config = ConfigDict(extra="allow")

    code: Optional[str] = None
    external_id: Optional[str] = None
    name: Optional[str] = None
    # Live-only field; type observed in the saved response.
    id: Optional[int]


class UKGReadyBenefitsResponse(BaseModel):
    """Cached schema path: 119."""
    model_config = ConfigDict(extra="allow")

    benefits: List[UKGReadyBenefitsResponseBenefitsItem]


class UKGReadyBenefitsResponseBenefitsItem(BaseModel):
    """Cached schema path: 119/benefits[]."""
    model_config = ConfigDict(extra="allow")

    id: int
    employee: Optional[UKGReadyBenefitsResponseBenefitsItemEmployee] = None
    name: Optional[str] = None
    coverage_level: Optional[str] = None
    benefit_plan: Optional[UKGReadyBenefitsResponseBenefitsItemBenefitPlan] = None
    coverage_effective_from: Optional[str] = None
    coverage_effective_to: Optional[str] = None


class UKGReadyBenefitsResponseBenefitsItemEmployee(BaseModel):
    """Cached schema path: 119/benefits[]/employee."""
    model_config = ConfigDict(extra="allow")

    account_id: Optional[float] = None


class UKGReadyBenefitsResponseBenefitsItemBenefitPlan(BaseModel):
    """Cached schema path: 119/benefits[]/benefit_plan."""
    model_config = ConfigDict(extra="allow")

    id: int
    # Type follows the documented string enum; membership checks are deferred.
    currency: Optional[str] = None


class UKGReadyDeductionInput(BaseModel):
    """Project input combining assignment, lookup, and benefit responses."""
    model_config = ConfigDict(extra="allow")

    assignments: Optional[UKGReadyDeductionResponse] = None
    code_lookup: Optional[UKGReadyDeductionCodesResponse] = None
    benefits: Optional[UKGReadyBenefitsResponse] = None

    @classmethod
    def validate_response(cls, response: Any) -> UKGReadyDeductionInput:
        if not isinstance(response, dict):
            return cls.model_validate(response)
        payload = dict(response)
        # Adapt documented native responses into explicit supplemental sections.
        if "deductions" in response:
            if "assignments" in response:
                raise ValueError("Supply assignments or native deductions, not both")
            payload["assignments"] = response
        if "items" in response:
            if "code_lookup" in response:
                raise ValueError("Supply code_lookup or native items, not both")
            payload["code_lookup"] = response
        if "benefits" in response and isinstance(response["benefits"], list):
            payload["benefits"] = {"benefits": response["benefits"]}
        return cls.model_validate(payload)
