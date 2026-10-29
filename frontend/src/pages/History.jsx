import React, { useState, useEffect } from 'react';
import { Search, Filter, Calendar, Download, AlertCircle, History as HistoryIcon } from 'lucide-react';
import { Card, CardHeader, CardContent } from '../components/Card';
import { StatusBadge } from '../components/StatusBadge';
import { api } from '../services/api';

export const History = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [deployments, setDeployments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      setLoading(true);
      try {
        const data = await api.getHistory();
        setDeployments(data);
      } catch (err) {
        console.error('Failed to fetch history:', err);
      }
      setLoading(false);
    };
    
    fetchHistory();
  }, []);

  const filteredDeployments = deployments.filter(dep => 
    dep.service.toLowerCase().includes(searchTerm.toLowerCase()) ||
    dep.id.toString().includes(searchTerm)
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-12">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-3">
        <div>
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-text-primary mb-1 sm:mb-2">Audit History</h2>
          <p className="text-sm sm:text-base text-text-secondary">Comprehensive log of past deployments, rollbacks, and risk assessments.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
          <button className="flex-1 sm:flex-initial flex items-center justify-center px-3 sm:px-4 py-2 bg-surface hover:bg-gray-800 border border-border rounded-lg text-gray-300 text-xs sm:text-sm font-medium transition-colors">
            <Calendar size={15} className="mr-2 text-gray-500" /> Last 30 Days
          </button>
          <button className="flex-1 sm:flex-initial flex items-center justify-center px-3 sm:px-4 py-2 bg-surface hover:bg-gray-800 border border-border rounded-lg text-gray-300 text-xs sm:text-sm font-medium transition-colors">
            <Download size={15} className="mr-2 text-gray-500" /> Export CSV
          </button>
        </div>
      </div>

      <Card className="bg-surface border-border shadow-xl overflow-hidden">
        <div className="p-4 border-b border-border/50 bg-surface-secondary flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3">
          <div className="relative flex-1 max-w-full sm:max-w-xs">
            <Search size={16} className="absolute left-3 top-2.5 text-gray-500" />
            <input 
              type="text"
              placeholder="Search by service or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-black/50 border border-border rounded-lg pl-10 pr-4 py-2 text-text-primary text-sm focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>
          <button className="flex items-center justify-center px-4 py-2 bg-gray-900 hover:bg-gray-800 border border-border rounded-lg text-gray-300 text-sm font-medium transition-colors">
            <Filter size={16} className="mr-2" /> Filters
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm min-w-[640px]">
            <thead className="bg-background/50 text-gray-500 uppercase tracking-wider text-xs border-b border-border/80">
              <tr>
                <th className="px-6 py-4 font-semibold">Deployment ID</th>
                <th className="px-6 py-4 font-semibold">Service</th>
                <th className="px-6 py-4 font-semibold">Strategy</th>
                <th className="px-6 py-4 font-semibold">Risk Score</th>
                <th className="px-6 py-4 font-semibold">Status</th>
                <th className="px-6 py-4 font-semibold">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/50">
              {filteredDeployments.length > 0 ? (
                filteredDeployments.map((dep, i) => (
                  <tr key={i} className="hover:bg-gray-900/30 transition-colors">
                    <td className="px-6 py-4 font-mono text-gray-400">#{dep.id}</td>
                    <td className="px-6 py-4 font-medium text-text-primary">{dep.service}</td>
                    <td className="px-6 py-4"><span className="text-blue-400 bg-blue-500/10 px-2 py-1 rounded text-xs">v1 → {dep.version}</span></td>
                    <td className="px-6 py-4"><StatusBadge status={dep.health_status || "UNKNOWN"} className="bg-transparent" /></td>
                    <td className="px-6 py-4"><StatusBadge status={dep.status} /></td>
                    <td className="px-6 py-4 text-gray-400">{new Date(dep.timestamp).toLocaleString()}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="px-6 py-24 text-center">
                    <div className="flex flex-col items-center justify-center text-gray-500">
                      <div className="w-16 h-16 bg-gray-900 rounded-full flex items-center justify-center mb-4 border border-border shadow-inner">
                        <HistoryIcon size={32} className="text-gray-600" />
                      </div>
                      <h3 className="text-lg font-medium text-gray-300 mb-1">No historical records found</h3>
                      <p className="text-sm max-w-sm text-gray-500">
                        Deployments and risk analysis events will appear here once executed through the pipeline.
                      </p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        <div className="p-4 border-t border-border/50 bg-surface-secondary flex justify-between items-center text-sm text-gray-500">
          <span>Showing {filteredDeployments.length} results</span>
          <div className="flex space-x-2">
            <button disabled className="px-3 py-1 rounded bg-gray-900 border border-border text-gray-600 cursor-not-allowed">Previous</button>
            <button disabled className="px-3 py-1 rounded bg-gray-900 border border-border text-gray-600 cursor-not-allowed">Next</button>
          </div>
        </div>
      </Card>
    </div>
  );
};
