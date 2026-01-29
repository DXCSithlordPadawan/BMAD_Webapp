# BMAD Forge API Guide

## Overview

This document provides comprehensive documentation for the BMAD Forge API endpoints. The API enables programmatic access to template management, prompt generation, document wizards, and validation services.

## Base URL

```
Development: http://localhost:8000
Production:  https://your-domain.com
```

## Authentication

Currently, BMAD Forge uses session-based authentication for the admin interface. API endpoints for public template browsing do not require authentication.

### CSRF Protection

All POST, PUT, PATCH, and DELETE requests require a CSRF token. Include the token in either:

- **Header:** `X-CSRFToken: <token>`
- **Cookie:** Automatically included when using session authentication

```javascript
// JavaScript example
fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify(data)
});
```

---

## API Endpoints

### Health Check

#### GET /health/

Check application health status.

**Response:**
```json
{
    "status": "healthy",
    "app": "BMAD Forge",
    "version": "1.3.0",
    "checks": {
        "database": "ok",
        "cache": "ok"
    }
}
```

**Status Codes:**
| Code | Description |
|------|-------------|
| 200 | Application healthy |
| 503 | Service unavailable |

---

### Templates

#### GET /templates/

List all active templates with optional filtering.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `role` | string | Filter by agent role (developer, architect, pm, qa, etc.) |
| `phase` | string | Filter by workflow phase (planning, development) |
| `search` | string | Search in title and description |
| `page` | integer | Page number for pagination |

**Example Request:**
```bash
curl "http://localhost:8000/templates/?role=developer&phase=development"
```

**Response:** HTML page with template list

---

#### GET /templates/{id}/

Get detailed information about a specific template.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Template ID |

**Response:** HTML page with template details

---

### Prompt Generation

#### GET /generate/{template_id}/

Display the prompt generation form for a template.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `template_id` | integer | Template ID |

**Response:** HTML form for prompt generation

---

#### POST /generate/{template_id}/

Generate a prompt from a template with provided variables.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `template_id` | integer | Template ID |

**Request Body:** Form data with variable values

**Response:** Redirect to generated prompt result page

---

#### GET /prompts/{id}/

View a generated prompt.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Generated prompt ID |

**Response:** HTML page with generated prompt

---

#### GET /prompts/{id}/download/

Download a generated prompt as a markdown file.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Generated prompt ID |

**Response:**
- Content-Type: `text/markdown`
- Content-Disposition: `attachment; filename="prompt_{id}.md"`

---

#### GET /prompts/history/

View history of generated prompts.

**Response:** HTML page with prompt history

---

### Document Generation Wizard

#### GET /generate-document/

Display template selection for document generation wizard.

**Response:** HTML page with template selection

---

#### GET /generate-document/{template_id}/

Display the interactive document generation wizard.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `template_id` | integer | Template ID |

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `step` | integer | Current wizard step (default: 1) |

**Response:** HTML wizard interface

---

#### POST /generate-document/{template_id}/

Submit wizard step data and navigate.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `template_id` | integer | Template ID |

**Request Body:** Form data
| Field | Type | Description |
|-------|------|-------------|
| `current_step` | integer | Current step number |
| `action` | string | Navigation action: `prev`, `next`, or `generate` |
| `section_content` | string | Content for current section |
| `var_{name}` | string | Variable values |

**Response:** Redirect to next step or generated result

---

### Real-Time Validation API

#### POST /generate-document/{template_id}/validate/

Validate section content in real-time with enhanced metadata support.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `template_id` | integer | Template ID |

**Request Body:**
```json
{
    "section_name": "Your Role",
    "content": "You are an experienced developer..."
}
```

