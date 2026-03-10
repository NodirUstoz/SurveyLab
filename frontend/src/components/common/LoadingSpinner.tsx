import React from 'react';

interface LoadingSpinnerProps {
  message?: string;
  size?: 'small' | 'medium' | 'large';
  fullPage?: boolean;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = 'Loading...',
  size = 'medium',
  fullPage = false,
}) => {
  const sizeMap = {
    small: { spinner: 20, border: 2 },
    medium: { spinner: 40, border: 3 },
    large: { spinner: 60, border: 4 },
  };
  const dims = sizeMap[size];

  const spinnerStyle: React.CSSProperties = {
    width: dims.spinner,
    height: dims.spinner,
    border: `${dims.border}px solid #e5e7eb`,
    borderTopColor: '#4f46e5',
    borderRadius: '50%',
    animation: 'spin 0.8s linear infinite',
  };

  const containerStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
    padding: 24,
    ...(fullPage ? { minHeight: '60vh' } : {}),
  };

  return (
    <div style={containerStyle}>
      <div style={spinnerStyle} />
      {message && <p style={{ color: '#6b7280', fontSize: 14 }}>{message}</p>}
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

export default LoadingSpinner;
