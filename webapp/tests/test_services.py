"""
Tests for BMAD Forge services.
"""

import pytest
from forge.services import TemplateParser, BMADValidator, GitHubSyncService


class TestTemplateParser:
    """Tests for the TemplateParser service."""
    
    def test_extract_variables_simple(self):
        """Test basic variable extraction."""
        content = "Hello {{name}}, welcome to {{place}}."
        variables = TemplateParser.extract_variables_simple(content)
        
        assert len(variables) == 2
        assert 'name' in variables
        assert 'place' in variables
    
    def test_extract_variables_mixed_syntax(self):
        """Test extracting mixed variable syntax."""
        content = "{{double}} and [single] and {{another}}"
        variables = TemplateParser.extract_variables_simple(content)
        
        assert len(variables) == 3
        assert 'double' in variables
        assert 'single' in variables
        assert 'another' in variables
    
    def test_extract_variables_with_defaults(self):
        """Test extracting variables with default values."""
        content = "{{name:John}} {{email:john@example.com}}"
        variables = TemplateParser.extract_variables_simple(content)
        
        assert len(variables) == 2
        assert 'name' in variables
        assert 'email' in variables
    
    def test_detect_sections(self):
        """Test section detection."""
        content = """
## Your Role
You are a developer.

## Input
Some input

## Output Requirements
Format output
"""
        sections = TemplateParser.detect_sections(content)
        
        assert '## Your Role' in sections
        assert '## Input' in sections
        assert '## Output Requirements' in sections
    
    def test_check_required_sections_all_present(self):
        """Test required sections check when all present."""
        content = """
## Your Role
Developer

## Input
Task description

## Output Requirements
Format requirements
"""
        is_valid, missing = TemplateParser.check_required_sections(content)
        
        assert is_valid is True
        assert len(missing) == 0
    
    def test_check_required_sections_missing(self):
        """Test required sections check when some missing."""
        content = """
## Your Role
Developer
"""
        is_valid, missing = TemplateParser.check_required_sections(content)
        
        assert is_valid is False
        assert len(missing) == 2
        assert '## Input' in missing
        assert '## Output Requirements' in missing
    
    def test_substitute_variables(self):
        """Test variable substitution."""
        content = "Hello {{name}}, you work at {{company}}."
        values = {'name': 'Alice', 'company': 'ACME'}
        
        result = TemplateParser.substitute_variables(content, values)
        
        assert result == "Hello Alice, you work at ACME."
    
    def test_find_unreplaced_variables(self):
        """Test finding unreplaced variables."""
        content = "Hello {{name}}, {{greeting}}!"
        values = {'name': 'Alice'}  # greeting not provided
        
        unreplaced = TemplateParser.find_unreplaced_variables(
            TemplateParser.substitute_variables(content, values)
        )
        
        assert 'greeting' in unreplaced
    
    def test_validate_template_valid(self):
        """Test template validation with valid template."""
        content = """
## Your Role
You are a developer.

## Input
Build a feature.

## Output Requirements
Provide code with tests.
"""
        result = TemplateParser.validate_template(content)
        
        assert result['is_valid'] is True
        assert len(result['errors']) == 0
    
    def test_validate_template_missing_sections(self):
        """Test template validation with missing sections."""
        content = "# Just a title"
        result = TemplateParser.validate_template(content)
        
        assert result['is_valid'] is False
        assert len(result['errors']) > 0


