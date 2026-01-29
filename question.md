## Role: As the designer of the application I wish to make improvements that comply with security constraints, document the application, define any APIs created or used
This is all to be done in planning mode.
## Objective 1:
Update all templates and agent files to allow seperation of each section so that interactive guided validation can be achieved through the application intereface to generate a new document based on the agent or template
By asking for confirmation of the details of each section, completing the document section by section to ensure it is completed fully and no elements have been omitted.
## Objective 2:
Examine all code and create a comprehensive set of documentation For Architecture (High Level and Low Level), Security Compliance (CIS Benchmark Level 2, DISA Stig, FIPS 140-3, PIP Standards), Maintenance Guide (Patching, Backup, etc), Support Tasks, User Guide,
Deployment Guide, Container Build Guide. All diagrams are to be in mermaid format all documents are to be in Markdown Format

## Inputs:
- [BMAD Framework](https://github.com/bmadcode/BMAD-METHOD-v5) for the methodology
- [Django](https://www.djangoproject.com/) for the web framework
- [Bootstrap 5](https://getbootstrap.com/) for the UI components
- [/media/odin/m2ssd/BMAD_Forge-main/docs] for documentation
- [/media/odin/m2ssd/BMAD_Forge-main/webapp] for code
- [/media/odin/m2ssd/BMAD_Forge-main] for BMAD_PRD.MD and README.MD

### Included Templates

#### Core Agent Templates (15 Templates)

Located in `forge/templates/agents/`:

##### Agent Role Templates
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

##### Workflow Templates
| Template | Phase | Description |
|----------|-------|-------------|
| `phase1.md` | Planning | Architecture brainstorm and initial planning |
| `phase2.md` | Development | Phase 2 development workflow |
| `phase3.md` | Development | Phase 3 development workflow |
| `generate_epics.md` | Planning | Epic and story generator from PRDs |
| `prd_generate_epic_prompt.md` | Planning | PRD-based epic generation |

##### Utility Templates
| Template | Purpose |
|----------|---------|
| `selfdocagent_prompt.md` | Self-documentation agent for code documentation |
| `selfdocslashcommand_prompt.md` | Self-documenting slash command integration |

#### Extended Document Templates

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


This application implements the specifications defined in [BMAD_PRD.md](BMAD_PRD.md).

## ✨ Features

### Core Functionality
- **Dashboard** - Overview with statistics and quick actions
- **Template Library** - Browse and filter 15+ BMAD templates by agent role and workflow phase
- **Generate Document** - Interactive wizard for section-by-section document creation with real-time validation
- **Dynamic Forms** - Auto-generated input forms based on template variables
- **Prompt Generation** - Generate BMAD-compliant prompts with variable substitution
- **BMAD Compliance** - Automated validation for required sections with 100% detection rate
- **Real-time Validation** - Immediate feedback during prompt generation
- **History Management** - Track and review generated prompts
- **GitHub Sync** - Import templates from remote repositories (recursive folder search)
- **Config File** - Easy-to-edit YAML configuration for version and template settings
- **Export Options**: Copy to clipboard or download prompts as markdown files

### Prompt Generation

Dynamic form generation includes:
- Automatic field generation based on template variables
- Smart field types (text input vs textarea)
- Real-time validation
- Template preview
- Variable substitution

### Generate Document (Interactive Wizard)

The Generate Document feature provides step-by-step document creation:
- **Section-by-section editing**: Fill in each template section individually, default value is the template example text
- **Real-time validation**: Immediate feedback as you type
- **Progress tracking**: Visual progress indicator showing completed/remaining steps
- **Variable management**: Fill in required variables with validation
- **Content suggestions**: Rule-based suggestions for improving content based on section type
- **Filtering support**: Filter templates by agent role and workflow phase when selecting

### BMAD Compliance

Generated prompts are validated for:
- Required sections (Your Role, Input, Output Requirements) - **100% detection rate**
- Complete variable substitution - **100% detection rate**
- Content structure and quality
- Compliance scoring

**Validation Targets:**
- 95%+ compliance rate for prompts generated through the platform
- < 5% false positive rate for validation warnings

## Outputs

### Amended Templates
Located in `forge/templates/agents/`:

##### Agent Role Templates
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

##### Workflow Templates
| Template | Phase | Description |
|----------|-------|-------------|
| `phase1.md` | Planning | Architecture brainstorm and initial planning |
| `phase2.md` | Development | Phase 2 development workflow |
| `phase3.md` | Development | Phase 3 development workflow |
| `generate_epics.md` | Planning | Epic and story generator from PRDs |
| `prd_generate_epic_prompt.md` | Planning | PRD-based epic generation |

##### Utility Templates
| Template | Purpose |
|----------|---------|
| `selfdocagent_prompt.md` | Self-documentation agent for code documentation |
| `selfdocslashcommand_prompt.md` | Self-documenting slash command integration |

#### Extended Document Templates

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

### Documentation
- ARCHITECTURE.md
- DEPENDENCY_ANALYSIS.md
- USER_GUIDE.md
- MAINTENANCE_GUIDE.md
- PRODUCTION_READINESS.md
- SUPPORT_TASKS.md
- SECURITY_COMPLIANCE.md

### Updated Code
- Updated Code for the changes

### TASK Breakdown
- Individual Tasks that can be submitted individually and independantly to generate a new application based on the planning phase output.
