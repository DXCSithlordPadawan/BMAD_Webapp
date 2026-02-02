# BMAD Forge - Operations Runbook
## Inline Editing Feature Support

**Version:** 1.0  
**Last Updated:** February 2, 2026  
**Target Audience:** Operations/DevOps/Support Team

---

## Table of Contents

1. [Overview](#overview)
2. [System Health Monitoring](#system-health-monitoring)
3. [Common Issues & Solutions](#common-issues--solutions)
4. [Performance Troubleshooting](#performance-troubleshooting)
5. [Security Incident Response](#security-incident-response)
6. [Maintenance Procedures](#maintenance-procedures)
7. [Escalation Procedures](#escalation-procedures)
8. [Emergency Contacts](#emergency-contacts)

---

## 1. Overview

### What Changed (v1.2.0)

**New Components:**
- Rich text editor (Quill.js via CDN)
- JavaScript file: `wizard-editor.js` (15KB)
- Enhanced session management
- HTML→Markdown conversion layer
- Real-time AJAX validation

**Modified Components:**
- `document_generator.py` - new methods
- `views.py` - session structure changed
- `generate_document_wizard.html` - UI updates

### Key Metrics to Monitor

| Metric | Normal | Warning | Critical |
|--------|--------|---------|----------|
| Page Load Time | < 2s | 2-5s | > 5s |
| AJAX Response | < 500ms | 500ms-1s | > 1s |
| Error Rate | < 0.5% | 0.5-2% | > 2% |
| Session Size | < 200KB | 200-500KB | > 500KB |
| Active Sessions | < 100 | 100-500 | > 500 |

---

## 2. System Health Monitoring

### Quick Health Check

```bash
#!/bin/bash
# health_check.sh

echo "=== BMAD Forge Health Check ==="
echo ""

# Check if app is responding
echo "1. Application Status:"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://bmad-forge.example.com/)
if [ $STATUS -eq 200 ]; then
    echo "   ✓ Application responding (HTTP $STATUS)"
else
    echo "   ✗ Application DOWN or ERROR (HTTP $STATUS)"
fi

# Check wizard page
echo "2. Wizard Endpoint:"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://bmad-forge.example.com/forge/template/1/wizard/)
if [ $STATUS -eq 200 ] || [ $STATUS -eq 302 ]; then
    echo "   ✓ Wizard accessible (HTTP $STATUS)"
else
    echo "   ✗ Wizard issue (HTTP $STATUS)"
fi

# Check static files
echo "3. Static Files:"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://bmad-forge.example.com/static/forge/js/wizard-editor.js)
if [ $STATUS -eq 200 ]; then
    echo "   ✓ wizard-editor.js accessible"
else
    echo "   ✗ Static files issue (HTTP $STATUS)"
fi

# Check CDN
echo "4. External Dependencies:"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://cdn.quilljs.com/1.3.7/quill.min.js)
if [ $STATUS -eq 200 ]; then
    echo "   ✓ Quill.js CDN accessible"
else
    echo "   ⚠ CDN issue - fallback may be needed"
fi

# Check database
echo "5. Database Connection:"
python manage.py dbshell --command="SELECT 1;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ Database connected"
else
    echo "   ✗ Database connection failed"
fi

echo ""
echo "=== Health Check Complete ==="
```

### Monitoring Dashboards

**Key Metrics Dashboard:**
```
┌─────────────────────────────────────────────┐
│ BMAD Forge - Production Monitoring         │
├─────────────────────────────────────────────┤
│ Uptime:          99.9% (last 7 days)        │
│ Active Users:    45 (current)               │
│ Requests/min:    230                        │
│ Avg Response:    1.2s                       │
│ Error Rate:      0.3%                       │
│ Session Count:   78                         │
│ Disk Usage:      42% (/var/www)            │
│ Memory Usage:    65% (4.2GB / 6.5GB)       │
│ CPU Load:        2.3 (avg)                  │
└─────────────────────────────────────────────┘
```

### Log Monitoring

**Key Log Files:**
```bash
# Application logs
tail -f /var/log/bmad-forge/application.log

# Error logs
tail -f /var/log/bmad-forge/error.log

# Access logs
tail -f /var/log/nginx/bmad-forge-access.log

# Django logs
tail -f /var/log/bmad-forge/django.log
```

**Critical Log Patterns to Watch:**
```bash
# XSS attempts (should be blocked)
grep -i "script.*alert" /var/log/bmad-forge/error.log

# CSRF failures
grep "CSRF" /var/log/bmad-forge/error.log

# Session errors
grep "session" /var/log/bmad-forge/error.log

# JavaScript errors
grep "wizard-editor" /var/log/bmad-forge/error.log

# CDN failures
grep "quilljs" /var/log/bmad-forge/error.log
```

---

## 3. Common Issues & Solutions

### Issue 1: Wizard Page Not Loading

**Symptoms:**
- Users report blank page
- Wizard shows error
- Editor not appearing

**Diagnosis:**
```bash
# Check application logs
tail -50 /var/log/bmad-forge/error.log | grep -i "wizard\|editor"

# Check nginx logs
tail -50 /var/log/nginx/error.log

# Verify static files
ls -lh /var/www/bmad-forge/static/forge/js/wizard-editor.js

# Check permissions
stat /var/www/bmad-forge/static/forge/js/wizard-editor.js
```

**Solutions:**

**A. Static Files Not Collected:**
```bash
cd /path/to/webapp
python manage.py collectstatic --noinput
sudo systemctl restart bmad-forge
```

**B. Permission Issues:**
```bash
sudo chown -R www-data:www-data /var/www/bmad-forge/static/
sudo chmod -R 755 /var/www/bmad-forge/static/
```

**C. Nginx Configuration:**
```nginx
# /etc/nginx/sites-available/bmad-forge
location /static/ {
    alias /var/www/bmad-forge/static/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Issue 2: Editor Not Loading (Quill.js)

**Symptoms:**
- White box instead of editor
- Console error: "Quill is not defined"
- Toolbar not visible

**Diagnosis:**
```bash
# Check CDN accessibility
curl -I https://cdn.quilljs.com/1.3.7/quill.min.js

# Check browser console (user reports)
# F12 → Console → Look for errors

# Check if blocked by firewall
telnet cdn.quilljs.com 443
```

**Solutions:**

**A. CDN Blocked/Slow:**
```bash
# Download Quill locally
mkdir -p /var/www/bmad-forge/static/vendor/quill
cd /var/www/bmad-forge/static/vendor/quill
wget https://cdn.quilljs.com/1.3.7/quill.min.js
wget https://cdn.quilljs.com/1.3.7/quill.snow.css

# Update template to use local files
# Edit: webapp/forge/templates/forge/generate_document_wizard.html
# Change CDN links to:
# {% static 'vendor/quill/quill.min.js' %}
# {% static 'vendor/quill/quill.snow.css' %}

python manage.py collectstatic --noinput
sudo systemctl restart bmad-forge
```

**B. Browser Cache:**
```
# Ask user to:
1. Hard refresh (Ctrl+Shift+R)
2. Clear browser cache
3. Try incognito mode
```

**C. JavaScript Error:**
```bash
# Check for syntax errors
grep -n "wizard-editor" /var/log/bmad-forge/error.log

# Verify file integrity
md5sum /var/www/bmad-forge/static/forge/js/wizard-editor.js
# Should match: [expected MD5 hash]
```

### Issue 3: Content Not Saving

**Symptoms:**
- User edits disappear
- "Previous" button shows old content
- Session timeout errors

**Diagnosis:**
```bash
# Check session configuration
python manage.py shell
>>> from django.conf import settings
>>> settings.SESSION_COOKIE_AGE
7200  # Should be 7200 (2 hours)

# Check session backend
>>> settings.SESSION_ENGINE
'django.contrib.sessions.backends.cached_db'

# Check session count
>>> from django.contrib.sessions.models import Session
>>> Session.objects.count()

# Check for expired sessions
>>> from django.utils import timezone
>>> expired = Session.objects.filter(expire_date__lt=timezone.now())
>>> expired.count()
```

**Solutions:**

**A. Session Timeout:**
```python
# settings.py - Increase timeout
SESSION_COOKIE_AGE = 14400  # 4 hours instead of 2
```
```bash
sudo systemctl restart bmad-forge
```

**B. Session Storage Full:**
```bash
# Clear old sessions
python manage.py clearsessions

# Check database size
du -sh /var/lib/postgresql/data/
```

**C. Cookie Issues:**
```python
# Verify settings.py
SESS ION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'  # Not 'Strict'
SESSION_COOKIE_SECURE = True      # Only in production
```

### Issue 4: Validation Not Working

**Symptoms:**
- No validation feedback
- AJAX requests failing
- 500 errors on validation endpoint

**Diagnosis:**
```bash
# Check AJAX endpoint
curl -X POST https://bmad-forge.example.com/forge/template/1/validate-section/ \
  -H "Content-Type: application/json" \
  -d '{"section_name":"Test","content":"Test content"}'

# Check error logs
grep "validate" /var/log/bmad-forge/error.log | tail -20

# Check rate limiting (if configured)
grep "rate limit" /var/log/nginx/error.log
```

**Solutions:**

**A. CSRF Token Issues:**
```javascript
// User may need to refresh to get new token
// Check browser console for "CSRF token missing"
```

**B. Endpoint Not Configured:**
```python
# urls.py - Verify route exists
path('template/<int:template_id>/validate-section/', 
     views.validate_section, name='validate_section'),
```

**C. Database Connection:**
```bash
# Check database connection
python manage.py dbshell --command="SELECT 1;"

# Restart database if needed
sudo systemctl restart postgresql
```

### Issue 5: Slow Performance

**Symptoms:**
- Page loads slowly
- Editor lag
- AJAX timeouts

**Diagnosis:**
```bash
# Check system resources
top
htop

# Check database performance
python manage.py dbshell
postgres=# SELECT * FROM pg_stat_activity;

# Check slow queries
postgres=# SELECT query, mean_time 
           FROM pg_stat_statements 
           ORDER BY mean_time DESC 
           LIMIT 10;

# Network latency
ping bmad-forge.example.com
traceroute bmad-forge.example.com
```

**Solutions:**

**A. Database Optimization:**
```bash
# Run VACUUM
python manage.py dbshell
postgres=# VACUUM ANALYZE;

# Add indexes (if not present)
python manage.py migrate
```

**B. Increase Resources:**
```bash
# Increase Gunicorn workers
# /etc/systemd/system/bmad-forge.service
ExecStart=/path/to/gunicorn \
  --workers 4 \
  --bind unix:/run/bmad-forge.sock \
  webapp.wsgi:application

sudo systemctl daemon-reload
sudo systemctl restart bmad-forge
```

**C. Enable Caching:**
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

---

## 4. Performance Troubleshooting

### Performance Monitoring

**Response Time Tracking:**
```bash
# Average response time (last 1000 requests)
awk '{print $10}' /var/log/nginx/bmad-forge-access.log | tail -1000 | \
  awk '{sum+=$1; count++} END {print sum/count}'

# 95th percentile
awk '{print $10}' /var/log/nginx/bmad-forge-access.log | tail -1000 | \
  sort -n | awk 'NR==int(NR*0.95)'
```

**Slow Endpoint Identification:**
```bash
# Find slowest endpoints
awk '{print $7, $10}' /var/log/nginx/bmad-forge-access.log | \
  sort -k2 -rn | head -20
```

### Optimization Actions

**If Response Time > 5 seconds:**

1. **Check Database:**
   ```bash
   python manage.py dbshell
   postgres=# SELECT * FROM pg_stat_activity WHERE state = 'active';
   ```

2. **Check Memory:**
   ```bash
   free -h
   # If low, restart application
   sudo systemctl restart bmad-forge
   ```

3. **Check Disk I/O:**
   ```bash
   iostat -x 1 10
   # If high, database may need optimization
   ```

4. **Enable Query Logging:**
   ```python
   # settings.py (temporarily)
   LOGGING = {
       'loggers': {
           'django.db.backends': {
               'level': 'DEBUG',
           }
       }
   }
   ```

---

## 5. Security Incident Response

### Incident Types

#### A. XSS Attempt Detected

**Detection:**
```bash
# Monitor for XSS patterns
grep -i "script.*alert\|onerror\|javascript:" /var/log/bmad-forge/access.log
```

**Response:**
1. Verify sanitization is working
2. Check if attempt was blocked
3. Log incident details
4. Review logs for source IP
5. Consider IP blocking if repeated

**Verification:**
```bash
# Check that content was sanitized
grep "Sanitized content" /var/log/bmad-forge/application.log
```

#### B. CSRF Token Failures

**Detection:**
```bash
grep "CSRF" /var/log/bmad-forge/error.log | tail -20
```

**Response:**
1. Check if legitimate user (session timeout?)
2. Verify CSRF middleware enabled
3. Check cookie settings
4. Review for automation/bot activity

**Action:**
```bash
# If high volume from single IP
sudo iptables -A INPUT -s <IP_ADDRESS> -j DROP

# Or use fail2ban
sudo fail2ban-client set bmad-forge banip <IP_ADDRESS>
```

#### C. Unusual Session Activity

**Detection:**
```bash
# Large session sizes
python manage.py shell
>>> from django.contrib.sessions.models import Session
>>> for s in Session.objects.all():
>>>     if len(s.session_data) > 100000:  # 100KB
>>>         print(f"Large session: {s.session_key}")
```

**Response:**
1. Investigate large sessions
2. Check for data injection attempts
3. Clear suspicious sessions
4. Review user activity

#### D. Database Injection Attempt

**Detection:**
```bash
grep -i "DROP\|DELETE\|';--" /var/log/bmad-forge/access.log
```

**Response:**
1. Verify Django ORM is handling (should be safe)
2. Log attempt details
3. Block source if repeated
4. Run security scan

---

## 6. Maintenance Procedures

### Routine Maintenance (Weekly)

```bash
#!/bin/bash
# weekly_maintenance.sh

echo "=== Weekly Maintenance ==="

# 1. Clear old sessions
echo "Clearing old sessions..."
python manage.py clearsessions

# 2. Database vacuum
echo "Optimizing database..."
python manage.py dbshell --command="VACUUM ANALYZE;"

# 3. Check disk space
echo "Checking disk space..."
df -h

# 4. Rotate logs
echo "Rotating logs..."
sudo logrotate /etc/logrotate.d/bmad-forge

# 5. Check for security updates
echo "Checking for updates..."
sudo apt update
sudo apt list --upgradable

# 6. Backup database
echo "Backing up database..."
pg_dump bmad_forge > /backups/bmad_forge_$(date +%Y%m%d).sql

# 7. Test health check
echo "Running health check..."
./health_check.sh

echo "=== Maintenance Complete ==="
```

### Deployment Procedure

**For Inline Editing Updates:**

```bash
#!/bin/bash
# deploy_inline_editing.sh

set -e  # Exit on error

echo "=== Deployment: Inline Editing Updates ==="

# 1. Backup current version
echo "1. Creating backup..."
cp -r /var/www/bmad-forge /var/www/bmad-forge_backup_$(date +%Y%m%d)

# 2. Pull new code
echo "2. Pulling updates..."
cd /var/www/bmad-forge
git pull origin main

# 3. Install dependencies (if needed)
echo "3. Checking dependencies..."
pip install -r requirements.txt --no-cache-dir

# 4. Run migrations (if any)
echo "4. Running migrations..."
python manage.py migrate

# 5. Collect static files
echo "5. Collecting static files..."
python manage.py collectstatic --noinput

# 6. Run tests
echo "6. Running tests..."
python manage.py test forge.tests.test_document_generator_editing
python manage.py test forge.tests.test_wizard_view_editing

# 7. Restart application
echo "7. Restarting application..."
sudo systemctl restart bmad-forge

# 8. Wait for startup
echo "8. Waiting for startup..."
sleep 5

# 9. Health check
echo "9. Running health check..."
./health_check.sh

# 10. Verify wizard works
echo "10. Testing wizard endpoint..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://bmad-forge.example.com/forge/template/1/wizard/)
if [ $STATUS -eq 200 ] || [ $STATUS -eq 302 ]; then
    echo "✓ Wizard accessible"
else
    echo "✗ Wizard test failed - ROLLING BACK"
    ./rollback.sh
    exit 1
fi

echo "=== Deployment Complete ==="
echo "Monitor logs for 15 minutes:"
echo "  tail -f /var/log/bmad-forge/error.log"
```

### Rollback Procedure

```bash
#!/bin/bash
# rollback.sh

echo "=== ROLLBACK INITIATED ==="

# 1. Stop application
echo "1. Stopping application..."
sudo systemctl stop bmad-forge

# 2. Restore backup
echo "2. Restoring from backup..."
BACKUP=$(ls -t /var/www/bmad-forge_backup_* | head -1)
echo "   Using backup: $BACKUP"
rm -rf /var/www/bmad-forge
cp -r $BACKUP /var/www/bmad-forge

# 3. Restore database (if needed)
# echo "3. Restoring database..."
# psql bmad_forge < /backups/bmad_forge_YYYYMMDD.sql

# 4. Collect static files
echo "4. Collecting static files..."
cd /var/www/bmad-forge
python manage.py collectstatic --noinput

# 5. Restart application
echo "5. Restarting application..."
sudo systemctl start bmad-forge

# 6. Verify
echo "6. Verifying..."
sleep 5
./health_check.sh

echo "=== ROLLBACK COMPLETE ==="
echo "Incident Response:"
echo "1. Document what went wrong"
echo "2. Notify development team"
echo "3. Schedule post-mortem"
```

---

## 7. Escalation Procedures

### Escalation Matrix

| Issue Severity | Response Time | Escalate To | Contact Method |
|----------------|---------------|-------------|----------------|
| **P1 - Critical** | 15 minutes | On-call Engineer | Phone + Page |
| Service Down | | + CTO (if > 30 min) | |
| **P2 - High** | 1 hour | Team Lead | Slack + Email |
| Degraded Performance | | | |
| **P3 - Medium** | 4 hours | Dev Team | Email + Ticket |
| Minor Bugs | | | |
| **P4 - Low** | Next Business Day | Support Team | Ticket |
| Questions, Requests | | | |

### When to Escalate

**Immediate Escalation (P1):**
- Application completely down
- Database corrupted
- Security breach detected
- Data loss occurring

**Escalate if Not Resolved in 30 min (P2):**
- Wizard not loading for all users
- Editor failures affecting > 50% users
- Performance degradation > 10s response
- CSRF/XSS vulnerabilities active

**Standard Escalation (P3/P4):**
- Single user issues
- Minor UI bugs
- Feature requests
- Documentation updates

---

## 8. Emergency Contacts

### Primary Contacts

**On-Call Rotation:**
```
Week of Feb 2:  John Doe (john.doe@example.com, +1-555-0100)
Week of Feb 9:  Jane Smith (jane.smith@example.com, +1-555-0101)
Week of Feb 16: Bob Johnson (bob.j@example.com, +1-555-0102)
```

**Team Leads:**
- **Development:** dev-lead@example.com, Slack: @dev-lead
- **DevOps:** devops-lead@example.com, Slack: @devops-lead
- **Security:** security@example.com, Slack: @security-team

**Management:**
- **CTO:** cto@example.com, +1-555-0200 (P1 only)
- **Product:** product@example.com

### External Contacts

**Hosting Provider:**
- Support: support@hosting.com
- Emergency: +1-800-HOSTING

**CDN Provider (Cloudflare):**
- Support: support@cloudflare.com
- Dashboard: dash.cloudflare.com

---

## Appendix A: Useful Commands

### Django Management

```bash
# Shell access
python manage.py shell

# Database shell
python manage.py dbshell

# Clear sessions
python manage.py clearsessions

# Collect static
python manage.py collectstatic --noinput

# Run tests
python manage.py test forge

# Check deployment
python manage.py check --deploy
```

### System Commands

```bash
# Service management
sudo systemctl status bmad-forge
sudo systemctl restart bmad-forge
sudo systemctl stop bmad-forge
sudo systemctl start bmad-forge

# Log viewing
journalctl -u bmad-forge -f
tail -f /var/log/bmad-forge/error.log

# Disk space
df -h
du -sh /var/www/bmad-forge/*

# Process monitoring
ps aux | grep gunicorn
htop
```

### Database Commands

```sql
-- Active sessions
SELECT * FROM pg_stat_activity;

-- Table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Recent generated prompts
SELECT id, created_at, is_valid FROM forge_generatedprompt
ORDER BY created_at DESC LIMIT 10;

-- Session count
SELECT COUNT(*) FROM django_session
WHERE expire_date > NOW();
```

---

## Appendix B: Monitoring Alerts

### Recommended Alerts

**Critical Alerts:**
- Application down (5xx errors > 50%)
- Response time > 10 seconds
- Disk space > 90%
- Memory usage > 95%
- Database connection failures

**Warning Alerts:**
- Response time > 5 seconds
- Error rate > 1%
- Disk space > 80%
- Memory usage > 85%
- High session count (> 500)

**Info Alerts:**
- Deployment completed
- Maintenance window started
- Backup completed
- SSL certificate expiring (< 30 days)

---

**Runbook Version:** 1.0  
**Last Updated:** February 2, 2026  
**Next Review:** May 2, 2026  
**Maintained By:** DevOps Team
