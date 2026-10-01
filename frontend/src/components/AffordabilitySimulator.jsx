import React, { useState, useEffect } from 'react';
import { Calculator, Wallet, CheckCircle2, Info, ArrowRight } from 'lucide-react';
import { api } from '../api/client';

export default function AffordabilitySimulator({ initialSimulatedEmi = 20000 }) {
  const [income, setIncome] = useState(120000);
  const [obligations, setObligations] = useState(25000);
  const [simulatedEmi, setSimulatedEmi] = useState(initialSimulatedEmi);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (initialSimulatedEmi > 0) {
      setSimulatedEmi(initialSimulatedEmi);
    }
  }, [initialSimulatedEmi]);

  const handleSimulate = async () => {
    if (!income || income <= 0 || !simulatedEmi || simulatedEmi <= 0) return;
    setLoading(true);
    try {
      const res = await api.simulateAffordability({
        new_monthly_income: Number(income),
        existing_monthly_obligations: Number(obligations || 0),
        simulated_monthly_repayment: Number(simulatedEmi)
      });
      setResult(res);
    } catch (err) {
      console.error('Affordability simulation error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleSimulate();
  }, [income, obligations, simulatedEmi]);

  return (
    <div className="sports-card" style={{ marginTop: '24px', background: '#FFFFFF' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
        <div style={{
          background: 'var(--parrot-green-light)',
          color: 'var(--parrot-green)',
          padding: '8px',
          borderRadius: '8px',
          display: 'flex'
        }}>
          <Wallet size={20} />
        </div>
        <div>
          <h3 style={{ fontSize: '1.15rem', color: '#0F172A', margin: 0 }}>
            Hypothetical Affordability Simulation
          </h3>
          <p style={{ fontSize: '0.8rem', color: '#64748B', margin: 0 }}>
            Deterministic cashflow breakdown comparing transition commitments against projected new income
          </p>
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '20px'
      }}>
        <div>
          <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: '#334155', marginBottom: '6px' }}>
            New Monthly In-Hand Income (₹)
          </label>
          <input
            type="number"
            value={income}
            onChange={(e) => setIncome(e.target.value)}
            style={{
              width: '100%',
              padding: '9px 12px',
              borderRadius: '8px',
              border: '1px solid #CBD5E1',
              fontSize: '0.92rem',
              fontWeight: 600,
              color: '#0F172A'
            }}
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: '#334155', marginBottom: '6px' }}>
            Existing Monthly Obligations / EMIs (₹)
          </label>
          <input
            type="number"
            value={obligations}
            onChange={(e) => setObligations(e.target.value)}
            style={{
              width: '100%',
              padding: '9px 12px',
              borderRadius: '8px',
              border: '1px solid #CBD5E1',
              fontSize: '0.92rem',
              fontWeight: 600,
              color: '#0F172A'
            }}
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: '#334155', marginBottom: '6px' }}>
            Simulated Buyout Repayment (₹/mo)
          </label>
          <input
            type="number"
            value={simulatedEmi}
            onChange={(e) => setSimulatedEmi(e.target.value)}
            style={{
              width: '100%',
              padding: '9px 12px',
              borderRadius: '8px',
              border: '1px solid #CBD5E1',
              fontSize: '0.92rem',
              fontWeight: 600,
              color: '#0F172A'
            }}
          />
        </div>
      </div>

      {result && (
        <div style={{
          background: '#F8FAFC',
          border: '1px solid #E2E8F0',
          borderRadius: '12px',
          padding: '18px 20px'
        }}>
          {/* Neutral Metric Cards */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '12px',
            marginBottom: '16px'
          }}>
            <div style={{
              background: '#FFFFFF',
              border: '1px solid #E2E8F0',
              borderRadius: '8px',
              padding: '12px 14px'
            }}>
              <div style={{ fontSize: '0.74rem', color: '#64748B', fontWeight: 600, textTransform: 'uppercase' }}>
                Repayment to Income Ratio
              </div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--parrot-green)', marginTop: '2px' }}>
                {result.repayment_income_ratio_percent.value}%
              </div>
              <div style={{ fontSize: '0.72rem', color: '#94A3B8', marginTop: '2px' }}>
                Calculated: ₹{simulatedEmi.toLocaleString('en-IN')} / ₹{income.toLocaleString('en-IN')}
              </div>
            </div>

            <div style={{
              background: '#FFFFFF',
              border: '1px solid #E2E8F0',
              borderRadius: '8px',
              padding: '12px 14px'
            }}>
              <div style={{ fontSize: '0.74rem', color: '#64748B', fontWeight: 600, textTransform: 'uppercase' }}>
                Buffer After Obligations
              </div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0F172A', marginTop: '2px' }}>
                ₹{result.remaining_income_after_obligations.value.toLocaleString('en-IN')}
              </div>
              <div style={{ fontSize: '0.72rem', color: '#94A3B8', marginTop: '2px' }}>
                Prior to buyout repayment
              </div>
            </div>

            <div style={{
              background: '#FFFFFF',
              border: '1px solid #E2E8F0',
              borderRadius: '8px',
              padding: '12px 14px'
            }}>
              <div style={{ fontSize: '0.74rem', color: '#64748B', fontWeight: 600, textTransform: 'uppercase' }}>
                Remaining Monthly Buffer
              </div>
              <div style={{
                fontSize: '1.4rem',
                fontWeight: 800,
                color: result.remaining_income_after_repayment.value >= 0 ? '#15803D' : '#E11D48',
                marginTop: '2px'
              }}>
                ₹{result.remaining_income_after_repayment.value.toLocaleString('en-IN')}
              </div>
              <div style={{ fontSize: '0.72rem', color: '#94A3B8', marginTop: '2px' }}>
                Net disposable cashflow
              </div>
            </div>
          </div>

          {/* Factual Statement */}
          <div style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: '10px',
            background: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '8px',
            padding: '12px 16px',
            fontSize: '0.85rem',
            color: '#334155'
          }}>
            <Info size={16} style={{ color: '#2563EB', marginTop: '2px', flexShrink: 0 }} />
            <div>
              <strong>Objective Mathematical Assessment:</strong> {result.factual_summary}
              <div style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '4px' }}>
                NoticeBridge does not provide loans or underwrite credit. This simulation provides mathematical visibility into your personal transition budget.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
