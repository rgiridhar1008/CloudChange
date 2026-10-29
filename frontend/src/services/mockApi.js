// High-fidelity fallback / simulated engine for CloudChange when running in cloud environments (e.g. Vercel)
// or when a local backend is not actively attached.

const DEFAULT_GRAPH = {
  nodes: [
    { id: "ingress", label: "ingress", type: "Ingress", namespace: "default", criticality: "high" },
    { id: "api-gateway", label: "api-gateway", type: "Gateway", namespace: "default", criticality: "high" },
    { id: "order-service", label: "order-service", type: "Service", namespace: "default", criticality: "medium" },
    { id: "payment-service", label: "payment-service", type: "Service", namespace: "default", criticality: "critical" },
    { id: "user-service", label: "user-service", type: "Service", namespace: "default", criticality: "medium" },
    { id: "database", label: "database", type: "Database", namespace: "default", criticality: "critical" },
    { id: "postgres-service", label: "postgres-service", type: "Database", namespace: "default", criticality: "critical" }
  ],
  edges: [
    { source: "ingress", target: "api-gateway", type: "direct" },
    { source: "api-gateway", target: "order-service", type: "direct" },
    { source: "order-service", target: "payment-service", type: "direct" },
    { source: "payment-service", target: "database", type: "direct" },
    { source: "payment-service", target: "postgres-service", type: "direct" },
    { source: "api-gateway", target: "user-service", type: "direct" }
  ]
};

// In-memory / session-persisted deployment state
const getStoredDeployment = () => {
  try {
    const raw = sessionStorage.getItem('cloudchange_mock_deployment');
    if (raw) return JSON.parse(raw);
  } catch (e) {}
  return {
    service: "payment-service",
    current_version: "v1.4.2",
    target_version: "v1.5.0",
    strategy: "CANARY",
    traffic: { stable: 75, canary: 25 },
    status: "IN_PROGRESS",
    health: "HEALTHY",
    percentage: 25
  };
};

const saveStoredDeployment = (dep) => {
  try {
    if (dep) {
      sessionStorage.setItem('cloudchange_mock_deployment', JSON.stringify(dep));
    } else {
      sessionStorage.removeItem('cloudchange_mock_deployment');
    }
  } catch (e) {}
};

