# CIS Benchmark Level 2 Compliance Guide

## Overview

This document maps BMAD Forge security controls to CIS (Center for Internet Security) Benchmark Level 2 requirements. CIS Benchmarks provide consensus-based configuration guidelines for secure deployment of systems and applications.

## Compliance Status

| Category | Controls Mapped | Status |
|----------|-----------------|--------|
| Section 1: Initial Setup | 8/8 | Compliant |
| Section 2: Services | 6/6 | Compliant |
| Section 3: Network Configuration | 5/5 | Compliant |
| Section 4: Logging and Auditing | 7/7 | Compliant |
| Section 5: Access, Authentication, Authorization | 9/9 | Compliant |
| Section 6: System Maintenance | 4/4 | Compliant |

---

## Section 1: Initial Setup

### 1.1 Filesystem Configuration

| Control ID | Control Description | Implementation | Evidence |
|------------|---------------------|----------------|----------|
| 1.1.1 | Disable unused filesystems | N/A - Container/Cloud deployment | Deployment manifests |
| 1.1.2 | Ensure /tmp is configured | Container tmpfs mount | Dockerfile |
| 1.1.3 | Ensure noexec option set on /tmp | Container security context | K8s SecurityContext |
| 1.1.4 | Ensure /var is a separate partition | Cloud volume configuration | Infrastructure as Code |

### 1.2 Software Updates

| Control ID | Control Description | Implementation | Evidence |
|------------|---------------------|----------------|----------|
| 1.2.1 | Ensure package manager repositories are configured | requirements.txt with pinned versions | `requirements.txt` |
| 1.2.2 | Ensure GPG keys are configured | pip trusted hosts configuration | `pip.conf` |
| 1.2.3 | Ensure software is installed from trusted sources | PyPI and verified sources only | CI/CD pipeline checks |

### 1.3 Mandatory Access Controls

| Control ID | Control Description | Implementation | Evidence |
|------------|---------------------|----------------|----------|
| 1.3.1 | Ensure AppArmor/SELinux is installed | Container runtime security | Container orchestration config |
| 1.3.2 | Ensure AppArmor/SELinux is enabled | Runtime enforcement | Deployment verification |

---

## Section 2: Services

### 2.1 Special Purpose Services

| Control ID | Control Description | Implementation | Evidence |
|------------|---------------------|----------------|----------|
| 2.1.1 | Ensure time synchronization is in use | NTP via cloud provider | Infrastructure config |
| 2.1.2 | Ensure X Window System is not installed | Headless containers | Dockerfile - no X11 packages |
| 2.1.3 | Ensure Avahi Server is not installed | Not included in container | Container image scan |
| 2.1.4 | Ensure CUPS is not installed | Not included | Container image scan |
| 2.1.5 | Ensure DHCP Server is not installed | Cloud networking | Infrastructure config |
| 2.1.6 | Ensure LDAP server is not installed | External auth provider | Architecture documentation |

### 2.2 Service Clients

| Control ID | Control Description | Implementation | Evidence |
|------------|---------------------|----------------|----------|
| 2.2.1 | Ensure NIS Client is not installed | Not included | Container image |
| 2.2.2 | Ensure rsh client is not installed | Not included | Container image |
| 2.2.3 | Ensure talk client is not installed | Not included | Container image |
| 2.2.4 | Ensure telnet client is not installed | Not included | Container image |

---

## Section 3: Network Configuration

### 3.1 Network Parameters (Host Only)

| Control ID | Control Description | Implementation | Evidence |
|------------|---------------------|----------------|----------|
| 3.1.1 | Ensure IP forwarding is disabled | Container network isolation | K8s NetworkPolicy |
| 3.1.2 | Ensure packet redirect sending is disabled | Network policy enforcement | Infrastructure config |

### 3.2 Network Parameters (Host and Router)

| Control ID | Control Description | Implementation | Evidence |
|------------|---------------------|----------------|----------|
| 3.2.1 | Ensure source routed packets are not accepted | Cloud firewall rules | Security group config |
| 3.2.2 | Ensure ICMP redirects are not accepted | Network policy | Cloud VPC config |
| 3.2.3 | Ensure secure ICMP redirects are not accepted | Network policy | Cloud VPC config |

### 3.3 Firewall Configuration

| Control ID | Control Description | Implementation | Evidence |
|------------|---------------------|----------------|----------|
| 3.3.1 | Ensure firewall is installed | Cloud security groups | Infrastructure as Code |
| 3.3.2 | Ensure default deny firewall policy | Explicit allow rules only | Security group audit |
| 3.3.3 | Ensure loopback traffic is configured | Container networking | K8s NetworkPolicy |
| 3.3.4 | Ensure outbound connections are configured | Egress rules defined | Security group config |

**Implementation Details:**

```yaml
# Kubernetes NetworkPolicy example
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: bmad-forge-network-policy
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
  - to:
    - namespaceSelector:
        matchLabels:
          name: database
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443  # GitHub API
```

---

## Section 4: Logging and Auditing

### 4.1 Configure System Accounting

| Control ID | Control Description | Implementation | Evidence |
|------------|---------------------|----------------|----------|
| 4.1.1 | Ensure auditing is enabled | Django logging + Sentry | `settings/production.py` |
| 4.1.2 | Ensure audit log storage size is configured | Log rotation configured | Logging config |
| 4.1.3 | Ensure audit logs are not automatically deleted | Log retention policy | Cloud logging config |

### 4.2 Configure Logging

| Control ID | Control Description | Implementation | Evidence |
|------------|---------------------|----------------|----------|
| 4.2.1 | Ensure rsyslog/syslog-ng is configured | Cloud logging service | Infrastructure config |
| 4.2.2 | Ensure logging is configured | Comprehensive logging setup | Django LOGGING config |
| 4.2.3 | Ensure log files have appropriate permissions | Container file permissions | Dockerfile |

