import React, { useState, useEffect } from 'react';
import { CheckCircle2, AlertCircle, XCircle, X } from 'lucide-react';
import { cn } from '../utils/cn';

// Simple event bus for toasts
const listeners = new Set();
export const toast = (message, type = 'info') => {
  listeners.forEach(listener => listener({ id: Date.now(), message, type }));
};

export const ToastProvider = () => {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    const listener = (newToast) => {
      setToasts(prev => [...prev, newToast]);
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== newToast.id));
      }, 5000);
    };
    
    listeners.add(listener);
    return () => listeners.delete(listener);
  }, []);

  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col space-y-3 pointer-events-none">
      {toasts.map(t => (
        <div 
          key={t.id} 
          className="pointer-events-auto animate-in slide-in-from-right-8 fade-in duration-300 flex items-center p-4 bg-surface border border-border rounded-xl shadow-2xl min-w-[300px]"
        >
          {t.type === 'success' && <CheckCircle2 className="text-green-500 w-5 h-5 mr-3 shrink-0" />}
          {t.type === 'error' && <XCircle className="text-red-500 w-5 h-5 mr-3 shrink-0" />}
          {t.type === 'info' && <AlertCircle className="text-blue-500 w-5 h-5 mr-3 shrink-0" />}
          
          <p className="text-sm text-gray-200 flex-1 font-medium">{t.message}</p>
          
          <button onClick={() => removeToast(t.id)} className="ml-4 text-gray-500 hover:text-gray-300 transition-colors">
            <X size={16} />
          </button>
        </div>
      ))}
    </div>
  );
};
