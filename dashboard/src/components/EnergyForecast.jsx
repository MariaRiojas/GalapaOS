import {
  ComposedChart, Area, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer,
  ReferenceLine, ReferenceArea,
} from 'recharts';
import { SEMAPHORE_COLORS } from '../utils/colors';

const DEMAND_RADIATION_EQUIV = 1000;

function buildColorBands(data) {
  if (!data || data.length < 2) return [];
  const bands = [];
  let start = 0;
  for (let i = 1; i <= data.length; i++) {
    if (i === data.length || data[i].color !== data[start].color) {
      bands.push({
        x1: data[start].time,
        x2: data[Math.min(i, data.length - 1)].time,
        color: data[start].color,
      });
      start = i;
    }
  }
  return bands;
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  const raw = payload[0]?.payload || {};
  const date = new Date(label);
  const hh = String(date.getHours()).padStart(2, '0');
  const mm = String(date.getMinutes()).padStart(2, '0');
  return (
    <div className="bg-slate-800 border border-slate-600 rounded-lg px-2 sm:px-3 py-1.5 sm:py-2 text-[10px] sm:text-xs shadow-xl">
      <p className="text-slate-300 font-medium mb-1">
        {hh}:{mm} {raw.is_forecast ? '(Forecast)' : ''}
      </p>
      <p className="text-eco-solar">
        Radiation: <strong>{raw.radiacion_wm2} W/m²</strong>
      </p>
      <p className="text-slate-400">
        Solar: {raw.solar_kw?.toFixed(3)} kW | kt: {raw.kt}
      </p>
      <p className={`font-medium ${
        raw.color === 'green' ? 'text-eco-green' : raw.color === 'red' ? 'text-eco-red' : 'text-eco-yellow'
      }`}>
        RDI: {raw.rdi}
      </p>
    </div>
  );
}

function Legend() {
  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[9px] sm:text-[10px] text-slate-400">
      <span className="flex items-center gap-1">
        <span className="w-3 h-0.5 bg-emerald-500 inline-block rounded" />
        Actual
      </span>
      <span className="flex items-center gap-1">
        <span className="w-3 h-0.5 inline-block rounded" style={{ background: 'repeating-linear-gradient(90deg, #60a5fa 0 4px, transparent 4px 7px)' }} />
        Predicted
      </span>
      <span className="flex items-center gap-1">
        <span className="w-3 h-0.5 inline-block rounded" style={{ background: 'repeating-linear-gradient(90deg, #f87171 0 4px, transparent 4px 7px)' }} />
        Demand Equiv.
      </span>
    </div>
  );
}

export default function EnergyForecast({ forecast, timesteps: filteredTs, filterBar }) {
  const timesteps = filteredTs || forecast.timesteps || [];
  if (timesteps.length === 0) return null;

  const data = timesteps.map(t => ({
    ...t,
    actual_rad: t.is_forecast ? null : t.radiacion_wm2,
    forecast_rad: t.is_forecast ? t.radiacion_wm2 : null,
  }));

  // Connect actual → forecast lines
  const lastActualIdx = data.reduce((last, d, i) => d.actual_rad != null ? i : last, 0);
  if (lastActualIdx < data.length - 1 && data[lastActualIdx + 1]?.forecast_rad != null) {
    data[lastActualIdx].forecast_rad = data[lastActualIdx].actual_rad;
  }

  const bands = buildColorBands(data);
  const maxRad = Math.max(...data.map(d => d.radiacion_wm2 || 0), 1200);
  const yMax = Math.ceil(maxRad / 200) * 200;

  return (
    <div className="bg-eco-card rounded-lg border border-slate-700 p-3 sm:p-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-2 sm:mb-3 gap-2 flex-wrap">
        <h3 className="text-[10px] sm:text-[11px] text-slate-400 uppercase tracking-wider font-medium">
          Energy Forecast
          <span className="text-slate-500 normal-case ml-2">Solar Radiation (W/m²)</span>
          <span className="text-slate-600 normal-case ml-1">({timesteps.length} points)</span>
        </h3>
        <div className="flex items-center gap-3 flex-wrap">
          {filterBar}
          <Legend />
        </div>
      </div>

      <ResponsiveContainer width="100%" height={320}>
        <ComposedChart data={data} margin={{ top: 10, right: 10, left: -5, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />

          {bands.map((b, i) => {
            const c = SEMAPHORE_COLORS[b.color]?.bg || '#64748b';
            return (
              <ReferenceArea
                key={i} x1={b.x1} x2={b.x2}
                fill={c} fillOpacity={0.06} strokeOpacity={0}
              />
            );
          })}

          <XAxis
            dataKey="time"
            tickFormatter={t => {
              const d = new Date(t);
              return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
            }}
            tick={{ fill: '#94a3b8', fontSize: 10 }}
            interval={Math.max(1, Math.floor(data.length / 10))}
            stroke="#475569"
            height={28}
          />
          <YAxis
            tick={{ fill: '#94a3b8', fontSize: 10 }}
            stroke="#475569"
            domain={[0, yMax]}
            width={50}
            tickFormatter={v => v >= 1000 ? `${(v / 1000).toFixed(1)}k` : v}
            label={{ value: 'W/m²', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 10, dx: 12 }}
          />

          <Tooltip content={<CustomTooltip />} />

          <Area
            dataKey="actual_rad"
            name="Actual"
            fill="#22c55e"
            fillOpacity={0.25}
            stroke="#22c55e"
            strokeWidth={2}
            type="monotone"
            connectNulls={false}
            dot={false}
          />

          <Line
            dataKey="forecast_rad"
            name="Predicted"
            stroke="#60a5fa"
            strokeWidth={2}
            strokeDasharray="6 3"
            type="monotone"
            connectNulls={false}
            dot={false}
          />

          <ReferenceLine
            y={DEMAND_RADIATION_EQUIV}
            stroke="#f87171"
            strokeDasharray="8 4"
            strokeWidth={1.5}
            label={{ value: 'Demand', fill: '#f87171', fontSize: 9, position: 'right' }}
          />

          {(() => {
            const lastActual = data.filter(d => d.actual_rad != null);
            if (lastActual.length === 0) return null;
            const nowTime = lastActual[lastActual.length - 1].time;
            return (
              <ReferenceLine
                x={nowTime}
                stroke="#94a3b8"
                strokeDasharray="4 4"
                label={{ value: 'NOW', fill: '#94a3b8', fontSize: 10, position: 'top' }}
              />
            );
          })()}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
