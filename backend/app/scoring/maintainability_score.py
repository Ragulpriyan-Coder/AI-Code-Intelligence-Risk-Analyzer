"""
Maintainability score calculator.
Computes deterministic maintainability score from analysis results.
"""
from typing import Dict, Any, List
from dataclasses import dataclass

from app.analyzers.complexity import FileComplexity
from app.analyzers.maintainability import FileMaintainability


@dataclass
class MaintainabilityScoreResult:
    """Result of maintainability score calculation."""
    score: float  # 0-100
    grade: str  # A, B, C, D, F
    breakdown: Dict[str, float]
    problem_areas: List[Dict]
    summary: str


# Component weights for final score
COMPONENT_WEIGHTS = {
    "maintainability_index": 0.30,
    "complexity": 0.25,
    "documentation": 0.20,
    "readability": 0.15,
    "consistency": 0.10,
}

# Grade thresholds
GRADE_THRESHOLDS = {
    "A": 85,
    "B": 70,
    "C": 55,
    "D": 40,
    "F": 0,
}


def calculate_maintainability_score(
    complexities: List[FileComplexity],
    maintainabilities: List[FileMaintainability]
) -> MaintainabilityScoreResult:
    """
    Calculate maintainability score from analysis results.

    Components:
    - Radon Maintainability Index (30%)
    - Cyclomatic Complexity (25%)
    - Documentation coverage (20%)
    - Readability metrics (15%)
    - Code consistency (10%)

    Args:
        complexities: List of FileComplexity results
        maintainabilities: List of FileMaintainability results

    Returns:
        MaintainabilityScoreResult with calculated score and details
    """
    # Calculate component scores
    mi_score = calculate_mi_component(complexities)
    complexity_score = calculate_complexity_component(complexities)
    documentation_score = calculate_documentation_component(maintainabilities)
    readability_score = calculate_readability_component(maintainabilities)
    consistency_score = calculate_consistency_component(maintainabilities)

    # Calculate weighted final score
    final_score = (
        mi_score * COMPONENT_WEIGHTS["maintainability_index"] +
        complexity_score * COMPONENT_WEIGHTS["complexity"] +
        documentation_score * COMPONENT_WEIGHTS["documentation"] +
        readability_score * COMPONENT_WEIGHTS["readability"] +
        consistency_score * COMPONENT_WEIGHTS["consistency"]
    )

    # Determine grade
    grade = "F"
    for g, threshold in GRADE_THRESHOLDS.items():
        if final_score >= threshold:
            grade = g
            break

    # Identify problem areas
    problem_areas = identify_problem_areas(
        complexities, maintainabilities,
        mi_score, complexity_score, documentation_score
    )

    # Create breakdown
    breakdown = {
        "maintainability_index": round(mi_score, 1),
        "complexity": round(complexity_score, 1),
        "documentation": round(documentation_score, 1),
        "readability": round(readability_score, 1),
        "consistency": round(consistency_score, 1),
    }

    # Generate summary
    summary = generate_maintainability_summary(
        final_score, grade, breakdown, len(complexities)
    )

    return MaintainabilityScoreResult(
        score=round(final_score, 1),
        grade=grade,
        breakdown=breakdown,
        problem_areas=problem_areas,
        summary=summary,
    )


def calculate_mi_component(complexities: List[FileComplexity]) -> float:
    """Calculate score from Radon Maintainability Index."""
    if not complexities:
        return 100.0

    valid_mi = [c.maintainability_index for c in complexities if c.maintainability_index > 0]

    if not valid_mi:
        return 50.0

    avg_mi = sum(valid_mi) / len(valid_mi)

    # MI ranges from 0-100, directly maps to our score
    return max(0.0, min(100.0, avg_mi))


