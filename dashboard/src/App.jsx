import Header from './components/Header';
import ActionTrigger from './components/ActionTrigger';
import Semaphore from './components/Semaphore';
import Timeline from './components/Timeline';
import AlertsPanel from './components/AlertsPanel';
import StationCards from './components/StationCards';
import ModelInfo from './components/ModelInfo';
import { useForecast, useStations, useModelInfo } from './data/useData';

export default function App() {
  const { data: forecast } = useForecast();
  const { data: stationsData } = useStations();
  const { data: modelInfo } = useModelInfo();

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

  const semaphore = {
    rdi: forecast.current_rdi,
    color: forecast.current_color,
    label: forecast.current_color === 'green' ? 'SURPLUS'
         : forecast.current_color === 'red' ? 'DEFICIT' : 'WATCH',
    action: forecast.current_action,
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header timestamp={forecast.generated_at} />

      <ActionTrigger
        color={forecast.current_color}
        message={forecast.action_trigger}
        nextTransition={forecast.next_transition}
      />

      <main className="flex-1 p-4 grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Left column: Semaphore + Alerts */}
        <div className="lg:col-span-1 flex flex-col gap-4">
          <Semaphore {...semaphore} />
          <AlertsPanel alerts={forecast.alerts} />
        </div>

        {/* Right column: Timeline + Stations */}
        <div className="lg:col-span-3 flex flex-col gap-4">
          <Timeline timesteps={forecast.timesteps} />
          {stationsData && (
            <StationCards
              stations={stationsData.stations}
              transect={stationsData.transect}
            />
          )}
        </div>
      </main>

      <ModelInfo info={modelInfo} />
    </div>
  );
}
