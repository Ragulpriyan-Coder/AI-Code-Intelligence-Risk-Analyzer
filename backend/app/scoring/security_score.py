"""
Security score calculator.
Computes deterministic security score from static analysis results.
"""
from typing import Dict, Any, List
from dataclasses import dataclass

from app.analyzers.security import FileSecurityAnalysis, Severity


@dataclass
class SecurityScoreResult:
    """Result of security score calculation."""
    score: float  # 0-100
    grade: str  # A, B, C, D, F
    risk_level: str  # Low, Medium, High, Critical
    breakdown: Dict[str, float]
    top_risks: List[Dict]
    summary: str


# Severity weights for score calculation
SEVERITY_WEIGHTS = {
    Severity.CRITICAL.value: 25,
    Severity.HIGH.value: 15,
    Severity.MEDIUM.value: 8,
    Severity.LOW.value: 3,
}

# Score thresholds for grades
GRADE_THRESHOLDS = {
    "A": 90,
    "B": 80,
    "C": 70,
    "D": 60,
    "F": 0,
}

# Risk level thresholds
RISK_THRESHOLDS = {
    "Low": 80,
    "Medium": 60,
    "High": 40,
    "Critical": 0,
}


def calculate_security_score(
    analyses: List[FileSecurityAnalysis],
    total_files: int
) -> SecurityScoreResult:
    """
    Calculate security score from analysis results.

    The score is calculated as:
    - Start with 100 points
    - Deduct points based on severity and count of issues
    - Apply diminishing returns for many issues
    - Consider the ratio of affected files

    Args:
        analyses: List of FileSecurityAnalysis results
        total_files: Total number of files in the project

    Returns:
        SecurityScoreResult with calculated score and details
    """
    # Count issues by severity
    severity_counts = {
        Severity.CRITICAL.value: 0,
        Severity.HIGH.value: 0,
        Severity.MEDIUM.value: 0,
        Severity.LOW.value: 0,
    }

    all_issues = []
    files_with_issues = 0

    for analysis in analyses:
        if analysis.issues:
            files_with_issues += 1
            for issue in analysis.issues:
                severity_counts[issue.severity.value] += 1
                all_issues.append({
                    "id": issue.issue_id,
                    "title": issue.title,
                    "severity": issue.severity.value,
                    "file": issue.file_path,
                    "line": issue.line_number,
                    "description": issue.description,
                    "recommendation": issue.recommendation,
                    "cwe": issue.cwe_id,
                })

    # Calculate base deductions
    deductions = 0.0

    for severity, count in severity_counts.items():
        weight = SEVERITY_WEIGHTS.get(severity, 5)
        # Apply diminishing returns: sqrt for counts > 3
        if count <= 3:
            deductions += count * weight
        else:
            deductions += 3 * weight + (count - 3) ** 0.7 * weight

    # File spread factor (more files affected = worse)
    if total_files > 0:
        spread_factor = files_with_issues / total_files
        # If more than 20% of files have issues, apply additional penalty
        if spread_factor > 0.2:
            deductions *= 1 + (spread_factor - 0.2)

    # Calculate final score
    score = max(0.0, min(100.0, 100.0 - deductions))

    # Determine grade
    grade = "F"
    for g, threshold in GRADE_THRESHOLDS.items():
        if score >= threshold:
            grade = g
            break

    # Determine risk level
    risk_level = "Critical"
    for level, threshold in RISK_THRESHOLDS.items():
        if score >= threshold:
            risk_level = level
            break

    # Get top risks (sorted by severity, then by count)
    top_risks = sorted(
        all_issues,
        key=lambda x: (
            {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(x["severity"], 4),
        )
    )[:10]

    # Calculate breakdown
    breakdown = {
        "critical_issues_impact": min(severity_counts[Severity.CRITICAL.value] * SEVERITY_WEIGHTS[Severity.CRITICAL.value], 40),
        "high_issues_impact": min(severity_counts[Severity.HIGH.value] * SEVERITY_WEIGHTS[Severity.HIGH.value], 30),
        "medium_issues_impact": min(severity_counts[Severity.MEDIUM.value] * SEVERITY_WEIGHTS[Severity.MEDIUM.value], 20),
        "low_issues_impact": min(severity_counts[Severity.LOW.value] * SEVERITY_WEIGHTS[Severity.LOW.value], 10),
        "files_affected_ratio": round(files_with_issues / max(1, total_files) * 100, 1),
    }

    # Generate summary
    summary = generate_security_summary(
        score, grade, risk_level,
        severity_counts, files_with_issues, total_files
    )

    return SecurityScoreResult(
        score=round(score, 1),
        grade=grade,
        risk_level=risk_level,
        breakdown=breakdown,
        top_risks=top_risks,
        summary=summary,
    )


def generate_security_summary(
    score: float,
    grade: str,
    risk_level: str,
    severity_counts: Dict[str, int],
    files_with_issues: int,
    total_files: int
) -> str:
    """Generate a human-readable security summary."""
    total_issues = sum(severity_counts.values())

    if total_issues == 0:
        return "No security issues detected. The codebase appears to follow security best practices."

    parts = []

    # Overall assessment
    if risk_level == "Critical":
        parts.append("CRITICAL: Immediate attention required.")
    elif risk_level == "High":
        parts.append("HIGH RISK: Significant security concerns found.")
    elif risk_level == "Medium":
        parts.append("MODERATE RISK: Some security issues need attention.")
    else:
        parts.append("LOW RISK: Minor security issues detected.")

    # Issue counts
    issue_parts = []
    if severity_counts.get(Severity.CRITICAL.value, 0) > 0:
        issue_parts.append(f"{severity_counts[Severity.CRITICAL.value]} critical")
    if severity_counts.get(Severity.HIGH.value, 0) > 0:
        issue_parts.append(f"{severity_counts[Severity.HIGH.value]} high")
    if severity_counts.get(Severity.MEDIUM.value, 0) > 0:
        issue_parts.append(f"{severity_counts[Severity.MEDIUM.value]} medium")
    if severity_counts.get(Severity.LOW.value, 0) > 0:
        issue_parts.append(f"{severity_counts[Severity.LOW.value]} low")

    parts.append(f"Found {total_issues} issues ({', '.join(issue_parts)}) across {files_with_issues} files.")

    return " ".join(parts)
