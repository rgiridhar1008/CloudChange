import React from 'react';
import { cn } from '../utils/cn';
import { CheckCircle2, AlertCircle, XCircle, Loader2, Info } from 'lucide-react';

export const StatusBadge = ({ status, className }) => {
  const getProps = (s) => {
    switch (s?.toUpperCase()) {
      case 'SUCCESS':
      case 'HEALTHY':
        return { color: 'bg-green-500/10 text-green-400 border-green-500/20', icon: CheckCircle2 };
      case 'WARNING':
      case 'MEDIUM':
      case 'PAUSED':
        return { color: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20', icon: AlertCircle };
      case 'CRITICAL':
      case 'FAILED':
      case 'ROLLED_BACK':
      case 'ROLLBACK_FAILED':
      case 'UNHEALTHY':
        return { color: 'bg-red-500/10 text-red-400 border-red-500/20', icon: XCircle };
      case 'IN_PROGRESS':
        return { color: 'bg-blue-500/10 text-blue-400 border-blue-500/20', icon: Loader2, spin: true };
      default:
        return { color: 'bg-gray-500/10 text-text-secondary border-gray-500/20', icon: Info };
    }
  };

  const { color, icon: Icon, spin } = getProps(status);

  return (
    <span className={cn("inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border", color, className)}>
      <Icon className={cn("w-3.5 h-3.5 mr-1.5", spin && "animate-spin")} />
      {status || 'UNKNOWN'}
    </span>
  );
};
