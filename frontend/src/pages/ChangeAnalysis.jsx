import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/Card';
import { GitCompare, ShieldAlert, Rocket, ChevronRight, FileCode, CheckCircle2, Info, AlertTriangle, ChevronDown } from 'lucide-react';
import { AVAILABLE_SERVICES, SERVICE_PRESETS } from '../utils/services';
import { api } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { RiskMeter } from '../components/RiskMeter';
import { StatusBadge } from '../components/StatusBadge';
import { toast } from '../components/Toast';

export const ChangeAnalysis = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [resourceName, setResourceName] = useState('payment-service');
  
  const [oldManifest, setOldManifest] = useState(`apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: payment
        image: payment:v1
        resources:
          requests:
            memory: "512Mi"
`);

  const [newManifest, setNewManifest] = useState(`apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: payment
        image: payment:v2
        resources:
          requests:
            memory: "128Mi"
`);

  const handleSelectService = (name) => {
    setResourceName(name);
    if (SERVICE_PRESETS[name]) {
      setOldManifest(SERVICE_PRESETS[name].old);
      setNewManifest(SERVICE_PRESETS[name].new);
    }
    setResult(null);
    setError(null);
  };

  const navigate = useNavigate();

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      if (!resourceName.trim()) throw new Error("Resource name cannot be empty.");
      if (!oldManifest.trim()) throw new Error("Current configuration cannot be empty.");
      if (!newManifest.trim()) throw new Error("Proposed configuration cannot be empty.");
      
      // Basic YAML heuristic check
      if (!oldManifest.includes('kind:') || !newManifest.includes('kind:')) {
        throw new Error("Invalid Kubernetes manifest. Missing 'kind' field.");
      }

      // Phase 8: Health Check
      try {
        await api.getClusterHealth();
      } catch (hcError) {
        throw new Error("CloudChange backend is offline. Please start the backend server.");
      }

      const res = await api.orchestrateAnalysis({
        resource_name: resourceName,
        manifest_content: newManifest,
        old_manifest_content: oldManifest
      });
      setResult(res);
    } catch (e) {
      console.error(e);
      let errorMsg = "Backend server is unreachable. Check that the backend is running.";
      if (e.response?.data?.message) {
         errorMsg = e.response.data.message;
      } else if (e.response?.data?.detail) {
         errorMsg = typeof e.response.data.detail === 'string' 
            ? e.response.data.detail 
            : JSON.stringify(e.response.data.detail);
      } else if (e.message) {
         errorMsg = e.message;
      }
      setError(errorMsg);
    }
    setLoading(false);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-12">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-text-primary mb-1 sm:mb-2">Change Analysis</h2>
          <p className="text-sm sm:text-base text-text-secondary">Detect configuration drifts and evaluate potential deployment impact.</p>
          <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 mt-3">
            <span className="text-xs text-text-secondary font-medium mr-1">Select Service:</span>
            {AVAILABLE_SERVICES.map((s) => (
              <button
                key={s.id}
                type="button"
                onClick={() => handleSelectService(s.id)}
                className={`text-xs px-2.5 sm:px-3 py-1 rounded-full border transition-all ${
                  resourceName === s.id
                    ? 'bg-blue-500/20 border-blue-500 text-blue-400 font-semibold shadow-sm shadow-blue-500/20 scale-105'
                    : 'bg-surface border-border text-text-secondary hover:text-text-primary hover:border-gray-600'
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 w-full sm:w-auto">
          <div className="relative w-full sm:w-56">
            <select
              value={resourceName}
              onChange={(e) => handleSelectService(e.target.value)}
              className="bg-surface border border-border rounded-lg pl-3 pr-8 py-2 text-text-primary text-sm font-medium focus:outline-none focus:border-blue-500 appearance-none cursor-pointer hover:border-gray-600 transition-colors shadow-sm w-full"
            >
              {AVAILABLE_SERVICES.map((s) => (
                <option key={s.id} value={s.id} className="bg-gray-900 text-white">
                  {s.label}
                </option>
              ))}
            </select>
            <ChevronDown size={14} className="absolute right-2.5 top-3 pointer-events-none text-text-secondary" />
          </div>
          <button 
            onClick={handleAnalyze}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-text-primary rounded-lg text-sm font-medium transition-colors disabled:opacity-50 flex items-center justify-center shadow-lg shadow-blue-900/20 w-full sm:w-auto"
          >
            {loading ? (
              <><span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin mr-2"></span> Analyzing...</>
            ) : (
              <><GitCompare size={16} className="mr-2" /> Analyze Impact & Risk</>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-start animate-in fade-in slide-in-from-top-4">
          <AlertTriangle className="text-red-400 mt-0.5 mr-3 flex-shrink-0" size={20} />
          <div className="flex-1">
            <h3 className="text-red-400 font-medium text-sm mb-1">Analysis failed</h3>
            <p className="text-red-300/80 text-sm">{error}</p>
          </div>
          <button onClick={() => setError(null)} className="text-red-400/50 hover:text-red-400 transition-colors ml-4">
            ×
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-surface border-border">
          <CardHeader className="border-b border-border/50 py-3 bg-surface-secondary">
            <div className="flex justify-between items-center w-full">
              <div className="flex items-center space-x-2">
                <FileCode className="text-text-secondary" size={16} />
                <CardTitle className="text-sm font-medium">Current Configuration</CardTitle>
              </div>
              <span className="text-xs text-gray-500 font-mono">v1 (Live)</span>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <textarea 
              value={oldManifest}
              onChange={(e) => setOldManifest(e.target.value)}
              className="w-full h-[280px] sm:h-[350px] md:h-[400px] bg-black p-4 text-text-secondary font-mono text-[13px] leading-relaxed focus:outline-none resize-none"
              spellCheck="false"
            />
          </CardContent>
        </Card>

        <Card className="bg-surface border-border">
          <CardHeader className="border-b border-border/50 py-3 bg-surface-secondary">
            <div className="flex justify-between items-center w-full">
              <div className="flex items-center space-x-2">
                <FileCode className="text-blue-400" size={16} />
                <CardTitle className="text-sm font-medium text-text-primary">Proposed Configuration</CardTitle>
              </div>
              <span className="text-xs text-blue-500 font-mono font-medium">v2 (Target)</span>
            </div>
          </CardHeader>
          <CardContent className="p-0 relative">
            <textarea 
              value={newManifest}
              onChange={(e) => setNewManifest(e.target.value)}
              className="w-full h-[280px] sm:h-[350px] md:h-[400px] bg-[#0a111a] p-4 text-blue-100 font-mono text-[13px] leading-relaxed focus:outline-none resize-none"
              spellCheck="false"
            />
          </CardContent>
        </Card>
      </div>

      {result && (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 animate-in slide-in-from-bottom-8 duration-500">
          <Card className="bg-surface border-border xl:col-span-1 shadow-xl">
            <CardHeader className="border-b border-border/50">
              <CardTitle>Detected Changes</CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              {result.changes.length > 0 ? (
                <div className="space-y-4">
                  {result.changes.map((change, i) => (
                    <div key={i} className="p-4 rounded-lg bg-gray-900/50 border border-border relative overflow-hidden">
                      <div className={`absolute left-0 top-0 bottom-0 w-1 ${
                        change.type === 'ADDED' ? 'bg-green-500' :
                        change.type === 'REMOVED' ? 'bg-red-500' :
                        'bg-yellow-500'
                      }`}></div>
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-xs font-bold uppercase tracking-wider text-text-primary">
                          {change.type.replace('_', ' ')}
                        </span>
                        <span className="text-[10px] text-gray-500 font-mono truncate max-w-[150px]" title={change.path}>{change.path.split('.').pop()}</span>
                      </div>
                      <div className="flex items-center space-x-2 text-sm font-mono">
                        {change.type !== 'ADDED' && <span className="text-red-400 bg-red-500/10 px-1 rounded">{String(change.old)}</span>}
                        {change.type === 'MODIFIED' || change.type.includes('REDUCTION') || change.type.includes('INCREASE') ? <span className="text-gray-500">→</span> : null}
                        {change.type !== 'REMOVED' && <span className="text-green-400 bg-green-500/10 px-1 rounded">{String(change.new)}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-12 text-gray-500">
                  <CheckCircle2 size={32} className="mb-3 text-green-500/50" />
                  <p>No configuration drifts detected.</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="bg-surface border-border xl:col-span-1 shadow-xl">
            <CardHeader className="border-b border-border/50">
              <CardTitle>Risk Evaluation</CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <RiskMeter score={result.risk.risk_score} />
              
              <div className="mt-8 space-y-4">
                <div className="flex justify-between items-center pb-3 border-b border-border/50">
                  <span className="text-sm text-text-secondary">Blast Radius Criticality</span>
                  <StatusBadge status={result.risk.blast_radius.criticality} />
                </div>
                <div className="flex justify-between items-center pb-3 border-b border-border/50">
                  <span className="text-sm text-text-secondary">Affected Services</span>
                  <span className="text-sm font-bold text-text-primary">{result.risk.affected_services.length}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-blue-900/10 border-blue-900/50 xl:col-span-1 shadow-xl">
            <CardHeader className="border-b border-blue-900/30">
              <div className="flex items-center space-x-2">
                <Rocket className="text-blue-400" size={18} />
                <CardTitle className="text-blue-400">Deployment Strategy</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="pt-6 flex flex-col h-[calc(100%-60px)]">
              <div className="flex justify-between items-center mb-6">
                <span className="text-3xl font-bold tracking-tight text-text-primary">{result.recommendation.strategy}</span>
                {result.recommendation.requires_approval && (
                  <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-xs font-bold tracking-wider border border-red-500/30">
                    APPROVAL REQ
                  </span>
                )}
              </div>
              
              {result.recommendation.explanation && (
                <div className="p-4 bg-surface/80 border border-border rounded-xl flex-1 mb-6">
                  <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center">
                    <Info size={14} className="mr-1.5" /> AI Explanation
                  </h4>
                  <p className="text-sm text-gray-300 leading-relaxed">
                    {result.recommendation.explanation}
                  </p>
                </div>
              )}

              <button 
                onClick={() => navigate('/deployment')}
                className="w-full mt-auto flex justify-center items-center py-3 bg-blue-600 hover:bg-blue-700 text-text-primary rounded-xl font-medium transition-colors shadow-lg shadow-blue-900/20"
              >
                Proceed to Deployment <ChevronRight size={18} className="ml-1" />
              </button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};
