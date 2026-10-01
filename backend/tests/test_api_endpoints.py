import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import Base, engine

Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "NoticeBridge"
    assert "NoticePeriodCalculator" in data["engines_active"]

def test_current_employment_crud():
    payload = {
        "company_name": "Acme Corp",
        "designation": "Staff Engineer",
        "joining_date": "2024-01-01",
        "resignation_date": "2026-01-01",
        "is_resigned": True,
        "notice_period_days": 90,
        "buyout_clause_permitted": True,
        "buyout_salary_basis": "basic",
        "monthly_divisor_basis": "30_days",
        "basic_salary_monthly": 75000.0,
        "gross_salary_monthly": 110000.0,
        "clause_reference_notes": "Clause 8.1: Notice buyout allowed."
    }
    response = client.post("/employment/current", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["company_name"]["value"] == "Acme Corp"
    assert data["notice_period_days"]["origin"] == "contract-derived"
    assert data["basic_salary_monthly"]["value"] == 75000.0

    # Get current employment
    get_res = client.get("/employment/current")
    assert get_res.status_code == 200
    assert get_res.json()["company_name"]["value"] == "Acme Corp"

def test_new_offer_crud():
    payload = {
        "company_name": "NextGen Systems",
        "designation": "Principal Engineer",
        "offered_ctc_annual": 2400000.0,
        "target_joining_date": (date.today() + timedelta(days=30)).isoformat(),
        "buyout_assistance_amount": 40000.0,
        "signing_bonus": 50000.0,
        "retention_clawback_months": 12
    }
    response = client.post("/employment/offer", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["company_name"]["value"] == "NextGen Systems"
    assert data["buyout_assistance_amount"]["value"] == 40000.0

    get_res = client.get("/employment/offer")
    assert get_res.status_code == 200
    assert get_res.json()["company_name"]["value"] == "NextGen Systems"

def test_notice_calculate_api():
    payload = {
        "contractual_notice_period": 90,
        "resignation_date": "2026-01-01",
        "intended_joining_date": "2026-01-31",
        "days_already_served": 30,
        "leave_adjustment_days": 0
    }
    response = client.post("/notice/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["remaining_notice_days"]["value"] == 60
    assert data["shortfall_days"]["value"] == 60
    assert data["shortfall_days"]["origin"] == "calculated"
    assert data["contractual_notice_days"]["origin"] == "contract-derived"

def test_notice_calculate_api_validation_error():
    # Intended joining earlier than resignation
    payload = {
        "contractual_notice_period": 90,
        "resignation_date": "2026-05-01",
        "intended_joining_date": "2026-04-01",
        "days_already_served": 0
    }
    response = client.post("/notice/calculate", json=payload)
    assert response.status_code == 422

def test_buyout_calculate_api():
    payload = {
        "salary_amount": 60000.0,
        "remaining_days": 60,
        "salary_basis": "basic",
        "divisor_basis": "30_days",
        "employer_contribution": 20000.0
    }
    response = client.post("/buyout/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["gross_buyout_amount"]["value"] == 120000.0
    assert data["net_employee_payable"]["value"] == 100000.0
    assert data["daily_rate"]["value"] == 2000.0
    assert "₹60,000.00 / 30" in data["formula_used"]["value"]

def test_buyout_calculate_zero_salary_error():
    payload = {
        "salary_amount": 0.0,
        "remaining_days": 30,
        "salary_basis": "basic"
    }
    response = client.post("/buyout/calculate", json=payload)
    assert response.status_code == 422

def test_repayment_calculate_api():
    payload = {
        "principal": 120000.0,
        "duration_months": 6,
        "annual_interest_rate_percent": 10.0,
        "service_fee_percent": 1.5
    }
    response = client.post("/repayment/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["principal_amount"]["value"] == 120000.0
    assert data["total_service_fee"]["value"] == 1800.0
    assert len(data["amortization_schedule"]) == 6
    assert data["amortization_schedule"][0]["month"] == 1

def test_scenario_simulate_api():
    payload = {
        "contractual_notice_period": 90,
        "resignation_date": "2026-01-01",
        "intended_joining_date": "2026-01-31",
        "days_already_served": 30,
        "leave_adjustment_days": 0,
        "monthly_salary": 60000.0,
        "gross_monthly_salary": 90000.0,
        "salary_basis": "basic",
        "divisor_basis": "30_days",
        "employer_offered_contribution": 30000.0,
        "preferred_tenor_months": 6,
        "annual_interest_rate_percent": 10.0
    }
    response = client.post("/scenario/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["scenarios"]) >= 5
    assert "summary_recommendation" in data

def test_dashboard_summary_api():
    response = client.get("/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "contractual_notice_period_days" in data
    assert "estimated_buyout_gross" in data
    assert "repayment_estimate_monthly" in data
    assert "transition_status" in data
    assert "legal_disclaimer" in data

def test_auth_login_and_register():
    import uuid
    uid = str(uuid.uuid4())[:8]
    test_email = f"jordan.{uid}@example.com"
    reg_payload = {
        "full_name": "Jordan Lee",
        "email": test_email,
        "password": "securepassword123"
    }
    reg_res = client.post("/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    assert "nb_token_" in reg_res.json()["access_token"]

    login_res = client.post("/auth/login", json={
        "email": test_email,
        "password": "securepassword123"
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()
