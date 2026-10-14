"""Project-required fields: record IDs and documented wrapper requirements."""
import importlib
import inspect
import types
import typing
import unittest
from pathlib import Path

from pydantic import BaseModel, ValidationError

NAMED_RECORD_IDS = {'PrismHRBatchList': {'batchId'}, 'PrismHRPayrollVoucher': {'voucherId'}, 'PrismHRAutoPolicy': {'autoInsurancePolicyId'}, 'PrismHRI9ImageAudit': {'auditId'}, 'PrismHRAltEmployer': {'altEmployerId'}, 'PrismHRClientMasterPayCode': {'payCodeId'}, 'PrismHRClientMasterDeductionCode': {'deductionCodeId'}, 'PrismHREmployeeType': {'typeCodeId'}, 'PrismHREmployeeStatus': {'statusCodeId'}, 'PrismHRReason': {'reasonCodeId'}, 'PrismHRBatchByDateResponseBatchListPayGroup': {'payGroupId'}}
WRAPPER_REQUIRED = {'IsolvedEmployeePayItemResponse': set(), 'IsolvedEmployeeDirectDepositResponse': set(), 'IsolvedPagedModelItemListOfEmployeeModel': set(), 'IsolvedEmployeeSalaryResponse': set(), 'IsolvedPagedModelItemListOfCheckModel': set(), 'IsolvedPayrollRunHistoryResponse': set(), 'PrismHRGetClientMasterResponse': {'errorMessage', 'errorCode'}, 'PrismHRDeductionResponse': {'errorMessage', 'errorCode'}, 'PrismHRDirectDepositResponse': {'errorCode', 'errorMessage'}, 'PrismHREmployeeResponse': {'errorMessage', 'errorCode'}, 'PrismHRPayrollResponseWithPagination': {'errorMessage', 'errorCode'}, 'PrismHRBatchByDateResponse': {'errorMessage', 'errorCode'}, 'UKGReadyEinsResponse': {'items'}, 'UKGReadyDeductionResponse': {'deductions'}, 'UKGReadyDeductionCodesResponse': {'items'}, 'UKGReadyBenefitsResponse': {'benefits'}, 'UKGReadyDirectDepositResponse': {'deposits', 'links'}, 'UKGReadyEmployeeListResponse': {'employees'}, 'UKGReadyCompensationHistoryResponse': {'compensations'}, 'UKGReadyPaycheckListResponse': {'pay_statements'}, 'UKGReadyPayrollRunResponse': {'payrolls'}}
WRAPPER_REQUIRED["UKGReadyCombinedEmployeeListResponse"] = {"employees"}


def sample(annotation):
    origin = typing.get_origin(annotation)
    args = typing.get_args(annotation)
    if origin in (typing.Union, types.UnionType):
        if type(None) in args:
            return None
        return sample(args[0])
    if origin is list:
        return []
    if origin is dict:
        return {}
    if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
        return minimal(annotation)
    return {str: "synthetic", int: 1, float: 1.0, bool: False}.get(annotation, None)


def minimal(model):
    return {
        field.alias or name: sample(field.annotation)
        for name, field in model.model_fields.items() if field.is_required()
    }


class SourceRequirednessChecks(unittest.TestCase):
    def test_all_source_models_follow_project_requiredness_and_validate_presence(self):
        import normalization.source_models as package
        folder = Path(package.__file__).parent if package.__file__ else Path(next(iter(package.__path__)))
        for path in sorted(folder.glob("*/*.py")):
            module = importlib.import_module(
                "normalization.source_models." + path.parent.name + "." + path.stem)
            for name, model in vars(module).items():
                if not inspect.isclass(model) or not issubclass(model, BaseModel):
                    continue
                if model.__module__ != module.__name__ or model.__pydantic_root_model__:
                    continue
                model.model_rebuild()
                expected = set(WRAPPER_REQUIRED.get(name, ()))
                if "id" in model.model_fields:
                    expected.add("id")
                expected.update(NAMED_RECORD_IDS.get(name, ()))
                actual = {key for key, field in model.model_fields.items() if field.is_required()}
                with self.subTest(model=name):
                    self.assertEqual(actual, expected)
                    payload = minimal(model)
                    model.model_validate(payload)
                    for key in expected:
                        missing = dict(payload)
                        missing.pop(model.model_fields[key].alias or key)
                        with self.subTest(model=name, missing=key), self.assertRaises(ValidationError):
                            model.model_validate(missing)
                    # All optional fields can be supplied as null, not only omitted.
                    nullable = dict(payload)
                    nullable.update({
                        field.alias or key: None for key, field in model.model_fields.items()
                        if key not in expected
                    })
                    model.model_validate(nullable)


if __name__ == "__main__":
    unittest.main()
