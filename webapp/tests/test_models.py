"""
Tests for BMAD Forge models.
"""

import pytest
from django.utils import timezone
from forge.models import Template, GeneratedPrompt


@pytest.mark.django_db
class TestTemplateModel:
    """Tests for the Template model."""
    
    def test_create_template(self):
        """Test creating a template."""
        template = Template.objects.create(
            title='Test Template',
            content='## Your Role\nYou are a {{role}}.\n\n## Input\n{{task}}',
            agent_role='developer',
            workflow_phase='development',
        )
        
        assert template.id is not None
        assert template.title == 'Test Template'
        assert template.agent_role == 'developer'
        assert template.workflow_phase == 'development'
        assert template.is_active is True
    
    def test_extract_variables_double_brace(self):
        """Test extracting {{VAR}} style variables."""
        template = Template.objects.create(
            title='Variables Test',
            content='Hello {{name}}, your email is {{email}}.',
            agent_role='developer',
            workflow_phase='development',
        )
        
        variables = template.extract_variables()
        assert 'name' in variables
        assert 'email' in variables
    
    def test_extract_variables_single_bracket(self):
        """Test extracting [VAR] style variables."""
        template = Template.objects.create(
            title='Variables Test',
            content='Project: [project_name], Budget: [budget]',
            agent_role='pm',
            workflow_phase='planning',
        )
        
        variables = template.extract_variables()
        assert 'project_name' in variables
        assert 'budget' in variables
    
    def test_extract_variables_mixed(self):
        """Test extracting mixed variable styles."""
        template = Template.objects.create(
            title='Mixed Variables',
            content='{{var1}} and [var2] and {{var3}}',
            agent_role='architect',
            workflow_phase='planning',
        )
        
        variables = template.extract_variables()
        assert len(variables) == 3
        assert 'var1' in variables
        assert 'var2' in variables
        assert 'var3' in variables
    
    def test_generate_prompt(self):
        """Test prompt generation with variable substitution."""
        template = Template.objects.create(
            title='Generate Test',
            content='Hello {{name}}! You are a {{role}}. [special]',
            agent_role='developer',
            workflow_phase='development',
        )
        
        result = template.generate_prompt(name='John', role='Developer', special='Note')
        
        assert 'Hello John!' in result
        assert 'You are a Developer.' in result
        assert 'Note' in result
    
    def test_get_variables_list(self):
        """Test getting variables as list."""
        template = Template.objects.create(
            title='List Test',
            content='{{a}} {{b}} {{c}}',
            agent_role='qa',
            workflow_phase='development',
        )
        
        variables = template.get_variables_list()
        assert isinstance(variables, list)
        assert len(variables) == 3
    
    def test_string_representation(self):
        """Test string representation of template."""
        template = Template.objects.create(
            title='Test Template',
            content='Test content',
            agent_role='scrum_master',
            workflow_phase='planning',
        )
        
        expected = 'Test Template (scrum_master - planning)'
        assert str(template) == expected
    
    def test_ordering(self):
        """Test default ordering."""
        Template.objects.create(
            title='Z Template', content='test', agent_role='developer', workflow_phase='development'
        )
        Template.objects.create(
            title='A Template', content='test', agent_role='developer', workflow_phase='development'
        )
        
        templates = list(Template.objects.all())
        assert templates[0].title == 'A Template'
        assert templates[1].title == 'Z Template'


