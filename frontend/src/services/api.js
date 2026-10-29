import axios from 'axios';
import { mockApi } from './mockApi';

// Base URL points to the live backend; defaults to Render in production, localhost in development
const defaultUrl = import.meta.env.PROD ? 'https://cloudchange-backend.onrender.com/api/v1' : 'http://127.0.0.1:8000';
let rawUrl = (import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || defaultUrl).trim();
rawUrl = rawUrl.replace(/\/+$/, '');
const API_URL = rawUrl === '' ? '/api/v1' : (rawUrl.endsWith('/api/v1') ? rawUrl : `${rawUrl}/api/v1`);

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 4000,
});

// Helper to determine if response is an SPA HTML rewrite rather than JSON
const isHtmlResponse = (data) => {
  return typeof data === 'string' && (data.trim().startsWith('<!doctype html') || data.trim().startsWith('<html'));
};

const safeCall = async (fn, fallbackFn) => {
  try {
    const res = await fn();
    if (res && isHtmlResponse(res.data)) {
      // Server returned HTML (e.g. Vercel SPA route rewrite)
      return await fallbackFn();
    }
    return res.data;
  } catch (err) {
    // If backend offline, 404, or network error in cloud environment, transparently fall back
    if (!err.response || err.response.status === 404 || err.response.status >= 500 || err.code === 'ECONNABORTED' || isHtmlResponse(err.response?.data)) {
      return await fallbackFn();
    }
    throw err;
  }
};

export const api = {
  // Phase 6: Analyze
  analyzeDependencies: async (data) => safeCall(
    () => apiClient.post('/analyze/dependencies', data),
    () => mockApi.analyzeDependencies(data)
  ),
  analyzeImpact: async (data) => safeCall(
    () => apiClient.post('/analyze/impact', data),
    () => mockApi.analyzeImpact(data)
  ),
  getGraph: async () => safeCall(
    () => apiClient.get('/graph'),
    () => mockApi.getGraph()
  ),
  
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
  getMetrics: async (serviceName) => safeCall(
    () => apiClient.get(`/monitoring/metrics?service_name=${serviceName}`),
    () => mockApi.getMetrics(serviceName)
  ),
  getHealth: async (serviceName) => safeCall(
    () => apiClient.get(`/monitoring/health?service_name=${serviceName}`),
    () => mockApi.getHealth(serviceName)
  ),

  // Overview & History
  getOverview: async () => safeCall(
    () => apiClient.get('/overview/'),
    () => mockApi.getOverview()
  ),
  getHistory: async () => safeCall(
    () => apiClient.get('/history/'),
    () => mockApi.getHistory()
  ),
  getClusterHealth: async () => safeCall(
    () => apiClient.get('/cluster/health'),
    () => mockApi.getClusterHealth()
  ),

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
