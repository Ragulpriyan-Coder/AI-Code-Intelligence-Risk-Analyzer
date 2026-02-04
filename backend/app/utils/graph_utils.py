"""
Graph utilities for dependency and architecture analysis.
"""
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
import networkx as nx


@dataclass
class DependencyNode:
    """Represents a module/file in the dependency graph."""
    name: str
    file_path: str
    node_type: str = "module"  # module, class, function
    imports: List[str] = field(default_factory=list)
    imported_by: List[str] = field(default_factory=list)


@dataclass
class GraphMetrics:
    """Metrics calculated from a dependency graph."""
    total_nodes: int = 0
    total_edges: int = 0
    avg_degree: float = 0.0
    max_in_degree: int = 0
    max_out_degree: int = 0
    density: float = 0.0
    is_cyclic: bool = False
    cycles: List[List[str]] = field(default_factory=list)
    strongly_connected_components: int = 0
    hub_nodes: List[str] = field(default_factory=list)  # Nodes with high connectivity
    isolated_nodes: List[str] = field(default_factory=list)  # Nodes with no connections


def create_dependency_graph(dependencies: Dict[str, List[str]]) -> nx.DiGraph:
    """
    Create a directed graph from dependencies.

    Args:
        dependencies: Dict mapping module names to list of imports

    Returns:
        NetworkX directed graph
    """
    graph = nx.DiGraph()

    for module, imports in dependencies.items():
        graph.add_node(module)
        for imp in imports:
            graph.add_edge(module, imp)

    return graph


def analyze_graph(graph: nx.DiGraph) -> GraphMetrics:
    """
    Analyze a dependency graph and compute metrics.

    Args:
        graph: NetworkX directed graph

    Returns:
        GraphMetrics with computed values
    """
    metrics = GraphMetrics()

    if graph.number_of_nodes() == 0:
        return metrics

    metrics.total_nodes = graph.number_of_nodes()
    metrics.total_edges = graph.number_of_edges()

    # Calculate degree statistics
    in_degrees = dict(graph.in_degree())
    out_degrees = dict(graph.out_degree())

    if in_degrees:
        metrics.max_in_degree = max(in_degrees.values())
    if out_degrees:
        metrics.max_out_degree = max(out_degrees.values())

    total_degree = sum(in_degrees.values()) + sum(out_degrees.values())
    metrics.avg_degree = total_degree / (2 * metrics.total_nodes) if metrics.total_nodes > 0 else 0

    # Calculate density
    metrics.density = nx.density(graph)

    # Check for cycles
    try:
        cycles = list(nx.simple_cycles(graph))
        metrics.is_cyclic = len(cycles) > 0
        metrics.cycles = cycles[:10]  # Limit to first 10 cycles
    except Exception:
        metrics.is_cyclic = False

    # Find strongly connected components
    sccs = list(nx.strongly_connected_components(graph))
    metrics.strongly_connected_components = len(sccs)

    # Find hub nodes (high connectivity)
    degree_threshold = metrics.avg_degree * 2
    for node in graph.nodes():
        degree = in_degrees.get(node, 0) + out_degrees.get(node, 0)
        if degree >= degree_threshold and degree > 3:
            metrics.hub_nodes.append(node)

    # Find isolated nodes
    for node in graph.nodes():
        if in_degrees.get(node, 0) == 0 and out_degrees.get(node, 0) == 0:
            metrics.isolated_nodes.append(node)

    return metrics


def find_circular_dependencies(graph: nx.DiGraph) -> List[Tuple[str, str]]:
    """
    Find all circular dependencies (bidirectional edges).

    Args:
        graph: NetworkX directed graph

    Returns:
        List of tuples representing circular dependencies
    """
    circular = []

    for u, v in graph.edges():
        if graph.has_edge(v, u) and (v, u) not in circular:
            circular.append((u, v))

    return circular


def calculate_modularity_score(graph: nx.DiGraph) -> float:
    """
    Calculate a modularity score based on graph structure.
    Higher score = better modular design.

    Args:
        graph: NetworkX directed graph

    Returns:
        Modularity score between 0 and 100
    """
    if graph.number_of_nodes() == 0:
        return 100.0

    metrics = analyze_graph(graph)

    score = 100.0

    # Penalize high density (tightly coupled)
    if metrics.density > 0.3:
        score -= (metrics.density - 0.3) * 50

    # Penalize cycles
    if metrics.is_cyclic:
        cycle_penalty = min(len(metrics.cycles) * 5, 30)
        score -= cycle_penalty

    # Penalize hub nodes (god modules)
    hub_penalty = min(len(metrics.hub_nodes) * 5, 20)
    score -= hub_penalty

    # Penalize isolated nodes (dead code potential)
    if metrics.total_nodes > 5:
        isolation_ratio = len(metrics.isolated_nodes) / metrics.total_nodes
        if isolation_ratio > 0.2:
            score -= (isolation_ratio - 0.2) * 20

    return max(0.0, min(100.0, score))


def get_dependency_depth(graph: nx.DiGraph) -> Dict[str, int]:
    """
    Calculate the depth of each node in the dependency tree.

    Args:
        graph: NetworkX directed graph

    Returns:
        Dict mapping node names to their depth
    """
    depths: Dict[str, int] = {}

    # Find root nodes (no incoming edges)
    roots = [n for n in graph.nodes() if graph.in_degree(n) == 0]

    for root in roots:
        for node in nx.descendants(graph, root):
            try:
                path_length = nx.shortest_path_length(graph, root, node)
                if node not in depths or path_length > depths[node]:
                    depths[node] = path_length
            except nx.NetworkXNoPath:
                continue

    # Set depth 0 for roots
    for root in roots:
        depths[root] = 0

    return depths


def identify_architectural_layers(graph: nx.DiGraph) -> Dict[str, List[str]]:
    """
    Attempt to identify architectural layers based on dependency structure.

    Args:
        graph: NetworkX directed graph

    Returns:
        Dict with layer names and their modules
    """
    layers: Dict[str, List[str]] = {
        "presentation": [],  # No outgoing deps to other layers
        "business": [],      # Middle layer
        "data": [],          # No incoming deps from other layers
        "utility": [],       # Used by many, uses few
    }

    in_degrees = dict(graph.in_degree())
    out_degrees = dict(graph.out_degree())

    for node in graph.nodes():
        in_deg = in_degrees.get(node, 0)
        out_deg = out_degrees.get(node, 0)

        # Heuristic-based layer assignment
        if in_deg == 0 and out_deg > 0:
            layers["presentation"].append(node)
        elif out_deg == 0 and in_deg > 0:
            layers["data"].append(node)
        elif in_deg > out_deg * 2:
            layers["utility"].append(node)
        else:
            layers["business"].append(node)

    return layers
