"""
Admin configuration for BMAD Forge models.
"""

from django.contrib import admin
from .models import Template, GeneratedPrompt


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'agent_role', 'workflow_phase', 'version', 'is_active', 'created_at', 'last_updated']
    list_filter = ['agent_role', 'workflow_phase', 'is_active', 'created_at']
    search_fields = ['title', 'content', 'description']
    readonly_fields = ['created_at', 'last_updated', 'variables']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('title', 'content', 'description')
        }),
        ('BMAD Metadata', {
            'fields': ('agent_role', 'workflow_phase', 'version', 'variables')
        }),
        ('Remote Source', {
            'fields': ('remote_url', 'remote_path'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_updated'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GeneratedPrompt)
class GeneratedPromptAdmin(admin.ModelAdmin):
    list_display = ['template', 'is_valid', 'created_at', 'get_input_summary']
    list_filter = ['is_valid', 'template__agent_role', 'created_at']
    search_fields = ['final_output']
    readonly_fields = ['created_at', 'input_data', 'final_output', 'validation_notes', 'missing_variables']
    
    fieldsets = (
        ('Prompt Information', {
            'fields': ('template', 'final_output')
        }),
        ('Input Data', {
            'fields': ('input_data',),
            'classes': ('collapse',)
        }),
        ('Validation', {
            'fields': ('is_valid', 'validation_notes', 'missing_variables')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_input_summary(self, obj):
        """Show a summary of input data."""
        if isinstance(obj.input_data, dict):
            return ', '.join(f"{k}: {v}" for k, v in list(obj.input_data.items())[:3])
        return str(obj.input_data)[:50]
    
    get_input_summary.short_description = 'Input Data'
