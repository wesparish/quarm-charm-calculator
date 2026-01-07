# Kubernetes Deployment Guide

## Quick Start

### 1. Build and Push Docker Image

```bash
# Build the image
docker build -f docker/Dockerfile -t quarm-charm-calculator:1.0.0 .

# Tag for your registry (example with Docker Hub)
docker tag quarm-charm-calculator:1.0.0 yourusername/quarm-charm-calculator:1.0.0

# Push to registry
docker push yourusername/quarm-charm-calculator:1.0.0
```

### 2. Deploy with Helm

```bash
# Install the chart
helm install quarm-charm ./helm/quarm-charm-calculator \
  --set image.repository=yourusername/quarm-charm-calculator \
  --set image.tag=1.0.0

# Check status
kubectl get pods -l app.kubernetes.io/name=quarm-charm-calculator

# Port forward to test locally
kubectl port-forward svc/quarm-charm-calculator 8080:80

# Visit http://localhost:8080
```

### 3. Enable Ingress (Optional)

```bash
# Update values
helm upgrade quarm-charm ./helm/quarm-charm-calculator \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=charm.yourdomain.com \
  --set ingress.hosts[0].paths[0].path=/ \
  --set ingress.hosts[0].paths[0].pathType=Prefix
```

## Production Deployment

For production, create a `values-prod.yaml`:

```yaml
replicaCount: 3

image:
  repository: yourusername/quarm-charm-calculator
  tag: "1.0.0"
  pullPolicy: Always

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: charm.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: charm-calculator-tls
      hosts:
        - charm.yourdomain.com

resources:
  limits:
    cpu: 1000m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
```

Then deploy:

```bash
helm install quarm-charm ./helm/quarm-charm-calculator -f values-prod.yaml
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Deploy

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: docker build -f docker/Dockerfile -t ${{ secrets.REGISTRY }}/quarm-charm-calculator:${{ github.sha }} .

      - name: Push to registry
        run: docker push ${{ secrets.REGISTRY }}/quarm-charm-calculator:${{ github.sha }}

      - name: Deploy to Kubernetes
        run: |
          helm upgrade --install quarm-charm ./helm/quarm-charm-calculator \
            --set image.tag=${{ github.sha }} \
            --set image.repository=${{ secrets.REGISTRY }}/quarm-charm-calculator
```

## Monitoring and Observability

### Prometheus Metrics (Future Enhancement)

Add to `values.yaml`:

```yaml
metrics:
  enabled: true
  serviceMonitor:
    enabled: true
```

### Grafana Dashboard

Import the provided dashboard JSON from `helm/dashboards/` (create if needed).

## Troubleshooting

See the [Helm Chart README](./helm/quarm-charm-calculator/README.md) for detailed troubleshooting steps.

