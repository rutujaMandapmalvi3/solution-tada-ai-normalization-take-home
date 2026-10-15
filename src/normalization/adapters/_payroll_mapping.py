"""Map validated payroll record families without combining their identities."""
from importlib.resources import as_file, files
from ..mapping_engine import MappingEngine, load_mapping_config
from ..canonical_models.canonical_model_payroll import (
    CanonicalPayrollRun, CanonicalPaycheckHeader, CanonicalPaycheck, CanonicalPayrollResult,
)


# Maps each supplied family separately and retains section/index provenance.
def map_payroll(provider, families, metadata):
    directory = "ukg_ready" if provider == "ukg-ready" else provider
    outputs = {"payroll_runs": [], "paycheck_headers": [], "paychecks": []}
    models = {"payroll_run": ("payroll_runs", CanonicalPayrollRun),
              "paycheck_header": ("paycheck_headers", CanonicalPaycheckHeader),
              "paycheck": ("paychecks", CanonicalPaycheck)}
    engines = {}
    for role, section, records in families:
        if not records:
            continue
        target, output_model = models[role]
        key = (role, type(records[0]))
        if key not in engines:
            resource = files("normalization").joinpath(f"mappings/{directory}/{role}.yaml")
            with as_file(resource) as path:
                config = load_mapping_config(path)
            engines[key] = MappingEngine(config, key[1], output_model)
        for index, record in enumerate(records):
            outputs[target].append(engines[key].map(record, metadata={
                "source_location": {"section": section, "record_index": index},
            }))
    return CanonicalPayrollResult(provider=provider, **outputs,
        source_metadata={provider: {"response": metadata}},
    ).model_dump(mode="json", exclude_unset=True)
