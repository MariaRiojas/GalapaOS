export const SEMAPHORE_COLORS = {
  green: { bg: '#22c55e', glow: 'rgba(34, 197, 94, 0.4)', text: '#bbf7d0' },
  yellow: { bg: '#eab308', glow: 'rgba(234, 179, 8, 0.4)', text: '#fef08a' },
  red: { bg: '#ef4444', glow: 'rgba(239, 68, 68, 0.4)', text: '#fecaca' },
};

export const CHART_COLORS = {
  solar: '#fbbf24',
  wind: '#38bdf8',
  rain: '#60a5fa',
  ramp: '#ef4444',
};

export function getStatusColor(status) {
  switch (status) {
    case 'clear': return '#22c55e';
    case 'partly_cloudy': return '#eab308';
    case 'cloudy': return '#94a3b8';
    default: return '#64748b';
  }
}

export function getKtColor(kt) {
  if (kt > 0.7) return '#22c55e';
  if (kt > 0.4) return '#eab308';
  return '#94a3b8';
}