class TestBMADValidator:
    """Tests for the BMADValidator service."""
    
    def test_validate_valid_prompt(self):
        """Test validating a BMAD-compliant prompt."""
        prompt = """
## Your Role
You are an experienced software developer.

## Input
Implement a user authentication system with the following requirements:
- User registration
- Login/logout
- Password reset

## Output Requirements
Provide the following:
1. Complete source code
2. Unit tests with 80% coverage
3. Documentation
4. Integration instructions
"""
        report = BMADValidator.validate(prompt)
        
        assert report.is_valid is True
        assert report.score > 0
    
    def test_validate_missing_role_section(self):
        """Test validation fails without Your Role section."""
        prompt = """
## Input
Some task

## Output Requirements
Output format
"""
        report = BMADValidator.validate(prompt)
        
        assert report.is_valid is False
        assert '## Your Role' in report.missing_sections
    
    def test_validate_with_unreplaced_variables(self):
        """Test validation fails with unreplaced variables."""
        prompt = """
## Your Role
You are {{role}}.

## Input
{{task}}

## Output Requirements
Provide results.
"""
        report = BMADValidator.validate(prompt)
        
        assert report.is_valid is False
        assert len(report.unreplaced_variables) > 0
    
    def test_quick_validate_valid(self):
        """Test quick validation for valid prompt."""
        prompt = """
## Your Role
Developer

## Input
Task

## Output Requirements
Format
"""
        is_valid, issues = BMADValidator.quick_validate(prompt)
        
        assert is_valid is True
        assert len(issues) == 0
    
    def test_quick_validate_invalid(self):
        """Test quick validation for invalid prompt."""
        prompt = "Just some text"
        is_valid, issues = BMADValidator.quick_validate(prompt)
        
        assert is_valid is False
        assert len(issues) > 0


