import React from 'react';

type StatusType = 'success' | 'warning' | 'danger' | 'danger-alert' | 'neutral' | 'primary-light';

interface StatusBadgeProps {
  status: StatusType;
  label: string;
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label }) => {
  return (
    <span className={`badge badge-${status}`}>
      {label}
    </span>
  );
};

export default StatusBadge;