**Response:**
```json
{
    "is_valid": true,
    "section_name": "Your Role",
    "severity": "info",
    "errors": [],
    "warnings": [],
    "info": ["Consider including these keywords: expertise"],
    "suggestions": [
        "Consider specifying clear responsibilities or objectives for this role."
    ],
    "unreplaced_variables": [],
    "missing_keywords": [],
    "word_count": 15,
    "min_words": 20,
    "completion_percentage": 75.0,
    "help_text": "Define the AI persona and responsibilities.",
    "examples": ["You are an experienced backend developer..."]
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `is_valid` | boolean | Overall validation status |
| `severity` | string | Highest severity level: `critical`, `warning`, `info` |
| `errors` | array | Critical issues that must be fixed |
| `warnings` | array | Non-critical issues |
| `info` | array | Informational messages |
| `suggestions` | array | Improvement suggestions |
| `unreplaced_variables` | array | Variables not yet replaced |
| `missing_keywords` | array | Required keywords not found |
| `word_count` | integer | Current word count |
| `min_words` | integer | Minimum required words |
| `completion_percentage` | float | Section completion (0-100) |
| `help_text` | string | Contextual help for section |
| `examples` | array | Example content |

**Status Codes:**
| Code | Description |
|------|-------------|
| 200 | Validation completed |
| 400 | Invalid JSON |
| 404 | Template not found |
| 405 | Method not allowed |

---

#### GET /generate-document/{template_id}/guidance/{section_name}/

Get contextual guidance for a specific section.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `template_id` | integer | Template ID |
| `section_name` | string | Section name (URL encoded) |

**Response:**
```json
{
    "section_name": "Your Role",
    "help_text": "Define the AI persona and primary responsibilities.",
    "min_words": 20,
    "max_words": null,
    "required": true,
    "examples": [
        "Act as an elite system architect who transforms requirements..."
    ],
    "keywords_required": ["architect", "design"],
    "keywords_recommended": ["blueprint", "technical", "specifications"],
    "input_type": "textarea",
    "structured_fields": [],
    "placeholder": "",
    "validation_severity": "critical"
}
```

**Status Codes:**
| Code | Description |
|------|-------------|
| 200 | Success |
| 404 | Template not found |
| 405 | Method not allowed |

---

#### POST /generate-document/{template_id}/validate-variable/

Validate a single variable value against its metadata rules.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `template_id` | integer | Template ID |

**Request Body:**
```json
{
    "variable_name": "PROJECT_NAME",
    "value": "MyProject"
}
```

**Response:**
```json
{
    "variable_name": "PROJECT_NAME",
    "is_valid": true,
    "errors": [],
    "metadata": {
        "description": "The name of the project",
        "required": true,
        "help_text": "Use alphanumeric characters only"
    }
}
```

**Validation Error Response:**
```json
{
    "variable_name": "PROJECT_NAME",
    "is_valid": false,
    "errors": [
        "Variable 'PROJECT_NAME' does not match required format."
    ],
    "metadata": {
        "description": "The name of the project",
        "required": true,
        "help_text": "Use alphanumeric characters only"
    }
}
```

**Status Codes:**
| Code | Description |
|------|-------------|
| 200 | Validation completed |
| 400 | Invalid JSON or missing variable_name |
| 404 | Template not found |
| 405 | Method not allowed |

---

#### POST /generate-document/{template_id}/completion-status/

Get overall wizard completion status and per-step status.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `template_id` | integer | Template ID |

**Request Body:**
```json
{
    "section_data": {
        "Your Role": "You are an experienced developer...",
        "Input": "Build a user authentication system..."
    },
    "variable_data": {
        "PROJECT_NAME": "AuthSystem",
        "FRAMEWORK": "Django"
    }
}
```

**Response:**
```json
{
    "overall_completion": 75.5,
    "completed_steps": 2,
    "total_steps": 3,
    "total_errors": 0,
    "total_warnings": 1,
    "is_ready_to_generate": true,
    "step_statuses": [
        {
            "step_number": 1,
            "section_name": "Your Role",
            "status": "completed",
            "completion_percentage": 100.0,
            "has_errors": false,
            "has_warnings": false,
            "error_count": 0,
            "warning_count": 0
        },
        {
            "step_number": 2,
            "section_name": "Input",
            "status": "has_warnings",
            "completion_percentage": 85.0,
            "has_errors": false,
            "has_warnings": true,
            "error_count": 0,
            "warning_count": 1
        },
        {
            "step_number": 3,
            "section_name": "Output Requirements",
            "status": "not_started",
            "completion_percentage": 0.0,
            "has_errors": false,
            "has_warnings": false,
            "error_count": 0,
            "warning_count": 0
        }
    ],
    "variable_errors": []
}
```

**Step Status Values:**
| Status | Description |
|--------|-------------|
| `not_started` | Section has no content |
| `in_progress` | Section has content but incomplete |
| `completed` | Section meets all requirements |
| `has_errors` | Section has critical validation errors |
| `has_warnings` | Section has non-critical warnings |

**Status Codes:**
| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Invalid JSON |
| 404 | Template not found |
| 405 | Method not allowed |

---

#### GET /generate-document/{template_id}/steps/

Get enhanced wizard steps with full metadata.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `template_id` | integer | Template ID |

**Response:**
```json
{
    "steps": [
        {
            "step_number": 1,
            "section_name": "Your Role",
            "section_level": 2,
            "description": "",
            "variables": ["PROJECT_NAME"],
            "questions": [],
            "original_content": "## Your Role\nYou are...",
            "metadata": {
                "required": true,
                "min_words": 20,
                "max_words": null,
                "input_type": "textarea",
                "validation_severity": "critical",
                "keywords_required": ["architect", "design"],
                "keywords_recommended": ["blueprint", "technical"]
            },
            "guidance": {
                "section_name": "Your Role",
                "help_text": "Define the AI persona...",
                "min_words": 20,
                "examples": ["Act as an elite system architect..."]
            },
            "variable_metadata": {
                "PROJECT_NAME": {
                    "description": "The project name",
                    "required": true,
                    "input_type": "text",
                    "options": [],
                    "help_text": "Enter the project name",
                    "placeholder": "Enter value for PROJECT_NAME",
                    "validation_pattern": "^[A-Za-z][A-Za-z0-9_-]*$"
                }
            }
        }
    ],
    "total_steps": 3
}
```

**Status Codes:**
| Code | Description |
|------|-------------|
| 200 | Success |
| 404 | Template not found |
| 405 | Method not allowed |

---

### GitHub Sync

#### GET /sync/

Display GitHub sync status and options.

**Response:** HTML page with sync interface

---

#### POST /sync/manual/

Trigger manual template synchronization from GitHub.

**Response:** Redirect to template list with sync results

---

## Error Responses

### Standard Error Format

```json
{
    "error": "Error message description"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 403 | Forbidden - CSRF token missing or invalid |
| 404 | Not Found - Resource doesn't exist |
| 405 | Method Not Allowed - Wrong HTTP method |
| 500 | Internal Server Error - Server-side error |

---

## Rate Limiting

Currently, no rate limiting is enforced on API endpoints. For production deployments, consider implementing rate limiting:

```python
# Example using django-ratelimit
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/h', method='POST')
def validate_section_realtime(request, template_id):
    ...
```

---

## Webhooks (Future)

Webhook support for the following events is planned:

| Event | Description |
|-------|-------------|
| `template.synced` | Templates synchronized from GitHub |
| `prompt.generated` | New prompt generated |
| `validation.failed` | Prompt validation failed |

---

## SDK Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

class BMADForgeClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()

    def get_templates(self, role=None, phase=None):
        """Fetch templates with optional filters."""
        params = {}
        if role:
            params['role'] = role
        if phase:
            params['phase'] = phase
        response = self.session.get(f"{self.base_url}/templates/", params=params)
        return response

    def validate_section(self, template_id, section_name, content):
        """Validate section content in real-time."""
        response = self.session.post(
            f"{self.base_url}/generate-document/{template_id}/validate/",
            json={
                "section_name": section_name,
                "content": content
            }
        )
        return response.json()

    def get_section_guidance(self, template_id, section_name):
        """Get guidance for a section."""
        response = self.session.get(
            f"{self.base_url}/generate-document/{template_id}/guidance/{section_name}/"
        )
        return response.json()

    def validate_variable(self, template_id, variable_name, value):
        """Validate a variable value."""
        response = self.session.post(
            f"{self.base_url}/generate-document/{template_id}/validate-variable/",
            json={
                "variable_name": variable_name,
                "value": value
            }
        )
        return response.json()

    def get_completion_status(self, template_id, section_data, variable_data):
        """Get wizard completion status."""
        response = self.session.post(
            f"{self.base_url}/generate-document/{template_id}/completion-status/",
            json={
                "section_data": section_data,
                "variable_data": variable_data
            }
        )
        return response.json()

# Usage
client = BMADForgeClient()

# Validate a section
result = client.validate_section(
    template_id=1,
    section_name="Your Role",
    content="You are an experienced developer..."
)
print(f"Valid: {result['is_valid']}, Word count: {result['word_count']}")

# Get guidance
guidance = client.get_section_guidance(1, "Your Role")
print(f"Help: {guidance['help_text']}")
```

### JavaScript

```javascript
class BMADForgeClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }

    async validateSection(templateId, sectionName, content) {
        const response = await fetch(
            `${this.baseUrl}/generate-document/${templateId}/validate/`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    section_name: sectionName,
                    content: content
                })
            }
        );
        return response.json();
    }

    async getSectionGuidance(templateId, sectionName) {
        const response = await fetch(
            `${this.baseUrl}/generate-document/${templateId}/guidance/${encodeURIComponent(sectionName)}/`
        );
        return response.json();
    }

    async validateVariable(templateId, variableName, value) {
        const response = await fetch(
            `${this.baseUrl}/generate-document/${templateId}/validate-variable/`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    variable_name: variableName,
                    value: value
                })
            }
        );
        return response.json();
    }

    async getCompletionStatus(templateId, sectionData, variableData) {
        const response = await fetch(
            `${this.baseUrl}/generate-document/${templateId}/completion-status/`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    section_data: sectionData,
                    variable_data: variableData
                })
            }
        );
        return response.json();
    }

    getCsrfToken() {
        const cookie = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }
}

