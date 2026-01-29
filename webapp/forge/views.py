"""
Views for BMAD Forge application.
"""

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, FormView, TemplateView, View
from django.http import JsonResponse, FileResponse, HttpResponse
from django.contrib import messages
from django.conf import settings
from django.db import models
from django.views.decorators.http import require_http_methods
from .models import Template, GeneratedPrompt
from .forms import DynamicPromptForm, TemplateFilterForm, GitHubSyncForm
from .services import GitHubSyncService, BMADValidator, DocumentGenerator
from .services.bmad_validator import MetadataAwareValidator
from .services.template_parser import TemplateParser


class DashboardView(TemplateView):
    """
    Dashboard view showing template count and recent generated prompts.
    """
    
    template_name = 'forge/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_templates'] = Template.objects.filter(is_active=True).count()
        context['templates_by_role'] = self._get_templates_by_role()
        context['templates_by_phase'] = self._get_templates_by_phase()
        context['recent_prompts'] = GeneratedPrompt.objects.select_related('template')[:5]
        context['recent_templates'] = Template.objects.filter(is_active=True).order_by('-created_at')[:5]
        return context
    
    def _get_templates_by_role(self):
        """Get template counts grouped by agent role.
        
        Counts templates for each role, considering that templates can have
        multiple roles stored in the agent_roles JSONField.
        """
        from collections import Counter
        
        templates = Template.objects.filter(is_active=True)
        role_counts = Counter()
        
        for template in templates:
            # Use the get_roles_list() method which handles both agent_role 
            # and agent_roles fields
            for role in template.get_roles_list():
                role_counts[role] += 1
        
        return dict(role_counts)
    
    def _get_templates_by_phase(self):
        """Get template counts grouped by workflow phase."""
        return dict(
            Template.objects.filter(is_active=True)
            .values('workflow_phase')
            .annotate(count=models.Count('id'))
            .values_list('workflow_phase', 'count')
        )


class TemplateListView(ListView):
    """
    List view for browsing and filtering templates.
    """
    
    model = Template
    template_name = 'forge/template_list.html'
    context_object_name = 'templates'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Template.objects.filter(is_active=True)
        
        # Apply filters
        agent_role = self.request.GET.get('agent_role')
        workflow_phase = self.request.GET.get('workflow_phase')
        search = self.request.GET.get('search')
        
        # Filter by workflow phase using the custom manager
        queryset = Template.objects.filter_by_workflow(queryset, workflow_phase)
        
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(content__icontains=search)
            )
        
        # Filter by role - handles multi-role templates using the custom manager
        queryset = Template.objects.filter_by_role(queryset, agent_role)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = TemplateFilterForm(self.request.GET)
        context['agent_roles'] = settings.BMAD_AGENT_ROLES
        context['workflow_phases'] = settings.BMAD_WORKFLOW_PHASES
        return context


class TemplateDetailView(DetailView):
    """
    Detail view showing template content and metadata.
    """
    
    model = Template
    template_name = 'forge/template_detail.html'
    context_object_name = 'template'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['variables'] = self.object.get_variables_list()
        return context


class PromptFormView(FormView):
    """
    Form view for generating prompts from templates.
    """
    
    template_name = 'forge/prompt_form.html'
    
    def get_template(self):
        template_id = self.kwargs.get('template_id')
        return get_object_or_404(Template, id=template_id, is_active=True)
    
    def get_form(self, form_class=None):
        template = self.get_template()
        form = DynamicPromptForm(template=template, **self.get_form_kwargs())
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['template'] = self.get_template()
        return context
    
    def form_valid(self, form):
        template = self.get_template()
        
        # Generate the prompt
        final_output = form.generate_output()
        
        # Validate the generated prompt
        validation_report = BMADValidator.validate(final_output)
        
        # Create the GeneratedPrompt record
        generated_prompt = GeneratedPrompt.objects.create(
            template=template,
            input_data=form.cleaned_data,
            final_output=final_output,
            is_valid=validation_report.is_valid,
            validation_notes=validation_report.notes,
            missing_variables=validation_report.unreplaced_variables,
        )
        
        # Add messages
        if validation_report.is_valid:
            messages.success(self.request, 'Prompt generated successfully!')
        else:
            messages.warning(
                self.request,
                f'Prompt generated with {len(validation_report.results)} issues'
            )
        
        return redirect('forge:prompt_result', pk=generated_prompt.id)


