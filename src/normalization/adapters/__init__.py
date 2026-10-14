# Provider registry: maps CLI provider names to adapter modules (ADAPTERS)
# and lists the entity types the CLI accepts (ENTITIES).
"""Provider dispatch only; adapters are deliberately unimplemented."""
from . import isolved, prismhr, ukg_ready

ADAPTERS = {"prismhr": prismhr, "isolved": isolved, "ukg-ready": ukg_ready}
ENTITIES = ("company", "employee", "direct_deposit", "deduction", "payroll")
