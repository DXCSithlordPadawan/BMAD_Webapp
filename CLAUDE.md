# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BMAD Forge is a Django-based web application for prompt engineering using the BMAD (Breakthrough Method for Agile AI-Driven Development) Framework. It enables teams to generate, validate, and manage BMAD-compliant prompts for AI coding assistants.

**Version:** 1.3.0
**Stack:** Django 5.x, Python 3.11+, Bootstrap 5, SQLite (dev) / PostgreSQL (prod)

## Development Commands

All commands run from the `webapp/` directory:

```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python load_local_templates.py

# Run development server
python manage.py runserver

# Database
python manage.py makemigrations    # After model changes
python manage.py migrate

# Tests (pytest configured in pytest.ini)
pytest                             # Run all tests
pytest -v                          # Verbose output
pytest --cov=forge                 # With coverage
pytest tests/test_services.py      # Specific file
pytest tests/test_services.py::test_template_sync  # Specific test

# Template sync from GitHub
python manage.py sync_templates --owner owner --repo repo --path path
```

## Architecture

### Core Structure

```
webapp/
├── bmad_forge/           # Django project config
│   ├── config.py         # ConfigLoader (YAML + env overrides)
│   └── settings.py       # Django settings
├── forge/                # Main application
│   ├── models.py         # Template, GeneratedPrompt models
│   ├── views.py          # Class-based views + validation API endpoints
│   ├── urls.py           # URL routing including API endpoints
│   ├── forms.py          # Dynamic forms for template variables
│   ├── services/         # Business logic layer
│   │   ├── github_sync.py       # GitHub API integration
│   │   ├── bmad_validator.py    # BMAD compliance + metadata-aware validation
│   │   ├── document_generator.py # Section-by-section wizard + completion tracking
│   │   └── template_parser.py   # Variable/section metadata extraction
│   └── templates/
│       ├── forge/        # Django HTML templates
│       ├── agents/       # BMAD agent prompt templates (15 core)
│       └── templates/    # BMAD document templates (15 core)
└── tests/                # Pytest test suite
```

### Configuration System

`config.yaml` in webapp/ provides app configuration. Environment variables override YAML values.

```python
# Access config values via dot notation
from bmad_forge.config import ConfigLoader
version = ConfigLoader.get('application.version')
repo = ConfigLoader.get('templates.github.repository')
```

Key env vars: `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, `GITHUB_TOKEN`, `DATABASE_URL`

### Template Variable Syntax

Templates use two syntaxes for placeholders:
- Double brace: `{{VARIABLE_NAME}}`
- Single bracket: `[VARIABLE_NAME]`

Variables are auto-extracted via regex on model save and stored in the `variables` JSONField.

### Enhanced Frontmatter Schema

Templates support YAML frontmatter with `sections` and `variables` blocks for guided validation:

```yaml
---
name: template-name
description: Template description
role: developer
workflow_phase: development
sections:
  "Your Role":
    required: true
    min_words: 20
    input_type: textarea
    help_text: "Define the AI persona and responsibilities"
    keywords_required: ["responsibility", "expertise"]
    validation_severity: critical  # critical|warning|info
    examples: ["You are an experienced backend developer..."]
variables:
  PROJECT_NAME:
    description: "The project name"
    required: true
    type: text  # text|textarea|select|multiselect|number|date|checkbox
    validation: "^[A-Za-z][A-Za-z0-9_-]*$"
    options: []  # For select/multiselect types
    depends_on: []  # Variable dependencies
