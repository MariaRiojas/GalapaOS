import { Sun, Wind, Cloud, Thermometer, CloudRain } from 'lucide-react';

function findClosestTimestep(timesteps, targetTime) {
  let closest = timesteps[0];
  let minDiff = Infinity;
  for (const ts of timesteps) {
    const diff = Math.abs(new Date(ts.time).getTime() - targetTime);
    if (diff < minDiff) { minDiff = diff; closest = ts; }
  }
  return closest;
}

export default function WeatherTable({ forecast }) {
  const ts = forecast.timesteps || [];
  if (ts.length === 0) return null;

  const now = ts.filter(t => !t.is_forecast);
  const currentTs = now[now.length - 1] || ts[0];
  const currentTime = new Date(currentTs.time).getTime();

  const offsets = [
    { label: '+3h', ms: 3 * 3600000 },
    { label: '+6h', ms: 6 * 3600000 },
    { label: '+12h', ms: 12 * 3600000 },
  ];

  const columns = offsets.map(o => {
    const target = currentTime + o.ms;
    const found = findClosestTimestep(ts, target);
    const t = new Date(found.time);
    const timeStr = `${String(t.getHours()).padStart(2, '0')}:${String(t.getMinutes()).padStart(2, '0')}`;
    return { ...o, ts: found, timeStr };
  });

  const rows = [
    {
      icon: Sun, label: 'Solar Rad.',
      shortLabel: 'Solar',
      values: columns.map(c => ({
        val: `${Math.round(c.ts.radiacion_wm2)}`,
        unit: 'W/m²',
        alert: c.ts.radiacion_wm2 > 800,
        warn: c.ts.radiacion_wm2 < 200 && c.ts.radiacion_wm2 > 0,
      })),
    },
    {
      icon: Wind, label: 'Wind Speed',
      shortLabel: 'Wind',
      values: columns.map(c => ({ val: `${c.ts.wind_ms}`, unit: 'm/s' })),
    },
    {
      icon: Cloud, label: 'Cloud Cover',
      shortLabel: 'Cloud',
      values: columns.map(c => ({
        val: `${c.ts.cloud_cover_pct}`,
        unit: '%',
        warn: c.ts.cloud_cover_pct > 70,
      })),
    },
    {
      icon: Thermometer, label: 'Temperature',
      shortLabel: 'Temp',
      values: columns.map(c => ({ val: `${c.ts.temp_c}`, unit: '°C' })),
    },
    {
      icon: CloudRain, label: 'Precipitation',
      shortLabel: 'Rain',
      values: columns.map(c => ({
        val: `${c.ts.rain_mm}`,
        unit: 'mm',
        warn: c.ts.rain_mm > 0.5,
      })),
    },
  ];

  return (
    <div className="bg-eco-card rounded-lg border border-slate-700 p-3 sm:p-4 overflow-x-auto">
      <h3 className="text-[10px] sm:text-[11px] text-slate-400 uppercase tracking-wider font-medium mb-2 sm:mb-3">
        Weather Forecast <span className="text-slate-500">({offsets.map(o => o.label).join(', ')})</span>
      </h3>
      <table className="w-full text-[11px] sm:text-xs min-w-[280px]">
        <thead>
          <tr className="border-b border-slate-700">
            <th className="text-left py-1 sm:py-1.5 text-slate-500 font-medium w-24 sm:w-32" />
            {columns.map(c => (
              <th key={c.label} className="text-center py-1 sm:py-1.5 text-slate-400 font-semibold">
                <div>{c.timeStr}</div>
                <div className="text-[9px] text-slate-500 font-normal">{c.label}</div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr key={ri} className="border-b border-slate-700/50">
              <td className="py-1.5 sm:py-2 text-slate-400">
                <div className="flex items-center gap-1">
                  <row.icon className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-slate-500 flex-shrink-0" />
                  <span className="hidden sm:inline">{row.label}</span>
                  <span className="sm:hidden">{row.shortLabel}</span>
                </div>
              </td>
              {row.values.map((v, vi) => (
                <td key={vi} className="text-center py-1.5 sm:py-2">
                  <span className={`font-medium ${
                    v.alert ? 'text-eco-solar' : v.warn ? 'text-eco-yellow' : 'text-slate-200'
                  }`}>
                    {v.val}
                  </span>
                  <span className="text-slate-500 ml-0.5 text-[9px] sm:text-[10px]">{v.unit}</span>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