class TestGitHubSyncService:
    """Tests for the GitHubSyncService."""
    
    def test_detect_agent_role_from_filename(self):
        """Test agent role detection from filename."""
        service = GitHubSyncService()
        
        assert service.detect_agent_role('content', 'developer_template.md') == 'developer'
        assert service.detect_agent_role('content', 'analyst_report.md') == 'analyst'
        assert service.detect_agent_role('content', 'pm_planning.md') == 'pm'
    
    def test_detect_workflow_phase_from_filename(self):
        """Test workflow phase detection from filename."""
        service = GitHubSyncService()
        
        assert service.detect_workflow_phase('content', 'planning_template.md') == 'planning'
        assert service.detect_workflow_phase('content', 'development_sprint.md') == 'development'
    
    def test_parse_template_description(self):
        """Test description extraction from template."""
        service = GitHubSyncService()
        
        content = """This is a brief description.

More details here.

## Your Role
..."""
        description = service.parse_template_description(content)
        
        assert 'brief description' in description
        assert '## Your Role' not in description
    
    def test_init_with_token(self):
        """Test service initialization with token."""
        service = GitHubSyncService(token='test-token')
        
        assert service.token == 'test-token'
        assert 'Authorization' in service.headers
    
    def test_fetch_directory_contents_recursive_files_only(self):
        """Test recursive fetch returns only files when directory has no subdirectories."""
        service = GitHubSyncService()
        
        # Mock fetch_directory_contents to return files only
        original_fetch = service.fetch_directory_contents
        service.fetch_directory_contents = lambda o, r, b, p: [
            {'name': 'file1.md', 'path': 'templates/file1.md', 'type': 'file'},
            {'name': 'file2.md', 'path': 'templates/file2.md', 'type': 'file'},
        ]
        
        result = service.fetch_directory_contents_recursive('owner', 'repo', 'main', 'templates')
        
        assert len(result) == 2
        assert all(item['type'] == 'file' for item in result)
        
        # Restore original method
        service.fetch_directory_contents = original_fetch
    
    def test_fetch_directory_contents_recursive_with_subdirectories(self):
        """Test recursive fetch traverses subdirectories and returns all files."""
        service = GitHubSyncService()
        
        # Track calls to verify recursion
        call_paths = []
        
        def mock_fetch(owner, repo, branch, path):
            call_paths.append(path)
            if path == 'templates':
                return [
                    {'name': 'file1.md', 'path': 'templates/file1.md', 'type': 'file'},
                    {'name': 'subdir', 'path': 'templates/subdir', 'type': 'dir'},
                ]
            elif path == 'templates/subdir':
                return [
                    {'name': 'file2.md', 'path': 'templates/subdir/file2.md', 'type': 'file'},
                    {'name': 'nested', 'path': 'templates/subdir/nested', 'type': 'dir'},
                ]
            elif path == 'templates/subdir/nested':
                return [
                    {'name': 'file3.md', 'path': 'templates/subdir/nested/file3.md', 'type': 'file'},
                ]
            return []
        
        service.fetch_directory_contents = mock_fetch
        
        result = service.fetch_directory_contents_recursive('owner', 'repo', 'main', 'templates')
        
        # Should have 3 files from all levels
        assert len(result) == 3
        file_paths = [f['path'] for f in result]
        assert 'templates/file1.md' in file_paths
        assert 'templates/subdir/file2.md' in file_paths
        assert 'templates/subdir/nested/file3.md' in file_paths
        
        # Verify all directories were traversed
        assert 'templates' in call_paths
        assert 'templates/subdir' in call_paths
        assert 'templates/subdir/nested' in call_paths
    
    def test_fetch_directory_contents_recursive_empty_directory(self):
        """Test recursive fetch handles empty directories gracefully."""
        service = GitHubSyncService()
        
        service.fetch_directory_contents = lambda o, r, b, p: []
        
        result = service.fetch_directory_contents_recursive('owner', 'repo', 'main', 'templates')
        
        assert result == []
    
    def test_fetch_directory_contents_recursive_mixed_content(self):
        """Test recursive fetch correctly filters files from mixed directory content."""
        service = GitHubSyncService()
        
        def mock_fetch(owner, repo, branch, path):
            if path == 'templates':
                return [
                    {'name': 'file1.md', 'path': 'templates/file1.md', 'type': 'file'},
                    {'name': 'readme.txt', 'path': 'templates/readme.txt', 'type': 'file'},
                    {'name': 'empty_subdir', 'path': 'templates/empty_subdir', 'type': 'dir'},
                ]
            elif path == 'templates/empty_subdir':
                return []  # Empty subdirectory
            return []
        
        service.fetch_directory_contents = mock_fetch
        
        result = service.fetch_directory_contents_recursive('owner', 'repo', 'main', 'templates')
        
        # Should have 2 files (empty subdir contributes nothing)
        assert len(result) == 2
        assert all(item['type'] == 'file' for item in result)
    
    def test_fetch_directory_contents_recursive_max_depth_protection(self):
        """Test recursive fetch stops at maximum depth to prevent excessive recursion."""
        service = GitHubSyncService()
        
        # Create a deeply nested structure that exceeds MAX_RECURSION_DEPTH
        def mock_fetch(owner, repo, branch, path):
            depth = path.count('/') + 1
            return [
                {'name': f'file_{depth}.md', 'path': f'{path}/file_{depth}.md', 'type': 'file'},
                {'name': f'level_{depth + 1}', 'path': f'{path}/level_{depth + 1}', 'type': 'dir'},
            ]
        
        service.fetch_directory_contents = mock_fetch
        
        result = service.fetch_directory_contents_recursive('owner', 'repo', 'main', 'level_0')
        
        # Should stop at MAX_RECURSION_DEPTH (10), so we get files from levels 0-9
        assert len(result) <= service.MAX_RECURSION_DEPTH
    
    def test_fetch_directory_contents_recursive_circular_reference_protection(self):
        """Test recursive fetch handles circular references (symlinks) gracefully."""
        service = GitHubSyncService()
        
        call_count = [0]  # Use list to allow modification in nested function
        
        def mock_fetch(owner, repo, branch, path):
            call_count[0] += 1
            if call_count[0] > 20:  # Safety limit for test
                return []
            if path == 'templates':
                return [
                    {'name': 'file1.md', 'path': 'templates/file1.md', 'type': 'file'},
                    {'name': 'subdir', 'path': 'templates/subdir', 'type': 'dir'},
                ]
            elif path == 'templates/subdir':
                return [
                    {'name': 'file2.md', 'path': 'templates/subdir/file2.md', 'type': 'file'},
                    # Simulate circular reference back to parent
                    {'name': 'link_to_templates', 'path': 'templates', 'type': 'dir'},
                ]
            return []
        
        service.fetch_directory_contents = mock_fetch
        
        result = service.fetch_directory_contents_recursive('owner', 'repo', 'main', 'templates')
        
        # Should complete without infinite loop
        assert len(result) == 2  # Only file1.md and file2.md
        file_paths = [f['path'] for f in result]
        assert 'templates/file1.md' in file_paths
        assert 'templates/subdir/file2.md' in file_paths


