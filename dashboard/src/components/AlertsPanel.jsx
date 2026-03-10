import { AlertTriangle, Info, CheckCircle, Clock } from 'lucide-react';

function AlertCard({ alert }) {
  const isWarning = alert.severity === 'warning';
  const Icon = isWarning ? AlertTriangle : Info;
  const borderColor = isWarning ? 'border-eco-yellow' : 'border-slate-600';
  const iconColor = isWarning ? 'text-eco-yellow' : 'text-eco-wind';

  return (
    <div className={`border ${borderColor} rounded-lg p-3 mb-2 bg-slate-800/50`}>
      <div className="flex items-start gap-2">
        <Icon className={`w-4 h-4 mt-0.5 flex-shrink-0 ${iconColor}`} />
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-slate-200">{alert.station}</p>
          <p className="text-xs text-slate-400 mt-0.5">{alert.event}</p>
          <div className="flex items-center gap-3 mt-1.5">
            {alert.eta_min != null && (
              <span className="flex items-center gap-1 text-[10px] text-slate-500">
                <Clock className="w-3 h-3" />
                {alert.eta_min > 0 ? `ETA ${alert.eta_min} min` : 'Now'}
              </span>
            )}
            {alert.confidence != null && (
              <div className="flex items-center gap-1">
                <div className="w-12 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${alert.confidence * 100}%`,
                      backgroundColor: isWarning ? '#eab308' : '#38bdf8',
                    }}
                  />
                </div>
                <span className="text-[10px] text-slate-500">{Math.round(alert.confidence * 100)}%</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function AlertsPanel({ alerts }) {
  return (
    <div className="bg-eco-card rounded-xl p-4 h-full">
      <h3 className="text-sm font-semibold text-slate-300 mb-3">Cross-Station Alerts</h3>
      {!alerts || alerts.length === 0 ? (
        <div className="flex items-center gap-2 text-eco-green bg-green-900/20 rounded-lg p-3">
          <CheckCircle className="w-4 h-4" />
          <span className="text-xs">All clear -- no anomalies detected</span>
        </div>
      ) : (
        <div className="space-y-1">
          {alerts.map((a, i) => <AlertCard key={i} alert={a} />)}
        </div>
      )}
    </div>
  );
}
