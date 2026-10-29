import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/Card';
import { Activity, ShieldCheck, Rocket, GitPullRequest, ArrowRight, CheckCircle2, Clock } from 'lucide-react';
import { api } from '../services/api';
import { StatusBadge } from '../components/StatusBadge';
import { useNavigate } from 'react-router-dom';

const StatCard = ({ title, value, subtitle, icon: Icon, colorClass }) => (
  <div className="bg-surface border border-border rounded-xl p-5 sm:p-6 flex items-start space-x-4 shadow-lg hover:border-gray-700 transition-colors">
    <div className={`p-3 rounded-lg bg-gray-900/50 border border-border flex-shrink-0 ${colorClass}`}>
      <Icon size={24} />
    </div>
    <div className="min-w-0 flex-1">
      <p className="text-sm font-medium text-text-secondary mb-1 truncate">{title}</p>
      <h3 className="text-2xl font-bold text-text-primary tracking-tight truncate">{value}</h3>
      <p className="text-xs text-gray-500 mt-1 truncate">{subtitle}</p>
    </div>
  </div>
);

const PipelineStage = ({ title, status, isLast, onClick }) => (
  <div
    className="flex flex-col items-center relative flex-1 cursor-pointer group"
    onClick={onClick}
  >
    <div className={`w-12 h-12 rounded-full flex items-center justify-center border-2 shadow-lg z-10 transition-transform group-hover:scale-110 ${status === 'complete' ? 'bg-green-500/10 border-green-500 text-green-500' :
        status === 'active' ? 'bg-blue-500/10 border-blue-500 text-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.3)] animate-pulse' :
          'bg-gray-900 border-gray-700 text-gray-600 group-hover:border-gray-500 group-hover:text-gray-400'
      }`}>
      {status === 'complete' ? <CheckCircle2 size={20} /> : <Activity size={20} />}
    </div>
    <span className={`mt-3 text-xs font-bold uppercase tracking-wider transition-colors ${status === 'complete' ? 'text-green-400' :
        status === 'active' ? 'text-blue-400' :
          'text-gray-500 group-hover:text-gray-400'
      }`}>{title}</span>

    {!isLast && (
      <div className="absolute top-6 left-1/2 w-full h-[2px] -z-0" style={{ transform: 'translateX(24px)' }}>
        <div className={`w-full h-full ${status === 'complete' ? 'bg-green-500/50' : 'bg-gray-800'}`}></div>
      </div>
    )}
  </div>
);

