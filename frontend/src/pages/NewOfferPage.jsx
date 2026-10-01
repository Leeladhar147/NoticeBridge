import React, { useState, useEffect } from 'react';
import { Briefcase, Save, CheckCircle2, AlertCircle, Calendar, Sparkles } from 'lucide-react';
import { api } from '../api/client';
import OriginBadge from '../components/OriginBadge';
import DocumentIntelligenceModal from '../components/DocumentIntelligenceModal';

export default function NewOfferPage({ setActivePage }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [sourceDoc, setSourceDoc] = useState(null);
  const [form, setForm] = useState({
    company_name: 'HyperScale Cloud Labs',
    designation: 'Lead Cloud Architect',
    offered_ctc_annual: 1800000,
    target_joining_date: '2026-10-30',
    buyout_assistance_amount: 30000,
    signing_bonus: 50000,
    retention_clawback_months: 12
  });

  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await api.getOffer();
        if (data) {
          setForm({
            company_name: data.company_name?.value || 'HyperScale Cloud Labs',
            designation: data.designation?.value || 'Lead Cloud Architect',
            offered_ctc_annual: data.offered_ctc_annual?.value || 1800000,
            target_joining_date: data.target_joining_date?.value || '2026-10-30',
            buyout_assistance_amount: data.buyout_assistance_amount?.value || 30000,
            signing_bonus: data.signing_bonus?.value || 50000,
            retention_clawback_months: data.retention_clawback_months?.value || 12
          });
        }
      } catch (e) {
        // Fallback default
      }
    };
    load();
  }, []);

  const handleApplyOffer = (extracted) => {
    setSourceDoc(extracted);
    setForm(prev => ({
      ...prev,
      company_name: extracted.offering_company?.value || prev.company_name,
      designation: extracted.role_title?.value || prev.designation,
      target_joining_date: extracted.target_joining_date?.value || prev.target_joining_date,
      offered_ctc_annual: extracted.offered_ctc_annual?.value ?? prev.offered_ctc_annual,
      buyout_assistance_amount: extracted.buyout_assistance_amount?.value ?? prev.buyout_assistance_amount,
      signing_bonus: extracted.signing_bonus?.value ?? prev.signing_bonus,
      retention_clawback_months: extracted.retention_clawback_months?.value ?? prev.retention_clawback_months
    }));
    setSuccess(true);
    setTimeout(() => setSuccess(false), 4000);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const payload = {
        ...form,
        offered_ctc_annual: Number(form.offered_ctc_annual),
        buyout_assistance_amount: Number(form.buyout_assistance_amount),
        signing_bonus: Number(form.signing_bonus),
        retention_clawback_months: Number(form.retention_clawback_months)
      };
      await api.saveOffer(payload);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.message || 'Failed to save offer.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ background: '#FFFFFF', minHeight: '100%' }}>
      <DocumentIntelligenceModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        documentType="offer_letter"
        onApplyExtraction={handleApplyOffer}
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
              <Briefcase size={24} />
            </div>
            <div>
              <h1 style={{ fontSize: '1.9rem', color: 'var(--text-primary)' }}>New Employer Offer & Assistance</h1>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                Target joining deadlines and employer co-sponsorship parameters
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
            <Sparkles size={16} /> Upload & Extract Offer
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
              <span>Extracted from: <strong>{sourceDoc.document_name}</strong></span>
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
            <Calendar size={16} color="#2563EB" />
            <span>Classified as User-Provided & Offer-Derived variables</span>
          </div>
          <OriginBadge origin="user-provided" source={sourceDoc ? sourceDoc.document_name : "Offer Letter"} />
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
            <CheckCircle2 size={18} /> Offer parameters successfully updated!
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
          <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', color: 'var(--text-primary)', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
            1. Offer Opportunity Details
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', marginBottom: '20px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
                Offering Company
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
                New Job Title
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

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
                Offered Annual CTC (₹)
              </label>
              <input
                type="number"
                required
                min="1"
                className="form-input"
                value={form.offered_ctc_annual}
                onChange={(e) => setForm({ ...form, offered_ctc_annual: e.target.value })}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
                Target Joining Deadline
              </label>
              <input
                type="date"
                required
                className="form-input"
                value={form.target_joining_date}
                onChange={(e) => setForm({ ...form, target_joining_date: e.target.value })}
              />
            </div>
          </div>

          <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', color: 'var(--text-primary)', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
            2. Buyout Assistance & Joining Incentives
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '28px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
                Buyout Assistance Co-Pay (₹)
              </label>
              <input
                type="number"
                min="0"
                className="form-input"
                value={form.buyout_assistance_amount}
                onChange={(e) => setForm({ ...form, buyout_assistance_amount: e.target.value })}
                placeholder="0"
              />
              <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '4px', display: 'block' }}>
                Direct reimbursement or buyout check provided by Company B
              </span>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
                Joining / Signing Bonus (₹)
              </label>
              <input
                type="number"
                min="0"
                className="form-input"
                value={form.signing_bonus}
                onChange={(e) => setForm({ ...form, signing_bonus: e.target.value })}
                placeholder="0"
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
                Retention Clawback Period (Months)
              </label>
              <input
                type="number"
                min="0"
                max="60"
                className="form-input"
                value={form.retention_clawback_months}
                onChange={(e) => setForm({ ...form, retention_clawback_months: e.target.value })}
              />
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <button
              type="submit"
              disabled={loading}
              className="btn-volt"
              style={{ padding: '11px 24px' }}
            >
              {loading ? 'Saving Offer...' : 'Save New Offer'}
              <Save size={16} />
            </button>

            <button
              type="button"
              onClick={() => setActivePage('notice-calc')}
              className="btn-outline"
            >
              Run Notice Calculator →
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
