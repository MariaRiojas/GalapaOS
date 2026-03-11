import { Sun, Thermometer, Droplets, Cloud, Gauge } from 'lucide-react';

export default function SolarConditions({ forecast }) {
  const ts = forecast.timesteps || [];
  // Pick the peak solar entry (highest radiation) as representative
  const nonForecast = ts.filter(t => !t.is_forecast);
  const peak = nonForecast.reduce((best, t) => (t.radiacion_wm2 > (best?.radiacion_wm2 || 0)) ? t : best, nonForecast[0]) || {};

  const items = [
    { icon: Sun, label: 'Peak Radiation', value: `${Math.round(peak.radiacion_wm2 || 0)}`, unit: 'W/m²', color: 'text-eco-solar' },
    { icon: Sun, label: 'Clarity Index (kt)', value: (peak.kt || 0).toFixed(2), unit: '', color: peak.kt > 0.7 ? 'text-eco-green' : peak.kt > 0.4 ? 'text-eco-yellow' : 'text-slate-300' },
    { icon: Thermometer, label: 'Temperature', value: `${peak.temp_c || '--'}`, unit: '°C', color: 'text-orange-400' },
    { icon: Droplets, label: 'Humidity', value: `${peak.humidity_pct || '--'}`, unit: '%', color: 'text-blue-400' },
    { icon: Cloud, label: 'Cloud Cover', value: `${peak.cloud_cover_pct || '--'}`, unit: '%', color: peak.cloud_cover_pct > 50 ? 'text-eco-yellow' : 'text-slate-300' },
    { icon: Gauge, label: 'Pressure', value: `${peak.pressure_hpa || '--'}`, unit: 'hPa', color: 'text-slate-300' },
  ];

  const peakTime = peak.time ? peak.time.split('T')[1]?.slice(0, 5) : '';

  return (
    <div className="bg-eco-card rounded-lg border border-slate-700 p-3 sm:p-4">
      <h3 className="text-[10px] sm:text-[11px] text-slate-400 uppercase tracking-wider font-medium mb-2 sm:mb-3">
        Solar Conditions
        {peakTime && <span className="text-slate-500 normal-case ml-1">(peak at {peakTime})</span>}
      </h3>
      <div className="grid grid-cols-2 gap-x-4 gap-y-2">
        {items.map((item, i) => (
          <div key={i} className="flex items-center gap-2">
            <item.icon className="w-3.5 h-3.5 text-slate-500 flex-shrink-0" />
            <div className="flex-1 min-w-0 flex items-baseline justify-between gap-1">
              <span className="text-[10px] sm:text-[11px] text-slate-400 truncate">{item.label}</span>
              <span className={`text-xs sm:text-sm font-semibold tabular-nums ${item.color}`}>
                {item.value}<span className="text-[9px] text-slate-500 ml-0.5">{item.unit}</span>
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
