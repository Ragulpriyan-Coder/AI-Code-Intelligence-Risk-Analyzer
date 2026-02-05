"""
Code complexity analyzer using radon and custom metrics.
Analyzes cyclomatic complexity, cognitive complexity, and code metrics.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from radon.complexity import cc_visit, cc_rank
from radon.metrics import h_visit, mi_visit, mi_rank
from radon.raw import analyze

from app.utils.file_utils import FileInfo, get_language_from_extension


@dataclass
class FunctionComplexity:
    """Complexity metrics for a single function."""
    name: str
    line_start: int
    complexity: int
    rank: str  # A, B, C, D, E, F
    is_method: bool = False
    class_name: Optional[str] = None


@dataclass
class FileComplexity:
    """Complexity analysis results for a single file."""
    path: str
    language: str

    # Cyclomatic complexity
    functions: List[FunctionComplexity] = field(default_factory=list)
    average_complexity: float = 0.0
    max_complexity: int = 0
    total_complexity: int = 0

    # Halstead metrics
    halstead_volume: float = 0.0
    halstead_difficulty: float = 0.0
    halstead_effort: float = 0.0
    halstead_bugs: float = 0.0  # Estimated bugs

    # Maintainability Index
    maintainability_index: float = 100.0
    maintainability_rank: str = "A"

    # Raw metrics
    loc: int = 0  # Lines of code
    lloc: int = 0  # Logical lines of code
    sloc: int = 0  # Source lines of code
    comments: int = 0
    multi_line_strings: int = 0
    blank_lines: int = 0

    # Analysis status
    parse_error: Optional[str] = None


def get_complexity_rank_description(rank: str) -> str:
    """Get description for complexity rank."""
    descriptions = {
        "A": "Simple, low risk",
        "B": "Well-structured, moderate complexity",
        "C": "Slightly complex, moderate risk",
        "D": "More complex, higher risk",
        "E": "Complex, high risk",
        "F": "Very complex, very high risk"
    }
    return descriptions.get(rank, "Unknown")


def analyze_python_complexity(content: str, file_path: str) -> FileComplexity:
    """
    Analyze Python code complexity using radon.

    Args:
        content: Python source code
        file_path: Path to the file

    Returns:
        FileComplexity with analysis results
    """
    result = FileComplexity(path=file_path, language="python")

    try:
        # Cyclomatic complexity analysis
        cc_results = cc_visit(content)

        for block in cc_results:
            func_complexity = FunctionComplexity(
                name=block.name,
                line_start=block.lineno,
                complexity=block.complexity,
                rank=cc_rank(block.complexity),
                is_method=block.is_method,
                class_name=block.classname if hasattr(block, 'classname') else None
            )
            result.functions.append(func_complexity)
            result.total_complexity += block.complexity

        if result.functions:
            result.average_complexity = result.total_complexity / len(result.functions)
            result.max_complexity = max(f.complexity for f in result.functions)

        # Halstead metrics
        try:
            h_results = h_visit(content)
            if h_results and hasattr(h_results, 'total'):
                total = h_results.total
                result.halstead_volume = getattr(total, 'volume', 0) or 0
                result.halstead_difficulty = getattr(total, 'difficulty', 0) or 0
                result.halstead_effort = getattr(total, 'effort', 0) or 0
                result.halstead_bugs = getattr(total, 'bugs', 0) or 0
        except (SyntaxError, ValueError, TypeError):
            # Halstead analysis can fail on malformed or complex code
            result.halstead_volume = 0.0

        # Maintainability Index
        try:
            mi_score = mi_visit(content, multi=False)
            result.maintainability_index = mi_score
            result.maintainability_rank = mi_rank(mi_score)
        except (SyntaxError, ValueError, TypeError):
            # Default to moderate maintainability on parse errors
            result.maintainability_index = 50.0
            result.maintainability_rank = "C"

        # Raw metrics
        try:
            raw = analyze(content)
            result.loc = raw.loc
            result.lloc = raw.lloc
            result.sloc = raw.sloc
            result.comments = raw.comments
            result.multi_line_strings = raw.multi
            result.blank_lines = raw.blank
        except (SyntaxError, ValueError):
            # Fallback to basic line counting
            lines = content.splitlines()
            result.loc = len(lines)
            result.sloc = len([l for l in lines if l.strip()])

    except SyntaxError as e:
        result.parse_error = f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        result.parse_error = str(e)

    return result


def analyze_generic_complexity(content: str, file_path: str, language: str) -> FileComplexity:
    """
    Basic complexity analysis for non-Python files.

    Args:
        content: Source code content
        file_path: Path to the file
        language: Programming language

    Returns:
        FileComplexity with basic metrics
    """
    result = FileComplexity(path=file_path, language=language)

    lines = content.splitlines()
    result.loc = len(lines)
    result.sloc = len([l for l in lines if l.strip()])
    result.blank_lines = len([l for l in lines if not l.strip()])

    # Estimate complexity based on control flow keywords
    control_keywords = {
        "javascript": ["if", "else", "for", "while", "switch", "case", "catch", "&&", "||", "?"],
        "typescript": ["if", "else", "for", "while", "switch", "case", "catch", "&&", "||", "?"],
        "java": ["if", "else", "for", "while", "switch", "case", "catch", "&&", "||", "?"],
        "go": ["if", "else", "for", "switch", "case", "select", "&&", "||"],
        "rust": ["if", "else", "for", "while", "match", "loop", "&&", "||", "?"],
    }

    keywords = control_keywords.get(language, ["if", "else", "for", "while"])

    # Simple complexity estimation
    complexity_count = 1  # Base complexity

    for line in lines:
        for keyword in keywords:
            if f" {keyword} " in f" {line} " or line.strip().startswith(keyword):
                complexity_count += 1

    result.total_complexity = complexity_count
    result.average_complexity = complexity_count / max(1, result.sloc / 20)  # Rough estimate

    # Estimate maintainability based on code length and complexity
    mi = 100 - (result.sloc / 50) - (complexity_count * 2)
    result.maintainability_index = max(0, min(100, mi))
    result.maintainability_rank = mi_rank(result.maintainability_index)

    return result


def analyze_file_complexity(file_info: FileInfo) -> FileComplexity:
    """
    Analyze complexity for a file based on its language.

    Args:
        file_info: FileInfo object with file content

    Returns:
        FileComplexity with analysis results
    """
    language = get_language_from_extension(file_info.extension)

    if language == "python":
        return analyze_python_complexity(file_info.content, file_info.relative_path)
    elif language:
        return analyze_generic_complexity(file_info.content, file_info.relative_path, language)
    else:
        return FileComplexity(
            path=file_info.relative_path,
            language="unknown",
            parse_error="Unsupported file type"
        )


def get_complexity_summary(complexities: List[FileComplexity]) -> Dict[str, Any]:
    """
    Generate a summary of complexity across all files.

    Args:
        complexities: List of FileComplexity results

    Returns:
        Summary dictionary
    """
    total_functions = 0
    total_complexity = 0
    high_complexity_functions = []
    maintainability_scores = []

    rank_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}

    for fc in complexities:
        if fc.parse_error:
            continue

        maintainability_scores.append(fc.maintainability_index)

        for func in fc.functions:
            total_functions += 1
            total_complexity += func.complexity
            rank_counts[func.rank] = rank_counts.get(func.rank, 0) + 1

            if func.complexity > 10:  # High complexity threshold
                high_complexity_functions.append({
                    "file": fc.path,
                    "function": func.name,
                    "complexity": func.complexity,
                    "rank": func.rank,
                    "line": func.line_start,
                })

    avg_complexity = total_complexity / total_functions if total_functions > 0 else 0
    avg_maintainability = sum(maintainability_scores) / len(maintainability_scores) if maintainability_scores else 100

    return {
        "total_functions": total_functions,
        "total_complexity": total_complexity,
        "average_complexity": round(avg_complexity, 2),
        "average_maintainability_index": round(avg_maintainability, 2),
        "complexity_distribution": rank_counts,
        "high_complexity_functions": sorted(
            high_complexity_functions,
            key=lambda x: x["complexity"],
            reverse=True
        )[:20],  # Top 20 most complex
        "files_analyzed": len(complexities),
        "files_with_errors": len([c for c in complexities if c.parse_error]),
    }
