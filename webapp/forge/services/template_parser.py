"""
Template parsing service for extracting variables and metadata.
"""

import re
import yaml
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class InputType(Enum):
    """Input types for template sections."""
    TEXTAREA = "textarea"
    TEXT = "text"
    STRUCTURED = "structured"
    SELECT = "select"
    MULTISELECT = "multiselect"
    CHECKBOX = "checkbox"


@dataclass
class StructuredField:
    """Represents a structured input field within a section."""
    name: str
    field_type: str  # text, select, multiselect, checkbox, textarea
    options: List[str] = field(default_factory=list)
    required: bool = False
    description: str = ""
    default_value: Optional[str] = None
    validation_pattern: Optional[str] = None


@dataclass
class SectionMetadata:
    """
    Metadata for a template section defining validation rules and input configuration.
    """
    name: str
    required: bool = True
    min_words: int = 10
    max_words: Optional[int] = None
    input_type: InputType = InputType.TEXTAREA
    help_text: str = ""
    keywords_required: List[str] = field(default_factory=list)
    keywords_recommended: List[str] = field(default_factory=list)
    validation_severity: ValidationSeverity = ValidationSeverity.WARNING
    examples: List[str] = field(default_factory=list)
    structured_fields: List[StructuredField] = field(default_factory=list)
    placeholder: str = ""

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> 'SectionMetadata':
        """Create SectionMetadata from a dictionary (parsed from YAML)."""
        # Parse input_type
        input_type_str = data.get('input_type', 'textarea').lower()
        try:
            input_type = InputType(input_type_str)
        except ValueError:
            input_type = InputType.TEXTAREA

        # Parse validation_severity
        severity_str = data.get('validation_severity', 'warning').lower()
        try:
            severity = ValidationSeverity(severity_str)
        except ValueError:
            severity = ValidationSeverity.WARNING

        # Parse structured fields
        structured_fields = []
        for field_data in data.get('structured_fields', []):
            structured_fields.append(StructuredField(
                name=field_data.get('name', ''),
                field_type=field_data.get('type', 'text'),
                options=field_data.get('options', []),
                required=field_data.get('required', False),
                description=field_data.get('description', ''),
                default_value=field_data.get('default'),
                validation_pattern=field_data.get('validation'),
            ))

        return cls(
            name=name,
            required=data.get('required', True),
            min_words=data.get('min_words', 10),
            max_words=data.get('max_words'),
            input_type=input_type,
            help_text=data.get('help_text', ''),
            keywords_required=data.get('keywords_required', []),
            keywords_recommended=data.get('keywords_recommended', []),
            validation_severity=severity,
            examples=data.get('examples', []),
            structured_fields=structured_fields,
            placeholder=data.get('placeholder', ''),
        )


@dataclass
class VariableMetadata:
    """
    Metadata for a template variable defining validation rules.
    """
    name: str
    description: str = ""
    required: bool = True
    validation_pattern: Optional[str] = None
    default_value: Optional[str] = None
    input_type: str = "text"  # text, textarea, select, multiselect
    options: List[str] = field(default_factory=list)
    help_text: str = ""
    placeholder: str = ""
    min_length: Optional[int] = None
    max_length: Optional[int] = None

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> 'VariableMetadata':
        """Create VariableMetadata from a dictionary (parsed from YAML)."""
        # Support both 'type' and 'input_type' keys
        input_type = data.get('input_type') or data.get('type', 'text')
        
        return cls(
            name=name,
            description=data.get('description', ''),
            required=data.get('required', True),
            validation_pattern=data.get('validation'),
            default_value=data.get('default'),
            input_type=input_type,
            options=data.get('options', []),
            help_text=data.get('help_text', ''),
            placeholder=data.get('placeholder', ''),
            min_length=data.get('min_length'),
            max_length=data.get('max_length'),
        )


@dataclass
class SectionValidationResult:
    """Result of validating section content against metadata."""
    is_valid: bool
    section_name: str
    severity: ValidationSeverity
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)
    missing_keywords: List[str] = field(default_factory=list)
    word_count: int = 0
    completion_percentage: float = 0.0


@dataclass
class TemplateVariable:
    """
    Represents a variable found in a template.
    """
    name: str
    syntax: str  # 'double_brace' or 'single_bracket'
    start_pos: int
    end_pos: int
    default_value: Optional[str] = None
    metadata: Optional[VariableMetadata] = None


