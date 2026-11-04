import React from 'react';

type BadgeTone = 'danger' | 'warn' | 'ok' | 'info' | 'neutral';

export const PageHead: React.FC<{ title: string; sub?: string }> = ({ title, sub }) => (
  <div className="page-head">
    <h2>{title}</h2>
    {sub && <p className="sub">{sub}</p>}
  </div>
);

export const Badge: React.FC<{ tone?: BadgeTone; children: React.ReactNode }> = ({ tone = 'neutral', children }) => (
  <span className={`badge badge-${tone}`}>{children}</span>
);

export const StatTile: React.FC<{ label: string; value: React.ReactNode }> = ({ label, value }) => (
  <div className="tile">
    <b>{value}</b>
    <span>{label}</span>
  </div>
);

export const Pager: React.FC<{
  page: number;
  totalPages: number;
  onPrev: () => void;
  onNext: () => void;
}> = ({ page, totalPages, onPrev, onNext }) => (
  <div className="pager">
    <button className="btn" onClick={onPrev} disabled={page === 1}>Trang trước</button>
    <span className="pager-info">Trang {page} / {totalPages}</span>
    <button className="btn" onClick={onNext} disabled={page >= totalPages}>Trang sau</button>
  </div>
);

export const EmptyState: React.FC<{
  title: string;
  desc?: string;
  action?: React.ReactNode;
  tone?: 'neutral' | 'ok';
}> = ({ title, desc, action, tone = 'neutral' }) => (
  <div className={`empty-state ${tone}`}>
    <h3>{title}</h3>
    {desc && <p>{desc}</p>}
    {action}
  </div>
);

export const Card: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className }) => (
  <div className={`panel-card ${className || ''}`}>{children}</div>
);

export const FilterPanel: React.FC<{
  title: string;
  icon?: React.ReactNode;
  onReset?: () => void;
  hasActive?: boolean;
  children: React.ReactNode;
}> = ({ title, icon, onReset, hasActive, children }) => (
  <div className="panel-filters">
    <div className="panel-filters-head">
      <div className="panel-filters-title">
        {icon}
        <span>{title}</span>
      </div>
      {hasActive && onReset && (
        <button className="btn btn-ghost-danger btn-sm" onClick={onReset}>Đặt lại bộ lọc</button>
      )}
    </div>
    {children}
  </div>
);
