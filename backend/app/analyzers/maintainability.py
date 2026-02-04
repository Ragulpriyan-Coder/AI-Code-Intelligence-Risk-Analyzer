"""
Maintainability analyzer for code quality assessment.
Analyzes documentation, code style, and maintainability metrics.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import re

from app.utils.file_utils import FileInfo, get_language_from_extension
from app.analyzers.structure import FileStructure
from app.analyzers.complexity import FileComplexity


@dataclass
class MaintainabilityIssue:
    """A maintainability issue found in code."""
    issue_type: str
    severity: str  # "info", "warning", "error"
    title: str
    description: str
    file_path: str
    line_number: int = 0
    suggestion: str = ""


@dataclass
class FileMaintainability:
    """Maintainability analysis for a single file."""
    path: str
    language: str

    # Documentation metrics
    has_module_docstring: bool = False
    docstring_coverage: float = 0.0
    comment_ratio: float = 0.0

    # Code quality metrics
    avg_function_length: float = 0.0
    max_function_length: int = 0
    avg_line_length: float = 0.0
    max_line_length: int = 0

    # Naming conventions
    naming_violations: List[Dict] = field(default_factory=list)

    # Code smells
    issues: List[MaintainabilityIssue] = field(default_factory=list)

    # Scores
    documentation_score: float = 100.0
    readability_score: float = 100.0
    consistency_score: float = 100.0


# Naming convention patterns
NAMING_PATTERNS = {
    "python": {
        "class": r"^[A-Z][a-zA-Z0-9]*$",  # PascalCase
        "function": r"^[a-z_][a-z0-9_]*$",  # snake_case
        "constant": r"^[A-Z][A-Z0-9_]*$",  # UPPER_SNAKE_CASE
        "variable": r"^[a-z_][a-z0-9_]*$",  # snake_case
    },
    "javascript": {
        "class": r"^[A-Z][a-zA-Z0-9]*$",  # PascalCase
        "function": r"^[a-z][a-zA-Z0-9]*$",  # camelCase
        "constant": r"^[A-Z][A-Z0-9_]*$",  # UPPER_SNAKE_CASE
        "variable": r"^[a-z_$][a-zA-Z0-9_$]*$",  # camelCase
    },
    "typescript": {},  # Inherits from JavaScript
}

NAMING_PATTERNS["typescript"] = NAMING_PATTERNS["javascript"]

# Code smell patterns
CODE_SMELL_PATTERNS = {
    "long_line": {
        "threshold": 120,
        "title": "Line too long",
        "severity": "warning"
    },
    "long_function": {
        "threshold": 50,
        "title": "Function too long",
        "severity": "warning"
    },
    "too_many_parameters": {
        "threshold": 5,
        "title": "Too many parameters",
        "severity": "warning"
    },
    "magic_number": {
        "pattern": r"(?<![a-zA-Z0-9_])(?!0[xX])[0-9]{2,}(?!\.[0-9])(?![a-zA-Z0-9_])",
        "title": "Magic number",
        "severity": "info"
    },
    "todo_comment": {
        "pattern": r"#\s*TODO|//\s*TODO|/\*\s*TODO",
        "title": "TODO comment found",
        "severity": "info"
    },
    "fixme_comment": {
        "pattern": r"#\s*FIXME|//\s*FIXME|/\*\s*FIXME",
        "title": "FIXME comment found",
        "severity": "warning"
    },
    "commented_code": {
        "pattern": r"^\s*#\s*(def |class |import |from |if |for |while |return )",
        "title": "Commented out code",
        "severity": "warning"
    },
    "print_statement": {
        "pattern": r"^\s*print\s*\(",
        "title": "Print statement (debug leftover?)",
        "severity": "info"
    },
}


def check_module_docstring(content: str, language: str) -> bool:
    """
    Check if a module has a docstring.

    Args:
        content: File content
        language: Programming language

    Returns:
        True if module has docstring
    """
    if language == "python":
        # Check for triple-quoted string at the start
        content = content.lstrip()
        return content.startswith('"""') or content.startswith("'''")

    return False


def calculate_comment_ratio(content: str, language: str) -> float:
    """
    Calculate the ratio of comment lines to code lines.

    Args:
        content: File content
        language: Programming language

    Returns:
        Comment ratio (0.0 to 1.0)
    """
    lines = content.splitlines()
    if not lines:
        return 0.0

    comment_lines = 0
    code_lines = 0

    if language == "python":
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                comment_lines += 1
            elif stripped and not stripped.startswith('"""') and not stripped.startswith("'''"):
                code_lines += 1
    elif language in {"javascript", "typescript", "java", "go", "rust"}:
        in_block_comment = False
        for line in lines:
            stripped = line.strip()
            if "/*" in stripped:
                in_block_comment = True
                comment_lines += 1
            elif "*/" in stripped:
                in_block_comment = False
                comment_lines += 1
            elif in_block_comment or stripped.startswith("//"):
                comment_lines += 1
            elif stripped:
                code_lines += 1

    if code_lines == 0:
        return 0.0

    return comment_lines / (comment_lines + code_lines)


