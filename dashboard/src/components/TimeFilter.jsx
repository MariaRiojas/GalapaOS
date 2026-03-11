import { Clock } from 'lucide-react';

const RANGES = [
  { label: '3h', hours: 3 },
  { label: '6h', hours: 6 },
  { label: '12h', hours: 12 },
  { label: '24h', hours: 24 },
];

export default function TimeFilter({ timesteps, selectedRange, onRangeChange, selectedDateTime, onDateTimeChange }) {
  if (!timesteps?.length) return null;

  // Compute min/max from data for the input bounds
  const times = timesteps.map(t => t.time);
  const minDt = times[0] || '';
  const maxDt = times[times.length - 1] || '';

  // Convert selectedDateTime to datetime-local format (YYYY-MM-DDTHH:mm)
  const inputValue = selectedDateTime ? selectedDateTime.slice(0, 16) : minDt.slice(0, 16);

  return (
    <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
      <div className="flex items-center gap-1.5">
        <Clock className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
        <input
          type="datetime-local"
          value={inputValue}
          min={minDt.slice(0, 16)}
          max={maxDt.slice(0, 16)}
          onChange={e => onDateTimeChange(e.target.value)}
          className="bg-slate-700 text-slate-200 text-[11px] sm:text-xs rounded-md px-2 py-1 border border-slate-600 focus:outline-none focus:border-eco-green [color-scheme:dark]"
        />
      </div>

      <div className="flex rounded-md overflow-hidden border border-slate-600">
        {RANGES.map(r => (
          <button
            key={r.label}
            onClick={() => onRangeChange(r.hours)}
            className={`px-2 sm:px-3 py-1 text-[11px] font-medium transition-colors ${
              selectedRange === r.hours
                ? 'bg-eco-green/20 text-eco-green'
                : 'bg-slate-700 text-slate-400 hover:bg-slate-600 hover:text-slate-200'
            }`}
          >
            {r.label}
          </button>
        ))}
      </div>
    </div>
  );
}
