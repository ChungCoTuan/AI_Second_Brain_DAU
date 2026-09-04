import React from 'react';
import './Shared.css';
import { RelationBadge } from './Badge';

interface RelationItemProps {
  title: string;
  meta: string;
  type: 'direct' | 'semantic';
  level?: 'direct_apply' | 'general_apply' | 'reference';
  similarity?: number;
  onClick?: () => void;
}

export const RelationItem: React.FC<RelationItemProps> = ({ title, meta, type, level, similarity, onClick }) => {
  return (
    <div className="relation-item" onClick={onClick}>
      <div className="relation-item-info">
        <span className="relation-item-title">{title}</span>
        <span className="relation-item-meta">{meta} {similarity && `• Độ tương đồng: ${similarity}%`}</span>
      </div>
      <div>
        <RelationBadge type={type} level={level} />
      </div>
    </div>
  );
};

interface RelationListProps {
  items: RelationItemProps[];
}

export const RelationList: React.FC<RelationListProps> = ({ items }) => {
  if (items.length === 0) {
    return <div className="text-muted" style={{ padding: '1rem', fontStyle: 'italic' }}>Chưa phát hiện văn bản liên quan</div>;
  }

  return (
    <div className="relation-list">
      {items.map((item, idx) => (
        <RelationItem key={idx} {...item} />
      ))}
    </div>
  );
};
