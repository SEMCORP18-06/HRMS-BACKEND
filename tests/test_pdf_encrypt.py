import os
import sys
from pypdf import PdfReader

# Add backend root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.pdf_encrypt import generate_salary_breakup_pdf, encrypt_pdf_aes

def run_test():
    print("[TEST] Running PDF Generation & AES-256 Encryption verification...")
    
    employee = {
        "name": "Test User",
        "email": "test@company.com",
        "role": "QA Architect",
        "designation": "QA Architect",
        "department": "Quality Assurance",
        "status": "ACTIVE"
    }
    
    payroll = {
        "basic_salary": 7500.0,
        "allowances": 1250.0,
        "deductions": 600.0,
        "pay_period": "2026-06"
    }
    
    temp_pdf = "test_temp_payslip.pdf"
    encrypted_pdf = "test_encrypted_payslip.pdf"
    password = "test@company.com"
    
    # 1. Generate PDF
    print("[TEST] Generating unencrypted salary breakup PDF...")
    generate_salary_breakup_pdf(employee, payroll, temp_pdf)
    assert os.path.exists(temp_pdf), "Unencrypted PDF was not created!"
    print("[TEST] Unencrypted PDF created successfully.")
    
    # 2. Encrypt PDF
    print("[TEST] Encrypting PDF with AES-256 password protect...")
    encrypt_pdf_aes(temp_pdf, encrypted_pdf, password)
    assert os.path.exists(encrypted_pdf), "Encrypted PDF was not created!"
    assert not os.path.exists(temp_pdf), "Temporary unencrypted PDF was not deleted!"
    print("[TEST] PDF encrypted and unencrypted file cleaned up.")
    
    # 3. Read without password (should show encrypted)
    print("[TEST] Attempting to read encrypted PDF without password...")
    reader = PdfReader(encrypted_pdf)
    assert reader.is_encrypted, "PDF is not flagged as encrypted!"
    print("[TEST] Verified PDF is flagged as encrypted.")
    
    # 4. Decrypt with wrong password
    print("[TEST] Attempting to decrypt with WRONG password...")
    decrypt_fail_status = reader.decrypt("wrongpassword")
    assert decrypt_fail_status == 0, "Decryption succeeded with invalid password!"
    print("[TEST] Correctly failed decryption with wrong password.")
    
    # 5. Decrypt with correct password
    print("[TEST] Decrypting with CORRECT password...")
    decrypt_success_status = reader.decrypt(password)
    assert decrypt_success_status > 0, "Decryption failed with correct password!"
    print(f"[TEST] Decryption success status: {decrypt_success_status}")
    
    text = reader.pages[0].extract_text()
    assert "Salary Slip" in text, "Could not find payslip text in decrypted PDF!"
    assert "QA Architect" in text, "Could not find employee role in decrypted PDF!"
    assert "7,500.00" in text, "Could not find base salary amount in decrypted PDF!"
    print("[TEST] Verified decrypted content is accurate and complete.")
    
    # Clean up test output
    if os.path.exists(encrypted_pdf):
        os.remove(encrypted_pdf)
        
    print("\n[TEST SUCCESS] PDF AES-256 encryption pipeline verified successfully!")

if __name__ == "__main__":
    run_test()
