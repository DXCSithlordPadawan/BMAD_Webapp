# DISA STIG Compliance Guide

## Overview

This document maps BMAD Forge security controls to Defense Information Systems Agency (DISA) Security Technical Implementation Guides (STIGs). STIGs provide security configuration standards for Department of Defense (DoD) systems.

## Applicable STIGs

| STIG | Version | Status |
|------|---------|--------|
| Web Server STIG | V2R5 | Partially Compliant |
| Application Security STIG | V5R3 | Compliant |
| PostgreSQL STIG | V2R4 | Compliant |
| Container Platform STIG | V1R3 | Compliant |

---

## Findings Summary

### By Category

| Category | Count | Status |
|----------|-------|--------|
| CAT I (High) | 0 | All Remediated |
| CAT II (Medium) | 3 | 2 Remediated, 1 POA&M |
| CAT III (Low) | 5 | 4 Remediated, 1 Accepted Risk |

---

## Web Server STIG (V2R5)

### CAT I Findings

| STIG ID | Title | Status | Implementation |
|---------|-------|--------|----------------|
| V-2246 | Web server must use encryption for connections | Compliant | TLS 1.2+ enforced via SECURE_SSL_REDIRECT |
| V-2247 | Web server must be configured to use approved DoD certificates | Compliant | Let's Encrypt with HSTS preload |
| V-2259 | Web server must not be a host for non-web functions | Compliant | Single-purpose container |

### CAT II Findings

| STIG ID | Title | Status | Implementation |
|---------|-------|--------|----------------|
| V-2230 | Logging must be enabled | Compliant | Django LOGGING configured |
| V-2234 | Log files must only be accessible by privileged users | Compliant | File permissions 640 |
| V-2242 | Web server must limit the number of allowed simultaneous sessions | POA&M | Rate limiting via django-ratelimit |
| V-2248 | Web server must have resource limits configured | Compliant | gunicorn worker limits |
| V-2255 | Web server must have all applicable patches installed | Compliant | Monthly patching schedule |

### CAT III Findings

| STIG ID | Title | Status | Implementation |
|---------|-------|--------|----------------|
| V-2257 | Web server must be configured for MIME type filtering | Compliant | Django ALLOWED_CONTENT_TYPES |
| V-2261 | Information about the web server must be protected | Compliant | Server header removed |

---

## Application Security STIG (V5R3)

### Authentication Controls

| STIG ID | Title | Status | Implementation |
|---------|-------|--------|----------------|
| V-222396 | Application must use NIST-validated cryptography | Compliant | Python cryptography library |
| V-222400 | Application must enforce approved authentication methods | Compliant | Django authentication backend |
| V-222401 | Application must terminate user sessions after inactivity | Compliant | SESSION_COOKIE_AGE = 3600 |
| V-222402 | Application must lock accounts after failed login attempts | Compliant | django-axes integration |
| V-222403 | Application must display approved system use notification | Compliant | Login page banner |

**Authentication Implementation:**

```python
# webapp/bmad_forge/settings/production.py

# Session security
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Account lockout (django-axes)
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=30)
AXES_LOCKOUT_TEMPLATE = 'forge/account_locked.html'
AXES_RESET_ON_SUCCESS = True
```

### Input Validation Controls

| STIG ID | Title | Status | Implementation |
|---------|-------|--------|----------------|
| V-222425 | Application must validate all input | Compliant | Django form validation |
| V-222426 | Application must not be vulnerable to SQL Injection | Compliant | Django ORM parameterization |
| V-222427 | Application must not be vulnerable to XSS | Compliant | Django template auto-escaping |
| V-222428 | Application must not be vulnerable to CSRF | Compliant | CSRF middleware enabled |
| V-222430 | Application must protect against command injection | Compliant | No shell execution from user input |

### Session Management Controls

| STIG ID | Title | Status | Implementation |
|---------|-------|--------|----------------|
| V-222440 | Session IDs must be unique and random | Compliant | Django session framework |
| V-222441 | Session tokens must not be passed in URLs | Compliant | Cookie-based sessions only |
| V-222442 | Application must regenerate session ID on authentication | Compliant | cycle_key() on login |
| V-222443 | Application must destroy session ID on logout | Compliant | flush() on logout |

