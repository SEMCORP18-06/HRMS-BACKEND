import sys
import os
import json
import jwt

sys.path.insert(0, r"C:\Users\Admin\.gemini\antigravity\scratch\hr-ops-agent\backend")

from app.main import app

def run_tests():
    client = app.test_client()
    app.config['TESTING'] = True
    
    # Generate a valid test JWT Token
    SECRET_KEY = "hr-ops-secret-key-12345"
    auth_payload = {
        "email": "rutuja.a@semcogroups.com",
        "role": "SUPER_ADMIN",
        "tenant_id": "semco",
        "employee_id": 1
    }
    token = jwt.encode(auth_payload, SECRET_KEY, algorithm="HS256")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    results = {
        "passed": 0,
        "failed": 0,
        "errors": [],
        "endpoint_results": []
    }

    def log_res(endpoint, method, status_code, data, expected_status=200):
        if isinstance(expected_status, int):
            is_pass = (status_code in [expected_status, 200, 201, 204])
        else:
            is_pass = (status_code in expected_status)

        entry = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "pass": is_pass,
            "response": data if isinstance(data, (dict, list)) else str(data)[:200]
        }
        results["endpoint_results"].append(entry)
        if is_pass:
            results["passed"] += 1
            print(f"  [PASS] {method} {endpoint} -> {status_code}")
        else:
            results["failed"] += 1
            err_msg = f"{method} {endpoint} returned {status_code}: {str(data)[:300]}"
            results["errors"].append(err_msg)
            print(f"  [FAIL] {err_msg}")
        return is_pass, data

    print("--- STARTING RIGOROUS HRMS API TEST SUITE (AUTHENTICATED) ---")

    # 1. Auth & Me
    print("\n1. Testing Auth Endpoints...")
    res = client.get('/api/auth/signup-status')
    log_res('/api/auth/signup-status', 'GET', res.status_code, res.get_json())

    res = client.get('/api/auth/tenants')
    log_res('/api/auth/tenants', 'GET', res.status_code, res.get_json())

    res = client.get('/api/auth/me', headers=headers)
    log_res('/api/auth/me', 'GET', res.status_code, res.get_json())

    # 2. Employees Directory
    print("\n2. Testing Employee Directory Endpoints...")
    res = client.get('/api/employees', headers=headers)
    log_res('/api/employees', 'GET', res.status_code, res.get_json())

    new_emp = {
        "name": "Automated Tester",
        "email": "auto.test@semcogroups.com",
        "role": "QA Engineer",
        "department": "Quality Assurance",
        "birthday": "1996-08-20",
        "joining_date": "2024-03-01",
        "ctc": 950000
    }
    res = client.post('/api/employees', data=json.dumps(new_emp), headers=headers)
    log_res('/api/employees', 'POST', res.status_code, res.get_json(), expected_status=[200, 201])

    emp_id = 1
    if res.status_code in [200, 201]:
        emp_data = res.get_json()
        if isinstance(emp_data, dict):
            emp_id = emp_data.get('id') or (emp_data.get('employee', {}).get('id')) or 1

    # 3. Attendance & Leaves
    print("\n3. Testing Attendance & Leave Endpoints...")
    res = client.get('/api/attendance/today', headers=headers)
    log_res('/api/attendance/today', 'GET', res.status_code, res.get_json())

    res = client.get('/api/attendance/my-month', headers=headers)
    log_res('/api/attendance/my-month', 'GET', res.status_code, res.get_json())

    res = client.get('/api/attendance/leave-summary', headers=headers)
    log_res('/api/attendance/leave-summary', 'GET', res.status_code, res.get_json())

    res = client.get('/api/attendance/leave-allocation', headers=headers)
    log_res('/api/attendance/leave-allocation', 'GET', res.status_code, res.get_json())

    res = client.get('/api/attendance/lock-status?month=2026-08', headers=headers)
    log_res('/api/attendance/lock-status', 'GET', res.status_code, res.get_json())

    mark_payload = {
        "status": "PRESENT",
        "notes": "Automated Test Suite Attendance Mark"
    }
    res = client.post('/api/attendance/mark', data=json.dumps(mark_payload), headers=headers)
    log_res('/api/attendance/mark', 'POST', res.status_code, res.get_json())

    # 4. Payroll & CTC
    print("\n4. Testing Payroll Endpoints...")
    res = client.get('/api/payroll', headers=headers)
    log_res('/api/payroll', 'GET', res.status_code, res.get_json())

    res = client.get('/api/payroll/my-payslips', headers=headers)
    log_res('/api/payroll/my-payslips', 'GET', res.status_code, res.get_json())

    gen_payroll_payload = {
        "employee_id": emp_id,
        "gross_salary": 80000,
        "pay_period": "2026-08"
    }
    res = client.post('/api/payroll/generate', data=json.dumps(gen_payroll_payload), headers=headers)
    log_res('/api/payroll/generate', 'POST', res.status_code, res.get_json())

    export_ctc_payload = {
        "employee_id": emp_id
    }
    res = client.post('/api/payroll/ctc/export', data=json.dumps(export_ctc_payload), headers=headers)
    log_res('/api/payroll/ctc/export', 'POST', res.status_code, res.get_json())

    # 5. Document Vault & E-Library
    print("\n5. Testing Document Vault & E-Library...")
    res = client.get(f'/api/documents/vault/{emp_id}', headers=headers)
    log_res(f'/api/documents/vault/{emp_id}', 'GET', res.status_code, res.get_json())

    res = client.get('/api/elibrary', headers=headers)
    log_res('/api/elibrary', 'GET', res.status_code, res.get_json())

    res = client.get('/api/elibrary/links', headers=headers)
    log_res('/api/elibrary/links', 'GET', res.status_code, res.get_json())

    # 6. Asset Management
    print("\n6. Testing Asset Management...")
    res = client.get('/api/assets', headers=headers)
    log_res('/api/assets', 'GET', res.status_code, res.get_json())

    new_asset = {
        "hardware_name": "Test Laptop Pro 16",
        "serial_number": f"TEST-SN-{os.urandom(4).hex().upper()}",
        "status": "AVAILABLE"
    }
    res = client.post('/api/assets', data=json.dumps(new_asset), headers=headers)
    log_res('/api/assets', 'POST', res.status_code, res.get_json(), expected_status=[200, 201])

    # 7. Policy Search
    print("\n7. Testing Policy Search...")
    res = client.get('/api/policies', headers=headers)
    log_res('/api/policies', 'GET', res.status_code, res.get_json())

    res = client.get('/api/policies/search?q=leave', headers=headers)
    log_res('/api/policies/search', 'GET', res.status_code, res.get_json())

    # 8. Celebrations & Events
    print("\n8. Testing Celebrations & Events...")
    res = client.get('/api/celebrations/all', headers=headers)
    log_res('/api/celebrations/all', 'GET', res.status_code, res.get_json())

    res = client.get('/api/celebrations/match', headers=headers)
    log_res('/api/celebrations/match', 'GET', res.status_code, res.get_json())

    res = client.get('/api/events', headers=headers)
    log_res('/api/events', 'GET', res.status_code, res.get_json())

    # 9. Daily Pulse & Surveys
    print("\n9. Testing Daily Pulse & Surveys...")
    res = client.get('/api/daily-pulse/today', headers=headers)
    log_res('/api/daily-pulse/today', 'GET', res.status_code, res.get_json())

    res = client.get('/api/daily-pulse/schedule', headers=headers)
    log_res('/api/daily-pulse/schedule', 'GET', res.status_code, res.get_json())

    res = client.get('/api/surveys/metrics', headers=headers)
    log_res('/api/surveys/metrics', 'GET', res.status_code, res.get_json())

    # 10. LMS & Discussions
    print("\n10. Testing LMS Club & Discussions...")
    res = client.get('/api/lms-club/clubs', headers=headers)
    log_res('/api/lms-club/clubs', 'GET', res.status_code, res.get_json())

    res = client.get('/api/discussions', headers=headers)
    log_res('/api/discussions', 'GET', res.status_code, res.get_json())

    # 11. Surprise Ops
    print("\n11. Testing Surprise Ops...")
    res = client.get('/api/surprise-ops/coupons', headers=headers)
    log_res('/api/surprise-ops/coupons', 'GET', res.status_code, res.get_json())

    res = client.get('/api/surprise-ops/appreciation', headers=headers)
    log_res('/api/surprise-ops/appreciation', 'GET', res.status_code, res.get_json())

    # 12. Offboarding Status
    print("\n12. Testing Offboarding Status...")
    res = client.get('/api/offboarding/status', headers=headers)
    log_res('/api/offboarding/status', 'GET', res.status_code, res.get_json())

    # Summary
    print("\n================ AUTHENTICATED TEST SUMMARY ================")
    print(f"TOTAL TESTED ENDPOINTS: {len(results['endpoint_results'])}")
    print(f"PASSED: {results['passed']}")
    print(f"FAILED: {results['failed']}")

    if results["errors"]:
        print("\nFAILURES & ERRORS ENCOUNTERED:")
        for err in results["errors"]:
            print(f" - {err}")

    with open(r"C:\Users\Admin\.gemini\antigravity\scratch\hrms_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved full test output to hrms_test_results.json")

if __name__ == '__main__':
    run_tests()
