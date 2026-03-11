import { Zap } from 'lucide-react';
import { formatDate, formatTime } from '../utils/formatters';

export default function Header({ timestamp }) {
  return (
    <header className="flex flex-col sm:flex-row items-start sm:items-center justify-between px-4 sm:px-6 py-3 bg-slate-900 border-b border-slate-700 gap-2">
      <div className="flex items-center gap-2 sm:gap-3 min-w-0">
        <Zap className="w-6 h-6 sm:w-7 sm:h-7 text-eco-green flex-shrink-0" />
        <div className="min-w-0">
          <h1 className="text-sm sm:text-lg font-bold tracking-tight truncate">
            SAN CRISTOBAL ISLAND
            <span className="hidden md:inline"> - MICROGRID STABILITY DASHBOARD</span>
          </h1>
          <p className="text-[10px] sm:text-xs text-slate-400 truncate">
            <span className="md:hidden">Microgrid Stability Dashboard | </span>
            AI EARLY WARNING SYSTEM
          </p>
        </div>
      </div>
      <div className="text-left sm:text-right flex-shrink-0 pl-8 sm:pl-0">
        <p className="text-xs sm:text-sm font-semibold text-slate-200">{formatDate(timestamp)}</p>
        <p className="text-[10px] sm:text-xs text-slate-500">{formatTime(timestamp)}</p>
      </div>
    </header>
  );
}
