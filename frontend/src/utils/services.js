export const AVAILABLE_SERVICES = [
  { id: 'payment-service', label: 'payment-service', desc: 'Critical Payment Gateway & Transaction Tier' },
  { id: 'order-service', label: 'order-service', desc: 'Order Processing & Cart Management' },
  { id: 'api-gateway', label: 'api-gateway', desc: 'Edge Ingress & Route Controller' },
  { id: 'auth-service', label: 'auth-service', desc: 'Identity, OAuth & Security Token Service' },
  { id: 'user-service', label: 'user-service', desc: 'User Accounts & Profile Data' }
];

export const SERVICE_PRESETS = {
  'payment-service': {
    old: `apiVersion: apps/v1
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
`,
    new: `apiVersion: apps/v1
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
`
  },
  'order-service': {
    old: `apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: order
        image: order-service:v2.0.4
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
`,
    new: `apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: order
        image: order-service:v2.1.0
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
`
  },
  'api-gateway': {
    old: `apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: gateway
        image: api-gateway:v1.1
        ports:
        - containerPort: 8080
`,
    new: `apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
spec:
  replicas: 4
  template:
    spec:
      containers:
      - name: gateway
        image: api-gateway:v1.2-rc
        ports:
        - containerPort: 8080
`
  },
  'auth-service': {
    old: `apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: auth
        image: auth:v1.0.0
`,
    new: `apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: auth
        image: auth:v1.1.0
`
  },
  'user-service': {
    old: `apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: user
        image: user-service:v1.0
`,
    new: `apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: user
        image: user-service:v1.1
`
  }
};

