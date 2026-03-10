export function formatTime(isoString) {
  if (!isoString) return '';
  const d = new Date(isoString);
  return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
}

export function formatDate(isoString) {
  if (!isoString) return '';
  const d = new Date(isoString);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export function formatNumber(n, decimals = 1) {
  if (n == null) return '--';
  return Number(n).toFixed(decimals);
}

export function formatPercent(n) {
  if (n == null) return '--';
  return `${Math.round(n * 100)}%`;
}
