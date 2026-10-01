import React, { useState, useEffect } from 'react';
import { Coins, Calculator, FileText, ArrowRight, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { api } from '../api/client';
import OriginBadge from '../components/OriginBadge';
import AffordabilitySimulator from '../components/AffordabilitySimulator';

export default function BuyoutCalculatorPage({ setActivePage }) {
  const [params, setParams] = useState({
    salary_amount: 60000,
    remaining_days: 60,
    salary_basis: 'basic',
    divisor_basis: '30_days',
    custom_divisor: null,
    employer_contribution: 30000,
    currency_symbol: '₹'
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [tenor, setTenor] = useState(6);
  const [apr, setApr] = useState(10);
  const [repayResult, setRepayResult] = useState(null);

  const runCalculation = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.calculateBuyout({
        ...params,
        salary_amount: Number(params.salary_amount),
        remaining_days: Number(params.remaining_days),
        employer_contribution: Number(params.employer_contribution),
        custom_divisor: params.custom_divisor ? Number(params.custom_divisor) : null
      });
      setResult(res);

      if (res && res.net_employee_payable.value > 0) {
        const repay = await api.calculateRepayment({
          principal: res.net_employee_payable.value,
          duration_months: tenor,
          annual_interest_rate_percent: apr,
          service_fee_percent: 1.5
        });
        setRepayResult(repay);
      } else {
        setRepayResult(null);
      }
    } catch (err) {
      setError(err.message || 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runCalculation();
  }, [params, tenor, apr]);

  const handleCTA = (page) => {
    setActivePage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div style={{ background: '#FFFFFF', minHeight: '100%' }}>
      <div className="container" style={{ padding: '36px 24px 60px 24px', maxWidth: '1040px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <div style={{
            background: 'var(--parrot-green-light)',
            padding: '8px',
            borderRadius: '8px',
            color: 'var(--parrot-green)'
          }}>
            <Coins size={24} />
          </div>
          <div>
            <h1 style={{ fontSize: '1.9rem', color: 'var(--text-primary)' }}>Contractual Buyout Calculator</h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
              Deterministic financial engine: configurable salary bases, divisors, and explainable formula audits
            </p>
          </div>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '24px',
          marginTop: '20px'
        }}>
          {/* Form Controls */}
          <div className="sports-card" style={{ background: '#FFFFFF' }}>
            <h3 style={{ fontSize: '1.15rem', marginBottom: '16px', color: 'var(--text-primary)', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
              Contractual Parameters
            </h3>

            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                  Applicable Monthly Salary (₹)
                </label>
                <OriginBadge origin="contract-derived" source="Pay Annexure" compact />
              </div>
              <input
                type="number"
                min="1"
                step="1000"
                className="form-input"
                value={params.salary_amount}
                onChange={(e) => setParams({ ...params, salary_amount: e.target.value })}
              />
            </div>

            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                  Remaining Notice / Shortfall Days
                </label>
                <OriginBadge origin="calculated" source="Notice Engine" compact />
              </div>
              <input
                type="number"
                min="0"
                max="365"
                className="form-input"
                value={params.remaining_days}
                onChange={(e) => setParams({ ...params, remaining_days: e.target.value })}
              />
            </div>

            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                  Contractual Salary Basis
                </label>
                <OriginBadge origin="contract-derived" source="Contract" compact />
              </div>
              <select
                className="form-input"
                value={params.salary_basis}
                onChange={(e) => setParams({ ...params, salary_basis: e.target.value })}
              >
                <option value="basic">Basic Salary Basis</option>
                <option value="gross">Gross Salary Basis</option>
                <option value="fixed">Fixed Salary Basis</option>
                <option value="custom">Custom Contractual Basis</option>
              </select>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                  Contractual Divisor Basis
                </label>
                <OriginBadge origin="contract-derived" source="Contract Clause" compact />
              </div>
              <select
                className="form-input"
                value={params.divisor_basis}
                onChange={(e) => setParams({ ...params, divisor_basis: e.target.value })}
              >
                <option value="30_days">30-Day Monthly Basis (₹ / 30)</option>
                <option value="26_working_days">26 Working Days Basis (₹ / 26)</option>
                <option value="calendar_month">Calendar Days in Month (28-31)</option>
                <option value="annual_365">Annualized Salary / 365 Days</option>
                <option value="custom">Custom Explicit Divisor</option>
              </select>
            </div>

            {params.divisor_basis === 'custom' && (
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
                  Custom Divisor Value
                </label>
                <input
                  type="number"
                  step="0.5"
                  className="form-input"
                  value={params.custom_divisor || ''}
                  onChange={(e) => setParams({ ...params, custom_divisor: e.target.value })}
                />
              </div>
            )}

            <div style={{ marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                  New Employer Buyout Assistance Co-Pay (₹)
                </label>
                <OriginBadge origin="user-provided" source="Offer Letter" compact />
              </div>
              <input
                type="number"
                min="0"
                step="5000"
                className="form-input"
                value={params.employer_contribution}
                onChange={(e) => setParams({ ...params, employer_contribution: e.target.value })}
              />
            </div>

            {error && (
              <div style={{
                background: 'var(--tradelearn-pink-light)',
                border: '1px solid var(--tradelearn-pink-border)',
                color: 'var(--tradelearn-pink-text)',
                padding: '10px 14px',
                borderRadius: '8px',
                fontSize: '0.85rem'
              }}>
                {error}
              </div>
            )}
          </div>

          {/* Output Display Card */}
          {result && (
            <div className="sports-card sports-card-glow-volt" style={{ background: '#FFFFFF' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3 style={{ fontSize: '1.15rem', color: 'var(--text-primary)' }}>Deterministic Buyout Audit</h3>
                <OriginBadge origin="calculated" source="BuyoutCalculator" />
              </div>

              {/* Formula Highlight Banner as required in Prompt: ₹60,000 / 30 × 60 = ₹120,000 */}
              <div style={{
                background: 'var(--parrot-green-light)',
                border: '1.5px solid var(--parrot-green-border)',
                borderRadius: '10px',
                padding: '16px',
                marginBottom: '18px'
              }}>
                <div style={{ fontSize: '0.74rem', color: 'var(--parrot-green-text)', textTransform: 'uppercase', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
                  Contractual Formula Used
                </div>
                <div style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '1.15rem',
                  fontWeight: 700,
                  color: 'var(--text-primary)',
                  marginTop: '4px'
                }}>
                  {result.formula_used.value}
                </div>
              </div>

              {/* Key Output Numbers */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '18px' }}>
                <div style={{ background: 'var(--bg-secondary)', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Daily Rate</div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 900, color: 'var(--text-primary)', fontFamily: 'var(--font-heading)' }}>
                    ₹{result.daily_rate.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    Basis: {result.salary_basis.value} / {result.divisor_value.value} days
                  </div>
                </div>

                <div style={{ background: 'var(--bg-secondary)', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Gross Buyout</div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 900, color: 'var(--parrot-green)', fontFamily: 'var(--font-heading)' }}>
                    ₹{result.gross_buyout_amount.value.toLocaleString()}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    For {result.remaining_days.value} remaining days
                  </div>
                </div>

                <div style={{ background: 'var(--bg-secondary)', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Employer Co-Pay</div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 900, color: '#0284C7', fontFamily: 'var(--font-heading)' }}>
                    ₹{result.employer_contribution.value.toLocaleString()}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    Applied to invoice
                  </div>
                </div>

                {/* Net Employee Liability - TradeLearn Pink highlight */}
                <div style={{ background: 'var(--tradelearn-pink-light)', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--tradelearn-pink-border)' }}>
                  <div style={{ fontSize: '0.74rem', color: 'var(--tradelearn-pink-text)', textTransform: 'uppercase', fontWeight: 700 }}>
                    Net Liability
                  </div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 900, color: 'var(--tradelearn-pink)', fontFamily: 'var(--font-heading)' }}>
                    ₹{result.net_employee_payable.value.toLocaleString()}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--tradelearn-pink-text)', marginTop: '2px' }}>
                    Immediate liquidity need
                  </div>
                </div>
              </div>

              {/* Repayment Simulation Quick Slider */}
              {repayResult && (
                <div style={{
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '10px',
                  padding: '14px 16px',
                  marginBottom: '18px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div style={{ fontSize: '0.84rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                      Financing Simulation ({tenor} Months @ {apr}% APR)
                    </div>
                    <OriginBadge origin="calculated" source="RepaymentCalculator" compact />
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Monthly Installment</div>
                      <div style={{ fontSize: '1.5rem', fontWeight: 900, color: 'var(--parrot-green)', fontFamily: 'var(--font-heading)' }}>
                        ₹{repayResult.monthly_repayment_amount.value.toLocaleString()}/mo
                      </div>
                    </div>
                    <div>
                      <label style={{ fontSize: '0.74rem', color: 'var(--text-muted)', display: 'block', marginBottom: '2px' }}>Tenor</label>
                      <select
                        className="form-input"
                        value={tenor}
                        onChange={(e) => setTenor(Number(e.target.value))}
                        style={{ padding: '5px 10px', fontSize: '0.82rem', width: 'auto' }}
                      >
                        <option value="3">3 Months</option>
                        <option value="6">6 Months</option>
                        <option value="9">9 Months</option>
                        <option value="12">12 Months</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              <button
                onClick={() => handleCTA('scenarios')}
                className="btn-volt"
                style={{ width: '100%', padding: '11px' }}
              >
                Compare All 6 Transition Scenarios <ArrowRight size={16} />
              </button>
            </div>
          )}
        </div>

        {/* Step-by-Step Mathematical Explanation Table */}
        {result && result.detailed_steps && (
          <div className="sports-card" style={{ marginTop: '28px', background: '#FFFFFF' }}>
            <h3 style={{ fontSize: '1.15rem', marginBottom: '16px', color: 'var(--text-primary)' }}>
              Step-by-Step Contractual Math Breakdown
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
              <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ color: 'var(--parrot-green-text)', fontWeight: 800, fontSize: '0.82rem', marginBottom: '4px' }}>
                  Step 1: Applicable Salary
                </div>
                <div style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
                  {result.detailed_steps.step_1_applicable_salary?.description}
                </div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.9rem', color: 'var(--text-primary)', marginTop: '6px', fontWeight: 700 }}>
                  ₹{result.detailed_steps.step_1_applicable_salary?.amount.toLocaleString()}
                </div>
              </div>

              <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ color: '#0284C7', fontWeight: 800, fontSize: '0.82rem', marginBottom: '4px' }}>
                  Step 2: Daily Rate Math
                </div>
                <div style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
                  {result.detailed_steps.step_2_daily_rate?.calculation}
                </div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                  Divisor: {result.detailed_steps.step_2_daily_rate?.divisor_basis}
                </div>
              </div>

              <div style={{ background: 'var(--bg-secondary)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ color: 'var(--parrot-green-text)', fontWeight: 800, fontSize: '0.82rem', marginBottom: '4px' }}>
                  Step 3: Gross Buyout Sum
                </div>
                <div style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
                  {result.detailed_steps.step_3_gross_buyout?.calculation}
                </div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.9rem', color: 'var(--text-primary)', marginTop: '6px', fontWeight: 700 }}>
                  Gross: ₹{result.detailed_steps.step_3_gross_buyout?.gross_amount.toLocaleString()}
                </div>
              </div>

              <div style={{ background: 'var(--tradelearn-pink-light)', padding: '14px', borderRadius: '8px', border: '1px solid var(--tradelearn-pink-border)' }}>
                <div style={{ color: 'var(--tradelearn-pink-text)', fontWeight: 800, fontSize: '0.82rem', marginBottom: '4px' }}>
                  Step 4: Net Employee Liability
                </div>
                <div style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
                  {result.detailed_steps.step_4_net_payable?.calculation}
                </div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.9rem', color: 'var(--tradelearn-pink-text)', marginTop: '6px', fontWeight: 700 }}>
                  Payable: ₹{result.detailed_steps.step_4_net_payable?.net_employee_payable.toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Section 14: Affordability Simulation */}
        <AffordabilitySimulator initialSimulatedEmi={repayResult?.monthly_emi?.value || 20000} />
      </div>
    </div>
  );
}