class TestDocumentGenerator:
    """Tests for the DocumentGenerator service."""
    
    def test_extract_sections(self):
        """Test extracting sections from template content."""
        from forge.services import DocumentGenerator
        
        content = """# Document Title

## Section One
Content for section one.

## Section Two
Content for section two.

### Subsection
More content here.
"""
        sections = DocumentGenerator.extract_sections(content)
        
        assert len(sections) >= 3
        section_names = [s.name for s in sections]
        assert 'Document Title' in section_names
        assert 'Section One' in section_names
        assert 'Section Two' in section_names
    
    def test_validate_section_content_valid(self):
        """Test section validation with valid content."""
        from forge.services import DocumentGenerator
        
        result = DocumentGenerator.validate_section_content(
            "Your Role",
            "You are an experienced software developer with responsibility for implementing features."
        )
        
        assert result.is_valid is True
        assert len(result.unreplaced_variables) == 0
    
    def test_validate_section_content_with_unreplaced_variables(self):
        """Test section validation detects unreplaced variables (100% detection requirement)."""
        from forge.services import DocumentGenerator
        
        result = DocumentGenerator.validate_section_content(
            "Input",
            "Process the {{file_name}} and analyze the [data_source]."
        )
        
        assert result.is_valid is False
        assert 'file_name' in result.unreplaced_variables
        assert 'data_source' in result.unreplaced_variables
    
    def test_validate_section_content_short_content(self):
        """Test section validation warns about short content."""
        from forge.services import DocumentGenerator
        
        result = DocumentGenerator.validate_section_content(
            "Context",
            "Brief."
        )
        
        # Should have warnings about short content
        assert len(result.warnings) > 0
    
    def test_get_wizard_steps(self):
        """Test generating wizard steps from template content."""
        from forge.services import DocumentGenerator
        
        content = """## Your Role
You are a developer.

## Input
Task description.

## Output Requirements
Format specifications.
"""
        steps = DocumentGenerator.get_wizard_steps(content)
        
        assert len(steps) == 3
        assert steps[0]['section_name'] == 'Your Role'
        assert steps[1]['section_name'] == 'Input'
        assert steps[2]['section_name'] == 'Output Requirements'
    
    def test_validate_document_compliance_valid(self):
        """Test document compliance validation with valid content."""
        from forge.services import DocumentGenerator
        
        content = """## Your Role
You are an experienced software developer.

## Input
Build a user authentication system.

## Output Requirements
Provide complete source code with tests.
"""
        report = DocumentGenerator.validate_document_compliance(content)
        
        assert report['is_compliant'] is True
        assert len(report['missing_sections']) == 0
        assert len(report['unreplaced_variables']) == 0
    
    def test_validate_document_compliance_missing_sections(self):
        """Test document compliance validation detects missing sections."""
        from forge.services import DocumentGenerator
        
        content = """## Your Role
Just a partial document.
"""
        report = DocumentGenerator.validate_document_compliance(content)
        
        assert report['is_compliant'] is False
        assert '## Input' in report['missing_sections']
        assert '## Output Requirements' in report['missing_sections']
    
    def test_validate_document_compliance_unreplaced_variables(self):
        """Test document compliance validation detects unreplaced variables (100% detection)."""
        from forge.services import DocumentGenerator
        
        content = """## Your Role
You are {{role_name}}.

## Input
Process {{input_data}}.

## Output Requirements
Return formatted output.
"""
        report = DocumentGenerator.validate_document_compliance(content)
        
        assert report['is_compliant'] is False
        assert 'role_name' in report['unreplaced_variables']
        assert 'input_data' in report['unreplaced_variables']


