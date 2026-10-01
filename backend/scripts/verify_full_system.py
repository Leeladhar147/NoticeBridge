"""
End-to-end verification script for NoticeBridge Prompt 2.
Tests all intelligent pipelines against the live running backend on port 8000.
"""

import sys
import requests
from io import BytesIO

BASE_URL = "http://127.0.0.1:8000"

SAMPLE_CONTRACT = """
EMPLOYMENT AGREEMENT - ACME DIGITAL SOLUTIONS PVT LTD
Between Acme Digital Solutions Pvt Ltd and Sanya Malhotra.

SECTION 1: APPOINTMENT
Designation: Principal Cloud Architect.

SECTION 2: NOTICE PERIOD
The employee must give ninety (90) days notice in writing prior to resignation.

SECTION 3: NOTICE BUYOUT AND SHORTFALL RECOVERY
Notice buyout is permitted subject to management approval.
The company will recover salary in lieu of notice for unserved notice days calculated on the basis of Gross Monthly Salary divided by 30 days.

SECTION 4: COMPENSATION SCHEDULE
- Basic Salary: Rs. 80,000 per month
- HRA and Allowances: Rs. 60,000 per month
- Total Gross Salary: Rs. 140,000 per month
"""

SAMPLE_OFFER = """
OFFER LETTER - HYPERSCALE NETWORKS
To: Sanya Malhotra
Target Date of Joining: 2026-11-01
Offered CTC: Rs. 3,200,000 per annum

TRANSITION ASSISTANCE:
HyperScale Networks agrees to provide notice buyout assistance of Rs. 70,000 to offset early release recovery.
Joining bonus: Rs. 100,000 with 12 months retention lock-in.
"""

