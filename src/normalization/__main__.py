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
    # Check the selected provider reference before processing input data.
    issues = readiness_issues(args.provider)
    if issues:
        print(json.dumps({"provider": args.provider, "readiness_issues": issues}, indent=2), file=sys.stderr)
        return 2
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
        else:
            result = ADAPTERS[args.provider].normalize(args.entity, response, reference)
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
