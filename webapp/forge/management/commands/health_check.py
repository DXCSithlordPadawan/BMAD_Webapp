"""
Health check management command for BMAD Forge.

Checks system health including database and cache connectivity.
Returns exit code 0 for healthy, 1 for unhealthy.

Usage:
    python manage.py health_check
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import sys


class Command(BaseCommand):
    help = 'Check application health (database, cache)'

    def handle(self, *args, **options):
        """Execute health checks."""
        healthy = True
        issues = []

        # Check database connectivity
        self.stdout.write('Checking database connectivity...')
        try:
            connection.ensure_connection()
            self.stdout.write(self.style.SUCCESS('✓ Database: OK'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Database: FAILED - {str(e)}'))
            issues.append(f'Database: {str(e)}')
            healthy = False

        # Check cache connectivity
        self.stdout.write('Checking cache connectivity...')
        try:
            cache.set('health_check', 'ok', 10)
            result = cache.get('health_check')
            if result == 'ok':
                self.stdout.write(self.style.SUCCESS('✓ Cache: OK'))
            elif settings.DEBUG and 'DummyCache' in str(settings.CACHES['default']['BACKEND']):
                # DummyCache doesn't actually cache, so this is expected in development
                self.stdout.write(self.style.SUCCESS('✓ Cache: OK (DummyCache in development)'))
            else:
                self.stdout.write(self.style.WARNING('⚠ Cache: Not functioning properly'))
                issues.append('Cache: Not returning expected values')
                healthy = False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Cache: FAILED - {str(e)}'))
            issues.append(f'Cache: {str(e)}')
            healthy = False

        # Print summary
        self.stdout.write('')
        if healthy:
            self.stdout.write(self.style.SUCCESS('=== HEALTH CHECK PASSED ==='))
            sys.exit(0)
        else:
            self.stdout.write(self.style.ERROR('=== HEALTH CHECK FAILED ==='))
            self.stdout.write(self.style.ERROR(f'Issues found: {len(issues)}'))
            for issue in issues:
                self.stdout.write(self.style.ERROR(f'  - {issue}'))
            sys.exit(1)
