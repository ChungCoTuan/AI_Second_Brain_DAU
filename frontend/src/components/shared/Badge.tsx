import React from 'react';
import './Shared.css';
import { CheckCircle, AlertCircle, XCircle, FileText, Bookmark, Info } from 'lucide-react';

// --- Types ---
export type NLIStatus = 'entailment' | 'neutral' | 'contradiction';
export type DocStatus = 'published' | 'pending_review' | 'expired' | 'replaced';

// --- Citation Badge ---
interface CitationBadgeProps {
  id: string;
  source: string;
  onClick?: () => void;
}
export const CitationBadge: React.FC<CitationBadgeProps> = ({ id, source, onClick }) => {
  return (
    <span className="badge badge-citation hover-lift" onClick={onClick} title={`ID: ${id}`}>
      <FileText size={14} />
      <span>{source}</span>
    </span>
  );
};

// --- Status Badge ---
interface StatusBadgeProps {
  status: DocStatus;
}
export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  let label = '';
  let className = 'badge ';

  switch (status) {
    case 'published':
      label = 'Đã published';
      className += 'badge-success';
      break;
    case 'pending_review':
      label = 'Đang chờ rà soát';
      className += 'badge-warning';
      break;
    case 'expired':
      label = 'Hết hiệu lực';
      className += 'badge-danger';
      break;
    case 'replaced':
      label = 'Đã thay thế';
      className += 'badge-danger';
      break;
  }

  return (
    <span className={className}>
      {status === 'published' && <CheckCircle size={14} />}
      {status === 'pending_review' && <AlertCircle size={14} />}
      {(status === 'expired' || status === 'replaced') && <XCircle size={14} />}
      <span>{label}</span>
    </span>
  );
};

// --- NLI Label Badge ---
interface NLILabelBadgeProps {
  label: NLIStatus;
}
export const NLILabelBadge: React.FC<NLILabelBadgeProps> = ({ label }) => {
  let text = '';
  let className = 'badge ';

  switch (label) {
    case 'entailment':
      text = 'Entailment';
      className += 'badge-success';
      break;
    case 'neutral':
      text = 'Neutral';
      className += 'badge-warning';
      break;
    case 'contradiction':
      text = 'Contradiction';
      className += 'badge-danger';
      break;
  }

  return (
    <span className={className}>
      {label === 'entailment' && <CheckCircle size={14} />}
      {label === 'neutral' && <AlertCircle size={14} />}
      {label === 'contradiction' && <XCircle size={14} />}
      <span>{text}</span>
    </span>
  );
};

// --- Priority Indicator ---
interface PriorityIndicatorProps {
  level: 'high' | 'medium' | 'low';
}
export const PriorityIndicator: React.FC<PriorityIndicatorProps> = ({ level }) => {
  const colors = {
    high: 'var(--color-danger)',
    medium: 'var(--color-warning)',
    low: 'var(--color-success)',
  };
  const labels = {
    high: 'Ưu tiên cao (Contradiction)',
    medium: 'Ưu tiên vừa (Neutral)',
    low: 'Bình thường',
  };

  return (
    <div className="priority-indicator" title={labels[level]}>
      <span className="priority-dot" style={{ backgroundColor: colors[level] }}></span>
      <span className="priority-label">{labels[level]}</span>
    </div>
  );
};

// --- Manual Override Badge ---
export const ManualOverrideBadge: React.FC = () => {
  return (
    <span className="badge badge-neutral">
      <Bookmark size={14} />
      <span>Đã xác nhận thủ công</span>
    </span>
  );
};

// --- Relation Badge ---
interface RelationBadgeProps {
  type: 'direct' | 'semantic';
  level?: 'direct_apply' | 'general_apply' | 'reference';
}
export const RelationBadge: React.FC<RelationBadgeProps> = ({ type, level }) => {
  if (type === 'semantic' && level) {
    const labels = {
      direct_apply: 'Áp dụng trực tiếp',
      general_apply: 'Áp dụng chung',
      reference: 'Tham khảo',
    };
    return (
      <span className="badge badge-primary-light">
        <Info size={14} />
        <span>{labels[level]}</span>
      </span>
    );
  }
  
  return (
    <span className="badge badge-neutral">
      <span>Quan hệ tường minh</span>
    </span>
  );
};
