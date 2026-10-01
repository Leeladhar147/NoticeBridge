"""
Direct PostgreSQL & API Live Verification Script.
Executes Part 10 requirements:
1. Create test user via API.
2. Confirm user exists in PostgreSQL table 'users' via direct SQL query.
3. Create employment information via API.
4. Confirm persistence in PostgreSQL 'current_employments' & 'employment_contracts'.
5. Create new offer via API.
6. Confirm persistence in PostgreSQL 'new_offers'.
7. Log out and log back in, confirm data remains.
8. Create second test user.
9. Confirm second user CANNOT see first user's data.
"""

import sys
import uuid
import requests
import psycopg

BASE_URL = "http://localhost:8000"
DB_URL = "postgresql://noticebridge:noticebridge_dev_secret@localhost:5439/noticebridge"


def run_verification():
    print("=" * 70)
    print("NOTICEBRIDGE: LIVE POSTGRESQL & AUTH VERIFICATION")
    print("=" * 70)

    # Step 1: Create test account A
    uid = uuid.uuid4().hex[:8]
    email_a = f"michael.{uid}@example.com"
    pass_a = "Corleone2026!"
    name_a = "Michael Corleone"

    print(f"\n[1] Registering Test User 1 ({name_a} - {email_a})...")
    res = requests.post(f"{BASE_URL}/auth/register", json={
        "full_name": name_a,
        "email": email_a,
        "password": pass_a
    })
    assert res.status_code == 201, f"Register failed: {res.text}"
    auth_a = res.json()
    token_a = auth_a["access_token"]
    user_a_id = auth_a["user_id"]
    print(f" -> User 1 created. ID: {user_a_id}, Token received.")

    # Step 2: Confirm user exists directly in PostgreSQL table 'users'
    print("\n[2] Querying PostgreSQL table 'users' via raw SQL...")
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, email, password_hash, created_at FROM users WHERE id = %s;", (user_a_id,))
            row = cur.fetchone()
            assert row is not None, "User not found in PostgreSQL!"
            db_id, db_name, db_email, db_hash, db_created = row
            assert db_email == email_a
            assert db_name == name_a
            assert db_hash.startswith("$2b$"), "Password hash is not bcrypt!"
            assert db_hash != pass_a, "Password was stored in plaintext!"
            print(f" -> Confirmed in PostgreSQL: ID={db_id}, Name='{db_name}', Email='{db_email}', CreatedAt={db_created}")
            print(f" -> Password is secure bcrypt hash: {db_hash[:20]}...")

    # Step 3: Create employment information
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print("\n[3] Creating Current Employment for User 1...")
    emp_payload = {
        "company_name": "Corleone Holdings Ltd",
        "designation": "Director of Strategy",
        "joining_date": "2023-01-15",
        "resignation_date": "2026-09-01",
        "is_resigned": True,
        "notice_period_days": 90,
        "buyout_clause_permitted": True,
        "buyout_salary_basis": "basic",
        "monthly_divisor_basis": "30_days",
        "basic_salary_monthly": 120000.0,
        "gross_salary_monthly": 180000.0,
        "clause_reference_notes": "Clause 14.1: Notice buyout permitted at Basic rate."
    }
    emp_res = requests.post(f"{BASE_URL}/employment/current", headers=headers_a, json=emp_payload)
    assert emp_res.status_code == 201, f"Failed to save employment: {emp_res.text}"
    emp_id = emp_res.json()["id"]
    print(f" -> Employment record created. ID: {emp_id}")

    # Step 4: Confirm persistence in PostgreSQL 'current_employments' and 'employment_contracts'
    print("\n[4] Querying PostgreSQL tables 'current_employments' and 'employment_contracts' via raw SQL...")
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ce.id, ce.company_name, ce.user_id, ec.notice_period_days, ec.basic_salary_monthly
                FROM current_employments ce
                JOIN employment_contracts ec ON ec.current_employment_id = ce.id
                WHERE ce.user_id = %s;
            """, (user_a_id,))
            row = cur.fetchone()
            assert row is not None, "Employment not found in PostgreSQL!"
            print(f" -> Confirmed in PostgreSQL: EmploymentID={row[0]}, Company='{row[1]}', NoticeDays={row[3]}, BasicSalary=INR {row[4]:,}")

    # Step 5: Create new offer
    print("\n[5] Creating New Offer for User 1...")
    offer_payload = {
        "company_name": "Sundance Cloud Ventures",
        "designation": "Chief Technology Officer",
        "offered_ctc_annual": 3600000.0,
        "target_joining_date": "2026-10-31",
        "buyout_assistance_amount": 60000.0,
        "signing_bonus": 100000.0,
        "retention_clawback_months": 12
    }
    offer_res = requests.post(f"{BASE_URL}/employment/offer", headers=headers_a, json=offer_payload)
    assert offer_res.status_code == 201, f"Failed to save offer: {offer_res.text}"
    offer_id = offer_res.json()["id"]
    print(f" -> Offer record created. ID: {offer_id}")

    # Step 6: Confirm persistence in PostgreSQL 'new_offers'
    print("\n[6] Querying PostgreSQL table 'new_offers' via raw SQL...")
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, company_name, offered_ctc_annual, buyout_assistance_amount FROM new_offers WHERE user_id = %s;", (user_a_id,))
            row = cur.fetchone()
            assert row is not None, "Offer not found in PostgreSQL!"
            print(f" -> Confirmed in PostgreSQL: OfferID={row[0]}, Company='{row[1]}', AnnualCTC=INR {row[2]:,}, BuyoutAid=INR {row[3]:,}")

    # Step 7: Logout and Log back in
    print("\n[7] Testing Logout & Login session restoration...")
    logout_res = requests.post(f"{BASE_URL}/auth/logout", headers=headers_a)
    assert logout_res.status_code == 200
    print(" -> Logged out successfully.")

    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email_a,
        "password": pass_a
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token_a_new = login_res.json()["access_token"]
    headers_a_new = {"Authorization": f"Bearer {token_a_new}"}
    print(" -> Logged back in. New JWT received.")

    # Confirm data remains intact
    cur_emp_after = requests.get(f"{BASE_URL}/employment/current", headers=headers_a_new)
    assert cur_emp_after.status_code == 200
    assert cur_emp_after.json()["company_name"]["value"] == "Corleone Holdings Ltd"
    print(" -> Verified User 1 employment persisted across sessions: 'Corleone Holdings Ltd'")

    # Step 8: Create second test user (Kay Adams)
    email_b = f"kay.{uid}@example.com"
    pass_b = "Adams2026!"
    name_b = "Kay Adams"
    print(f"\n[8] Registering Test User 2 ({name_b} - {email_b})...")
    res_b = requests.post(f"{BASE_URL}/auth/register", json={
        "full_name": name_b,
        "email": email_b,
        "password": pass_b
    })
    assert res_b.status_code == 201
    token_b = res_b.json()["access_token"]
    user_b_id = res_b.json()["user_id"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    print(f" -> User 2 created. ID: {user_b_id}")

    # Step 9: Confirm User 2 CANNOT access User 1's data
    print("\n[9] Checking User Data Isolation between User 1 and User 2...")
    user2_cur_emp = requests.get(f"{BASE_URL}/employment/current", headers=headers_b)
    assert user2_cur_emp.status_code == 404, "Security violation: User 2 accessed User 1's employment!"
    print(" -> User 2 queried /employment/current: Returned 404 (No data for User 2). [ISOLATION VERIFIED]")

    user2_offer = requests.get(f"{BASE_URL}/employment/offer", headers=headers_b)
    assert user2_offer.status_code == 404, "Security violation: User 2 accessed User 1's offer!"
    print(" -> User 2 queried /employment/offer: Returned 404 (No data for User 2). [ISOLATION VERIFIED]")

    # Check total users in PostgreSQL
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users;")
            total_users = cur.fetchone()[0]
            print(f"\n[10] Total users stored in PostgreSQL 'users' table: {total_users}")

    print("\n" + "=" * 70)
    print("ALL POSTGRESQL & DATA ISOLATION VERIFICATION CHECKS PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    run_verification()