def check_naming_conventions(
    structure: FileStructure,
    language: str
) -> List[Dict]:
    """
    Check naming convention violations.

    Args:
        structure: FileStructure object
        language: Programming language

    Returns:
        List of naming violations
    """
    violations = []
    patterns = NAMING_PATTERNS.get(language, {})

    if not patterns:
        return violations

    # Check class names
    class_pattern = patterns.get("class")
    if class_pattern:
        for cls in structure.classes:
            if not re.match(class_pattern, cls.name):
                violations.append({
                    "type": "class",
                    "name": cls.name,
                    "line": cls.line_start,
                    "expected": "PascalCase"
                })

    # Check function names
    func_pattern = patterns.get("function")
    if func_pattern:
        for func in structure.functions:
            # Skip dunder methods
            if func.name.startswith("__") and func.name.endswith("__"):
                continue
            if not re.match(func_pattern, func.name):
                violations.append({
                    "type": "function",
                    "name": func.name,
                    "line": func.line_start,
                    "expected": "snake_case" if language == "python" else "camelCase"
                })

    return violations


def detect_code_smells(
    content: str,
    file_path: str,
    structure: Optional[FileStructure] = None
) -> List[MaintainabilityIssue]:
    """
    Detect code smells in the content.

    Args:
        content: File content
        file_path: Path to file
        structure: Optional FileStructure

    Returns:
        List of maintainability issues
    """
    issues = []
    lines = content.splitlines()

    # Check line lengths
    threshold = CODE_SMELL_PATTERNS["long_line"]["threshold"]
    long_lines = [(i + 1, len(line)) for i, line in enumerate(lines) if len(line) > threshold]
    for line_num, length in long_lines[:5]:  # Report max 5
        issues.append(MaintainabilityIssue(
            issue_type="long_line",
            severity="warning",
            title=f"Line {line_num} is too long ({length} chars)",
            description=f"Lines should be under {threshold} characters for readability",
            file_path=file_path,
            line_number=line_num,
            suggestion="Break into multiple lines or extract to variables"
        ))

    # Check for TODO/FIXME comments
    for pattern_name in ["todo_comment", "fixme_comment", "commented_code", "print_statement"]:
        pattern_info = CODE_SMELL_PATTERNS[pattern_name]
        pattern = re.compile(pattern_info["pattern"], re.IGNORECASE)

        for i, line in enumerate(lines):
            if pattern.search(line):
                issues.append(MaintainabilityIssue(
                    issue_type=pattern_name,
                    severity=pattern_info["severity"],
                    title=pattern_info["title"],
                    description=line.strip()[:80],
                    file_path=file_path,
                    line_number=i + 1,
                ))

    # Check function lengths if structure available
    if structure:
        for func in structure.functions:
            length = func.line_end - func.line_start + 1
            if length > CODE_SMELL_PATTERNS["long_function"]["threshold"]:
                issues.append(MaintainabilityIssue(
                    issue_type="long_function",
                    severity="warning",
                    title=f"Function '{func.name}' is too long ({length} lines)",
                    description="Long functions are harder to understand and maintain",
                    file_path=file_path,
                    line_number=func.line_start,
                    suggestion="Break into smaller functions with single responsibilities"
                ))

        # Check parameter counts
        for func in structure.functions:
            if func.args_count > CODE_SMELL_PATTERNS["too_many_parameters"]["threshold"]:
                issues.append(MaintainabilityIssue(
                    issue_type="too_many_parameters",
                    severity="warning",
                    title=f"Function '{func.name}' has too many parameters ({func.args_count})",
                    description="Functions with many parameters are hard to call correctly",
                    file_path=file_path,
                    line_number=func.line_start,
                    suggestion="Consider using a configuration object or class"
                ))

    return issues


def analyze_file_maintainability(
    file_info: FileInfo,
    structure: Optional[FileStructure] = None,
    complexity: Optional[FileComplexity] = None
) -> FileMaintainability:
    """
    Analyze maintainability of a single file.

    Args:
        file_info: FileInfo object
        structure: Optional FileStructure from structure analyzer
        complexity: Optional FileComplexity from complexity analyzer

    Returns:
        FileMaintainability with analysis results
    """
    language = get_language_from_extension(file_info.extension) or "unknown"

    result = FileMaintainability(
        path=file_info.relative_path,
        language=language,
    )

    content = file_info.content
    lines = content.splitlines()

    # Documentation metrics
    result.has_module_docstring = check_module_docstring(content, language)
    result.comment_ratio = calculate_comment_ratio(content, language)

    if structure:
        result.docstring_coverage = structure.docstring_coverage

    # Line metrics
    if lines:
        line_lengths = [len(l) for l in lines if l.strip()]
        if line_lengths:
            result.avg_line_length = sum(line_lengths) / len(line_lengths)
            result.max_line_length = max(line_lengths)

    # Function metrics
    if structure and structure.functions:
        func_lengths = [f.line_end - f.line_start + 1 for f in structure.functions]
        result.avg_function_length = sum(func_lengths) / len(func_lengths)
        result.max_function_length = max(func_lengths)

    # Naming conventions
    if structure:
        result.naming_violations = check_naming_conventions(structure, language)

    # Code smells
    result.issues = detect_code_smells(content, file_info.relative_path, structure)

    # Calculate scores
    result.documentation_score = calculate_documentation_score(result)
    result.readability_score = calculate_readability_score(result, complexity)
    result.consistency_score = calculate_consistency_score(result)

    return result


