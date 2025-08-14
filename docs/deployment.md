# Deployment Guide

This guide provides comprehensive instructions for deploying the Drift Watch Backend application in various environments, from local development to production cloud deployments.

## Deployment Overview

The Drift Watch Backend is designed as a cloud-native application with support for:

- **Containerization**: Docker-based deployments
- **Orchestration**: Kubernetes deployments  
- **Cloud Platforms**: AWS, Azure, Google Cloud Platform
- **Traditional Deployments**: Virtual machines and bare metal

## Prerequisites

### System Requirements

**Minimum Requirements**:

- **CPU**: 2 cores
- **Memory**: 4GB RAM
- **Storage**: 20GB available space
- **Network**: HTTPS connectivity for authentication

**Recommended for Production**:

- **CPU**: 4+ cores
- **Memory**: 8+ GB RAM
- **Storage**: 100+ GB available space
- **Database**: Dedicated MongoDB cluster

### Software Dependencies

- **Python 3.11+**: Application runtime
- **MongoDB 6.0+**: Database system
- **Docker 20.10+**: Container runtime (for containerized deployments)
- **Kubernetes 1.24+**: Container orchestration (for K8s deployments)

## Docker Deployment

### Building the Docker Image

Create the Docker image from the project root:

```bash
# Build the image
docker build -t drift-watch-backend:latest .

# Tag for registry
docker tag drift-watch-backend:latest your-registry/drift-watch-backend:v1.0.0

# Push to registry
docker push your-registry/drift-watch-backend:v1.0.0
```

### Docker Compose Deployment

Create a `docker-compose.yml` file for local or simple deployments:

```yaml
version: '3.8'

services:
  # Application Service
  drift-watch-backend:
    build: .
    # Or use pre-built image:
    # image: your-registry/drift-watch-backend:latest
    
    environment:
      # Database Configuration
      - APP_DATABASE_HOST=mongodb
      - APP_DATABASE_PORT=27017
      - APP_DATABASE_NAME=drift-watch
      - APP_DATABASE_USERNAME=drift_user
      
      # Authentication Configuration
      - APP_TRUSTED_OP_LIST=["https://your-auth-provider.com"]
      - APP_USERS_ENTITLEMENTS=["drift-watch-user"]
      - APP_ADMIN_ENTITLEMENTS=["drift-watch-admin"]
      
      # API Configuration
      - APP_API_TITLE=Drift Watch API
      - APP_SECRETS_DIR=/app/secrets
    
    volumes:
      - ./secrets:/app/secrets:ro
      - ./logs:/app/logs
    
    ports:
      - "5000:5000"
    
    depends_on:
      - mongodb
      - mongo-setup
    
    restart: unless-stopped
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Database Service
  mongodb:
    image: mongo:6.0.3
    
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=admin_secure_password
      - MONGO_INITDB_DATABASE=drift-watch
    
    ports:
      - "27017:27017"
    
    volumes:
      - mongodb_data:/data/db
      - ./mongo-init:/docker-entrypoint-initdb.d:ro
    
    restart: unless-stopped
    
    command: mongod --auth

  # Database Initialization
  mongo-setup:
    image: mongo:6.0.3
    depends_on:
      - mongodb
    volumes:
      - ./mongo-init/init-users.js:/init-users.js:ro
    command: >
      bash -c "
        sleep 10 &&
        mongosh --host mongodb --authenticationDatabase admin 
                --username admin --password admin_secure_password
                --eval 'load(\"/init-users.js\")'
      "

volumes:
  mongodb_data:
    driver: local

networks:
  default:
    driver: bridge
```

### MongoDB Initialization Script

Create `mongo-init/init-users.js`:

```javascript
// Create application database and user
use('drift-watch');

db.createUser({
  user: 'drift_user',
  pwd: 'user_secure_password',
  roles: [
    {
      role: 'readWrite',
      db: 'drift-watch'
    }
  ]
});

// Create initial indexes
db.experiments.createIndex({ "created_at": -1 });
db.experiments.createIndex({ "name": 1 }, { unique: true });
db.experiments.createIndex({ "permissions.user": 1 });

db.drifts.createIndex({ "experiment_id": 1, "created_at": -1 });
db.drifts.createIndex({ "model_name": 1 });
db.drifts.createIndex({ "drift_score": -1 });

console.log("Database initialization completed");
```

### Secrets Configuration

Create the secrets directory structure:

```bash
mkdir -p secrets
echo "user_secure_password" > secrets/app_database_password
echo '["https://your-auth-provider.com"]' > secrets/app_trusted_op_list
echo '["drift-watch-user"]' > secrets/app_users_entitlements
echo '["drift-watch-admin"]' > secrets/app_admin_entitlements
```

