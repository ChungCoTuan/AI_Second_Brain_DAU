import React from 'react';

type StatusType = 'success' | 'warning' | 'danger';

interface StatusBadgeProps {
  status: StatusType;
  label: string;
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label }) => {
  return (
    <span className={`status-badge status-${status}`}>
      {label}
    </span>
  );
};

export default StatusBadge;
