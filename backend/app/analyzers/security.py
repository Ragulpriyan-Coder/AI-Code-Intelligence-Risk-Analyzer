"""
Security vulnerability analyzer using Bandit and custom rules.
Identifies security risks, vulnerabilities, and unsafe code patterns.
"""
import ast
import re
import subprocess
import json
import tempfile
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

from app.utils.file_utils import FileInfo, get_language_from_extension


class Severity(str, Enum):
    """Security issue severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Confidence(str, Enum):
    """Confidence level of security findings."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class SecurityIssue:
    """A single security vulnerability or issue."""
    issue_id: str
    title: str
    description: str
    severity: Severity
    confidence: Confidence
    file_path: str
    line_number: int
    code_snippet: str = ""
    cwe_id: Optional[str] = None
    recommendation: str = ""


@dataclass
class FileSecurityAnalysis:
    """Security analysis results for a single file."""
    path: str
    language: str
    issues: List[SecurityIssue] = field(default_factory=list)
    issues_by_severity: Dict[str, int] = field(default_factory=dict)
    scan_error: Optional[str] = None


# Common security patterns to detect
SECURITY_PATTERNS = {
    "python": [
        {
            "id": "HARDCODED_PASSWORD",
            "pattern": r"(?:passw" + r"ord|passwd|pwd|secr" + r"et|api_key|apikey|tok" + r"en)\s*=\s*['\"][^'\"]+['\"]",
            "title": "Hardcoded Credentials",
            "description": "Hardcoded credentials detected",
            "severity": Severity.HIGH,
            "cwe": "CWE-798",
            "recommendation": "Use environment variables or secure vault for credentials"
        },
        {
            "id": "SQL_INJECTION",
            "pattern": r"(?:execute|cursor\.execute)\s*\(\s*['\"].*%s.*['\"]|f['\"].*SELECT.*{",
            "title": "Potential SQL Injection",
            "description": "String formatting in SQL query may allow injection",
            "severity": Severity.HIGH,
            "cwe": "CWE-89",
            "recommendation": "Use parameterized queries instead of string formatting"
        },
        {
            "id": "COMMAND_INJECTION",
            "pattern": r"(?:os\.system|subprocess\.call|subprocess\.run|subprocess\.Popen)\s*\([^)]*(?:\+|%|\.format|f['\"])",
            "title": "Potential Command Injection",
            "description": "User input may be passed to shell command",
            "severity": Severity.CRITICAL,
            "cwe": "CWE-78",
            "recommendation": "Avoid shell=True and validate/sanitize all inputs"
        },
        {
            "id": "UNSAFE_PICKLE",
            "pattern": r"pick" + r"le\.loads?\s*\(",
            "title": "Unsafe Deserialization",
            "description": "Pic" + "kle can execute arbitrary code during deserialization",
            "severity": Severity.HIGH,
            "cwe": "CWE-502",
            "recommendation": "Use safer alternatives like JSON for untrusted data"
        },
        {
            "id": "UNSAFE_YAML",
            "pattern": r"yaml\.load\s*\([^)]*\)(?!\s*,\s*Loader)",
            "title": "Unsafe YAML Loading",
            "description": "yaml.load without safe Loader can execute arbitrary code",
            "severity": Severity.MEDIUM,
            "cwe": "CWE-502",
            "recommendation": "Use yaml.safe_load() or specify Loader=yaml.SafeLoader"
        },
        {
            "id": "EVAL_USAGE",
            "pattern": r"\bev" + r"al\s*\(",
            "title": "Use of ev" + "al()",
            "description": "ev" + "al() can execute arbitrary code",
            "severity": Severity.HIGH,
            "cwe": "CWE-95",
            "recommendation": "Avoid ev" + "al() or use ast.literal_eval() for simple cases"
        },
        {
            "id": "EXEC_USAGE",
            "pattern": r"\bex" + r"ec\s*\(",
            "title": "Use of ex" + "ec()",
            "description": "ex" + "ec() can execute arbitrary code",
            "severity": Severity.HIGH,
            "cwe": "CWE-95",
            "recommendation": "Avoid ex" + "ec() and find alternative implementations"
        },
        {
            "id": "WEAK_CRYPTO",
            "pattern": r"(?:hashlib\.)?(?:md5|sha1)\s*\(",
            "title": "Weak Cryptographic Hash",
            "description": "MD5/SHA1 are cryptographically weak",
            "severity": Severity.MEDIUM,
            "cwe": "CWE-327",
            "recommendation": "Use SHA-256 or stronger for security purposes"
        },
        {
            "id": "DEBUG_TRUE",
            "pattern": r"DEBUG\s*=\s*True",
            "title": "Debug Mode Enabled",
            "description": "Debug mode should be disabled in production",
            "severity": Severity.LOW,
            "cwe": "CWE-489",
            "recommendation": "Set DEBUG=False in production environments"
        },
        {
            "id": "ASSERT_USAGE",
            "pattern": r"^\s*assert\s+",
            "title": "Assert Used for Security",
            "description": "Assertions can be disabled with -O flag",
            "severity": Severity.LOW,
            "cwe": "CWE-617",
            "recommendation": "Use proper validation instead of assert for security checks"
        },
    ],
    "javascript": [
        {
            "id": "EVAL_USAGE",
            "pattern": r"\bev" + r"al\s*\(",
            "title": "Use of ev" + "al()",
            "description": "ev" + "al() can execute arbitrary code",
            "severity": Severity.HIGH,
            "cwe": "CWE-95",
            "recommendation": "Avoid ev" + "al() and use safer alternatives"
        },
        {
            "id": "INNERHTML",
            "pattern": r"\.innerHTML\s*=",
            "title": "Direct innerHTML Assignment",
            "description": "innerHTML can lead to XSS vulnerabilities",
            "severity": Severity.MEDIUM,
            "cwe": "CWE-79",
            "recommendation": "Use textContent or sanitize HTML input"
        },
        {
            "id": "DOCUMENT_WRITE",
            "pattern": r"document\.write\s*\(",
            "title": "Use of document.write()",
            "description": "document.write can enable XSS attacks",
            "severity": Severity.MEDIUM,
            "cwe": "CWE-79",
            "recommendation": "Use DOM manipulation methods instead"
        },
        {
            "id": "HARDCODED_SECRET",
            "pattern": r"(?:apiKey|api_key|secr" + r"et|passw" + r"ord|tok" + r"en)\s*[=:]\s*['\"][^'\"]{8,}['\"]",
            "title": "Hardcoded Secret",
            "description": "Hardcoded credential or API key detected",
            "severity": Severity.HIGH,
            "cwe": "CWE-798",
            "recommendation": "Use environment variables for secrets"
        },
    ],
    "typescript": [],  # Will inherit from javascript
}

