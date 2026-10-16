# Command-line interface. Input: a command plus --input bundle JSON and --output path. Output: the canonical document file, stderr messages and an exit code.
# CLI entry point (`python -m normalization`): list-providers, check-inputs, normalize.
# `normalize` reads one provider bundle (--input), checks provider readiness,
# runs the pipeline and writes one canonical document to --output (never overwrites).
"""Local entry point. Transformation output schema is chosen by the candidate."""
import argparse
import json
import sys
from pathlib import Path

from .adapters import ADAPTERS
from .pipeline import normalize_bundle
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


# Attach reference provenance to the document without replacing pipeline metadata.
# Records reference-pack warnings once in the document's source_metadata.
def _add_reference_warnings(document, provider, reference, issues):
    document.setdefault("source_metadata", {}).setdefault(provider, {})["reference_pack"] = {
        "provider": provider,
        "reference_version": reference.get("reference_version"),
        "distribution_status": (reference.get("distribution") or {}).get("status"),
        "warnings": list(issues),
    }
    return document


# Parses the command, checks reference readiness, runs the pipeline and writes the document.
def main(argv=None):
    # Define the CLI commands and accepted arguments.
    parser = argparse.ArgumentParser(description="Tada AI normalization starter")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list-providers")
    commands.add_parser("check-inputs")
    run = commands.add_parser("normalize", help="normalize one provider bundle into one canonical document")
    run.add_argument("--input", type=Path, required=True,
                     help='bundle JSON: {"provider": ..., "responses": [{"endpoint", "params", "body"}]}')
    run.add_argument("--output", type=Path, required=True)
    # Parse command-line arguments into the selected command and its inputs.
    args = parser.parse_args(argv)
    if args.command == "list-providers":
        print("\n".join(ADAPTERS))
        return 0
    if args.command == "check-inputs":
        issues = all_readiness_issues()
        print(json.dumps(issues, indent=2))
        return 2 if any(issues.values()) else 0
    try:
        # Open the bundle and deserialize JSON into Python dictionaries and lists.
        with args.input.open(encoding="utf-8") as stream:
            # Input: The stream containing JSON text.
            # Output: A Python dictionary containing nested dictionaries, lists and scalar values.
            bundle = json.load(stream)
        provider = bundle.get("provider") if isinstance(bundle, dict) else None
        if provider not in ADAPTERS:
            raise ValueError(f"Bundle 'provider' must be one of {', '.join(ADAPTERS)}")
        # Check the provider reference before processing input data.
        issues = readiness_issues(provider)
        errors = [issue for issue in issues if issue not in _REFERENCE_WARNINGS]
        reference_warnings = [issue for issue in issues if issue in _REFERENCE_WARNINGS]
        if errors:
            print(json.dumps({"provider": provider, "readiness_issues": errors}, indent=2), file=sys.stderr)
            return 2
        if reference_warnings:
            print("Warning: " + json.dumps({"provider": provider,
                  "reference_warnings": reference_warnings}), file=sys.stderr)
        document = normalize_bundle(bundle)
        if reference_warnings:
            document = _add_reference_warnings(document, provider, load_reference(provider),
                                               reference_warnings)
        # Serialize first and refuse overwriting an existing file.
        serialized = json.dumps(document, indent=2, allow_nan=False) + "\n"
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(serialized)
    # Report file, parsing, contract, mapping or serialization failures to the caller.
    except (OSError, ValueError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
