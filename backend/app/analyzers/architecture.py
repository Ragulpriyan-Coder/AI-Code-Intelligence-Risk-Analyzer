"""
Architecture analyzer for code structure and design patterns.
Analyzes project organization, dependencies, and architectural patterns.
"""
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict
import re

from app.utils.file_utils import ProjectStructure, FileInfo, get_language_from_extension
from app.utils.graph_utils import (
    create_dependency_graph,
    analyze_graph,
    calculate_modularity_score,
    find_circular_dependencies,
    identify_architectural_layers,
    GraphMetrics,
)
from app.analyzers.structure import FileStructure, get_dependency_map


@dataclass
class ArchitecturalIssue:
    """An architectural issue or anti-pattern."""
    issue_type: str
    severity: str  # "low", "medium", "high"
    title: str
    description: str
    affected_files: List[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class ArchitectureAnalysis:
    """Complete architecture analysis results."""
    # Project structure
    total_modules: int = 0
    total_packages: int = 0
    max_depth: int = 0
    directory_structure: Dict[str, int] = field(default_factory=dict)

    # Dependency analysis
    dependency_graph_metrics: Optional[GraphMetrics] = None
    modularity_score: float = 100.0
    circular_dependencies: List[tuple] = field(default_factory=list)
    hub_modules: List[str] = field(default_factory=list)  # Highly connected modules

    # Architectural layers
    identified_layers: Dict[str, List[str]] = field(default_factory=dict)
    layer_violations: List[Dict] = field(default_factory=list)

    # Code organization
    file_type_distribution: Dict[str, int] = field(default_factory=dict)
    avg_module_size: float = 0.0
    large_modules: List[Dict] = field(default_factory=list)

    # Issues found
    issues: List[ArchitecturalIssue] = field(default_factory=list)

    # Overall assessment
    organization_score: float = 100.0
    coupling_score: float = 100.0
    cohesion_score: float = 100.0


# Common architectural patterns and their indicators
ARCHITECTURAL_PATTERNS = {
    "mvc": {
        "indicators": ["models", "views", "controllers", "model", "view", "controller"],
        "description": "Model-View-Controller pattern"
    },
    "mvvm": {
        "indicators": ["models", "views", "viewmodels", "viewmodel"],
        "description": "Model-View-ViewModel pattern"
    },
    "layered": {
        "indicators": ["presentation", "business", "data", "domain", "infrastructure", "application"],
        "description": "Layered/N-Tier architecture"
    },
    "hexagonal": {
        "indicators": ["adapters", "ports", "domain", "application", "infrastructure"],
        "description": "Hexagonal/Ports and Adapters architecture"
    },
    "microservices": {
        "indicators": ["services", "api", "gateway"],
        "description": "Microservices-like structure"
    },
}

# Anti-patterns to detect
ANTI_PATTERNS = {
    "god_module": {
        "description": "Module with too many responsibilities",
        "threshold": {"lines": 1000, "classes": 10, "functions": 50}
    },
    "circular_dependency": {
        "description": "Modules that depend on each other in a cycle"
    },
    "deep_nesting": {
        "description": "Excessively deep directory nesting",
        "threshold": 6
    },
    "scattered_config": {
        "description": "Configuration files scattered across the project"
    },
}


def analyze_directory_structure(project: ProjectStructure) -> Dict[str, Any]:
    """
    Analyze the directory structure of a project.

    Args:
        project: ProjectStructure object

    Returns:
        Analysis results
    """
    structure = defaultdict(int)
    depths = []

    for directory in project.directories:
        depth = directory.count("/") + directory.count("\\")
        depths.append(depth)

        # Get top-level directory
        parts = Path(directory).parts
        if parts:
            structure[parts[0]] += 1

    return {
        "top_level_dirs": dict(structure),
        "max_depth": max(depths) if depths else 0,
        "avg_depth": sum(depths) / len(depths) if depths else 0,
        "total_directories": len(project.directories),
    }


def detect_architectural_pattern(project: ProjectStructure) -> Optional[str]:
    """
    Attempt to detect the architectural pattern used.

    Args:
        project: ProjectStructure object

    Returns:
        Detected pattern name or None
    """
    dir_names = set()
    for directory in project.directories:
        parts = Path(directory).parts
        for part in parts:
            dir_names.add(part.lower())

    for pattern_name, pattern_info in ARCHITECTURAL_PATTERNS.items():
        matches = sum(1 for ind in pattern_info["indicators"] if ind in dir_names)
        if matches >= 2:  # At least 2 matching indicators
            return pattern_name

    return None


def find_god_modules(
    structures: List[FileStructure],
    complexity_data: Optional[Dict] = None
) -> List[Dict]:
    """
    Find modules that are too large or have too many responsibilities.

    Args:
        structures: List of FileStructure objects
        complexity_data: Optional complexity analysis data

    Returns:
        List of god module findings
    """
    god_modules = []

    thresholds = ANTI_PATTERNS["god_module"]["threshold"]

    for structure in structures:
        issues = []

        if structure.total_lines > thresholds["lines"]:
            issues.append(f"Too many lines ({structure.total_lines})")

        if len(structure.classes) > thresholds["classes"]:
            issues.append(f"Too many classes ({len(structure.classes)})")

        if len(structure.functions) > thresholds["functions"]:
            issues.append(f"Too many functions ({len(structure.functions)})")

        if issues:
            god_modules.append({
                "file": structure.path,
                "lines": structure.total_lines,
                "classes": len(structure.classes),
                "functions": len(structure.functions),
                "issues": issues,
            })

    return sorted(god_modules, key=lambda x: x["lines"], reverse=True)


def analyze_coupling(dependency_map: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Analyze coupling between modules.

    Args:
        dependency_map: Map of module dependencies

    Returns:
        Coupling analysis results
    """
    # Create and analyze dependency graph
    graph = create_dependency_graph(dependency_map)
    metrics = analyze_graph(graph)

    # Find circular dependencies
    circular = find_circular_dependencies(graph)

    # Calculate coupling score
    modularity = calculate_modularity_score(graph)

    # Identify potential layers
    layers = identify_architectural_layers(graph)

    return {
        "graph_metrics": metrics,
        "modularity_score": modularity,
        "circular_dependencies": circular,
        "layers": layers,
    }


def detect_layer_violations(
    dependency_map: Dict[str, List[str]],
    layers: Dict[str, List[str]]
) -> List[Dict]:
    """
    Detect violations of layer boundaries.

    Args:
        dependency_map: Map of module dependencies
        layers: Identified architectural layers

    Returns:
        List of layer violation findings
    """
    violations = []

    # Build reverse layer mapping
    module_to_layer = {}
    for layer_name, modules in layers.items():
        for module in modules:
            module_to_layer[module] = layer_name

    # Layer dependency rules (what each layer can depend on)
    allowed_deps = {
        "presentation": {"business", "utility"},
        "business": {"data", "utility"},
        "data": {"utility"},
        "utility": set(),
    }

    for module, deps in dependency_map.items():
        module_layer = module_to_layer.get(module)
        if not module_layer:
            continue

        allowed = allowed_deps.get(module_layer, set())

        for dep in deps:
            dep_layer = module_to_layer.get(dep)
            if dep_layer and dep_layer != module_layer and dep_layer not in allowed:
                violations.append({
                    "source_module": module,
                    "source_layer": module_layer,
                    "target_module": dep,
                    "target_layer": dep_layer,
                    "message": f"{module_layer} should not depend on {dep_layer}",
                })

    return violations


def analyze_architecture(
    project: ProjectStructure,
    structures: List[FileStructure]
) -> ArchitectureAnalysis:
    """
    Perform complete architecture analysis.

    Args:
        project: ProjectStructure object
        structures: List of FileStructure objects

    Returns:
        ArchitectureAnalysis with complete results
    """
    analysis = ArchitectureAnalysis()

    # Analyze directory structure
    dir_analysis = analyze_directory_structure(project)
    analysis.total_packages = dir_analysis["total_directories"]
    analysis.max_depth = dir_analysis["max_depth"]
    analysis.directory_structure = dir_analysis["top_level_dirs"]

    # File statistics
    analysis.total_modules = project.total_files
    analysis.file_type_distribution = project.file_types

    if project.total_files > 0:
        analysis.avg_module_size = project.total_lines / project.total_files

    # Find large modules
    large_threshold = 500  # lines
    analysis.large_modules = [
        {"file": f.relative_path, "lines": f.lines}
        for f in project.files
        if f.lines > large_threshold
    ]

    # Dependency and coupling analysis
    dependency_map = get_dependency_map(structures)

    if dependency_map:
        coupling_analysis = analyze_coupling(dependency_map)

        analysis.dependency_graph_metrics = coupling_analysis["graph_metrics"]
        analysis.modularity_score = coupling_analysis["modularity_score"]
        analysis.circular_dependencies = coupling_analysis["circular_dependencies"]
        analysis.identified_layers = coupling_analysis["layers"]

        if coupling_analysis["graph_metrics"]:
            analysis.hub_modules = coupling_analysis["graph_metrics"].hub_nodes

        # Detect layer violations
        analysis.layer_violations = detect_layer_violations(
            dependency_map,
            analysis.identified_layers
        )

    # Find god modules
    god_modules = find_god_modules(structures)
    for gm in god_modules:
        analysis.issues.append(ArchitecturalIssue(
            issue_type="god_module",
            severity="high",
            title=f"God Module: {gm['file']}",
            description=", ".join(gm["issues"]),
            affected_files=[gm["file"]],
            recommendation="Split this module into smaller, focused modules"
        ))

    # Report circular dependencies
    for dep in analysis.circular_dependencies:
        analysis.issues.append(ArchitecturalIssue(
            issue_type="circular_dependency",
            severity="medium",
            title="Circular Dependency",
            description=f"Circular dependency between {dep[0]} and {dep[1]}",
            affected_files=list(dep),
            recommendation="Refactor to break the dependency cycle"
        ))

    # Check for deep nesting
    if analysis.max_depth > ANTI_PATTERNS["deep_nesting"]["threshold"]:
        analysis.issues.append(ArchitecturalIssue(
            issue_type="deep_nesting",
            severity="low",
            title="Deep Directory Nesting",
            description=f"Project has {analysis.max_depth} levels of nesting",
            recommendation="Consider flattening the directory structure"
        ))

    # Calculate scores
    analysis.organization_score = calculate_organization_score(analysis)
    analysis.coupling_score = analysis.modularity_score
    analysis.cohesion_score = calculate_cohesion_score(analysis, structures)

    return analysis


def calculate_organization_score(analysis: ArchitectureAnalysis) -> float:
    """
    Calculate organization score based on project structure.

    Args:
        analysis: ArchitectureAnalysis object

    Returns:
        Score between 0 and 100
    """
    score = 100.0

    # Penalize deep nesting
    if analysis.max_depth > 5:
        score -= (analysis.max_depth - 5) * 5

    # Penalize large modules
    large_module_penalty = min(len(analysis.large_modules) * 3, 20)
    score -= large_module_penalty

    # Penalize god modules
    god_module_count = sum(1 for i in analysis.issues if i.issue_type == "god_module")
    score -= god_module_count * 10

    return max(0.0, min(100.0, score))


def calculate_cohesion_score(
    analysis: ArchitectureAnalysis,
    structures: List[FileStructure]
) -> float:
    """
    Calculate cohesion score based on code organization.

    Args:
        analysis: ArchitectureAnalysis object
        structures: List of FileStructure objects

    Returns:
        Score between 0 and 100
    """
    score = 100.0

    # Penalize scattered functionality (many small files)
    if analysis.total_modules > 0:
        avg_size = analysis.avg_module_size
        if avg_size < 50:  # Very small modules might indicate poor cohesion
            score -= (50 - avg_size) * 0.5

    # Reward clear layer separation
    layers_with_content = sum(1 for modules in analysis.identified_layers.values() if modules)
    if layers_with_content >= 3:
        score += 10

    # Penalize layer violations
    violation_penalty = min(len(analysis.layer_violations) * 5, 30)
    score -= violation_penalty

    return max(0.0, min(100.0, score))


def get_architecture_summary(analysis: ArchitectureAnalysis) -> Dict[str, Any]:
    """
    Generate a summary of architecture analysis.

    Args:
        analysis: ArchitectureAnalysis object

    Returns:
        Summary dictionary
    """
    return {
        "total_modules": analysis.total_modules,
        "total_packages": analysis.total_packages,
        "max_nesting_depth": analysis.max_depth,
        "avg_module_size": round(analysis.avg_module_size, 1),
        "modularity_score": round(analysis.modularity_score, 1),
        "organization_score": round(analysis.organization_score, 1),
        "coupling_score": round(analysis.coupling_score, 1),
        "cohesion_score": round(analysis.cohesion_score, 1),
        "circular_dependencies_count": len(analysis.circular_dependencies),
        "hub_modules": analysis.hub_modules[:5],
        "large_modules_count": len(analysis.large_modules),
        "layer_violations_count": len(analysis.layer_violations),
        "issues_count": len(analysis.issues),
        "issues_by_severity": {
            "high": sum(1 for i in analysis.issues if i.severity == "high"),
            "medium": sum(1 for i in analysis.issues if i.severity == "medium"),
            "low": sum(1 for i in analysis.issues if i.severity == "low"),
        },
        "top_issues": [
            {
                "type": i.issue_type,
                "severity": i.severity,
                "title": i.title,
                "description": i.description,
                "recommendation": i.recommendation,
            }
            for i in sorted(
                analysis.issues,
                key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.severity, 3)
            )[:10]
        ],
    }
