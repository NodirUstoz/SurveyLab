import React from 'react';

interface StatsCardProps {
  label: string;
  value: string | number;
  subtitle?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color?: string;
  size?: 'small' | 'medium' | 'large';
}

const StatsCard: React.FC<StatsCardProps> = ({
  label,
  value,
  subtitle,
  trend,
  color = '#4f46e5',
  size = 'medium',
}) => {
  const fontSizes = {
    small: { value: 20, label: 11, subtitle: 10 },
    medium: { value: 28, label: 12, subtitle: 11 },
    large: { value: 36, label: 14, subtitle: 12 },
  };
  const sizes = fontSizes[size];

  return (
    <div
      style={{
        backgroundColor: '#fff',
        border: '1px solid #e5e7eb',
        borderRadius: 12,
        padding: size === 'large' ? 24 : 16,
        display: 'flex',
        flexDirection: 'column',
        gap: 4,
      }}
    >
      <div
        style={{
          fontSize: sizes.label,
          fontWeight: 500,
          color: '#6b7280',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontSize: sizes.value,
          fontWeight: 700,
          color: color,
          lineHeight: 1.2,
        }}
      >
        {value}
      </div>
      {(subtitle || trend) && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            fontSize: sizes.subtitle,
          }}
        >
          {trend && (
            <span
              style={{
                color: trend.isPositive ? '#10b981' : '#ef4444',
                fontWeight: 600,
              }}
            >
              {trend.isPositive ? '+' : ''}{trend.value}%
            </span>
          )}
          {subtitle && (
            <span style={{ color: '#9ca3af' }}>{subtitle}</span>
          )}
        </div>
      )}
    </div>
  );
};

export default StatsCard;