class TestLoadLocalTemplates:
    """Tests for load_local_templates.py script functionality."""

    @staticmethod
    def _get_template_directories():
        """Helper to import TEMPLATE_DIRECTORIES from load_local_templates module."""
        import sys
        import os

        # Add webapp to path to import the module
        webapp_path = os.path.join(os.path.dirname(__file__), '..')
        if webapp_path not in sys.path:
            sys.path.insert(0, webapp_path)

        from load_local_templates import TEMPLATE_DIRECTORIES
        return TEMPLATE_DIRECTORIES

    def test_template_directories_constant_contains_both_directories(self):
        """Test that TEMPLATE_DIRECTORIES includes both agents and templates directories."""
        template_dirs = self._get_template_directories()

        assert 'forge/templates/agents' in template_dirs
        assert 'forge/templates/templates' in template_dirs
        assert len(template_dirs) == 2

    def test_template_directories_exist(self):
        """Test that all configured template directories exist on disk."""
        import os

        base_dir = os.path.join(os.path.dirname(__file__), '..')
        template_dirs = self._get_template_directories()

        for template_dir in template_dirs:
            full_path = os.path.join(base_dir, template_dir)
            assert os.path.exists(full_path), f"Template directory should exist: {full_path}"
            assert os.path.isdir(full_path), f"Should be a directory: {full_path}"

    def test_template_directories_contain_md_files(self):
        """Test that both template directories contain markdown files."""
        import os

        base_dir = os.path.join(os.path.dirname(__file__), '..')
        template_dirs = self._get_template_directories()
        min_count = 10  # Each directory should have at least 10 template files

        for template_dir in template_dirs:
            full_path = os.path.join(base_dir, template_dir)
            md_files = [f for f in os.listdir(full_path) if f.endswith('.md')]
            assert len(md_files) >= min_count, \
                f"Directory {template_dir} should have at least {min_count} .md files, found {len(md_files)}"


class TestSectionMetadata:
    """Tests for SectionMetadata parsing and validation."""

    def test_parse_section_metadata_from_frontmatter(self):
        """Test parsing section metadata from YAML frontmatter."""
        from forge.services.template_parser import TemplateParser, SectionMetadata

        content = '''---
name: test-template
sections:
  "Your Role":
    required: true
    min_words: 20
    help_text: "Define the AI persona"
    keywords_required:
      - responsibility
      - expertise
    validation_severity: critical
---
## Your Role
Content here.
'''
        metadata = TemplateParser.parse_section_metadata(content)

        assert 'Your Role' in metadata
        section = metadata['Your Role']
        assert section.required is True
        assert section.min_words == 20
        assert section.help_text == "Define the AI persona"
        assert 'responsibility' in section.keywords_required
        assert section.validation_severity.value == 'critical'

    def test_parse_section_metadata_empty_frontmatter(self):
        """Test parsing returns empty dict for content without section metadata."""
        from forge.services.template_parser import TemplateParser

        content = '''---
name: test-template
role: developer
---
## Your Role
Content here.
'''
        metadata = TemplateParser.parse_section_metadata(content)
        assert metadata == {}

    def test_section_metadata_from_dict(self):
        """Test creating SectionMetadata from dictionary."""
        from forge.services.template_parser import SectionMetadata, ValidationSeverity

        data = {
            'required': True,
            'min_words': 25,
            'max_words': 100,
            'help_text': 'Test help',
            'keywords_required': ['test', 'keyword'],
            'validation_severity': 'warning',
            'examples': ['Example 1', 'Example 2'],
        }

        section = SectionMetadata.from_dict('Test Section', data)

        assert section.name == 'Test Section'
        assert section.required is True
        assert section.min_words == 25
        assert section.max_words == 100
        assert section.help_text == 'Test help'
        assert section.keywords_required == ['test', 'keyword']
        assert section.validation_severity == ValidationSeverity.WARNING
        assert len(section.examples) == 2