def calculate_complexity_component(complexities: List[FileComplexity]) -> float:
    """Calculate score from cyclomatic complexity."""
    if not complexities:
        return 100.0

    total_complexity = sum(c.total_complexity for c in complexities)
    total_functions = sum(len(c.functions) for c in complexities)

    if total_functions == 0:
        return 100.0

    avg_complexity = total_complexity / total_functions

    # Score mapping:
    # 1-5: 100-90 (simple)
    # 6-10: 90-70 (moderate)
    # 11-20: 70-50 (complex)
    # 21-50: 50-20 (very complex)
    # 50+: 20-0 (extremely complex)

    if avg_complexity <= 5:
        score = 100 - (avg_complexity - 1) * 2.5
    elif avg_complexity <= 10:
        score = 90 - (avg_complexity - 5) * 4
    elif avg_complexity <= 20:
        score = 70 - (avg_complexity - 10) * 2
    elif avg_complexity <= 50:
        score = 50 - (avg_complexity - 20) * 1
    else:
        score = max(0, 20 - (avg_complexity - 50) * 0.4)

    # Penalize for high-complexity functions (> 15)
    high_complexity_count = sum(
        1 for c in complexities
        for f in c.functions
        if f.complexity > 15
    )

    if high_complexity_count > 0:
        penalty = min(high_complexity_count * 3, 20)
        score -= penalty

    return max(0.0, min(100.0, score))


def calculate_documentation_component(maintainabilities: List[FileMaintainability]) -> float:
    """Calculate score from documentation metrics."""
    if not maintainabilities:
        return 100.0

    doc_scores = [m.documentation_score for m in maintainabilities]
    return sum(doc_scores) / len(doc_scores)


def calculate_readability_component(maintainabilities: List[FileMaintainability]) -> float:
    """Calculate score from readability metrics."""
    if not maintainabilities:
        return 100.0

    read_scores = [m.readability_score for m in maintainabilities]
    return sum(read_scores) / len(read_scores)


def calculate_consistency_component(maintainabilities: List[FileMaintainability]) -> float:
    """Calculate score from consistency metrics."""
    if not maintainabilities:
        return 100.0

    cons_scores = [m.consistency_score for m in maintainabilities]
    return sum(cons_scores) / len(cons_scores)


def identify_problem_areas(
    complexities: List[FileComplexity],
    maintainabilities: List[FileMaintainability],
    mi_score: float,
    complexity_score: float,
    documentation_score: float
) -> List[Dict]:
    """Identify specific problem areas in the codebase."""
    problems = []

    # Find complex files
    for complexity in complexities:
        if complexity.average_complexity > 10:
            problems.append({
                "type": "high_complexity",
                "file": complexity.path,
                "metric": f"Average complexity: {complexity.average_complexity:.1f}",
                "recommendation": "Refactor complex functions into smaller units"
            })

        if complexity.maintainability_index < 40:
            problems.append({
                "type": "low_maintainability",
                "file": complexity.path,
                "metric": f"MI: {complexity.maintainability_index:.1f}",
                "recommendation": "Improve code structure and reduce complexity"
            })

    # Find files with poor documentation
    for maint in maintainabilities:
        if maint.documentation_score < 40:
            problems.append({
                "type": "poor_documentation",
                "file": maint.path,
                "metric": f"Documentation score: {maint.documentation_score:.1f}",
                "recommendation": "Add docstrings and improve comments"
            })

        if len(maint.issues) > 5:
            problems.append({
                "type": "code_smells",
                "file": maint.path,
                "metric": f"{len(maint.issues)} issues found",
                "recommendation": "Address code smells and warnings"
            })

    # Sort by severity (approximated by metric values)
    return sorted(problems, key=lambda x: x["metric"])[:15]


def generate_maintainability_summary(
    score: float,
    grade: str,
    breakdown: Dict[str, float],
    file_count: int
) -> str:
    """Generate a human-readable maintainability summary."""
    parts = []

    # Overall assessment
    if grade == "A":
        parts.append("Excellent maintainability.")
    elif grade == "B":
        parts.append("Good maintainability with minor improvements possible.")
    elif grade == "C":
        parts.append("Moderate maintainability. Some refactoring recommended.")
    elif grade == "D":
        parts.append("Below average maintainability. Significant improvements needed.")
    else:
        parts.append("Poor maintainability. Major refactoring required.")

    # Identify weakest areas
    weak_areas = [
        (name, score) for name, score in breakdown.items()
        if score < 60
    ]

    if weak_areas:
        weak_areas.sort(key=lambda x: x[1])
        area_names = [a[0].replace("_", " ") for a in weak_areas[:2]]
        parts.append(f"Focus areas: {', '.join(area_names)}.")

    parts.append(f"Analyzed {file_count} files.")

    return " ".join(parts)
