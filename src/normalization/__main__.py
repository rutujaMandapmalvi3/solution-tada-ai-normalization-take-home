# CLI entry point (`python -m normalization`): list-providers, check-inputs, normalize.
# `normalize` checks provider readiness, reads the --input JSON, calls the provider
# adapter, and writes the result to --output (refuses to overwrite an existing file).
"""Local entry point. Transformation output schema is chosen by the candidate."""
import argparse
import json
import sys
from pathlib import Path

from .adapters import ADAPTERS, ENTITIES
from .references import all_readiness_issues, load_reference, readiness_issues



# These reference-pack limitations are visible warnings, not unreadable-input errors.
_REFERENCE_WARNINGS = {
    "Lookup contents are a template or remain unverified.",
    "Reference version is missing.",
    "Candidate-distribution permission has not been verified.",
    "OpenAPI artifact is absent or unverified.",
    "Approved OpenAPI filename is missing.",
    "Approved OpenAPI file must exist inside the provider openapi directory.",
    "OpenAPI provenance/version/checksum metadata is incomplete.",
}


# Attach reference provenance without replacing existing mapping metadata.
def _add_reference_warnings(result, provider, reference, issues):
    pack = {
        "provider": provider,
        "reference_version": reference.get("reference_version"),
        "distribution_status": (reference.get("distribution") or {}).get("status"),
        "warnings": list(issues),
    }
    if isinstance(result, list):
        if not result:
            # An empty employee list has no record on which to retain warnings.
            result = {"employees": [], "source_metadata": {}}
        else:
            for record in result:
                record.setdefault("source_metadata", {}).setdefault(provider, {})["reference_pack"] = dict(pack)
            return result
    result.setdefault("source_metadata", {}).setdefault(provider, {})["reference_pack"] = pack
    return result


def main(argv=None):
    # Define the CLI commands and accepted arguments.
    parser = argparse.ArgumentParser(description="Tada AI normalization starter")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list-providers")
    commands.add_parser("check-inputs")
    run = commands.add_parser("normalize")
    run.add_argument("--provider", choices=ADAPTERS, required=True)
    run.add_argument("--entity", choices=ENTITIES, required=True)
    run.add_argument("--input", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--client-id", help="Original request client ID for PrismHR employee input")
    run.add_argument("--employee-id", help="Employee owner for direct-deposit or deduction input")
    # Parse command-line arguments into the selected command and its inputs.
    args = parser.parse_args(argv)
    if args.command == "list-providers":
        print("\n".join(ADAPTERS))
        return 0
    if args.command == "check-inputs":
        issues = all_readiness_issues()
        print(json.dumps(issues, indent=2))
        return 2 if any(issues.values()) else 0
    requires_client_id = args.provider == "prismhr" and args.entity == "employee"
    if requires_client_id and (args.client_id is None or not args.client_id.strip()):
        parser.error("--client-id is required and must be nonblank for PrismHR employee normalization")
    requires_employee_id = args.entity in ("direct_deposit", "deduction")
    if requires_employee_id and (args.employee_id is None or not args.employee_id.strip()):
        parser.error(f"--employee-id is required and must be nonblank for {args.entity} normalization")
    # Check the selected provider reference before processing input data.
    issues = readiness_issues(args.provider)
    errors = [issue for issue in issues if issue not in _REFERENCE_WARNINGS]
    reference_warnings = [issue for issue in issues if issue in _REFERENCE_WARNINGS]
    if errors:
        print(json.dumps({"provider": args.provider, "readiness_issues": errors}, indent=2), file=sys.stderr)
        return 2
    if reference_warnings:
        print("Warning: " + json.dumps({"provider": args.provider,
              "reference_warnings": reference_warnings}), file=sys.stderr)
    try:
        # Open the input JSON file for reading.
        with args.input.open(encoding="utf-8") as stream:
            # Read and deserialize JSON into Python dictionaries, lists, and values.
            response = json.load(stream)
        # Select the provider module from ADAPTERS using the requested provider name.
        # Call normalize with the entity, deserialized response, and loaded reference.
        reference = load_reference(args.provider)
        if requires_client_id:
            result = ADAPTERS[args.provider].normalize(
                args.entity, response, reference, client_id=args.client_id
            )
        elif requires_employee_id:
            result = ADAPTERS[args.provider].normalize(
                args.entity, response, reference, employee_id=args.employee_id
            )
        else:
            result = ADAPTERS[args.provider].normalize(args.entity, response, reference)
        if reference_warnings:
            result = _add_reference_warnings(result, args.provider, reference, reference_warnings)
        # Serialize first and refuse overwriting an existing file in this scaffold.
        serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
        # Create the output file and write the serialized result.
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(serialized)
    # Report file, parsing, serialization, or adapter failures to the CLI caller.
    except (OSError, ValueError, TypeError, NotImplementedError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