class TestVariableMetadata:
    """Tests for VariableMetadata parsing and validation."""

    def test_parse_variable_metadata_from_frontmatter(self):
        """Test parsing variable metadata from YAML frontmatter."""
        from forge.services.template_parser import TemplateParser

        content = '''---
name: test-template
variables:
  PROJECT_NAME:
    description: "The project name"
    required: true
    validation: "^[A-Za-z][A-Za-z0-9_-]*$"
    help_text: "Use alphanumeric characters only"
  FRAMEWORK:
    description: "Framework to use"
    required: false
    input_type: select
    options:
      - React
      - Vue
      - Angular
---
Content here.
'''
        metadata = TemplateParser.parse_variable_metadata(content)

        assert 'PROJECT_NAME' in metadata
        assert 'FRAMEWORK' in metadata

        project_var = metadata['PROJECT_NAME']
        assert project_var.description == "The project name"
        assert project_var.required is True
        assert project_var.validation_pattern == "^[A-Za-z][A-Za-z0-9_-]*$"

        framework_var = metadata['FRAMEWORK']
        assert framework_var.input_type == 'select'
        assert 'React' in framework_var.options
        assert framework_var.required is False

    def test_validate_variable_value_with_pattern(self):
        """Test variable validation with regex pattern."""
        from forge.services.template_parser import TemplateParser, VariableMetadata

        metadata = VariableMetadata(
            name='PROJECT_NAME',
            required=True,
            validation_pattern='^[A-Za-z][A-Za-z0-9_-]*$'
        )

        # Valid value
        is_valid, errors = TemplateParser.validate_variable_value('PROJECT_NAME', 'MyProject', metadata)
        assert is_valid is True
        assert len(errors) == 0

        # Invalid value (starts with number)
        is_valid, errors = TemplateParser.validate_variable_value('PROJECT_NAME', '123Project', metadata)
        assert is_valid is False
        assert len(errors) > 0

    def test_validate_variable_value_required(self):
        """Test variable validation for required fields."""
        from forge.services.template_parser import TemplateParser, VariableMetadata

        metadata = VariableMetadata(name='REQUIRED_VAR', required=True)

        # Empty value for required field
        is_valid, errors = TemplateParser.validate_variable_value('REQUIRED_VAR', '', metadata)
        assert is_valid is False
        assert any('required' in e.lower() for e in errors)

    def test_validate_variable_value_select_options(self):
        """Test variable validation for select options."""
        from forge.services.template_parser import TemplateParser, VariableMetadata

        metadata = VariableMetadata(
            name='FRAMEWORK',
            input_type='select',
            options=['React', 'Vue', 'Angular']
        )

        # Valid option
        is_valid, errors = TemplateParser.validate_variable_value('FRAMEWORK', 'React', metadata)
        assert is_valid is True

        # Invalid option
        is_valid, errors = TemplateParser.validate_variable_value('FRAMEWORK', 'Svelte', metadata)
        assert is_valid is False


class TestSectionValidation:
    """Tests for section validation against metadata."""

    def test_validate_section_against_metadata_valid(self):
        """Test section validation with valid content."""
        from forge.services.template_parser import TemplateParser, SectionMetadata, ValidationSeverity

        metadata = SectionMetadata(
            name='Your Role',
            required=True,
            min_words=10,
            keywords_required=['responsibility'],
            validation_severity=ValidationSeverity.CRITICAL
        )

        content = "You are an experienced developer with responsibility for implementing features and ensuring code quality."

        result = TemplateParser.validate_section_against_metadata('Your Role', content, metadata)

        assert result.is_valid is True
        assert result.word_count >= 10
        assert len(result.errors) == 0
        assert len(result.missing_keywords) == 0

    def test_validate_section_against_metadata_missing_words(self):
        """Test section validation fails with insufficient words."""
        from forge.services.template_parser import TemplateParser, SectionMetadata, ValidationSeverity

        metadata = SectionMetadata(
            name='Your Role',
            required=True,
            min_words=20,
            validation_severity=ValidationSeverity.CRITICAL
        )

        content = "You are a developer."  # Only 4 words

        result = TemplateParser.validate_section_against_metadata('Your Role', content, metadata)

        assert result.is_valid is False
        assert result.word_count < 20
        assert len(result.errors) > 0

    def test_validate_section_against_metadata_missing_keywords(self):
        """Test section validation fails with missing required keywords."""
        from forge.services.template_parser import TemplateParser, SectionMetadata, ValidationSeverity

        metadata = SectionMetadata(
            name='Your Role',
            required=True,
            min_words=5,
            keywords_required=['responsibility', 'expertise'],
            validation_severity=ValidationSeverity.CRITICAL
        )

        content = "You are an experienced developer with great skills."

        result = TemplateParser.validate_section_against_metadata('Your Role', content, metadata)

        assert result.is_valid is False
        assert 'responsibility' in result.missing_keywords
        assert 'expertise' in result.missing_keywords

    def test_validate_section_with_unreplaced_variables(self):
        """Test section validation detects unreplaced variables."""
        from forge.services.template_parser import TemplateParser, SectionMetadata

        metadata = SectionMetadata(name='Input', min_words=5)

        content = "Process the {{file_name}} from [data_source] location."

        result = TemplateParser.validate_section_against_metadata('Input', content, metadata)

        assert result.is_valid is False
        assert any('unreplaced' in e.lower() for e in result.errors)

    def test_get_section_metadata_with_defaults(self):
        """Test getting section metadata with fallback defaults."""
        from forge.services.template_parser import TemplateParser

        content = '''## Your Role
Developer content.

## Input
Input content.

## Custom Section
Custom content.
'''
        metadata = TemplateParser.get_section_metadata_with_defaults(content)

        # Standard sections should have defaults
        assert 'Your Role' in metadata
        assert metadata['Your Role'].required is True
        assert metadata['Your Role'].min_words == 20

        assert 'Input' in metadata
        assert metadata['Input'].required is True

        # Custom section should have generic defaults
        assert 'Custom Section' in metadata
        assert metadata['Custom Section'].required is False


