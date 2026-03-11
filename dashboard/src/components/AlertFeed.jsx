import { AlertTriangle, Info, CheckCircle } from 'lucide-react';

export default function AlertFeed({ alerts }) {
  return (
    <div className="bg-eco-card rounded-lg border border-slate-700 p-3 sm:p-4 flex-1">
      <h3 className="text-[10px] sm:text-[11px] text-slate-400 uppercase tracking-wider font-medium mb-2 sm:mb-3">Alert Feed</h3>

      {(!alerts || alerts.length === 0) ? (
        <div className="flex items-center gap-2 text-eco-green bg-green-900/20 rounded-md p-2 sm:p-3">
          <CheckCircle className="w-3.5 h-3.5 sm:w-4 sm:h-4 flex-shrink-0" />
          <span className="text-[11px] sm:text-xs">All clear -- no anomalies detected</span>
        </div>
      ) : (
        <div className="space-y-1.5 sm:space-y-2">
          {alerts.map((a, i) => {
            const isWarning = a.severity === 'warning';
            const Icon = isWarning ? AlertTriangle : Info;
            return (
              <div
                key={i}
                className={`flex items-start gap-1.5 sm:gap-2 px-2 sm:px-3 py-1.5 sm:py-2 rounded-md text-[11px] sm:text-xs ${
                  isWarning ? 'bg-yellow-900/20 border border-eco-yellow/30' : 'bg-blue-900/20 border border-blue-500/30'
                }`}
              >
                <Icon className={`w-3 h-3 sm:w-3.5 sm:h-3.5 mt-0.5 flex-shrink-0 ${isWarning ? 'text-eco-yellow' : 'text-eco-wind'}`} />
                <div className="min-w-0">
                  <span className={`font-medium ${isWarning ? 'text-eco-yellow' : 'text-eco-wind'}`}>
                    {isWarning ? 'Warning' : 'Info'}
                  </span>
                  <span className="text-slate-300 ml-1">{a.event}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
