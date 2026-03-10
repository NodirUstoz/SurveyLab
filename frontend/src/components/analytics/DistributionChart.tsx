import React from 'react';

interface DistributionChartProps {
  title: string;
  data: Record<string, number>;
  total: number;
  labelMap?: Record<string, string>;
  color?: string;
  showPercentage?: boolean;
}

const COLORS = [
  '#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#6366f1',
];

const DistributionChart: React.FC<DistributionChartProps> = ({
  title,
  data,
  total,
  labelMap,
  color,
  showPercentage = true,
}) => {
  const entries = Object.entries(data).sort(([, a], [, b]) => b - a);
  const maxValue = entries.length > 0 ? Math.max(...entries.map(([, v]) => v)) : 1;

  return (
    <div
      style={{
        backgroundColor: '#fff',
        border: '1px solid #e5e7eb',
        borderRadius: 12,
        padding: 20,
      }}
    >
      <h4 style={{ margin: '0 0 16px', fontSize: 14, fontWeight: 600, color: '#374151' }}>
        {title}
      </h4>
      {entries.length === 0 ? (
        <p style={{ color: '#9ca3af', fontSize: 13 }}>No data available</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {entries.map(([key, count], index) => {
            const percentage = total > 0 ? (count / total) * 100 : 0;
            const barColor = color || COLORS[index % COLORS.length];
            const label = labelMap?.[key] || key;

            return (
              <div key={key}>
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    fontSize: 13,
                    marginBottom: 4,
                  }}
                >
                  <span style={{ color: '#374151' }}>{label}</span>
                  <span style={{ color: '#6b7280' }}>
                    {count}
                    {showPercentage && ` (${percentage.toFixed(1)}%)`}
                  </span>
                </div>
                <div
                  style={{
                    height: 8,
                    backgroundColor: '#f3f4f6',
                    borderRadius: 4,
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      height: '100%',
                      width: `${(count / maxValue) * 100}%`,
                      backgroundColor: barColor,
                      borderRadius: 4,
                      transition: 'width 0.3s ease',
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default DistributionChart;
