import React, { useState, useEffect } from 'react';
import { Building2, Save, FileText, CheckCircle2, AlertCircle, Sparkles, Upload } from 'lucide-react';
import { api } from '../api/client';
import OriginBadge from '../components/OriginBadge';
import DocumentIntelligenceModal from '../components/DocumentIntelligenceModal';

export default function CurrentEmploymentPage({ setActivePage }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [sourceDoc, setSourceDoc] = useState(null);
  const [form, setForm] = useState({
    company_name: 'Apex Global Technologies',
    designation: 'Senior Systems Engineer',
    joining_date: '2024-02-15',
    resignation_date: '2026-08-31',
    is_resigned: true,
    notice_period_days: 90,
    buyout_clause_permitted: true,
    buyout_salary_basis: 'basic',
    monthly_divisor_basis: '30_days',
    custom_divisor: '',
    basic_salary_monthly: 60000,
    gross_salary_monthly: 95000,
    clause_reference_notes: 'Clause 14.2: Notice buyout permitted subject to management approval at Basic Salary rate.'
  });

  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await api.getCurrentEmployment();
        if (data) {
          setForm({
            company_name: data.company_name?.value || 'Apex Global Technologies',
            designation: data.designation?.value || 'Senior Systems Engineer',
            joining_date: data.joining_date?.value || '2024-02-15',
            resignation_date: data.resignation_date?.value || '2026-08-31',
            is_resigned: data.is_resigned?.value ?? true,
            notice_period_days: data.notice_period_days?.value || 90,
            buyout_clause_permitted: data.buyout_clause_permitted?.value ?? true,
            buyout_salary_basis: data.buyout_salary_basis?.value || 'basic',
            monthly_divisor_basis: data.monthly_divisor_basis?.value || '30_days',
            custom_divisor: data.custom_divisor?.value || '',
            basic_salary_monthly: data.basic_salary_monthly?.value || 60000,
            gross_salary_monthly: data.gross_salary_monthly?.value || 95000,
            clause_reference_notes: data.clause_reference_notes?.value || ''
          });
        }
      } catch (e) {
        // Fallback default
      }
    };
    load();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const payload = {
        ...form,
        notice_period_days: Number(form.notice_period_days),
        basic_salary_monthly: Number(form.basic_salary_monthly),
        gross_salary_monthly: form.gross_salary_monthly ? Number(form.gross_salary_monthly) : null,
        custom_divisor: form.custom_divisor ? Number(form.custom_divisor) : null
      };
      await api.saveCurrentEmployment(payload);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.message || 'Failed to save current employment.');
    } finally {
      setLoading(false);
    }
  };

  const handleApplyContract = (extracted) => {
    setSourceDoc(extracted);
    setForm(prev => ({
      ...prev,
      company_name: extracted.company_name?.value || prev.company_name,
      notice_period_days: extracted.notice_period_days?.value ?? prev.notice_period_days,
      buyout_clause_permitted: extracted.buyout_permitted?.value ?? prev.buyout_clause_permitted,
      buyout_salary_basis: extracted.buyout_salary_basis?.value && extracted.buyout_salary_basis.value !== 'unknown' 
        ? extracted.buyout_salary_basis.value 
        : prev.buyout_salary_basis,
      basic_salary_monthly: extracted.basic_salary_monthly?.value ?? prev.basic_salary_monthly,
      gross_salary_monthly: extracted.gross_salary_monthly?.value ?? prev.gross_salary_monthly,
      clause_reference_notes: extracted.notice_period_days?.evidence_quote 
        ? `Extracted from ${extracted.document_name} (Page ${extracted.notice_period_days?.page_number || 1}): "${extracted.notice_period_days.evidence_quote.slice(0, 140)}"`
        : prev.clause_reference_notes
    }));
    setSuccess(true);
    setTimeout(() => setSuccess(false), 4000);
  };

  return (
    <div style={{ background: '#FFFFFF', minHeight: '100%' }}>
      <DocumentIntelligenceModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        documentType="employment_agreement"
        onApplyExtraction={handleApplyContract}
      />

      <div className="container" style={{ padding: '36px 24px 60px 24px', maxWidth: '840px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px', marginBottom: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              background: 'var(--parrot-green-light)',
              padding: '8px',
              borderRadius: '8px',
              color: 'var(--parrot-green)'
            }}>
              <Building2 size={24} />
            </div>
            <div>
              <h1 style={{ fontSize: '1.9rem', color: 'var(--text-primary)' }}>Current Employment & Contract Terms</h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                Deterministic parameters extracted from your signed employment agreement
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={() => setIsModalOpen(true)}
            style={{
              background: 'var(--parrot-green-light)',
              color: 'var(--parrot-green-text)',
              border: '1px solid var(--parrot-green-border)',
              borderRadius: '8px',
              padding: '8px 16px',
              fontSize: '0.86rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              boxShadow: '0 2px 6px rgba(22, 163, 74, 0.12)'
            }}
          >
            <Sparkles size={16} /> Upload & Extract Contract
          </button>
        </div>

        {sourceDoc && (
          <div style={{
            background: '#F0FDF4',
            border: '1px solid #BBF7D0',
            borderRadius: '8px',
            padding: '10px 14px',
            marginTop: '12px',
            marginBottom: '12px',
            fontSize: '0.82rem',
            color: '#15803D',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle2 size={16} />
              <span>Grounding verified from: <strong>{sourceDoc.document_name}</strong></span>
            </div>
            <span style={{ fontSize: '0.74rem', background: '#DCFCE7', padding: '2px 8px', borderRadius: '4px', fontWeight: 700 }}>
              AI RAG Extracted
            </span>
          </div>
        )}

        <div style={{
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '10px',
          padding: '12px 16px',
          margin: '18px 0 24px 0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '10px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            <FileText size={16} color="#2563EB" />
            <span>Classified as Contract-Derived variables for deterministic calculation</span>
          </div>
          <OriginBadge origin="contract-derived" source={sourceDoc ? sourceDoc.document_name : "Employment Agreement"} />
        </div>

        {success && (
          <div style={{
            background: 'var(--parrot-green-light)',
            border: '1px solid var(--parrot-green-border)',
            color: 'var(--parrot-green-text)',
            padding: '12px 16px',
            borderRadius: '8px',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontWeight: 600
          }}>
            <CheckCircle2 size={18} /> Contract terms successfully recorded and synchronized!
          </div>
        )}

        {error && (
          <div style={{
            background: 'var(--tradelearn-pink-light)',
            border: '1px solid var(--tradelearn-pink-border)',
            color: 'var(--tradelearn-pink-text)',
            padding: '12px 16px',
            borderRadius: '8px',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}>
            <AlertCircle size={18} /> {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="sports-card" style={{ background: '#FFFFFF' }}>
          {/* Section 1: Employment Identity */}
          <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', color: 'var(--text-primary)', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
            1. Employment Identity
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', marginBottom: '20px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
                Current Employer Name
              </label>
              <input
                type="text"
                required
                className="form-input"
                value={form.company_name}
                onChange={(e) => setForm({ ...form, company_name: e.target.value })}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
                Job Designation / Title
              </label>
              <input
                type="text"
                required
                className="form-input"
                value={form.designation}
                onChange={(e) => setForm({ ...form, designation: e.target.value })}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: '16px', marginBottom: '24px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
                Joining Date
              </label>
              <input
                type="date"
                required
                className="form-input"
                value={form.joining_date}
                onChange={(e) => setForm({ ...form, joining_date: e.target.value })}
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
                Resignation Date
              </label>
              <input
                type="date"
                className="form-input"
                value={form.resignation_date}
                onChange={(e) => setForm({ ...form, resignation_date: e.target.value })}
              />
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', paddingTop: '22px' }}>
              <input
                type="checkbox"
                id="resigned"
                checked={form.is_resigned}
                onChange={(e) => setForm({ ...form, is_resigned: e.target.checked })}
                style={{ width: '18px', height: '18px', accentColor: 'var(--parrot-green)' }}
              />
              <label htmlFor="resigned" style={{ fontSize: '0.85rem', color: 'var(--text-primary)', cursor: 'pointer', fontWeight: 600 }}>
                Resignation Submitted
              </label>
            </div>
          </div>

          {/* Section 2: Notice & Buyout Clauses */}
          <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', color: 'var(--text-primary)', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
            2. Notice Period & Buyout Clauses
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '20px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
                Contractual Notice Period (Days)
              </label>
              <input
                type="number"
                required
                min="1"
                max="365"
                className="form-input"
                value={form.notice_period_days}
                onChange={(e) => setForm({ ...form, notice_period_days: e.target.value })}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
                Contractual Salary Basis
              </label>
              <select
                className="form-input"
                value={form.buyout_salary_basis}
                onChange={(e) => setForm({ ...form, buyout_salary_basis: e.target.value })}
              >
                <option value="basic">Basic Salary Basis (Standard)</option>
                <option value="gross">Gross Salary Basis</option>
                <option value="fixed">Fixed Salary Basis</option>
                <option value="custom">Custom Contractual Amount</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
                Monthly Divisor Basis
              </label>
              <select
                className="form-input"
                value={form.monthly_divisor_basis}
                onChange={(e) => setForm({ ...form, monthly_divisor_basis: e.target.value })}
              >
                <option value="30_days">30-Day Monthly Standard (₹/30)</option>
                <option value="26_working_days">26 Working Days Standard (₹/26)</option>
                <option value="calendar_month">Calendar Days in Month (28-31)</option>
                <option value="annual_365">Annualized Salary / 365 Days</option>
                <option value="custom">Custom Explicit Divisor</option>
              </select>
            </div>
          </div>

          {form.monthly_divisor_basis === 'custom' && (
            <div style={{ marginBottom: '18px' }}>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
                Custom Divisor Value (e.g. 25 or 28)
              </label>
              <input
                type="number"
                step="0.1"
                className="form-input"
                value={form.custom_divisor}
                onChange={(e) => setForm({ ...form, custom_divisor: e.target.value })}
              />
            </div>
          )}

          {/* Section 3: Salary Components */}
          <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', color: 'var(--text-primary)', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
            3. Salary Components (INR)
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', marginBottom: '20px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
                Monthly Basic Salary (₹)
              </label>
              <input
                type="number"
                required
                min="1"
                className="form-input"
                value={form.basic_salary_monthly}
                onChange={(e) => setForm({ ...form, basic_salary_monthly: e.target.value })}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
                Monthly Gross Salary (₹, Optional)
              </label>
              <input
                type="number"
                min="1"
                className="form-input"
                value={form.gross_salary_monthly}
                onChange={(e) => setForm({ ...form, gross_salary_monthly: e.target.value })}
              />
            </div>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
              Contract Clause Excerpt / Reference Notes
            </label>
            <textarea
              className="form-input"
              rows="3"
              value={form.clause_reference_notes}
              onChange={(e) => setForm({ ...form, clause_reference_notes: e.target.value })}
              placeholder="e.g. Clause 14.2: Either party may terminate employment by giving 90 days notice in writing or paying salary in lieu thereof..."
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <button
              type="submit"
              disabled={loading}
              className="btn-volt"
              style={{ padding: '11px 24px' }}
            >
              {loading ? 'Saving Terms...' : 'Save Contract Terms'}
              <Save size={16} />
            </button>

            <button
              type="button"
              onClick={() => setActivePage('new-offer')}
              className="btn-outline"
            >
              Next: Configure New Offer →
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
