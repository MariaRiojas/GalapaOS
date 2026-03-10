import { getKtColor } from '../utils/colors';
import { STATION_DISTANCES } from '../utils/constants';

export default function TransectProfile({ stations, transect }) {
  if (!stations?.length) return null;

  const width = 500;
  const height = 80;
  const padX = 30;
  const padY = 15;

  const maxDist = 14.1;
  const maxElev = 800;

  const scaleX = (d) => padX + (d / maxDist) * (width - 2 * padX);
  const scaleY = (e) => height - padY - (e / maxElev) * (height - 2 * padY);

  const points = stations.map(s => ({
    x: scaleX(STATION_DISTANCES[s.id] || 0),
    y: scaleY(s.elevation_m),
    ...s,
  }));

  // Terrain line
  const terrainPath = `M ${padX} ${scaleY(0)} ` +
    points.map(p => `L ${p.x} ${p.y}`).join(' ') +
    ` L ${width - padX} ${scaleY(0)}`;

  return (
    <div className="mt-3">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full" style={{ maxHeight: 80 }}>
        {/* Terrain fill */}
        <path d={terrainPath} fill="#1e293b" stroke="#475569" strokeWidth="1" />

        {/* Station dots */}
        {points.map(p => (
          <g key={p.id}>
            <circle
              cx={p.x}
              cy={p.y}
              r={6}
              fill={getKtColor(p.kt)}
              stroke="#0f172a"
              strokeWidth={2}
            />
            <text
              x={p.x}
              y={p.y - 10}
              textAnchor="middle"
              fill="#94a3b8"
              fontSize="7"
            >
              {p.elevation_m}m
            </text>
          </g>
        ))}

        {/* Propagation arrow */}
        {transect?.propagation_lag_mira_jun_min && (
          <g>
            <line
              x1={points[0]?.x + 8}
              y1={points[0]?.y}
              x2={points[points.length - 1]?.x - 8}
              y2={points[points.length - 1]?.y}
              stroke="#38bdf8"
              strokeWidth={1}
              strokeDasharray="3 2"
              markerEnd="url(#arrow)"
            />
            <defs>
              <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5"
                markerWidth="4" markerHeight="4" orient="auto-start-auto">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8" />
              </marker>
            </defs>
            <text
              x={(points[0]?.x + points[points.length - 1]?.x) / 2}
              y={Math.min(points[0]?.y, points[points.length - 1]?.y) - 5}
              textAnchor="middle"
              fill="#38bdf8"
              fontSize="7"
            >
              {transect.propagation_lag_mira_jun_min} min lag
            </text>
          </g>
        )}

        {/* Axis labels */}
        <text x={padX} y={height - 2} fill="#64748b" fontSize="7">0 km</text>
        <text x={width - padX} y={height - 2} fill="#64748b" fontSize="7" textAnchor="end">14.1 km</text>
      </svg>
    </div>
  );
}
