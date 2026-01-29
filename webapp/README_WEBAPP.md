# BMAD Forge Web Application

A Django-based web application for prompt engineering using the BMAD (Breakthrough Method for Agile AI-Driven Development) Framework. This application enables teams to generate, validate, and manage BMAD-compliant prompts for AI coding assistants.

## Overview

BMAD Forge is built according to the specifications in [BMAD_PRD.md](../BMAD_PRD.md) and provides a comprehensive platform for:

- **Template Management**: Browse and filter BMAD templates by agent role and workflow phase
- **Generate Document**: Interactive wizard for section-by-section document creation with real-time validation
- **Dynamic Forms**: Auto-generated forms based on template variables
- **Prompt Generation**: Generate BMAD-compliant prompts with variable substitution
- **BMAD Validation**: Validate generated prompts against framework requirements with 100% detection rate
- **Real-time Validation**: Immediate feedback during document generation
- **GitHub Sync**: Import templates from remote GitHub repositories
- **History Management**: Track and review previously generated prompts
- **Export Options**: Copy to clipboard or download prompts as text files

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Git

### Installation

1. Navigate to the webapp directory:
```bash
cd webapp
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables (optional):
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run database migrations:
```bash
python manage.py migrate
```

6. Load initial templates:
```bash
python load_local_templates.py
```

7. Start the development server:
```bash
python manage.py runserver
```

8. Open your browser and navigate to:
```
http://localhost:8000
```

## Features

### BMAD Framework Support

The application supports all standard BMAD agent roles and workflow phases:

#### Agent Roles
- **Orchestrator**: Coordination and oversight
- **Analyst**: Requirements and data analysis
- **Project Manager**: Planning and tracking
- **Architect**: System design and architecture
- **Scrum Master**: Agile process facilitation
- **Developer**: Implementation and coding
- **QA Engineer**: Testing and quality assurance

#### Workflow Phases
- **Planning Phase**: Requirements, analysis, planning
- **Development Phase**: Implementation, testing, deployment

### Template Management

The template library provides:
- Card-based grid layout with responsive design
- **Agent Role Filtering**: Filter templates by BMAD agent role (supports multi-role templates)
- **Workflow Phase Filtering**: Filter templates by planning or development phase
- **Combined Filtering**: Use both filters together to narrow down results
- Full-text search across titles, descriptions, and content
- Template detail views with metadata
- Variable detection and display

### Prompt Generation

Dynamic form generation includes:
- Automatic field generation based on template variables
- Smart field types (text input vs textarea)
- Real-time validation
- Template preview
- Variable substitution

### Generate Document (Interactive Wizard)

The Generate Document feature provides step-by-step document creation:
- **Section-by-section editing**: Fill in each template section individually
- **Real-time validation**: Immediate feedback as you type
- **Progress tracking**: Visual progress indicator showing completed/remaining steps
- **Variable management**: Fill in required variables with validation
- **Content suggestions**: Rule-based suggestions for improving content based on section type
- **Filtering support**: Filter templates by agent role and workflow phase when selecting

### BMAD Validation

Generated prompts are validated for:
- Required sections (Your Role, Input, Output Requirements) - **100% detection rate**
- Complete variable substitution - **100% detection rate**
- Content structure and quality
- Compliance scoring

**Validation Targets:**
- 95%+ compliance rate for prompts generated through the platform
- < 5% false positive rate for validation warnings

## Configuration

### Configuration File (config.yaml)

BMAD Forge uses a `config.yaml` file for easy configuration. Edit this file to customize application settings without modifying code.

```yaml
# BMAD Forge Configuration File
application:
  version: "1.1.0"
  name: "BMAD Forge"

templates:
  # Local templates directory (relative to webapp folder)
  local_path: "forge/templates/agents"
  
  # GitHub repository settings for template synchronization
  github:
    repository: "DXCSithlordPadawan/BMAD_Forge"
    branch: "main"
    remote_path: "webapp/forge/templates"
  
  # Template sync behavior
  sync:
    overwrite_existing: true  # Overwrite existing templates during sync
    match_by: "title"         # Match templates by title (alternative: remote_path)
```

**Key Features:**
- **Easy to Edit**: Simple YAML format for configuration changes
- **Version Control**: Track application version in config file
- **Template Locations**: Configure where templates are stored and synced from
- **Sync Behavior**: Control how template synchronization handles existing templates
- **Recursive Search**: Template sync recursively searches configured folder and all subfolders

### Environment Variables

Environment variables can override config.yaml settings:

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `True` |
| `SECRET_KEY` | Django secret key | Auto-generated |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `GITHUB_TOKEN` | GitHub personal access token | (empty) |
| `APP_VERSION` | Override application version | config.yaml value |
| `APP_NAME` | Override application name | config.yaml value |
| `TEMPLATE_REPO` | Override GitHub repository | config.yaml value |

### Database Configuration

For MVP, BMAD Forge uses SQLite by default (no configuration needed). For production, configure PostgreSQL in your `.env` file or `settings.py`.

## Project Structure

```
webapp/
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── config.yaml           # Application configuration file
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore patterns
├── README.md             # Quick start guide
├── README_WEBAPP.md      # This file
├── load_local_templates.py  # Script to load templates
├── bmad_forge/           # Project configuration
│   ├── config.py        # Configuration loader
│   ├── settings.py       # Django settings
│   ├── urls.py          # Root URL configuration
│   └── wsgi.py          # WSGI application
├── forge/               # Main application
│   ├── models.py        # Database models
│   ├── views.py         # View functions
│   ├── forms.py         # Form classes
│   ├── urls.py          # URL routing
│   ├── admin.py         # Admin configuration
│   ├── services/        # Business logic
│   │   ├── github_sync.py
│   │   ├── template_parser.py
│   │   ├── document_generator.py
│   │   └── bmad_validator.py
│   ├── templates/       # HTML templates and prompt templates
│   │   ├── forge/       # Django HTML templates (UI)
│   │   ├── agents/      # BMAD prompt templates (15 core templates)
│   │   └── templates/   # Extended document templates (PRD, roadmap, etc.)
│   └── static/          # CSS and JavaScript
└── tests/               # Test suite
    ├── test_models.py
    ├── test_views.py
    ├── test_services.py
    ├── test_config.py   # Configuration tests
    └── test_template_simulation.py  # Template simulation tests
