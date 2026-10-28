import React from 'react';
import { cn } from '../utils/cn';

export const RiskMeter = ({ score }) => {
  const getRiskDetails = (s) => {
    if (s >= 75) return { label: 'CRITICAL', color: 'bg-red-500', text: 'text-red-500', shadow: 'shadow-red-500/50' };
    if (s >= 50) return { label: 'HIGH', color: 'bg-orange-500', text: 'text-orange-500', shadow: 'shadow-orange-500/50' };
    if (s >= 25) return { label: 'MEDIUM', color: 'bg-yellow-500', text: 'text-yellow-500', shadow: 'shadow-yellow-500/50' };
    return { label: 'LOW', color: 'bg-green-500', text: 'text-green-500', shadow: 'shadow-green-500/50' };
  };

  const { label, color, text, shadow } = getRiskDetails(score);

  return (
    <div className="w-full">
      <div className="flex justify-between items-end mb-2">
        <div className="flex flex-col">
          <span className="text-text-secondary text-sm font-medium uppercase tracking-wider mb-1">Calculated Risk</span>
          <div className="flex items-baseline space-x-2">
            <span className={cn("text-4xl font-bold tracking-tighter", text)}>{score}</span>
            <span className="text-gray-500 text-sm font-medium">/ 100</span>
          </div>
        </div>
        <span className={cn("px-3 py-1 rounded-full text-xs font-bold tracking-wider border", color.replace('bg-', 'border-').replace('500', '500/30'), color.replace('bg-', 'text-'), color.replace('bg-', 'bg-').replace('500', '500/10'))}>
          {label}
        </span>
      </div>
      
      <div className="relative h-2 w-full bg-gray-800 rounded-full overflow-hidden mt-4">
        {/* The background gradient representing the zones */}
        <div className="absolute inset-0 w-full h-full opacity-20" 
             style={{ background: 'linear-gradient(90deg, #22c55e 0%, #eab308 33%, #f97316 66%, #ef4444 100%)' }}
        />
        
        {/* The actual score bar */}
        <div 
          className={cn("absolute top-0 left-0 h-full rounded-full transition-all duration-1000 ease-out shadow-lg", color, shadow)}
          style={{ width: `${Math.max(2, score)}%` }}
        />
      </div>
      
      <div className="flex justify-between mt-2 text-[10px] font-semibold text-gray-500 uppercase tracking-widest">
        <span>Low</span>
        <span>Med</span>
        <span>High</span>
        <span>Crit</span>
      </div>
    </div>
  );
};
