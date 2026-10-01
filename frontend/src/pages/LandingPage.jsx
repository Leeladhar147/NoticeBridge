import React, { useState } from 'react';
import {
  ArrowRight,
  ShieldCheck,
  Clock,
  Coins,
  Cpu,
  Layers,
  FileSpreadsheet,
  AlertTriangle,
  CheckCircle2,
  Play,
  Building2
} from 'lucide-react';
import NoticeBridgeLogo from '../components/NoticeBridgeLogo';

export default function LandingPage({ setActivePage, user }) {
  const [quickSalary, setQuickSalary] = useState(60000);
  const [quickShortfall, setQuickShortfall] = useState(60);
  const [quickDivisor, setQuickDivisor] = useState(30);

  const quickBuyout = (quickSalary / quickDivisor) * quickShortfall;
  const quickEMI = Math.round(quickBuyout / 6);

  const handleCTA = (page) => {
    setActivePage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleScrollToHowItWorks = () => {
    const el = document.getElementById('how-it-works');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div style={{ background: '#FFFFFF' }}>
      {/* HERO SECTION WITH PANORAMIC BRIDGE JOURNEY (Current Company -> Bridge -> New Opportunity) */}
      <section style={{
        position: 'relative',
        minHeight: '660px',
        padding: '50px 0 340px 0',
        backgroundImage: "url('/noticebridge_hero_bg.jpg')",
        backgroundRepeat: 'no-repeat',
        backgroundPosition: 'center bottom',
        backgroundSize: 'cover',
        borderBottom: '1px solid var(--border-subtle)',
        overflow: 'hidden'
      }}>
        {/* Soft top ambient fade for crystal-clear headline text in the sky */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '52%',
          background: 'linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.75) 45%, rgba(255,255,255,0) 100%)',
          zIndex: 1,
          pointerEvents: 'none'
        }} />

        {/* Floating Contextual Badges: Current Company (Left Building) and New Opportunity (Right Skyscraper) */}
        <div className="hero-pins-container" style={{ position: 'absolute', inset: 0, zIndex: 3, pointerEvents: 'none' }}>
          {/* Current Company Pin (Over Left Corporate Building) */}
          <div style={{
            position: 'absolute',
            left: '18%',
            bottom: '36%',
            background: '#FFFFFF',
            border: '1px solid rgba(226, 232, 240, 0.95)',
            borderRadius: '10px',
            padding: '7px 14px',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            boxShadow: '0 8px 24px rgba(15, 23, 42, 0.12)',
            pointerEvents: 'auto'
          }}>
            <div style={{ color: '#16A34A', display: 'flex' }}>
              <Building2 size={18} />
            </div>
            <div style={{ lineHeight: 1.15 }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#0F172A' }}>Current</div>
              <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#0F172A' }}>Company</div>
            </div>
            {/* Dotted anchor line pointing directly down to the corporate building */}
            <div style={{
              position: 'absolute',
              bottom: '-20px',
              left: '22px',
              height: '20px',
              borderLeft: '2.5px dotted #16A34A'
            }} />
          </div>

          {/* New Opportunity Pin (Over Right Glass Skyscrapers) */}
          <div style={{
            position: 'absolute',
            right: '12%',
            bottom: '46%',
            background: '#FFFFFF',
            border: '1px solid rgba(226, 232, 240, 0.95)',
            borderRadius: '10px',
            padding: '7px 14px',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            boxShadow: '0 8px 24px rgba(15, 23, 42, 0.12)',
            pointerEvents: 'auto'
          }}>
            <div style={{ color: '#16A34A', display: 'flex' }}>
              <Building2 size={18} />
            </div>
            <div style={{ lineHeight: 1.15 }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#0F172A' }}>New</div>
              <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#0F172A' }}>Opportunity</div>
            </div>
            {/* Dotted anchor line pointing down to the skyscraper */}
            <div style={{
              position: 'absolute',
              bottom: '-24px',
              left: '22px',
              height: '24px',
              borderLeft: '2.5px dotted #16A34A'
            }} />
          </div>
        </div>

        <div className="container" style={{ position: 'relative', zIndex: 2, textAlign: 'center' }}>
          <div style={{ maxWidth: '680px', margin: '0 auto' }}>
            {/* Small eyebrow */}
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              background: '#DCFCE7',
              border: '1px solid #BBF7D0',
              padding: '6px 14px',
              borderRadius: '20px',
              marginBottom: '16px'
            }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#15803D" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 19V9a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v10" />
                <path d="M4 19h16" />
                <path d="M9 19v-6a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v6" />
              </svg>
              <span style={{
                fontFamily: 'var(--font-heading)',
                fontSize: '0.76rem',
                fontWeight: 800,
                color: '#15803D',
                letterSpacing: '0.08em',
                textTransform: 'uppercase'
              }}>
                YOUR NEXT CHAPTER, MADE CLEAR
              </span>
            </div>

            {/* Main heading */}
            <h1 style={{
              fontSize: 'clamp(2.4rem, 4.4vw, 3.6rem)',
              lineHeight: 1.12,
              fontWeight: 900,
              marginBottom: '14px',
              color: '#0F172A',
              letterSpacing: '-0.03em'
            }}>
              Navigate Your <span style={{ color: '#16A34A' }}>Career Transition</span>
            </h1>

            {/* Supporting text */}
            <p style={{
              fontSize: '1.12rem',
              color: '#475569',
              lineHeight: 1.55,
              marginBottom: '24px',
              fontWeight: 500,
              maxWidth: '560px',
              margin: '0 auto 24px auto'
            }}>
              Understand your notice period, explore buyout options, and plan your transition with clarity.
            </p>

            {/* Primary & Secondary CTA Buttons */}
            <div style={{ display: 'flex', gap: '14px', justifyContent: 'center', flexWrap: 'wrap', alignItems: 'center' }}>
              <button
                onClick={() => handleCTA(user ? 'dashboard' : 'signup')}
                style={{
                  background: '#16A34A',
                  color: '#FFFFFF',
                  fontFamily: 'var(--font-heading)',
                  fontWeight: 700,
                  fontSize: '0.96rem',
                  padding: '12px 26px',
                  borderRadius: '8px',
                  border: '1px solid #15803D',
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  boxShadow: '0 4px 14px rgba(22, 163, 74, 0.3)',
                  transition: 'all 0.18s ease'
                }}
              >
                Get Started
                <ArrowRight size={17} />
              </button>

              <button
                onClick={handleScrollToHowItWorks}
                style={{
                  background: '#FFFFFF',
                  color: '#0F172A',
                  fontFamily: 'var(--font-heading)',
                  fontWeight: 700,
                  fontSize: '0.94rem',
                  padding: '11px 22px',
                  borderRadius: '8px',
                  border: '1px solid #CBD5E1',
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '10px',
                  boxShadow: '0 2px 8px rgba(15, 23, 42, 0.05)',
                  transition: 'all 0.18s ease'
                }}
              >
                <div style={{
                  width: '20px',
                  height: '20px',
                  borderRadius: '50%',
                  background: '#16A34A',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#FFFFFF'
                }}>
                  <Play size={10} fill="#FFFFFF" style={{ marginLeft: '1px' }} />
                </div>
                See How It Works
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* THE 3-WAY IMPASSE BREAKDOWN */}
      <section id="how-it-works" style={{ padding: '50px 0 60px 0', background: '#FFFFFF' }}>
        <div className="container">
          <div style={{
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '16px',
            padding: '36px'
          }}>
            <div style={{
              fontFamily: 'var(--font-heading)',
              fontSize: '0.82rem',
              color: 'var(--parrot-green)',
              fontWeight: 800,
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              marginBottom: '6px'
            }}>
              The 3-Way Impasse Breakdown
            </div>
            <h2 style={{ fontSize: '1.9rem', marginBottom: '28px', color: 'var(--text-primary)' }}>
              Why Indian & Global Tech Transitions Break Down
            </h2>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
              gap: '20px'
            }}>
              {/* Card 1: Company A */}
              <div className="sports-card">
                <div style={{
                  color: 'var(--text-muted)',
                  fontSize: '0.78rem',
                  fontWeight: 800,
                  textTransform: 'uppercase',
                  marginBottom: '8px'
                }}>
                  Current Employer (Company A)
                </div>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, marginBottom: '6px', color: 'var(--text-primary)' }}>
                  90-Day Lock-In
                </div>
                <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  Enforces strict contractual notice duration. Early release requires monetary buyout on Basic or Gross salary.
                </p>
              </div>

              {/* Card 2: Company B */}
              <div className="sports-card sports-card-glow-volt">
                <div style={{
                  color: 'var(--parrot-green)',
                  fontSize: '0.78rem',
                  fontWeight: 800,
                  textTransform: 'uppercase',
                  marginBottom: '8px'
                }}>
                  New Employer (Company B)
                </div>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, marginBottom: '6px', color: 'var(--text-primary)' }}>
                  30-Day Joining Deadline
                </div>
                <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  Critical onboarding timelines. Threatens to rescind the candidate's offer if unable to onboard within 30 days.
                </p>
              </div>

              {/* Card 3: The Liquidity Crunch - Tasteful TradeLearn Pink accent */}
              <div className="sports-card sports-card-glow-magenta" style={{ background: '#FFFDFD' }}>
                <div style={{
                  color: 'var(--tradelearn-pink)',
                  fontSize: '0.78rem',
                  fontWeight: 800,
                  textTransform: 'uppercase',
                  marginBottom: '8px'
                }}>
                  The Candidate's Liquidity Crunch
                </div>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, marginBottom: '6px', color: 'var(--tradelearn-pink)' }}>
                  ₹1,20,000 Upfront Need
                </div>
                <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  Candidate has a 60-day shortfall but lacks immediate liquidity to pay Company A's invoice in a lump sum.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* INTERACTIVE INSTANT SIMULATOR TEASER */}
      <section id="features" style={{ padding: '20px 0 60px 0', background: '#FFFFFF' }}>
        <div className="container">
          <div className="sports-card" style={{
            background: '#FFFFFF',
            border: '2px solid var(--parrot-green-border)',
            boxShadow: '0 4px 20px rgba(22, 163, 74, 0.08)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', marginBottom: '24px' }}>
              <div>
                <span className="sports-pill" style={{ background: 'var(--parrot-green-light)', color: 'var(--parrot-green-text)', border: '1px solid var(--parrot-green-border)', marginBottom: '8px' }}>
                  <span>LIVE DEMO ENGINE</span>
                </span>
                <h3 style={{ fontSize: '1.5rem', marginTop: '6px', color: 'var(--text-primary)' }}>
                  Buyout & Repayment Quick Simulator
                </h3>
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                DETERMINISTIC FORMULA ENGINE
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px', marginBottom: '28px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  Monthly Salary ({quickDivisor}-day basis)
                </label>
                <input
                  type="number"
                  className="form-input"
                  value={quickSalary}
                  onChange={(e) => setQuickSalary(Number(e.target.value))}
                  step="5000"
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  Shortfall Days to Buy Out
                </label>
                <input
                  type="number"
                  className="form-input"
                  value={quickShortfall}
                  onChange={(e) => setQuickShortfall(Number(e.target.value))}
                  min="1"
                  max="90"
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  Contractual Divisor Basis
                </label>
                <select
                  className="form-input"
                  value={quickDivisor}
                  onChange={(e) => setQuickDivisor(Number(e.target.value))}
                >
                  <option value="30">30-Day Monthly Standard</option>
                  <option value="26">26 Working Days Standard</option>
                  <option value="31">31 Calendar Days</option>
                </select>
              </div>
            </div>

            {/* Calculated Output Highlight */}
            <div style={{
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '10px',
              padding: '20px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '20px'
            }}>
              <div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontFamily: 'var(--font-mono)' }}>
                  Deterministic Formula Result
                </div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.15rem', color: 'var(--text-primary)', marginTop: '4px' }}>
                  (₹{quickSalary.toLocaleString()} / {quickDivisor}) × {quickShortfall} days = <strong style={{ color: 'var(--parrot-green)' }}>₹{quickBuyout.toLocaleString()}</strong>
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontFamily: 'var(--font-mono)' }}>
                  6-Month Simulated EMI
                </div>
                <div style={{ fontSize: '1.7rem', fontWeight: 900, color: 'var(--parrot-green)', fontFamily: 'var(--font-heading)' }}>
                  ₹{quickEMI.toLocaleString()}<span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>/mo</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CORE ARCHITECTURAL PILLARS */}
      <section id="about" style={{ padding: '30px 0 80px 0', background: 'var(--bg-secondary)', borderTop: '1px solid var(--border-subtle)' }}>
        <div className="container">
          <div style={{ textAlign: 'center', maxWidth: '640px', margin: '0 auto 40px auto' }}>
            <h2 style={{ fontSize: '1.9rem', marginBottom: '10px', color: 'var(--text-primary)' }}>
              Deterministic Engineering Foundation
            </h2>
            <p style={{ color: 'var(--text-secondary)' }}>
              Built strictly on deterministic mathematical Python engines. Zero LLM hallucinations for money, dates, or formulas.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
            <div className="sports-card">
              <div style={{ color: 'var(--parrot-green)', marginBottom: '14px' }}>
                <Cpu size={26} />
              </div>
              <h3 style={{ fontSize: '1.15rem', marginBottom: '8px', color: 'var(--text-primary)' }}>
                Pure Python Math Engine
              </h3>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                Every buyout sum, daily rate, and amortized repayment installment is computed via deterministic, unit-tested Python functions.
              </p>
            </div>

            <div className="sports-card">
              <div style={{ color: '#0284C7', marginBottom: '14px' }}>
                <FileSpreadsheet size={26} />
              </div>
              <h3 style={{ fontSize: '1.15rem', marginBottom: '8px', color: 'var(--text-primary)' }}>
                Configurable Contract Divisors
              </h3>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                Accommodates basic vs gross salary, 30-day, 26-day working, or custom contract clauses. Never makes unsupported assumptions.
              </p>
            </div>

            <div className="sports-card">
              <div style={{ color: 'var(--tradelearn-pink)', marginBottom: '14px' }}>
                <Layers size={26} />
              </div>
              <h3 style={{ fontSize: '1.15rem', marginBottom: '8px', color: 'var(--text-primary)' }}>
                Multi-Scenario Simulation
              </h3>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                Side-by-side evaluation of 6 distinct transition scenarios: full notice, buyout, employer contribution, and extended tenors.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
