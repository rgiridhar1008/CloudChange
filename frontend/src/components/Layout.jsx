import React, { useState, useEffect } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { LayoutDashboard, Network, ShieldAlert, Rocket, Activity, GitCompare, History, Settings, Bell, Sun, Moon } from 'lucide-react';
import { cn } from '../utils/cn';
import { ToastProvider } from './Toast';
import { api } from '../services/api';

const navigation = [
  { name: 'Overview', to: '/', icon: LayoutDashboard },
  { name: 'Change Analysis', to: '/change', icon: GitCompare },
  { name: 'Dependency Graph', to: '/graph', icon: Network },
  { name: 'Risk Analysis', to: '/risk', icon: ShieldAlert },
  { name: 'Deployment', to: '/deployment', icon: Rocket },
  { name: 'Monitoring', to: '/monitoring', icon: Activity },
  { name: 'History', to: '/history', icon: History },
];

export const Layout = () => {
  const [theme, setTheme] = useState(localStorage.getItem('cloudchange-theme') || 'dark');
  const [clusterHealth, setClusterHealth] = useState({ status: 'HEALTHY', cluster: 'minikube' });

  useEffect(() => {
    let active = true;
    const fetchCluster = async () => {
      try {
        const data = await api.getClusterHealth();
        if (active && data) {
          setClusterHealth(data);
        }
      } catch (e) {
        // keep previous state
      }
    };
    fetchCluster();
    const interval = setInterval(fetchCluster, 8000);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    const root = window.document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem('cloudchange-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  return (
    <div className="flex h-screen bg-background text-text-primary font-sans selection:bg-blue-500/30 transition-colors duration-300">
      {/* Sidebar */}
      <div className="w-64 bg-surface-secondary border-r border-border flex flex-col shadow-2xl z-20 relative transition-colors duration-300">
        <div className="h-16 flex items-center px-6 border-b border-border bg-surface-secondary transition-colors duration-300">
          <div className="flex items-center space-x-3 text-blue-500">
            <img src="/logo.png" alt="CloudChange Logo" className="h-12 w-auto object-contain drop-shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
            <span className="text-xl font-bold tracking-tight text-text-primary">CloudChange</span>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto py-6 px-3 flex flex-col justify-between">
          <nav className="space-y-1">
            <div className="px-3 mb-2 text-xs font-semibold text-text-secondary uppercase tracking-wider">
              Main Menu
            </div>
            {navigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.to}
                className={({ isActive }) => cn(
                  "group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-all duration-200 relative overflow-hidden",
                  isActive 
                    ? "text-primary bg-primary/10 shadow-[inset_2px_0_0_0_var(--primary)]" 
                    : "text-text-secondary hover:bg-surface/50 hover:text-text-primary"
                )}
              >
                <item.icon 
                  className={cn(
                    "mr-3 flex-shrink-0 h-[18px] w-[18px] transition-colors",
                    "text-current"
                  )} 
                  aria-hidden="true" 
                />
                {item.name}
              </NavLink>
            ))}
          </nav>

          <div className="mt-8 px-3">
            <div className="p-4 rounded-lg bg-surface border border-border">
              <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2">Environment</h4>
              <div className="flex items-center space-x-2 text-sm text-text-primary">
                <div className={cn("w-2 h-2 rounded-full", clusterHealth.status === 'HEALTHY' ? "bg-success animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.6)]" : "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]")}></div>
                <span className="font-medium capitalize">{clusterHealth.cluster || 'Minikube'}</span>
              </div>
              <p className="text-xs text-text-secondary mt-1 pl-4">Status: {clusterHealth.status === 'HEALTHY' ? 'Connected' : clusterHealth.status}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
        {/* Subtle background noise/grid */}
        <div className="absolute inset-0 pointer-events-none opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(currentColor 1px, transparent 1px)', backgroundSize: '32px 32px' }}></div>
        
        <header className="h-16 bg-background/80 backdrop-blur-md border-b border-border flex items-center justify-between px-8 z-10 sticky top-0 shadow-sm transition-colors duration-300">
          <div className="flex items-center">
            <h1 className="text-lg font-semibold text-text-primary">Control Center</h1>
          </div>
          <div className="flex items-center space-x-5 text-sm text-text-secondary">
            <button 
              onClick={toggleTheme} 
              className="hover:text-primary transition-colors flex items-center justify-center p-2 rounded-full hover:bg-surface" 
              title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
            >
              {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
            </button>
            <button className="hover:text-primary transition-colors"><Bell size={18} /></button>
            <button className="hover:text-primary transition-colors"><Settings size={18} /></button>
            <div className="h-4 w-px bg-border"></div>
            <div className="flex items-center bg-surface px-3 py-1.5 rounded-full border border-border shadow-sm">
              <span className={cn("w-2 h-2 rounded-full mr-2", clusterHealth.status === 'HEALTHY' ? "bg-success shadow-[0_0_5px_rgba(16,185,129,0.5)]" : "bg-red-500 shadow-[0_0_5px_rgba(239,68,68,0.5)]")}></span> 
              <span className="text-text-secondary font-medium text-xs uppercase tracking-wide">Cluster {clusterHealth.status === 'HEALTHY' ? 'Healthy' : 'Disconnected'}</span>
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-8 relative z-0">
          <div className="max-w-[1600px] mx-auto">
            <Outlet />
          </div>
        </main>
        
        <ToastProvider />
      </div>
    </div>
  );
};
