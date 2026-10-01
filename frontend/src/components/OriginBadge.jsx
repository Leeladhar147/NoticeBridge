import React from 'react';
import { FileText, User, Cpu } from 'lucide-react';

export default function OriginBadge({ origin, source, compact = false }) {
  if (!origin) return null;

  const originLower = String(origin).toLowerCase();

  if (originLower === 'contract-derived') {
    return (
      <span
        className="badge-origin badge-contract"
        title={source ? `Contract Provenance: ${source}` : 'Verified from employment contract'}
      >
        <FileText size={11} />
        {!compact && 'Contract'}
      </span>
    );
  }

  if (originLower === 'user-provided') {
    return (
      <span
        className="badge-origin badge-user"
        title={source ? `User Input: ${source}` : 'Entered by candidate'}
      >
        <User size={11} />
        {!compact && 'User'}
      </span>
    );
  }

  if (originLower === 'calculated') {
    return (
      <span
        className="badge-origin badge-calculated"
        title={source ? `Deterministic Python Engine: ${source}` : 'Computed by deterministic Python engine'}
      >
        <Cpu size={11} />
        {!compact && 'Engine'}
      </span>
    );
  }

  return (
    <span className="badge-origin badge-user">
      {origin}
    </span>
  );
}