def calculate_documentation_score(maintainability: FileMaintainability) -> float:
    """Calculate documentation score."""
    score = 100.0

    # Module docstring
    if not maintainability.has_module_docstring:
        score -= 15

    # Docstring coverage
    score -= (100 - maintainability.docstring_coverage) * 0.5

    # Comment ratio (ideal is 10-30%)
    ratio = maintainability.comment_ratio
    if ratio < 0.05:
        score -= 15
    elif ratio > 0.4:
        score -= 10  # Too many comments can also be a smell

    return max(0.0, min(100.0, score))


def calculate_readability_score(
    maintainability: FileMaintainability,
    complexity: Optional[FileComplexity]
) -> float:
    """Calculate readability score."""
    score = 100.0

    # Line length penalty
    if maintainability.max_line_length > 120:
        score -= min((maintainability.max_line_length - 120) * 0.2, 20)

    # Function length penalty
    if maintainability.max_function_length > 50:
        score -= min((maintainability.max_function_length - 50) * 0.3, 20)

    # Complexity impact
    if complexity and complexity.average_complexity > 5:
        score -= min((complexity.average_complexity - 5) * 3, 20)

    # Code smell penalties
    issue_penalties = {
        "long_line": 2,
        "long_function": 5,
        "too_many_parameters": 3,
        "commented_code": 2,
        "print_statement": 1,
    }

    for issue in maintainability.issues:
        penalty = issue_penalties.get(issue.issue_type, 1)
        score -= penalty

    return max(0.0, min(100.0, score))


def calculate_consistency_score(maintainability: FileMaintainability) -> float:
    """Calculate consistency score based on naming and style."""
    score = 100.0

    # Naming violation penalties
    score -= len(maintainability.naming_violations) * 5

    return max(0.0, min(100.0, score))


def get_maintainability_summary(analyses: List[FileMaintainability]) -> Dict[str, Any]:
    """
    Generate a summary of maintainability analysis.

    Args:
        analyses: List of FileMaintainability results

    Returns:
        Summary dictionary
    """
    if not analyses:
        return {
            "files_analyzed": 0,
            "avg_documentation_score": 100.0,
            "avg_readability_score": 100.0,
            "avg_consistency_score": 100.0,
            "issues": [],
        }

    # Calculate averages
    doc_scores = [a.documentation_score for a in analyses]
    read_scores = [a.readability_score for a in analyses]
    cons_scores = [a.consistency_score for a in analyses]

    # Collect all issues
    all_issues = []
    for analysis in analyses:
        all_issues.extend(analysis.issues)

    # Count issues by type
    issue_counts: Dict[str, int] = {}
    for issue in all_issues:
        issue_counts[issue.issue_type] = issue_counts.get(issue.issue_type, 0) + 1

    # Get files with worst scores
    worst_files = sorted(
        analyses,
        key=lambda x: (x.documentation_score + x.readability_score + x.consistency_score) / 3
    )[:10]

    return {
        "files_analyzed": len(analyses),
        "avg_documentation_score": round(sum(doc_scores) / len(doc_scores), 1),
        "avg_readability_score": round(sum(read_scores) / len(read_scores), 1),
        "avg_consistency_score": round(sum(cons_scores) / len(cons_scores), 1),
        "files_with_docstrings": sum(1 for a in analyses if a.has_module_docstring),
        "avg_comment_ratio": round(sum(a.comment_ratio for a in analyses) / len(analyses), 3),
        "total_issues": len(all_issues),
        "issues_by_type": issue_counts,
        "issues_by_severity": {
            "error": sum(1 for i in all_issues if i.severity == "error"),
            "warning": sum(1 for i in all_issues if i.severity == "warning"),
            "info": sum(1 for i in all_issues if i.severity == "info"),
        },
        "worst_files": [
            {
                "path": f.path,
                "documentation_score": round(f.documentation_score, 1),
                "readability_score": round(f.readability_score, 1),
                "consistency_score": round(f.consistency_score, 1),
                "issues_count": len(f.issues),
            }
            for f in worst_files
        ],
        "top_issues": [
            {
                "type": i.issue_type,
                "severity": i.severity,
                "title": i.title,
                "file": i.file_path,
                "line": i.line_number,
            }
            for i in sorted(
                all_issues,
                key=lambda x: {"error": 0, "warning": 1, "info": 2}.get(x.severity, 3)
            )[:20]
        ],
    }
