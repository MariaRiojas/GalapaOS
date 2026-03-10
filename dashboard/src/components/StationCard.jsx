import { Wind, Droplets, Thermometer } from 'lucide-react';
import { getKtColor } from '../utils/colors';
import { formatNumber } from '../utils/formatters';

export default function StationCard({ station }) {
  const ktColor = getKtColor(station.kt);

  return (
    <div className="bg-slate-800/60 rounded-lg p-3 border border-slate-700 min-w-[140px] flex-1">
      <div className="flex items-center justify-between mb-2">
        <div>
          <p className="text-xs font-semibold text-slate-200">{station.name}</p>
          <p className="text-[10px] text-slate-500">{station.elevation_m}m | {station.zone}</p>
        </div>
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold"
          style={{
            backgroundColor: `${ktColor}20`,
            border: `2px solid ${ktColor}`,
            color: ktColor,
          }}
        >
          {formatNumber(station.kt, 1)}
        </div>
      </div>
      <div className="space-y-1">
        <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
          <Wind className="w-3 h-3 text-eco-wind" />
          <span>{formatNumber(station.wind_ms)} m/s</span>
        </div>
        <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
          <Thermometer className="w-3 h-3 text-orange-400" />
          <span>{formatNumber(station.temp_c)}C</span>
        </div>
        <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
          <Droplets className="w-3 h-3 text-eco-rain" />
          <span>{formatNumber(station.rain_mm, 2)} mm</span>
        </div>
        {station.inversion && (
          <p className="text-[10px] text-eco-yellow mt-1">Inversion active</p>
        )}
      </div>
    </div>
  );
}
