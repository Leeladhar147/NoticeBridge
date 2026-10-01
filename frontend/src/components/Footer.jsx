import React from 'react';
import { AlertTriangle, Cpu, Shield } from 'lucide-react';

export default function Footer() {
  return (
    <footer style={{
      background: 'var(--bg-secondary)',
      borderTop: '1px solid var(--border-subtle)',
      padding: '48px 0 32px 0',
      marginTop: '80px',
      color: 'var(--text-secondary)'
    }}>
      <div className="container">
        {/* Critical Disclaimer Banner */}
        <div style={{
          background: '#FFF5F5',
          border: '1px solid #FED7D7',
          borderRadius: '12px',
          padding: '20px 24px',
          marginBottom: '36px',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '16px'
        }}>
          <div style={{
            background: 'var(--tradelearn-pink-light)',
            padding: '10px',
            borderRadius: '8px',
            color: 'var(--tradelearn-pink)',
            flexShrink: 0
          }}>
            <AlertTriangle size={24} />
          </div>
          <div>
            <div style={{
              fontFamily: 'var(--font-heading)',
              fontWeight: 800,
              fontSize: '0.98rem',
              color: '#991B1B',
              marginBottom: '4px',
              letterSpacing: '0.01em'
            }}>
              PROTOTYPE & SIMULATION DISCLAIMER
            </div>
            <p style={{ fontSize: '0.86rem', color: '#4A5568', lineHeight: '1.6' }}>
              <strong>NoticeBridge is a notice-period transition and financing simulation platform.</strong> It is an engineering prototype and analytical sandbox, <strong>NOT a registered financial institution, broker, or lender</strong>, and does NOT execute real monetary loans or disbursements. It does not provide legal advice. Contractual calculations are deterministic simulations dependent strictly upon employment agreements and user-provided inputs.
            </p>
          </div>
        </div>

        {/* Footer Meta */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px',
          paddingTop: '20px',
          borderTop: '1px solid var(--border-subtle)',
          fontSize: '0.82rem',
          color: 'var(--text-muted)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>NoticeBridge Core v1.0.0</span>
            <span>•</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Cpu size={14} color="var(--parrot-green)" />
              Deterministic Python Engine
            </span>
            <span>•</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Shield size={14} color="#0284C7" />
              Zero-LLM Math Integrity
            </span>
          </div>

          <div style={{ color: 'var(--text-muted)' }}>
            Architecture Principle: Document → Structured Data → Deterministic Engine → Explainable Result
          </div>
        </div>
      </div>
    </footer>
  );
}
