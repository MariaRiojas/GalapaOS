import { Shield, Flame } from 'lucide-react';
import { SEMAPHORE_COLORS } from '../utils/colors';

export default function GridStatus({ forecast }) {
  const colors = SEMAPHORE_COLORS[forecast.current_color] || SEMAPHORE_COLORS.yellow;
  const isStable = forecast.current_color === 'green';
  const isCritical = forecast.current_color === 'red';
  const label = isStable ? 'STABLE' : isCritical ? 'DEFICIT' : 'WATCH';
  const fossilStatus = isCritical ? 'ACTIVE' : 'INACTIVE';

  return (
    <div className="bg-eco-card rounded-lg border border-slate-700 p-3 sm:p-4">
      <h3 className="text-[10px] sm:text-[11px] text-slate-400 uppercase tracking-wider font-medium mb-2 sm:mb-3">Grid Status</h3>
      <div className="grid grid-cols-2 gap-3">
        <div className="flex items-center gap-2 sm:gap-3">
          <div
            className="w-8 h-8 sm:w-10 sm:h-10 rounded-full flex items-center justify-center animate-pulse-glow flex-shrink-0"
            style={{ backgroundColor: `${colors.bg}30`, border: `2px solid ${colors.bg}` }}
          >
            <Shield className="w-4 h-4 sm:w-5 sm:h-5" style={{ color: colors.bg }} />
          </div>
          <div className="min-w-0">
            <p className="text-[10px] sm:text-xs text-slate-400">Stability</p>
            <p className="text-base sm:text-lg font-bold truncate" style={{ color: colors.bg }}>{label}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 sm:gap-3">
          <div
            className={`w-8 h-8 sm:w-10 sm:h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
              isCritical ? 'bg-red-900/40 border-2 border-eco-red' : 'bg-slate-700/40 border-2 border-slate-600'
            }`}
          >
            <Flame className={`w-4 h-4 sm:w-5 sm:h-5 ${isCritical ? 'text-eco-red' : 'text-slate-500'}`} />
          </div>
          <div className="min-w-0">
            <p className="text-[10px] sm:text-xs text-slate-400">Fossil Backup</p>
            <p className={`text-base sm:text-lg font-bold truncate ${isCritical ? 'text-eco-red' : 'text-slate-500'}`}>
              {fossilStatus}
            </p>
          </div>
        </div>
      </div>
      {forecast.action_trigger && (
        <div
          className="mt-2 sm:mt-3 px-2 sm:px-3 py-2 rounded-md text-[11px] sm:text-xs"
          style={{ backgroundColor: `${colors.bg}15`, border: `1px solid ${colors.bg}30` }}
        >
          <p className="leading-relaxed" style={{ color: colors.text }}>{forecast.action_trigger}</p>
          {forecast.next_transition && (
            <p className="text-slate-500 mt-0.5">Next: {forecast.next_transition}</p>
          )}
        </div>
      )}
    </div>
  );
}