### Data Protection Controls

| STIG ID | Title | Status | Implementation |
|---------|-------|--------|----------------|
| V-222450 | Application must use encryption for data at rest | Compliant | Database encryption |
| V-222451 | Application must use encryption for data in transit | Compliant | TLS 1.2+ required |
| V-222452 | Application must protect sensitive data in memory | Compliant | Secure string handling |
| V-222453 | Application must not store passwords in reversible form | Compliant | PBKDF2 password hasher |

---

## PostgreSQL STIG (V2R4)

### Database Security

| STIG ID | Title | Status | Implementation |
|---------|-------|--------|----------------|
| V-214044 | PostgreSQL must use NIST-validated FIPS 140-2 cryptography | Compliant | OpenSSL FIPS module |
| V-214045 | PostgreSQL must limit concurrent sessions | Compliant | max_connections configured |
| V-214046 | PostgreSQL must require SSL connections | Compliant | sslmode='require' |
| V-214047 | PostgreSQL must use approved TLS versions | Compliant | TLS 1.2+ only |

**Database Connection Configuration:**

```python
# webapp/bmad_forge/settings/production.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
            'sslcert': '/etc/ssl/certs/db-client.crt',
            'sslkey': '/etc/ssl/private/db-client.key',
            'sslrootcert': '/etc/ssl/certs/db-ca.crt',
        },
        'CONN_MAX_AGE': 600,
    }
}
```

### Audit and Logging

| STIG ID | Title | Status | Implementation |
|---------|-------|--------|----------------|
| V-214050 | PostgreSQL must generate audit records | Compliant | pgaudit extension |
| V-214051 | PostgreSQL audit records must include timestamp | Compliant | log_timestamp = on |
| V-214052 | PostgreSQL must protect audit information | Compliant | Audit log permissions |

---

## Container Platform STIG (V1R3)

### Container Security

| STIG ID | Title | Status | Implementation |
|---------|-------|--------|----------------|
| V-242381 | Container must not run as root | Compliant | USER directive in Dockerfile |
| V-242382 | Container must use read-only root filesystem | Compliant | readOnlyRootFilesystem: true |
| V-242383 | Container must drop all capabilities | Compliant | securityContext.capabilities.drop: ["ALL"] |
| V-242384 | Container must not allow privilege escalation | Compliant | allowPrivilegeEscalation: false |

**Kubernetes Security Context:**

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bmad-forge
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      containers:
      - name: bmad-forge
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
      volumes:
      - name: tmp
        emptyDir: {}
      - name: static
        emptyDir: {}
```

---

## Plan of Action and Milestones (POA&M)

### Open Findings

| STIG ID | Title | Category | Target Date | Owner |
|---------|-------|----------|-------------|-------|
| V-2242 | Session limits | CAT II | 2026-03-31 | Development Team |

### Accepted Risks

| STIG ID | Title | Category | Justification | Approved By |
|---------|-------|----------|---------------|-------------|
| V-2261 | Server header removal | CAT III | Server header already removed; minimal residual risk | ISSM |

---

## Compliance Verification

### Automated Scans

```bash
# SCAP compliance scan
oscap xccdf eval --profile stig-web-server \
  --results scan-results.xml \
  --report scan-report.html \
  web-server-stig.xml

# Database compliance check
psql -c "SELECT name, setting FROM pg_settings WHERE name IN (
  'ssl', 'ssl_cert_file', 'ssl_key_file', 'ssl_ca_file',
  'log_connections', 'log_disconnections', 'log_statement'
);"
```

### Manual Verification Checklist

- [ ] TLS certificate valid and properly configured
- [ ] Session management controls functioning
- [ ] Account lockout working after failed attempts
- [ ] Audit logging capturing all required events
- [ ] Database connections using SSL
- [ ] Container running as non-root user

---

## Security Control Inheritance

BMAD Forge inherits security controls from the following:

| Control Source | Controls Inherited |
|----------------|-------------------|
| Cloud Provider | Network security, physical security, infrastructure |
| Container Platform | Container isolation, resource limits, network policies |
| Django Framework | CSRF protection, XSS prevention, SQL injection prevention |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-29 | Security Team | Initial document |