class TestEnhancedDocumentGenerator:
    """Tests for enhanced document generator functionality."""

    def test_validate_section_with_metadata(self):
        """Test enhanced section validation with metadata support."""
        from forge.services import DocumentGenerator

        template_content = '''---
name: test-template
sections:
  "Your Role":
    required: true
    min_words: 15
    keywords_recommended:
      - responsibility
      - expertise
---
## Your Role
Template content.
'''
        section_content = "You are an experienced developer with responsibility for implementing features and expertise in testing."

        result = DocumentGenerator.validate_section_with_metadata(
            'Your Role',
            section_content,
            template_content
        )

        assert result.is_valid is True
        assert result.word_count >= 15
        assert hasattr(result, 'completion_percentage')

    def test_get_enhanced_wizard_steps(self):
        """Test getting enhanced wizard steps with metadata."""
        from forge.services import DocumentGenerator

        template_content = '''---
name: test-template
sections:
  "Your Role":
    required: true
    min_words: 20
    help_text: "Define the AI persona"
variables:
  PROJECT_NAME:
    description: "Project name"
    required: true
---
## Your Role
{{PROJECT_NAME}} template content.

## Input
Input content.
'''
        steps = DocumentGenerator.get_enhanced_wizard_steps(template_content)

        # Should have at least 3 steps: Template Variables + 2 sections
        assert len(steps) >= 3
        
        # First step should be Template Variables (since template has variables in frontmatter)
        first_step = steps[0]
        assert first_step['section_name'] == 'Template Variables'
        assert first_step['metadata']['min_words'] == 0
        assert 'PROJECT_NAME' in first_step['variables']
        
        # Second step should be "Your Role"
        second_step = steps[1]
        assert 'metadata' in second_step
        assert 'guidance' in second_step
        assert second_step['metadata']['required'] is True
        assert second_step['metadata']['min_words'] == 20

    def test_calculate_completion_status(self):
        """Test calculating overall wizard completion status."""
        from forge.services import DocumentGenerator

        template_content = '''## Your Role
Content.

## Input
Content.
'''
        wizard_steps = DocumentGenerator.get_enhanced_wizard_steps(template_content)

        section_data = {
            'Your Role': 'You are an experienced developer with responsibility for implementing high quality software solutions.',
        }
        variable_data = {}

        status = DocumentGenerator.calculate_completion_status(
            wizard_steps,
            section_data,
            variable_data,
            template_content
        )

        assert 'overall_completion' in status
        assert 'completed_steps' in status
        assert 'total_steps' in status
        assert 'is_ready_to_generate' in status
        assert 'step_statuses' in status


