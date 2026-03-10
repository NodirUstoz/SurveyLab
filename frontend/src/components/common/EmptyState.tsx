import React from 'react';

interface EmptyStateProps {
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  actionLabel,
  onAction,
  icon,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '48px 24px',
        textAlign: 'center',
        backgroundColor: '#f9fafb',
        borderRadius: 12,
        border: '1px dashed #d1d5db',
      }}
    >
      {icon && (
        <div style={{ fontSize: 48, marginBottom: 16, color: '#9ca3af' }}>
          {icon}
        </div>
      )}
      <h3
        style={{
          fontSize: 18,
          fontWeight: 600,
          color: '#374151',
          margin: '0 0 8px 0',
        }}
      >
        {title}
      </h3>
      {description && (
        <p
          style={{
            fontSize: 14,
            color: '#6b7280',
            margin: '0 0 20px 0',
            maxWidth: 400,
          }}
        >
          {description}
        </p>
      )}
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          style={{
            padding: '10px 20px',
            backgroundColor: '#4f46e5',
            color: '#fff',
            border: 'none',
            borderRadius: 8,
            fontSize: 14,
            fontWeight: 500,
            cursor: 'pointer',
          }}
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
};

export default EmptyState;
