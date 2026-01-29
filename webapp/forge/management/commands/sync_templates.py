"""
Management command to sync templates from GitHub.
"""

from django.core.management.base import BaseCommand, CommandError
from forge.services import GitHubSyncService


class Command(BaseCommand):
    help = 'Sync BMAD templates from GitHub repository'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--owner',
            type=str,
            help='Repository owner (default: from settings)',
        )
        parser.add_argument(
            '--repo',
            type=str,
            help='Repository name (default: from settings)',
        )
        parser.add_argument(
            '--branch',
            type=str,
            default='main',
            help='Branch name (default: main)',
        )
        parser.add_argument(
            '--path',
            type=str,
            default='webapp/forge/templates',
            help='Path to templates directory (default: webapp/forge/templates)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )
    
    def handle(self, *args, **options):
        from django.conf import settings
        
        owner = options['owner']
        repo = options['repo']
        branch = options['branch']
        path = options['path']
        verbose = options['verbose']
        
        # Use settings if not provided
        if not owner or not repo:
            # Parse from TEMPLATE_REPO setting
            repo_parts = settings.TEMPLATE_REPO.split('/')
            if len(repo_parts) != 2:
                raise CommandError('Invalid TEMPLATE_REPO format. Expected: owner/repo')
            
            if not owner:
                owner = repo_parts[0]
            if not repo:
                repo = repo_parts[1]
        
        self.stdout.write(f'Syncing templates from {owner}/{repo}')
        self.stdout.write(f'Branch: {branch}, Path: {path}')
        self.stdout.write('')
        
        # Perform sync
        service = GitHubSyncService()
        results = service.sync_templates(owner, repo, branch, path)
        
        if results['success']:
            self.stdout.write(self.style.SUCCESS(f'Sync completed successfully!'))
            self.stdout.write(f'  Created: {results["created"]}')
            self.stdout.write(f'  Updated: {results["updated"]}')
            
            if verbose and results['templates']:
                self.stdout.write('')
                self.stdout.write('Templates synced:')
                for template in results['templates']:
                    self.stdout.write(
                        f'  - {template["title"]} ({template["agent_role"]} - {template["workflow_phase"]})'
                    )
        else:
            self.stdout.write(self.style.ERROR('Sync failed!'))
            for error in results['errors']:
                self.stdout.write(f'  Error: {error}')
        
        # Show any errors
        if results.get('errors'):
            self.stdout.write('')
            for error in results['errors']:
                self.stdout.write(self.style.WARNING(f'Warning: {error}'))
