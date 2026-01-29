"""
Tests for simulating document generation from all templates in the webapp.
This module ensures all templates in forge/templates/agents can be processed
without errors and validates the document generation pipeline.
"""

import os
import pytest
from forge.models import Template
from forge.services import TemplateParser, DocumentGenerator, BMADValidator


# Define template list once for reuse across all parametrized tests
TEMPLATE_FILES = [
    "architect_prompt.md",
    "backend_prompt.md",
    "devops_prompt.md",
    "frontend_prompt.md",
    "generate_epics.md",
    "phase1.md",
    "phase2.md",
    "phase3.md",
    "prd_generate_epic_prompt.md",
    "productmanager_prompt.md",
    "qa_prompt.md",
    "security_prompt.md",
    "selfdocagent_prompt.md",
    "selfdocslashcommand_prompt.md",
    "uxdesigner_prompt.md",
]


class TestTemplateSimulation:
    """
    Comprehensive tests simulating document generation for each template
    in the webapp/forge/templates/agents directory.
    """

    @pytest.fixture
    def templates_directory(self):
        """Get the path to the agents templates directory."""
        return os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'forge', 'templates', 'agents'
        )

    @pytest.fixture
    def all_template_files(self, templates_directory):
        """List all markdown template files."""
        if not os.path.exists(templates_directory):
            return []
        return [f for f in os.listdir(templates_directory) if f.endswith('.md')]

    def test_templates_directory_exists(self, templates_directory):
        """Verify the templates directory exists."""
        assert os.path.exists(templates_directory), \
            f"Templates directory not found: {templates_directory}"

    def test_templates_are_present(self, all_template_files):
        """Verify templates are present in the directory."""
        assert len(all_template_files) > 0, \
            "No template files found in agents directory"

    @pytest.mark.parametrize("template_file", TEMPLATE_FILES)
    def test_template_file_exists(self, templates_directory, template_file):
        """Test that each expected template file exists."""
        filepath = os.path.join(templates_directory, template_file)
        assert os.path.exists(filepath), f"Template file not found: {template_file}"

    @pytest.mark.parametrize("template_file", TEMPLATE_FILES)
    def test_template_loads_without_error(self, templates_directory, template_file):
        """Test that each template can be loaded and read without errors."""
        filepath = os.path.join(templates_directory, template_file)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert content is not None
        assert len(content) > 0, f"Template {template_file} is empty"

    @pytest.mark.parametrize("template_file", TEMPLATE_FILES)
    def test_template_parser_extracts_variables(self, templates_directory, template_file):
        """Test that the template parser can extract variables without errors."""
        filepath = os.path.join(templates_directory, template_file)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract variables using simple method
        variables_simple = TemplateParser.extract_variables_simple(content)
        assert isinstance(variables_simple, list), \
            f"extract_variables_simple failed for {template_file}"
        
        # Extract variables using detailed method
        variables_detailed = TemplateParser.extract_variables(content)
        assert isinstance(variables_detailed, list), \
            f"extract_variables failed for {template_file}"

    @pytest.mark.parametrize("template_file", TEMPLATE_FILES)
    def test_document_generator_extracts_sections(self, templates_directory, template_file):
        """Test that DocumentGenerator can extract sections without errors."""
        filepath = os.path.join(templates_directory, template_file)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract sections
        sections = DocumentGenerator.extract_sections(content)
        assert isinstance(sections, list), \
            f"extract_sections failed for {template_file}"
        
        # Verify section objects have expected attributes
        for section in sections:
            assert hasattr(section, 'name'), \
                f"Section missing 'name' attribute in {template_file}"
            assert hasattr(section, 'content'), \
                f"Section missing 'content' attribute in {template_file}"

    @pytest.mark.parametrize("template_file", TEMPLATE_FILES)
    def test_document_generator_gets_wizard_steps(self, templates_directory, template_file):
        """Test that DocumentGenerator can generate wizard steps without errors."""
        filepath = os.path.join(templates_directory, template_file)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get wizard steps
        steps = DocumentGenerator.get_wizard_steps(content)
        assert isinstance(steps, list), \
            f"get_wizard_steps failed for {template_file}"

    @pytest.mark.parametrize("template_file", TEMPLATE_FILES)
    def test_template_validation(self, templates_directory, template_file):
        """Test that the template parser validates templates without errors."""
        filepath = os.path.join(templates_directory, template_file)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Validate template
        result = TemplateParser.validate_template(content)
        assert isinstance(result, dict), \
            f"validate_template failed for {template_file}"
        assert 'is_valid' in result
        assert 'errors' in result
        assert 'warnings' in result
        assert 'variables' in result
        assert 'sections' in result

    @pytest.mark.parametrize("template_file", TEMPLATE_FILES)
    def test_simulate_document_generation(self, templates_directory, template_file):
        """
        Simulate complete document generation for each template.
        This tests the full pipeline from template loading to document generation.
        """
        filepath = os.path.join(templates_directory, template_file)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Step 1: Extract variables
        variables = TemplateParser.extract_variables_simple(content)
        
        # Step 2: Create mock values for all variables
        mock_values = {}
        for var in variables:
            mock_values[var] = f"Test value for {var}"
        
        # Step 3: Extract sections
        sections = DocumentGenerator.extract_sections(content)
        
        # Step 4: Create mock section data
        section_data = {}
        for section in sections:
            if hasattr(section, 'name'):
                section_data[section.name] = f"Test content for section {section.name}"
        
        # Step 5: Generate the document
        generated_doc, validations = DocumentGenerator.generate_document(
            content, section_data, mock_values
        )
        
        # Verify generation succeeded
        assert generated_doc is not None, \
            f"Document generation failed for {template_file}"
        assert len(generated_doc) > 0, \
            f"Generated document is empty for {template_file}"
        assert isinstance(validations, list), \
            f"Validations should be a list for {template_file}"

    @pytest.mark.parametrize("template_file", TEMPLATE_FILES)
    def test_simulate_document_generation_with_variable_substitution(
        self, templates_directory, template_file
    ):
        """
        Test document generation with full variable substitution.
        Verifies that variables are properly replaced.
        """
        filepath = os.path.join(templates_directory, template_file)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract variables
        variables = TemplateParser.extract_variables_simple(content)
        
        # Create mock values for all variables
        mock_values = {}
        for var in variables:
            mock_values[var] = f"REPLACED_{var}_VALUE"
        
        # Generate the document
        generated_doc, validations = DocumentGenerator.generate_document(
            content, {}, mock_values
        )
        
        # Verify all provided variables were replaced using the service's method
        remaining_vars = TemplateParser.find_unreplaced_variables(generated_doc)
        
        # Check that provided variables were replaced
        for var in mock_values:
            assert var not in remaining_vars, \
                f"Variable '{var}' was not replaced in {template_file}"
            # Also verify the replacement value appears in the document
            assert mock_values[var] in generated_doc, \
                f"Replacement value for '{var}' not found in {template_file}"

    @pytest.mark.parametrize("template_file", TEMPLATE_FILES)
    def test_bmad_validator_processes_template(self, templates_directory, template_file):
        """Test that BMAD validator can process each template without errors."""
        filepath = os.path.join(templates_directory, template_file)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Run BMAD validation
        report = BMADValidator.validate(content)
        
        # Verify report structure
        assert hasattr(report, 'is_valid')
        assert hasattr(report, 'score')
        assert hasattr(report, 'results')
        assert hasattr(report, 'missing_sections')
        assert hasattr(report, 'unreplaced_variables')

    @pytest.mark.parametrize("template_file", TEMPLATE_FILES)
    def test_document_compliance_validation(self, templates_directory, template_file):
        """Test document compliance validation for each template."""
        filepath = os.path.join(templates_directory, template_file)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Run compliance validation
        report = DocumentGenerator.validate_document_compliance(content)
        
        # Verify report structure
        assert isinstance(report, dict)
        assert 'is_compliant' in report
        assert 'compliance_score' in report
        assert 'missing_sections' in report
        assert 'unreplaced_variables' in report
        assert 'issues' in report
        assert 'warnings' in report


