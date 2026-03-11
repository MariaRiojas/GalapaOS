import { useState, useMemo } from 'react';
import { useForecast } from './data/useData';
import Header from './components/Header';
import KpiRow from './components/KpiRow';
import EnergyForecast from './components/EnergyForecast';
import TimeFilter from './components/TimeFilter';
import SolarConditions from './components/SolarConditions';
import AlertFeed from './components/AlertFeed';
import GridStatus from './components/GridStatus';

function filterTimesteps(timesteps, startDateTime, rangeHours) {
  if (!timesteps?.length || !startDateTime) return timesteps || [];
  const start = new Date(startDateTime).getTime();
  const end = start + rangeHours * 60 * 60 * 1000;
  return timesteps.filter(t => {
    const ts = new Date(t.time).getTime();
    return ts >= start && ts < end;
  });
}

export default function App() {
  const { data: forecast } = useForecast();
  const [rangeHours, setRangeHours] = useState(24);
  const [selectedDateTime, setSelectedDateTime] = useState(null);

  // Default to first available timestep
  const defaultDateTime = useMemo(() => {
    if (!forecast?.timesteps?.length) return null;
    return forecast.timesteps[0].time;
  }, [forecast]);

  const activeDateTime = selectedDateTime || defaultDateTime;

  const filteredTimesteps = useMemo(() => {
    if (!forecast?.timesteps || !activeDateTime) return forecast?.timesteps || [];
    return filterTimesteps(forecast.timesteps, activeDateTime, rangeHours);
  }, [forecast, activeDateTime, rangeHours]);

  if (!forecast) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-eco-green border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Loading EcoDispatch...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header timestamp={forecast.generated_at} />
      <KpiRow forecast={forecast} />

      <main className="flex-1 p-3 sm:p-4 space-y-3 sm:space-y-4">
        <EnergyForecast
          forecast={forecast}
          timesteps={filteredTimesteps}
          filterBar={
            <TimeFilter
              timesteps={forecast.timesteps}
              selectedRange={rangeHours}
              onRangeChange={setRangeHours}
              selectedDateTime={activeDateTime}
              onDateTimeChange={setSelectedDateTime}
            />
          }
        />

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 sm:gap-4">
          <GridStatus forecast={forecast} />
          <SolarConditions forecast={forecast} />
          <AlertFeed alerts={forecast.alerts} />
        </div>
      </main>
    </div>
  );
}
