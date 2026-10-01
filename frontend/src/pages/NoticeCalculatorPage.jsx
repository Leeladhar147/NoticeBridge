import React, { useState, useEffect } from 'react';
import { Clock, Calendar, ArrowRight, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { api } from '../api/client';
import OriginBadge from '../components/OriginBadge';

export default function NoticeCalculatorPage({ setActivePage }) {
  const [params, setParams] = useState({
    contractual_notice_period: 90,
    resignation_date: '2026-08-31',
    intended_joining_date: '2026-10-30',
    days_already_served: 30,
    leave_adjustment_days: 0
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runCalculation = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.calculateNotice(params);
      setResult(res);
    } catch (err) {
      setError(err.message || 'Notice calculation failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runCalculation();
  }, [params]);

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
            <Clock size={24} />
          </div>
          <div>
            <h1 style={{ fontSize: '1.9rem', color: 'var(--text-primary)' }}>Notice Period Calculator</h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
              Deterministic calendar engine: served notice, remaining tenure, earliest release, and joining shortfall
            </p>
          </div>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '24px',
          marginTop: '20px'
        }}>
          {/* Form Controls Card */}
          <div className="sports-card" style={{ background: '#FFFFFF' }}>
            <h3 style={{ fontSize: '1.15rem', marginBottom: '16px', color: 'var(--text-primary)', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
              Calculation Inputs
            </h3>

            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                  Contractual Notice (Days)
                </label>
                <OriginBadge origin="contract-derived" source="Contract" compact />
              </div>
              <input
                type="number"
                min="1"
                max="365"
                className="form-input"
                value={params.contractual_notice_period}
                onChange={(e) => setParams({ ...params, contractual_notice_period: Number(e.target.value) })}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
                  Resignation Date
                </label>
                <input
                  type="date"
                  className="form-input"
                  value={params.resignation_date}
                  onChange={(e) => setParams({ ...params, resignation_date: e.target.value })}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
                  Intended Joining Date
                </label>
                <input
                  type="date"
                  className="form-input"
                  value={params.intended_joining_date}
                  onChange={(e) => setParams({ ...params, intended_joining_date: e.target.value })}
                />
              </div>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                  Days Already Served: <strong>{params.days_already_served} Days</strong>
                </label>
                <OriginBadge origin="user-provided" source="Tracker" compact />
              </div>
              <input
                type="range"
                min="0"
                max={params.contractual_notice_period}
                value={params.days_already_served}
                onChange={(e) => setParams({ ...params, days_already_served: Number(e.target.value) })}
                style={{ width: '100%', accentColor: 'var(--parrot-green)' }}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                  Leave Adjustment Days (Off-set against notice)
                </label>
                <OriginBadge origin="user-provided" source="Leave Balance" compact />
              </div>
              <input
                type="number"
                min="0"
                max={params.contractual_notice_period - params.days_already_served}
                className="form-input"
                value={params.leave_adjustment_days}
                onChange={(e) => setParams({ ...params, leave_adjustment_days: Number(e.target.value) })}
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

          {/* Engine Output Display Card */}
          {result && (
            <div className="sports-card sports-card-glow-volt" style={{ background: '#FFFFFF' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3 style={{ fontSize: '1.15rem', color: 'var(--text-primary)' }}>Deterministic Calculation Results</h3>
                <OriginBadge origin="calculated" source="NoticePeriodCalculator" />
              </div>

              {/* Status Summary Banner */}
              <div style={{
                background: result.is_transition_feasible_without_buyout.value ? 'var(--parrot-green-light)' : 'var(--tradelearn-pink-light)',
                border: result.is_transition_feasible_without_buyout.value ? '1px solid var(--parrot-green-border)' : '1px solid var(--tradelearn-pink-border)',
                borderRadius: '8px',
                padding: '12px 16px',
                marginBottom: '18px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px'
              }}>
                {result.is_transition_feasible_without_buyout.value ? (
                  <CheckCircle2 size={18} color="var(--parrot-green)" />
                ) : (
                  <AlertTriangle size={18} color="var(--tradelearn-pink)" />
                )}
                <div style={{
                  fontSize: '0.86rem',
                  color: result.is_transition_feasible_without_buyout.value ? 'var(--parrot-green-text)' : 'var(--tradelearn-pink-text)',
                  fontWeight: 600
                }}>
                  {result.status_summary}
                </div>
              </div>

              {/* Core Outputs Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '18px' }}>
                <div style={{ background: 'var(--bg-secondary)', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Remaining Notice</div>
                  <div style={{ fontSize: '1.7rem', fontWeight: 900, color: 'var(--text-primary)', fontFamily: 'var(--font-heading)' }}>
                    {result.remaining_notice_days.value} <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>Days</span>
                  </div>
                </div>

                <div style={{ background: 'var(--bg-secondary)', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Notice Shortfall</div>
                  <div style={{
                    fontSize: '1.7rem',
                    fontWeight: 900,
                    color: result.shortfall_days.value > 0 ? 'var(--tradelearn-pink)' : 'var(--parrot-green)',
                    fontFamily: 'var(--font-heading)'
                  }}>
                    {result.shortfall_days.value} <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>Days</span>
                  </div>
                </div>

                <div style={{ background: 'var(--bg-secondary)', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Earliest Standard Release</div>
                  <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
                    {result.earliest_release_date.value}
                  </div>
                </div>

                <div style={{ background: 'var(--bg-secondary)', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Required Joining Date</div>
                  <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--parrot-green)', fontFamily: 'var(--font-mono)' }}>
                    {result.intended_joining_date.value}
                  </div>
                </div>
              </div>

              {/* Formula Explanation Log */}
              <div style={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '8px',
                padding: '14px',
                marginBottom: '18px',
                fontSize: '0.8rem',
                fontFamily: 'var(--font-mono)',
                color: 'var(--text-secondary)'
              }}>
                <div style={{ color: 'var(--text-primary)', fontWeight: 700, marginBottom: '4px' }}>Deterministic Formula Audit:</div>
                <div>• {result.explanation.formula_served}</div>
                <div>• {result.explanation.formula_remaining}</div>
                <div>• {result.explanation.formula_release}</div>
                <div style={{ color: result.shortfall_days.value > 0 ? 'var(--tradelearn-pink)' : 'var(--parrot-green)' }}>
                  • {result.explanation.formula_shortfall}
                </div>
              </div>

              <button
                onClick={() => handleCTA('buyout-calc')}
                className="btn-volt"
                style={{ width: '100%', padding: '11px' }}
              >
                Feed {result.shortfall_days.value} Days Shortfall to Buyout Engine <ArrowRight size={16} />
              </button>
            </div>
          )}
        </div>

        {/* Timeline Milestones Visualization */}
        {result && result.timeline && (
          <div className="sports-card" style={{ marginTop: '28px', background: '#FFFFFF' }}>
            <h3 style={{ fontSize: '1.15rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-primary)' }}>
              <Calendar size={18} color="var(--parrot-green)" />
              Milestone Chronology
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px' }}>
              {result.timeline.map((m, idx) => (
                <div
                  key={idx}
                  style={{
                    background: m.status === 'target' ? 'var(--parrot-green-light)' : 'var(--bg-secondary)',
                    border: m.status === 'target' ? '1px solid var(--parrot-green-border)' : '1px solid var(--border-subtle)',
                    borderRadius: '8px',
                    padding: '12px 14px'
                  }}
                >
                  <div style={{
                    fontSize: '0.74rem',
                    fontFamily: 'var(--font-mono)',
                    color: m.status === 'target' ? 'var(--parrot-green-text)' : 'var(--text-muted)',
                    fontWeight: 700,
                    marginBottom: '3px'
                  }}>
                    {m.target_date}
                  </div>
                  <div style={{ fontSize: '0.88rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '3px' }}>
                    {m.label}
                  </div>
                  <div style={{ fontSize: '0.76rem', color: 'var(--text-secondary)' }}>
                    {m.description}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