---
```

### Data Models

**Template:** Stores BMAD prompt templates with auto-extracted variables, agent roles (JSONField for multi-role), workflow phase (planning/development), GitHub source tracking.

**GeneratedPrompt:** User-generated prompts with input_data, validation status, missing_variables tracking. ForeignKey to Template.

### Service Layer Pattern

Business logic is isolated in `forge/services/`:

**GitHubSyncService** (`github_sync.py`):
- Recursive GitHub repo traversal
- YAML/TOML frontmatter parsing
- Rate limiting and error handling

**BMADValidator** (`bmad_validator.py`):
- Required section detection (## Your Role, ## Input, ## Output Requirements)
- Unreplaced variable detection
- `MetadataAwareValidator` class for enhanced validation with severity levels

**DocumentGenerator** (`document_generator.py`):
- Interactive wizard with session persistence
- `EnhancedRealTimeValidation` with severity levels (critical/warning/info)
- `WizardStepStatus` tracking (completed/in_progress/pending/blocked)
- `calculate_completion_status()` for progress tracking
- Keyword validation (required/recommended)

**TemplateParser** (`template_parser.py`):
- `SectionMetadata` and `VariableMetadata` dataclasses
- `ValidationSeverity` enum (CRITICAL, WARNING, INFO)
- `InputType` enum (TEXT, TEXTAREA, SELECT, MULTISELECT, STRUCTURED)
- `parse_frontmatter()` - Extract YAML frontmatter
- `parse_section_metadata()` - Parse section validation rules
- `parse_variable_metadata()` - Parse variable validation rules
- `get_section_metadata_with_defaults()` - Backward compatibility
- `validate_section_against_metadata()` - Content validation
- `validate_variable_value()` - Variable validation

### API Endpoints

**Document Generation Wizard API** (prefix: `/generate-document/<id>/`):

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/guidance/<section>/` | Get section metadata, help text, examples, keywords |
| POST | `/validate-variable/` | Validate single variable against metadata rules |
| POST | `/completion-status/` | Get overall completion percentage and blocking issues |
| GET | `/steps/` | Get all wizard steps with metadata and status |
| POST | `/validate/` | Real-time section validation |

**Standard API** (see `docs/API_GUIDE.md` for complete reference):

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/templates/` | List templates with filtering |
| GET | `/api/templates/<id>/` | Get template details |
| POST | `/api/prompts/generate/` | Generate prompt from template |
| GET | `/api/prompts/` | List generated prompts |
| POST | `/api/sync/` | Trigger GitHub sync |

### BMAD Framework

**Agent Roles:** orchestrator, analyst, pm, architect, scrum_master, developer, qa

**Workflow Phases:** planning, development

**Validation Severity Levels:**
- `critical` - Must be resolved before generation (missing required sections, unreplaced variables)
- `warning` - Should be addressed but doesn't block (short content, missing recommended keywords)
- `info` - Suggestions for improvement

## Key Documentation

### Core Documentation
- `BMAD_PRD.md` - Complete product requirements document
- `docs/ARCHITECTURE.md` - System architecture with Mermaid diagrams
- `docs/API_GUIDE.md` - Complete API reference
- `docs/SECURITY_GUIDE.md` - Security implementation and compliance mappings
- `docs/PRODUCTION_READINESS.md` - Deployment guide
- `docs/USER_GUIDE.md` - End-user documentation

### Operations Documentation
- `docs/MAINTENANCE_GUIDE.md` - System maintenance procedures
- `docs/SUPPORT_TASKS.md` - Support runbooks and escalation
- `docs/CONTAINER_BUILD_GUIDE.md` - Docker and Kubernetes deployment

### Compliance Documentation
- `docs/compliance/CIS_BENCHMARK_L2.md` - CIS security controls mapping
- `docs/compliance/DISA_STIG.md` - DISA security requirements
- `docs/compliance/FIPS_140_3.md` - Cryptographic compliance
- `docs/compliance/PEP_STANDARDS.md` - Python enhancement proposals compliance

## Testing

Test classes in `webapp/tests/test_services.py`:

- `TestSectionMetadata` - Section metadata parsing and defaults
- `TestVariableMetadata` - Variable metadata parsing and validation
- `TestSectionValidation` - Content validation against metadata rules
- `TestEnhancedDocumentGenerator` - Wizard steps and completion tracking
- `TestMetadataAwareValidator` - Full validation with severity levels
- `TestLegacyTemplateCompatibility` - Backward compatibility for templates without metadata

Run tests:
```bash
cd webapp
pytest tests/test_services.py -v
pytest tests/test_services.py::TestSectionMetadata -v  # Specific class
```

## Key Implementation Files

When modifying the validation system, these are the critical files:

1. **`forge/services/template_parser.py`** - Metadata dataclasses and parsing
2. **`forge/services/document_generator.py`** - Wizard logic and real-time validation
3. **`forge/services/bmad_validator.py`** - BMAD compliance and metadata-aware validation
4. **`forge/views.py`** - API endpoints for validation
5. **`forge/urls.py`** - URL routing for API endpoints
6. **`forge/templates/forge/generate_document_wizard.html`** - Wizard UI with completion tracker
