"""
Technical debt calculator.
Computes technical debt index and refactor urgency from all analysis results.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from app.scoring.security_score import SecurityScoreResult
from app.scoring.maintainability_score import MaintainabilityScoreResult
from app.scoring.architecture_score import ArchitectureScoreResult


class RefactorUrgency(str, Enum):
    """Urgency levels for refactoring."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass
class TechDebtResult:
    """Result of technical debt calculation."""
    index: float  # 0-100 (higher = more debt)
    urgency: RefactorUrgency
    breakdown: Dict[str, float]
    priority_items: List[Dict]
    estimated_effort: str
    summary: str


# Weights for debt calculation
DEBT_WEIGHTS = {
    "security": 0.35,  # Security issues are critical
    "maintainability": 0.30,
    "architecture": 0.25,
    "code_smells": 0.10,
}

# Urgency thresholds (debt index)
URGENCY_THRESHOLDS = {
    RefactorUrgency.LOW: 25,
    RefactorUrgency.MEDIUM: 50,
    RefactorUrgency.HIGH: 75,
    RefactorUrgency.CRITICAL: 100,
}


def calculate_tech_debt(
    security: SecurityScoreResult,
    maintainability: MaintainabilityScoreResult,
    architecture: ArchitectureScoreResult,
    total_lines: int,
    total_files: int
) -> TechDebtResult:
    """
    Calculate technical debt index from all analysis results.

    The debt index represents how much "debt" has accumulated:
    - 0 = No debt (perfect codebase)
    - 100 = Maximum debt (critical state)

    Args:
        security: Security score result
        maintainability: Maintainability score result
        architecture: Architecture score result
        total_lines: Total lines of code
        total_files: Total number of files

    Returns:
        TechDebtResult with debt index and details
    """
    # Convert scores to debt (100 - score)
    security_debt = 100 - security.score
    maintainability_debt = 100 - maintainability.score
    architecture_debt = 100 - architecture.score

    # Calculate code smell debt from maintainability issues
    code_smell_debt = calculate_code_smell_debt(maintainability)

    # Calculate weighted debt index
    debt_index = (
        security_debt * DEBT_WEIGHTS["security"] +
        maintainability_debt * DEBT_WEIGHTS["maintainability"] +
        architecture_debt * DEBT_WEIGHTS["architecture"] +
        code_smell_debt * DEBT_WEIGHTS["code_smells"]
    )

    # Apply size factor (larger codebases with same % debt have more absolute debt)
    size_factor = calculate_size_factor(total_lines, total_files)
    adjusted_debt = debt_index * size_factor

    # Cap at 100
    final_debt = min(100.0, adjusted_debt)

    # Determine urgency
    urgency = determine_urgency(final_debt, security)

    # Get priority items
    priority_items = get_priority_items(security, maintainability, architecture)

    # Calculate breakdown
    breakdown = {
        "security_debt": round(security_debt, 1),
        "maintainability_debt": round(maintainability_debt, 1),
        "architecture_debt": round(architecture_debt, 1),
        "code_smell_debt": round(code_smell_debt, 1),
        "size_factor": round(size_factor, 2),
    }

    # Estimate effort
    estimated_effort = estimate_refactor_effort(final_debt, total_lines)

    # Generate summary
    summary = generate_debt_summary(
        final_debt, urgency, breakdown, priority_items
    )

    return TechDebtResult(
        index=round(final_debt, 1),
        urgency=urgency,
        breakdown=breakdown,
        priority_items=priority_items,
        estimated_effort=estimated_effort,
        summary=summary,
    )


def calculate_code_smell_debt(maintainability: MaintainabilityScoreResult) -> float:
    """Calculate debt from code smell issues."""
    # Count problem areas
    problem_count = len(maintainability.problem_areas)

    if problem_count == 0:
        return 0.0

    # Each problem adds debt, with diminishing returns
    if problem_count <= 5:
        return problem_count * 8
    elif problem_count <= 15:
        return 40 + (problem_count - 5) * 4
    else:
        return 80 + min((problem_count - 15) * 2, 20)


def calculate_size_factor(total_lines: int, total_files: int) -> float:
    """
    Calculate size factor for debt adjustment.
    Larger codebases need more careful management.
    """
    # Base factor is 1.0
    factor = 1.0

    # Small projects (< 1000 lines) get a slight reduction
    if total_lines < 1000:
        factor = 0.9
    # Medium projects (1000-10000 lines) stay at 1.0
    elif total_lines < 10000:
        factor = 1.0
    # Large projects (10000-50000 lines) get slight increase
    elif total_lines < 50000:
        factor = 1.1
    # Very large projects (50000+ lines) get more increase
    else:
        factor = 1.2

    return factor