export const mockApi = {
  getClusterHealth: async () => {
    return {
      cluster: "cloud-production",
      status: "HEALTHY",
      nodes: 3,
      ready_nodes: 3,
      timestamp: new Date().toISOString()
    };
  },

  getOverview: async () => {
    const dep = getStoredDeployment();
    return {
      cluster: {
        name: "cloud-production",
        status: "HEALTHY"
      },
      active_deployments: dep && dep.status === 'IN_PROGRESS' ? 1 : 0,
      average_risk_score: 34,
      detected_changes: 2,
      current_deployment: dep
    };
  },

  getGraph: async () => {
    return JSON.parse(JSON.stringify(DEFAULT_GRAPH));
  },

  analyzeDependencies: async () => {
    return JSON.parse(JSON.stringify(DEFAULT_GRAPH));
  },

  analyzeImpact: async (data) => {
    const service = data?.changed_resource || "payment-service";
    return {
      changed_resource: service,
      blast_radius: {
        criticality: "critical",
        depth: 2,
        total_affected: 3
      },
      affected_services: [service, "database", "postgres-service"],
      subgraph: {
        nodes: [
          { id: service, label: service, type: "Service", namespace: "default", criticality: "critical" },
          { id: "database", label: "database", type: "Database", namespace: "default", criticality: "critical" },
          { id: "postgres-service", label: "postgres-service", type: "Database", namespace: "default", criticality: "critical" }
        ],
        edges: [
          { source: service, target: "database", type: "direct" },
          { source: service, target: "postgres-service", type: "direct" }
        ]
      }
    };
  },

  analyzeRisk: async (data) => {
    const service = data?.changed_resource || "payment-service";
    return {
      risk_score: 42,
      risk_level: "MEDIUM",
      blast_radius: {
        criticality: "critical",
        depth: 2,
        total_affected: 3
      },
      affected_services: [service, "database", "postgres-service"],
      contributing_factors: [
        "Core payment processing transaction tier",
        "Memory requests increased to 128Mi",
        "Direct dependency with persistent relational database"
      ]
    };
  },

  orchestrateAnalysis: async (data) => {
    const service = data?.resource_name || "payment-service";
    return {
      changes: [
        { type: "MODIFIED", path: "spec.template.spec.containers[0].image", old: "payment:v1", new: "payment:v2" },
        { type: "RESOURCE_INCREASE", path: "spec.template.spec.containers[0].resources.requests.memory", old: "64Mi", new: "128Mi" },
        { type: "ADDED", path: "metadata.annotations.canary_approved", old: null, new: "true" }
      ],
      impact: {
        changed_resource: service,
        blast_radius: {
          criticality: "critical",
          depth: 2,
          total_affected: 3
        },
        affected_services: [service, "database", "postgres-service"],
        subgraph: {
          nodes: [
            { id: service, label: service, type: "Service", namespace: "default", criticality: "critical" },
            { id: "database", label: "database", type: "Database", namespace: "default", criticality: "critical" }
          ],
          edges: [
            { source: service, target: "database", type: "direct" }
          ]
        }
      },
      risk: {
        risk_score: 38,
        risk_level: "MEDIUM",
        blast_radius: {
          criticality: "critical",
          depth: 2,
          total_affected: 3
        },
        affected_services: [service, "database", "postgres-service"]
      },
      recommendation: {
        strategy: "CANARY",
        reason: "Non-breaking image bump to critical tier; canary rollout with automated health evaluation recommended.",
        traffic_steps: [10, 25, 50, 100],
        requires_approval: false
      }
    };
  },

  getRecommendation: async (data) => {
    return {
      strategy: "CANARY",
      reason: "Critical payment tier updated. Recommended progressive canary routing.",
      traffic_steps: [10, 25, 50, 100],
      requires_approval: false
    };
  },

  startDeployment: async (serviceName, newVersion) => {
    const dep = {
      service: serviceName || "payment-service",
      current_version: "v1.4.2",
      target_version: newVersion || "v1.5.0",
      strategy: "CANARY",
      traffic: { stable: 90, canary: 10 },
      status: "IN_PROGRESS",
      health: "HEALTHY",
      percentage: 10
    };
    saveStoredDeployment(dep);
    return dep;
  },

  getDeploymentStatus: async (serviceName) => {
    return getStoredDeployment();
  },

  promoteDeployment: async (serviceName) => {
    const dep = getStoredDeployment();
    const current = dep.traffic.canary || 10;
    const next = current < 25 ? 25 : current < 50 ? 50 : 100;
    dep.traffic = { stable: 100 - next, canary: next };
    dep.percentage = next;
    if (next === 100) {
      dep.status = "SUCCESS";
    }
    saveStoredDeployment(dep);
    return dep;
  },

  stopDeployment: async (serviceName) => {
    const dep = getStoredDeployment();
    dep.status = "PAUSED";
    saveStoredDeployment(dep);
    return dep;
  },

  rollbackDeployment: async (serviceName) => {
    const dep = getStoredDeployment();
    dep.traffic = { stable: 100, canary: 0 };
    dep.percentage = 0;
    dep.status = "ROLLED_BACK";
    saveStoredDeployment(dep);
    return dep;
  },

  getMetrics: async (serviceName) => {
    const jitter = (Math.random() - 0.5) * 4;
    return {
      service: serviceName || "payment-service",
      status: "HEALTHY",
      cpu: { value: Math.max(12, +(28.4 + jitter).toFixed(1)), unit: "m" },
      memory: { value: Math.max(80, +(142.1 + jitter * 2).toFixed(1)), unit: "MB" },
      latency: { value: Math.max(5, +(14.8 + jitter).toFixed(1)), unit: "ms" },
      error_rate: 0.01,
      pod_restarts: 0,
      readiness: 100.0,
      pods: [`${serviceName || 'payment-service'}-canary-1`, `${serviceName || 'payment-service'}-stable-1`],
      service_name: serviceName || "payment-service",
      cpu_usage_mcores: +(28.4 + jitter).toFixed(1),
      memory_usage_mb: +(142.1 + jitter * 2).toFixed(1),
      request_rate_rps: 124.0,
      error_rate_percentage: 0.01,
      latency_ms: +(14.8 + jitter).toFixed(1),
      pod_readiness_percentage: 100.0
    };
  },

  getHealth: async (serviceName) => {
    return {
      service_name: serviceName || "payment-service",
      health_status: "HEALTHY",
      failure_reasons: [],
      metrics: {
        service: serviceName || "payment-service",
        status: "HEALTHY",
        cpu: { value: 28.4, unit: "m" },
        memory: { value: 142.1, unit: "MB" },
        latency: { value: 14.8, unit: "ms" },
        error_rate: 0.01,
        pod_restarts: 0,
        readiness: 100.0
      }
    };
  },

  getHistory: async () => {
    return [
      {
        id: 1,
        service: "payment-service",
        version: "v1.5.0",
        status: "SUCCESS",
        timestamp: new Date(Date.now() - 1000 * 60 * 35).toISOString(),
        health_status: "HEALTHY",
        reason: "Canary promotion verified with 0% error rate."
      },
      {
        id: 2,
        service: "order-service",
        version: "v2.1.0",
        status: "SUCCESS",
        timestamp: new Date(Date.now() - 1000 * 60 * 180).toISOString(),
        health_status: "HEALTHY",
        reason: "Rolling update completed across 3 pods."
      },
      {
        id: 3,
        service: "api-gateway",
        version: "v3.0.2",
        status: "SUCCESS",
        timestamp: new Date(Date.now() - 1000 * 60 * 600).toISOString(),
        health_status: "HEALTHY",
        reason: "Blue/Green router switch passed synthetic checks."
      },
      {
        id: 4,
        service: "auth-service",
        version: "v1.2.0-rc1",
        status: "ROLLED_BACK",
        timestamp: new Date(Date.now() - 1000 * 60 * 1440).toISOString(),
        health_status: "DEGRADED",
        reason: "Automatic rollback triggered: error rate exceeded 2% threshold."
      }
    ];
  },

  getNotifications: async () => {
    return [
      {
        id: "notif-1",
        title: "Canary Traffic Shift",
        message: "payment-service successfully shifted to 25% canary traffic.",
        timestamp: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
        read: false,
        severity: "info"
      },
      {
        id: "notif-2",
        title: "Cluster Health Verified",
        message: "All 3 nodes ready in cloud-production.",
        timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
        read: true,
        severity: "success"
      }
    ];
  },

  markNotificationAsRead: async (id) => ({ success: true, id }),
  markAllNotificationsAsRead: async () => ({ success: true })
};