class PromptResultView(DetailView):
    """
    View for displaying generated prompt with validation results.
    """
    
    model = GeneratedPrompt
    template_name = 'forge/prompt_result.html'
    context_object_name = 'prompt'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['validation_report'] = self.object.get_validation_status()
        
        # Get validation details
        validator_report = BMADValidator.validate(self.object.final_output)
        context['validation_details'] = validator_report
        
        return context


class PromptHistoryView(ListView):
    """
    View showing history of generated prompts.
    """
    
    model = GeneratedPrompt
    template_name = 'forge/prompt_history.html'
    context_object_name = 'prompts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = GeneratedPrompt.objects.select_related('template')
        
        # Filter by validation status
        status = self.request.GET.get('status')
        if status == 'valid':
            queryset = queryset.filter(is_valid=True)
        elif status == 'invalid':
            queryset = queryset.filter(is_valid=False)
        
        return queryset


class GitHubSyncView(FormView):
    """
    View for GitHub synchronization interface.
    """
    
    template_name = 'forge/github_sync.html'
    form_class = GitHubSyncForm
    
    def get_initial(self):
        """Set initial values from settings."""
        return {
            'repo_url': f"https://github.com/{settings.TEMPLATE_REPO}",
            'path': 'webapp/forge/templates',
        }
    
    def form_valid(self, form):
        # Parse repository URL
        repo_url = form.cleaned_data['repo_url']
        path = form.cleaned_data['path']
        branch = form.cleaned_data.get('branch', 'main')
        
        # Extract owner and repo from URL
        parts = repo_url.rstrip('/').split('/')
        if len(parts) >= 2:
            owner = parts[-2]
            repo = parts[-1]
        else:
            messages.error(self.request, 'Invalid repository URL')
            return redirect('forge:github_sync')
        
        # Perform sync
        service = GitHubSyncService()
        results = service.sync_templates(owner, repo, branch, path)
        
        if results['success']:
            messages.success(
                self.request,
                f"Sync completed: {results['created']} created, {results['updated']} updated"
            )
        else:
            messages.error(self.request, f"Sync failed: {', '.join(results['errors'])}")
        
        return redirect('forge:template_list')


def manual_sync(request):
    """
    Manual sync endpoint using configured repository.
    """
    service = GitHubSyncService()
    results = service.sync_from_config()
    
    if results['success']:
        messages.success(
            request,
            f"Sync completed: {results['created']} created, {results['updated']} updated"
        )
    else:
        messages.error(request, f"Sync failed: {', '.join(results['errors'])}")
    
    return redirect('forge:template_list')


def download_prompt(request, pk):
    """
    Download generated prompt as a Markdown file.
    """
    prompt = get_object_or_404(GeneratedPrompt, pk=pk)
    
    response = HttpResponse(
        prompt.final_output,
        content_type='text/markdown; charset=utf-8'
    )
    filename = f"bmad_prompt_{pk}_{prompt.created_at.strftime('%Y%m%d_%H%M%S')}.md"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def health_check(request):
    """
    Health check endpoint for monitoring.
    Checks database and cache connectivity.
    Returns 200 for healthy, 503 for unhealthy.
    """
    from django.db import connection
    from django.core.cache import cache

    health_status = {
        'status': 'healthy',
        'app': settings.APP_NAME,
        'version': settings.APP_VERSION,
        'checks': {}
    }

    # Check database connectivity
    try:
        connection.ensure_connection()
        health_status['checks']['database'] = 'ok'
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = f'error: {str(e)}'

    # Check cache connectivity
    try:
        cache.set('health_check', 'ok', 10)
        result = cache.get('health_check')
        if result == 'ok':
            health_status['checks']['cache'] = 'ok'
        elif settings.DEBUG and 'DummyCache' in str(settings.CACHES['default']['BACKEND']):
            # DummyCache in development - this is expected
            health_status['checks']['cache'] = 'ok (DummyCache)'
        else:
            health_status['checks']['cache'] = 'warning: not functioning'
    except Exception as e:
        health_status['checks']['cache'] = f'error: {str(e)}'

    # Return 503 if unhealthy, 200 if healthy
    status_code = 503 if health_status['status'] == 'unhealthy' else 200
    return JsonResponse(health_status, status=status_code)