@pytest.mark.django_db
class TestTemplateManagerFiltering:
    """Tests for the TemplateManager filtering methods."""
    
    def test_filter_by_workflow_returns_matching_templates(self):
        """Test filter_by_workflow returns only templates in specified phase."""
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
        
        queryset = Template.objects.filter(is_active=True)
        filtered = Template.objects.filter_by_workflow(queryset, 'planning')
        
        assert filtered.count() == 1
        assert filtered.first().title == 'Planning Template'
    
    def test_filter_by_workflow_with_empty_value(self):
        """Test filter_by_workflow returns all templates when workflow is empty."""
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
        
        queryset = Template.objects.filter(is_active=True)
        filtered = Template.objects.filter_by_workflow(queryset, '')
        
        assert filtered.count() == 2
    
    def test_filter_by_workflow_with_none_value(self):
        """Test filter_by_workflow returns all templates when workflow is None."""
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
        
        queryset = Template.objects.filter(is_active=True)
        filtered = Template.objects.filter_by_workflow(queryset, None)
        
        assert filtered.count() == 2
    
    def test_filter_by_role_returns_matching_templates(self):
        """Test filter_by_role returns templates with specified role."""
        Template.objects.create(
            title='Developer Template',
            content='test',
            agent_role='developer',
            workflow_phase='development',
        )
        Template.objects.create(
            title='PM Template',
            content='test',
            agent_role='pm',
            workflow_phase='planning',
        )
        
        queryset = Template.objects.filter(is_active=True)
        filtered = Template.objects.filter_by_role(queryset, 'developer')
        
        assert filtered.count() == 1
        assert filtered.first().title == 'Developer Template'
    
    def test_filter_by_role_with_multi_role_template(self):
        """Test filter_by_role finds templates where role is secondary."""
        Template.objects.create(
            title='Multi-Role Template',
            content='test',
            agent_role='developer',
            agent_roles=['developer', 'architect'],
            workflow_phase='development',
        )
        
        queryset = Template.objects.filter(is_active=True)
        filtered = Template.objects.filter_by_role(queryset, 'architect')
        
        assert filtered.count() == 1
        assert filtered.first().title == 'Multi-Role Template'
    
    def test_combined_role_and_workflow_filtering(self):
        """Test combining filter_by_role and filter_by_workflow."""
        Template.objects.create(
            title='Dev Planning',
            content='test',
            agent_role='developer',
            workflow_phase='planning',
        )
        Template.objects.create(
            title='Dev Development',
            content='test',
            agent_role='developer',
            workflow_phase='development',
        )
        Template.objects.create(
            title='PM Planning',
            content='test',
            agent_role='pm',
            workflow_phase='planning',
        )
        
        queryset = Template.objects.filter(is_active=True)
        queryset = Template.objects.filter_by_workflow(queryset, 'planning')
        queryset = Template.objects.filter_by_role(queryset, 'developer')
        
        assert queryset.count() == 1
        assert queryset.first().title == 'Dev Planning'


@pytest.mark.django_db
class TestGeneratedPromptModel:
    """Tests for the GeneratedPrompt model."""
    
    def test_create_generated_prompt(self):
        """Test creating a generated prompt."""
        template = Template.objects.create(
            title='Test Template',
            content='Hello {{name}}!',
            agent_role='developer',
            workflow_phase='development',
        )
        
        prompt = GeneratedPrompt.objects.create(
            template=template,
            input_data={'name': 'Alice'},
            final_output='Hello Alice!',
            is_valid=True,
            validation_notes=['All sections present'],
        )
        
        assert prompt.id is not None
        assert prompt.template == template
        assert prompt.is_valid is True
    
    def test_get_validation_status_valid(self):
        """Test validation status for valid prompt."""
        template = Template.objects.create(
            title='Test', content='test', agent_role='developer', workflow_phase='development'
        )
        prompt = GeneratedPrompt.objects.create(
            template=template,
            input_data={},
            final_output='test',
            is_valid=True,
        )
        
        assert prompt.get_validation_status() == 'Valid'
    
    def test_get_validation_status_invalid(self):
        """Test validation status for invalid prompt."""
        template = Template.objects.create(
            title='Test', content='test', agent_role='developer', workflow_phase='development'
        )
        prompt = GeneratedPrompt.objects.create(
            template=template,
            input_data={},
            final_output='test',
            is_valid=False,
            missing_variables=['name', 'role'],
        )
        
        status = prompt.get_validation_status()
        assert 'Invalid' in status
        assert '2 issues' in status
    
    def test_ordering(self):
        """Test that prompts are ordered by creation date descending."""
        template = Template.objects.create(
            title='Test', content='test', agent_role='developer', workflow_phase='development'
        )
        
        prompt1 = GeneratedPrompt.objects.create(
            template=template, input_data={}, final_output='first'
        )
        prompt2 = GeneratedPrompt.objects.create(
            template=template, input_data={}, final_output='second'
        )
        
        prompts = list(GeneratedPrompt.objects.all())
        assert prompts[0].id == prompt2.id
        assert prompts[1].id == prompt1.id