### Running with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f drift-watch-backend

# Check service status
docker-compose ps

# Stop services
docker-compose down

# Stop and remove volumes (careful: deletes data)
docker-compose down -v
```

## Kubernetes Deployment

### Namespace Setup

Create a dedicated namespace:

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: drift-watch
  labels:
    name: drift-watch
```

### ConfigMap Configuration

Create configuration for non-sensitive data:

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: drift-watch-config
  namespace: drift-watch
data:
  # Database Configuration
  APP_DATABASE_HOST: "mongodb-service"
  APP_DATABASE_PORT: "27017"
  APP_DATABASE_NAME: "drift-watch"
  APP_DATABASE_USERNAME: "drift_user"
  
  # API Configuration
  APP_API_TITLE: "Drift Watch API"
  APP_API_VERSION: "1.0.0"
  APP_SECRETS_DIR: "/app/secrets"
  
  # Authentication Configuration
  APP_ENTITLEMENTS_PATH: "realm_access/roles"
  APP_TRUSTED_OP_LIST: |
    ["https://your-auth-provider.com"]
  APP_USERS_ENTITLEMENTS: |
    ["drift-watch-user", "platform-access"]
```

### Secret Configuration

Create secrets for sensitive data:

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: drift-watch-secrets
  namespace: drift-watch
type: Opaque
stringData:
  # Database Password
  app_database_password: "user_secure_password"
  
  # Admin Entitlements
  app_admin_entitlements: |
    ["drift-watch-admin", "platform-admin"]
  
  # MongoDB Admin Password (for database setup)
  mongodb_root_password: "admin_secure_password"
  mongodb_user_password: "user_secure_password"
```

### MongoDB Deployment

Deploy MongoDB as a StatefulSet:

```yaml
# mongodb.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
  namespace: drift-watch
spec:
  serviceName: mongodb-service
  replicas: 1
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:6.0.3
        
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          value: "admin"
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: drift-watch-secrets
              key: mongodb_root_password
        - name: MONGO_INITDB_DATABASE
          value: "drift-watch"
        
        ports:
        - containerPort: 27017
        
        volumeMounts:
        - name: mongodb-data
          mountPath: /data/db
        - name: mongodb-init
          mountPath: /docker-entrypoint-initdb.d
        
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      
      volumes:
      - name: mongodb-init
        configMap:
          name: mongodb-init-scripts
  
  volumeClaimTemplates:
  - metadata:
      name: mongodb-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi

---
apiVersion: v1
kind: Service
metadata:
  name: mongodb-service
  namespace: drift-watch
spec:
  selector:
    app: mongodb
  ports:
  - port: 27017
    targetPort: 27017
  clusterIP: None  # Headless service for StatefulSet
```

### Application Deployment

Deploy the application:

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: drift-watch-backend
  namespace: drift-watch
  labels:
    app: drift-watch-backend
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  
  selector:
    matchLabels:
      app: drift-watch-backend
  
  template:
    metadata:
      labels:
        app: drift-watch-backend
    spec:
      containers:
      - name: backend
        image: your-registry/drift-watch-backend:latest
        
        envFrom:
        - configMapRef:
            name: drift-watch-config
        
        volumeMounts:
        - name: secrets-volume
          mountPath: /app/secrets
          readOnly: true
        
        ports:
        - containerPort: 5000
        
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
      
      volumes:
      - name: secrets-volume
        secret:
          secretName: drift-watch-secrets

---
apiVersion: v1
kind: Service
metadata:
  name: drift-watch-service
  namespace: drift-watch
spec:
  selector:
    app: drift-watch-backend
  ports:
  - port: 80
    targetPort: 5000
    protocol: TCP
  type: ClusterIP
```

### Ingress Configuration

Expose the application with ingress:

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: drift-watch-ingress
  namespace: drift-watch
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.drift-watch.your-domain.com
    secretName: drift-watch-tls
  
  rules:
  - host: api.drift-watch.your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: drift-watch-service
            port:
              number: 80
```

### Kubernetes Deployment Commands

Deploy to Kubernetes:

```bash
# Create namespace
kubectl apply -f namespace.yaml

# Deploy configuration
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml

# Deploy database
kubectl apply -f mongodb.yaml

# Wait for database to be ready
kubectl wait --for=condition=ready pod -l app=mongodb -n drift-watch --timeout=300s

# Deploy application
kubectl apply -f deployment.yaml

# Expose application
kubectl apply -f ingress.yaml

# Check deployment status
kubectl get all -n drift-watch

# View logs
kubectl logs -f deployment/drift-watch-backend -n drift-watch
```

