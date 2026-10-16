# isolved route table. Input: none (static data). Output: ROUTES, endpoint -> how its records are mapped, identified and linked.
# isolved adapter: which contract endpoint feeds which canonical record, and how
# ids/refs are built (docs/solution-docs/relationship_policies.md, Tables 1-2).
"""isolved routes (primary Swagger snapshot paths).

Owner scope = clientId:legalId (a client holds several legal companies).
See route.py for the route keys.
"""

from .route import Route

LEGALS = "/api/clients/{clientId}/legals"
EMPLOYEE = LEGALS + "/{legalId}/employees/{employeeId}"
COMPANY = ("company", "{params.clientId}:{params.legalId}")
EMPLOYEE_REF = ("employee", "{params.clientId}:{params.legalId}:{params.employeeId}")

_EMPLOYEE = {
    "type": "employee", "yaml": "employee",
    "id": "{params.clientId}:{params.legalId}:{record.id}",
    "refs": {"company_ref": COMPANY},
}
_RUN = {
    "type": "payroll_run", "records": "[]", "yaml": "payroll_run",
    "id": "{params.clientId}:{params.legalId}:{params.paygroupId}:{record.id}",
    "refs": {"company_ref": COMPANY},
}

ROUTES: dict[str, list[Route]] = {
    LEGALS: [{
        "type": "company", "records": "[]", "yaml": "company",
        "context": {"source_record_type": "legal_company"},
        "id": "{params.clientId}:{record.id}",
    }],
    LEGALS + "/{legalId}/employees/{id}": [{**_EMPLOYEE, "records": "",
                                          "check": [("{record.id}", "{params.id}")]}],
    LEGALS + "/{legalId}/employees": [{**_EMPLOYEE, "records": "results[]"}],
    # Salary history has no employee id; it merges into the employee by id.
    EMPLOYEE + "/salaries": [{
        "type": "employee", "records": "", "wrap": "salary_history", "yaml": "employee_salaries",
        "context": {"employee_id": "{params.employeeId}"},
        "id": "{params.clientId}:{params.legalId}:{params.employeeId}",
        "refs": {"company_ref": COMPANY},
    }],
    EMPLOYEE + "/directdeposits": [{
        "type": "direct_deposit", "records": "[]", "yaml": "direct_deposit",
        "context": {"employee_id": "{params.employeeId}"},
        "id": "{params.clientId}:{params.legalId}:{params.employeeId}:{record.id}",
        "refs": {"company_ref": COMPANY, "employee_ref": EMPLOYEE_REF},
    }],
    EMPLOYEE + "/payItems": [{
        "type": "deduction", "records": "[]", "yaml": "deduction",
        # The endpoint also returns Earning and Memo Calc items: kept as filtered records.
        "where": {"payItemType": "Deduction"},
        "context": {"employee_id": "{params.employeeId}"},
        "check": [("{record.employeeId}", "{params.employeeId}")],
        "defaults": {"employee_id": "{params.employeeId}"},
        "id": "{params.clientId}:{params.legalId}:{params.employeeId}:{record.id}",
        "refs": {"company_ref": COMPANY, "employee_ref": EMPLOYEE_REF},
    }],
    LEGALS + "/{legalId}/paygroupId/{paygroupId}/payrollRunHistory": [_RUN],
    LEGALS + "/{legalId}/paygroupId/{paygroupId}/payrollRunHistory/byDate": [_RUN],
    # A check carries no payroll run id, so no payroll_run_ref (known gap).
    LEGALS + "/{legalId}/payGroups/{payGroupId}/checks": [{
        "type": "paycheck", "records": "results[]", "yaml": "paycheck",
        "id": "{params.clientId}:{params.legalId}:{record.id}",
        "refs": {"company_ref": COMPANY,
                 "employee_ref": ("employee", "{params.clientId}:{params.legalId}:{record.employeeId}")},
    }],
}
