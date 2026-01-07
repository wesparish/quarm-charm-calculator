# Quarm Charm Calculator Helm Chart

A production-ready Helm chart for deploying the Quarm Charm Calculator to Kubernetes.

## Features

- ✅ Multi-replica deployment with anti-affinity
- ✅ Horizontal Pod Autoscaling (HPA)
- ✅ Pod Disruption Budget (PDB)
- ✅ Resource limits and requests
- ✅ Health checks (liveness & readiness probes)
- ✅ Security context (non-root user)
- ✅ Ingress with TLS support
- ✅ Service Account
- ✅ ConfigMap for configuration

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- An Ingress Controller (if using ingress)
- cert-manager (if using TLS)

## Installation

### Quick Start

```bash
# Install from the helm directory
helm install quarm-charm ./helm/quarm-charm-calculator

# Or install with custom values
helm install quarm-charm ./helm/quarm-charm-calculator -f my-values.yaml
```

### With Ingress Enabled

```bash
helm install quarm-charm ./helm/quarm-charm-calculator \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=charm.example.com \
  --set ingress.hosts[0].paths[0].path=/ \
  --set ingress.hosts[0].paths[0].pathType=Prefix
```

### With Custom Image

```bash
helm install quarm-charm ./helm/quarm-charm-calculator \
  --set image.repository=myregistry.io/quarm-charm-calculator \
  --set image.tag=v1.0.0
```

## Configuration

### Key Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `2` |
| `image.repository` | Image repository | `quarm-charm-calculator` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `80` |
| `ingress.enabled` | Enable ingress | `false` |
| `ingress.className` | Ingress class name | `nginx` |
| `ingress.hosts` | Ingress hosts | `[]` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `256Mi` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `128Mi` |
| `autoscaling.enabled` | Enable HPA | `false` |
| `autoscaling.minReplicas` | Minimum replicas | `2` |
| `autoscaling.maxReplicas` | Maximum replicas | `10` |

### Example Values Files

#### Production Deployment

```yaml
# values-prod.yaml
replicaCount: 3

image:
  repository: myregistry.io/quarm-charm-calculator
  tag: "1.0.0"
  pullPolicy: Always

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: charm.mydomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: charm-calculator-tls
      hosts:
        - charm.mydomain.com

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
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

podDisruptionBudget:
  enabled: true
  minAvailable: 2
```

#### Development Deployment

```yaml
# values-dev.yaml
replicaCount: 1

image:
  repository: quarm-charm-calculator
  tag: latest
  pullPolicy: Always

resources:
  limits:
    cpu: 200m
    memory: 128Mi
  requests:
    cpu: 50m
    memory: 64Mi

autoscaling:
  enabled: false

podDisruptionBudget:
  enabled: false
```

## Usage

### Install

```bash
# Development
helm install quarm-charm ./helm/quarm-charm-calculator -f values-dev.yaml

# Production
helm install quarm-charm ./helm/quarm-charm-calculator -f values-prod.yaml
```

### Upgrade

```bash
helm upgrade quarm-charm ./helm/quarm-charm-calculator -f values-prod.yaml
```

### Uninstall

```bash
helm uninstall quarm-charm
```

### View Status

```bash
# Check deployment status
helm status quarm-charm

# Get values
helm get values quarm-charm

# List releases
helm list
```

## Monitoring

### Check Pods

```bash
kubectl get pods -l app.kubernetes.io/name=quarm-charm-calculator
```

### View Logs

```bash
kubectl logs -l app.kubernetes.io/name=quarm-charm-calculator -f
```

### Check Service

```bash
kubectl get svc -l app.kubernetes.io/name=quarm-charm-calculator
```

### Check Ingress

```bash
kubectl get ingress
```

## Troubleshooting

### Pod not starting

```bash
# Describe pod
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

### Ingress not working

```bash
# Check ingress
kubectl describe ingress quarm-charm-calculator

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

### Certificate issues

```bash
# Check certificate
kubectl get certificate

# Check cert-manager logs
kubectl logs -n cert-manager -l app=cert-manager
```

## Security

The chart implements several security best practices:

- Non-root user (UID 1000)
- Read-only root filesystem (where possible)
- Security context with dropped capabilities
- Resource limits to prevent resource exhaustion
- Pod Security Standards compatible

## High Availability

For production deployments:

1. Set `replicaCount` >= 3
2. Enable `podDisruptionBudget`
3. Configure anti-affinity rules (enabled by default)
4. Enable `autoscaling` for dynamic scaling
5. Set appropriate resource requests/limits

## Backup and Recovery

Since this is a stateless application, no backup is required. Simply redeploy with the same Helm chart.

## Contributing

To modify the chart:

1. Edit values in `values.yaml`
2. Update templates in `templates/`
3. Increment version in `Chart.yaml`
4. Test with `helm lint ./helm/quarm-charm-calculator`
5. Package with `helm package ./helm/quarm-charm-calculator`

## License

Same as the application license.

