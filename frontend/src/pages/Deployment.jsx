import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/Card';
import { api } from '../services/api';
import { Play, Pause, FastForward, RotateCcw, AlertTriangle, Terminal, Rocket, CheckCircle2 } from 'lucide-react';
import { cn } from '../utils/cn';
import { ConfirmationDialog } from '../components/ConfirmationDialog';
import { StatusBadge } from '../components/StatusBadge';
import { toast } from '../components/Toast';

export const Deployment = () => {
  const [serviceName, setServiceName] = useState('payment-service');
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showRollbackConfirm, setShowRollbackConfirm] = useState(false);
  const [showPromoteConfirm, setShowPromoteConfirm] = useState(false);

  const fetchStatus = async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const res = await api.getDeploymentStatus(serviceName);
      setStatus(res);
    } catch (e) {
      console.error(e);
      if (!silent) toast("Failed to fetch deployment status", "error");
    }
    if (!silent) setLoading(false);
  };

  // Poll status while deployment is in progress
  useEffect(() => {
    let interval;
    if (status?.status === 'IN_PROGRESS' || status?.status === 'PAUSED') {
      interval = setInterval(() => fetchStatus(true), 3000);
    }
    return () => clearInterval(interval);
  }, [status?.status, serviceName]);

  const handleStart = async () => {
    setLoading(true);
    try {
      const res = await api.startDeployment(serviceName, 'v2.0');
      setStatus(res);
      toast("Canary deployment initiated", "info");
    } catch (e) { toast("Failed to start deployment", "error"); }
    setLoading(false);
  };

  const handlePromote = async () => {
    setShowPromoteConfirm(false);
    setLoading(true);
    try {
      const res = await api.promoteDeployment(serviceName);
      setStatus(res);
      toast("Deployment promoted to 100%", "success");
    } catch (e) { toast("Failed to promote deployment", "error"); }
    setLoading(false);
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      const res = await api.stopDeployment(serviceName);
      setStatus(res);
      toast("Deployment paused", "info");
    } catch (e) { toast("Failed to pause deployment", "error"); }
    setLoading(false);
  };

  const handleRollback = async () => {
    setShowRollbackConfirm(false);
    setLoading(true);
    try {
      const res = await api.rollbackDeployment(serviceName);
      setStatus({
        service_name: serviceName,
        status: res.status || 'ROLLED_BACK',
        current_percentage: 0,
        health_status: 'UNKNOWN',
        message: res.message
      });
      toast("Rollback executed successfully", "error");
    } catch (e) { toast("Rollback failed", "error"); }
    setLoading(false);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-12">
      <ConfirmationDialog 
        isOpen={showRollbackConfirm}
        title="Force Rollback?"
        message={`Are you sure you want to rollback ${serviceName} to the previous stable version? All traffic will be immediately shifted back to v1. This action cannot be undone.`}
        isDestructive={true}
        confirmText="Execute Rollback"
        onConfirm={handleRollback}
        onCancel={() => setShowRollbackConfirm(false)}
      />
      <ConfirmationDialog 
        isOpen={showPromoteConfirm}
        title="Promote Canary to Stable?"
        message={`This will bypass any remaining canary steps and shift 100% of traffic to the new version of ${serviceName}.`}
        confirmText="Promote to 100%"
        onConfirm={handlePromote}
        onCancel={() => setShowPromoteConfirm(false)}
      />

      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-text-primary mb-2">Canary Deployment Engine</h2>
          <p className="text-text-secondary">Control active rollouts, monitor traffic distribution, and manage risk.</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="relative">
            <input 
              type="text" 
              value={serviceName}
              onChange={(e) => setServiceName(e.target.value)}
              className="bg-black/50 border border-border rounded-lg pl-10 pr-4 py-2 text-text-primary text-sm focus:outline-none focus:border-blue-500 w-64"
              placeholder="Service Name"
            />
            <Terminal size={16} className="absolute left-3 top-2.5 text-gray-500" />
          </div>
          <button 
            onClick={() => fetchStatus(false)} 
            className="px-6 py-2 bg-gray-800 hover:bg-gray-700 text-text-primary rounded-lg text-sm font-medium transition-colors"
          >
            Connect
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        <div className="xl:col-span-8 space-y-6">
          <Card className="bg-surface border-border shadow-xl overflow-hidden">
            <CardHeader className="border-b border-border/50 bg-surface-secondary py-4">
              <div className="flex justify-between items-center">
                <CardTitle>Traffic Distribution</CardTitle>
                <div className="flex space-x-2">
                  <StatusBadge status={status?.status || 'NOT CONNECTED'} />
                  {status?.health_status && <StatusBadge status={status.health_status} className="bg-transparent" />}
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-10 pb-12 px-10">
              <div className="relative w-full h-16 bg-gray-900 rounded-2xl overflow-hidden flex border border-border shadow-inner">
                {/* Old Version */}
                <div 
                  className="h-full bg-slate-800 flex items-center px-6 transition-all duration-1000 ease-in-out relative overflow-hidden group"
                  style={{ width: `${status?.traffic?.stable ?? (100 - (status?.current_percentage || 0))}%` }}
                >
                  <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-20 mix-blend-overlay"></div>
                  <span className="text-xl font-bold text-slate-300 z-10 whitespace-nowrap">v1.0 (Stable)</span>
                  <span className="absolute right-6 text-3xl font-black text-slate-700/50 group-hover:text-slate-600 transition-colors z-10">
                    {status?.traffic?.stable ?? (100 - (status?.current_percentage || 0))}%
                  </span>
                </div>
                
                {/* New Version */}
                <div 
                  className="h-full bg-blue-600 flex items-center justify-end px-6 transition-all duration-1000 ease-in-out relative overflow-hidden group shadow-[inset_4px_0_15px_rgba(0,0,0,0.3)]"
                  style={{ width: `${status?.traffic?.canary ?? (status?.current_percentage || 0)}%` }}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-blue-600"></div>
                  <div className="absolute inset-0 opacity-30" style={{ backgroundImage: 'linear-gradient(45deg, rgba(255,255,255,.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,.15) 50%, rgba(255,255,255,.15) 75%, transparent 75%, transparent)', backgroundSize: '40px 40px', animation: 'stripes 2s linear infinite' }}></div>
                  <style>{`@keyframes stripes { from { background-position: 40px 0; } to { background-position: 0 0; } }`}</style>
                  
                  <span className="absolute left-6 text-3xl font-black text-blue-900/40 group-hover:text-blue-900/60 transition-colors z-10">
                    {status?.traffic?.canary ?? (status?.current_percentage || 0)}%
                  </span>
                  <span className="text-xl font-bold text-text-primary z-10 whitespace-nowrap drop-shadow-md">v2.0 (Canary)</span>
                </div>
              </div>

              {/* Traffic Ruler */}
              <div className="flex justify-between mt-4 px-2 text-xs font-bold text-gray-600">
                <span>0%</span>
                <span>25%</span>
                <span>50%</span>
                <span>75%</span>
                <span>100%</span>
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button 
              onClick={handleStart} 
              disabled={loading || status?.status === 'IN_PROGRESS' || status?.status === 'SUCCESS'} 
              className="flex flex-col justify-center items-center p-6 bg-surface hover:bg-gray-800 border border-border rounded-xl text-text-primary transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
            >
              <div className="w-12 h-12 rounded-full bg-blue-500/10 flex items-center justify-center mb-3 group-hover:bg-blue-500/20 transition-colors">
                <Play className="text-blue-500 fill-current" size={20} />
              </div>
              <span className="font-semibold text-sm">Start Canary</span>
            </button>
            <button 
              onClick={handleStop} 
              disabled={loading || status?.status !== 'IN_PROGRESS'} 
              className="flex flex-col justify-center items-center p-6 bg-surface hover:bg-gray-800 border border-border rounded-xl text-text-primary transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
            >
              <div className="w-12 h-12 rounded-full bg-yellow-500/10 flex items-center justify-center mb-3 group-hover:bg-yellow-500/20 transition-colors">
                <Pause className="text-yellow-500 fill-current" size={20} />
              </div>
              <span className="font-semibold text-sm">Pause Rollout</span>
            </button>
            <button 
              onClick={() => setShowPromoteConfirm(true)} 
              disabled={loading || (status?.status !== 'IN_PROGRESS' && status?.status !== 'PAUSED')} 
              className="flex flex-col justify-center items-center p-6 bg-surface hover:bg-gray-800 border border-border rounded-xl text-text-primary transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
            >
              <div className="w-12 h-12 rounded-full bg-green-500/10 flex items-center justify-center mb-3 group-hover:bg-green-500/20 transition-colors">
                <FastForward className="text-green-500 fill-current" size={20} />
              </div>
              <span className="font-semibold text-sm">Force Promote</span>
            </button>
            <button 
              onClick={() => setShowRollbackConfirm(true)} 
              disabled={loading || !status || status?.status === 'ROLLED_BACK'} 
              className="flex flex-col justify-center items-center p-6 bg-surface hover:bg-gray-800 border border-border rounded-xl text-text-primary transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
            >
              <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center mb-3 group-hover:bg-red-500/20 transition-colors">
                <RotateCcw className="text-red-500" size={20} />
              </div>
              <span className="font-semibold text-sm">Abort & Rollback</span>
            </button>
          </div>
        </div>

        <div className="xl:col-span-4">
          <Card className="bg-surface border-border shadow-xl h-full flex flex-col">
            <CardHeader className="border-b border-border/50 bg-surface-secondary py-4">
              <CardTitle>Event Timeline</CardTitle>
            </CardHeader>
            <CardContent className="pt-6 flex-1 bg-black/20">
              {status ? (
                <div className="space-y-6 relative before:absolute before:inset-0 before:ml-4 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gray-800">
                  {status.events && status.events.length > 0 ? (
                    [...status.events].reverse().map((ev, i) => (
                      <div key={i} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                        <div className={`flex items-center justify-center w-8 h-8 rounded-full border-4 border-[#111111] ${ev.status === 'SUCCESS' ? 'bg-green-500' : ev.status === 'FAILED' ? 'bg-red-500' : 'bg-yellow-500'} text-text-primary shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2`}>
                          {ev.status === 'SUCCESS' ? <CheckCircle2 size={12} /> : ev.status === 'FAILED' ? <AlertTriangle size={12} /> : <Terminal size={12} />}
                        </div>
                        <div className="w-[calc(100%-3rem)] md:w-[calc(50%-2rem)] p-4 rounded-xl bg-gray-900 border border-border shadow">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-bold text-gray-200 text-sm">{ev.event}</span>
                            <span className="text-[10px] text-gray-500">{new Date(ev.timestamp).toLocaleTimeString()}</span>
                          </div>
                          <p className="text-xs text-text-secondary font-mono leading-relaxed break-words">{ev.status}</p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full border-4 border-[#111111] bg-blue-500 text-text-primary shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                        <Rocket size={12} />
                      </div>
                      <div className="w-[calc(100%-3rem)] md:w-[calc(50%-2rem)] p-4 rounded-xl bg-gray-900 border border-border shadow">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-bold text-gray-200 text-sm">Deployment Updated</span>
                        </div>
                        <p className="text-xs text-text-secondary font-mono leading-relaxed break-words">{status.message || "Status synced from cluster."}</p>
                      </div>
                    </div>
                  )}

                  {status.status === 'ROLLED_BACK' && (
                    <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full border-4 border-[#111111] bg-red-500 text-text-primary shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                        <RotateCcw size={12} />
                      </div>
                      <div className="w-[calc(100%-3rem)] md:w-[calc(50%-2rem)] p-4 rounded-xl bg-red-900/20 border border-red-900/50 shadow">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-bold text-red-400 text-sm">Rolled Back</span>
                        </div>
                        <p className="text-xs text-red-400/80">Traffic reverted to v1.0. Deployment aborted.</p>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-500">
                  <Terminal size={32} className="mb-3 text-gray-700" />
                  <p className="text-sm">Connect to a service to view timeline</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
