import React, { useState, useEffect } from 'react';
import {
  Clock,
  Calendar,
  DollarSign,
  ArrowRight,
  Shield,
  Layers,
  RefreshCw,
  Building2,
  Briefcase,
  BookOpen,
  FileCheck,
  CheckCircle2
} from 'lucide-react';
import { api } from '../api/client';
import OriginBadge from '../components/OriginBadge';
import AffordabilitySimulator from '../components/AffordabilitySimulator';

export default function DashboardPage({ setActivePage, user }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [seedingDemo, setSeedingDemo] = useState(false);

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const summary = await api.getDashboardSummary();
      setData(summary);
    } catch (err) {
      console.warn('Dashboard fetch error:', err.message);
      setError(err.message || 'Failed to load dashboard metrics.');
    } finally {
      setLoading(false);
    }
  };

  const handleSeedDemo = async () => {
    setSeedingDemo(true);
    try {
      await api.seedDemo();
      await fetchDashboard();
    } catch (err) {
      alert('Could not seed demonstration scenario: ' + err.message);
    } finally {
      setSeedingDemo(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const handleNav = (page) => {
    setActivePage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (loading) {
    return (
      <div className="container" style={{ padding: '80px 24px', textAlign: 'center' }}>
        <RefreshCw size={36} color="var(--parrot-green)" style={{ animation: 'spin 1s linear infinite' }} />
        <div style={{ marginTop: '16px', color: 'var(--text-muted)' }}>Loading Deterministic Engine Metrics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container" style={{ padding: '80px 24px', textAlign: 'center' }}>
        <div style={{ color: 'var(--tradelearn-pink-text)', marginBottom: '16px', fontSize: '1.1rem', fontWeight: 600 }}>
          {error}
        </div>
        <button onClick={fetchDashboard} className="btn-volt">
          Retry
        </button>
      </div>
    );
  }

  const d = data;
  if (!d) return null;

  const totalNotice = d.contractual_notice_period_days?.value || 0;
  const served = d.days_served?.value || 0;
  const remaining = d.days_remaining?.value || 0;
  const servedPct = totalNotice > 0 ? Math.min(100, Math.round((served / totalNotice) * 100)) : 0;
  const hasFullData = d.current_company && d.target_company && totalNotice > 0;

  return (
    <div style={{ background: '#FFFFFF', minHeight: '100%' }}>
      <div className="container" style={{ padding: '36px 24px 60px 24px' }}>
        {/* Onboarding Banner if profile setup is pending */}
        {!hasFullData && (
          <div style={{
            background: 'var(--parrot-green-light)',
            border: '1px solid var(--parrot-green-border)',
            borderRadius: '12px',
            padding: '20px 24px',
            marginBottom: '28px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '16px'
          }}>
            <div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>
                Welcome to NoticeBridge{user?.full_name ? `, ${user.full_name}` : ''}!
              </div>
              <p style={{ margin: 0, fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                Set up your current employment and target offer to run deterministic transition calculations and financing models.
              </p>
            </div>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              <button
                onClick={() => handleNav('current-job')}
                className="btn-volt"
                style={{ padding: '9px 18px', fontSize: '0.84rem' }}
              >
                1. Add Current Job
              </button>
              <button
                onClick={() => handleNav('new-offer')}
                className="btn-outline"
                style={{ padding: '9px 18px', fontSize: '0.84rem' }}
              >
                2. Add New Offer
              </button>
              <button
                onClick={handleSeedDemo}
                disabled={seedingDemo}
                className="btn-outline"
                style={{ padding: '9px 18px', fontSize: '0.84rem', borderColor: 'var(--parrot-green)' }}
              >
                {seedingDemo ? 'Loading Demo...' : 'Load Sample Demo Data'}
              </button>
            </div>
          </div>
        )}

        {/* Top Banner / Status Overview */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '20px',
          marginBottom: '28px',
          paddingBottom: '20px',
          borderBottom: '1px solid var(--border-subtle)'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span className="sports-pill" style={{
                background: 'var(--parrot-green-light)',
                color: 'var(--parrot-green-text)',
                border: '1px solid var(--parrot-green-border)'
              }}>
                <span>{d.transition_status?.value || 'Setup Pending'}</span>
              </span>
              {d.transition_status && (
                <OriginBadge origin={d.transition_status.origin} source={d.transition_status.source_reference} />
              )}
            </div>
            <h1 style={{ fontSize: '2.1rem', marginBottom: '2px', color: 'var(--text-primary)' }}>
              Transition Mission Control
            </h1>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <Building2 size={15} color="var(--text-secondary)" /> {d.current_company || 'Current Company Pending'}
              </span>
              <span>➔</span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '5px', color: 'var(--parrot-green-text)', fontWeight: 600 }}>
                <Briefcase size={15} color="var(--parrot-green)" /> {d.target_company || 'Target Offer Pending'}
              </span>
            </div>
          </div>

          {/* Readiness Meter */}
          <div style={{
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '10px',
            padding: '14px 22px',
            display: 'flex',
            alignItems: 'center',
            gap: '16px'
          }}>
            <div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontFamily: 'var(--font-mono)' }}>
                Readiness Score
              </div>
              <div style={{ fontSize: '1.75rem', fontWeight: 900, color: 'var(--parrot-green)', fontFamily: 'var(--font-heading)' }}>
                {d.readiness_score}%
              </div>
            </div>
            <button
              onClick={() => handleNav('scenarios')}
              className="btn-volt"
              style={{ padding: '8px 16px', fontSize: '0.82rem' }}
            >
              Optimize Plan
            </button>
          </div>
        </div>

        {/* SECTION 8 KPI METRIC GRID */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '18px',
          marginBottom: '28px'
        }}>
          {/* Metric 1: Current Notice Period */}
          <div className="sports-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                Current Notice Period
              </span>
              <OriginBadge origin={d.contractual_notice_period_days.origin} source={d.contractual_notice_period_days.source_reference} compact />
            </div>
            <div className="metric-number" style={{ fontSize: '2.3rem', color: 'var(--text-primary)', marginBottom: '6px' }}>
              {d.contractual_notice_period_days.value} <span style={{ fontSize: '0.95rem', color: 'var(--text-muted)', fontWeight: 600 }}>Days</span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Mandatory notice term per employment contract
            </div>
          </div>

          {/* Metric 2: Days Served vs Remaining */}
          <div className="sports-card sports-card-glow-volt">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                Days Served / Remaining
              </span>
              <OriginBadge origin={d.days_remaining.origin} source={d.days_remaining.source_reference} compact />
            </div>
            <div className="metric-number" style={{ fontSize: '2.3rem', color: 'var(--parrot-green)', marginBottom: '8px' }}>
              {d.days_served.value} <span style={{ fontSize: '1.1rem', color: 'var(--text-muted)', fontWeight: 600 }}>/ {d.days_remaining.value} left</span>
            </div>
            {/* Progress bar */}
            <div style={{ width: '100%', height: '7px', background: '#E2E8F0', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{
                width: `${servedPct}%`,
                height: '100%',
                background: 'var(--parrot-green)',
                borderRadius: '4px'
              }} />
            </div>
          </div>

          {/* Metric 3: New Employer Joining Deadline */}
          <div className="sports-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                New Joining Deadline
              </span>
              <OriginBadge origin={d.new_employer_joining_deadline.origin} source={d.new_employer_joining_deadline.source_reference} compact />
            </div>
            <div className="metric-number" style={{ fontSize: '2.3rem', color: 'var(--text-primary)', marginBottom: '6px' }}>
              {d.days_until_joining_deadline.value} <span style={{ fontSize: '0.95rem', color: 'var(--text-muted)', fontWeight: 600 }}>Days Away</span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Target: {d.new_employer_joining_deadline.value}
            </div>
          </div>

          {/* Metric 4: Estimated Buyout & Shortfall (TradeLearn Pink accent on liquidity wall) */}
          <div className="sports-card sports-card-glow-magenta" style={{ background: '#FFFDFD' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--tradelearn-pink)', textTransform: 'uppercase', fontWeight: 700 }}>
                Estimated Buyout
              </span>
              <OriginBadge origin={d.estimated_buyout_gross.origin} source={d.estimated_buyout_gross.source_reference} compact />
            </div>
            <div className="metric-number" style={{ fontSize: '2.3rem', color: 'var(--tradelearn-pink)', marginBottom: '6px' }}>
              ₹{d.estimated_buyout_gross.value.toLocaleString()}
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Less ₹{d.employer_contribution_available.value.toLocaleString()} co-pay = <strong>₹{d.financing_amount_needed.value.toLocaleString()}</strong> net
            </div>
          </div>
        </div>

        {/* SECONDARY ROW: FINANCING & REPAYMENT ESTIMATE */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px', marginBottom: '28px' }}>
          {/* Repayment Card */}
          <div className="sports-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <h3 style={{ fontSize: '1.15rem', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-primary)' }}>
                <DollarSign size={18} color="var(--parrot-green)" />
                Repayment & Liquidity Bridge
              </h3>
              <OriginBadge origin={d.repayment_estimate_monthly.origin} source={d.repayment_estimate_monthly.source_reference} />
            </div>

            <div style={{
              background: 'var(--bg-secondary)',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '16px',
              border: '1px solid var(--border-subtle)'
            }}>
              <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                Monthly Repayment Estimate ({d.repayment_tenor_months.value} Months)
              </div>
              <div style={{ fontSize: '2.1rem', fontWeight: 900, color: 'var(--parrot-green)', fontFamily: 'var(--font-heading)', marginTop: '2px' }}>
                ₹{d.repayment_estimate_monthly.value.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 500 }}>/month</span>
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Principal: ₹{d.financing_amount_needed.value.toLocaleString()} • Simulated @ 10% APR
              </div>
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                onClick={() => handleNav('buyout-calc')}
                className="btn-cyan"
                style={{ flex: 1, padding: '9px', fontSize: '0.84rem' }}
              >
                Examine Buyout Math
              </button>
              <button
                onClick={() => handleNav('results')}
                className="btn-outline"
                style={{ padding: '9px 14px', fontSize: '0.84rem' }}
              >
                Full Amortization
              </button>
            </div>
          </div>

          {/* Transition Timeline Milestones */}
          <div className="sports-card">
            <h3 style={{ fontSize: '1.15rem', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-primary)' }}>
              <Clock size={18} color="var(--parrot-green)" />
              Milestone Synchronization
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {d.timeline_milestones.map((m, idx) => (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '9px 12px',
                    background: m.status === 'target' ? 'var(--parrot-green-light)' : 'var(--bg-secondary)',
                    border: m.status === 'target' ? '1px solid var(--parrot-green-border)' : '1px solid var(--border-subtle)',
                    borderRadius: '8px'
                  }}
                >
                  <div>
                    <div style={{ fontSize: '0.86rem', fontWeight: 700, color: m.status === 'target' ? 'var(--parrot-green-text)' : 'var(--text-primary)' }}>
                      {m.label}
                    </div>
                    <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>{m.description}</div>
                  </div>
                  <div style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.82rem',
                    color: m.status === 'target' ? 'var(--parrot-green-text)' : 'var(--text-secondary)',
                    fontWeight: 700
                  }}>
                    {m.target_date}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* SCENARIOS PREVIEW */}
        <div className="sports-card" style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h3 style={{ fontSize: '1.25rem', color: 'var(--text-primary)' }}>Transition Scenarios Matrix</h3>
              <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)' }}>
                Deterministic simulation comparing costs, joining deadlines, and monthly burden
              </p>
            </div>
            <button
              onClick={() => handleNav('scenarios')}
              className="btn-volt"
              style={{ padding: '8px 16px', fontSize: '0.82rem' }}
            >
              Explore 6 Scenarios <ArrowRight size={14} />
            </button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: '14px' }}>
            {d.scenario_snapshot.map((s) => (
              <div
                key={s.id}
                style={{
                  background: '#FFFFFF',
                  border: s.is_recommended ? '1.5px solid var(--parrot-green)' : '1px solid var(--border-subtle)',
                  borderRadius: '10px',
                  padding: '16px',
                  position: 'relative',
                  boxShadow: s.is_recommended ? '0 4px 14px rgba(22, 163, 74, 0.1)' : 'var(--card-shadow)'
                }}
              >
                {s.is_recommended && (
                  <div style={{
                    position: 'absolute',
                    top: '-9px',
                    right: '10px',
                    background: 'var(--parrot-green)',
                    color: '#FFFFFF',
                    fontSize: '0.66rem',
                    fontWeight: 900,
                    fontFamily: 'var(--font-heading)',
                    padding: '2px 7px',
                    borderRadius: '4px',
                    textTransform: 'uppercase'
                  }}>
                    RECOMMENDED
                  </div>
                )}
                <div style={{ fontSize: '0.96rem', fontWeight: 800, marginBottom: '2px', color: 'var(--text-primary)' }}>{s.title}</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '12px' }}>{s.tagline}</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.84rem', paddingTop: '8px', borderTop: '1px solid var(--border-subtle)' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Net Out-of-Pocket:</span>
                  <span style={{ fontWeight: 700, color: s.net_cost === 0 ? 'var(--parrot-green)' : 'var(--text-primary)' }}>
                    ₹{s.net_cost.toLocaleString()}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.84rem', marginTop: '4px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Joining Date:</span>
                  <span style={{ fontWeight: 600, fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>{s.joining_date}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* SECTION 16: CONTRACT-DERIVED EVIDENCE GROUNDING */}
        <div className="sports-card" style={{ marginTop: '24px', background: '#FFFFFF' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <div style={{
              background: 'var(--parrot-green-light)',
              color: 'var(--parrot-green)',
              padding: '8px',
              borderRadius: '8px',
              display: 'flex'
            }}>
              <BookOpen size={20} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.15rem', color: 'var(--text-primary)', margin: 0 }}>
                Contract-Derived Evidence & Provenance
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
                Traceable source audit for every contractual parameter powering the calculation engine
              </p>
            </div>
          </div>

          <div style={{ border: '1px solid #E2E8F0', borderRadius: '10px', overflow: 'hidden' }}>
            <div style={{
              display: 'grid',
              gridTemplateColumns: '200px 1fr 140px',
              padding: '10px 16px',
              background: '#F8FAFC',
              borderBottom: '1px solid #E2E8F0',
              fontWeight: 700,
              fontSize: '0.76rem',
              color: '#64748B',
              textTransform: 'uppercase'
            }}>
              <div>Parameter</div>
              <div>Source Grounding / Evidence Citation</div>
              <div style={{ textAlign: 'right' }}>Provenance</div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '200px 1fr 140px', padding: '12px 16px', borderBottom: '1px solid #F1F5F9', alignItems: 'center', fontSize: '0.84rem' }}>
              <div style={{ fontWeight: 600, color: '#0F172A' }}>Notice Period</div>
              <div style={{ color: '#334155' }}>
                90 Days • <span style={{ color: '#64748B', fontStyle: 'italic' }}>Employment Agreement, Section 2: "ninety (90) days notice in writing"</span>
              </div>
              <div style={{ textAlign: 'right' }}>
                <OriginBadge origin="contract-derived" source="Employment Agreement" compact />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '200px 1fr 140px', padding: '12px 16px', borderBottom: '1px solid #F1F5F9', alignItems: 'center', fontSize: '0.84rem' }}>
              <div style={{ fontWeight: 600, color: '#0F172A' }}>Notice Buyout Permitted</div>
              <div style={{ color: '#334155' }}>
                Permitted • <span style={{ color: '#64748B', fontStyle: 'italic' }}>Clause 3: "permit a notice buyout or early release subject to recovery of salary"</span>
              </div>
              <div style={{ textAlign: 'right' }}>
                <OriginBadge origin="contract-derived" source="Employment Agreement" compact />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '200px 1fr 140px', padding: '12px 16px', borderBottom: '1px solid #F1F5F9', alignItems: 'center', fontSize: '0.84rem' }}>
              <div style={{ fontWeight: 600, color: '#0F172A' }}>Buyout Salary Basis</div>
              <div style={{ color: '#334155' }}>
                Basic Monthly Salary • <span style={{ color: '#64748B', fontStyle: 'italic' }}>Clause 3.2: "calculated on the basis of Monthly Basic Salary divided by 30 days"</span>
              </div>
              <div style={{ textAlign: 'right' }}>
                <OriginBadge origin="contract-derived" source="Employment Agreement" compact />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '200px 1fr 140px', padding: '12px 16px', alignItems: 'center', fontSize: '0.84rem' }}>
              <div style={{ fontWeight: 600, color: '#0F172A' }}>Employer Co-Sponsorship</div>
              <div style={{ color: '#334155' }}>
                ₹30,000 • <span style={{ color: '#64748B', fontStyle: 'italic' }}>Offer Letter, Transition Support Schedule: "buyout assistance of Rs. 30,000"</span>
              </div>
              <div style={{ textAlign: 'right' }}>
                <OriginBadge origin="user-provided" source="Offer Letter" compact />
              </div>
            </div>
          </div>
        </div>

        {/* SECTION 14: AFFORDABILITY SIMULATION */}
        <AffordabilitySimulator initialSimulatedEmi={d.repayment_estimate_monthly.value} />
      </div>
    </div>
  );
}
