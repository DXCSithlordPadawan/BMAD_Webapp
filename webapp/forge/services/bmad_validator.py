"""
BMAD compliance validation service.
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from .template_parser import (
    TemplateParser,
    SectionMetadata,
    VariableMetadata,
    ValidationSeverity as ParserValidationSeverity,
    SectionValidationResult,
)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

    @classmethod
    def from_parser_severity(cls, severity: ParserValidationSeverity) -> 'ValidationSeverity':
        """Convert from parser ValidationSeverity to this ValidationSeverity."""
        mapping = {
            ParserValidationSeverity.CRITICAL: cls.ERROR,
            ParserValidationSeverity.WARNING: cls.WARNING,
            ParserValidationSeverity.INFO: cls.INFO,
        }
        return mapping.get(severity, cls.WARNING)


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    severity: ValidationSeverity
    message: str
    section: Optional[str] = None
    details: Optional[Dict] = None


@dataclass
class BMADValidationReport:
    """Comprehensive validation report for a generated prompt."""
    is_valid: bool = True
    score: int = 0
    max_score: int = 100
    results: List[ValidationResult] = field(default_factory=list)
    missing_sections: List[str] = field(default_factory=list)
    unreplaced_variables: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    
    def add_result(self, result: ValidationResult):
        """Add a validation result to the report."""
        self.results.append(result)
        if result.severity == ValidationSeverity.ERROR:
            self.is_valid = False
            self.score -= 10
        elif result.severity == ValidationSeverity.WARNING:
            self.score -= 5
    
    def get_summary(self) -> Dict:
        """Get a summary dictionary of the validation report."""
        return {
            'is_valid': self.is_valid,
            'score': max(0, self.score),
            'missing_sections': self.missing_sections,
            'unreplaced_variables': self.unreplaced_variables,
            'notes': self.notes,
            'total_checks': len(self.results),
            'passed_checks': sum(1 for r in self.results if r.severity != ValidationSeverity.ERROR),
        }


class BMADValidator:
    """
    Service for validating generated prompts against BMAD framework requirements.
    """
    
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
    
    ROLE_KEYWORDS = {
        'orchestrator': ['orchestrator', 'coordination', 'oversight', 'workflow'],
        'analyst': ['analyst', 'analysis', 'data', 'insights'],
        'pm': ['project manager', 'product owner', 'stakeholder'],
        'architect': ['architect', 'architecture', 'design', 'system'],
        'scrum_master': ['scrum master', 'agile', 'sprint', 'ceremony'],
        'developer': ['developer', 'engineer', 'code', 'implementation'],
        'qa': ['qa', 'quality assurance', 'tester', 'testing'],
    }
    
    @classmethod
    def validate(cls, prompt_content: str) -> BMADValidationReport:
        """
        Perform comprehensive BMAD validation on a prompt.
        
        Args:
            prompt_content: The generated prompt content
            
        Returns:
            BMADValidationReport with all validation results
        """
        report = BMADValidationReport()
        content_lower = prompt_content.lower()
        
        # 1. Check for required sections
        for section in cls.REQUIRED_SECTIONS:
            if section.lower() not in content_lower:
                report.missing_sections.append(section)
                report.add_result(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"Missing required section: {section}",
                    section=section,
                ))
        
        # 2. Check for unreplaced variables
        unreplaced = TemplateParser.find_unreplaced_variables(prompt_content)
        if unreplaced:
            report.unreplaced_variables = unreplaced
            report.add_result(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message=f"Unreplaced variables found: {', '.join(unreplaced)}",
                details={'variables': unreplaced}
            ))
        
        # 3. Check section structure and content
        sections = TemplateParser.detect_sections(prompt_content)
        
        # Check "Your Role" section has content
        if '## Your Role' in sections:
            role_section = prompt_content[sections['## Your Role'][1]:]
            next_section_pos = len(role_section)
            for section in sections:
                if section != '## Your Role':
                    pos = role_section.lower().find(section.lower())
                    if pos != -1:
                        next_section_pos = pos
                        break
            role_content = role_section[:next_section_pos].strip()
            if len(role_content) < 10:
                report.add_result(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.WARNING,
                    message="'## Your Role' section appears to have minimal content",
                    section='## Your Role',
                ))
        
        # 4. Check "Input" section has content
        if '## Input' in sections:
            input_section = prompt_content[sections['## Input'][1]:]
            next_section_pos = len(input_section)
            for section in sections:
                if section != '## Input':
                    pos = input_section.lower().find(section.lower())
                    if pos != -1:
                        next_section_pos = pos
                        break
            input_content = input_section[:next_section_pos].strip()
            if len(input_content) < 10:
                report.add_result(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.WARNING,
                    message="'## Input' section appears to have minimal content",
                    section='## Input',
                ))
        
        # 5. Check "Output Requirements" section
        if '## Output Requirements' in sections:
            output_section = prompt_content[sections['## Output Requirements'][1]:]
            next_section_pos = len(output_section)
            for section in sections:
                if section != '## Output Requirements':
                    pos = output_section.lower().find(section.lower())
                    if pos != -1:
                        next_section_pos = pos
                        break
            output_content = output_section[:next_section_pos].strip()
            
            # Check for specific output format keywords
            format_keywords = ['format', 'structure', 'output', 'response', 'return']
            has_format_keyword = any(kw in output_content.lower() for kw in format_keywords)
            if not has_format_keyword:
                report.add_result(ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.WARNING,
                    message="'## Output Requirements' should specify the expected output format",
                    section='## Output Requirements',
                ))
        
        # 6. Check overall structure
        total_sections = len(sections)
        if total_sections < 3:
            report.add_result(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                message="Prompt has fewer sections than recommended for BMAD compliance",
            ))
        
        # 7. Check for meaningful content
        word_count = len(prompt_content.split())
        if word_count < 50:
            report.add_result(ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                message="Prompt content seems very short (< 50 words)",
            ))
        elif word_count < 100:
            report.notes.append("Prompt is relatively short; consider adding more context")
        
        # 8. Check for variable usage (good practice)
        variable_count = len(TemplateParser.extract_variables(prompt_content))
        if variable_count > 0 and len(unreplaced) == 0:
            report.score += 10  # Bonus for using variables properly
        
        # 9. Optional sections bonus
        optional_present = sum(1 for s in cls.OPTIONAL_SECTIONS if s in sections)
        if optional_present >= 2:
            report.score += 10  # Bonus for comprehensive structure
        
        # Calculate final score
        report.score = max(0, min(100, report.score))
        
        return report
    
    @classmethod
    def quick_validate(cls, prompt_content: str) -> Tuple[bool, List[str]]:
        """
        Quick validation with basic checks.
        
        Args:
            prompt_content: The generated prompt content
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        content_lower = prompt_content.lower()
        
        # Check required sections
        for section in cls.REQUIRED_SECTIONS:
            if section.lower() not in content_lower:
                issues.append(f"Missing {section}")
        
        # Check for unreplaced variables
        unreplaced = TemplateParser.find_unreplaced_variables(prompt_content)
        if unreplaced:
            issues.append(f"Unreplaced variables: {', '.join(unreplaced)}")
        
        return len(issues) == 0, issues
    
    @classmethod
    def validate_for_role(cls, prompt_content: str, role: str) -> ValidationResult:
        """
        Validate prompt content for specific BMAD agent role.
        
        Args:
            prompt_content: The generated prompt content
            role: BMAD agent role identifier
            
        Returns:
            ValidationResult for role-specific checks
        """
        keywords = cls.ROLE_KEYWORDS.get(role, [])
        content_lower = prompt_content.lower()
        
        has_role_content = any(kw in content_lower for kw in keywords)
        
        if not has_role_content:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                message=f"Prompt may not be appropriately scoped for {role} role",
                details={'role': role, 'expected_keywords': keywords}
            )
        
        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            message=f"Prompt appears appropriate for {role} role",
        )


