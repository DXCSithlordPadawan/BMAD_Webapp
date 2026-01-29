"""
Tests for BMAD Forge views.
"""

import pytest
from django.urls import reverse
from django.test import override_settings
from django.core.management import call_command
from io import StringIO
from forge.models import Template, GeneratedPrompt


@pytest.mark.django_db
class TestDashboardView:
    """Tests for the dashboard view."""
    
    def test_dashboard_view(self, client):
        """Test dashboard loads correctly."""
        response = client.get(reverse('forge:dashboard'))
        
        assert response.status_code == 200
        assert 'BMAD Forge' in response.content.decode()
    
    def test_dashboard_shows_template_count(self, client):
        """Test dashboard displays template count."""
        Template.objects.create(
            title='Test Template',
            content='test',
            agent_role='developer',
            workflow_phase='development',
        )
        
        response = client.get(reverse('forge:dashboard'))
        
        content = response.content.decode()
        assert '1' in content or 'Total Templates' in content


@pytest.mark.django_db
class TestTemplateListView:
    """Tests for the template list view."""
    
    def test_template_list(self, client):
        """Test template list loads."""
        response = client.get(reverse('forge:template_list'))
        
        assert response.status_code == 200
    
    def test_template_list_with_templates(self, client):
        """Test template list shows templates."""
        Template.objects.create(
            title='Developer Template',
            content='test',
            agent_role='developer',
            workflow_phase='development',
        )
        Template.objects.create(
            title='Analyst Template',
            content='test',
            agent_role='analyst',
            workflow_phase='planning',
        )
        
        response = client.get(reverse('forge:template_list'))
        content = response.content.decode()
        
        assert 'Developer Template' in content
        assert 'Analyst Template' in content
    
    def test_template_filter_by_role(self, client):
        """Test filtering templates by agent role."""
        Template.objects.create(
            title='Dev Template',
            content='test',
            agent_role='developer',
            workflow_phase='development',
        )
        Template.objects.create(
            title='Analyst Template',
            content='test',
            agent_role='analyst',
            workflow_phase='planning',
        )
        
        response = client.get(reverse('forge:template_list') + '?agent_role=developer')
        content = response.content.decode()
        
        assert 'Dev Template' in content
        assert 'Analyst Template' not in content
    
    def test_template_search(self, client):
        """Test searching templates."""
        Template.objects.create(
            title='Authentication Template',
            content='test',
            agent_role='developer',
            workflow_phase='development',
        )
        
        response = client.get(reverse('forge:template_list') + '?search=auth')
        content = response.content.decode()
        
        assert 'Authentication Template' in content
    
    def test_template_filter_by_role_with_multi_roles(self, client):
        """Test filtering templates by role when templates have multiple roles."""
        # Create a template with multiple roles where 'architect' is secondary
        Template.objects.create(
            title='Multi-Role Template',
            content='test',
            agent_role='developer',
            agent_roles=['developer', 'architect'],
            workflow_phase='development',
        )
        # Create a template with only architect role
        Template.objects.create(
            title='Architect Only',
            content='test',
            agent_role='architect',
            workflow_phase='planning',
        )
        # Create a template with no architect role
        Template.objects.create(
            title='QA Only',
            content='test',
            agent_role='qa',
            workflow_phase='development',
        )
        
        # Filter by architect - should show both templates with architect role
        response = client.get(reverse('forge:template_list') + '?agent_role=architect')
        content = response.content.decode()
        
        assert 'Multi-Role Template' in content
        assert 'Architect Only' in content
        assert 'QA Only' not in content
    
    def test_template_filter_multi_role_shows_all_roles_in_display(self, client):
        """Test that templates display all their roles in the template list."""
        Template.objects.create(
            title='Multi-Role Display Test',
            content='test',
            agent_role='developer',
            agent_roles=['developer', 'architect', 'qa'],
            workflow_phase='development',
        )
        
        response = client.get(reverse('forge:template_list'))
        content = response.content.decode()
        
        # Check that all roles are displayed
        assert 'DEVELOPER' in content
        assert 'ARCHITECT' in content
        assert 'QA' in content
    
    def test_template_filter_by_workflow_phase(self, client):
        """Test filtering templates by workflow phase."""
        Template.objects.create(
            title='Planning Template',
            content='test',
            agent_role='pm',
            workflow_phase='planning',
        )
        Template.objects.create(
            title='Development Template',
            content='test',
            agent_role='developer',
            workflow_phase='development',
        )
        
        # Filter by planning phase
        response = client.get(reverse('forge:template_list') + '?workflow_phase=planning')
        content = response.content.decode()
        
        assert 'Planning Template' in content
        assert 'Development Template' not in content
    
    def test_template_filter_by_workflow_phase_development(self, client):
        """Test filtering templates by development workflow phase."""
        Template.objects.create(
            title='Planning Template',
            content='test',
            agent_role='pm',
            workflow_phase='planning',
        )
        Template.objects.create(
            title='Development Template',
            content='test',
            agent_role='developer',
            workflow_phase='development',
        )
        
        # Filter by development phase
        response = client.get(reverse('forge:template_list') + '?workflow_phase=development')
        content = response.content.decode()
        
        assert 'Development Template' in content
        assert 'Planning Template' not in content
    
    def test_template_filter_combined_role_and_workflow(self, client):
        """Test filtering templates by both agent role and workflow phase."""
        # Developer in planning phase
        Template.objects.create(
            title='Dev Planning',
            content='test',
            agent_role='developer',
            workflow_phase='planning',
        )
        # Developer in development phase
        Template.objects.create(
            title='Dev Development',
            content='test',
            agent_role='developer',
            workflow_phase='development',
        )
        # PM in planning phase
        Template.objects.create(
            title='PM Planning',
            content='test',
            agent_role='pm',
            workflow_phase='planning',
        )
        
        # Filter by developer AND planning
        response = client.get(reverse('forge:template_list') + '?agent_role=developer&workflow_phase=planning')
        content = response.content.decode()
        
        assert 'Dev Planning' in content
        assert 'Dev Development' not in content
        assert 'PM Planning' not in content


