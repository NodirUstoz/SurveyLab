import React from 'react';

interface StatusBadgeProps {
  status: string;
  size?: 'small' | 'medium';
}

const STATUS_STYLES: Record<string, { bg: string; color: string }> = {
  draft: { bg: '#f3f4f6', color: '#374151' },
  published: { bg: '#d1fae5', color: '#065f46' },
  closed: { bg: '#fee2e2', color: '#991b1b' },
  archived: { bg: '#ede9fe', color: '#5b21b6' },
  complete: { bg: '#d1fae5', color: '#065f46' },
  partial: { bg: '#fef3c7', color: '#92400e' },
  disqualified: { bg: '#fee2e2', color: '#991b1b' },
  generating: { bg: '#dbeafe', color: '#1e40af' },
  ready: { bg: '#d1fae5', color: '#065f46' },
  failed: { bg: '#fee2e2', color: '#991b1b' },
  sending: { bg: '#dbeafe', color: '#1e40af' },
  sent: { bg: '#d1fae5', color: '#065f46' },
  scheduled: { bg: '#e0e7ff', color: '#3730a3' },
};

const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'medium' }) => {
  const styles = STATUS_STYLES[status] || { bg: '#f3f4f6', color: '#374151' };

  return (
    <span
      style={{
        display: 'inline-block',
        padding: size === 'small' ? '2px 8px' : '4px 12px',
        fontSize: size === 'small' ? 11 : 12,
        fontWeight: 600,
        textTransform: 'capitalize',
        borderRadius: 9999,
        backgroundColor: styles.bg,
        color: styles.color,
        letterSpacing: '0.02em',
      }}
    >
      {status.replace('_', ' ')}
    </span>
  );
};

export default StatusBadge;
