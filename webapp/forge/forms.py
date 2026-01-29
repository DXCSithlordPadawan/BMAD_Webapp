"""
Forms for BMAD Forge application.
"""

from django import forms
from django.conf import settings
from .models import Template, GeneratedPrompt


class DynamicPromptForm(forms.Form):
    """
    Dynamic form that generates fields based on template variables.
    """
    
    def __init__(self, *args, template=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.template = template
        
        if template:
            variables = template.get_variables_list()
            for var in variables:
                # Create field name without special characters for form field
                field_name = var.lower().replace(' ', '_')
                
                # Determine if this should be a textarea (long content)
                long_vars = ['description', 'context', 'details', 'requirements', 'content', 'instructions']
                is_long = any(long_var in var.lower() for long_var in long_vars)
                
                if is_long:
                    field_class = forms.CharField(widget=forms.Textarea(attrs={
                        'class': 'form-control',
                        'rows': 4,
                        'placeholder': f'Enter {var}',
                    }))
                else:
                    field_class = forms.CharField(widget=forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': f'Enter {var}',
                    }))
                
                field_class.label = var.replace('_', ' ').title()
                field_class.help_text = f"Value for {var}"
                self.fields[field_name] = field_class
    
    def generate_output(self):
        """Generate the prompt output using form data."""
        if not self.template:
            return None
        
        # Map form field names to template variable names
        output_data = {}
        variables = self.template.get_variables_list()
        
        for var in variables:
            field_name = var.lower().replace(' ', '_')
            output_data[var] = self.cleaned_data.get(field_name, '')
        
        return self.template.generate_prompt(**output_data)


class TemplateFilterForm(forms.Form):
    """
    Form for filtering templates in the library.
    """
    
    agent_role = forms.ChoiceField(
        choices=[('', 'All Roles')] + list(settings.BMAD_AGENT_ROLES),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
    )
    workflow_phase = forms.ChoiceField(
        choices=[('', 'All Phases')] + list(settings.BMAD_WORKFLOW_PHASES),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
    )
    search = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search templates...',
        }),
        required=False,
    )


class GitHubSyncForm(forms.Form):
    """
    Form for GitHub sync configuration.
    """
    
    repo_url = forms.URLField(
        label='Repository URL',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://github.com/owner/repo',
        }),
        help_text="GitHub repository URL containing BMAD templates"
    )
    
    branch = forms.CharField(
        initial='main',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'main',
        }),
        help_text="Branch to sync from"
    )
    
    path = forms.CharField(
        initial='templates',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'templates',
        }),
        help_text="Directory path containing template files"
    )


class GeneratedPromptForm(forms.ModelForm):
    """
    Form for manually creating or editing generated prompts.
    """
    
    class Meta:
        model = GeneratedPrompt
        fields = ['template', 'input_data', 'final_output', 'is_valid', 'validation_notes']
        widgets = {
            'template': forms.Select(attrs={'class': 'form-select'}),
            'input_data': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
            }),
            'final_output': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
            }),
            'is_valid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'validation_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
        }
