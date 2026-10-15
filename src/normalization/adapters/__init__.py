# Provider registry. Input: none. Output: ADAPTERS, mapping each provider name to its route-table module.
# Provider registry: maps provider names (bundle "provider") to adapter modules.
# Each adapter module exposes ROUTES: contract endpoint -> list of routes.
"""Provider dispatch: each adapter declares how its endpoints map to canonical records."""
from . import isolved, prismhr, ukg_ready

ADAPTERS = {"prismhr": prismhr, "isolved": isolved, "ukg-ready": ukg_ready}
