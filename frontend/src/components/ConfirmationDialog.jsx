import React from 'react';
import { AlertTriangle, X } from 'lucide-react';

export const ConfirmationDialog = ({ isOpen, title, message, onConfirm, onCancel, confirmText = "Confirm", cancelText = "Cancel", isDestructive = false }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-surface border border-border rounded-xl shadow-2xl w-full max-w-md overflow-hidden flex flex-col scale-in-95 duration-200">
        <div className="flex justify-between items-center p-5 border-b border-border/50">
          <div className="flex items-center space-x-3">
            {isDestructive ? (
              <div className="p-2 bg-red-500/10 rounded-full">
                <AlertTriangle className="text-red-500 w-5 h-5" />
              </div>
            ) : null}
            <h3 className="text-lg font-semibold text-text-primary">{title}</h3>
          </div>
          <button onClick={onCancel} className="text-text-secondary hover:text-gray-200 transition-colors">
            <X size={20} />
          </button>
        </div>
        <div className="p-5 text-gray-300 text-sm leading-relaxed">
          {message}
        </div>
        <div className="p-5 bg-background border-t border-border/50 flex justify-end space-x-3">
          <button 
            onClick={onCancel}
            className="px-4 py-2 rounded-lg text-sm font-medium text-gray-300 hover:text-text-primary hover:bg-gray-800 transition-colors"
          >
            {cancelText}
          </button>
          <button 
            onClick={onConfirm}
            className={`px-4 py-2 rounded-lg text-sm font-medium text-text-primary transition-colors shadow-lg ${
              isDestructive 
                ? 'bg-red-600 hover:bg-red-700 shadow-red-900/20' 
                : 'bg-blue-600 hover:bg-blue-700 shadow-blue-900/20'
            }`}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
};
