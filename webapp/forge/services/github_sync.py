"""
GitHub synchronization service for fetching and updating templates.
"""

import os
import requests
import json
import base64
import re
import yaml
from typing import List, Dict, Optional, Tuple
from django.conf import settings
from django.utils import timezone
from ..models import Template


class GitHubSyncService:
    """
    Service for synchronizing BMAD templates from GitHub repositories.
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the GitHub sync service.
        
        Args:
            token: GitHub personal access token for API authentication
        """
        self.token = token or settings.GITHUB_TOKEN
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
        }
        if self.token:
            self.headers['Authorization'] = f'Bearer {self.token}'
    
    def get_raw_url(self, owner: str, repo: str, branch: str, path: str) -> str:
        """
        Construct the raw URL for a file in GitHub.
        """
        return f"{settings.GITHUB_RAW_BASE_URL}/{owner}/{repo}/{branch}/{path}"
    
    def fetch_file_content(self, owner: str, repo: str, branch: str, path: str) -> Optional[str]:
        """
        Fetch the content of a file from GitHub.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            path: File path in the repository
            
        Returns:
            File content as string, or None if fetch failed
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        params = {'ref': branch} if branch else {}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data.get('encoding') == 'base64':
                return base64.b64decode(data['content']).decode('utf-8')
            return data.get('content', '')
            
        except (requests.RequestException, json.JSONDecodeError, Exception) as e:
            print(f"Error fetching file {path}: {e}")
            return None
    
    def fetch_directory_contents(self, owner: str, repo: str, branch: str, path: str) -> List[Dict]:
        """
        Fetch the contents of a directory from GitHub.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            path: Directory path in the repository
            
        Returns:
            List of file/directory information dictionaries
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        params = {'ref': branch} if branch else {}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
            
        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"Error fetching directory {path}: {e}")
            return []
    
    # Maximum recursion depth to prevent excessive API calls or stack overflow
    MAX_RECURSION_DEPTH = 10
    
    def fetch_directory_contents_recursive(
        self, 
        owner: str, 
        repo: str, 
        branch: str, 
        path: str,
        _current_depth: int = 0,
        _visited_paths: set = None
    ) -> List[Dict]:
        """
        Recursively fetch the contents of a directory and all subdirectories from GitHub.
        
        Includes protection against:
        - Excessive recursion depth (max 10 levels)
        - Circular references via symlinks (tracks visited paths)
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            path: Directory path in the repository
            _current_depth: Internal counter for recursion depth (do not set manually)
            _visited_paths: Internal set of visited paths to prevent cycles (do not set manually)
            
        Returns:
            List of all file information dictionaries (flattened from all subdirectories)
        """
        # Initialize visited paths set on first call
        if _visited_paths is None:
            _visited_paths = set()
        
        # Check recursion depth limit
        if _current_depth >= self.MAX_RECURSION_DEPTH:
            print(f"Warning: Maximum recursion depth ({self.MAX_RECURSION_DEPTH}) reached at path: {path}")
            return []
        
        # Check for circular references
        if path in _visited_paths:
            print(f"Warning: Circular reference detected, skipping path: {path}")
            return []
        
        _visited_paths.add(path)
        
        all_files = []
        contents = self.fetch_directory_contents(owner, repo, branch, path)
        
        for item in contents:
            if item.get('type') == 'file':
                all_files.append(item)
            elif item.get('type') == 'dir':
                # Recursively fetch contents of subdirectory
                subdir_path = item.get('path', '')
                subdir_files = self.fetch_directory_contents_recursive(
                    owner, repo, branch, subdir_path,
                    _current_depth=_current_depth + 1,
                    _visited_paths=_visited_paths
                )
                all_files.extend(subdir_files)
        
        return all_files
    
    def parse_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """
        Parse YAML frontmatter from template content.
        
        Templates can have YAML frontmatter delimited by --- at the start.
        Example:
            ---
            name: my-template
            description: My template description
            role: developer
            workflow_phase: development
            ---
            
            Template content starts here...
        
        Args:
            content: Template content with optional frontmatter
            
        Returns:
            Tuple of (frontmatter dict, remaining content)
        """
        frontmatter = {}
        
        # Handle None or empty content
        if not content:
            return frontmatter, content or ''
        
        remaining_content = content
        
        # Check if content starts with frontmatter delimiter
        if content.strip().startswith('---'):
            lines = content.strip().split('\n')
            # Find the closing delimiter
            end_index = -1
            for i, line in enumerate(lines[1:], start=1):
                if line.strip() == '---':
                    end_index = i
                    break
            
            if end_index > 0:
                # Extract and parse the frontmatter
                frontmatter_text = '\n'.join(lines[1:end_index])
                try:
                    frontmatter = yaml.safe_load(frontmatter_text) or {}
                except yaml.YAMLError as e:
                    # Log the error for debugging but continue with empty frontmatter
                    import logging
                    logging.warning(f"Failed to parse YAML frontmatter: {e}")
                    frontmatter = {}
                
                # Get the remaining content after frontmatter
                remaining_content = '\n'.join(lines[end_index + 1:]).strip()
        
        return frontmatter, remaining_content
    
    def detect_agent_roles(self, content: str, filename: str) -> List[str]:
        """
        Detect all BMAD agent roles from template content or filename.
        
        Supports multiple roles via YAML frontmatter 'roles' field (list).
        Falls back to single 'role' field or auto-detection.
        
        Priority order:
        1. Check YAML frontmatter 'roles' field (list of roles)
        2. Check YAML frontmatter 'role' field (single role)
        3. Auto-detect from filename/content
        
        Args:
            content: Template content
            filename: Template filename
            
        Returns:
            List of detected agent role identifiers
        """
        valid_roles = [role[0] for role in settings.BMAD_AGENT_ROLES]
        frontmatter, _ = self.parse_frontmatter(content)
        
        # 1. Check for 'roles' field (list of roles)
        if 'roles' in frontmatter:
            roles = frontmatter['roles']
            if isinstance(roles, list):
                valid_detected = [r for r in roles if r in valid_roles]
                if valid_detected:
                    return valid_detected
                # If 'roles' was explicitly set but all values were invalid,
                # log a warning and fall through to auto-detection
                import logging
                logging.warning(
                    f"Template '{filename}' has 'roles' field with no valid roles: {roles}. "
                    f"Valid roles are: {valid_roles}"
                )
            elif isinstance(roles, str) and roles in valid_roles:
                return [roles]
        
        # 2. Check for single 'role' field
        if frontmatter.get('role') in valid_roles:
            return [frontmatter['role']]
        
        # 3. Fall back to auto-detection (returns single role)
        detected = self.detect_agent_role(content, filename)
        return [detected]
    
    def detect_agent_role(self, content: str, filename: str) -> str:
        """
        Detect the primary BMAD agent role from template content or filename.
        
        Priority order:
        1. Check YAML frontmatter 'roles' field (first role in list)
        2. Check YAML frontmatter 'role' field (recommended method)
        3. Check filename patterns
        4. Check content for role indicators
        5. Default to 'developer'
        
        Args:
            content: Template content
            filename: Template filename
            
        Returns:
            Detected agent role identifier (primary role)
        """
        # Valid roles from settings
        valid_roles = [role[0] for role in settings.BMAD_AGENT_ROLES]
        
        # 1. Check frontmatter first (preferred method)
        frontmatter, _ = self.parse_frontmatter(content)
        
        # Check for 'roles' list first (return first role as primary)
        if 'roles' in frontmatter:
            roles = frontmatter['roles']
            if isinstance(roles, list) and roles:
                first_role = roles[0]
                if first_role in valid_roles:
                    return first_role
            elif isinstance(roles, str) and roles in valid_roles:
                return roles
        
        # Check for single 'role' field
        if frontmatter.get('role') in valid_roles:
            return frontmatter['role']
        
        content_lower = content.lower()
        filename_lower = filename.lower()
        
        # 2. Check filename patterns
        if 'orchestrator' in filename_lower:
            return 'orchestrator'
        if 'analyst' in filename_lower:
            return 'analyst'
        if 'pm' in filename_lower or 'project_manager' in filename_lower:
            return 'pm'
        if 'architect' in filename_lower:
            return 'architect'
        if 'scrum' in filename_lower:
            return 'scrum_master'
        if 'developer' in filename_lower or 'dev' in filename_lower:
            return 'developer'
        if 'qa' in filename_lower or 'test' in filename_lower or 'quality' in filename_lower:
            return 'qa'
        
        # 3. Check content for role indicators
        if '## Your Role' in content:
            role_section = content.split('## Your Role')[1].split('##')[0].lower()
            if 'orchestrator' in role_section:
                return 'orchestrator'
            if 'analyst' in role_section:
                return 'analyst'
            if 'project manager' in role_section:
                return 'pm'
            if 'architect' in role_section:
                return 'architect'
            if 'scrum master' in role_section:
                return 'scrum_master'
            if 'developer' in role_section:
                return 'developer'
            if 'qa engineer' in role_section or 'quality assurance' in role_section:
                return 'qa'
        
        # 4. Default to developer if no role detected
        return 'developer'
    
    def detect_workflow_phase(self, content: str, filename: str) -> str:
        """
        Detect the BMAD workflow phase from template content or filename.
        
        Priority order:
        1. Check YAML frontmatter 'workflow_phase' field (recommended method)
        2. Check filename patterns
        3. Check content for phase indicators
        4. Keyword analysis
        5. Default to 'development'
        
        Args:
            content: Template content
            filename: Template filename
            
        Returns:
            Detected workflow phase identifier
        """
        # Valid phases from settings
        valid_phases = [phase[0] for phase in settings.BMAD_WORKFLOW_PHASES]
        
        # 1. Check frontmatter first (preferred method)
        frontmatter, _ = self.parse_frontmatter(content)
        if frontmatter.get('workflow_phase') in valid_phases:
            return frontmatter['workflow_phase']
        
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # 2. Check filename patterns
        if 'planning' in filename_lower or 'plan' in filename_lower:
            return 'planning'
        if 'development' in filename_lower or 'dev' in filename_lower or 'sprint' in filename_lower:
            return 'development'
        
        # 3. Check content for phase indicators
        if 'planning phase' in content_lower:
            return 'planning'
        if 'development phase' in content_lower:
            return 'development'
        
        # 4. Check for typical planning vs development content
        planning_keywords = ['requirements', 'analysis', 'estimate', 'roadmap', 'backlog']
        development_keywords = ['implementation', 'code', 'feature', 'refactor', 'testing']
        
        planning_count = sum(1 for kw in planning_keywords if kw in content_lower)
        development_count = sum(1 for kw in development_keywords if kw in content_lower)
        
        if planning_count > development_count:
            return 'planning'
        
        # 5. Default to development
        return 'development'
    
    def parse_template_description(self, content: str) -> str:
        """
        Extract description from template content.
        
        Priority order:
        1. Check YAML frontmatter 'description' field (recommended method)
        2. Extract from first few lines of content
        
        Args:
            content: Template content
            
        Returns:
            Description string
        """
        # 1. Check frontmatter first (preferred method)
        frontmatter, remaining_content = self.parse_frontmatter(content)
        if frontmatter.get('description'):
            return frontmatter['description']
        
        # 2. Fallback to extracting from content
        lines = remaining_content.strip().split('\n')
        description_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('##') or line.startswith('#'):
                break
            if line:
                description_lines.append(line)
        
        return ' '.join(description_lines[:3]) if description_lines else ''
    
    def sync_templates(self, owner: str, repo: str, branch: str, path: str) -> Dict:
        """
        Synchronize templates from a GitHub repository.
        
        When a template already exists (matched by title or remote_path based on config),
        the existing template is overwritten ensuring only one version shows in the database.
        
        Recursively searches the specified path and all subdirectories for template files.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            path: Directory path containing templates
            
        Returns:
            Dictionary with sync results
        """
        results = {
            'success': True,
            'created': 0,
            'updated': 0,
            'errors': [],
            'templates': [],
        }
        
        # Get sync settings from config
        overwrite_existing = getattr(settings, 'TEMPLATE_SYNC_OVERWRITE', True)
        match_by = getattr(settings, 'TEMPLATE_SYNC_MATCH_BY', 'title')
        
        try:
            # Recursively fetch all files from the directory and subdirectories
            contents = self.fetch_directory_contents_recursive(owner, repo, branch, path)
            
            for item in contents:
                
                filename = item.get('name', '')
                if not filename.endswith(('.md', '.txt', '.template')):
                    continue
                
                content = self.fetch_file_content(owner, repo, branch, item.get('path'))
                if not content:
                    results['errors'].append(f"Failed to fetch: {filename}")
                    continue
                
                # Detect metadata
                agent_role = self.detect_agent_role(content, filename)
                agent_roles = self.detect_agent_roles(content, filename)
                workflow_phase = self.detect_workflow_phase(content, filename)
                description = self.parse_template_description(content)
                
                # Generate title from filename
                title = filename.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').title()
                
                # Build remote URL
                remote_url = f"https://github.com/{owner}/{repo}/blob/{branch}/{item.get('path')}"
                
                # Prepare template data
                template_data = {
                    'content': content,
                    'agent_role': agent_role,
                    'agent_roles': agent_roles,
                    'workflow_phase': workflow_phase,
                    'remote_url': remote_url,
                    'remote_path': item.get('path'),
                    'description': description,
                    'is_active': True,
                }
                
                # Handle template creation/update based on match_by setting
                if overwrite_existing:
                    if match_by == 'title':
                        # Match by title - overwrite any template with the same title
                        template_data['remote_path'] = item.get('path')
                        template, created = Template.objects.update_or_create(
                            title=title,
                            defaults=template_data
                        )
                    else:
                        # Match by remote_path (default behavior)
                        template_data['title'] = title
                        template, created = Template.objects.update_or_create(
                            remote_path=item.get('path'),
                            defaults=template_data
                        )
                else:
                    # No overwrite - only create if doesn't exist
                    template_data['title'] = title
                    template_data['remote_path'] = item.get('path')
                    template, created = Template.objects.get_or_create(
                        title=title,
                        defaults=template_data
                    )
                
                if created:
                    results['created'] += 1
                else:
                    results['updated'] += 1
                
                results['templates'].append({
                    'title': template.title,
                    'agent_role': template.agent_role,
                    'agent_roles': template.agent_roles,
                    'workflow_phase': template.workflow_phase,
                })
        
        except Exception as e:
            results['success'] = False
            results['errors'].append(str(e))
        
        return results
    
    def sync_from_config(self) -> Dict:
        """
        Sync templates using settings configuration from config.yaml.
        
        Returns:
            Dictionary with sync results
        """
        # Get repository settings from config
        repo = getattr(settings, 'TEMPLATE_GITHUB_REPO', None) or settings.TEMPLATE_REPO
        branch = getattr(settings, 'TEMPLATE_GITHUB_BRANCH', 'main')
        remote_path = getattr(settings, 'TEMPLATE_GITHUB_PATH', 'webapp/forge/templates')
        
        # Parse template repo
        repo_parts = repo.split('/')
        if len(repo_parts) != 2:
            return {
                'success': False,
                'errors': ['Invalid TEMPLATE_REPO format. Expected: owner/repo'],
            }
        
        owner, repo_name = repo_parts
        return self.sync_templates(owner, repo_name, branch, remote_path)


def sync_templates_from_github() -> Dict:
    """
    Convenience function to sync templates from configured repository.
    
    Returns:
        Sync results dictionary
    """
    service = GitHubSyncService()
    return service.sync_from_config()
