import { SEMAPHORE_COLORS } from '../utils/colors';
import { formatNumber } from '../utils/formatters';

export default function Semaphore({ rdi, color, label, action }) {
  const colors = SEMAPHORE_COLORS[color] || SEMAPHORE_COLORS.yellow;

  return (
    <div className="bg-eco-card rounded-xl p-6 flex flex-col items-center justify-center gap-3">
      <div
        className="w-36 h-36 rounded-full flex items-center justify-center animate-pulse-glow"
        style={{
          backgroundColor: `${colors.bg}30`,
          boxShadow: `0 0 40px ${colors.glow}, 0 0 80px ${colors.glow}`,
          border: `3px solid ${colors.bg}`,
        }}
      >
        <span className="text-4xl font-bold" style={{ color: colors.bg }}>
          {formatNumber(rdi, 2)}
        </span>
      </div>
      <div className="text-center">
        <p className="text-lg font-bold tracking-wider" style={{ color: colors.bg }}>
          {label || color?.toUpperCase()}
        </p>
        <p className="text-xs text-slate-400 mt-1 max-w-48">{action}</p>
      </div>
      <p className="text-[10px] text-slate-500 mt-1">Renewable Dispatch Index</p>
    </div>
  );
}