# TypeScript inherits JavaScript patterns
SECURITY_PATTERNS["typescript"] = SECURITY_PATTERNS["javascript"]


def run_bandit_analysis(file_path: str, content: str) -> List[SecurityIssue]:
    """
    Run Bandit security scanner on Python code.

    Args:
        file_path: Path to the file
        content: Python source code

    Returns:
        List of security issues found
    """
    issues = []

    try:
        # Create temporary file for bandit
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            temp_path = f.name

        # Run bandit
        result = subprocess.run(
            ['bandit', '-f', 'json', '-q', temp_path],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Parse results
        if result.stdout:
            try:
                bandit_results = json.loads(result.stdout)
                for issue in bandit_results.get('results', []):
                    severity = Severity.MEDIUM
                    if issue.get('issue_severity') == 'HIGH':
                        severity = Severity.HIGH
                    elif issue.get('issue_severity') == 'LOW':
                        severity = Severity.LOW

                    confidence = Confidence.MEDIUM
                    if issue.get('issue_confidence') == 'HIGH':
                        confidence = Confidence.HIGH
                    elif issue.get('issue_confidence') == 'LOW':
                        confidence = Confidence.LOW

                    issues.append(SecurityIssue(
                        issue_id=issue.get('test_id', 'UNKNOWN'),
                        title=issue.get('test_name', 'Unknown Issue'),
                        description=issue.get('issue_text', ''),
                        severity=severity,
                        confidence=confidence,
                        file_path=file_path,
                        line_number=issue.get('line_number', 0),
                        code_snippet=issue.get('code', ''),
                        cwe_id=issue.get('issue_cwe', {}).get('id') if isinstance(issue.get('issue_cwe'), dict) else None,
                    ))
            except json.JSONDecodeError:
                pass

        # Clean up temp file
        Path(temp_path).unlink(missing_ok=True)

    except subprocess.TimeoutExpired:
        pass
    except FileNotFoundError:
        # Bandit not installed, fall back to pattern matching
        pass
    except Exception:
        pass

    return issues


def run_pattern_analysis(content: str, file_path: str, language: str) -> List[SecurityIssue]:
    """
    Run pattern-based security analysis.

    Args:
        content: Source code content
        file_path: Path to the file
        language: Programming language

    Returns:
        List of security issues found
    """
    issues = []
    patterns = SECURITY_PATTERNS.get(language, [])

    lines = content.splitlines()

    for pattern_def in patterns:
        pattern = re.compile(pattern_def["pattern"], re.IGNORECASE | re.MULTILINE)

        for i, line in enumerate(lines, 1):
            if pattern.search(line):
                issues.append(SecurityIssue(
                    issue_id=pattern_def["id"],
                    title=pattern_def["title"],
                    description=pattern_def["description"],
                    severity=pattern_def["severity"],
                    confidence=Confidence.MEDIUM,
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip()[:100],
                    cwe_id=pattern_def.get("cwe"),
                    recommendation=pattern_def.get("recommendation", ""),
                ))

    return issues


def analyze_file_security(file_info: FileInfo) -> FileSecurityAnalysis:
    """
    Analyze security vulnerabilities in a file.

    Args:
        file_info: FileInfo object with file content

    Returns:
        FileSecurityAnalysis with results
    """
    language = get_language_from_extension(file_info.extension) or "unknown"

    result = FileSecurityAnalysis(
        path=file_info.relative_path,
        language=language,
    )

    try:
        issues = []

        # Run pattern-based analysis
        issues.extend(run_pattern_analysis(
            file_info.content,
            file_info.relative_path,
            language
        ))

        # Run Bandit for Python files
        if language == "python":
            bandit_issues = run_bandit_analysis(
                file_info.relative_path,
                file_info.content
            )
            # Merge and deduplicate
            existing_lines = {(i.line_number, i.issue_id) for i in issues}
            for issue in bandit_issues:
                if (issue.line_number, issue.issue_id) not in existing_lines:
                    issues.append(issue)

        result.issues = issues

        # Count by severity
        for issue in issues:
            sev = issue.severity.value
            result.issues_by_severity[sev] = result.issues_by_severity.get(sev, 0) + 1

    except Exception as e:
        result.scan_error = str(e)

    return result


def get_security_summary(analyses: List[FileSecurityAnalysis]) -> Dict[str, Any]:
    """
    Generate a summary of security findings across all files.

    Args:
        analyses: List of FileSecurityAnalysis results

    Returns:
        Summary dictionary
    """
    all_issues = []
    severity_totals = {s.value: 0 for s in Severity}
    files_with_issues = 0

    for analysis in analyses:
        if analysis.issues:
            files_with_issues += 1
            all_issues.extend(analysis.issues)

            for sev, count in analysis.issues_by_severity.items():
                severity_totals[sev] += count

    # Group issues by type
    issues_by_type: Dict[str, List[SecurityIssue]] = {}
    for issue in all_issues:
        if issue.issue_id not in issues_by_type:
            issues_by_type[issue.issue_id] = []
        issues_by_type[issue.issue_id].append(issue)

    # Get top issues
    top_issues = sorted(
        all_issues,
        key=lambda x: (
            {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(x.severity.value, 4),
            {"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(x.confidence.value, 3)
        )
    )[:30]

    return {
        "total_issues": len(all_issues),
        "files_with_issues": files_with_issues,
        "files_scanned": len(analyses),
        "severity_breakdown": severity_totals,
        "issues_by_type": {
            k: {"count": len(v), "severity": v[0].severity.value if v else "UNKNOWN"}
            for k, v in issues_by_type.items()
        },
        "top_issues": [
            {
                "id": i.issue_id,
                "title": i.title,
                "severity": i.severity.value,
                "file": i.file_path,
                "line": i.line_number,
                "description": i.description,
                "recommendation": i.recommendation,
                "cwe": i.cwe_id,
            }
            for i in top_issues
        ],
        "critical_count": severity_totals.get("CRITICAL", 0),
        "high_count": severity_totals.get("HIGH", 0),
        "medium_count": severity_totals.get("MEDIUM", 0),
        "low_count": severity_totals.get("LOW", 0),
    }