class TestMetadataAwareValidator:
    """Tests for the MetadataAwareValidator service."""

    def test_validate_with_metadata_valid_prompt(self):
        """Test metadata-aware validation with valid content."""
        from forge.services.bmad_validator import MetadataAwareValidator

        template_content = '''---
name: test-template
sections:
  "Your Role":
    required: true
    min_words: 10
---
## Your Role
Template role content.

## Input
Template input content.

## Output Requirements
Template output content.
'''
        prompt_content = '''## Your Role
You are an experienced software developer with expertise in building applications.

## Input
Build a user authentication system with login and registration.

## Output Requirements
Provide complete source code with unit tests and documentation.
'''
        result = MetadataAwareValidator.validate_with_metadata(prompt_content, template_content)

        assert result.is_valid is True
        assert result.overall_score > 50
        assert len(result.errors) == 0

    def test_validate_with_metadata_missing_section(self):
        """Test metadata-aware validation detects missing required sections."""
        from forge.services.bmad_validator import MetadataAwareValidator

        template_content = '''---
name: test-template
---
## Your Role
Content.

## Input
Content.

## Output Requirements
Content.
'''
        prompt_content = '''## Your Role
You are a developer.
'''
        result = MetadataAwareValidator.validate_with_metadata(prompt_content, template_content)

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any('Input' in e for e in result.errors)

    def test_get_section_guidance(self):
        """Test getting section guidance from metadata."""
        from forge.services.bmad_validator import MetadataAwareValidator

        template_content = '''---
name: test-template
sections:
  "Your Role":
    help_text: "Define the AI persona and responsibilities"
    min_words: 20
    examples:
      - "You are an expert developer..."
---
## Your Role
Content.
'''
        guidance = MetadataAwareValidator.get_section_guidance('Your Role', template_content)

        assert 'help_text' in guidance
        assert guidance['help_text'] == "Define the AI persona and responsibilities"
        assert guidance['min_words'] == 20

    def test_validate_variable(self):
        """Test validating individual variable values."""
        from forge.services.bmad_validator import MetadataAwareValidator

        template_content = '''---
name: test-template
variables:
  PROJECT_NAME:
    required: true
    validation: "^[A-Za-z][A-Za-z0-9_-]*$"
---
Content.
'''
        # Valid value
        result = MetadataAwareValidator.validate_variable('PROJECT_NAME', 'MyProject', template_content)
        assert result['is_valid'] is True

        # Invalid value
        result = MetadataAwareValidator.validate_variable('PROJECT_NAME', '123Invalid', template_content)
        assert result['is_valid'] is False


class TestLegacyTemplateCompatibility:
    """Tests for backward compatibility with templates without metadata."""

    def test_legacy_template_gets_default_metadata(self):
        """Test that templates without frontmatter metadata get sensible defaults."""
        from forge.services.template_parser import TemplateParser

        content = '''## Your Role
You are a developer.

## Input
Task description.

## Output Requirements
Format output.
'''
        metadata = TemplateParser.get_section_metadata_with_defaults(content)

        # Should have defaults for standard sections
        assert 'Your Role' in metadata
        assert metadata['Your Role'].required is True
        assert metadata['Your Role'].min_words == 20

    def test_legacy_template_validation_works(self):
        """Test that validation works on templates without metadata."""
        from forge.services import DocumentGenerator

        content = '''## Your Role
You are an experienced developer with responsibility for building software.

## Input
Build a feature.

## Output Requirements
Provide code.
'''
        # Should work without errors
        result = DocumentGenerator.validate_section_with_metadata(
            'Your Role',
            'You are an experienced developer with responsibility for building applications.',
            content
        )

        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'completion_percentage')

    def test_frontmatter_parsing_handles_no_frontmatter(self):
        """Test frontmatter parsing handles content without frontmatter."""
        from forge.services.template_parser import TemplateParser

        content = '''## Your Role
No frontmatter here.

## Input
Just content.
'''
        frontmatter, remaining = TemplateParser.parse_frontmatter(content)

        assert frontmatter == {}
        assert '## Your Role' in remaining
