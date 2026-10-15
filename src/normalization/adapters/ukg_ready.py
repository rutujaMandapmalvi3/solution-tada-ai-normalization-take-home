# UKG Ready adapter: which documented endpoint feeds which canonical record, and
# how ids/refs are built (docs/solution-docs/relationship_policies.md, Tables 1-2).
"""UKG Ready routes (paths of the cached reference pages).

Owner scope = cid. The company is the cid itself; EIN lookup items are separate
company records linked to it. Both pay-statement path placeholders are named
{id}, so bundles pass them as params payroll_id and pay_statement_id.
See prismhr.py for the route keys.
"""

COMPANIES = "/v2/companies/{cid}"
COMPANY = ("company", "{params.cid}")
EMPLOYEE_REF = ("employee", "{params.cid}:{params.aid}")

_EMPLOYEE = {
    "type": "employee", "yaml": "employee",
    "id": "{params.cid}:{record.id}",
    "refs": {"company_ref": COMPANY},
}
_STATEMENT_REFS = {
    "company_ref": COMPANY,
    "employee_ref": ("employee", "{params.cid}:{record.employee.account_id}"),
    "payroll_run_ref": ("payroll_run", "{params.cid}:{params.payroll_id}"),
}

ROUTES = {
    COMPANIES + "/lookup/eins": [
        {
            "type": "company", "records": "", "yaml": "company_root", "ignore": ["items"],
            "context": {"source_record_type": "company", "source_record_id": "{params.cid}"},
            "id": "{params.cid}",
        },
        {
            "type": "company", "records": "items[]", "yaml": "company",
            "context": {"source_record_type": "ein"},
            "id": "{params.cid}:ein:{record.id}",
            "refs": {"company_ref": COMPANY},
        },
    ],
    COMPANIES + "/employees/{aid}": [{**_EMPLOYEE, "records": "",
                                     "check": [("{record.id}", "{params.aid}")]}],
    COMPANIES + "/employees": [{**_EMPLOYEE, "records": "employees[]",
                                "schema": (COMPANIES + "/employees/{aid}", "")}],
    # pay-info and compensation history carry no employee id; they merge into
    # the employee by id.
    COMPANIES + "/employees/{aid}/pay-info": [{
        "type": "employee", "records": "", "wrap": "pay_info", "yaml": "employee_pay_info",
        "context": {"employee_id": "{params.aid}"},
        "id": "{params.cid}:{params.aid}",
        "refs": {"company_ref": COMPANY},
    }],
    COMPANIES + "/employees/{aid}/compensation/history": [{
        "type": "employee", "records": "", "wrap": "compensation_history",
        "yaml": "employee_compensation",
        "context": {"employee_id": "{params.aid}"},
        "id": "{params.cid}:{params.aid}",
        "refs": {"company_ref": COMPANY},
    }],
    COMPANIES + "/employees/{aid}/direct-deposits": [{
        "type": "direct_deposit", "records": "deposits[]", "yaml": "direct_deposit",
        "context": {"employee_id": "{params.aid}"},
        "id": "{params.cid}:{params.aid}:{record.id}",
        "refs": {"company_ref": COMPANY, "employee_ref": EMPLOYEE_REF},
    }],
    COMPANIES + "/employees/{aid}/deductions": [{
        "type": "deduction", "records": "deductions[]", "yaml": "deduction",
        "context": {"employee_id": "{params.aid}"},
        "id": "{params.cid}:{params.aid}:{record.id}",
        "refs": {"company_ref": COMPANY, "employee_ref": EMPLOYEE_REF},
    }],
    COMPANIES + "/payrolls": [{
        "type": "payroll_run", "records": "payrolls[]", "yaml": "payroll_run",
        "id": "{params.cid}:{record.id}",
        "refs": {"company_ref": COMPANY},
    }],
    # Statement list (header) and statement detail share the id and merge.
    COMPANIES + "/payrolls/{id}/pay-statements": [{
        "type": "paycheck", "records": "pay_statements[]", "yaml": "paycheck_header",
        "id": "{params.cid}:{record.id}", "refs": _STATEMENT_REFS,
    }],
    COMPANIES + "/payrolls/{id}/pay-statements/{id}": [{
        "type": "paycheck", "records": "", "yaml": "paycheck",
        "fill_record": {"id": "{params.pay_statement_id}"},
        "id": "{params.cid}:{record.id}",
        "refs": _STATEMENT_REFS,
    }],
}
