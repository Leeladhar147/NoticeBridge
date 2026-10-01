import React, { useState, useEffect } from 'react';
import { Layers, ArrowRight, CheckCircle2, XCircle, AlertCircle, RefreshCw, Zap } from 'lucide-react';
import { api } from '../api/client';
import OriginBadge from '../components/OriginBadge';

export default function ScenarioSimulatorPage({ setActivePage }) {
  const [params, setParams] = useState({
    contractual_notice_period: 90,
    resignation_date: '2026-08-31',
    intended_joining_date: '2026-10-30',
    days_already_served: 30,
    leave_adjustment_days: 0,
    monthly_salary: 60000,
    gross_monthly_salary: 95000,
    salary_basis: 'basic',
    divisor_basis: '30_days',
    employer_offered_contribution: 30000,
    preferred_tenor_months: 6,
    annual_interest_rate_percent: 10.0
  });

  const [matrix, setMatrix] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runSimulation = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.simulateScenarios(params);
      setMatrix(res);
    } catch (err) {
      setError(err.message || 'Scenario simulation failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runSimulation();
  }, [params]);

  const handleCTA = (page) => {
    setActivePage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div style={{ background: '#FFFFFF', minHeight: '100%' }}>
      <div className="container" style={{ padding: '36px 24px 60px 24px', maxWidth: '1240px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <div style={{
            background: 'var(--parrot-green-light)',
            padding: '8px',
            borderRadius: '8px',
            color: 'var(--parrot-green)'
          }}>
            <Layers size={24} />
          </div>
          <div>
            <h1 style={{ fontSize: '1.9rem', color: 'var(--text-primary)' }}>Transition Scenarios Matrix</h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
              Deterministic simulation comparing 6 real-world transition, buyout, and financing strategies
            </p>
          </div>
        </div>

        {/* Interactive Parameters Bar */}
        <div className="sports-card" style={{ background: 'var(--bg-secondary)', margin: '20px 0 28px 0', padding: '18px 22px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-secondary)' }}>
              Simulation Adjusters
            </span>
            <OriginBadge origin="user-provided" source="Scenario Engine Controls" />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '4px' }}>
                Monthly Basic (₹)
              </label>
              <input
                type="number"
                className="form-input"
                value={params.monthly_salary}
                onChange={(e) => setParams({ ...params, monthly_salary: Number(e.target.value) })}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '4px' }}>
                Employer Co-Pay (₹)
              </label>
              <input
                type="number"
                className="form-input"
                value={params.employer_offered_contribution}
                onChange={(e) => setParams({ ...params, employer_offered_contribution: Number(e.target.value) })}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '4px' }}>
                Financing Tenor
              </label>
              <select
                className="form-input"
                value={params.preferred_tenor_months}
                onChange={(e) => setParams({ ...params, preferred_tenor_months: Number(e.target.value) })}
              >
                <option value="3">3 Months</option>
                <option value="6">6 Months</option>
                <option value="9">9 Months</option>
                <option value="12">12 Months</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '4px' }}>
                Simulated APR (%)
              </label>
              <input
                type="number"
                className="form-input"
                value={params.annual_interest_rate_percent}
                onChange={(e) => setParams({ ...params, annual_interest_rate_percent: Number(e.target.value) })}
              />
            </div>
          </div>
        </div>

        {error && (
          <div style={{
            background: 'var(--tradelearn-pink-light)',
            border: '1px solid var(--tradelearn-pink-border)',
            color: 'var(--tradelearn-pink-text)',
            padding: '12px 16px',
            borderRadius: '8px',
            marginBottom: '20px'
          }}>
            {error}
          </div>
        )}

        {/* Summary Recommendation Banner */}
        {matrix && (
          <div style={{
            background: 'var(--parrot-green-light)',
            border: '1.5px solid var(--parrot-green-border)',
            borderRadius: '12px',
            padding: '18px 22px',
            marginBottom: '28px',
            display: 'flex',
            alignItems: 'center',
            gap: '14px'
          }}>
            <div style={{
              background: 'var(--parrot-green)',
              color: '#FFFFFF',
              borderRadius: '50%',
              padding: '8px',
              flexShrink: 0
            }}>
              <Zap size={20} />
            </div>
            <div>
              <div style={{ fontSize: '0.76rem', color: 'var(--parrot-green-text)', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Algorithmic Transition Recommendation
              </div>
              <div style={{ fontSize: '1.02rem', color: 'var(--text-primary)', fontWeight: 700, marginTop: '2px' }}>
                {matrix.summary_recommendation}
              </div>
            </div>
          </div>
        )}

        {/* SCENARIOS 6-WAY GRID */}
        {matrix && matrix.scenarios && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
            gap: '20px'
          }}>
            {matrix.scenarios.map((sc, idx) => {
              const isRec = sc.is_recommended;
              return (
                <div
                  key={sc.id}
                  className="sports-card"
                  style={{
                    background: '#FFFFFF',
                    border: isRec ? '2px solid var(--parrot-green)' : '1px solid var(--border-subtle)',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    boxShadow: isRec ? '0 4px 18px rgba(22, 163, 74, 0.12)' : 'var(--card-shadow)'
                  }}
                >
                  <div>
                    {/* Top Badges */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                      <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                        STRATEGY #{idx + 1}
                      </span>
                      <div style={{ display: 'flex', gap: '6px' }}>
                        {sc.is_recommended && (
                          <span className="sports-pill" style={{ background: 'var(--parrot-green)', color: '#FFFFFF' }}>
                            <span>RECOMMENDED</span>
                          </span>
                        )}
                        {sc.is_fastest_transition && (
                          <span className="sports-pill" style={{ background: '#E0F2FE', color: '#0369A1' }}>
                            <span>ON SCHEDULE</span>
                          </span>
                        )}
                        {sc.is_financially_lightest && (
                          <span className="sports-pill" style={{ background: '#F3E8FF', color: '#6B21A8' }}>
                            <span>ZERO EXPENSE</span>
                          </span>
                        )}
                      </div>
                    </div>

                    <h3 style={{ fontSize: '1.25rem', marginBottom: '3px', color: 'var(--text-primary)' }}>{sc.title}</h3>
                    <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', marginBottom: '14px' }}>
                      {sc.tagline}
                    </p>

                    {/* Financial & Timeline Metrics Table */}
                    <div style={{
                      background: 'var(--bg-secondary)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: '8px',
                      padding: '12px 14px',
                      marginBottom: '14px',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '7px',
                      fontSize: '0.85rem'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: 'var(--text-muted)' }}>Joining Date:</span>
                        <span style={{ fontWeight: 700, fontFamily: 'var(--font-mono)', color: sc.delay_in_joining_days > 0 ? 'var(--tradelearn-pink)' : 'var(--text-primary)' }}>
                          {sc.joining_date} ({sc.delay_in_joining_days}d delay)
                        </span>
                      </div>

                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: 'var(--text-muted)' }}>Gross Buyout Invoice:</span>
                        <span style={{ fontWeight: 600 }}>₹{sc.gross_buyout_cost.toLocaleString()}</span>
                      </div>

                      {sc.employer_contribution > 0 && (
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span style={{ color: 'var(--text-muted)' }}>Employer Co-Pay:</span>
                          <span style={{ fontWeight: 700, color: 'var(--parrot-green)' }}>
                            - ₹{sc.employer_contribution.toLocaleString()}
                          </span>
                        </div>
                      )}

                      <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: '4px', borderTop: '1px solid var(--border-subtle)' }}>
                        <span style={{ color: 'var(--text-primary)', fontWeight: 700 }}>Net Employee Payable:</span>
                        <span style={{ fontWeight: 900, color: sc.net_employee_liability === 0 ? 'var(--parrot-green)' : 'var(--tradelearn-pink)', fontSize: '0.95rem' }}>
                          ₹{sc.net_employee_liability.toLocaleString()}
                        </span>
                      </div>

                      {sc.monthly_repayment_estimate > 0 && (
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span style={{ color: 'var(--text-muted)' }}>Simulated Monthly EMI:</span>
                          <span style={{ fontWeight: 700, color: 'var(--parrot-green)' }}>
                            ₹{sc.monthly_repayment_estimate.toLocaleString()}/mo ({sc.repayment_tenor_months}m)
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Pros & Cons */}
                    <div style={{ marginBottom: '14px' }}>
                      <div style={{ fontSize: '0.76rem', color: 'var(--parrot-green-text)', fontWeight: 800, textTransform: 'uppercase', marginBottom: '5px' }}>
                        Advantages:
                      </div>
                      {sc.pros.map((p, pIdx) => (
                        <div key={pIdx} style={{ display: 'flex', alignItems: 'flex-start', gap: '7px', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '3px' }}>
                          <CheckCircle2 size={13} color="var(--parrot-green)" style={{ flexShrink: 0, marginTop: '2px' }} />
                          <span>{p}</span>
                        </div>
                      ))}

                      <div style={{ fontSize: '0.76rem', color: 'var(--tradelearn-pink-text)', fontWeight: 800, textTransform: 'uppercase', margin: '8px 0 5px 0' }}>
                        Trade-Offs & Risks:
                      </div>
                      {sc.cons.map((c, cIdx) => (
                        <div key={cIdx} style={{ display: 'flex', alignItems: 'flex-start', gap: '7px', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '3px' }}>
                          <XCircle size={13} color="var(--tradelearn-pink)" style={{ flexShrink: 0, marginTop: '2px' }} />
                          <span>{c}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <button
                    onClick={() => handleCTA('results')}
                    className={isRec ? 'btn-volt' : 'btn-outline'}
                    style={{ width: '100%', padding: '9px', fontSize: '0.85rem' }}
                  >
                    Generate Plan for Strategy #{idx + 1} <ArrowRight size={14} />
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
