import { useState, useEffect, useMemo } from 'react';

// --- RDI based solely on solar radiation ---
const DEMAND_AVG_KW = 800;
const SOLAR_CONVERSION = 0.0008; // W/m² → kW
const RDI_GREEN = 1.0;
const RDI_YELLOW = 0.6;

function radiacionToSolarKw(wm2) {
  return wm2 * SOLAR_CONVERSION;
}

function computeRdi(solarKw) {
  const renewable = solarKw * 1000; // solar only — no wind data available
  return Math.min(renewable / DEMAND_AVG_KW, 2.0);
}

function rdiToSemaphore(rdi) {
  if (rdi > RDI_GREEN) return { color: 'green', label: 'SURPLUS', action: 'Diesel OFF -- safe on renewables' };
  if (rdi > RDI_YELLOW) return { color: 'yellow', label: 'WATCH', action: 'Diesel STANDBY -- ramp approaching' };
  return { color: 'red', label: 'DEFICIT', action: 'Diesel ON -- renewables insufficient' };
}

// --- Transform raw radiacion_solar API data ---
function transformRadiacion(raw) {
  const sorted = [...raw].sort((a, b) => a.fecha.localeCompare(b.fecha));

  const timesteps = [];
  const rdiValues = [];

  for (const entry of sorted) {
    const vars = entry.variables_predictoras;
    const hist = [...entry.historico].sort((a, b) => a.timestamp - b.timestamp);
    const currentRad = hist.length > 0 ? hist[hist.length - 1].radiacion : 0;

    const solarKw = radiacionToSolarKw(currentRad);
    const rdi = computeRdi(solarKw);
    const sem = rdiToSemaphore(rdi);

    let solarRampProb = 0;
    if (hist.length >= 3) {
      const recent = hist.slice(-3).map(h => h.radiacion);
      if (recent[0] > 10) {
        const drop = (recent[2] - recent[0]) / Math.max(recent[0], 1);
        solarRampProb = Math.min(1, Math.max(0, -drop));
      }
    }

    timesteps.push({
      time: entry.fecha.replace('Z', ''),
      radiacion_wm2: +currentRad.toFixed(1),
      solar_kw: +solarKw.toFixed(3),
      rdi: +rdi.toFixed(2),
      color: sem.color,
      solar_ramp_prob: +solarRampProb.toFixed(3),
      kt: vars.indice_claridad || 0,
      temp_c: vars.temperatura_actual,
      humidity_pct: vars.humedad,
      cloud_cover_pct: vars.nubosidad,
      pressure_hpa: vars.presion_atmosferica,
      historico: hist,
      predicciones: entry.predicciones,
    });
    rdiValues.push(rdi);
  }

  // Add 6 prediction steps from last entry
  const last = sorted[sorted.length - 1];
  if (last?.predicciones) {
    const lastDate = new Date(last.fecha);
    const lastVars = last.variables_predictoras;
    for (let i = 1; i <= 6; i++) {
      const predRad = last.predicciones[`prediccion_${i}`];
      if (predRad == null) continue;
      const predTime = new Date(lastDate.getTime() + i * 3600000);
      const predSolarKw = radiacionToSolarKw(predRad);
      const predRdi = computeRdi(predSolarKw);
      const predSem = rdiToSemaphore(predRdi);

      timesteps.push({
        time: predTime.toISOString().replace('Z', '').split('.')[0],
        radiacion_wm2: +predRad.toFixed(1),
        solar_kw: +predSolarKw.toFixed(3),
        rdi: +predRdi.toFixed(2),
        color: predSem.color,
        solar_ramp_prob: 0,
        kt: lastVars.indice_claridad || 0,
        temp_c: lastVars.temperatura_actual,
        humidity_pct: lastVars.humedad,
        cloud_cover_pct: lastVars.nubosidad,
        pressure_hpa: lastVars.presion_atmosferica,
        is_forecast: true,
      });
      rdiValues.push(predRdi);
    }
  }

  timesteps.sort((a, b) => a.time.localeCompare(b.time));

  // Action trigger
  let actionTrigger = '';
  let nextTransition = null;
  for (let i = 1; i < timesteps.length; i++) {
    if (timesteps[i].color !== timesteps[0].color) {
      const t = timesteps[i].time.split('T')[1]?.slice(0, 5) || '';
      const col = timesteps[i].color;
      nextTransition = `${col.charAt(0).toUpperCase() + col.slice(1)} at ${t}`;
      if (col === 'green') actionTrigger = `Surplus Expected. Power down Generator #2 at ${t}.`;
      else if (col === 'red') actionTrigger = `Deficit Expected. Start Generator #2 at ${t}.`;
      else actionTrigger = `Ramp approaching. Standby Generator #2 by ${t}.`;
      break;
    }
  }
  if (!actionTrigger) {
    const s = rdiToSemaphore(rdiValues[0] || 0);
    actionTrigger = `${s.label}. No transitions expected in next ${timesteps.length}h.`;
  }

  // Alerts — only solar ramp (real data)
  const alerts = buildAlerts(timesteps);

  // Current: closest to now
  const nowIso = new Date().toISOString().replace('Z', '');
  let currentIdx = 0;
  for (let i = 0; i < timesteps.length; i++) {
    if (timesteps[i].time <= nowIso) currentIdx = i;
  }
  const current = timesteps[currentIdx] || timesteps[0];
  const currentSem = rdiToSemaphore(current.rdi);

  return {
    generated_at: timesteps[0]?.time || '',
    target_station: 'san_cristobal',
    current_rdi: current.rdi,
    current_color: current.color,
    current_action: `${currentSem.label} -- ${currentSem.action}`,
    action_trigger: actionTrigger,
    next_transition: nextTransition,
    timesteps,
    alerts,
  };
}

function buildAlerts(timesteps) {
  const alerts = [];
  // Solar ramp detection — the only real signal we have
  for (let i = 2; i < timesteps.length; i++) {
    const prev = timesteps[i - 2].radiacion_wm2;
    const curr = timesteps[i].radiacion_wm2;
    if (prev > 100 && curr < prev * 0.5) {
      alerts.push({
        severity: 'warning',
        station: 'San Cristóbal',
        event: `Solar ramp detected: ${prev.toFixed(0)} → ${curr.toFixed(0)} W/m²`,
      });
    }
  }
  // Low clarity index warning
  const lowKt = timesteps.find(t => !t.is_forecast && t.kt > 0 && t.kt < 0.3);
  if (lowKt) {
    alerts.push({
      severity: 'info',
      station: 'San Cristóbal',
      event: `Low clarity index (kt=${lowKt.kt}) at ${lowKt.time.split('T')[1]?.slice(0, 5)}`,
    });
  }
  return alerts;
}

// --- Hooks ---

function useJsonData(path) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(path)
      .then(r => {
        if (!r.ok) throw new Error(`Failed to load ${path}`);
        return r.json();
      })
      .then(setData)
      .catch(setError);
  }, [path]);

  return { data, error };
}

export function useForecast() {
  const { data: raw, error } = useJsonData('/data/radiacion_solar.json');

  const forecast = useMemo(() => {
    if (!raw) return null;
    return transformRadiacion(raw);
  }, [raw]);

  return { data: forecast, error };
}

export function useModelInfo() {
  return useJsonData('/data/model_info.json');
}