@pytest.mark.django_db
class TestDashboardMultiRoles:
    """Tests for multi-role support in the dashboard."""
    
    def test_dashboard_counts_templates_by_all_roles(self, client):
        """Test that dashboard counts templates for all their roles."""
        # Create a template with multiple roles
        Template.objects.create(
            title='Multi-Role Template',
            content='test',
            agent_role='developer',
            agent_roles=['developer', 'architect'],
            workflow_phase='development',
        )
        
        response = client.get(reverse('forge:dashboard'))
        
        # The template should be counted for both developer and architect
        context = response.context
        templates_by_role = context.get('templates_by_role', {})
        
        # Both roles should have a count of 1
        assert templates_by_role.get('developer', 0) >= 1
        assert templates_by_role.get('architect', 0) >= 1


@pytest.mark.django_db
class TestPromptFormView:
    """Tests for the prompt generation form view."""
    
    def test_prompt_form_loads(self, client):
        """Test prompt form loads correctly."""
        template = Template.objects.create(
            title='Test Template',
            content='Hello {{name}}!',
            agent_role='developer',
            workflow_phase='development',
        )
        
        response = client.get(reverse('forge:prompt_form', args=[template.id]))
        
        assert response.status_code == 200
    
    def test_prompt_form_generates_prompt(self, client):
        """Test form submission generates a prompt."""
        template = Template.objects.create(
            title='Test Template',
            content='Hello {{name}}!',
            agent_role='developer',
            workflow_phase='development',
        )
        
        response = client.post(
            reverse('forge:prompt_form', args=[template.id]),
            {'name': 'World'}
        )
        
        assert response.status_code == 302
        assert GeneratedPrompt.objects.filter(template=template).exists()


@pytest.mark.django_db
class TestPromptResultView:
    """Tests for the prompt result view."""
    
    def test_prompt_result_view(self, client):
        """Test viewing a generated prompt."""
        template = Template.objects.create(
            title='Test',
            content='Hello {{name}}!',
            agent_role='developer',
            workflow_phase='development',
        )
        prompt = GeneratedPrompt.objects.create(
            template=template,
            input_data={'name': 'World'},
            final_output='Hello World!',
            is_valid=True,
        )
        
        response = client.get(reverse('forge:prompt_result', args=[prompt.id]))
        
        assert response.status_code == 200
        assert 'Hello World!' in response.content.decode()
    
    def test_prompt_result_shows_validation(self, client):
        """Test validation status is displayed."""
        template = Template.objects.create(
            title='Test',
            content='test',
            agent_role='developer',
            workflow_phase='development',
        )
        prompt = GeneratedPrompt.objects.create(
            template=template,
            input_data={},
            final_output='test',
            is_valid=False,
            validation_notes=['Missing section'],
        )
        
        response = client.get(reverse('forge:prompt_result', args=[prompt.id]))
        content = response.content.decode()
        
        assert 'Invalid' in content or 'Needs Review' in content


@pytest.mark.django_db
class TestGitHubSyncView:
    """Tests for the GitHub sync view."""
    
    def test_sync_view_loads(self, client):
        """Test sync view loads."""
        response = client.get(reverse('forge:github_sync'))
        
        assert response.status_code == 200
        assert 'GitHub' in response.content.decode() or 'Sync' in response.content.decode()


@pytest.mark.django_db
class TestPromptHistoryView:
    """Tests for the prompt history view."""
    
    def test_history_view_loads(self, client):
        """Test history view loads."""
        response = client.get(reverse('forge:prompt_history'))
        
        assert response.status_code == 200
    
    def test_history_shows_prompts(self, client):
        """Test history displays generated prompts."""
        template = Template.objects.create(
            title='Test',
            content='test',
            agent_role='developer',
            workflow_phase='development',
        )
        GeneratedPrompt.objects.create(
            template=template,
            input_data={},
            final_output='test',
            is_valid=True,
        )
        
        response = client.get(reverse('forge:prompt_history'))
        content = response.content.decode()
        
        assert 'Test' in content


