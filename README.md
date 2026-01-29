# BMAD_Forge

A Django-based web application called "BMAD Forge" that serves as a prompt engineering tool for generating BMAD (Breakthrough Method for Agile AI-Driven Development) Framework-compliant prompts.

## 🚀 Quick Start

The web application is located in the `webapp/` directory. To get started:

```bash
cd webapp
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python load_local_templates.py
python manage.py runserver
```

Then visit http://localhost:8000

📖 **For complete documentation, see [webapp/README_WEBAPP.md](webapp/README_WEBAPP.md)**

## 📋 Product Requirements

This application implements the specifications defined in [BMAD_PRD.md](BMAD_PRD.md).

## ✨ Features

### Core Functionality
- **Dashboard** - Overview with statistics and quick actions
- **Template Library** - Browse and filter 15+ BMAD templates by agent role and workflow phase
- **Generate Document** - Interactive wizard for section-by-section document creation with real-time validation
- **Dynamic Forms** - Auto-generated input forms based on template variables
- **Prompt Generation** - Variable substitution with validation
- **BMAD Compliance** - Automated validation for required sections with 100% detection rate
- **Real-time Validation** - Immediate feedback during prompt generation
- **History Management** - Track and review generated prompts
- **GitHub Sync** - Import templates from remote repositories (recursive folder search)
- **Config File** - Easy-to-edit YAML configuration for version and template settings

### Validation Capabilities
- **100% Detection Rate** for missing required sections (## Your Role, ## Input, ## Output Requirements)
- **100% Detection Rate** for unreplaced template variables ({{var}} or [var] syntax)
- **< 5% False Positive Rate** for validation warnings
- **95%+ Compliance Rate** target for prompts generated through the platform

### Supported BMAD Elements

**Agent Roles:**
- Orchestrator - Coordination and oversight
- Analyst - Requirements and data analysis  
- Project Manager - Planning and tracking
- Architect - System design and architecture
- Scrum Master - Agile process facilitation
- Developer - Implementation and coding
- QA Engineer - Testing and quality assurance

**Workflow Phases:**
- Planning Phase - Requirements, analysis, estimation
- Development Phase - Implementation, testing, deployment

### Included Templates (15 Core Templates + 15 Extended Templates)

The webapp includes BMAD-compliant prompt templates located in `webapp/forge/templates/`:

#### Core Agent Templates (`agents/`)
| Template | Description |
|----------|-------------|
| `architect_prompt.md` | System architect for technical blueprints and architecture design |
| `backend_prompt.md` | Senior backend engineer for server-side implementation |
| `frontend_prompt.md` | Senior frontend engineer for UI implementation |
| `devops_prompt.md` | DevOps & deployment engineer for infrastructure and CI/CD |
| `productmanager_prompt.md` | Product manager for requirements and product planning |
| `qa_prompt.md` | QA & test automation engineer for testing strategies |
| `security_prompt.md` | Security analyst for vulnerability assessment |
| `uxdesigner_prompt.md` | UX designer for user experience and design |
| `generate_epics.md` | Epic and story generator from PRDs |
| `prd_generate_epic_prompt.md` | PRD-based epic generation |
| `phase1.md` | Architecture brainstorm agent (Phase 1 planning) |
| `phase2.md` | Phase 2 development workflow |
| `phase3.md` | Phase 3 development workflow |
| `selfdocagent_prompt.md` | Self-documentation agent |
| `selfdocslashcommand_prompt.md` | Self-documenting slash command agent |

#### Extended Document Templates (`templates/`)
Additional templates for product management including PRD, roadmap, backlog, and design specification templates.

## 🏗️ Architecture

### Technical Stack
- **Backend**: Django 5.x, Python 3.11+
- **Frontend**: Bootstrap 5, vanilla JavaScript
- **Database**: SQLite (development), PostgreSQL (production)
- **External Services**: GitHub API for template synchronization

### Project Structure
```
BMAD_Forge/
├── BMAD_PRD.md           # Product requirements document
├── README.md             # This file
└── webapp/              # Production web application ⭐
    ├── README.md         # Quick start guide
    ├── README_WEBAPP.md  # Detailed setup guide
    ├── config.yaml       # Application configuration ⭐
    ├── manage.py
    ├── requirements.txt
    ├── bmad_forge/      # Django project config
    │   └── config.py    # Configuration loader
    ├── forge/           # Main application
    │   ├── templates/
    │   │   ├── forge/   # Django HTML templates
    │   │   └── agents/  # 15 BMAD prompt templates ⭐
    │   └── services/    # Business logic
    └── tests/           # Test suite (includes config tests)
```

## 📚 Documentation

- **[docs/USER_GUIDE.md](docs/USER_GUIDE.md)** - Comprehensive user guide for all features
- **[webapp/README_WEBAPP.md](webapp/README_WEBAPP.md)** - Complete setup and usage guide
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technical architecture documentation
- **[BMAD_PRD.md](BMAD_PRD.md)** - Detailed product requirements
- **[BMAD Framework](https://github.com/bmadcode/BMAD-METHOD-v5)** - Framework methodology

## 🎯 Use Cases

1. **Generate BMAD-Compliant Prompts** - Create structured prompts for AI coding assistants
2. **Generate Documents** - Use the interactive wizard to create documents section-by-section with real-time validation
3. **Template Management** - Organize and maintain reusable prompt templates
4. **Team Standardization** - Ensure consistent prompt quality across development teams
5. **GitHub Integration** - Sync templates from organizational repositories

## 🛠️ Development

### Prerequisites
- Python 3.11 or higher
- pip package manager
- Git

### Local Development Setup
```bash
cd webapp
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python load_local_templates.py
python manage.py runserver
```

### Running Tests
```bash
cd webapp
pytest
```

## 🚢 Deployment

The application supports standard Django deployment patterns:
- Docker containerization
- WSGI/ASGI server deployment
- PostgreSQL for production database
- Static file serving via CDN

See [webapp/README_WEBAPP.md](webapp/README_WEBAPP.md) for detailed deployment instructions.

## 📝 License

This project is part of the BMAD Framework ecosystem.

## 🙏 Acknowledgments

- [BMAD Framework](https://github.com/bmadcode/BMAD-METHOD-v5) for the methodology
- [Django](https://www.djangoproject.com/) for the web framework
- [Bootstrap 5](https://getbootstrap.com/) for UI components

---

**Status**: ✅ Web application fully functional and ready for use
