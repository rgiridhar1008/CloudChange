import React from 'react';
import { cn } from '../utils/cn';

export const Card = ({ className, children, ...props }) => (
  <div className={cn("rounded-xl border border-border bg-gray-900/50 backdrop-blur-sm text-gray-100 shadow-xl overflow-hidden", className)} {...props}>
    {children}
  </div>
);

export const CardHeader = ({ className, children, ...props }) => (
  <div className={cn("flex flex-col space-y-1.5 p-6 border-b border-border", className)} {...props}>
    {children}
  </div>
);

export const CardTitle = ({ className, children, ...props }) => (
  <h3 className={cn("text-lg font-semibold leading-none tracking-tight", className)} {...props}>
    {children}
  </h3>
);

export const CardContent = ({ className, children, ...props }) => (
  <div className={cn("p-6 pt-4", className)} {...props}>
    {children}
  </div>
);
