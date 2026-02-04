"""
Architecture score calculator.
Computes deterministic architecture score from analysis results.
"""
from typing import Dict, Any, List
from dataclasses import dataclass

from app.analyzers.architecture import ArchitectureAnalysis


@dataclass
class ArchitectureScoreResult:
    """Result of architecture score calculation."""
    score: float  # 0-100
    grade: str  # A, B, C, D, F
    breakdown: Dict[str, float]
    issues: List[Dict]
    summary: str


# Component weights for final score
COMPONENT_WEIGHTS = {
    "modularity": 0.30,
    "organization": 0.25,
    "coupling": 0.25,
    "cohesion": 0.20,
}

# Grade thresholds
GRADE_THRESHOLDS = {
    "A": 85,
    "B": 70,
    "C": 55,
    "D": 40,
    "F": 0,
}


def calculate_architecture_score(
    architecture: ArchitectureAnalysis
) -> ArchitectureScoreResult:
    """
    Calculate architecture score from analysis results.

    Components:
    - Modularity (30%): How well-separated are modules
    - Organization (25%): Project structure quality
    - Coupling (25%): Dependency health
    - Cohesion (20%): Code grouping quality

    Args:
        architecture: ArchitectureAnalysis result

    Returns:
        ArchitectureScoreResult with calculated score and details
    """
    # Get component scores from the analysis
    modularity_score = architecture.modularity_score
    organization_score = architecture.organization_score
    coupling_score = architecture.coupling_score
    cohesion_score = architecture.cohesion_score

    # Apply penalties for specific issues
    issue_penalty = calculate_issue_penalty(architecture)

    # Calculate weighted final score
    base_score = (
        modularity_score * COMPONENT_WEIGHTS["modularity"] +
        organization_score * COMPONENT_WEIGHTS["organization"] +
        coupling_score * COMPONENT_WEIGHTS["coupling"] +
        cohesion_score * COMPONENT_WEIGHTS["cohesion"]
    )

    final_score = max(0.0, base_score - issue_penalty)

    # Determine grade
    grade = "F"
    for g, threshold in GRADE_THRESHOLDS.items():
        if final_score >= threshold:
            grade = g
            break

    # Format issues for output
    formatted_issues = [
        {
            "type": issue.issue_type,
            "severity": issue.severity,
            "title": issue.title,
            "description": issue.description,
            "recommendation": issue.recommendation,
        }
        for issue in architecture.issues
    ]

    # Create breakdown
    breakdown = {
        "modularity": round(modularity_score, 1),
        "organization": round(organization_score, 1),
        "coupling": round(coupling_score, 1),
        "cohesion": round(cohesion_score, 1),
        "issue_penalty": round(issue_penalty, 1),
    }

    # Generate summary
    summary = generate_architecture_summary(
        final_score, grade, architecture, breakdown
    )

    return ArchitectureScoreResult(
        score=round(final_score, 1),
        grade=grade,
        breakdown=breakdown,
        issues=formatted_issues,
        summary=summary,
    )


def calculate_issue_penalty(architecture: ArchitectureAnalysis) -> float:
    """Calculate penalty based on architectural issues."""
    penalty = 0.0

    severity_weights = {
        "high": 8,
        "medium": 4,
        "low": 2,
    }

    for issue in architecture.issues:
        penalty += severity_weights.get(issue.severity, 2)

    # Additional penalties for specific patterns
    if architecture.circular_dependencies:
        penalty += len(architecture.circular_dependencies) * 3

    if architecture.layer_violations:
        penalty += len(architecture.layer_violations) * 2

    if len(architecture.hub_modules) > 3:
        penalty += (len(architecture.hub_modules) - 3) * 2

    return min(penalty, 40)  # Cap penalty at 40 points


def generate_architecture_summary(
    score: float,
    grade: str,
    architecture: ArchitectureAnalysis,
    breakdown: Dict[str, float]
) -> str:
    """Generate a human-readable architecture summary."""
    parts = []

    # Overall assessment
    if grade == "A":
        parts.append("Excellent architecture.")
    elif grade == "B":
        parts.append("Good architecture with minor concerns.")
    elif grade == "C":
        parts.append("Acceptable architecture. Some improvements recommended.")
    elif grade == "D":
        parts.append("Problematic architecture. Restructuring recommended.")
    else:
        parts.append("Poor architecture. Major restructuring needed.")

    # Key metrics
    parts.append(f"{architecture.total_modules} modules in {architecture.total_packages} packages.")

    # Highlight issues
    if architecture.circular_dependencies:
        parts.append(f"{len(architecture.circular_dependencies)} circular dependencies found.")

    if architecture.hub_modules:
        parts.append(f"{len(architecture.hub_modules)} hub modules identified (potential god objects).")

    # Weakest component
    components = {k: v for k, v in breakdown.items() if k != "issue_penalty"}
    if components:
        weakest = min(components.items(), key=lambda x: x[1])
        if weakest[1] < 60:
            parts.append(f"Focus area: {weakest[0]}.")

    return " ".join(parts)
