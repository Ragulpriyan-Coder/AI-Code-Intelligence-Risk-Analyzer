"""
Code structure analyzer using AST parsing.
Analyzes imports, classes, functions, and overall code organization.
"""
import ast
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

from app.utils.file_utils import FileInfo, get_language_from_extension


@dataclass
class FunctionInfo:
    """Information about a function/method."""
    name: str
    line_start: int
    line_end: int
    args_count: int
    has_docstring: bool
    is_async: bool = False
    decorators: List[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    line_start: int
    line_end: int
    methods_count: int
    has_docstring: bool
    base_classes: List[str] = field(default_factory=list)
    methods: List[FunctionInfo] = field(default_factory=list)


@dataclass
class ImportInfo:
    """Information about an import statement."""
    module: str
    names: List[str] = field(default_factory=list)
    is_from_import: bool = False
    line: int = 0


@dataclass
class FileStructure:
    """Structure analysis results for a single file."""
    path: str
    language: str
    imports: List[ImportInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    global_variables: List[str] = field(default_factory=list)
    total_lines: int = 0
    code_lines: int = 0
    docstring_coverage: float = 0.0
    parse_error: Optional[str] = None


class PythonStructureAnalyzer(ast.NodeVisitor):
    """AST visitor for analyzing Python code structure."""

    def __init__(self):
        self.imports: List[ImportInfo] = []
        self.classes: List[ClassInfo] = []
        self.functions: List[FunctionInfo] = []
        self.global_variables: List[str] = []
        self._current_class: Optional[ClassInfo] = None

    def visit_Import(self, node: ast.Import) -> None:
        """Process import statements."""
        for alias in node.names:
            self.imports.append(ImportInfo(
                module=alias.name,
                names=[alias.asname or alias.name],
                is_from_import=False,
                line=node.lineno
            ))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Process from ... import statements."""
        module = node.module or ""
        names = [alias.name for alias in node.names]
        self.imports.append(ImportInfo(
            module=module,
            names=names,
            is_from_import=True,
            line=node.lineno
        ))
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Process class definitions."""
        # Get base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{self._get_attr_name(base)}")

        # Check for docstring
        has_docstring = (
            node.body and
            isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, (ast.Str, ast.Constant))
        )

        class_info = ClassInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            methods_count=0,
            has_docstring=has_docstring,
            base_classes=bases,
            methods=[]
        )

        # Process methods
        self._current_class = class_info
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method = self._process_function(item)
                class_info.methods.append(method)
                class_info.methods_count += 1

        self._current_class = None
        self.classes.append(class_info)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Process function definitions (top-level only)."""
        if self._current_class is None:
            self.functions.append(self._process_function(node))

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Process async function definitions."""
        if self._current_class is None:
            func = self._process_function(node)
            func.is_async = True
            self.functions.append(func)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Process global variable assignments."""
        if self._current_class is None:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    # Only track uppercase (constants) and module-level vars
                    if target.id.isupper() or not target.id.startswith("_"):
                        self.global_variables.append(target.id)
        self.generic_visit(node)

    def _process_function(self, node) -> FunctionInfo:
        """Extract function information from AST node."""
        # Get decorators
        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(self._get_attr_name(dec))
            elif isinstance(dec, ast.Call):
                if isinstance(dec.func, ast.Name):
                    decorators.append(dec.func.id)

        # Check for docstring
        has_docstring = (
            node.body and
            isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, (ast.Str, ast.Constant))
        )

        # Count arguments
        args_count = len(node.args.args)
        if node.args.vararg:
            args_count += 1
        if node.args.kwarg:
            args_count += 1

        return FunctionInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            args_count=args_count,
            has_docstring=has_docstring,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            decorators=decorators
        )

    def _get_attr_name(self, node: ast.Attribute) -> str:
        """Get full attribute name (e.g., 'module.submodule.attr')."""
        parts = [node.attr]
        current = node.value
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))


def analyze_python_structure(content: str, file_path: str) -> FileStructure:
    """
    Analyze Python code structure using AST.

    Args:
        content: Python source code
        file_path: Path to the file

    Returns:
        FileStructure with analysis results
    """
    structure = FileStructure(path=file_path, language="python")

    try:
        tree = ast.parse(content)
        analyzer = PythonStructureAnalyzer()
        analyzer.visit(tree)

        structure.imports = analyzer.imports
        structure.classes = analyzer.classes
        structure.functions = analyzer.functions
        structure.global_variables = analyzer.global_variables

        # Calculate metrics
        lines = content.splitlines()
        structure.total_lines = len(lines)
        structure.code_lines = len([l for l in lines if l.strip() and not l.strip().startswith("#")])

        # Calculate docstring coverage
        total_items = len(structure.functions) + len(structure.classes)
        items_with_docs = sum(1 for f in structure.functions if f.has_docstring)
        items_with_docs += sum(1 for c in structure.classes if c.has_docstring)

        if total_items > 0:
            structure.docstring_coverage = (items_with_docs / total_items) * 100

    except SyntaxError as e:
        structure.parse_error = f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        structure.parse_error = str(e)

    return structure


def analyze_file_structure(file_info: FileInfo) -> FileStructure:
    """
    Analyze code structure for a file based on its language.

    Args:
        file_info: FileInfo object with file content

    Returns:
        FileStructure with analysis results
    """
    language = get_language_from_extension(file_info.extension)

    if language == "python":
        return analyze_python_structure(file_info.content, file_info.relative_path)

    # For other languages, return basic structure
    # (Full support would require language-specific parsers)
    lines = file_info.content.splitlines()
    return FileStructure(
        path=file_info.relative_path,
        language=language or "unknown",
        total_lines=len(lines),
        code_lines=len([l for l in lines if l.strip()]),
    )


def get_dependency_map(structures: List[FileStructure]) -> Dict[str, List[str]]:
    """
    Build a dependency map from file structures.

    Args:
        structures: List of FileStructure objects

    Returns:
        Dict mapping file paths to their imports
    """
    dependencies = {}

    for structure in structures:
        imports = []
        for imp in structure.imports:
            imports.append(imp.module)
        dependencies[structure.path] = imports

    return dependencies
