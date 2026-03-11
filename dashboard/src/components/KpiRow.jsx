import { Sun, Gauge, Zap, TrendingUp } from 'lucide-react';
import { SEMAPHORE_COLORS } from '../utils/colors';

const DEMAND_KW = 912;

function KpiCard({ icon: Icon, label, value, unit, sub, color }) {
  return (
    <div className="bg-eco-card rounded-lg p-3 sm:p-4 border border-slate-700">
      <div className="flex items-center gap-1.5 mb-1 sm:mb-2">
        <Icon className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-slate-400 flex-shrink-0" />
        <span className="text-[10px] sm:text-[11px] text-slate-400 uppercase tracking-wider font-medium truncate">{label}</span>
      </div>
      <div className="flex items-baseline gap-1">
        <span className="text-xl sm:text-2xl lg:text-3xl font-bold tabular-nums" style={{ color: color || '#e2e8f0' }}>{value}</span>
        <span className="text-xs sm:text-sm text-slate-400">{unit}</span>
      </div>
      {sub && <p className="text-[10px] sm:text-[11px] text-slate-500 mt-0.5 sm:mt-1 truncate">{sub}</p>}
    </div>
  );
}

export default function KpiRow({ forecast }) {
  const ts = forecast.timesteps || [];
  // Current: latest non-forecast entry with radiation
  const nonForecast = ts.filter(t => !t.is_forecast);
  const current = nonForecast.reduce((best, t) =>
    (t.radiacion_wm2 > (best?.radiacion_wm2 || 0)) ? t : best, nonForecast[0]) || {};

  const solarGeneration = Math.round(current.radiacion_wm2 || 0);
  const renewablePct = Math.min(100, Math.round((current.rdi || 0) * 100));

  // Error: compare a past prediction with its actual
  const actual = nonForecast.filter(t => t.radiacion_wm2 > 10);
  let errorPct = '--';
  if (actual.length >= 2) {
    const lastActual = actual[actual.length - 1];
    const prevEntry = nonForecast.find(t => t.predicciones);
    if (prevEntry?.predicciones?.prediccion_1 && lastActual.radiacion_wm2 > 10) {
      const predicted = prevEntry.predicciones.prediccion_1;
      const actualVal = lastActual.radiacion_wm2;
      errorPct = Math.abs(Math.round(((predicted - actualVal) / Math.max(actualVal, 1)) * 100));
    }
  }

  const colors = SEMAPHORE_COLORS[forecast.current_color] || SEMAPHORE_COLORS.yellow;

  return (
    <div className="px-3 sm:px-4 pt-3 sm:pt-4 grid grid-cols-2 md:grid-cols-4 gap-2 sm:gap-3">
      <KpiCard
        icon={Gauge}
        label="Demanda Actual"
        value={DEMAND_KW}
        unit="kW"
        sub="Pto. Baquerizo Moreno"
      />
      <KpiCard
        icon={Sun}
        label="Radiación Solar"
        value={solarGeneration}
        unit="W/m²"
        sub={`≈ ${(current.solar_kw || 0).toFixed(2)} kW`}
        color="#fbbf24"
      />
      <KpiCard
        icon={TrendingUp}
        label="% Uso Renovable"
        value={renewablePct}
        unit="%"
        sub={`RDI: ${(current.rdi || 0).toFixed(2)}`}
        color={colors.bg}
      />
      <KpiCard
        icon={Zap}
        label="% Error Predicción"
        value={errorPct}
        unit={typeof errorPct === 'number' ? '%' : ''}
        sub="Predicción vs real"
        color={typeof errorPct === 'number' && errorPct > 20 ? '#ef4444' : '#22c55e'}
      />
    </div>
  );
}
