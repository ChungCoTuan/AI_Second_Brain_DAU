import React from 'react';
import './Shared.css';
import { StatusBadge } from './Badge';
import type { DocStatus } from './Badge';
import { Folder } from 'lucide-react';

// --- Document Card ---
interface DocumentCardProps {
  title: string;
  type: string;
  topic: string;
  status: DocStatus;
  date: string;
  onClick?: () => void;
}

export const DocumentCard: React.FC<DocumentCardProps> = ({ title, type, topic, status, date, onClick }) => {
  return (
    <div className="doc-card" onClick={onClick}>
      <div className="doc-card-header">
        <h3 className="doc-card-title">{title}</h3>
        <StatusBadge status={status} />
      </div>
      <div className="doc-card-meta">
        <span>{type}</span>
        <span>•</span>
        <span>{topic}</span>
        <span>•</span>
        <span>{date}</span>
      </div>
    </div>
  );
};

// --- Topic Card ---
interface TopicCardProps {
  title: string;
  count: number;
  icon?: React.ReactNode;
  onClick?: () => void;
}

export const TopicCard: React.FC<TopicCardProps> = ({ title, count, icon, onClick }) => {
  return (
    <div className="topic-card" onClick={onClick}>
      <div className="topic-card-icon">
        {icon || <Folder size={24} />}
      </div>
      <h3 className="topic-card-title">{title}</h3>
      <span className="topic-card-count">{count} văn bản</span>
    </div>
  );
};
