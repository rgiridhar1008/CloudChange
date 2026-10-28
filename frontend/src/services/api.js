import axios from 'axios';

// Base URL points to the FastAPI backend, configurable via .env
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout
});

// Add request interceptor for logging
apiClient.interceptors.request.use((config) => {
  if (import.meta.env.DEV) {
    console.log(`[API Request] ${config.method.toUpperCase()} ${config.url}`, config.data || '');
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Add response interceptor for logging and centralized error handling
apiClient.interceptors.response.use((response) => {
  if (import.meta.env.DEV) {
    console.log(`[API Response] ${response.config.method.toUpperCase()} ${response.config.url} - Status: ${response.status}`, response.data);
  }
  return response;
}, (error) => {
  let errorMessage = error.message;

  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    if (error.response.status === 422) {
      errorMessage = `Validation Error: ${JSON.stringify(error.response.data?.detail || error.response.data)}`;
    } else if (error.response.status >= 500) {
      errorMessage = error.response.data?.message || error.response.data?.detail || "Backend Service Unavailable";
    } else {
      errorMessage = error.response.data?.message || error.response.data?.detail || error.message;
    }
  } else if (error.request) {
    // The request was made but no response was received
    errorMessage = "Kubernetes/Backend Unavailable (Network Error)";
  }

  if (import.meta.env.DEV) {
    console.error(`[API Error]`, {
      url: error.config?.url,
      method: error.config?.method?.toUpperCase(),
      status: error.response?.status,
      data: error.response?.data,
      message: errorMessage
    });
  }
  
  // Attach the parsed message to the error object so components can use it
  error.parsedMessage = errorMessage;
  return Promise.reject(error);
});

export const api = {
  // Phase 6: Analyze
  analyzeDependencies: async (data) => {
    const response = await apiClient.post('/analyze/dependencies', data);
    return response.data;
  },
  analyzeImpact: async (data) => {
    const response = await apiClient.post('/analyze/impact', data);
    return response.data;
  },
  getGraph: async () => {
    const response = await apiClient.get('/graph');
    return response.data;
  },
  
  // Phase 7: Risk
  analyzeRisk: async (data) => {
    const response = await apiClient.post('/analyze/risk', data);
    return response.data;
  },
  
  // Phase 15: Unified Orchestration
  orchestrateAnalysis: async (data) => {
    const response = await apiClient.post('/analyze/unified', data);
    return response.data;
  },

  // Phase 8: Deployment Recommendation
  getRecommendation: async (data) => {
    const response = await apiClient.post('/deployment/recommendation', data);
    return response.data;
  },

  // Phase 10 & 12: Deployment Engine
  startDeployment: async (serviceName, newVersion) => {
    const response = await apiClient.post('/deployment/start', { service_name: serviceName, new_version: newVersion });
    return response.data;
  },
  getDeploymentStatus: async (serviceName) => {
    const response = await apiClient.get(`/deployment/status?service_name=${serviceName}`);
    return response.data;
  },
  promoteDeployment: async (serviceName) => {
    const response = await apiClient.post('/deployment/promote', { service_name: serviceName });
    return response.data;
  },
  stopDeployment: async (serviceName) => {
    const response = await apiClient.post('/deployment/stop', { service_name: serviceName });
    return response.data;
  },
  rollbackDeployment: async (serviceName) => {
    const response = await apiClient.post('/deployment/rollback', { service_name: serviceName });
    return response.data;
  },

  // Phase 11: Monitoring
  getMetrics: async (serviceName) => {
    const response = await apiClient.get(`/monitoring/metrics?service_name=${serviceName}`);
    return response.data;
  },
  getHealth: async (serviceName) => {
    const response = await apiClient.get(`/monitoring/health?service_name=${serviceName}`);
    return response.data;
  },

  // Overview & History
  getOverview: async () => {
    const response = await apiClient.get('/overview/');
    return response.data;
  },
  getHistory: async () => {
    const response = await apiClient.get('/history/');
    return response.data;
  },
  getClusterHealth: async () => {
    const response = await apiClient.get('/cluster/health');
    return response.data;
  },
};
