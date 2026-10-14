"""PrismHR direct-deposit source validation; canonical mapping is pending."""
import copy
import unittest

from normalization.adapters import prismhr


def response(deposit=None):
    return {
        "errorCode": "0", "errorMessage": "",
        "employee": [{"id": "synthetic", "firstName": "Test", "lastName": "Employee",
                      "middleInitial": "", "preferredName": "", "directDeposit": deposit}],
    }


def setup():
    return {
        "achStatus": "A", "voucherType": "R", "directDepositChecksum": "test",
        "achVoucher": [{"transitNum": "001234567", "accountNum": "masked",
                        "accountType": "C", "method": "F", "amount": 0.0,
                        "limit": 0.0, "status": "D", "bankName": "Synthetic",
                        "voucherTypeOverride": "R"}],
    }


class DirectDepositChecks(unittest.TestCase):
    def assert_valid_source(self, payload):
        original = copy.deepcopy(payload)
        with self.assertRaisesRegex(NotImplementedError, "source validation passed"):
            prismhr.normalize("direct_deposit", payload, {})
        self.assertEqual(payload, original)

    def test_accepts_populated_accounts_without_mutating_input(self):
        self.assert_valid_source(response(setup()))

    def test_accepts_empty_employee_list_null_setup_and_empty_accounts(self):
        for employee_value in [None, []]:
            self.assert_valid_source({"errorCode": "0", "errorMessage": "",
                                      "employee": employee_value})
        self.assert_valid_source({"errorCode": "0", "errorMessage": ""})
        empty = setup()
        empty["achVoucher"] = []
        for payload in [{"errorCode": "0", "errorMessage": "", "employee": []},
                        response(), response(empty)]:
            with self.subTest(payload=payload):
                self.assert_valid_source(payload)

    def test_requires_documented_wrapper_fields_and_valid_collection_types(self):
        for key in ["errorCode", "errorMessage"]:
            payload = response()
            del payload[key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                prismhr.normalize_direct_deposits(payload, {})
        for payload in [None, [],
                        {**response(), "employee": "invalid"}]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                prismhr.normalize_direct_deposits(payload, {})

    def test_rejects_provider_errors(self):
        for code in ["1", "NOT_FOUND"]:
            with self.subTest(code=code), self.assertRaisesRegex(ValueError, "request failed"):
                prismhr.normalize_direct_deposits({"errorCode": code, "errorMessage": "test"}, {})

    def test_validates_every_employee_and_account(self):
        payload = response(setup())
        payload["employee"].append({})
        with self.assertRaises(ValueError):
            prismhr.normalize_direct_deposits(payload, {})
        payload = response(setup())
        payload["employee"][0]["directDeposit"]["achVoucher"].append({"amount": []})
        with self.assertRaises(ValueError):
            prismhr.normalize_direct_deposits(payload, {})

    def test_accepts_missing_optional_deposit_and_nullable_wrapper_fields(self):
        payload = response()
        del payload["employee"][0]["directDeposit"]
        self.assert_valid_source({**payload, "infoMessage": None,
                                  "updateMessage": None, "extension": None})

    def test_rejects_invalid_wrapper_field_types(self):
        for field, value in [("infoMessage", "wrong"), ("updateMessage", []),
                             ("errorMessage", None), ("extension", "wrong")]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                prismhr.normalize_direct_deposits({**response(), field: value}, {})

    def test_missing_deposit_does_not_hide_another_employee_with_setup(self):
        payload = response()
        payload["employee"].append(response(setup())["employee"][0])
        with self.assertRaisesRegex(NotImplementedError, "1 employee record"):
            prismhr.normalize_direct_deposits(payload, {})

    def test_does_not_treat_informational_wrapper_fields_as_failure(self):
        self.assert_valid_source({**response(), "infoMessage": ["test"],
                                  "extension": {"any": {"note": "test"}},
                                  "updateMessage": "test"})




if __name__ == "__main__":
    unittest.main()
