import { ArrowRight } from 'lucide-react';
import StationCard from './StationCard';
import TransectProfile from './TransectProfile';

export default function StationCards({ stations, transect }) {
  if (!stations?.length) return null;

  const sorted = [...stations].sort((a, b) => a.order - b.order);

  return (
    <div className="bg-eco-card rounded-xl p-4">
      <h3 className="text-sm font-semibold text-slate-300 mb-3">
        Station Transect
        <span className="text-[10px] text-slate-500 ml-2 font-normal">coast &rarr; summit</span>
      </h3>
      <div className="flex gap-2 items-stretch">
        {sorted.map((s, i) => (
          <div key={s.id} className="flex items-stretch gap-2 flex-1">
            <StationCard station={s} />
            {i < sorted.length - 1 && (
              <div className="flex items-center">
                <ArrowRight className="w-3 h-3 text-slate-600" />
              </div>
            )}
          </div>
        ))}
      </div>
      <TransectProfile stations={sorted} transect={transect} />
    </div>
  );
}
