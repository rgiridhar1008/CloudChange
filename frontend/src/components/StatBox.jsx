import React from 'react';
import { Card, CardContent } from './Card';

export const StatBox = ({ title, value, subtitle, icon: Icon, colorClass = "text-blue-500" }) => {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between space-x-4">
          <div className="flex flex-col">
            <span className="text-sm font-medium text-text-secondary">{title}</span>
            <span className="text-2xl font-bold mt-1 text-text-primary">{value}</span>
            {subtitle && (
              <span className="text-xs text-gray-500 mt-1">{subtitle}</span>
            )}
          </div>
          {Icon && (
            <div className={`p-3 rounded-full bg-gray-800/50 ${colorClass}`}>
              <Icon size={24} />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
