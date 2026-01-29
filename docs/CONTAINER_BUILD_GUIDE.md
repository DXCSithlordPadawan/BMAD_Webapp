# BMAD Forge Container Build Guide

## Overview

This guide covers containerization of BMAD Forge using Docker, including multi-stage builds, security scanning, Docker Compose configuration, and Kubernetes manifests.

## Table of Contents

1. [Dockerfile](#dockerfile)
2. [Docker Compose](#docker-compose)
3. [Security Scanning](#security-scanning)
4. [Kubernetes Manifests](#kubernetes-manifests)
5. [CI/CD Integration](#cicd-integration)

---

## Dockerfile

### Multi-Stage Production Build

```dockerfile
# syntax=docker/dockerfile:1.4

# =============================================================================
# Stage 1: Builder
# =============================================================================
FROM python:3.11-slim-bookworm AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
WORKDIR /build
COPY webapp/requirements.txt webapp/requirements-prod.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt -r requirements-prod.txt

# =============================================================================
# Stage 2: Production
# =============================================================================
FROM python:3.11-slim-bookworm AS production

# Labels for container metadata
LABEL org.opencontainers.image.title="BMAD Forge" \
      org.opencontainers.image.description="BMAD Framework prompt engineering application" \
      org.opencontainers.image.version="1.3.0" \
      org.opencontainers.image.vendor="BMAD Forge Team" \
      org.opencontainers.image.source="https://github.com/example/bmad-forge"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_HOME=/app \
    APP_USER=bmadforge

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd --gid 1000 ${APP_USER} && \
    useradd --uid 1000 --gid ${APP_USER} --shell /bin/bash --create-home ${APP_USER}

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set up application directory
WORKDIR ${APP_HOME}

# Copy application code
COPY --chown=${APP_USER}:${APP_USER} webapp/ .

# Create necessary directories
RUN mkdir -p staticfiles media logs && \
    chown -R ${APP_USER}:${APP_USER} staticfiles media logs

# Collect static files
RUN python manage.py collectstatic --noinput

# Switch to non-root user
USER ${APP_USER}

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", \
     "--worker-class", "gthread", "--worker-tmp-dir", "/dev/shm", \
     "--access-logfile", "-", "--error-logfile", "-", \
     "--capture-output", "--enable-stdio-inheritance", \
     "bmad_forge.wsgi:application"]
```

### Development Dockerfile

```dockerfile
# Dockerfile.dev
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY webapp/requirements.txt webapp/requirements-dev.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt -r requirements-dev.txt

COPY webapp/ .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

---

## Docker Compose

### Production Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    image: bmad-forge:${VERSION:-latest}
    container_name: bmad-forge-web
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS:-localhost}
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - REDIS_URL=redis://redis:6379/0
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - SENTRY_DSN=${SENTRY_DSN:-}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - bmad-network
    volumes:
      - static_files:/app/staticfiles
      - media_files:/app/media
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M

  db:
    image: postgres:15-alpine
    container_name: bmad-forge-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${DB_NAME:-bmad_forge}
      - POSTGRES_USER=${DB_USER:-bmad_forge}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - bmad-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-bmad_forge} -d ${DB_NAME:-bmad_forge}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: bmad-forge-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - bmad-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:1.25-alpine
    container_name: bmad-forge-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - static_files:/var/www/static:ro
      - media_files:/var/www/media:ro
      - ./certbot/conf:/etc/letsencrypt:ro
      - ./certbot/www:/var/www/certbot:ro
    depends_on:
      - web
    networks:
      - bmad-network

networks:
  bmad-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  static_files:
  media_files:
```

### Development Configuration

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.dev
    container_name: bmad-forge-dev
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
      - SECRET_KEY=dev-secret-key-not-for-production
      - DATABASE_URL=postgresql://bmad_forge:devpassword@db:5432/bmad_forge
    depends_on:
      - db
    volumes:
      - ./webapp:/app
    command: python manage.py runserver 0.0.0.0:8000

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=bmad_forge
      - POSTGRES_USER=bmad_forge
      - POSTGRES_PASSWORD=devpassword
    ports:
      - "5432:5432"
    volumes:
      - dev_postgres_data:/var/lib/postgresql/data

volumes:
  dev_postgres_data:
```

---

## Security Scanning

### Container Image Scanning

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  trivy-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build image
        run: docker build -t bmad-forge:scan .

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'bmad-forge:scan'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'

  hadolint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Lint Dockerfile
        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: Dockerfile
          failure-threshold: warning
```

### Manual Scanning Commands

```bash
# Scan with Trivy
trivy image bmad-forge:latest

# Scan with Grype
grype bmad-forge:latest

# Scan with Dockle (best practices)
dockle bmad-forge:latest

# Scan Dockerfile with Hadolint
hadolint Dockerfile
```

---

## Kubernetes Manifests

### Namespace and ConfigMap

```yaml
# kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: bmad-forge
  labels:
    name: bmad-forge

---
# kubernetes/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: bmad-forge-config
  namespace: bmad-forge
data:
  ALLOWED_HOSTS: "bmad-forge.example.com"
  DEBUG: "False"
  DJANGO_SETTINGS_MODULE: "bmad_forge.settings.production"
```

### Secrets

```yaml
# kubernetes/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: bmad-forge-secrets
  namespace: bmad-forge
type: Opaque
stringData:
  SECRET_KEY: "your-secret-key-here"
  DATABASE_URL: "postgresql://user:pass@postgres:5432/bmad_forge"
  REDIS_URL: "redis://redis:6379/0"
  GITHUB_TOKEN: "ghp_xxxx"
  SENTRY_DSN: "https://xxx@sentry.io/xxx"
```

### Deployment

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bmad-forge
  namespace: bmad-forge
  labels:
    app: bmad-forge
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bmad-forge
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: bmad-forge
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      serviceAccountName: bmad-forge
      containers:
        - name: bmad-forge
          image: bmad-forge:1.3.0
          imagePullPolicy: Always
          ports:
            - name: http
              containerPort: 8000
              protocol: TCP
          envFrom:
            - configMapRef:
                name: bmad-forge-config
            - secretRef:
                name: bmad-forge-secrets
          resources:
            requests:
              cpu: "250m"
              memory: "512Mi"
            limits:
              cpu: "1000m"
              memory: "2Gi"
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          volumeMounts:
            - name: tmp
              mountPath: /tmp
            - name: static
              mountPath: /app/staticfiles
          livenessProbe:
            httpGet:
              path: /health/
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health/
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
      volumes:
        - name: tmp
          emptyDir: {}
        - name: static
          emptyDir: {}
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: kubernetes.io/hostname
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: bmad-forge
```

### Service and Ingress

```yaml
# kubernetes/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: bmad-forge
  namespace: bmad-forge
  labels:
    app: bmad-forge
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: http
      protocol: TCP
      name: http
  selector:
    app: bmad-forge

---
# kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bmad-forge
  namespace: bmad-forge
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
spec:
  tls:
    - hosts:
        - bmad-forge.example.com
      secretName: bmad-forge-tls
  rules:
    - host: bmad-forge.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: bmad-forge
                port:
                  number: 80
```

### Horizontal Pod Autoscaler

```yaml
# kubernetes/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bmad-forge
  namespace: bmad-forge
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: bmad-forge
  minReplicas: 2
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
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
        - type: Pods
          value: 4
          periodSeconds: 15
      selectPolicy: Max
```

### Network Policy

```yaml
# kubernetes/networkpolicy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: bmad-forge-network-policy
  namespace: bmad-forge
spec:
  podSelector:
    matchLabels:
      app: bmad-forge
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
          port: 8000
  egress:
    # Allow DNS
    - to:
        - namespaceSelector: {}
      ports:
        - protocol: UDP
          port: 53
    # Allow PostgreSQL
    - to:
        - namespaceSelector:
            matchLabels:
              name: database
      ports:
        - protocol: TCP
          port: 5432
    # Allow Redis
    - to:
        - namespaceSelector:
            matchLabels:
              name: cache
      ports:
        - protocol: TCP
          port: 6379
    # Allow HTTPS (GitHub API, Sentry)
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0
      ports:
        - protocol: TCP
          port: 443
```

---

## CI/CD Integration

### Build and Push Pipeline

```yaml
# .github/workflows/build.yml
name: Build and Push

on:
  push:
    branches: [main]
    tags: ['v*']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      security-events: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=sha,prefix=

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Run Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload scan results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
```

---

## Quick Reference

### Build Commands

```bash
# Build production image
docker build -t bmad-forge:latest .

# Build with specific target
docker build --target production -t bmad-forge:prod .

# Build development image
docker build -f Dockerfile.dev -t bmad-forge:dev .

# Build with build args
docker build --build-arg VERSION=1.3.0 -t bmad-forge:1.3.0 .
```

### Run Commands

```bash
# Run with Docker Compose
docker-compose up -d

# Run development environment
docker-compose -f docker-compose.dev.yml up

# View logs
docker-compose logs -f web

# Execute management command
docker-compose exec web python manage.py migrate

# Shell access
docker-compose exec web /bin/bash
```

### Kubernetes Commands

```bash
# Apply manifests
kubectl apply -f kubernetes/

# Check deployment status
kubectl -n bmad-forge get pods

# View logs
kubectl -n bmad-forge logs -f deployment/bmad-forge

# Execute command in pod
kubectl -n bmad-forge exec -it deployment/bmad-forge -- python manage.py shell

# Port forward for debugging
kubectl -n bmad-forge port-forward svc/bmad-forge 8000:80
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-29 | DevOps Team | Initial document |