class GenerateDocumentSelectView(ListView):
    """
    View for selecting a template to generate a document from.
    """
    
    model = Template
    template_name = 'forge/generate_document_select.html'
    context_object_name = 'templates'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Template.objects.filter(is_active=True)
        
        # Apply filters
        agent_role = self.request.GET.get('agent_role')
        workflow_phase = self.request.GET.get('workflow_phase')
        search = self.request.GET.get('search')
        
        # Filter by workflow phase using the custom manager
        queryset = Template.objects.filter_by_workflow(queryset, workflow_phase)
        
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(content__icontains=search)
            )
        
        # Filter by role - handles multi-role templates using the custom manager
        queryset = Template.objects.filter_by_role(queryset, agent_role)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = TemplateFilterForm(self.request.GET)
        context['agent_roles'] = settings.BMAD_AGENT_ROLES
        context['workflow_phases'] = settings.BMAD_WORKFLOW_PHASES
        return context


class GenerateDocumentWizardView(TemplateView):
    """
    Wizard view for interactive document generation.
    Presents template sections one at a time and collects user input.
    """

    template_name = 'forge/generate_document_wizard.html'

    def get_template_object(self):
        template_id = self.kwargs.get('template_id')
        return get_object_or_404(Template, id=template_id, is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        template = self.get_template_object()

        # Get enhanced wizard steps with metadata from DocumentGenerator
        wizard_steps = DocumentGenerator.get_enhanced_wizard_steps(template.content)

        # Get current step from query param
        current_step = int(self.request.GET.get('step', 1))
        current_step = max(1, min(current_step, len(wizard_steps)))

        context['template'] = template
        context['wizard_steps'] = wizard_steps
        context['current_step'] = current_step
        context['total_steps'] = len(wizard_steps)

        if wizard_steps:
            current_section = wizard_steps[current_step - 1]
            context['current_section'] = current_section

        # Get stored section data from session
        session_key = f'doc_gen_{template.id}'
        context['section_data'] = self.request.session.get(session_key, {})

        return context
    
    def post(self, request, *args, **kwargs):
        template = self.get_template_object()
        wizard_steps = DocumentGenerator.get_wizard_steps(template.content)
        
        current_step = int(request.POST.get('current_step', 1))
        action = request.POST.get('action', 'next')
        
        # Store section data in session
        session_key = f'doc_gen_{template.id}'
        section_data = request.session.get(session_key, {})
        
        # Get current section name
        if wizard_steps and 1 <= current_step <= len(wizard_steps):
            current_section = wizard_steps[current_step - 1]
            section_name = current_section['section_name']
            
            # Store the section content
            section_content = request.POST.get('section_content', '')
            section_data[section_name] = section_content
            
            # Store variable values
            for var in current_section.get('variables', []):
                var_value = request.POST.get(f'var_{var}', '')
                section_data[f'var_{var}'] = var_value
            
            request.session[session_key] = section_data
        
        # Handle navigation
        if action == 'prev' and current_step > 1:
            return redirect(f"{request.path}?step={current_step - 1}")
        elif action == 'next' and current_step < len(wizard_steps):
            return redirect(f"{request.path}?step={current_step + 1}")
        elif action == 'generate':
            # Generate the final document
            return self._generate_document(request, template, section_data, wizard_steps)
        
        return redirect(f"{request.path}?step={current_step}")
    
    def _generate_document(self, request, template, section_data, wizard_steps):
        """Generate the final document and create a GeneratedPrompt record."""
        # Separate section content from variable data
        variable_data = {}
        section_content = {}
        
        for key, value in section_data.items():
            if key.startswith('var_'):
                var_name = key[4:]  # Remove 'var_' prefix
                variable_data[var_name] = value
            else:
                section_content[key] = value
        
        # Generate the document
        final_output, validations = DocumentGenerator.generate_document(
            template.content,
            section_content,
            variable_data
        )
        
        # Validate for BMAD compliance
        compliance_report = DocumentGenerator.validate_document_compliance(final_output)
        
        # Also run the existing BMADValidator for comprehensive validation
        bmad_report = BMADValidator.validate(final_output)
        
        # Create the GeneratedPrompt record
        generated_prompt = GeneratedPrompt.objects.create(
            template=template,
            input_data={
                'sections': section_content,
                'variables': variable_data,
            },
            final_output=final_output,
            is_valid=compliance_report['is_compliant'] and bmad_report.is_valid,
            validation_notes=compliance_report['warnings'] + compliance_report['issues'],
            missing_variables=compliance_report['unreplaced_variables'],
        )
        
        # Clear session data
        session_key = f'doc_gen_{template.id}'
        if session_key in request.session:
            del request.session[session_key]
        
        # Add messages
        if generated_prompt.is_valid:
            messages.success(request, 'Document generated successfully with full BMAD compliance!')
        else:
            issue_count = len(compliance_report['issues'])
            messages.warning(
                request,
                f'Document generated with {issue_count} validation issue(s). Review and fix as needed.'
            )
        
        return redirect('forge:prompt_result', pk=generated_prompt.id)


def validate_section_realtime(request, template_id):
    """
    API endpoint for real-time section validation.
    Returns validation results as JSON for immediate feedback.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body)
        section_name = data.get('section_name', '')
        content = data.get('content', '')

        # Get template for metadata
        template = get_object_or_404(Template, id=template_id, is_active=True)

        # Perform enhanced real-time validation with metadata
        validation = DocumentGenerator.validate_section_with_metadata(
            section_name, content, template.content
        )

        return JsonResponse(validation.to_dict())

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_section_guidance(request, template_id, section_name):
    """
    API endpoint for getting contextual guidance for a section.
    Returns help text, examples, and validation requirements.
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'GET method required'}, status=405)

    try:
        template = get_object_or_404(Template, id=template_id, is_active=True)

        # Get guidance for the section
        guidance = DocumentGenerator.get_section_help(section_name, template.content)

        return JsonResponse(guidance)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def validate_variable(request, template_id):
    """
    API endpoint for validating a single variable value.
    Returns validation result with errors if any.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body)
        variable_name = data.get('variable_name', '')
        value = data.get('value', '')

        if not variable_name:
            return JsonResponse({'error': 'variable_name is required'}, status=400)

        template = get_object_or_404(Template, id=template_id, is_active=True)

        # Validate the variable
        result = MetadataAwareValidator.validate_variable(
            variable_name, value, template.content
        )

        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_completion_status(request, template_id):
    """
    API endpoint for getting overall completion status of the wizard.
    Returns completion percentage and per-step status.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body)
        section_data = data.get('section_data', {})
        variable_data = data.get('variable_data', {})

        template = get_object_or_404(Template, id=template_id, is_active=True)

        # Get wizard steps
        wizard_steps = DocumentGenerator.get_enhanced_wizard_steps(template.content)

        # Calculate completion status
        status = DocumentGenerator.calculate_completion_status(
            wizard_steps, section_data, variable_data, template.content
        )

        return JsonResponse(status)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_enhanced_wizard_steps(request, template_id):
    """
    API endpoint for getting enhanced wizard steps with metadata.
    Returns steps with validation rules, guidance, and structured fields.
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'GET method required'}, status=405)

    try:
        template = get_object_or_404(Template, id=template_id, is_active=True)

        # Get enhanced wizard steps
        steps = DocumentGenerator.get_enhanced_wizard_steps(template.content)

        return JsonResponse({'steps': steps, 'total_steps': len(steps)})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
