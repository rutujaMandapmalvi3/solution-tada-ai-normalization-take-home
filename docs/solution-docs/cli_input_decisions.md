# CLI input

## Decisions

| Decision | Why |
|---|---|
| `--provider` and `--entity` are removed; the command is `normalize --input <bundle> --output <file>`. Record types come from each endpoint's routes, not from an entity value. | Flexibility: one run normalizes every entity in the bundle, so records merge and links between entities are checked in the same run. |

## Assumptions

| Assumption | Why |
|---|---|
| Every bundle has a top-level `provider` field (`prismhr`, `isolved` or `ukg-ready`). | It selects the provider's adapter, so no CLI flag is needed. |