def validate_prompt(prompt_content: str) -> Dict:
    """
    Convenience function to validate a prompt and return results.

    Args:
        prompt_content: The prompt content to validate

    Returns:
        Dictionary with validation results
    """
    report = BMADValidator.validate(prompt_content)
    return report.get_summary()


@dataclass
class MetadataValidationResult:
    """Result of metadata-aware validation."""
    is_valid: bool
    overall_score: int = 100
    section_results: List[Dict] = field(default_factory=list)
    variable_results: List[Dict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)
    completion_percentage: float = 0.0


class MetadataAwareValidator:
    """
    Enhanced validator that uses template metadata for validation rules.
    """

    @classmethod
    def validate_with_metadata(
        cls,
        prompt_content: str,
        template_content: str
    ) -> MetadataValidationResult:
        """
        Perform comprehensive validation using template metadata.

        Args:
            prompt_content: The generated prompt content to validate
            template_content: The original template content with metadata

        Returns:
            MetadataValidationResult with detailed validation information
        """
        result = MetadataValidationResult(is_valid=True)

        # Get section metadata with defaults
        section_metadata = TemplateParser.get_section_metadata_with_defaults(template_content)
        variable_metadata = TemplateParser.parse_variable_metadata(template_content)

        # Detect sections in prompt
        sections = TemplateParser.detect_sections(prompt_content)

        # Extract section content for validation
        section_contents = cls._extract_section_contents(prompt_content, sections)

        # Validate each section
        total_completion = 0
        section_count = 0

        for section_name, metadata in section_metadata.items():
            clean_name = section_name.replace('## ', '')
            section_content = section_contents.get(section_name, section_contents.get(f'## {section_name}', ''))

            # Check if required section is missing
            if metadata.required and not section_content.strip():
                result.is_valid = False
                result.errors.append(f"Missing required section: {clean_name}")
                result.overall_score -= 20
                result.section_results.append({
                    'section_name': clean_name,
                    'is_valid': False,
                    'severity': 'error',
                    'errors': [f"Required section is missing"],
                    'warnings': [],
                    'completion_percentage': 0,
                })
                continue

            # Validate section content
            validation = TemplateParser.validate_section_against_metadata(
                clean_name, section_content, metadata
            )

            # Convert to result format
            severity = ValidationSeverity.from_parser_severity(validation.severity)
            section_result = {
                'section_name': clean_name,
                'is_valid': validation.is_valid,
                'severity': severity.value,
                'errors': validation.errors,
                'warnings': validation.warnings,
                'info': validation.info,
                'word_count': validation.word_count,
                'min_words': metadata.min_words,
                'completion_percentage': validation.completion_percentage,
                'missing_keywords': validation.missing_keywords,
            }
            result.section_results.append(section_result)

            if not validation.is_valid:
                result.is_valid = False
                result.errors.extend(validation.errors)
                result.overall_score -= 10 * len(validation.errors)

            result.warnings.extend(validation.warnings)
            result.info.extend(validation.info)
            result.overall_score -= 2 * len(validation.warnings)

            total_completion += validation.completion_percentage
            section_count += 1

        # Calculate overall completion
        if section_count > 0:
            result.completion_percentage = total_completion / section_count

        # Check for unreplaced variables
        unreplaced = TemplateParser.find_unreplaced_variables(prompt_content)
        if unreplaced:
            result.is_valid = False
            result.errors.append(f"Unreplaced variables: {', '.join(unreplaced)}")
            result.overall_score -= 15 * len(unreplaced)

            for var in unreplaced:
                result.variable_results.append({
                    'variable_name': var,
                    'is_valid': False,
                    'error': 'Variable not replaced',
                })

        # Normalize score
        result.overall_score = max(0, min(100, result.overall_score))

        return result

    @classmethod
    def _extract_section_contents(
        cls,
        content: str,
        sections: Dict[str, Tuple[int, int]]
    ) -> Dict[str, str]:
        """
        Extract content for each section.

        Args:
            content: Full document content
            sections: Dictionary mapping section names to their positions

        Returns:
            Dictionary mapping section names to their content
        """
        section_contents = {}
        sorted_sections = sorted(sections.items(), key=lambda x: x[1][0])

        for i, (section_name, (start, end)) in enumerate(sorted_sections):
            # Find the end of this section (start of next section or end of content)
            if i + 1 < len(sorted_sections):
                next_start = sorted_sections[i + 1][1][0]
                section_content = content[end:next_start].strip()
            else:
                section_content = content[end:].strip()

            section_contents[section_name] = section_content

        return section_contents

    @classmethod
    def get_section_guidance(
        cls,
        section_name: str,
        template_content: str
    ) -> Dict[str, Any]:
        """
        Get contextual guidance for filling out a section.

        Args:
            section_name: Name of the section
            template_content: Original template content

        Returns:
            Dictionary with guidance information
        """
        section_metadata = TemplateParser.get_section_metadata_with_defaults(template_content)
        metadata = section_metadata.get(section_name)

        return TemplateParser.get_section_guidance(section_name, metadata)

    @classmethod
    def validate_variable(
        cls,
        variable_name: str,
        value: str,
        template_content: str
    ) -> Dict[str, Any]:
        """
        Validate a single variable value.

        Args:
            variable_name: Name of the variable
            value: Value to validate
            template_content: Original template content

        Returns:
            Dictionary with validation result
        """
        variable_metadata = TemplateParser.parse_variable_metadata(template_content)
        metadata = variable_metadata.get(variable_name)

        is_valid, errors = TemplateParser.validate_variable_value(
            variable_name, value, metadata
        )

        return {
            'variable_name': variable_name,
            'is_valid': is_valid,
            'errors': errors,
            'metadata': {
                'description': metadata.description if metadata else '',
                'required': metadata.required if metadata else True,
                'help_text': metadata.help_text if metadata else '',
            } if metadata else None,
        }

    @classmethod
    def quick_validate_with_metadata(
        cls,
        prompt_content: str,
        template_content: str
    ) -> Tuple[bool, List[str], int]:
        """
        Quick validation with metadata support.

        Args:
            prompt_content: The generated prompt content
            template_content: The original template content

        Returns:
            Tuple of (is_valid, list of issues, compliance score)
        """
        result = cls.validate_with_metadata(prompt_content, template_content)
        issues = result.errors + result.warnings
        return result.is_valid, issues, result.overall_score
