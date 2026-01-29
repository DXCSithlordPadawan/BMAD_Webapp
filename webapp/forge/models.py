"""
Database models for BMAD Forge application.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import json
import re


class TemplateManager(models.Manager):
    """Custom manager for Template model with multi-role and workflow filtering support."""
    
    def filter_by_role(self, queryset, role):
        """
        Filter templates by role, checking both agent_role and agent_roles fields.
        
        Uses Python-based filtering for cross-database compatibility (works with SQLite,
        PostgreSQL, etc.) since JSONField contains lookup support varies by database.
        
        Args:
            queryset: The queryset to filter
            role: The role to filter by
            
        Returns:
            Filtered queryset containing templates with the specified role
        """
        if not role:
            return queryset
            
        matching_ids = [
            template.id for template in queryset
            if template.has_role(role)
        ]
        return queryset.filter(id__in=matching_ids)
    
    def filter_by_workflow(self, queryset, workflow_phase):
        """
        Filter templates by workflow phase.
        
        Args:
            queryset: The queryset to filter
            workflow_phase: The workflow phase to filter by (e.g., 'planning', 'development')
            
        Returns:
            Filtered queryset containing templates with the specified workflow phase
        """
        if not workflow_phase:
            return queryset
        return queryset.filter(workflow_phase=workflow_phase)


class Template(models.Model):
    """
    Represents a BMAD template synced from a GitHub repository.
    Contains metadata about agent roles, workflow phases, and template content.
    """
    
    # Custom manager
    objects = TemplateManager()
    
    title = models.CharField(
        max_length=255,
        help_text="Template title"
    )
    content = models.TextField(
        help_text="Template content with {{VARIABLE_NAME}} or [VARIABLE_NAME] placeholders"
    )
    agent_role = models.CharField(
        max_length=50,
        choices=settings.BMAD_AGENT_ROLES,
        help_text="Primary BMAD agent role associated with this template"
    )
    agent_roles = models.JSONField(
        default=list,
        blank=True,
        help_text="List of all BMAD agent roles that can use this template"
    )
    workflow_phase = models.CharField(
        max_length=50,
        choices=settings.BMAD_WORKFLOW_PHASES,
        help_text="BMAD workflow phase associated with this template"
    )
    remote_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Original remote URL where this template was synced from"
    )
    remote_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="File path in the remote repository"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Template description and usage instructions"
    )
    version = models.CharField(
        max_length=50,
        default='1.0.0',
        help_text="Template version"
    )
    variables = models.JSONField(
        default=list,
        blank=True,
        help_text="Detected variables in the template"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is active and available for use"
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="Last time this template was updated"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this template was first created"
    )
    
    class Meta:
        ordering = ['agent_role', 'workflow_phase', 'title']
        indexes = [
            models.Index(fields=['agent_role', 'workflow_phase']),
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.agent_role} - {self.workflow_phase})"
    
    def extract_variables(self):
        """
        Extract variables from template content using regex patterns.
        Supports both {{VARIABLE_NAME}} and [VARIABLE_NAME] syntax.
        """
        pattern = r'\{\{(\w+)\}\}|\[(\w+)\]'
        matches = re.findall(pattern, self.content)
        variables = set()
        for match in matches:
            variables.add(match[0] if match[0] else match[1])
        return sorted(list(variables))
    
    def save(self, *args, **kwargs):
        """Override save to auto-extract variables and sync agent_roles."""
        self.variables = self.extract_variables()
        # Ensure agent_roles is initialized and includes the primary agent_role
        if self.agent_roles is None:
            self.agent_roles = []
        if self.agent_role and self.agent_role not in self.agent_roles:
            # Add primary role at the beginning, preserving other roles
            self.agent_roles = [self.agent_role] + [r for r in self.agent_roles if r != self.agent_role]
        super().save(*args, **kwargs)
    
    def get_variables_list(self):
        """Return variables as a list."""
        if isinstance(self.variables, str):
            return json.loads(self.variables)
        return self.variables or []
    
    def get_roles_list(self):
        """Return all roles this template is associated with."""
        if self.agent_roles:
            return self.agent_roles
        return [self.agent_role] if self.agent_role else []
    
    def get_roles_display(self):
        """Return a human-readable string of all roles."""
        role_dict = dict(settings.BMAD_AGENT_ROLES)
        roles = self.get_roles_list()
        return ', '.join(role_dict.get(r, r) for r in roles)
    
    def has_role(self, role: str) -> bool:
        """Check if this template is associated with a specific role."""
        return role in self.get_roles_list()
    
    def generate_prompt(self, **kwargs):
        """
        Generate a prompt by substituting variables with provided values.
        
        Args:
            **kwargs: Variable names and their replacement values
            
        Returns:
            str: Generated prompt with variables substituted
        """
        result = self.content
        for key, value in kwargs.items():
            # Support both {{VAR}} and [VAR] syntax
            result = result.replace('{{' + key + '}}', str(value))
            result = result.replace('[' + key + ']', str(value))
        return result


class GeneratedPrompt(models.Model):
    """
    Represents a generated prompt with user input data and validation results.
    """
    
    template = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name='generated_prompts',
        help_text="The template used to generate this prompt"
    )
    input_data = models.JSONField(
        help_text="User input data used to generate the prompt"
    )
    final_output = models.TextField(
        help_text="The generated prompt output"
    )
    is_valid = models.BooleanField(
        default=False,
        help_text="Whether the generated prompt is BMAD-compliant"
    )
    validation_notes = models.JSONField(
        default=list,
        blank=True,
        help_text="Notes from BMAD validation checks"
    )
    missing_variables = models.JSONField(
        default=list,
        blank=True,
        help_text="List of variables that were not replaced"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this prompt was generated"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['template', 'created_at']),
            models.Index(fields=['is_valid', 'created_at']),
        ]
    
    def __str__(self):
        return f"Generated Prompt from {self.template.title} at {self.created_at}"
    
    def get_input_data_display(self):
        """Return input data as a formatted string."""
        if isinstance(self.input_data, dict):
            return ', '.join(f"{k}: {v}" for k, v in self.input_data.items())
        return str(self.input_data)
    
    def get_validation_status(self):
        """Return validation status as a human-readable string."""
        if self.is_valid:
            return "Valid"
        return f"Invalid ({len(self.missing_variables)} issues)"
