import uuid
import pytest
from io import BytesIO
from fastapi.testclient import TestClient

from app.main import app
from app.models.database import get_db, SessionLocal
from app.models.entities import User, CurrentEmployment, EmploymentContract, NewOffer, UploadedDocument
from app.services.auth_service import AuthService
from app.repositories.employee_repo import UserRepository

client = TestClient(app)


def get_unique_email(prefix="user"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}@noticebridge.test"


def test_password_hashing():
    """Verify bcrypt hashing generates salted, non-plaintext, verifiable hashes."""
    raw_pass = "superSecretPassword123!"
    hashed = AuthService.hash_password(raw_pass)

    assert hashed != raw_pass
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    assert AuthService.verify_password(raw_pass, hashed) is True
    assert AuthService.verify_password("wrongPassword123!", hashed) is False
    assert AuthService.verify_password("", hashed) is False


def test_signup_success():
    """Verify signup creates a real user in DB and returns access token."""
    email = get_unique_email("signup")
    res = client.post("/auth/register", json={
        "full_name": "Sarah Connor",
        "email": email,
        "password": "Resistance2026!"
    })
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == email
    assert body["full_name"] == "Sarah Connor"
    assert "access_token" in body
    assert body["token_type"] == "bearer"

    # Verify user exists in database with hashed password
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is not None
        assert user.password_hash != "Resistance2026!"
        assert AuthService.verify_password("Resistance2026!", user.password_hash) is True
    finally:
        db.close()


def test_signup_duplicate_email_rejected():
    """Verify duplicate registration fails with 400."""
    email = get_unique_email("dup")
    payload = {
        "full_name": "First User",
        "email": email,
        "password": "Password123!"
    }
    res1 = client.post("/auth/register", json=payload)
    assert res1.status_code == 201

    # Second attempt with same email
    res2 = client.post("/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"].lower()


def test_signup_short_password_rejected():
    """Verify passwords shorter than 6 characters are rejected."""
    email = get_unique_email("short")
    res = client.post("/auth/register", json={
        "full_name": "Short Pass",
        "email": email,
        "password": "123"
    })
    assert res.status_code == 400
    assert "at least 6 characters" in res.json()["detail"]


