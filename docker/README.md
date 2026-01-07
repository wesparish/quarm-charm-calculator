# Docker build and run instructions

## Building the Image

```bash
# From the project root directory
docker build -f docker/Dockerfile -t quarm-charm-calculator:latest .
```

## Running Locally

```bash
# Run the container
docker run -d \
  --name quarm-charm \
  -p 5000:5000 \
  --restart unless-stopped \
  quarm-charm-calculator:latest

# View logs
docker logs -f quarm-charm

# Stop the container
docker stop quarm-charm

# Remove the container
docker rm quarm-charm
```

## Building for Multiple Architectures

```bash
# Build for AMD64 and ARM64
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f docker/Dockerfile \
  -t quarm-charm-calculator:latest \
  --push \
  .
```

## Production Deployment

For production, consider:
1. Using a container registry (Docker Hub, GitHub Container Registry, etc.)
2. Adding volume mounts for persistent data
3. Setting resource limits
4. Using docker-compose for easier management

Example docker-compose.yml:

```yaml
version: '3.8'

services:
  quarm-charm-calculator:
    image: quarm-charm-calculator:latest
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "5000:5000"
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.1'
          memory: 128M
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5000/', timeout=2)"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
```

## Environment Variables

The application supports these environment variables:
- `FLASK_ENV`: Set to `production` for production deployments
- `FLASK_DEBUG`: Set to `0` for production

## Security Notes

- The container runs as non-root user (uid 1000)
- Uses multi-stage build for smaller image size
- No unnecessary packages installed
- Health checks included