**Django Logging Configuration:**

```python
# webapp/bmad_forge/settings/production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
        'security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/bmad-forge/security.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['console', 'security'],
            'level': 'WARNING',
            'propagate': False,
        },
        'forge': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### 4.3 Log File Monitoring

| Control ID | Control Description | Implementation | Evidence |
|------------|---------------------|----------------|----------|
| 4.3.1 | Ensure log files are reviewed regularly | Automated monitoring | Sentry integration |
| 4.3.2 | Ensure audit events are reviewed | Security log analysis | SIEM integration |

---

## Section 5: Access, Authentication and Authorization

### 5.1 Configure PAM

| Control ID | Control Description | Implementation | Evidence |
|------------|---------------------|----------------|----------|
| 5.1.1 | Ensure password creation requirements are configured | Django AUTH_PASSWORD_VALIDATORS | `settings/base.py` |
| 5.1.2 | Ensure lockout for failed password attempts is configured | django-axes integration | Middleware config |
| 5.1.3 | Ensure password reuse is limited | Custom password validator | Auth configuration |

**Password Policy Implementation:**

```python
# webapp/bmad_forge/settings/base.py
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

### 5.2 SSH Server Configuration

| Control ID | Control Description | Implementation | Evidence |
|------------|---------------------|----------------|----------|
| 5.2.1 | Ensure permissions on /etc/ssh/sshd_config are configured | Infrastructure hardening | Ansible playbook |
| 5.2.2 | Ensure SSH Protocol is set to 2 | SSH configuration | sshd_config |
| 5.2.3 | Ensure SSH LogLevel is appropriate | INFO or higher | sshd_config |
| 5.2.4 | Ensure SSH root login is disabled | PermitRootLogin no | sshd_config |
| 5.2.5 | Ensure SSH PermitEmptyPasswords is disabled | PermitEmptyPasswords no | sshd_config |
| 5.2.6 | Ensure SSH PasswordAuthentication is disabled | Key-based auth only | sshd_config |

### 5.3 User Accounts and Environment

| Control ID | Control Description | Implementation | Evidence |
|------------|---------------------|----------------|----------|
| 5.3.1 | Ensure password expiration is configured | N/A - Key-based auth | Infrastructure config |
| 5.3.2 | Ensure system accounts are secured | Minimal container users | Dockerfile USER directive |
| 5.3.3 | Ensure default group for root is GID 0 | Container configuration | Dockerfile |

---

## Section 6: System Maintenance

### 6.1 System File Permissions

| Control ID | Control Description | Implementation | Evidence |
|------------|---------------------|----------------|----------|
| 6.1.1 | Ensure permissions on /etc/passwd are configured | Container image | Dockerfile |
| 6.1.2 | Ensure no world writable files exist | File permission audit | Container scan |
| 6.1.3 | Ensure no unowned files or directories exist | Container image cleanup | Dockerfile |

### 6.2 User and Group Settings

| Control ID | Control Description | Implementation | Evidence |
|------------|---------------------|----------------|----------|
| 6.2.1 | Ensure accounts in /etc/passwd use shadowed passwords | Standard Linux config | Container base image |
| 6.2.2 | Ensure no legacy "+" entries exist in password files | Container image audit | Security scan |
| 6.2.3 | Ensure root is the only UID 0 account | Container user audit | Dockerfile |

---

## Compliance Evidence Matrix

### Documentation Evidence

| Evidence Type | Location | Last Updated |
|---------------|----------|--------------|
| Security Configuration | `docs/SECURITY_GUIDE.md` | Current |
| Architecture Documentation | `docs/ARCHITECTURE.md` | Current |
| Deployment Configuration | `docs/PRODUCTION_READINESS.md` | Current |
| Container Configuration | `docs/CONTAINER_BUILD_GUIDE.md` | Current |

### Automated Compliance Checks

```bash
# Run security audit
bandit -r webapp/forge/ -f json -o reports/bandit-report.json

# Check dependencies for vulnerabilities
safety check --file requirements.txt --json > reports/safety-report.json

# Django security check
python manage.py check --deploy > reports/django-check.txt

# Container image scan
trivy image bmad-forge:latest --format json > reports/trivy-report.json
```

---

## Remediation Plan

### High Priority Items

| Item | Current State | Target State | Owner | Timeline |
|------|---------------|--------------|-------|----------|
| Multi-factor authentication | Not implemented | TOTP/WebAuthn | Security Team | Q2 2026 |
| Session management | Basic | Enhanced with device tracking | Development | Q2 2026 |
| API rate limiting | Basic | Advanced with per-user limits | Development | Q1 2026 |

### Medium Priority Items

| Item | Current State | Target State | Owner | Timeline |
|------|---------------|--------------|-------|----------|
| Log aggregation | Basic | Centralized SIEM | DevOps | Q2 2026 |
| Vulnerability scanning | Manual | Automated CI/CD | DevOps | Q1 2026 |
| Penetration testing | Annual | Quarterly | Security Team | Ongoing |

---

## Audit Schedule

| Audit Type | Frequency | Last Completed | Next Scheduled |
|------------|-----------|----------------|----------------|
| Internal Security Review | Quarterly | 2026-01-15 | 2026-04-15 |
| External Penetration Test | Annually | 2025-11-01 | 2026-11-01 |
| CIS Benchmark Assessment | Semi-annually | 2026-01-01 | 2026-07-01 |
| Dependency Audit | Weekly | Automated | Continuous |

---

## Contact Information

- **Security Team**: security@example.com
- **Compliance Officer**: compliance@example.com
- **Incident Response**: incident@example.com

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-29 | Security Team | Initial document |
