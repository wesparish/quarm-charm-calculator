# Docker & Kubernetes Deployment - Complete! 🐳☸️

## ✅ What Was Created

### Docker (`./docker/`)
- **`Dockerfile`** - Multi-stage lightweight container
  - Based on Python 3.10-slim
  - Non-root user (UID 1000)
  - Health checks included
  - ~150MB final image size

- **`README.md`** - Docker build and run instructions
- **`.dockerignore`** - Optimized build context

### Helm Chart (`./helm/quarm-charm-calculator/`)
Production-ready Kubernetes Helm chart with:

**Core Templates:**
- `deployment.yaml` - Multi-replica deployment
- `service.yaml` - ClusterIP service
- `ingress.yaml` - Ingress with TLS support
- `serviceaccount.yaml` - Service account for pods
- `hpa.yaml` - Horizontal Pod Autoscaler
- `pdb.yaml` - Pod Disruption Budget
- `configmap.yaml` - Configuration management
- `_helpers.tpl` - Template helpers

**Configuration:**
- `Chart.yaml` - Chart metadata (v1.0.0)
- `values.yaml` - Default configuration
- `README.md` - Comprehensive documentation

**Documentation:**
- `helm/DEPLOYMENT.md` - Quick deployment guide

## 🚀 Quick Start

### 1. Build Docker Image

```bash
cd ~/workspace/QuarmCharmCalculator

# Build
docker build -f docker/Dockerfile -t quarm-charm-calculator:1.0.0 .

# Test locally
docker run -d -p 5000:5000 --name charm-test quarm-charm-calculator:1.0.0

# Visit http://localhost:5000
# Stop: docker stop charm-test && docker rm charm-test
```

### 2. Deploy to Kubernetes

```bash
# Quick install (development)
helm install quarm-charm ./helm/quarm-charm-calculator

# Check status
kubectl get pods -l app.kubernetes.io/name=quarm-charm-calculator

# Port forward to test
kubectl port-forward svc/quarm-charm-calculator 8080:80

# Visit http://localhost:8080
```

### 3. Production Deployment

```bash
# With ingress and autoscaling
helm install quarm-charm ./helm/quarm-charm-calculator \
  --set replicaCount=3 \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=charm.yourdomain.com \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=3 \
  --set autoscaling.maxReplicas=20
```

## 🎯 Key Features

### Docker Container
✅ **Security:**
- Non-root user (UID 1000)
- Minimal attack surface
- No unnecessary packages

✅ **Performance:**
- Multi-stage build
- Optimized layer caching
- Small image size (~150MB)

✅ **Production-Ready:**
- Health checks
- Proper signal handling
- Resource efficient

### Helm Chart
✅ **High Availability:**
- Multiple replicas (default: 2)
- Pod anti-affinity rules
- Pod Disruption Budget
- Horizontal Pod Autoscaling

✅ **Security:**
- Non-root containers
- Security contexts
- Read-only root filesystem
- Dropped capabilities

✅ **Scalability:**
- HPA based on CPU/Memory
- Configurable resource limits
- Auto-scaling from 2-10 pods

✅ **Observability:**
- Liveness probes
- Readiness probes
- Health check endpoints
- Structured logging

✅ **TLS/HTTPS:**
- Ingress with cert-manager
- Automatic certificate management
- SSL redirect

## 📊 Default Configuration

| Resource | Value |
|----------|-------|
| **Replicas** | 2 |
| **CPU Request** | 100m |
| **CPU Limit** | 500m |
| **Memory Request** | 128Mi |
| **Memory Limit** | 256Mi |
| **Service Port** | 80 → 5000 |
| **Ingress** | Disabled (enable with values) |
| **Autoscaling** | Disabled (enable with values) |

## 🔧 Configuration Examples

### Development
```yaml
# values-dev.yaml
replicaCount: 1
resources:
  limits:
    cpu: 200m
    memory: 128Mi
autoscaling:
  enabled: false
```

### Production
```yaml
# values-prod.yaml
replicaCount: 3
ingress:
  enabled: true
  hosts:
    - host: charm.yourdomain.com
  tls:
    - secretName: charm-tls
      hosts: [charm.yourdomain.com]
resources:
  limits:
    cpu: 1000m
    memory: 512Mi
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
podDisruptionBudget:
  enabled: true
  minAvailable: 2
```

## 📁 File Structure

```
QuarmCharmCalculator/
├── docker/
│   ├── Dockerfile           # Multi-stage container build
│   └── README.md            # Docker documentation
├── helm/
│   ├── DEPLOYMENT.md        # Deployment guide
│   └── quarm-charm-calculator/
│       ├── Chart.yaml       # Chart metadata
│       ├── values.yaml      # Default configuration
│       ├── README.md        # Chart documentation
│       └── templates/       # Kubernetes manifests
│           ├── deployment.yaml
│           ├── service.yaml
│           ├── ingress.yaml
│           ├── hpa.yaml
│           ├── pdb.yaml
│           ├── serviceaccount.yaml
│           ├── configmap.yaml
│           └── _helpers.tpl
└── .dockerignore           # Docker build optimization
```

## 🧪 Testing

### Helm Chart Validation
```bash
# Lint chart
helm lint ./helm/quarm-charm-calculator

# Dry run
helm install quarm-charm ./helm/quarm-charm-calculator --dry-run --debug

# Template output
helm template quarm-charm ./helm/quarm-charm-calculator
```

### Docker Build Test
```bash
# Build
docker build -f docker/Dockerfile -t test:local .

# Run
docker run -d -p 5000:5000 test:local

# Health check
curl http://localhost:5000/

# Logs
docker logs $(docker ps -q --filter ancestor=test:local)
```

## 🌐 Access Methods

### 1. Port Forward (Development)
```bash
kubectl port-forward svc/quarm-charm-calculator 8080:80
# Visit http://localhost:8080
```

### 2. NodePort (Testing)
```yaml
service:
  type: NodePort
  nodePort: 30000
# Visit http://<node-ip>:30000
```

### 3. Ingress (Production)
```yaml
ingress:
  enabled: true
  hosts:
    - host: charm.yourdomain.com
# Visit https://charm.yourdomain.com
```

## 🔄 CI/CD Integration

The setup is ready for:
- GitHub Actions
- GitLab CI
- Jenkins
- ArgoCD
- Flux

See `helm/DEPLOYMENT.md` for CI/CD examples.

## 📝 Next Steps

1. **Push to Registry:**
   ```bash
   docker tag quarm-charm-calculator:1.0.0 your-registry/quarm-charm-calculator:1.0.0
   docker push your-registry/quarm-charm-calculator:1.0.0
   ```

2. **Deploy to Cluster:**
   ```bash
   helm install quarm-charm ./helm/quarm-charm-calculator \
     --set image.repository=your-registry/quarm-charm-calculator \
     --set image.tag=1.0.0
   ```

3. **Configure Ingress:**
   - Update `values.yaml` with your domain
   - Ensure cert-manager is installed
   - Apply ingress configuration

4. **Monitor:**
   ```bash
   kubectl get pods -l app.kubernetes.io/name=quarm-charm-calculator -w
   kubectl logs -l app.kubernetes.io/name=quarm-charm-calculator -f
   ```

## 🎉 Complete!

Your Quarm Charm Calculator is now ready for production deployment to Kubernetes! The container is lightweight, secure, and the Helm chart follows best practices for high availability and scalability.