class TemplateParser:
    """
    Service for parsing BMAD templates and extracting variables.
    """
    
    # Regex patterns for variable detection
    DOUBLE_BRACE_PATTERN = r'\{\{(\w+(?::[^}]+)?)\}\}'
    SINGLE_BRACKET_PATTERN = r'\[(\w+(?::[^\]]+)?)\]'
    
    # BMAD section patterns
    REQUIRED_SECTIONS = [
        '## Your Role',
        '## Input',
        '## Output Requirements',
    ]
    
    OPTIONAL_SECTIONS = [
        '## Context',
        '## Constraints',
        '## Examples',
        '## Step-by-Step Instructions',
        '## Success Criteria',
        '## Notes',
    ]
    
    ALL_SECTIONS = REQUIRED_SECTIONS + OPTIONAL_SECTIONS
    
    @classmethod
    def extract_variables(cls, content: str) -> List[TemplateVariable]:
        """
        Extract all variables from template content.
        
        Args:
            content: Template content string
            
        Returns:
            List of TemplateVariable objects
        """
        variables = []
        
        # Find double brace variables: {{VAR_NAME}} or {{VAR_NAME:default}}
        for match in re.finditer(cls.DOUBLE_BRACE_PATTERN, content):
            var = TemplateVariable(
                name=match.group(1).split(':')[0],
                syntax='double_brace',
                start_pos=match.start(),
                end_pos=match.end(),
                default_value=match.group(1).split(':')[1] if ':' in match.group(1) else None
            )
            if var not in variables:
                variables.append(var)
        
        # Find single bracket variables: [VAR_NAME]
        for match in re.finditer(cls.SINGLE_BRACKET_PATTERN, content):
            var = TemplateVariable(
                name=match.group(1),
                syntax='single_bracket',
                start_pos=match.start(),
                end_pos=match.end(),
            )
            if var not in variables:
                variables.append(var)
        
        return variables
    
    @classmethod
    def extract_variables_simple(cls, content: str) -> List[str]:
        """
        Extract variable names from template content (simple version).
        
        Args:
            content: Template content string
            
        Returns:
            List of variable names
        """
        pattern = r'\{\{(\w+)\}\}|\[(\w+)\]'
        matches = re.findall(pattern, content)
        variables = set()
        for match in matches:
            variables.add(match[0] if match[0] else match[1])
        return sorted(list(variables))
    
    @classmethod
    def detect_sections(cls, content: str) -> Dict[str, Tuple[int, int]]:
        """
        Detect BMAD sections in template content.
        
        Args:
            content: Template content string
            
        Returns:
            Dictionary mapping section names to their (start, end) positions
        """
        sections = {}
        content_lower = content.lower()
        
        for section in cls.ALL_SECTIONS:
            section_lower = section.lower()
            pos = content_lower.find(section_lower)
            if pos != -1:
                sections[section] = (pos, pos + len(section))
        
        return sections
    
    @classmethod
    def check_required_sections(cls, content: str) -> Tuple[bool, List[str]]:
        """
        Check if all required BMAD sections are present.
        
        Args:
            content: Template content string
            
        Returns:
            Tuple of (is_valid, list of missing sections)
        """
        sections = cls.detect_sections(content)
        missing = []
        
        for section in cls.REQUIRED_SECTIONS:
            if section not in sections:
                missing.append(section)
        
        return len(missing) == 0, missing
    
    @classmethod
    def validate_template(cls, content: str) -> Dict:
        """
        Validate a template for BMAD compliance.
        
        Args:
            content: Template content string
            
        Returns:
            Dictionary with validation results
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'variables': [],
            'sections': [],
        }
        
        # Check required sections
        is_valid, missing = cls.check_required_sections(content)
        if not is_valid:
            result['is_valid'] = False
            result['errors'].append(f"Missing required sections: {', '.join(missing)}")
        
        # Extract variables
        variables = cls.extract_variables(content)
        result['variables'] = [
            {
                'name': v.name,
                'syntax': v.syntax,
                'has_default': v.default_value is not None,
            }
            for v in variables
        ]
        
        # Check for potential issues
        if not variables:
            result['warnings'].append("No variables found in template")
        
        # Detect present sections
        sections = cls.detect_sections(content)
        result['sections'] = list(sections.keys())
        
        return result
    
    @classmethod
    def substitute_variables(cls, content: str, values: Dict[str, str]) -> str:
        """
        Substitute variables in template content with provided values.
        
        Args:
            content: Template content string
            values: Dictionary mapping variable names to replacement values
            
        Returns:
            Content with variables substituted
        """
        result = content
        
        for var_name, value in values.items():
            # Replace double brace syntax
            result = result.replace('{{' + var_name + '}}', str(value))
            # Replace single bracket syntax
            result = result.replace('[' + var_name + ']', str(value))
        
        return result
    
    @classmethod
    def find_unreplaced_variables(cls, content: str) -> List[str]:
        """
        Find variables that were not replaced (still present in content).

        Args:
            content: Template content string

        Returns:
            List of unreplaced variable names
        """
        variables = cls.extract_variables_simple(content)
        # Check if any variables remain in content
        unreplaced = []
        for var in variables:
            if '{{' + var + '}}' in content or '[' + var + ']' in content:
                unreplaced.append(var)
        return unreplaced

    @classmethod
    def parse_frontmatter(cls, content: str) -> Tuple[Dict[str, Any], str]:
        """
        Parse YAML frontmatter from template content.

        Args:
            content: Template content string

        Returns:
            Tuple of (frontmatter dict, remaining content)
        """
        if not content.startswith('---'):
            return {}, content

        # Find the closing ---
        lines = content.split('\n')
        end_index = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_index = i
                break

        if end_index == -1:
            return {}, content

        # Parse YAML frontmatter
        frontmatter_text = '\n'.join(lines[1:end_index])
        remaining_content = '\n'.join(lines[end_index + 1:])

        try:
            frontmatter = yaml.safe_load(frontmatter_text) or {}
        except yaml.YAMLError:
            frontmatter = {}

        return frontmatter, remaining_content.strip()

    @classmethod
    def parse_section_metadata(cls, content: str) -> Dict[str, SectionMetadata]:
        """
        Parse section metadata from template frontmatter.

        Args:
            content: Template content string

        Returns:
            Dictionary mapping section names to SectionMetadata
        """
        frontmatter, _ = cls.parse_frontmatter(content)
        sections_data = frontmatter.get('sections', {})

        section_metadata = {}
        for section_name, section_config in sections_data.items():
            if isinstance(section_config, dict):
                section_metadata[section_name] = SectionMetadata.from_dict(
                    section_name, section_config
                )

        return section_metadata

    @classmethod
    def parse_variable_metadata(cls, content: str) -> Dict[str, VariableMetadata]:
        """
        Parse variable metadata from template frontmatter.

        Args:
            content: Template content string

        Returns:
            Dictionary mapping variable names to VariableMetadata
        """
        frontmatter, _ = cls.parse_frontmatter(content)
        variables_data = frontmatter.get('variables', {})

        variable_metadata = {}
        for var_name, var_config in variables_data.items():
            if isinstance(var_config, dict):
                variable_metadata[var_name] = VariableMetadata.from_dict(
                    var_name, var_config
                )

        return variable_metadata

    @classmethod
    def get_section_metadata_with_defaults(
        cls,
        content: str
    ) -> Dict[str, SectionMetadata]:
        """
        Get section metadata with fallback defaults for templates without metadata.

        Default rules for backward compatibility:
        - "Your Role": required, min_words=20, severity=critical
        - "Input": required, min_words=15, severity=critical
        - "Output Requirements": required, min_words=20, severity=critical
        - Other sections: optional, min_words=10, severity=warning

        Args:
            content: Template content string

        Returns:
            Dictionary mapping section names to SectionMetadata
        """
        # Parse any existing metadata from frontmatter
        metadata = cls.parse_section_metadata(content)

        # Define default section configurations
        default_configs = {
            'Your Role': SectionMetadata(
                name='Your Role',
                required=True,
                min_words=20,
                validation_severity=ValidationSeverity.CRITICAL,
                help_text="Define the AI persona and primary responsibilities.",
                keywords_recommended=['responsibility', 'expertise', 'role', 'task'],
            ),
            'Input': SectionMetadata(
                name='Input',
                required=True,
                min_words=15,
                validation_severity=ValidationSeverity.CRITICAL,
                help_text="Specify what information or data will be provided.",
                keywords_recommended=['provide', 'given', 'receive', 'include'],
            ),
            'Output Requirements': SectionMetadata(
                name='Output Requirements',
                required=True,
                min_words=20,
                validation_severity=ValidationSeverity.CRITICAL,
                help_text="Define the expected output format and structure.",
                keywords_recommended=['format', 'structure', 'output', 'return', 'produce'],
            ),
            'Context': SectionMetadata(
                name='Context',
                required=False,
                min_words=10,
                validation_severity=ValidationSeverity.WARNING,
                help_text="Provide background information and context.",
            ),
            'Constraints': SectionMetadata(
                name='Constraints',
                required=False,
                min_words=10,
                validation_severity=ValidationSeverity.WARNING,
                help_text="Define any limitations or restrictions.",
            ),
            'Examples': SectionMetadata(
                name='Examples',
                required=False,
                min_words=10,
                validation_severity=ValidationSeverity.INFO,
                help_text="Provide examples of expected input/output.",
            ),
            'Step-by-Step Instructions': SectionMetadata(
                name='Step-by-Step Instructions',
                required=False,
                min_words=10,
                validation_severity=ValidationSeverity.WARNING,
                help_text="Break down the process into clear steps.",
            ),
            'Success Criteria': SectionMetadata(
                name='Success Criteria',
                required=False,
                min_words=10,
                validation_severity=ValidationSeverity.WARNING,
                help_text="Define how success will be measured.",
            ),
            'Notes': SectionMetadata(
                name='Notes',
                required=False,
                min_words=5,
                validation_severity=ValidationSeverity.INFO,
                help_text="Additional notes and considerations.",
            ),
        }

        # Detect sections in content
        detected_sections = cls.detect_sections(content)

        # Merge: use provided metadata, fall back to defaults
        result = {}
        for section_name in detected_sections:
            # Clean section name (remove ## prefix if present)
            clean_name = section_name.replace('## ', '').strip()

            if clean_name in metadata:
                result[clean_name] = metadata[clean_name]
            elif clean_name in default_configs:
                result[clean_name] = default_configs[clean_name]
            else:
                # Create default metadata for unknown sections
                result[clean_name] = SectionMetadata(
                    name=clean_name,
                    required=False,
                    min_words=10,
                    validation_severity=ValidationSeverity.WARNING,
                )

        return result

    @classmethod
    def validate_section_against_metadata(
        cls,
        section_name: str,
        content: str,
        metadata: Optional[SectionMetadata] = None
    ) -> SectionValidationResult:
        """
        Validate section content against its metadata rules.

        Args:
            section_name: Name of the section being validated
            content: Content of the section
            metadata: SectionMetadata for validation rules (uses defaults if None)

        Returns:
            SectionValidationResult with validation details
        """
        # Use default metadata if none provided
        if metadata is None:
            default_metadata = cls.get_section_metadata_with_defaults('')
            metadata = default_metadata.get(
                section_name,
                SectionMetadata(
                    name=section_name,
                    required=False,
                    min_words=10,
                    validation_severity=ValidationSeverity.WARNING,
                )
            )

        result = SectionValidationResult(
            is_valid=True,
            section_name=section_name,
            severity=metadata.validation_severity,
        )

        # Calculate word count
        words = content.split()
        result.word_count = len(words)

        # Check minimum word count
        if result.word_count < metadata.min_words:
            if metadata.validation_severity == ValidationSeverity.CRITICAL:
                result.is_valid = False
                result.errors.append(
                    f"Section '{section_name}' has {result.word_count} words, "
                    f"minimum required is {metadata.min_words}."
                )
            else:
                result.warnings.append(
                    f"Section '{section_name}' has {result.word_count} words, "
                    f"recommended minimum is {metadata.min_words}."
                )

        # Check maximum word count
        if metadata.max_words and result.word_count > metadata.max_words:
            result.warnings.append(
                f"Section '{section_name}' has {result.word_count} words, "
                f"recommended maximum is {metadata.max_words}."
            )

        # Check required keywords
        content_lower = content.lower()
        missing_required = []
        for keyword in metadata.keywords_required:
            if keyword.lower() not in content_lower:
                missing_required.append(keyword)

        if missing_required:
            result.is_valid = False
            result.missing_keywords = missing_required
            result.errors.append(
                f"Missing required keywords in '{section_name}': {', '.join(missing_required)}"
            )

        # Check recommended keywords (info only)
        missing_recommended = []
        for keyword in metadata.keywords_recommended:
            if keyword.lower() not in content_lower:
                missing_recommended.append(keyword)

        if missing_recommended:
            result.info.append(
                f"Consider including these keywords in '{section_name}': {', '.join(missing_recommended)}"
            )

        # Check for unreplaced variables
        unreplaced = cls.find_unreplaced_variables(content)
        if unreplaced:
            result.is_valid = False
            result.errors.append(
                f"Unreplaced variables in '{section_name}': {', '.join(unreplaced)}"
            )

        # Calculate completion percentage
        if metadata.min_words > 0:
            word_percentage = min(100, (result.word_count / metadata.min_words) * 100)
        else:
            word_percentage = 100 if result.word_count > 0 else 0

        keyword_count = len(metadata.keywords_required) + len(metadata.keywords_recommended)
        if keyword_count > 0:
            found_keywords = (
                len(metadata.keywords_required) - len(missing_required) +
                len(metadata.keywords_recommended) - len(missing_recommended)
            )
            keyword_percentage = (found_keywords / keyword_count) * 100
        else:
            keyword_percentage = 100

        result.completion_percentage = (word_percentage + keyword_percentage) / 2

        return result

    @classmethod
    def validate_variable_value(
        cls,
        variable_name: str,
        value: str,
        metadata: Optional[VariableMetadata] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate a variable value against its metadata rules.

        Args:
            variable_name: Name of the variable
            value: Value to validate
            metadata: VariableMetadata for validation rules

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        if metadata is None:
            # Basic validation without metadata
            if not value or not value.strip():
                return False, [f"Variable '{variable_name}' cannot be empty."]
            return True, []

        # Check required
        if metadata.required and (not value or not value.strip()):
            errors.append(f"Variable '{variable_name}' is required.")
            return False, errors

        # Skip further validation if empty and not required
        if not value or not value.strip():
            return True, []

        # Check min length
        if metadata.min_length and len(value) < metadata.min_length:
            errors.append(
                f"Variable '{variable_name}' must be at least "
                f"{metadata.min_length} characters."
            )

        # Check max length
        if metadata.max_length and len(value) > metadata.max_length:
            errors.append(
                f"Variable '{variable_name}' must be at most "
                f"{metadata.max_length} characters."
            )

        # Check validation pattern
        if metadata.validation_pattern:
            try:
                pattern = re.compile(metadata.validation_pattern)
                if not pattern.match(value):
                    errors.append(
                        f"Variable '{variable_name}' does not match required format."
                    )
            except re.error:
                # Invalid regex pattern, skip validation
                pass

        # Check options (for select/multiselect)
        if metadata.options and metadata.input_type in ('select', 'multiselect'):
            if metadata.input_type == 'multiselect':
                values = [v.strip() for v in value.split(',')]
                for v in values:
                    if v and v not in metadata.options:
                        errors.append(
                            f"Invalid value '{v}' for variable '{variable_name}'. "
                            f"Valid options: {', '.join(metadata.options)}"
                        )
            elif value not in metadata.options:
                errors.append(
                    f"Invalid value for variable '{variable_name}'. "
                    f"Valid options: {', '.join(metadata.options)}"
                )

        return len(errors) == 0, errors

    @classmethod
    def get_section_guidance(cls, section_name: str, metadata: Optional[SectionMetadata] = None) -> Dict:
        """
        Get contextual guidance for a section.

        Args:
            section_name: Name of the section
            metadata: Optional section metadata

        Returns:
            Dictionary with guidance information
        """
        if metadata is None:
            default_metadata = cls.get_section_metadata_with_defaults('')
            metadata = default_metadata.get(section_name)

        if metadata is None:
            return {
                'section_name': section_name,
                'help_text': f"Enter content for the {section_name} section.",
                'min_words': 10,
                'required': False,
                'examples': [],
                'keywords_recommended': [],
            }

        return {
            'section_name': section_name,
            'help_text': metadata.help_text,
            'min_words': metadata.min_words,
            'max_words': metadata.max_words,
            'required': metadata.required,
            'examples': metadata.examples,
            'keywords_required': metadata.keywords_required,
            'keywords_recommended': metadata.keywords_recommended,
            'input_type': metadata.input_type.value,
            'structured_fields': [
                {
                    'name': f.name,
                    'type': f.field_type,
                    'options': f.options,
                    'required': f.required,
                    'description': f.description,
                }
                for f in metadata.structured_fields
            ],
            'placeholder': metadata.placeholder,
            'validation_severity': metadata.validation_severity.value,
        }