@pytest.mark.django_db
class TestGenerateDocumentSelectView:
    """Tests for the document generation selection view."""
    
    def test_generate_document_select_loads(self, client):
        """Test generate document selection page loads."""
        response = client.get(reverse('forge:generate_document_select'))
        
        assert response.status_code == 200
        assert 'Generate Document' in response.content.decode()
    
    def test_generate_document_select_shows_templates(self, client):
        """Test that templates are displayed for selection."""
        Template.objects.create(
            title='Test Template',
            content='## Your Role\nTest role',
            agent_role='developer',
            workflow_phase='development',
        )
        
        response = client.get(reverse('forge:generate_document_select'))
        content = response.content.decode()
        
        assert 'Test Template' in content


@pytest.mark.django_db
class TestGenerateDocumentWizardView:
    """Tests for the document generation wizard view."""
    
    def test_wizard_view_loads(self, client):
        """Test wizard view loads for a template."""
        template = Template.objects.create(
            title='Wizard Template',
            content='## Your Role\nYou are a developer.\n\n## Input\nTask description.\n\n## Output Requirements\nFormat specs.',
            agent_role='developer',
            workflow_phase='development',
        )
        
        response = client.get(reverse('forge:generate_document_wizard', args=[template.id]))
        
        assert response.status_code == 200
        assert 'Wizard Template' in response.content.decode()
    
    def test_wizard_shows_steps(self, client):
        """Test wizard displays section steps."""
        template = Template.objects.create(
            title='Multi-Section Template',
            content='## Section One\nContent one.\n\n## Section Two\nContent two.',
            agent_role='developer',
            workflow_phase='development',
        )
        
        response = client.get(reverse('forge:generate_document_wizard', args=[template.id]))
        content = response.content.decode()
        
        assert 'Section One' in content or 'Step' in content
    
    def test_wizard_navigation_next(self, client):
        """Test navigating to next step in wizard."""
        template = Template.objects.create(
            title='Nav Template',
            content='## Section One\nContent one.\n\n## Section Two\nContent two.',
            agent_role='developer',
            workflow_phase='development',
        )
        
        response = client.post(
            reverse('forge:generate_document_wizard', args=[template.id]),
            {'current_step': 1, 'action': 'next', 'section_content': 'Test content'}
        )
        
        assert response.status_code == 302
        assert '?step=2' in response.url
    
    def test_wizard_generates_document(self, client):
        """Test wizard generates document on final step."""
        template = Template.objects.create(
            title='Generate Template',
            content='## Your Role\nYou are a developer.\n\n## Input\nTask description.\n\n## Output Requirements\nFormat specs.',
            agent_role='developer',
            workflow_phase='development',
        )
        
        # First, set up session data by navigating through steps
        session = client.session
        session[f'doc_gen_{template.id}'] = {
            'Your Role': 'Test role content',
            'Input': 'Test input content',
            'Output Requirements': 'Test output content',
        }
        session.save()
        
        response = client.post(
            reverse('forge:generate_document_wizard', args=[template.id]) + '?step=3',
            {'current_step': 3, 'action': 'generate', 'section_content': 'Final content'}
        )
        
        # Should redirect to prompt result
        assert response.status_code == 302
        assert GeneratedPrompt.objects.filter(template=template).exists()


@pytest.mark.django_db
class TestHealthCheckView:
    """Tests for the HTTP health check endpoint."""

    def test_health_check_endpoint_healthy(self, client):
        """Health check returns 200 when all systems operational."""
        response = client.get(reverse('forge:health_check'))

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'checks' in data
        assert 'database' in data['checks']
        assert 'cache' in data['checks']

    def test_health_check_includes_app_info(self, client):
        """Health check includes application name and version."""
        response = client.get(reverse('forge:health_check'))

        data = response.json()
        assert 'app' in data
        assert 'version' in data

    @override_settings(
        DEBUG=True,
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            }
        }
    )
    def test_health_check_with_dummy_cache_in_debug(self, client):
        """Health check handles DummyCache gracefully in DEBUG mode."""
        response = client.get(reverse('forge:health_check'))

        assert response.status_code == 200
        data = response.json()
        # Should be OK even with DummyCache in development
        assert 'cache' in data['checks']
        assert 'ok' in data['checks']['cache'].lower()


@pytest.mark.django_db
class TestHealthCheckManagementCommand:
    """Tests for the health_check management command."""

    @override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'unique-snowflake',
            }
        }
    )
    def test_health_check_command_success(self):
        """Management command succeeds when systems healthy."""
        out = StringIO()

        # Should exit with code 0 (success)
        with pytest.raises(SystemExit) as exc_info:
            call_command('health_check', stdout=out)

        assert exc_info.value.code == 0
        output = out.getvalue()
        assert '✓ Database: OK' in output
        assert '✓ Cache: OK' in output
        assert 'HEALTH CHECK PASSED' in output

    @override_settings(
        DEBUG=True,
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            }
        }
    )
    def test_health_check_command_with_dummy_cache(self):
        """Management command handles DummyCache in development."""
        out = StringIO()

        with pytest.raises(SystemExit) as exc_info:
            call_command('health_check', stdout=out)

        assert exc_info.value.code == 0
        output = out.getvalue()
        assert 'Cache: OK' in output
