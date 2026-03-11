import {
  ComposedChart, Area, Line, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer,
  ReferenceArea,
} from 'recharts';
import { CHART_COLORS, SEMAPHORE_COLORS } from '../utils/colors';
import { formatTime } from '../utils/formatters';

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

function formatAxisTick(time, rangeHours) {
  const d = new Date(time);
  const hh = String(d.getHours()).padStart(2, '0');
  const mm = String(d.getMinutes()).padStart(2, '0');
  if (rangeHours > 24) {
    const day = d.getDate();
    const mon = d.toLocaleDateString('en-US', { month: 'short' });
    return `${day} ${mon} ${hh}:${mm}`;
  }
  return `${hh}:${mm}`;
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  const date = new Date(label);
  const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  const timeStr = formatTime(label);
  const raw = payload[0]?.payload || {};
  return (
    <div className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-xs shadow-lg">
      <p className="text-slate-300 font-medium mb-1">{dateStr} {timeStr}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }}>
          {p.name}: {typeof p.value === 'number' ? p.value.toFixed(2) : p.value}
        </p>
      ))}
      {raw.radiacion_wm2 != null && (
        <p className="text-amber-300 mt-1">Irradiance: {raw.radiacion_wm2} W/m²</p>
      )}
      {raw.temp_c != null && (
        <p className="text-orange-300">Temp: {raw.temp_c}°C | Humidity: {raw.humidity_pct}%</p>
      )}
      {raw.cloud_cover_pct != null && (
        <p className="text-blue-300">Cloud: {raw.cloud_cover_pct}% | kt: {raw.kt}</p>
      )}
      {raw.is_forecast && (
        <p className="text-purple-400 mt-1 italic">Forecast</p>
      )}
    </div>
  );
}

export default function Timeline({ timesteps, rangeHours = 12, filterBar }) {
  if (!timesteps?.length) {
    return (
      <div className="bg-eco-card rounded-xl p-6 flex items-center justify-center h-full">
        <p className="text-slate-500">No forecast data</p>
      </div>
    );
  }

  const data = timesteps.map(t => ({
    ...t,
    timeLabel: formatTime(t.time),
  }));

  const bands = buildColorBands(data);

  const tickInterval = rangeHours <= 6 ? Math.max(1, Math.floor(data.length / 12))
    : rangeHours <= 12 ? Math.max(1, Math.floor(data.length / 8))
    : rangeHours <= 24 ? Math.max(1, Math.floor(data.length / 8))
    : Math.max(1, Math.floor(data.length / 10));

  return (
    <div className="bg-eco-card rounded-xl p-4">
      <div className="flex items-center justify-between mb-3 px-2 flex-wrap gap-2">
        <h3 className="text-sm font-semibold text-slate-300">
          Forecast Timeline
          <span className="text-slate-500 font-normal ml-2">
            ({data.length} points)
          </span>
        </h3>
        {filterBar}
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <ComposedChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />

          {bands.map((b, i) => {
            const c = SEMAPHORE_COLORS[b.color]?.bg || '#64748b';
            return (
              <ReferenceArea
                key={i}
                x1={b.x1}
                x2={b.x2}
                fill={c}
                fillOpacity={0.08}
                strokeOpacity={0}
              />
            );
          })}

          <XAxis
            dataKey="time"
            tickFormatter={t => formatAxisTick(t, rangeHours)}
            tick={{ fill: '#94a3b8', fontSize: 10 }}
            interval={tickInterval}
            stroke="#475569"
            angle={rangeHours > 24 ? -25 : 0}
            textAnchor={rangeHours > 24 ? 'end' : 'middle'}
            height={rangeHours > 24 ? 45 : 30}
          />
          <YAxis
            yAxisId="left"
            tick={{ fill: '#94a3b8', fontSize: 10 }}
            stroke="#475569"
            label={{ value: 'W/m²', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 10 }}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            tick={{ fill: '#94a3b8', fontSize: 10 }}
            stroke="#475569"
            label={{ value: 'kW / m/s', angle: 90, position: 'insideRight', fill: '#94a3b8', fontSize: 10 }}
          />

          <Tooltip content={<CustomTooltip />} />

          <Area
            yAxisId="left"
            dataKey="radiacion_wm2"
            name="Irradiance"
            fill={CHART_COLORS.radiation || '#f97316'}
            fillOpacity={0.2}
            stroke={CHART_COLORS.radiation || '#f97316'}
            strokeWidth={2}
            type="monotone"
          />
          <Line
            yAxisId="right"
            dataKey="solar_kw"
            name="Solar kW"
            stroke={CHART_COLORS.solar}
            strokeWidth={2}
            dot={false}
            type="monotone"
          />
          <Line
            yAxisId="right"
            dataKey="wind_ms"
            name="Wind"
            stroke={CHART_COLORS.wind}
            strokeWidth={2}
            dot={false}
            type="monotone"
          />
          <Bar
            yAxisId="right"
            dataKey="rain_mm"
            name="Rain"
            fill={CHART_COLORS.rain}
            fillOpacity={0.6}
            barSize={4}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
