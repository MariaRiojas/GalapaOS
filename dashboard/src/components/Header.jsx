import { Zap } from 'lucide-react';
import { formatDate, formatTime } from '../utils/formatters';

export default function Header({ timestamp }) {
  return (
    <header className="flex items-center justify-between px-6 py-3 border-b border-slate-700">
      <div className="flex items-center gap-3">
        <Zap className="w-7 h-7 text-eco-green" />
        <div>
          <h1 className="text-xl font-bold tracking-tight">EcoDispatch</h1>
          <p className="text-xs text-slate-400">San Cristobal Island Microgrid</p>
        </div>
      </div>
      <div className="text-right">
        <p className="text-sm text-slate-300">{formatDate(timestamp)}</p>
        <p className="text-xs text-slate-500">{formatTime(timestamp)} | DEMO MODE</p>
      </div>
    </header>
  );
}
