"""PrismHR client-master source validation; company mapping is connected."""
import copy
import unittest

from normalization.adapters import prismhr


def response():
    return {"errorCode": "0", "errorMessage": "", "clientMaster": {"id": "001"}}


class CompanyValidationChecks(unittest.TestCase):
    def assert_valid(self, payload):
        before = copy.deepcopy(payload)
        result = prismhr.normalize("company", payload, {})
        self.assertIsInstance(result["companies"], list)
        self.assertEqual(payload, before)

    def test_valid_client_master_preserves_input(self):
        self.assert_valid(response())

    def test_absent_optional_client_master_returns_empty_list(self):
        for extra in [{}, {"clientMaster": None}]:
            with self.subTest(extra=extra):
                self.assertEqual(prismhr.normalize(
                    "company", {"errorCode": "0", "errorMessage": "", **extra}, {})["companies"], [])

    def test_requires_wrapper_fields_and_valid_shapes(self):
        for field in ["errorCode", "errorMessage"]:
            payload = response()
            del payload[field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                prismhr.normalize_company(payload, {})
        for payload in [None, [], {**response(), "clientMaster": []},
                        {**response(), "errorMessage": None}]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                prismhr.normalize_company(payload, {})

    def test_provider_errors_do_not_become_empty_success(self):
        for code in ["1", "NOT_FOUND"]:
            with self.subTest(code=code), self.assertRaisesRegex(ValueError, "request failed"):
                prismhr.normalize_company({"errorCode": code, "errorMessage": "test"}, {})

    def test_present_client_requires_only_record_id(self):
        self.assert_valid({**response(), "clientMaster": {"id": "001", "clientName": None}})
        with self.assertRaises(ValueError):
            prismhr.normalize_company({**response(), "clientMaster": {}}, {})
        with self.assertRaises(ValueError):
            prismhr.normalize_company(
                {**response(), "clientMaster": {"id": "001", "contractorsAllowed1099": []}}, {})

    def test_validates_nested_objects_and_each_record(self):
        payload = response()
        payload["clientMaster"]["altEmployer"] = [{"altEmployerId": "001"}]
        payload["clientMaster"]["observedHoliday"] = [
            {"name": "test", "description": "test", "holidayDate": []}]
        self.assert_valid(payload)
        for field in ["altEmployer", "observedHoliday"]:
            invalid = copy.deepcopy(payload)
            invalid["clientMaster"][field].append(
                {} if field == "altEmployer" else {"name": []})
            with self.subTest(field=field), self.assertRaises(ValueError):
                prismhr.normalize_company(invalid, {})

    def test_optional_nested_data_and_extensions(self):
        for value in [None, []]:
            payload = response()
            payload["clientMaster"]["altEmployer"] = value
            payload["extension"] = {"any": {"note": "synthetic"}}
            self.assert_valid(payload)
        with self.assertRaises(ValueError):
            prismhr.normalize_company({**response(), "extension": "wrong"}, {})


if __name__ == "__main__":
    unittest.main()
