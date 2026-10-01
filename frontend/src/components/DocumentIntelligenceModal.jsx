import React, { useState } from 'react';
import { 
  Upload, FileText, CheckCircle2, AlertTriangle, ShieldCheck, 
  HelpCircle, Sparkles, X, ChevronRight, BookOpen, Lock
} from 'lucide-react';
import { api } from '../api/client';

export default function DocumentIntelligenceModal({
  isOpen,
  onClose,
  documentType = 'employment_agreement', // 'employment_agreement' or 'offer_letter'
  onApplyExtraction
}) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [step, setStep] = useState('upload'); // 'upload' | 'review'
  const [extractedData, setExtractedData] = useState(null);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    const selected = e.target.files?.[0];
    if (!selected) return;

    // Validate size (10MB)
    if (selected.size > 10 * 1024 * 1024) {
      setError('File size exceeds the 10 MB limit.');
      return;
    }

    const ext = selected.name.split('.').pop()?.toLowerCase();
    if (!['pdf', 'txt', 'md'].includes(ext)) {
      setError('Only PDF, TXT, and Markdown files are supported.');
      return;
    }

    setError(null);
    setFile(selected);
  };

  const handleUploadAndExtract = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);

    try {
      // 1. Upload document securely
      const uploadRes = await api.uploadDocument(file, 1, documentType);
      const docId = uploadRes.document_id;

      // 2. Run targeted RAG and source-grounded extraction
      setUploading(false);
      setExtracting(true);

      let intelligenceRes;
      if (documentType === 'employment_agreement') {
        intelligenceRes = await api.extractContract(docId);
      } else {
        intelligenceRes = await api.extractOffer(docId);
      }

      setExtractedData(intelligenceRes);
      setStep('review');
    } catch (err) {
      setError(err.message || 'Failed to process document.');
    } finally {
      setUploading(false);
      setExtracting(false);
    }
  };

  const handleConfirmAndApply = () => {
    if (onApplyExtraction && extractedData) {
      onApplyExtraction(extractedData);
    }
    onClose();
  };

  const getConfidenceBadge = (confidence) => {
    switch (confidence) {
      case 'HIGH':
        return (
          <span style={{
            background: '#EFF6FF',
            color: '#1D4ED8',
            border: '1px solid #BFDBFE',
            padding: '2px 8px',
            borderRadius: '999px',
            fontSize: '0.72rem',
            fontWeight: 700,
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px'
          }}>
            <ShieldCheck size={12} /> High Confidence
          </span>
        );
      case 'MEDIUM':
        return (
          <span style={{
            background: '#FEF3C7',
            color: '#B45309',
            border: '1px solid #FDE68A',
            padding: '2px 8px',
            borderRadius: '999px',
            fontSize: '0.72rem',
            fontWeight: 700,
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px'
          }}>
            <AlertTriangle size={12} /> Medium Confidence
          </span>
        );
      case 'UNKNOWN':
      default:
        return (
          <span style={{
            background: '#FFF1F2',
            color: '#BE123C',
            border: '1px solid #FECDD3',
            padding: '2px 8px',
            borderRadius: '999px',
            fontSize: '0.72rem',
            fontWeight: 700,
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px'
          }}>
            <HelpCircle size={12} /> Needs Confirmation
          </span>
        );
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(15, 23, 42, 0.65)',
        backdropFilter: 'blur(4px)',
        zIndex: 10000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px'
      }}
    >
      <div
        className="sports-card"
        style={{
          width: '100%',
          maxWidth: '820px',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          padding: '0',
          overflow: 'hidden',
          background: '#FFFFFF',
          borderRadius: '16px',
          boxShadow: '0 25px 50px -12px rgba(15, 23, 42, 0.25)'
        }}
      >
        {/* Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: '#F8FAFC'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              background: 'var(--parrot-green-light)',
              color: 'var(--parrot-green)',
              padding: '8px',
              borderRadius: '8px',
              display: 'flex'
            }}>
              <Sparkles size={20} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.25rem', color: '#0F172A', margin: 0 }}>
                {documentType === 'employment_agreement' 
                  ? 'Extract Contract Intelligence' 
                  : 'Extract Offer Details'}
              </h2>
              <p style={{ fontSize: '0.8rem', color: '#64748B', margin: 0 }}>
                Targeted RAG clause retrieval with strict source-grounded evidence
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: '#64748B',
              padding: '6px',
              borderRadius: '6px',
              display: 'flex'
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Body content */}
        <div style={{ padding: '24px', overflowY: 'auto', flex: 1 }}>
          {error && (
            <div style={{
              background: '#FFF1F2',
              border: '1px solid #FECDD3',
              color: '#BE123C',
              padding: '12px 16px',
              borderRadius: '8px',
              marginBottom: '20px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              fontSize: '0.88rem'
            }}>
              <AlertTriangle size={18} />
              <span>{error}</span>
            </div>
          )}

          {step === 'upload' ? (
            <div>
              <div
                style={{
                  border: '2px dashed #CBD5E1',
                  borderRadius: '12px',
                  padding: '36px 20px',
                  textAlign: 'center',
                  background: '#F8FAFC',
                  cursor: 'pointer',
                  transition: 'border-color 0.2s ease',
                  position: 'relative'
                }}
              >
                <input
                  type="file"
                  accept=".pdf,.txt,.md"
                  onChange={handleFileChange}
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    opacity: 0,
                    cursor: 'pointer'
                  }}
                />
                <div style={{
                  width: '48px',
                  height: '48px',
                  borderRadius: '50%',
                  background: 'var(--parrot-green-light)',
                  color: 'var(--parrot-green)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 12px auto'
                }}>
                  <Upload size={24} />
                </div>
                <h4 style={{ fontSize: '1rem', color: '#0F172A', marginBottom: '4px' }}>
                  {file ? file.name : 'Click or drag & drop employment document here'}
                </h4>
                <p style={{ fontSize: '0.8rem', color: '#64748B', margin: 0 }}>
                  Supports PDF (up to 10 MB), TXT, or Markdown
                </p>
                {file && (
                  <div style={{
                    marginTop: '12px',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    color: 'var(--parrot-green)',
                    fontSize: '0.82rem',
                    fontWeight: 600
                  }}>
                    <FileText size={16} /> Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
                  </div>
                )}
              </div>

              {/* Privacy Safeguards note */}
              <div style={{
                marginTop: '20px',
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '8px',
                padding: '14px 16px',
                display: 'flex',
                gap: '12px',
                alignItems: 'flex-start'
              }}>
                <Lock size={18} style={{ color: 'var(--parrot-green)', marginTop: '2px', flexShrink: 0 }} />
                <div style={{ fontSize: '0.82rem', color: '#475569', lineHeight: 1.45 }}>
                  <strong>Confidentiality Guarantee:</strong> Employment agreements contain sensitive personal data. 
                  Documents are stored in a private directory, full text is never logged publicly, and clauses are 
                  retrieved strictly to assist in parameter validation.
                </div>
              </div>
            </div>
          ) : (
            <div>
              {/* Review Extracted Data */}
              <div style={{
                background: 'var(--parrot-green-light)',
                border: '1px solid var(--parrot-green-border)',
                borderRadius: '8px',
                padding: '14px 18px',
                marginBottom: '20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--parrot-green-text)', textTransform: 'uppercase', fontWeight: 700 }}>
                    Extraction Summary
                  </div>
                  <div style={{ fontSize: '0.9rem', color: '#0F172A', fontWeight: 600 }}>
                    Document: {extractedData.document_name}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--parrot-green-text)' }}>Overall Confidence:</span>
                  {getConfidenceBadge(extractedData.overall_confidence)}
                </div>
              </div>

              {/* Warnings / Unknowns */}
              {extractedData.requires_user_confirmation && (
                <div style={{
                  background: '#FFFBEB',
                  border: '1px solid #FDE68A',
                  borderRadius: '8px',
                  padding: '12px 16px',
                  marginBottom: '20px',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '10px'
                }}>
                  <AlertTriangle size={18} style={{ color: '#D97706', marginTop: '2px' }} />
                  <div>
                    <strong style={{ color: '#92400E', fontSize: '0.85rem' }}>Human Verification Required:</strong>
                    <p style={{ color: '#B45309', fontSize: '0.82rem', margin: '4px 0 0 0' }}>
                      Some terms could not be determined with high confidence and require your manual confirmation.
                      Values will not be assumed.
                    </p>
                  </div>
                </div>
              )}

              {/* Extracted Fields Table with Citations */}
              <h4 style={{ fontSize: '0.95rem', color: '#0F172A', marginBottom: '12px' }}>
                Contract-Derived Parameters & Evidence Grounding
              </h4>

              <div style={{
                border: '1px solid #E2E8F0',
                borderRadius: '10px',
                overflow: 'hidden',
                marginBottom: '20px'
              }}>
                {documentType === 'employment_agreement' ? (
                  <>
                    <EvidenceRow 
                      label="Company Name" 
                      field={extractedData.company_name} 
                    />
                    <EvidenceRow 
                      label="Notice Period" 
                      field={extractedData.notice_period_days} 
                      formatter={(v) => v ? `${v} Days` : 'Unknown (Needs Confirmation)'} 
                    />
                    <EvidenceRow 
                      label="Buyout Clause Permitted" 
                      field={extractedData.buyout_permitted} 
                      formatter={(v) => v === true ? 'Permitted' : (v === false ? 'Explicitly Prohibited' : 'Unknown / Needs Confirmation')} 
                    />
                    <EvidenceRow 
                      label="Salary Basis" 
                      field={extractedData.buyout_salary_basis} 
                      formatter={(v) => v ? `${v.toUpperCase()} Salary` : 'Unknown'} 
                    />
                    <EvidenceRow 
                      label="Monthly Basic Salary" 
                      field={extractedData.basic_salary_monthly} 
                      formatter={(v) => v ? `₹${v.toLocaleString('en-IN')}` : 'Not Specified'} 
                    />
                    <EvidenceRow 
                      label="Monthly Gross Salary" 
                      field={extractedData.gross_salary_monthly} 
                      formatter={(v) => v ? `₹${v.toLocaleString('en-IN')}` : 'Not Specified'} 
                    />
                  </>
                ) : (
                  <>
                    <EvidenceRow 
                      label="Offering Company" 
                      field={extractedData.offering_company} 
                    />
                    <EvidenceRow 
                      label="Designation / Role" 
                      field={extractedData.role_title} 
                    />
                    <EvidenceRow 
                      label="Target Joining Date" 
                      field={extractedData.target_joining_date} 
                    />
                    <EvidenceRow 
                      label="Annual CTC" 
                      field={extractedData.offered_ctc_annual} 
                      formatter={(v) => v ? `₹${v.toLocaleString('en-IN')}` : 'Not Specified'} 
                    />
                    <EvidenceRow 
                      label="Buyout Assistance Contribution" 
                      field={extractedData.buyout_assistance_amount} 
                      formatter={(v) => v ? `₹${v.toLocaleString('en-IN')}` : 'None Stated (Can simulate manually)'} 
                    />
                  </>
                )}
              </div>

              {/* Retrieved Raw Clauses */}
              {extractedData.retrieved_clauses && extractedData.retrieved_clauses.length > 0 && (
                <div>
                  <h4 style={{ fontSize: '0.9rem', color: '#0F172A', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <BookOpen size={16} style={{ color: '#2563EB' }} /> Retrieved Contractual Clauses
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {extractedData.retrieved_clauses.slice(0, 3).map((clause, idx) => (
                      <div key={idx} style={{
                        background: '#F8FAFC',
                        border: '1px solid #E2E8F0',
                        borderRadius: '8px',
                        padding: '10px 14px',
                        fontSize: '0.8rem'
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', color: '#64748B', marginBottom: '4px', fontSize: '0.74rem' }}>
                          <span style={{ fontWeight: 600, color: '#2563EB' }}>Clause: {clause.query_intent}</span>
                          <span>Page {clause.page_number} {clause.section_title ? `• ${clause.section_title}` : ''}</span>
                        </div>
                        <div style={{ color: '#334155', fontStyle: 'italic', lineHeight: 1.4 }}>
                          "{clause.text_content.slice(0, 220)}..."
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '16px 24px',
          borderTop: '1px solid var(--border-subtle)',
          display: 'flex',
          justifyContent: 'flex-end',
          gap: '12px',
          background: '#F8FAFC'
        }}>
          <button
            onClick={onClose}
            style={{
              padding: '9px 18px',
              borderRadius: '8px',
              border: '1px solid #CBD5E1',
              background: '#FFFFFF',
              color: '#334155',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '0.88rem'
            }}
          >
            Cancel
          </button>

          {step === 'upload' ? (
            <button
              onClick={handleUploadAndExtract}
              disabled={!file || uploading || extracting}
              style={{
                padding: '9px 20px',
                borderRadius: '8px',
                border: 'none',
                background: !file || uploading || extracting ? '#94A3B8' : 'var(--parrot-green)',
                color: '#FFFFFF',
                cursor: !file || uploading || extracting ? 'not-allowed' : 'pointer',
                fontWeight: 700,
                fontSize: '0.88rem',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                boxShadow: 'var(--shadow-parrot)'
              }}
            >
              {uploading ? 'Uploading...' : extracting ? 'Retrieving Clauses...' : 'Extract Contract Terms'}
              <ChevronRight size={16} />
            </button>
          ) : (
            <button
              onClick={handleConfirmAndApply}
              style={{
                padding: '9px 22px',
                borderRadius: '8px',
                border: 'none',
                background: 'var(--parrot-green)',
                color: '#FFFFFF',
                cursor: 'pointer',
                fontWeight: 700,
                fontSize: '0.88rem',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                boxShadow: 'var(--shadow-parrot)'
              }}
            >
              <CheckCircle2 size={16} /> Confirm & Populate Form
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function EvidenceRow({ label, field, formatter }) {
  if (!field) return null;
  const displayVal = formatter ? formatter(field.value) : (field.value ?? 'Unknown');
  const isUnknown = field.confidence === 'UNKNOWN' || field.value === null;

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '180px 1fr 140px',
      padding: '12px 16px',
      borderBottom: '1px solid #F1F5F9',
      alignItems: 'center',
      gap: '12px',
      background: isUnknown ? '#FFFDF5' : '#FFFFFF'
    }}>
      <div style={{ fontSize: '0.84rem', fontWeight: 600, color: '#334155' }}>
        {label}
      </div>

      <div>
        <div style={{
          fontSize: '0.9rem',
          fontWeight: 700,
          color: isUnknown ? '#B45309' : '#0F172A',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          {displayVal}
        </div>
        {field.evidence_quote && (
          <div style={{
            fontSize: '0.74rem',
            color: '#64748B',
            marginTop: '2px',
            fontStyle: 'italic'
          }}>
            Source quote: "{field.evidence_quote.slice(0, 110)}..."
          </div>
        )}
        {field.status_message && (
          <div style={{ fontSize: '0.72rem', color: '#D97706', marginTop: '2px' }}>
            Note: {field.status_message}
          </div>
        )}
      </div>

      <div style={{ textAlign: 'right' }}>
        <span style={{
          background: field.confidence === 'HIGH' ? '#EFF6FF' : '#FEF3C7',
          color: field.confidence === 'HIGH' ? '#1D4ED8' : '#B45309',
          border: field.confidence === 'HIGH' ? '1px solid #BFDBFE' : '1px solid #FDE68A',
          padding: '2px 8px',
          borderRadius: '999px',
          fontSize: '0.7rem',
          fontWeight: 700
        }}>
          {field.confidence === 'HIGH' ? 'Page ' + (field.page_number || '1') : 'Needs Review'}
        </span>
      </div>
    </div>
  );
}
