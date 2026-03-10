import { Brain } from 'lucide-react';

export default function ModelInfo({ info }) {
  if (!info) return null;

  const bestTarget = info.targets?.solar_ramp_3h;
  const bestMetrics = bestTarget?.[info.best_model];

  return (
    <footer className="px-6 py-2 border-t border-slate-700 flex items-center gap-4 text-[11px] text-slate-500">
      <Brain className="w-3.5 h-3.5" />
      <span>Best model: <strong className="text-slate-400">{info.best_model}</strong></span>
      {bestMetrics && (
        <>
          <span>PR-AUC: <strong className="text-slate-400">{bestMetrics.PR_AUC}</strong></span>
          <span>CSI: <strong className="text-slate-400">{bestMetrics.CSI}</strong></span>
        </>
      )}
      <span>Features: {info.feature_count}</span>
      <span>Lookback: {info.lookback_hours}h</span>
      <span className="ml-auto">{info.data_range}</span>
    </footer>
  );
}
