import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/Card';
import { api } from '../services/api';
import { RiskMeter } from '../components/RiskMeter';
import { StatusBadge } from '../components/StatusBadge';
import { Play, ShieldAlert, Zap, Cpu, Network, AlertTriangle } from 'lucide-react';

export const RiskAnalysis = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [error, setError] = useState(null);

  const [payloadText, setPayloadText] = useState(JSON.stringify({
    "changed_resource": "payment-service",
    "changes": [
      {
        "type": "REPLICA_REDUCTION",
        "path": "spec.replicas",
        "old": 3,
        "new": 1
      },
      {
        "type": "MEMORY_REDUCTION",
        "path": "spec.template.spec.containers[0].resources.requests.memory",
        "old": "512Mi",
        "new": "128Mi"
      }
    ]
  }, null, 2));

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      let parsedPayload;
      try {
        parsedPayload = JSON.parse(payloadText);
      } catch (e) {
        throw new Error("Invalid JSON payload.");
      }

      const riskData = await api.analyzeRisk(parsedPayload);
      setResult(riskData);
      
      const recPayload = {
        risk_score: riskData.risk_score,
        risk_level: riskData.risk_level,
        blast_radius: riskData.blast_radius,
        affected_services: riskData.affected_services,
        criticality: riskData.blast_radius.criticality
      };
      
      const recData = await api.getRecommendation(recPayload);
      setRecommendation(recData);
    } catch (err) {
      console.error(err);
      let errorMsg = "Failed to analyze risk. Ensure backend is running.";
      if (err.response?.data?.detail) {
        errorMsg = typeof err.response.data.detail === 'string' ? err.response.data.detail : JSON.stringify(err.response.data.detail);
      } else if (err.message) {
        errorMsg = err.message;
      }
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-text-primary mb-2">Risk Analysis Engine</h2>
          <p className="text-text-secondary">Evaluate the blast radius and calculate deployment risk based on configuration drifts.</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-start">
          <AlertTriangle className="text-red-400 mt-0.5 mr-3 flex-shrink-0" size={20} />
          <div className="flex-1">
            <h3 className="text-red-400 font-medium text-sm mb-1">Analysis failed</h3>
            <p className="text-red-300/80 text-sm">{error}</p>
          </div>
          <button onClick={() => setError(null)} className="text-red-400/50 hover:text-red-400 transition-colors ml-4">×</button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <Card className="bg-surface border-border lg:col-span-4 shadow-xl flex flex-col">
          <CardHeader className="border-b border-border/50 bg-surface-secondary">
            <CardTitle>Analysis Payload</CardTitle>
          </CardHeader>
          <CardContent className="p-0 flex-1 flex flex-col relative">
            <div className="absolute top-3 right-3 flex space-x-2">
              <span className="w-3 h-3 rounded-full bg-red-500/80"></span>
              <span className="w-3 h-3 rounded-full bg-yellow-500/80"></span>
              <span className="w-3 h-3 rounded-full bg-green-500/80"></span>
            </div>
            <textarea 
              value={payloadText}
              onChange={(e) => setPayloadText(e.target.value)}
              className="flex-1 bg-[#0a111a] p-6 pt-10 text-[13px] text-blue-200 overflow-x-auto border-b border-border font-mono resize-none focus:outline-none w-full h-[400px]"
              spellCheck="false"
            />
            <div className="p-4 bg-surface">
              <button 
                onClick={handleAnalyze}
                disabled={loading}
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-text-primary rounded-xl font-medium transition-colors disabled:opacity-50 flex justify-center items-center shadow-lg shadow-blue-900/20"
              >
                {loading ? <span className="w-5 h-5 rounded-full border-2 border-white/30 border-t-white animate-spin"></span> : <><Play size={18} className="mr-2 fill-current" /> Execute Risk Engine</>}
              </button>
            </div>
          </CardContent>
        </Card>

        {result && recommendation ? (
          <div className="lg:col-span-8 space-y-6 animate-in slide-in-from-right-8 duration-500">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="bg-surface border-border shadow-xl">
                <CardHeader className="border-b border-border/50">
                  <div className="flex items-center space-x-2">
                    <ShieldAlert className="text-yellow-500" size={18} />
                    <CardTitle>Risk Factors</CardTitle>
                  </div>
                </CardHeader>
                <CardContent className="pt-6">
                  <RiskMeter score={result.risk_score} />
                  
                  <div className="mt-8 space-y-3">
                    <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Contributing Factors</h4>
                    {result.risk_factors?.map((f, i) => (
                      <div key={i} className="flex justify-between items-center p-3 bg-gray-900/50 border border-border rounded-lg">
                        <div className="flex items-center space-x-3">
                          {f.factor.includes('Traffic') ? <Network size={16} className="text-blue-400" /> : 
                           f.factor.includes('Reduction') ? <Zap size={16} className="text-orange-400" /> : 
                           <Cpu size={16} className="text-text-secondary" />}
                          <span className="text-sm text-gray-300">{f.factor}</span>
                        </div>
                        <span className="text-sm font-mono font-bold text-red-400 bg-red-500/10 px-2 py-0.5 rounded">
                          +{f.score}
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-surface border-border shadow-xl flex flex-col">
                <CardHeader className="border-b border-border/50">
                  <CardTitle>Deployment Strategy</CardTitle>
                </CardHeader>
                <CardContent className="pt-6 flex-1 flex flex-col">
                  <div className="flex justify-between items-center mb-6">
                    <span className="text-3xl font-bold tracking-tight text-text-primary">{recommendation.strategy}</span>
                    {recommendation.requires_approval && (
                      <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-xs font-bold tracking-wider border border-red-500/30">
                        APPROVAL REQ
                      </span>
                    )}
                  </div>
                  
                  <p className="text-sm text-text-secondary mb-6">{recommendation.reason}</p>
                  
                  {recommendation.explanation && (
                    <div className="p-5 bg-blue-900/10 border border-blue-900/30 rounded-xl flex-1">
                      <h4 className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-3 flex items-center">
                        <span className="mr-2 animate-pulse text-lg leading-none">✨</span> AI Explanation
                      </h4>
                      <p className="text-sm text-gray-300 leading-relaxed">
                        {recommendation.explanation}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
            
            <Card className="bg-surface border-border shadow-xl">
              <CardHeader className="border-b border-border/50">
                <CardTitle>Blast Radius Assessment</CardTitle>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="grid grid-cols-3 gap-6 text-center">
                  <div className="p-4 bg-gray-900/50 rounded-xl border border-border">
                    <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Criticality</p>
                    <StatusBadge status={result.blast_radius.criticality} className="text-sm px-4 py-1.5" />
                  </div>
                  <div className="p-4 bg-gray-900/50 rounded-xl border border-border">
                    <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Depth</p>
                    <p className="text-2xl font-bold text-text-primary">{result.blast_radius.depth}</p>
                  </div>
                  <div className="p-4 bg-gray-900/50 rounded-xl border border-border">
                    <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Affected Services</p>
                    <p className="text-2xl font-bold text-text-primary">{result.affected_services.length}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          <div className="lg:col-span-8 flex flex-col items-center justify-center border-2 border-dashed border-border rounded-xl bg-background p-12 text-gray-500 min-h-[400px]">
            <ShieldAlert size={48} className="mb-4 text-gray-700" />
            <h3 className="text-lg font-medium text-text-secondary mb-1">Awaiting Analysis</h3>
            <p className="text-sm text-center max-w-sm">Execute the Risk Engine to evaluate the payload and determine the blast radius.</p>
          </div>
        )}
      </div>
    </div>
  );
};
