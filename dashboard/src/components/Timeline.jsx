import {
  ComposedChart, Area, Line, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer,
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

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-xs shadow-lg">
      <p className="text-slate-300 font-medium mb-1">{formatTime(label)}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }}>
          {p.name}: {typeof p.value === 'number' ? p.value.toFixed(2) : p.value}
        </p>
      ))}
    </div>
  );
}

export default function Timeline({ timesteps }) {
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

  // Find approximate "now" (1/3 into the forecast)
  const nowIdx = Math.floor(data.length / 3);
  const nowTime = data[nowIdx]?.time;

  return (
    <div className="bg-eco-card rounded-xl p-4">
      <h3 className="text-sm font-semibold text-slate-300 mb-2 px-2">12-Hour Forecast</h3>
      <ResponsiveContainer width="100%" height={260}>
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
            tickFormatter={formatTime}
            tick={{ fill: '#94a3b8', fontSize: 10 }}
            interval={Math.floor(data.length / 6)}
            stroke="#475569"
          />
          <YAxis
            yAxisId="left"
            tick={{ fill: '#94a3b8', fontSize: 10 }}
            stroke="#475569"
            label={{ value: 'kW', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 10 }}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            tick={{ fill: '#94a3b8', fontSize: 10 }}
            stroke="#475569"
            label={{ value: 'm/s', angle: 90, position: 'insideRight', fill: '#94a3b8', fontSize: 10 }}
          />

          <Tooltip content={<CustomTooltip />} />

          <Area
            yAxisId="left"
            dataKey="solar_kw"
            name="Solar"
            fill={CHART_COLORS.solar}
            fillOpacity={0.3}
            stroke={CHART_COLORS.solar}
            strokeWidth={2}
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

          {nowTime && (
            <ReferenceLine
              x={nowTime}
              yAxisId="left"
              stroke="#e2e8f0"
              strokeDasharray="4 4"
              strokeWidth={1}
              label={{ value: 'NOW', fill: '#e2e8f0', fontSize: 10, position: 'top' }}
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