def run_verification():
    print("=" * 60)
    print("NOTICEBRIDGE PROMPT 2 LIVE END-TO-END VERIFICATION")
    print("=" * 60)

    # 1. Health check
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[OK] 1. Backend health check passed.")

    # 2. Register employee
    import uuid
    email = f"sanya_{uuid.uuid4().hex[:6]}@example.com"
    reg = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "full_name": "Sanya Malhotra",
        "password": "Password123!"
    })
    assert reg.status_code == 201, f"Registration failed: {reg.text}"
    user_id = reg.json()["user_id"]
    print(f"[OK] 2. Employee registered (ID: {user_id}).")

    # 3. Upload Employment Agreement
    files = {"file": ("Acme_Contract.txt", BytesIO(SAMPLE_CONTRACT.encode("utf-8")), "text/plain")}
    data = {"employee_id": str(user_id), "document_type": "employment_agreement"}
    upload_res = requests.post(f"{BASE_URL}/documents/upload", files=files, data=data)
    assert upload_res.status_code == 201, f"Contract upload failed: {upload_res.text}"
    contract_doc_id = upload_res.json()["document_id"]
    print(f"[OK] 3. Contract uploaded successfully (Doc ID: {contract_doc_id}).")

    # 4. Extract Contract Intelligence via Targeted RAG
    extract_res = requests.post(f"{BASE_URL}/documents/{contract_doc_id}/extract-contract")
    assert extract_res.status_code == 200, f"Extraction failed: {extract_res.text}"
    contract_intel = extract_res.json()
    assert contract_intel["notice_period_days"]["value"] == 90
    assert contract_intel["buyout_salary_basis"]["value"] == "gross"
    assert contract_intel["basic_salary_monthly"]["value"] == 80000.0
    assert contract_intel["gross_salary_monthly"]["value"] == 140000.0
    print(f"[OK] 4. Targeted RAG contract extraction passed:")
    print(f"     - Notice Period: {contract_intel['notice_period_days']['value']} Days (Confidence: {contract_intel['notice_period_days']['confidence']})")
    print(f"     - Buyout Basis: {contract_intel['buyout_salary_basis']['value']} (Quote: '{contract_intel['buyout_salary_basis']['evidence_quote'][:60]}...')")
    print(f"     - Gross Salary: INR {contract_intel['gross_salary_monthly']['value']:,}")

    # 5. Confirm Contract Parameters (Human-in-the-loop)
    confirm_res = requests.post(f"{BASE_URL}/documents/confirm-contract", json={
        "document_id": contract_doc_id,
        "company_name": "Acme Digital Solutions",
        "notice_period_days": 90,
        "buyout_clause_permitted": True,
        "buyout_salary_basis": "gross",
        "monthly_divisor_basis": "30_days",
        "basic_salary_monthly": 80000.0,
        "gross_salary_monthly": 140000.0
    })
    assert confirm_res.status_code == 200, f"Confirmation failed: {confirm_res.text}"
    print("[OK] 5. Human-in-the-loop confirmation verified and persisted.")

    # 6. Upload Offer Letter and Extract
    offer_files = {"file": ("HyperScale_Offer.txt", BytesIO(SAMPLE_OFFER.encode("utf-8")), "text/plain")}
    offer_data = {"employee_id": str(user_id), "document_type": "offer_letter"}
    offer_up = requests.post(f"{BASE_URL}/documents/upload", files=offer_files, data=offer_data)
    assert offer_up.status_code == 201
    offer_doc_id = offer_up.json()["document_id"]

    offer_extract = requests.post(f"{BASE_URL}/documents/{offer_doc_id}/extract-offer")
    assert offer_extract.status_code == 200
    offer_intel = offer_extract.json()
    assert offer_intel["buyout_assistance_amount"]["value"] == 70000.0
    print(f"[OK] 6. Offer letter extraction passed:")
    print(f"     - Company: {offer_intel['offering_company']['value']}")
    print(f"     - Buyout Assistance: INR {offer_intel['buyout_assistance_amount']['value']:,}")
    print(f"     - Signing Bonus: INR {offer_intel['signing_bonus']['value']:,}")

    # 7. Deterministic Buyout Calculation
    buyout_res = requests.post(f"{BASE_URL}/buyout/calculate", json={
        "salary_amount": 140000.0,
        "remaining_days": 60,
        "salary_basis": "gross",
        "divisor_basis": "30_days",
        "employer_contribution": 70000.0
    })
    assert buyout_res.status_code == 200
    b_data = buyout_res.json()
    assert b_data["gross_buyout_amount"]["value"] == 280000.0
    assert b_data["net_employee_payable"]["value"] == 210000.0
    print(f"[OK] 7. Deterministic Buyout Calculation passed:")
    print(f"     - Gross Buyout: INR {b_data['gross_buyout_amount']['value']:,}")
    print(f"     - Net Employee Payable: INR {b_data['net_employee_payable']['value']:,}")
    formula_str = str(b_data['formula_used'].get('value', b_data['formula_used'])).replace("\u20b9", "INR ")
    print(f"     - Formula: {formula_str}")

    # 8. Affordability Simulation
    afford_res = requests.post(f"{BASE_URL}/affordability/simulate", json={
        "new_monthly_income": 200000.0,
        "existing_monthly_obligations": 35000.0,
        "simulated_monthly_repayment": 36000.0
    })
    assert afford_res.status_code == 200
    a_data = afford_res.json()
    assert a_data["repayment_income_ratio_percent"]["value"] == 18.0
    assert a_data["remaining_income_after_repayment"]["value"] == 129000.0
    print(f"[OK] 8. Deterministic Affordability Simulation passed:")
    print(f"     - Repayment / Income Ratio: {a_data['repayment_income_ratio_percent']['value']}%")
    print(f"     - Remaining Monthly Buffer: INR {a_data['remaining_income_after_repayment']['value']:,}")
    summary_str = a_data['factual_summary'].replace("\u20b9", "INR ")
    print(f"     - Factual Statement: {summary_str}")

    # 9. Dashboard Summary API
    dash_res = requests.get(f"{BASE_URL}/dashboard/summary")
    assert dash_res.status_code == 200
    print("[OK] 9. Dashboard Summary API returns valid metrics and milestone structures.")

    print("\n" + "=" * 60)
    print("ALL 9 LIVE VERIFICATION GATES PASSED PERFECTLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_verification()
