import { AlertTriangle, CheckCircle, AlertCircle } from 'lucide-react';
import { SEMAPHORE_COLORS } from '../utils/colors';

export default function ActionTrigger({ color, message, nextTransition }) {
  const colors = SEMAPHORE_COLORS[color] || SEMAPHORE_COLORS.yellow;
  const Icon = color === 'green' ? CheckCircle : color === 'red' ? AlertTriangle : AlertCircle;

  return (
    <div
      className="mx-4 mt-3 px-5 py-3 rounded-lg flex items-center gap-4 animate-slide-in"
      style={{ backgroundColor: `${colors.bg}20`, border: `1px solid ${colors.bg}40` }}
    >
      <Icon className="w-6 h-6 flex-shrink-0" style={{ color: colors.bg }} />
      <div className="flex-1">
        <p className="font-semibold text-sm" style={{ color: colors.text }}>{message}</p>
        {nextTransition && (
          <p className="text-xs text-slate-400 mt-0.5">Next transition: {nextTransition}</p>
        )}
      </div>
    </div>
  );
}