```

## Included Templates

### Core Agent Templates (15 Templates)

Located in `forge/templates/agents/`:

#### Agent Role Templates
| Template | Agent Role | Description |
|----------|------------|-------------|
| `architect_prompt.md` | Architect | System architecture design and technical blueprints |
| `backend_prompt.md` | Developer | Senior backend engineer for server-side implementation |
| `frontend_prompt.md` | Developer | Senior frontend engineer for UI implementation |
| `devops_prompt.md` | Developer | DevOps & deployment engineer for infrastructure and CI/CD |
| `productmanager_prompt.md` | Project Manager | Product planning and requirements documentation |
| `qa_prompt.md` | QA Engineer | Test automation and quality assurance strategies |
| `security_prompt.md` | Analyst | Security vulnerability assessment and compliance |
| `uxdesigner_prompt.md` | Designer | UX design and user experience optimization |

#### Workflow Templates
| Template | Phase | Description |
|----------|-------|-------------|
| `phase1.md` | Planning | Architecture brainstorm and initial planning |
| `phase2.md` | Development | Phase 2 development workflow |
| `phase3.md` | Development | Phase 3 development workflow |
| `generate_epics.md` | Planning | Epic and story generator from PRDs |
| `prd_generate_epic_prompt.md` | Planning | PRD-based epic generation |

#### Utility Templates
| Template | Purpose |
|----------|---------|
| `selfdocagent_prompt.md` | Self-documentation agent for code documentation |
| `selfdocslashcommand_prompt.md` | Self-documenting slash command integration |

### Extended Document Templates

Located in `forge/templates/templates/` - Additional document templates for product management:

| Template | Description |
|----------|-------------|
| `PRD_template.md` | Product Requirements Document template |
| `ProductRoadmap_template.md` | Product roadmap planning template |
| `ProductStrategy_template.md` | Product strategy documentation |
| `ProductBacklog_template.md` | Product backlog organization |
| `FeatureRequestDocument_template.md` | Feature request documentation |
| `MVPFeatureList_template.md` | MVP feature list planning |
| `ReleasePlan_template.md` | Release planning template |
| `UserStoryMapping_template.md` | User story mapping template |
| `CustomerJourneyMap_template.md` | Customer journey mapping |
| `DesignSpec_template.md` | Design specification template |
| `UsabilityTestPlan_template.md` | Usability testing plan |
| `APIDocumentation_template.md` | API documentation template |
| `KPIDashboard_template.md` | KPI dashboard template |
| `ProductSecurityAssessment_template.md` | Security assessment template |
| `technicaldesigndocument_template.md` | Technical design document |

## Usage

### Creating a Prompt

1. Browse the template library from the dashboard
2. Select a template matching your needs
3. Fill in the dynamic form with required values
4. Click "Generate Prompt"
5. Review the generated prompt and validation results
6. Copy to clipboard or download the result

### Template Format

BMAD Forge templates use the following variable syntax:
- `{{VARIABLE_NAME}}` - Double brace syntax
- `[VARIABLE_NAME]` - Single bracket syntax

Example template:
```markdown
## Your Role
You are an experienced {{agent_role}} specializing in {{domain}}.

## Input
{{project_description}}

## Output Requirements
Provide a comprehensive {{deliverable}} that includes:
1. Key objectives
2. Implementation approach
3. Timeline
```

## Development

### Running Tests

```bash
pytest
```

Or with coverage:
```bash
pytest --cov=forge
```

### Creating Migrations

After modifying models:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Management Commands

Sync templates from GitHub:
```bash
python manage.py sync_templates --owner owner --repo repo --path path
```

## Deployment

### Production Checklist

1. Set `DEBUG=False` in environment
2. Generate a strong `SECRET_KEY`
3. Configure a production database (PostgreSQL recommended)
4. Set up static file serving
5. Configure allowed hosts
6. Set up HTTPS/SSL certificate
7. Configure GitHub token for private repositories

### Docker Deployment (Optional)

A Dockerfile can be created for containerized deployment. The application is designed to work with standard Django deployment practices.

## Technology Stack

- **Backend**: Django 5.x, Python 3.11+
- **Frontend**: Bootstrap 5, vanilla JavaScript
- **Database**: SQLite (development), PostgreSQL (production)
- **External Services**: GitHub API (for template synchronization)

## License

This project is part of the BMAD Framework ecosystem.

## Acknowledgments

- [BMAD Framework](https://github.com/bmadcode/BMAD-METHOD-v5) for the methodology
- [Django](https://www.djangoproject.com/) for the web framework
- [Bootstrap 5](https://getbootstrap.com/) for the UI components

## Support

For issues, questions, or contributions, please refer to the main repository documentation.
