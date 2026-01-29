# BMAD Forge

A Django-based web application for prompt engineering using the BMAD (Breakthrough Method for Agile AI-Driven Development) Framework. Generate, validate, and manage BMAD-compliant prompts for AI coding assistants.

## Features

- **Template Library**: Browse and filter BMAD templates by agent role and workflow phase
- **Dynamic Forms**: Auto-generated forms based on template variables
- **Prompt Generation**: Generate BMAD-compliant prompts with variable substitution
- **BMAD Validation**: Validate generated prompts against framework requirements
- **GitHub Sync**: Import templates from remote GitHub repositories
- **History Management**: Track and review previously generated prompts
- **Export Options**: Copy to clipboard or download prompts as text files

## BMAD Framework Support

BMAD Forge supports all standard BMAD agent roles and workflow phases:

### Agent Roles
- **Orchestrator**: Coordination and oversight
- **Analyst**: Requirements and data analysis
- **Project Manager**: Planning and tracking
- **Architect**: System design and architecture
- **Scrum Master**: Agile process facilitation
- **Developer**: Implementation and coding
- **QA Engineer**: Testing and quality assurance

### Workflow Phases
- **Planning Phase**: Requirements, analysis, planning
- **Development Phase**: Implementation, testing, deployment

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip or uv package manager
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd bmad_forge
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

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run database migrations:
```bash
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

7. Open your browser and navigate to:
```
http://localhost:8000
```

### Syncing Templates

After starting the server, sync templates from GitHub:

1. Navigate to the Sync page (`/sync/`)
2. Enter the repository URL (or use the default from config.yaml)
3. Click "Sync Templates"

**Template Sync Behavior:**
- Templates are synced recursively from the configured folder and all subfolders
- When a template already exists (matched by title), it is overwritten ensuring only one version shows
- Configure sync behavior in `config.yaml` under `templates.sync`

Default repository: `DXCSithlordPadawan/BMAD_Forge` (path: `webapp/forge/templates`)

## Configuration

### Configuration File (config.yaml)

BMAD Forge uses a `config.yaml` file for easy configuration of application settings. This file is located in the `webapp/` directory.

```yaml
# BMAD Forge Configuration File
application:
  version: "1.1.0"
  name: "BMAD Forge"

templates:
  # Local templates directory
  local_path: "forge/templates/agents"
  
  # GitHub repository settings
  github:
    repository: "DXCSithlordPadawan/BMAD_Forge"
    branch: "main"
    remote_path: "webapp/forge/templates"
  
  # Sync behavior
  sync:
    overwrite_existing: true  # Overwrites existing templates during sync
    match_by: "title"         # Match templates by title (alternative: remote_path)
```

**Key Configuration Options:**

| Setting | Description | Default |
|---------|-------------|---------|
| `application.version` | Application version number | `1.0.0` |
| `application.name` | Application display name | `BMAD Forge` |
| `templates.local_path` | Local template directory path | `forge/templates/agents` |
| `templates.github.repository` | GitHub repo for templates | `DXCSithlordPadawan/BMAD_Forge` |
| `templates.github.branch` | Git branch to sync from | `main` |
| `templates.github.remote_path` | Path within repo for templates | `webapp/forge/templates` |
| `templates.sync.overwrite_existing` | Overwrite existing templates on sync | `true` |
| `templates.sync.match_by` | Field to match templates (`title` or `remote_path`) | `title` |

### Environment Variables

Environment variables override config.yaml settings when set:

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `True` |
| `SECRET_KEY` | Django secret key | Auto-generated |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `GITHUB_TOKEN` | GitHub personal access token | (empty) |
| `APP_VERSION` | Overrides config.yaml version | - |
| `APP_NAME` | Overrides config.yaml app name | - |
| `TEMPLATE_REPO` | Overrides config.yaml repository | - |

### Database Configuration

For MVP, BMAD Forge uses SQLite by default. For production, configure PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bmad_forge',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Project Structure

```
bmad_forge/
├── manage.py
├── requirements.txt
├── config.yaml               # Application configuration file
├── .env.example
├── README.md
├── bmad_forge/           # Project configuration
│   ├── config.py         # Configuration loader
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── forge/                # Main application
│   ├── models.py         # Database models
│   ├── views.py          # View functions
│   ├── forms.py          # Form classes
│   ├── urls.py           # URL routing
│   ├── admin.py          # Admin configuration
│   ├── services/         # Business logic
│   │   ├── github_sync.py
│   │   ├── template_parser.py
│   │   ├── document_generator.py
│   │   └── bmad_validator.py
│   ├── templates/        # HTML and prompt templates
│   │   ├── forge/        # Django HTML templates
│   │   └── agents/       # 15 BMAD prompt templates
│   └── static/           # CSS and JavaScript
└── tests/                # Test suite
    ├── test_models.py
    ├── test_views.py
    ├── test_services.py
    ├── test_config.py    # Configuration tests
    └── test_template_simulation.py
```

## Included Templates

### Core Agent Templates (`forge/templates/agents/`)
The application includes 15 BMAD-compliant prompt templates:

| Template | Description |
|----------|-------------|
| `architect_prompt.md` | System architect for technical blueprints |
| `backend_prompt.md` | Senior backend engineer for server-side implementation |
| `frontend_prompt.md` | Senior frontend engineer for UI implementation |
| `devops_prompt.md` | DevOps & deployment engineer for infrastructure |
| `productmanager_prompt.md` | Product manager for requirements |
| `qa_prompt.md` | QA & test automation engineer |
| `security_prompt.md` | Security analyst for vulnerability assessment |
| `uxdesigner_prompt.md` | UX designer for user experience |
| `generate_epics.md` | Epic and story generator from PRDs |
| `prd_generate_epic_prompt.md` | PRD-based epic generation |
| `phase1.md` | Architecture brainstorm (Phase 1) |
| `phase2.md` | Phase 2 development workflow |
| `phase3.md` | Phase 3 development workflow |
| `selfdocagent_prompt.md` | Self-documentation agent |
| `selfdocslashcommand_prompt.md` | Self-documenting slash command |

### Extended Document Templates (`forge/templates/templates/`)
Additional templates for product management (PRD, roadmap, backlog, design specs, etc.)

## Usage

### Creating a Prompt

1. Browse the template library
2. Select a template matching your needs
3. Fill in the dynamic form with required values
4. Click "Generate Prompt"
5. Review the generated prompt
6. Copy or download the result

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

### BMAD Compliance

Generated prompts are validated for:
- Required sections (Your Role, Input, Output Requirements)
- Complete variable substitution
- Meaningful content length
- Proper structure

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

### Example Production Settings

```python
import os

DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Acknowledgments

- [BMAD Framework](https://github.com/bmadcode/BMAD-METHOD-v5) for the methodology
- [Django](https://www.djangoproject.com/) for the web framework
- [Bootstrap 5](https://getbootstrap.com/) for the UI components
