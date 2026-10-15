"""Contract layer: schema lookup, live renames, live-only fields and the validation policy."""
import unittest

from normalization import contracts

EMPLOYEE = "/employee/v1/getEmployee"
VOUCHERS = "/payroll/v1/getPayrollVoucherForBatch"


class SchemaLookup(unittest.TestCase):
    def test_every_provider_resolves_a_response_schema(self):
        for provider, endpoint, path in (
            ("prismhr", EMPLOYEE, "employee[]"),
            ("isolved", "/api/clients/{clientId}/legals/{legalId}/employees/{id}", ""),
            ("ukg-ready", "/v2/companies/{cid}/employees/{aid}", ""),
        ):
            with self.subTest(provider=provider):
                schema = contracts.response_schema(provider, endpoint).at(path)
                self.assertIn("id", schema.declared())

    def test_ukg_page_name_is_derived_from_the_endpoint(self):
        self.assertEqual(contracts.ukg_page("/v2/companies/{cid}/employees/{aid}"),
                         "__v2__companies__(cid)__employees__(aid).html")

    def test_unknown_endpoint_and_unknown_field_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "No prismhr GET 200"):
            contracts.response_schema("prismhr", "/not/a/path")
        with self.assertRaisesRegex(ValueError, "No UKG Ready GET schema"):
            contracts.response_schema("ukg-ready", "/v2/companies/{cid}/nothing")
        with self.assertRaises(KeyError):
            contracts.response_schema("prismhr", EMPLOYEE).at("employee[].notAField")

    def test_live_only_fields_count_as_declared_for_mapping(self):
        record = contracts.response_schema("prismhr", VOUCHERS).at("payrollVouchers[]")
        self.assertIn("isManualCheck", record.declared())
        self.assertIn("voucherId", record.declared())

    def test_wrapped_section_exposes_the_body_schema(self):
        body = contracts.response_schema("ukg-ready", "/v2/companies/{cid}/employees/{aid}/pay-info")
        self.assertIn("standard_work_day", body.wrap("pay_info").at("pay_info").declared())


class Prepare(unittest.TestCase):
    def test_live_singular_names_are_renamed_to_contract_names(self):
        body = contracts.prepare("prismhr", {"endpoint": EMPLOYEE, "body": {
            "errorCode": "0", "payrollVoucher": [],
            "employee": [{"person": {"employerId": ["1"]}, "client": {"hawaiiMedWaiver": []}}]}})
        self.assertIn("payrollVouchers", body)
        self.assertIn("employerIds", body["employee"][0]["person"])
        self.assertIn("hawaiiMedWaivers", body["employee"][0]["client"])

    def test_rename_is_scoped_by_parent(self):
        body = contracts.prepare("prismhr", {"endpoint": "x", "body": {"clientMaster": {"employerId": "E"}}})
        self.assertEqual(body["clientMaster"], {"employerId": "E"})

    def test_both_spellings_supplied_keeps_live_one(self):
        body = contracts.prepare("prismhr", {"endpoint": "x", "body": {"payrollVoucher": [1], "payrollVouchers": [2]}})
        self.assertEqual(body, {"payrollVoucher": [1], "payrollVouchers": [2]})

    def test_prismhr_error_code_and_http_status_stop_the_run(self):
        with self.assertRaisesRegex(ValueError, "errorCode=EMP-1"):
            contracts.prepare("prismhr", {"endpoint": EMPLOYEE, "body": {"errorCode": "EMP-1", "errorMessage": "x"}})
        with self.assertRaisesRegex(ValueError, "HTTP status 404"):
            contracts.prepare("isolved", {"endpoint": "x", "status": 404, "body": None})


class Validate(unittest.TestCase):
    def test_nulls_and_missing_required_fields_are_accepted(self):
        body = {"errorCode": "0", "employee": [{"id": "7", "firstName": None}]}
        self.assertEqual(contracts.validate("prismhr", EMPLOYEE, body), [])

    def test_wrong_type_stops_the_run_with_its_path(self):
        with self.assertRaisesRegex(ValueError, "employee/0/firstName"):
            contracts.validate("prismhr", EMPLOYEE, {"errorCode": "0", "employee": [{"id": "7", "firstName": 5}]})

    def test_integral_float_counts_as_integer(self):
        self.assertEqual(contracts.validate("ukg-ready", "/v2/companies/{cid}/employees/{aid}", {"id": 7.0}), [])
        with self.assertRaisesRegex(ValueError, "id"):
            contracts.validate("ukg-ready", "/v2/companies/{cid}/employees/{aid}", {"id": 7.5})

    def test_undocumented_field_is_contract_drift(self):
        warnings = contracts.validate("ukg-ready", "/v2/companies/{cid}/employees/{aid}",
                                      {"id": 7, "ein_name": "Primary"})
        self.assertEqual([w["code"] for w in warnings], ["contract_drift"])
        self.assertIn("ein_name", warnings[0]["message"])


if __name__ == "__main__":
    unittest.main()