def determine_urgency(debt_index: float, security: SecurityScoreResult) -> RefactorUrgency:
    """Determine refactor urgency based on debt and critical issues."""
    # Critical security issues always escalate urgency
    if security.risk_level == "Critical":
        return RefactorUrgency.CRITICAL

    if security.risk_level == "High" and debt_index > 40:
        return RefactorUrgency.CRITICAL

    # Standard threshold-based urgency
    if debt_index >= 75:
        return RefactorUrgency.CRITICAL
    elif debt_index >= 50:
        return RefactorUrgency.HIGH
    elif debt_index >= 25:
        return RefactorUrgency.MEDIUM
    else:
        return RefactorUrgency.LOW


def get_priority_items(
    security: SecurityScoreResult,
    maintainability: MaintainabilityScoreResult,
    architecture: ArchitectureScoreResult
) -> List[Dict]:
    """Get prioritized list of items to address."""
    items = []

    # Add security issues (highest priority)
    for risk in security.top_risks[:5]:
        items.append({
            "category": "security",
            "priority": 1 if risk["severity"] in ["CRITICAL", "HIGH"] else 2,
            "title": risk["title"],
            "file": risk.get("file", ""),
            "description": risk.get("description", ""),
            "recommendation": risk.get("recommendation", ""),
        })

    # Add maintainability problems
    for problem in maintainability.problem_areas[:5]:
        items.append({
            "category": "maintainability",
            "priority": 2,
            "title": problem["type"].replace("_", " ").title(),
            "file": problem.get("file", ""),
            "description": problem.get("metric", ""),
            "recommendation": problem.get("recommendation", ""),
        })

    # Add architecture issues
    for issue in architecture.issues[:5]:
        items.append({
            "category": "architecture",
            "priority": 2 if issue["severity"] == "high" else 3,
            "title": issue["title"],
            "file": "",
            "description": issue.get("description", ""),
            "recommendation": issue.get("recommendation", ""),
        })

    # Sort by priority
    items.sort(key=lambda x: x["priority"])

    return items[:15]


def estimate_refactor_effort(debt_index: float, total_lines: int) -> str:
    """
    Estimate the effort required to address technical debt.
    Returns a qualitative assessment, not exact time.
    """
    # Base effort categories
    if debt_index < 15:
        base = "Minimal"
    elif debt_index < 30:
        base = "Light"
    elif debt_index < 50:
        base = "Moderate"
    elif debt_index < 75:
        base = "Significant"
    else:
        base = "Major"

    # Adjust for codebase size
    if total_lines > 50000:
        size_note = "large codebase"
    elif total_lines > 10000:
        size_note = "medium codebase"
    else:
        size_note = "small codebase"

    return f"{base} effort ({size_note})"


def generate_debt_summary(
    debt_index: float,
    urgency: RefactorUrgency,
    breakdown: Dict[str, float],
    priority_items: List[Dict]
) -> str:
    """Generate a human-readable technical debt summary."""
    parts = []

    # Overall assessment
    if urgency == RefactorUrgency.CRITICAL:
        parts.append("CRITICAL: Immediate action required to address technical debt.")
    elif urgency == RefactorUrgency.HIGH:
        parts.append("HIGH: Significant technical debt requiring prompt attention.")
    elif urgency == RefactorUrgency.MEDIUM:
        parts.append("MODERATE: Manageable technical debt. Plan for improvements.")
    else:
        parts.append("LOW: Technical debt is under control.")

    # Identify primary debt source
    debt_sources = [
        ("security", breakdown["security_debt"]),
        ("maintainability", breakdown["maintainability_debt"]),
        ("architecture", breakdown["architecture_debt"]),
    ]
    debt_sources.sort(key=lambda x: x[1], reverse=True)

    if debt_sources[0][1] > 30:
        parts.append(f"Primary concern: {debt_sources[0][0]}.")

    # Priority count
    high_priority = sum(1 for item in priority_items if item["priority"] == 1)
    if high_priority > 0:
        parts.append(f"{high_priority} high-priority items need immediate attention.")

    return " ".join(parts)


def get_overall_health_score(
    security: SecurityScoreResult,
    maintainability: MaintainabilityScoreResult,
    architecture: ArchitectureScoreResult
) -> Dict[str, Any]:
    """
    Calculate an overall code health score combining all metrics.

    Returns:
        Dictionary with overall health metrics
    """
    # Weighted average of scores
    overall = (
        security.score * 0.35 +
        maintainability.score * 0.35 +
        architecture.score * 0.30
    )

    # Determine health status
    if overall >= 80:
        status = "Healthy"
        color = "green"
    elif overall >= 60:
        status = "Fair"
        color = "yellow"
    elif overall >= 40:
        status = "Concerning"
        color = "orange"
    else:
        status = "Critical"
        color = "red"

    return {
        "overall_score": round(overall, 1),
        "status": status,
        "color": color,
        "components": {
            "security": security.score,
            "maintainability": maintainability.score,
            "architecture": architecture.score,
        },
    }