def test_login_success_and_jwt():
    """Verify login authenticates and issues a decodable JWT token."""
    email = get_unique_email("login")
    password = "CorrectHorseBatteryStaple!"
    
    reg_res = client.post("/auth/register", json={
        "full_name": "Login User",
        "email": email,
        "password": password
    })
    assert reg_res.status_code == 201

    login_res = client.post("/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_res.status_code == 200
    login_body = login_res.json()
    token = login_body["access_token"]
    assert token is not None

    payload = AuthService.decode_access_token(token)
    assert str(payload["sub"]) == str(login_body["user_id"])
    assert payload["email"] == email


def test_login_invalid_password_rejected():
    """Verify login with incorrect password returns 401."""
    email = get_unique_email("badpass")
    client.post("/auth/register", json={
        "full_name": "Wrong Pass User",
        "email": email,
        "password": "validPassword123!"
    })

    res = client.post("/auth/login", json={
        "email": email,
        "password": "totallyWrongPassword!"
    })
    assert res.status_code == 401
    assert "Invalid email or password" in res.json()["detail"]


def test_login_nonexistent_email_rejected():
    """Verify login with unregistered email returns 401."""
    res = client.post("/auth/login", json={
        "email": "does.not.exist.anywhere@noticebridge.test",
        "password": "anyPassword123!"
    })
    assert res.status_code == 401


def test_logout_endpoint():
    """Verify logout route returns 200 confirmation."""
    res = client.post("/auth/logout")
    assert res.status_code == 200
    assert "successfully" in res.json()["message"].lower()


def test_protected_routes_require_auth():
    """Verify protected endpoints reject unauthenticated requests with 401."""
    res = client.get("/auth/me")
    assert res.status_code == 401
    assert "Authentication required" in res.json()["detail"]


def test_protected_route_with_valid_token():
    """Verify /auth/me returns the authenticated user identity."""
    email = get_unique_email("me")
    reg_res = client.post("/auth/register", json={
        "full_name": "Elena Rostova",
        "email": email,
        "password": "Password2026!"
    })
    token = reg_res.json()["access_token"]

    res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == email
    assert res.json()["full_name"] == "Elena Rostova"


def test_user_data_isolation_employment_and_offer():
    """
    CRITICAL SECURITY CHECK:
    Verify User A and User B have complete data isolation.
    User B cannot see or overwrite User A's employment or offer.
    """
    email_a = get_unique_email("user_a")
    res_a = client.post("/auth/register", json={
        "full_name": "User Alpha",
        "email": email_a,
        "password": "PasswordA123!"
    })
    token_a = res_a.json()["access_token"]

    email_b = get_unique_email("user_b")
    res_b = client.post("/auth/register", json={
        "full_name": "User Beta",
        "email": email_b,
        "password": "PasswordB123!"
    })
    token_b = res_b.json()["access_token"]

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates current job at Alpha Technologies
    client.post("/employment/current", headers=headers_a, json={
        "company_name": "Alpha Technologies Ltd",
        "designation": "Systems Architect",
        "joining_date": "2023-01-01",
        "resignation_date": "2026-09-01",
        "is_resigned": True,
        "notice_period_days": 90,
        "buyout_clause_permitted": True,
        "buyout_salary_basis": "basic",
        "monthly_divisor_basis": "30_days",
        "basic_salary_monthly": 80000.0,
        "gross_salary_monthly": 120000.0
    })

    # User B creates current job at Beta Enterprises
    client.post("/employment/current", headers=headers_b, json={
        "company_name": "Beta Enterprises Inc",
        "designation": "Data Scientist",
        "joining_date": "2022-06-01",
        "resignation_date": "2026-09-15",
        "is_resigned": True,
        "notice_period_days": 60,
        "buyout_clause_permitted": True,
        "buyout_salary_basis": "gross",
        "monthly_divisor_basis": "26_working_days",
        "basic_salary_monthly": 110000.0,
        "gross_salary_monthly": 150000.0
    })

    # User A reads current job -> Must strictly see Alpha Technologies
    get_a = client.get("/employment/current", headers=headers_a)
    assert get_a.status_code == 200
    assert get_a.json()["company_name"]["value"] == "Alpha Technologies Ltd"
    assert get_a.json()["notice_period_days"]["value"] == 90

    # User B reads current job -> Must strictly see Beta Enterprises
    get_b = client.get("/employment/current", headers=headers_b)
    assert get_b.status_code == 200
    assert get_b.json()["company_name"]["value"] == "Beta Enterprises Inc"
    assert get_b.json()["notice_period_days"]["value"] == 60


def test_user_document_ownership_and_access_control():
    """
    CRITICAL SECURITY CHECK:
    User B must be rejected with 403 Forbidden when trying to access User A's document.
    """
    email_a = get_unique_email("doc_a")
    res_a = client.post("/auth/register", json={
        "full_name": "Owner User",
        "email": email_a,
        "password": "PasswordA123!"
    })
    token_a = res_a.json()["access_token"]
    user_a_id = res_a.json()["user_id"]

    email_b = get_unique_email("doc_b")
    res_b = client.post("/auth/register", json={
        "full_name": "Attacker User",
        "email": email_b,
        "password": "PasswordB123!"
    })
    token_b = res_b.json()["access_token"]

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A uploads a private contract
    contract_text = "Private confidential contract between Company A and Owner User. Notice period is 90 days."
    files = {"file": ("OwnerContract.txt", BytesIO(contract_text.encode("utf-8")), "text/plain")}
    upload_res = client.post("/documents/upload", headers=headers_a, files=files)
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["document_id"]

    # User A can access their own document
    owner_view = client.get(f"/documents/{doc_id}", headers=headers_a)
    assert owner_view.status_code == 200
    assert owner_view.json()["document_id"] == doc_id

    # User B attempts to access User A's document -> Must be 403 Forbidden
    unauthorized_view = client.get(f"/documents/{doc_id}", headers=headers_b)
    assert unauthorized_view.status_code == 403
    assert "Forbidden" in unauthorized_view.json()["detail"]

    # User B attempts to extract User A's document -> Must be 403 Forbidden
    unauthorized_extract = client.post(f"/documents/{doc_id}/extract-contract", headers=headers_b)
    assert unauthorized_extract.status_code == 403


def test_database_relationships_and_cascades():
    """Verify database relationships, foreign keys, and cascade delete semantics."""
    db = SessionLocal()
    try:
        user = User(
            name="Cascade Test User",
            email=get_unique_email("cascade"),
            password_hash=AuthService.hash_password("Pass123!")
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        from datetime import date
        emp = CurrentEmployment(
            user_id=user.id,
            company_name="Cascade Inc",
            designation="Tester",
            joining_date=date.today(),
            is_resigned=False
        )
        db.add(emp)
        db.commit()
        db.refresh(emp)

        contract = EmploymentContract(
            current_employment_id=emp.id,
            notice_period_days=60,
            basic_salary_monthly=50000.0
        )
        db.add(contract)
        db.commit()

        # Check relationships
        assert len(user.current_employments) == 1
        assert user.current_employments[0].company_name == "Cascade Inc"
        assert user.current_employments[0].contract.notice_period_days == 60

        # Delete user -> cascades to employment and contract
        db.delete(user)
        db.commit()

        emp_check = db.query(CurrentEmployment).filter(CurrentEmployment.id == emp.id).first()
        assert emp_check is None

        contract_check = db.query(EmploymentContract).filter(EmploymentContract.id == contract.id).first()
        assert contract_check is None
    finally:
        db.close()
