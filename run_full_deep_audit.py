import sys
import os
import json
import jwt
from bson import ObjectId

sys.path.insert(0, r"C:\Users\Admin\.gemini\antigravity\scratch\hr-ops-agent\backend")

from app.main import app, db, SECRET_KEY

def run_deep_audit():
    client = app.test_client()
    app.config['TESTING'] = True

    # 1. Get real admin employee from DB
    admin_emp = db.employees.find_one({"role": "SUPER_ADMIN"}) or db.employees.find_one()
    if not admin_emp:
        print("No employee found in DB!")
        return

    admin_emp_id_str = str(admin_emp["_id"])
    admin_email = admin_emp.get("email", "rutuja.a@semcogroups.com")
    tenant_id = admin_emp.get("tenant_id", "semco")

    print(f"Using Admin Employee: {admin_emp.get('name')} (ID: {admin_emp_id_str}, Email: {admin_email})")

    # Generate JWT Token for SUPER_ADMIN
    token = jwt.encode({
        "sub": admin_email,
        "email": admin_email,
        "role": "SUPER_ADMIN",
        "tenant_id": tenant_id,
        "employee_id": admin_emp_id_str
    }, SECRET_KEY, algorithm="HS256")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Generate JWT Token for regular EMPLOYEE
    emp = db.employees.find_one({"role": "Employee"}) or admin_emp
    emp_id_str = str(emp["_id"])
    emp_email = emp.get("email", "employee@semcogroups.com")
    emp_token = jwt.encode({
        "sub": emp_email,
        "email": emp_email,
        "role": "Employee",
        "tenant_id": tenant_id,
        "employee_id": emp_id_str
    }, SECRET_KEY, algorithm="HS256")

    emp_headers = {
        "Authorization": f"Bearer {emp_token}",
        "Content-Type": "application/json"
    }

    audit_results = {
        "admin_tests": {"passed": 0, "failed": 0, "details": []},
        "employee_tests": {"passed": 0, "failed": 0, "details": []},
        "bugs_found": []
    }

    def test_ep(category, name, method, url, req_headers, payload=None, expected=[200, 201, 204]):
        if payload and isinstance(payload, dict):
            res = client.open(url, method=method, headers=req_headers, data=json.dumps(payload))
        else:
            res = client.open(url, method=method, headers=req_headers)

        status = res.status_code
        try:
            body = res.get_json()
        except Exception:
            body = res.get_data(as_text=True)[:200]

        is_ok = status in expected if isinstance(expected, list) else status == expected
        res_entry = {
            "category": category,
            "name": name,
            "method": method,
            "url": url,
            "status": status,
            "passed": is_ok,
            "response": body
        }
        
        target = audit_results["admin_tests"] if req_headers == headers else audit_results["employee_tests"]
        target["details"].append(res_entry)

        if is_ok:
            target["passed"] += 1
            print(f"  [PASS] {method:6s} {url:45s} -> HTTP {status}")
        else:
            target["failed"] += 1
            bug_desc = f"[{category}] {method} {url} returned HTTP {status} (Expected {expected}): {str(body)[:250]}"
            audit_results["bugs_found"].append(bug_desc)
            print(f"  [FAIL] {method:6s} {url:45s} -> HTTP {status}: {str(body)[:150]}")
        return res_entry

    print("\n========================================================")
    print("      EXECUTING DEEP HRMS PORTAL FUNCTIONAL AUDIT       ")
    print("========================================================\n")

    # Module 1: Auth & User Identity
    print("--- Module 1: Auth & User Profile ---")
    test_ep("Auth", "Get Signup Status", "GET", "/api/auth/signup-status", headers)
    test_ep("Auth", "Get Tenants", "GET", "/api/auth/tenants", headers)
    test_ep("Auth", "Get My Profile (Admin)", "GET", "/api/auth/me", headers)
    test_ep("Auth", "Get My Profile (Employee)", "GET", "/api/auth/me", emp_headers)

    # Module 2: Employee Directory & Profiles
    print("\n--- Module 2: Employee Directory & Management ---")
    test_ep("Employees", "List Employees", "GET", "/api/employees", headers)
    
    new_employee_payload = {
        "name": "Audit Test Subject",
        "email": f"audit.subject.{os.urandom(3).hex()}@semcogroups.com",
        "role": "QA Engineer",
        "department": "Engineering",
        "birthday": "1995-04-12",
        "joining_date": "2024-01-15",
        "ctc": 1200000
    }
    create_emp_res = test_ep("Employees", "Create Employee", "POST", "/api/employees", headers, new_employee_payload, expected=[200, 201])
    created_id = None
    if create_emp_res["passed"] and isinstance(create_emp_res["response"], dict):
        created_id = create_emp_res["response"].get("id") or create_emp_res["response"].get("employee", {}).get("id")

    # Module 3: Attendance & Leaves
    print("\n--- Module 3: Attendance & Leave Management ---")
    test_ep("Attendance", "Today's Attendance Status", "GET", "/api/attendance/today", headers)
    test_ep("Attendance", "My Monthly Attendance", "GET", "/api/attendance/my-month", headers)
    test_ep("Attendance", "Leave Summary", "GET", "/api/attendance/leave-summary", headers)
    test_ep("Attendance", "Leave Allocations", "GET", "/api/attendance/leave-allocation", headers)
    test_ep("Attendance", "Month Lock Status", "GET", "/api/attendance/lock-status?month=2026-08", headers)
    
    # Test Attendance Marking with various statuses
    test_ep("Attendance", "Mark Attendance (PRESENT)", "POST", "/api/attendance/mark", headers, {"status": "PRESENT", "notes": "On site"}, expected=[200, 201])
    test_ep("Attendance", "Mark Attendance (REMOTE)", "POST", "/api/attendance/mark", headers, {"status": "REMOTE", "notes": "WFH"}, expected=[200, 201])
    test_ep("Attendance", "Mark Attendance (LEAVE)", "POST", "/api/attendance/mark", headers, {"status": "LEAVE", "notes": "Casual leave"}, expected=[200, 201])
    test_ep("Attendance", "Mark Attendance (Invalid Status)", "POST", "/api/attendance/mark", headers, {"status": "INVALID_STATUS"}, expected=400)

    # Module 4: Payroll, CTC & Payslips
    print("\n--- Module 4: Payroll & Compensation ---")
    test_ep("Payroll", "List Payrolls", "GET", "/api/payroll", headers)
    test_ep("Payroll", "My Payslips", "GET", "/api/payroll/my-payslips", headers)
    
    payroll_payload = {
        "employee_id": admin_emp_id_str,
        "gross_salary": 150000,
        "pay_period": "2026-08"
    }
    test_ep("Payroll", "Generate Payroll", "POST", "/api/payroll/generate", headers, payroll_payload, expected=[200, 201])
    test_ep("Payroll", "Export CTC Statement", "POST", "/api/payroll/ctc/export", headers, {"employee_id": admin_emp_id_str}, expected=[200, 201])

    # Module 5: Document Vault & E-Library
    print("\n--- Module 5: Document Vault & E-Library ---")
    test_ep("DocVault", "Get Document Vault", "GET", f"/api/documents/vault/{admin_emp_id_str}", headers)
    test_ep("ELibrary", "List E-Library Files", "GET", "/api/elibrary", headers)
    test_ep("ELibrary", "List E-Library Links", "GET", "/api/elibrary/links", headers)

    # Module 6: Asset Management
    print("\n--- Module 6: Asset Management ---")
    test_ep("Assets", "List Assets", "GET", "/api/assets", headers)
    
    asset_payload = {
        "hardware_name": "MacBook Pro M3 Max 16-inch",
        "serial_number": f"MBP-{os.urandom(4).hex().upper()}",
        "status": "AVAILABLE"
    }
    asset_res = test_ep("Assets", "Create Asset", "POST", "/api/assets", headers, asset_payload, expected=[200, 201])

    # Module 7: Policy Search & Knowledge Base
    print("\n--- Module 7: Policy Search & Knowledge Base ---")
    test_ep("Policies", "List Policies", "GET", "/api/policies", headers)
    test_ep("Policies", "Search Policies (Query='leave')", "GET", "/api/policies/search?q=leave", headers)
    test_ep("Policies", "Search Policies (Query='wfh')", "GET", "/api/policies/search?q=wfh", headers)

    # Module 8: Celebrations & Company Events
    print("\n--- Module 8: Celebrations & Events ---")
    test_ep("Celebrations", "List All Celebrations", "GET", "/api/celebrations/all", headers)
    test_ep("Celebrations", "Match Today's Celebrations", "GET", "/api/celebrations/match", headers)
    test_ep("Events", "List Events", "GET", "/api/events", headers)

    # Module 9: Daily Pulse & Engagement Surveys
    print("\n--- Module 9: Daily Pulse & Surveys ---")
    test_ep("DailyPulse", "Get Today's Daily Pulse", "GET", "/api/daily-pulse/today", headers)
    test_ep("DailyPulse", "Get Pulse Schedule", "GET", "/api/daily-pulse/schedule", headers)
    test_ep("Surveys", "Get Survey Metrics", "GET", "/api/surveys/metrics", headers)

    survey_payload = {
        "survey_month": "2026-08",
        "q1_burnout": 4,
        "q2_alignment": 5,
        "q3_satisfaction": 5
    }
    test_ep("Surveys", "Submit Survey Response", "POST", "/api/surveys/submit", headers, survey_payload, expected=[200, 201])

    # Module 10: LMS & Discussion Forums
    print("\n--- Module 10: LMS Clubs & Discussions ---")
    test_ep("LMS", "List Clubs", "GET", "/api/lms-club/clubs", headers)
    test_ep("LMS", "List Discussions", "GET", "/api/discussions", headers)

    # Module 11: Surprise Ops (Appreciations & Vouchers)
    print("\n--- Module 11: Surprise Ops ---")
    test_ep("SurpriseOps", "List Coupons", "GET", "/api/surprise-ops/coupons", headers)
    test_ep("SurpriseOps", "List Appreciations", "GET", "/api/surprise-ops/appreciation", headers)

    # Module 12: Offboarding Workflow
    print("\n--- Module 12: Offboarding Status ---")
    test_ep("Offboarding", "Get Offboarding Status (Admin)", "GET", "/api/offboarding/status", headers)
    test_ep("Offboarding", "Get Offboarding Status (Employee)", "GET", "/api/offboarding/status", emp_headers)

    print("\n========================================================")
    print("                    AUDIT SUMMARY                       ")
    print("========================================================")
    admin_passed = audit_results["admin_tests"]["passed"]
    admin_failed = audit_results["admin_tests"]["failed"]
    emp_passed = audit_results["employee_tests"]["passed"]
    emp_failed = audit_results["employee_tests"]["failed"]

    print(f"ADMIN ROLE TESTS     : {admin_passed} PASSED, {admin_failed} FAILED")
    print(f"EMPLOYEE ROLE TESTS  : {emp_passed} PASSED, {emp_failed} FAILED")
    print(f"TOTAL BUGS DETECTED  : {len(audit_results['bugs_found'])}")

    if audit_results["bugs_found"]:
        print("\nDETAILED BUG LIST:")
        for idx, bug in enumerate(audit_results["bugs_found"], 1):
            print(f" {idx}. {bug}")

    with open(r"C:\Users\Admin\.gemini\antigravity\scratch\hrms_deep_audit_report.json", "w") as f:
        json.dump(audit_results, f, indent=2)

    print("\nSaved full audit JSON to hrms_deep_audit_report.json")

if __name__ == '__main__':
    run_deep_audit()
