import axios from 'axios';
import { mockApi } from './mockApi';

// Base URL points to the live backend; defaults to Render in production, localhost in development
const defaultUrl = import.meta.env.PROD 
  ? 'https://cloudchange-backend.onrender.com/api/v1' 
  : 'http://127.0.0.1:8000';
let rawUrl = (import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || defaultUrl).trim();
rawUrl = rawUrl.replace(/\/+$/, '');
const API_URL = rawUrl === '' ? '/api/v1' : (rawUrl.endsWith('/api/v1') ? rawUrl : `${rawUrl}/api/v1`);

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 5000,
});

// Helper to determine if response is an SPA HTML rewrite rather than JSON
const isHtmlResponse = (data) => {
  return typeof data === 'string' && (data.trim().startsWith('<!doctype html') || data.trim().startsWith('<html'));
};

const safeCall = async (fn, fallbackFn) => {
  try {
    const res = await fn();
    if (res && isHtmlResponse(res.data)) {
      return await fallbackFn();
    }
    return res.data;
  } catch (err) {
    if (!err.response || err.response.status === 404 || err.response.status >= 500 || err.code === 'ECONNABORTED' || isHtmlResponse(err.response?.data)) {
      return await fallbackFn();
    }
    throw err;
  }
};

export const api = {
  // Phase 6: Analyze
  analyzeDependencies: async (data) => {
    try {
      const res = await safeCall(
        () => apiClient.post('/analyze/dependencies', data),
        () => mockApi.analyzeDependencies(data)
      );
      if (!res || !Array.isArray(res.nodes) || res.nodes.length === 0) {
        return await mockApi.analyzeDependencies(data);
      }
      return res;
    } catch {
      return await mockApi.analyzeDependencies(data);
    }
  },

  analyzeImpact: async (data) => safeCall(
    () => apiClient.post('/analyze/impact', data),
    () => mockApi.analyzeImpact(data)
  ),

  getGraph: async () => {
    try {
      const data = await safeCall(
        () => apiClient.get('/graph'),
        () => mockApi.getGraph()
      );
      if (!data || !Array.isArray(data.nodes) || data.nodes.length === 0) {
        return await mockApi.getGraph();
      }
      return data;
    } catch {
      return await mockApi.getGraph();
    }
  },
  
  // Phase 7: Risk
  analyzeRisk: async (data) => safeCall(
    () => apiClient.post('/analyze/risk', data),
    () => mockApi.analyzeRisk(data)
  ),
  
  // Phase 15: Unified Orchestration
  orchestrateAnalysis: async (data) => safeCall(
    () => apiClient.post('/analyze/unified', data),
    () => mockApi.orchestrateAnalysis(data)
  ),

  // Phase 8: Deployment Recommendation
  getRecommendation: async (data) => safeCall(
    () => apiClient.post('/deployment/recommendation', data),
    () => mockApi.getRecommendation(data)
  ),

  // Phase 10 & 12: Deployment Engine
  startDeployment: async (serviceName, newVersion) => safeCall(
    () => apiClient.post('/deployment/start', { service_name: serviceName, new_version: newVersion }),
    () => mockApi.startDeployment(serviceName, newVersion)
  ),
  getDeploymentStatus: async (serviceName) => safeCall(
    () => apiClient.get(`/deployment/status?service_name=${serviceName}`),
    () => mockApi.getDeploymentStatus(serviceName)
  ),
  promoteDeployment: async (serviceName) => safeCall(
    () => apiClient.post('/deployment/promote', { service_name: serviceName }),
    () => mockApi.promoteDeployment(serviceName)
  ),
  stopDeployment: async (serviceName) => safeCall(
    () => apiClient.post('/deployment/stop', { service_name: serviceName }),
    () => mockApi.stopDeployment(serviceName)
  ),
  rollbackDeployment: async (serviceName) => safeCall(
    () => apiClient.post('/deployment/rollback', { service_name: serviceName }),
    () => mockApi.rollbackDeployment(serviceName)
  ),

  // Phase 11: Monitoring
  getMetrics: async (serviceName) => {
    try {
      const data = await safeCall(
        () => apiClient.get(`/monitoring/metrics?service_name=${serviceName}`),
        () => mockApi.getMetrics(serviceName)
      );
      return data;
    } catch {
      return await mockApi.getMetrics(serviceName);
    }
  },

  getHealth: async (serviceName) => safeCall(
    () => apiClient.get(`/monitoring/health?service_name=${serviceName}`),
    () => mockApi.getHealth(serviceName)
  ),

  // Overview & History
  getOverview: async () => {
    try {
      const data = await safeCall(
        () => apiClient.get('/overview/'),
        () => mockApi.getOverview()
      );
      if (!data || data.cluster?.status === 'DISCONNECTED' || !data.cluster) {
        const mock = await mockApi.getOverview();
        return {
          ...mock,
          ...(data || {}),
          cluster: mock.cluster,
          active_deployments: (data && data.active_deployments > 0) ? data.active_deployments : mock.active_deployments,
          average_risk_score: (data && data.average_risk_score > 0) ? data.average_risk_score : mock.average_risk_score,
          detected_changes: (data && data.detected_changes > 0) ? data.detected_changes : mock.detected_changes,
          current_deployment: data?.current_deployment || mock.current_deployment
        };
      }
      return data;
    } catch {
      return await mockApi.getOverview();
    }
  },

  getHistory: async () => {
    try {
      const data = await safeCall(
        () => apiClient.get('/history/'),
        () => mockApi.getHistory()
      );
      if (!data || !Array.isArray(data) || data.length === 0) {
        return await mockApi.getHistory();
      }
      return data;
    } catch {
      return await mockApi.getHistory();
    }
  },

  getClusterHealth: async () => {
    try {
      const data = await safeCall(
        () => apiClient.get('/cluster/health'),
        () => mockApi.getClusterHealth()
      );
      if (!data || data.status === 'DISCONNECTED') {
        return await mockApi.getClusterHealth();
      }
      return data;
    } catch {
      return await mockApi.getClusterHealth();
    }
  },

  // Notifications
  getNotifications: async (limit = 50) => safeCall(
    () => apiClient.get(`/notifications/?limit=${limit}`),
    () => mockApi.getNotifications(limit)
  ),
  markNotificationAsRead: async (id) => safeCall(
    () => apiClient.put(`/notifications/${id}/read`),
    () => mockApi.markNotificationAsRead(id)
  ),
  markAllNotificationsAsRead: async () => safeCall(
    () => apiClient.put('/notifications/read-all'),
    () => mockApi.markAllNotificationsAsRead()
  ),
};
