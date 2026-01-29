"""
Pytest configuration for BMAD Forge tests.
"""

import pytest
from django.test import override_settings


@pytest.fixture
def sample_template_content():
    """Sample BMAD template content for testing."""
    return """
## Your Role
You are an experienced {{agent_role}} specializing in {{domain}}.

## Input
The following information is provided:
{{project_description}}

## Context
This project is part of the {{initiative_name}} initiative.

## Output Requirements
Provide a comprehensive {{deliverable}} that includes:
1. Key objectives and success criteria
2. Implementation approach
3. Timeline and milestones
4. Risk assessment and mitigation strategies

Format the output using Markdown with clear hierarchical structure.
"""


@pytest.fixture
def sample_variables():
    """Expected variables in the sample template."""
    return ['agent_role', 'domain', 'project_description', 'initiative_name', 'deliverable']


@pytest.fixture
def invalid_template_content():
    """Template missing required BMAD sections."""
    return """
# {{title}}

This is a {{type}} document.

{{content}}
"""


@pytest.fixture
def mock_github_response():
    """Mock GitHub API response."""
    return [
        {
            'name': 'analyst_template.md',
            'path': 'templates/analyst_template.md',
            'type': 'file',
            'content': 'bmF0aXZlIGNvbnRlbnQ=',  # base64 encoded "native content"
        },
        {
            'name': 'developer_template.md',
            'path': 'templates/developer_template.md',
            'type': 'file',
            'content': 'c29tZSBjb250ZW50',  # base64 encoded "some content"
        },
    ]