class TestTemplateListIntegrity:
    """Tests to verify template list integrity in the application."""

    @pytest.fixture
    def templates_directory(self):
        """Get the path to the agents templates directory."""
        return os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'forge', 'templates', 'agents'
        )

    def test_all_expected_templates_exist(self, templates_directory):
        """Verify all expected templates exist in the directory."""
        for template_file in TEMPLATE_FILES:
            filepath = os.path.join(templates_directory, template_file)
            assert os.path.exists(filepath), \
                f"Expected template not found: {template_file}"

    def test_no_unexpected_templates(self, templates_directory):
        """Verify there are no unexpected templates in the directory."""
        actual_files = [f for f in os.listdir(templates_directory) if f.endswith('.md')]
        
        for actual_file in actual_files:
            assert actual_file in TEMPLATE_FILES, \
                f"Unexpected template found: {actual_file}"

    def test_template_count_matches(self, templates_directory):
        """Verify the template count matches expected."""
        actual_files = [f for f in os.listdir(templates_directory) if f.endswith('.md')]
        assert len(actual_files) == len(TEMPLATE_FILES), \
            f"Template count mismatch: expected {len(TEMPLATE_FILES)}, found {len(actual_files)}"


@pytest.mark.django_db(transaction=True)
class TestTemplatesDatabaseLoading:
    """Tests for loading templates into the database."""

    @pytest.fixture
    def templates_directory(self):
        """Get the path to the agents templates directory."""
        return os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'forge', 'templates', 'agents'
        )

    def test_load_all_templates_to_database(self, templates_directory):
        """Test that all templates can be loaded into the database."""
        from forge.services import GitHubSyncService
        
        # GitHubSyncService uses class methods that don't require a token
        sync_service = GitHubSyncService()
        
        for filename in os.listdir(templates_directory):
            if not filename.endswith('.md'):
                continue
            
            filepath = os.path.join(templates_directory, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse template metadata using class methods
            title = filename.replace('.md', '').replace('_', ' ').title()
            variables = TemplateParser.extract_variables_simple(content)
            description = sync_service.parse_template_description(content)
            agent_role = sync_service.detect_agent_role(content, filename)
            workflow_phase = sync_service.detect_workflow_phase(content, filename)
            
            # Create or update template
            template, created = Template.objects.update_or_create(
                title=title,
                defaults={
                    'content': content,
                    'agent_role': agent_role,
                    'workflow_phase': workflow_phase,
                    'description': description or '',
                    'variables': variables,
                    'remote_path': filepath,
                    'is_active': True,
                }
            )
            
            # Verify template was created successfully
            assert template is not None
            assert template.title == title
            assert template.content == content
