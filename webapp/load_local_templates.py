#!/usr/bin/env python
"""
Script to load templates from local directories into the database.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bmad_forge.settings')
django.setup()

from forge.models import Template
from forge.services.template_parser import TemplateParser
from forge.services.github_sync import GitHubSyncService

# Directories containing templates to load
TEMPLATE_DIRECTORIES = [
    'forge/templates/agents',
    'forge/templates/templates',
]


def load_templates_from_directory(templates_dir, parser, sync_service):
    """
    Load templates from a single directory.
    
    Args:
        templates_dir: Path to the directory containing templates
        parser: TemplateParser instance
        sync_service: GitHubSyncService instance
        
    Returns:
        Tuple of (created_count, updated_count)
    """
    created_count = 0
    updated_count = 0
    
    if not os.path.exists(templates_dir):
        print(f"Templates directory not found: {templates_dir}")
        return created_count, updated_count
    
    # Process all .md files in the templates directory
    try:
        filenames = os.listdir(templates_dir)
    except OSError as e:
        print(f"Error listing directory {templates_dir}: {e}")
        return created_count, updated_count
    
    for filename in filenames:
        if not filename.endswith('.md'):
            continue
        
        filepath = os.path.join(templates_dir, filename)
        print(f"Processing: {filename}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the template
            title = filename.replace('.md', '').replace('_', ' ').title()
            variables = parser.extract_variables_simple(content)
            description = sync_service.parse_template_description(content)
            agent_role = sync_service.detect_agent_role(content, filename)
            agent_roles = sync_service.detect_agent_roles(content, filename)
            workflow_phase = sync_service.detect_workflow_phase(content, filename)
            
            # Check if template already exists
            template, created = Template.objects.update_or_create(
                title=title,
                defaults={
                    'content': content,
                    'agent_role': agent_role,
                    'agent_roles': agent_roles,
                    'workflow_phase': workflow_phase,
                    'description': description or '',
                    'variables': variables,
                    'remote_path': filepath,
                    'is_active': True,
                }
            )
            
            roles_display = ', '.join(agent_roles) if agent_roles else 'auto-detected'
            if created:
                created_count += 1
                print(f"  ✓ Created: {title} (roles: {roles_display})")
            else:
                updated_count += 1
                print(f"  ✓ Updated: {title} (roles: {roles_display})")
                
        except Exception as e:
            print(f"  ✗ Error processing {filename}: {e}")
    
    return created_count, updated_count


def load_templates():
    """Load templates from all configured local template directories."""
    base_dir = os.path.dirname(__file__)
    parser = TemplateParser()
    sync_service = GitHubSyncService()
    total_created = 0
    total_updated = 0
    
    for template_dir in TEMPLATE_DIRECTORIES:
        templates_dir = os.path.join(base_dir, template_dir)
        print(f"\nLoading templates from: {template_dir}")
        print("-" * 50)
        
        created, updated = load_templates_from_directory(
            templates_dir, parser, sync_service
        )
        total_created += created
        total_updated += updated
    
    print(f"\n✓ Completed!")
    print(f"  Total Created: {total_created}")
    print(f"  Total Updated: {total_updated}")


if __name__ == '__main__':
    load_templates()
