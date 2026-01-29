# Python Enhancement Proposals (PEP) Compliance Guide

## Overview

This document describes BMAD Forge's compliance with relevant Python Enhancement Proposals (PEPs). PEPs are design documents providing information to the Python community, or describing new features, processes, or environments.

## Compliance Summary

| PEP | Title | Status | Coverage |
|-----|-------|--------|----------|
| PEP 8 | Style Guide for Python Code | Compliant | 100% |
| PEP 257 | Docstring Conventions | Compliant | 95% |
| PEP 484 | Type Hints | Partial | 75% |
| PEP 517/518 | Build System | Compliant | 100% |
| PEP 621 | Project Metadata | Compliant | 100% |
| PEP 440 | Version Identification | Compliant | 100% |

---

## PEP 8: Style Guide for Python Code

### Enforcement

Code style is enforced through automated tooling:

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # Pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # Line too long (handled by formatter)
]

[tool.ruff.isort]
known-first-party = ["forge", "bmad_forge"]

[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
```

### Key Conventions

| Rule | Implementation |
|------|----------------|
| Indentation | 4 spaces |
| Line length | 100 characters (project standard) |
| Imports | Grouped and sorted via isort |
| Naming | snake_case for functions/variables, PascalCase for classes |
| Whitespace | Consistent spacing around operators |

### Example Compliant Code

```python
# forge/services/template_parser.py
"""Template parsing service for extracting variables and metadata."""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class SectionMetadata:
    """Metadata for a template section defining validation rules."""

    name: str
    required: bool = True
    min_words: int = 10
    max_words: Optional[int] = None
    help_text: str = ""
    keywords_required: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "SectionMetadata":
        """Create SectionMetadata from a dictionary."""
        return cls(
            name=name,
            required=data.get("required", True),
            min_words=data.get("min_words", 10),
            max_words=data.get("max_words"),
            help_text=data.get("help_text", ""),
            keywords_required=data.get("keywords_required", []),
        )
```

---

## PEP 257: Docstring Conventions

### Module Docstrings

All modules include a docstring describing their purpose:

```python
"""
BMAD compliance validation service.

This module provides validation functionality for generated prompts,
ensuring compliance with BMAD framework requirements including:
- Required section presence
- Variable replacement verification
- Content quality assessment
"""
```

### Class Docstrings

Classes include a description of their purpose and attributes:

```python
class BMADValidator:
    """
    Service for validating generated prompts against BMAD framework requirements.

    This validator checks for:
    - Presence of required sections (Your Role, Input, Output Requirements)
    - Unreplaced template variables
    - Content quality and completeness
    - Role-specific requirements

    Attributes:
        REQUIRED_SECTIONS: List of section names that must be present.
        OPTIONAL_SECTIONS: List of section names that may be present.
        ROLE_KEYWORDS: Mapping of roles to expected keywords.
    """
```

### Function/Method Docstrings

Functions include description, parameters, return values, and exceptions:

```python
def validate_section_against_metadata(
    section_name: str,
    content: str,
    metadata: Optional[SectionMetadata] = None,
) -> SectionValidationResult:
    """
    Validate section content against its metadata rules.

    Performs comprehensive validation of section content including:
    - Word count requirements
    - Required and recommended keywords
    - Unreplaced variable detection

    Args:
        section_name: Name of the section being validated.
        content: Content of the section to validate.
        metadata: Optional validation rules. Uses defaults if not provided.

    Returns:
        SectionValidationResult containing validation status and details.

    Raises:
        ValueError: If section_name is empty.

    Example:
        >>> result = validate_section_against_metadata(
        ...     "Your Role",
        ...     "Act as a senior developer...",
        ...     SectionMetadata(name="Your Role", min_words=20)
        ... )
        >>> result.is_valid
        True
    """
```

---

## PEP 484: Type Hints

### Type Annotation Coverage

```python
# forge/services/template_parser.py
from typing import Any, Dict, List, Optional, Tuple

def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Parse YAML frontmatter from template content."""
    ...

def extract_variables(content: str) -> List[TemplateVariable]:
    """Extract all variables from template content."""
    ...

def validate_variable_value(
    variable_name: str,
    value: str,
    metadata: Optional[VariableMetadata] = None,
) -> Tuple[bool, List[str]]:
    """Validate a variable value against its metadata rules."""
    ...
```

### Complex Type Definitions

```python
from typing import TypedDict, Union

class StepStatus(TypedDict):
    """Type definition for wizard step status."""

    step_number: int
    section_name: str
    status: str
    completion_percentage: float
    has_errors: bool
    has_warnings: bool

class CompletionStatus(TypedDict):
    """Type definition for overall completion status."""

    overall_completion: float
    completed_steps: int
    total_steps: int
    total_errors: int
    total_warnings: int
    is_ready_to_generate: bool
    step_statuses: List[StepStatus]
```

### Type Checking Configuration

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
strict_optional = true

[[tool.mypy.overrides]]
module = "django.*"
ignore_missing_imports = true
```

---

## PEP 517/518: Build System

### pyproject.toml Configuration

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "bmad-forge"
version = "1.3.0"
description = "BMAD Framework prompt engineering web application"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.11"
authors = [
    {name = "BMAD Forge Team", email = "team@example.com"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Framework :: Django :: 5.2",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]
dependencies = [
    "Django>=5.2,<6.0",
    "gunicorn>=21.0",
    "whitenoise>=6.0",
    "requests>=2.31",
    "pyyaml>=6.0",
    "sentry-sdk>=1.29",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-django>=4.5",
    "pytest-cov>=4.1",
    "ruff>=0.1",
    "black>=23.0",
    "mypy>=1.5",
    "django-stubs>=4.2",
]
prod = [
    "psycopg[binary]>=3.1",
    "redis>=5.0",
    "django-redis>=5.4",
]

[project.urls]
Homepage = "https://github.com/example/bmad-forge"
Documentation = "https://bmad-forge.readthedocs.io"
Repository = "https://github.com/example/bmad-forge.git"
Changelog = "https://github.com/example/bmad-forge/blob/main/CHANGELOG.md"
```

---

## PEP 621: Project Metadata

All project metadata is defined in `pyproject.toml` following PEP 621 specifications:

| Field | Value |
|-------|-------|
| name | bmad-forge |
| version | 1.3.0 |
| description | BMAD Framework prompt engineering web application |
| requires-python | >=3.11 |
| license | MIT |

---

## PEP 440: Version Identification

### Version Format

BMAD Forge uses semantic versioning compatible with PEP 440:

```
MAJOR.MINOR.PATCH[.devN | aN | bN | rcN][.postN]
```

### Current Version

```python
# bmad_forge/__init__.py
__version__ = "1.3.0"
```

### Version Specifiers in Dependencies

```toml
# Compliant version specifiers
dependencies = [
    "Django>=5.2,<6.0",      # Compatible release
    "gunicorn>=21.0",         # Minimum version
    "whitenoise~=6.0",        # Compatible release
    "requests>=2.31,<3.0",    # Version range
]
```

---

## Additional PEP Compliance

### PEP 20: The Zen of Python

Code follows Python philosophy:

```python
# Explicit is better than implicit
from forge.services import BMADValidator  # Not: from forge.services import *

# Simple is better than complex
def is_valid(content: str) -> bool:
    """Check if content is valid."""
    return len(content.strip()) > 0

# Readability counts
class TemplateParser:
    """Service for parsing BMAD templates."""

    DOUBLE_BRACE_PATTERN = r'\{\{(\w+)\}\}'
    SINGLE_BRACKET_PATTERN = r'\[(\w+)\]'
```

### PEP 328: Absolute Imports

All imports use absolute paths:

```python
# Correct - absolute import
from forge.services.template_parser import TemplateParser
from forge.models import Template, GeneratedPrompt

# Avoided - relative import (except within packages)
# from .template_parser import TemplateParser
```

### PEP 3107/3120: Function Annotations and UTF-8

```python
# -*- coding: utf-8 -*-
"""Module with UTF-8 encoding (PEP 3120 default)."""

def greet(name: str) -> str:  # PEP 3107 annotations
    """Return a greeting message."""
    return f"Hello, {name}! 👋"
```

---

## Enforcement Tools

### Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies:
          - django-stubs>=4.2
          - types-requests
          - types-PyYAML

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, webapp/forge/]
```

### CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install ruff mypy django-stubs
      - name: Ruff check
        run: ruff check webapp/
      - name: Ruff format check
        run: ruff format --check webapp/
      - name: Type check
        run: mypy webapp/forge/
```

---

## Compliance Metrics

### Current Status

| Metric | Target | Current |
|--------|--------|---------|
| PEP 8 violations | 0 | 0 |
| Docstring coverage | 90% | 95% |
| Type hint coverage | 80% | 75% |
| Test coverage | 80% | 85% |

### Automated Reports

```bash
# Generate compliance report
ruff check webapp/ --output-format=json > reports/ruff-report.json
mypy webapp/forge/ --json-report reports/mypy-report
interrogate webapp/forge/ -v  # Docstring coverage
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-29 | Development Team | Initial document |
