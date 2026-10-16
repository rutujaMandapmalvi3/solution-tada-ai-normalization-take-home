# PrismHR route table. Input: none (static data). Output: ROUTES, endpoint -> how its records are mapped, identified and linked.
# PrismHR adapter: which contract endpoint feeds which canonical record, and how
# ids/refs are built (docs/solution-docs/relationship_policies.md, Tables 1-2).
"""PrismHR routes.

Route keys are described in route.py. Placeholders: {params.x} request params,
{record.x} the mapped record, {parent.x} the enclosing record.
Owner scope = clientId (PrismHR employee ids are unique only within a client).
provider:record_type:owner_scope[:employee_key]:record_key
provider : record_type : owner_scope : [employee_key] : record_key - taken from response
prismhr  : employee    : 001         : (none)         : 007
"""

from .route import Route

COMPANY = ("company", "{params.clientId}")

ROUTES: dict[str, list[Route]] = {
    "/clientMaster/v1/getClientMaster": [{
        "type": "company", "records": "clientMaster", "yaml": "company",
        "context": {"source_record_type": "client"},
        "check": [("{record.id}", "{params.clientId}")],
        "id": "{params.clientId}",
    }],
    "/employee/v1/getEmployee": [
        {
            "type": "employee", "records": "employee[]", "yaml": "employee",
            # Deposit accounts are their own records (next route).
            "ignore": ["directDeposit.achVoucher"],
            "context": {"client_id": "{params.clientId}"},
            "check": [("{record.id}", "{params.employeeId}")],
            "id": "{params.clientId}:{record.id}",
            "refs": {"company_ref": COMPANY},
        },
        {
            "type": "direct_deposit", "records": "employee[].directDeposit.achVoucher[]",
            "yaml": "direct_deposit",
            "context": {"employee_id": "{parent.id}", "deposit_id": None},
            "check": [("{parent.id}", "{params.employeeId}")],
            # No deposit id in PrismHR: the bank account identifies the allocation.
            "id": "{params.clientId}:{parent.id}:{record.transitNum}:{record.accountNum}",
            "refs": {"company_ref": COMPANY,
                     "employee_ref": ("employee", "{params.clientId}:{parent.id}")},
        },
    ],
    "/deductions/v1/getDeductions": [{
        "type": "deduction", "records": "employeeDeductions.deduction[]", "yaml": "deduction",
        "context": {"employee_id": "{params.employeeId}", "deduction_id": None},
        # No deduction id in PrismHR: the code identifies the assignment per employee.
        "id": "{params.clientId}:{params.employeeId}:{record.deductionCode}",
        "refs": {"company_ref": COMPANY,
                 "employee_ref": ("employee", "{params.clientId}:{params.employeeId}")},
    }],
    "/payroll/v1/getBatchListByDate": [{
        "type": "payroll_run", "records": "batchList[]", "yaml": "payroll_run",
        "id": "{params.clientId}:{record.batchId}",
        "refs": {"company_ref": COMPANY},
    }],
    "/payroll/v1/getPayrollVoucherForBatch": [{
        "type": "paycheck", "records": "payrollVouchers[]", "yaml": "paycheck",
        "id": "{params.clientId}:{record.voucherId}",
        "refs": {"company_ref": COMPANY,
                 "employee_ref": ("employee", "{params.clientId}:{record.employeeId}"),
                 "payroll_run_ref": ("payroll_run", "{params.clientId}:{record.batchId}")},
    }],
}