export const Overview = () => {
  const [overviewData, setOverviewData] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const data = await api.getOverview();
        setOverviewData(data);
      } catch (err) {
        console.error("Failed to fetch overview", err);
      }
      setLoading(false);
    };

    fetchData();
  }, []);

  const getPipelineStatus = (stage) => {
    const dStatus = overviewData?.current_deployment?.status;
    if (!dStatus) return 'pending';

    if (dStatus === 'SUCCESS') return 'complete';
    if (dStatus === 'FAILED' || dStatus === 'ROLLED_BACK') return 'pending';

    switch (stage) {
      case 'change': return 'complete';
      case 'risk': return 'complete';
      case 'deploy': return dStatus === 'IN_PROGRESS' ? 'active' : 'complete';
      case 'monitor': return dStatus === 'IN_PROGRESS' ? 'active' : 'pending';
      case 'promote': return 'pending';
      default: return 'pending';
    }
  };

  if (loading) {
    return <div className="animate-pulse space-y-6">
      <div className="h-8 bg-gray-800 rounded w-1/4"></div>
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6">
        <div className="h-32 bg-gray-800 rounded-xl"></div>
        <div className="h-32 bg-gray-800 rounded-xl"></div>
      </div>
    </div>;
  }

  const clusterStatus = overviewData?.cluster?.status || "UNKNOWN";
  const activeCount = overviewData?.active_deployments || 0;
  const avgRisk = overviewData?.average_risk_score || 0;
  const detected = overviewData?.detected_changes || 0;
  const deployment = overviewData?.current_deployment;

  return (
    <div className="space-y-6 sm:space-y-8 animate-in fade-in duration-500">
      <div>
        <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-text-primary mb-1 sm:mb-2">Command Center</h2>
        <p className="text-sm sm:text-base text-text-secondary">Monitor changes, deployment risk, cluster health, and rollout activity.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 sm:gap-6">
        <StatCard
          title="Cluster Health"
          value={clusterStatus}
          subtitle={clusterStatus === 'HEALTHY' ? `${overviewData?.cluster?.name || 'minikube'} (Connected)` : 'Cluster Offline (Run: minikube start)'}
          icon={Activity}
          colorClass={clusterStatus === 'HEALTHY' ? "text-green-500" : "text-amber-500"}
        />
        <StatCard
          title="Active Deployments"
          value={activeCount.toString()}
          subtitle={activeCount > 0 ? 'Canary Rollout Active' : 'No active rollouts'}
          icon={Rocket}
          colorClass="text-blue-500"
        />
        <StatCard
          title="Average Risk Score"
          value={avgRisk.toString()}
          subtitle="From historical DB"
          icon={ShieldCheck}
          colorClass="text-yellow-500"
        />
        <StatCard
          title="Detected Changes"
          value={detected.toString()}
          subtitle={detected > 0 ? 'Awaiting analysis' : 'No uncommitted changes'}
          icon={GitPullRequest}
          colorClass="text-purple-500"
        />
      </div>

      <Card className="bg-surface border-border shadow-xl">
        <CardHeader className="border-b border-border/50 pb-4">
          <CardTitle>Delivery Pipeline</CardTitle>
        </CardHeader>
        <CardContent className="pt-8 pb-6 overflow-x-auto">
          <div className="flex justify-between items-start min-w-[520px] md:min-w-0 w-full px-4">
            <PipelineStage title="Change" status={getPipelineStatus('change')} onClick={() => navigate('/change')} />
            <PipelineStage title="Analyze" status={getPipelineStatus('risk')} onClick={() => navigate('/risk')} />
            <PipelineStage title="Deploy" status={getPipelineStatus('deploy')} onClick={() => navigate('/deployment')} />
            <PipelineStage title="Monitor" status={getPipelineStatus('monitor')} onClick={() => navigate('/monitoring')} />
            <PipelineStage title="Promote" status={getPipelineStatus('promote')} isLast={true} onClick={() => navigate('/history')} />
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <Card className="bg-surface border-border shadow-xl">
          <CardHeader className="border-b border-border/50">
            <CardTitle>Current Deployment</CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            {deployment ? (
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-sm text-gray-500 uppercase tracking-wider font-semibold mb-1">Target Service</p>
                    <p className="text-xl font-bold text-text-primary">{deployment.service}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-500 uppercase tracking-wider font-semibold mb-1">Strategy</p>
                    <p className="text-lg font-bold text-blue-400">{deployment.strategy}</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm font-medium">
                    <span className="text-gray-300">Traffic Distribution</span>
                    <span className="text-blue-400">{deployment.traffic?.canary}% New</span>
                  </div>
                  <div className="w-full bg-gray-800 rounded-full h-4 relative overflow-hidden flex">
                    <div className="bg-gray-600 h-full transition-all duration-1000" style={{ width: `${deployment.traffic?.stable}%` }}></div>
                    <div className="bg-blue-500 h-full transition-all duration-1000 shadow-[0_0_10px_rgba(59,130,246,0.5)]" style={{ width: `${deployment.traffic?.canary}%` }}></div>
                  </div>
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>{deployment.current_version} (Stable)</span>
                    <span>{deployment.target_version} (Canary)</span>
                  </div>
                </div>

                <div className="flex justify-between items-center pt-4 border-t border-border/50">
                  <div className="flex space-x-4">
                    <StatusBadge status={deployment.status} />
                    <StatusBadge status={deployment.health} className="bg-transparent" />
                  </div>
                  <button
                    onClick={() => navigate('/deployment')}
                    className="flex items-center text-sm font-medium text-blue-400 hover:text-blue-300 transition-colors"
                  >
                    Manage Rollout <ArrowRight size={16} className="ml-1" />
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500 mb-4">No deployment data available.</p>
                <button onClick={() => navigate('/deployment')} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-text-primary rounded-lg text-sm font-medium transition-colors">
                  Go to Deployment Engine
                </button>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="bg-surface border-border shadow-xl">
          <CardHeader className="border-b border-border/50">
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="relative pl-6 border-l-2 border-border space-y-8">
              {deployment?.status === 'IN_PROGRESS' && (
                <div className="relative">
                  <div className="absolute -left-[35px] top-1 w-4 h-4 bg-surface border-2 border-blue-500 rounded-full shadow-[0_0_8px_rgba(59,130,246,0.6)]"></div>
                  <p className="text-sm font-semibold text-text-primary">Canary Deployment Active</p>
                  <p className="text-sm text-text-secondary mt-1">Routing {deployment.traffic?.canary}% traffic to target version of {deployment.service}</p>
                  <p className="text-xs text-gray-500 mt-2 flex items-center"><Clock size={12} className="mr-1" /> Live</p>
                </div>
              )}
              {clusterStatus && (
                <div className="relative">
                  <div className="absolute -left-[35px] top-1 w-4 h-4 bg-surface border-2 border-green-500 rounded-full"></div>
                  <p className="text-sm font-semibold text-text-primary">Cluster Status Evaluated</p>
                  <p className="text-sm text-text-secondary mt-1">Cluster marked as {clusterStatus}</p>
                  <p className="text-xs text-gray-500 mt-2 flex items-center"><Clock size={12} className="mr-1" /> Live</p>
                </div>
              )}
              {!deployment && !clusterStatus && (
                <p className="text-gray-500 text-sm">No recent activity detected.</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