## Cloud Platform Deployments

### AWS Deployment

#### ECS (Elastic Container Service)

Create task definition:

```json
{
  "family": "drift-watch-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/drift-watch-task-role",
  
  "containerDefinitions": [
    {
      "name": "drift-watch-backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/drift-watch-backend:latest",
      
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      
      "environment": [
        {
          "name": "APP_DATABASE_HOST",
          "value": "documentdb-cluster.cluster-xxx.region.docdb.amazonaws.com"
        },
        {
          "name": "APP_DATABASE_PORT", 
          "value": "27017"
        },
        {
          "name": "APP_DATABASE_NAME",
          "value": "drift-watch"
        }
      ],
      
      "secrets": [
        {
          "name": "APP_DATABASE_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:drift-watch/database-xxx:password::"
        }
      ],
      
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/drift-watch-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:5000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

#### DocumentDB Configuration

Set up AWS DocumentDB cluster:

```bash
# Create DocumentDB cluster
aws docdb create-db-cluster \
  --db-cluster-identifier drift-watch-cluster \
  --engine docdb \
  --master-username admin \
  --master-user-password SecurePassword123 \
  --vpc-security-group-ids sg-xxxxxxxxx \
  --db-subnet-group-name drift-watch-subnet-group

# Create DocumentDB instance
aws docdb create-db-instance \
  --db-cluster-identifier drift-watch-cluster \
  --db-instance-identifier drift-watch-instance \
  --db-instance-class db.t3.medium \
  --engine docdb
```

### Azure Deployment

#### Azure Container Instances

Deploy with Azure CLI:

```bash
# Create resource group
az group create --name drift-watch-rg --location eastus

# Create Azure Container Registry
az acr create --resource-group drift-watch-rg --name driftwatchacr --sku Basic

# Push image to ACR
az acr build --registry driftwatchacr --image drift-watch-backend:latest .

# Create Cosmos DB (MongoDB API)
az cosmosdb create \
  --resource-group drift-watch-rg \
  --name drift-watch-cosmos \
  --kind MongoDB \
  --server-version "4.0"

# Deploy container instance
az container create \
  --resource-group drift-watch-rg \
  --name drift-watch-backend \
  --image driftwatchacr.azurecr.io/drift-watch-backend:latest \
  --cpu 2 \
  --memory 4 \
  --ports 5000 \
  --environment-variables \
    APP_DATABASE_HOST=drift-watch-cosmos.mongo.cosmos.azure.com \
    APP_DATABASE_PORT=10255 \
  --secure-environment-variables \
    APP_DATABASE_PASSWORD=primary-connection-string
```

### Google Cloud Platform

#### Cloud Run Deployment

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/drift-watch-backend

# Deploy to Cloud Run
gcloud run deploy drift-watch-backend \
  --image gcr.io/PROJECT_ID/drift-watch-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars APP_DATABASE_HOST=mongodb-atlas-cluster.xxx.mongodb.net \
  --set-env-vars APP_DATABASE_PORT=27017 \
  --memory 1Gi \
  --cpu 1 \
  --concurrency 80 \
  --timeout 300
```

## Production Considerations

### High Availability

#### Database Replication

Set up MongoDB replica set:

```javascript
// Initialize replica set
rs.initiate({
  _id: "drift-watch-replica",
  members: [
    { _id: 0, host: "mongo1:27017", priority: 2 },
    { _id: 1, host: "mongo2:27017", priority: 1 },
    { _id: 2, host: "mongo3:27017", priority: 1, arbiterOnly: true }
  ]
});
```

#### Application Scaling

Configure horizontal pod autoscaling:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: drift-watch-hpa
  namespace: drift-watch
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: drift-watch-backend
  
  minReplicas: 3
  maxReplicas: 10
  
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Monitoring and Logging

#### Prometheus Monitoring

```yaml
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: drift-watch-metrics
  namespace: drift-watch
spec:
  selector:
    matchLabels:
      app: drift-watch-backend
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

#### Centralized Logging

Configure log aggregation:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*drift-watch*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      format json
    </source>
    
    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch.logging.svc.cluster.local
      port 9200
      index_name drift-watch-logs
    </match>
```

### Security Configuration

#### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: drift-watch-network-policy
  namespace: drift-watch
spec:
  podSelector:
    matchLabels:
      app: drift-watch-backend
  
  policyTypes:
  - Ingress
  - Egress
  
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 5000
  
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: mongodb
    ports:
    - protocol: TCP
      port: 27017
```

This deployment guide provides comprehensive instructions for deploying the Drift Watch Backend application across various platforms and environments, from simple Docker deployments to complex cloud-native architectures.
