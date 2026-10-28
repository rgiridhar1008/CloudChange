import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/Card';
import { api } from '../services/api';
import { Activity, Cpu, HardDrive, Zap, RefreshCw, AlertTriangle, Terminal, Network, ShieldCheck } from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';
import { cn } from '../utils/cn';

const MetricCard = ({ title, value, unit, icon: Icon, color, trend = "stable" }) => (
  <Card className="bg-surface border-border shadow-xl overflow-hidden group">
    <CardContent className="p-6 relative">
      <div className={`absolute -right-6 -top-6 w-24 h-24 rounded-full ${color.replace('text-', 'bg-')}/5 group-hover:${color.replace('text-', 'bg-')}/10 transition-colors`}></div>
      <div className="flex justify-between items-start mb-4 relative z-10">
        <div className={`p-2.5 rounded-lg bg-gray-900 border border-border ${color}`}>
          <Icon size={20} />
        </div>
        {trend === 'up' && <span className="text-xs font-bold text-green-500 bg-green-500/10 px-2 py-1 rounded">↑</span>}
        {trend === 'down' && <span className="text-xs font-bold text-red-500 bg-red-500/10 px-2 py-1 rounded">↓</span>}
      </div>
      <div className="relative z-10">
        <h3 className="text-text-secondary text-xs font-bold uppercase tracking-wider mb-1">{title}</h3>
        <div className="flex items-baseline space-x-1">
          <span className="text-3xl font-bold text-text-primary tracking-tight">{value}</span>
          <span className="text-sm font-medium text-gray-500">{unit}</span>
        </div>
      </div>
    </CardContent>
  </Card>
);

export const Monitoring = () => {
  const [serviceName, setServiceName] = useState('payment-service');
  const [metrics, setMetrics] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchMetrics = async () => {
    setLoading(true);
    setError(null);
    try {
      const [m, h] = await Promise.all([
        api.getMetrics(serviceName),
        api.getHealth(serviceName)
      ]);
      setMetrics(m);
      setHealth(h);
    } catch (e) {
      console.error(e);
      let errorMsg = "Failed to fetch telemetry data. Ensure Prometheus is running.";
      if (e.response?.data?.detail) {
        errorMsg = typeof e.response.data.detail === 'string' ? e.response.data.detail : JSON.stringify(e.response.data.detail);
      } else if (e.message) {
        errorMsg = e.message;
      }
      setError(errorMsg);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchMetrics();
    // eslint-disable-next-line
  }, []);

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-12">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-text-primary mb-2">Live Observability</h2>
          <p className="text-text-secondary">Real-time metrics, health checks, and pod status.</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-start">
          <AlertTriangle className="text-red-400 mt-0.5 mr-3 flex-shrink-0" size={20} />
          <div className="flex-1">
            <h3 className="text-red-400 font-medium text-sm mb-1">Telemetry Fetch Failed</h3>
            <p className="text-red-300/80 text-sm">{error}</p>
          </div>
          <button onClick={() => setError(null)} className="text-red-400/50 hover:text-red-400 transition-colors ml-4">×</button>
        </div>
      )}

      <Card className="bg-surface border-border shadow-xl">
        <CardContent className="p-4 flex items-center space-x-4">
          <div className="relative flex-1 max-w-sm">
            <input 
              type="text" 
              value={serviceName}
              onChange={(e) => setServiceName(e.target.value)}
              className="w-full bg-black/50 border border-border rounded-lg pl-10 pr-4 py-2 text-text-primary text-sm focus:outline-none focus:border-blue-500 transition-colors"
              placeholder="Target Service (e.g. payment-service)"
            />
            <Terminal size={16} className="absolute left-3 top-2.5 text-gray-500" />
          </div>
          <button 
            onClick={fetchMetrics} 
            disabled={loading} 
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-text-primary rounded-lg text-sm font-medium transition-colors flex items-center disabled:opacity-50"
          >
            <RefreshCw size={16} className={cn("mr-2", loading && "animate-spin")} /> 
            Sync Telemetry
          </button>
        </CardContent>
      </Card>

      {health && (
        <div className={cn(
          "p-6 rounded-xl border flex items-start space-x-4 shadow-xl",
          health.health_status === 'HEALTHY' ? 'bg-green-900/10 border-green-900/50' : 'bg-red-900/10 border-red-900/50'
        )}>
          <div className={cn(
            "p-3 rounded-full",
            health.health_status === 'HEALTHY' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
          )}>
            {health.health_status === 'HEALTHY' ? <ShieldCheck size={24} /> : <AlertTriangle size={24} />}
          </div>
          <div className="flex-1">
            <h3 className={cn(
              "font-bold text-lg mb-1 tracking-tight",
              health.health_status === 'HEALTHY' ? 'text-green-400' : 'text-red-400'
            )}>
              Service is {health.health_status}
            </h3>
            {health.failure_reasons.length > 0 ? (
              <ul className="mt-3 space-y-2">
                {health.failure_reasons.map((reason, i) => (
                  <li key={i} className="text-sm text-red-300 flex items-center bg-red-950/30 p-2 rounded border border-red-900/30 font-mono">
                    <span className="w-1.5 h-1.5 rounded-full bg-red-500 mr-2 flex-shrink-0"></span>
                    {reason}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-green-500/80">All health checks passed successfully. No anomalies detected in current rollout window.</p>
            )}
          </div>
        </div>
      )}

      {metrics && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <MetricCard 
            title="CPU Usage" 
            value={metrics.cpu.value} 
            unit={metrics.cpu.unit} 
            icon={Cpu} 
            color="text-blue-400"
            trend={metrics.cpu.value > 500 ? 'up' : 'stable'}
          />
          <MetricCard 
            title="Memory Usage" 
            value={metrics.memory.value} 
            unit={metrics.memory.unit} 
            icon={HardDrive} 
            color="text-purple-400" 
          />
          <MetricCard 
            title="P99 Latency" 
            value={metrics.latency.value} 
            unit={metrics.latency.unit} 
            icon={Zap} 
            color={metrics.latency.value > 200 ? 'text-yellow-500' : 'text-green-400'} 
            trend={metrics.latency.value > 200 ? 'up' : 'stable'}
          />
          <MetricCard 
            title="Error Rate" 
            value={metrics.error_rate} 
            unit="%" 
            icon={AlertTriangle} 
            color={metrics.error_rate > 1 ? 'text-red-500' : 'text-text-secondary'} 
          />
          <MetricCard 
            title="Pod Restarts" 
            value={metrics.pod_restarts} 
            unit="count" 
            icon={RefreshCw} 
            color={metrics.pod_restarts > 0 ? 'text-orange-500' : 'text-text-secondary'} 
          />
          <MetricCard 
            title="Readiness" 
            value={metrics.readiness} 
            unit="%" 
            icon={Network} 
            color={metrics.readiness < 100 ? 'text-yellow-500' : 'text-green-500'} 
          />
        </div>
      )}
    </div>
  );
};
