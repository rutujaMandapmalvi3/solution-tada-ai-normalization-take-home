"""PrismHR payroll-run source validation and mapping integration."""
import copy
import unittest

from normalization.adapters import prismhr


def response():
    return {
        "errorCode": "0", "errorMessage": "",
        "batchList": [{
            "batchId": "001", "payDate": "2026-10-14", "batchType": "R",
            "batchStatus": "source-status",
            "payGroup": [{"payGroupId": "01", "payPeriodStartDate": "2026-10-01",
                          "payPeriodEndDate": "2026-10-14",
                          "weeksWorked": "0", "deductPeriod": "12345"}],
        }],
    }


class PayrollValidationChecks(unittest.TestCase):
    def assert_valid(self, payload):
        before = copy.deepcopy(payload)
        result = prismhr.normalize("payroll", payload, {})
        self.assertEqual(result["provider"], 'prismhr')
        self.assertEqual(payload, before)

    def test_validates_batches_without_mutating_source_values(self):
        self.assert_valid(response())

    def test_missing_null_and_empty_batches_return_empty_list(self):
        for extra in [{}, {"batchList": None}, {"batchList": []}]:
            payload = {"errorCode": "0", "errorMessage": "", **extra}
            before = copy.deepcopy(payload)
            with self.subTest(extra=extra):
                self.assertFalse(any(prismhr.normalize("payroll", payload, {})[key]
                                     for key in ("payroll_runs", "paycheck_headers", "paychecks")))
                self.assertEqual(payload, before)

    def test_requires_wrapper_fields_and_valid_types(self):
        for field in ["errorCode", "errorMessage"]:
            payload = response()
            del payload[field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                prismhr.normalize_payroll(payload, {})
        for payload in [None, [], {**response(), "errorCode": None},
                        {**response(), "errorMessage": []},
                        {**response(), "batchList": {}}]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                prismhr.normalize_payroll(payload, {})

    def test_provider_error_does_not_become_empty_success(self):
        for code in ["1", "NOT_FOUND"]:
            with self.subTest(code=code), self.assertRaisesRegex(ValueError, "request failed"):
                prismhr.normalize_payroll({"errorCode": code, "errorMessage": "test"}, {})

    def test_validates_every_batch_and_nested_pay_group(self):
        for invalid in [{"batchId": []}, {"payGroup": "wrong"},
                        {"payGroup": [{"payGroupId": "valid"}, {"weeksWorked": []}]}]:
            payload = response()
            payload["batchList"].append(invalid)
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                prismhr.normalize_payroll(payload, {})

    def test_optional_fields_and_pay_groups_accept_missing_null_or_empty(self):
        for batch in [{"batchId": "001"}, {"batchId": "001", "payGroup": None},
                      {"batchId": "001", "payGroup": []},
                      {"batchId": None, "payDate": None,
                       "payGroup": [{"payGroupId": None, "weeksWorked": None}]}]:
            with self.subTest(batch=batch):
                self.assert_valid({**response(), "batchList": [batch]})

    def test_extension_is_validated_without_treating_presence_as_failure(self):
        for extension in [None, {"any": {"note": "synthetic"}}]:
            with self.subTest(extension=extension):
                self.assert_valid({**response(), "extension": extension})
        with self.assertRaises(ValueError):
            prismhr.normalize_payroll({**response(), "extension": "wrong"}, {})


    def test_combined_sections_validate_both_even_when_one_is_empty(self):
        # An empty voucher list must not hide an invalid batch.
        payload = {**response(), "payrollVouchers": []}
        self.assert_valid(payload)
        payload["batchList"][0]["payGroup"] = "wrong"
        with self.assertRaises(ValueError):
            prismhr.normalize("payroll", payload, {})
        # An empty batch list must not hide an invalid voucher.
        with self.assertRaises(ValueError):
            prismhr.normalize("payroll", {
                "errorCode": "0", "errorMessage": "",
                "batchList": [], "payrollVouchers": [{}],
            }, {})

    def test_combined_sections_accept_valid_batches_and_vouchers(self):
        payload = {**response(), "payrollVouchers": [voucher()]}
        before = copy.deepcopy(payload)
        result = prismhr.normalize("payroll", payload, {})
        self.assertEqual(len(result["payroll_runs"]), 1)
        self.assertEqual(len(result["paychecks"]), 1)
        self.assertEqual(payload, before)

    def test_wrapper_only_payroll_still_checks_required_fields(self):
        with self.assertRaises(ValueError):
            prismhr.normalize("payroll", {"errorCode": "0"}, {})


def voucher():
    return {
        "voucherId": "001", "checkNumber": "0001", "payDate": "2026-10-14",
        "employeeId": "E1", "payPeriod": "source-period",
        "payPeriodStart": "2026-10-01", "payPeriodEnd": "2026-10-14",
        "totalEarnings": 0.0, "netPay": 0.0, "voidVoucherId": "",
        "fitTaxableAmount": 0.0, "earnAmount": 0.0, "otherEarnAmount": 0.0,
        "wcHomeClass": "", "wcState": "", "batchId": "001",
        "asoClientGLAcctDistribution": None,
    }


def paycheck_response():
    return {"errorCode": "0", "errorMessage": "", "payrollVouchers": [voucher()]}


class PaycheckValidationChecks(unittest.TestCase):
    def assert_valid(self, payload):
        before = copy.deepcopy(payload)
        result = prismhr.normalize("payroll", payload, {})
        self.assertEqual(result["provider"], 'prismhr')
        self.assertEqual(payload, before)

    def test_accepts_contract_and_live_collection_names(self):
        self.assert_valid(paycheck_response())
        payload = paycheck_response()
        payload["payrollVoucher"] = payload.pop("payrollVouchers")
        self.assert_valid(payload)

    def test_missing_null_and_empty_collections_return_empty_list(self):
        for extra in [{}, {"payrollVouchers": None}, {"payrollVouchers": []},
                      {"payrollVoucher": None}, {"payrollVoucher": []}]:
            payload = {"errorCode": "0", "errorMessage": "", **extra}
            before = copy.deepcopy(payload)
            with self.subTest(extra=extra):
                self.assertFalse(any(prismhr.normalize("payroll", payload, {})[key]
                                     for key in ("payroll_runs", "paycheck_headers", "paychecks")))
                self.assertEqual(payload, before)

    def test_requires_wrapper_fields_and_valid_shapes(self):
        for field in ["errorCode", "errorMessage"]:
            payload = paycheck_response()
            del payload[field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                prismhr.normalize("payroll", payload, {})
        for payload in [None, [], {**paycheck_response(), "payrollVouchers": {}},
                        {**paycheck_response(), "errorMessage": None}]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                prismhr.normalize("payroll", payload, {})

    def test_provider_errors_do_not_become_empty_success(self):
        for code in ["1", "NOT_FOUND"]:
            with self.subTest(code=code), self.assertRaisesRegex(ValueError, "request failed"):
                prismhr.normalize_payroll({"errorCode": code, "errorMessage": "test"}, {})

    def test_requires_voucher_id_but_accepts_optional_fields_absent(self):
        for field in ["employeeId", "netPay", "asoClientGLAcctDistribution"]:
            payload = paycheck_response()
            del payload["payrollVouchers"][0][field]
            self.assert_valid(payload)
        self.assert_valid({**paycheck_response(), "payrollVouchers": [{"voucherId": "001"}]})
        payload = paycheck_response()
        payload["payrollVouchers"].append({})
        with self.assertRaises(ValueError):
            prismhr.normalize("payroll", payload, {})

    def test_validates_nested_payments_earnings_taxes_and_deductions(self):
        valid = {
            "directDeposit": [{"transitNum": "001234567", "accountNum": "masked",
                               "status": "source-status", "amount": 0.0}],
            "earning": [{"payCode": "R", "chargeDate": "2026-10-14",
                         "hoursUnits": 0.0, "hoursWorked": 0.0}],
            "employeeTax": [{"empTaxDeductCode": "T", "empTaxableAmount": 0.0,
                             "empTaxAmount": 0.0, "empOverLimitAmount": 0.0}],
            "deduction": [{"deductCode": "D", "deductDescription": "test",
                           "deductAmount": 0.0, "deductType": "source-type",
                           "deductUnionId": "", "planId": ""}],
        }
        payload = paycheck_response()
        payload["payrollVouchers"][0].update(valid)
        self.assert_valid(payload)
        for field, records in valid.items():
            payload = paycheck_response()
            invalid_field = {"directDeposit": "amount", "earning": "hoursWorked",
                             "employeeTax": "empTaxAmount", "deduction": "deductAmount"}[field]
            payload["payrollVouchers"][0][field] = records + [{invalid_field: []}]
            with self.subTest(field=field), self.assertRaises(ValueError):
                prismhr.normalize("payroll", payload, {})

    def test_optional_nested_sections_accept_missing_null_and_empty_lists(self):
        for value in [None, []]:
            payload = paycheck_response()
            payload["payrollVouchers"][0].update(
                directDeposit=value, employeeTax=value, earning=value, deduction=value)
            self.assert_valid(payload)

    def test_validates_pagination_and_extension_without_inferring_failure(self):
        self.assert_valid({**paycheck_response(), "total": 1, "startpage": 0, "count": 1,
                           "extension": {"any": {"note": "synthetic"}}})
        self.assert_valid({**paycheck_response(), "total": None, "startpage": None,
                           "count": None, "extension": None})
        for field, value in [("total", "wrong"), ("startpage", []),
                             ("count", {}), ("extension", "wrong")]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                prismhr.normalize_payroll({**paycheck_response(), field: value}, {})