// Usage
const client = new BMADForgeClient();

// Validate section
const result = await client.validateSection(1, 'Your Role', 'You are an expert...');
console.log(`Valid: ${result.is_valid}, Completion: ${result.completion_percentage}%`);

// Get guidance
const guidance = await client.getSectionGuidance(1, 'Your Role');
console.log(`Min words: ${guidance.min_words}`);
```

### cURL

```bash
# Health check
curl -s http://localhost:8000/health/ | jq .

# Validate section
curl -X POST http://localhost:8000/generate-document/1/validate/ \
    -H "Content-Type: application/json" \
    -d '{"section_name": "Your Role", "content": "You are a developer..."}' | jq .

# Get section guidance
curl -s "http://localhost:8000/generate-document/1/guidance/Your%20Role/" | jq .

# Validate variable
curl -X POST http://localhost:8000/generate-document/1/validate-variable/ \
    -H "Content-Type: application/json" \
    -d '{"variable_name": "PROJECT_NAME", "value": "MyProject"}' | jq .

# Get completion status
curl -X POST http://localhost:8000/generate-document/1/completion-status/ \
    -H "Content-Type: application/json" \
    -d '{
        "section_data": {"Your Role": "Content here..."},
        "variable_data": {"PROJECT_NAME": "Test"}
    }' | jq .

# Get wizard steps
curl -s http://localhost:8000/generate-document/1/steps/ | jq .
```

---

## API Versioning

Currently, the API is unversioned. Future versions will use URL path versioning:

```
/api/v1/templates/
/api/v2/templates/
```

---

## Changelog

### Version 1.3.0

- Added enhanced validation API with metadata support
- Added `/guidance/` endpoint for section help
- Added `/validate-variable/` endpoint for variable validation
- Added `/completion-status/` endpoint for progress tracking
- Added `/steps/` endpoint for enhanced wizard steps
- Enhanced validation responses with severity levels and suggestions

### Version 1.2.0

- Added real-time section validation endpoint
- Added document generation wizard

### Version 1.1.0

- Added prompt history endpoints
- Added download functionality

### Version 1.0.0

- Initial API release
- Template browsing and filtering
- Basic prompt generation

---

## Support

For API support and bug reports:

- **GitHub Issues:** https://github.com/example/bmad-forge/issues
- **Email:** api-support@example.com

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-29 | Development Team | Initial document |
