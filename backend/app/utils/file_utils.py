"""
File utility functions for code analysis.
"""
import os
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field

from app.core.config import settings


@dataclass
class FileInfo:
    """Information about a source code file."""
    path: str
    relative_path: str
    extension: str
    size_bytes: int
    lines: int = 0
    content: str = ""


@dataclass
class ProjectStructure:
    """Structure information about a project."""
    root_path: str
    total_files: int = 0
    total_lines: int = 0
    total_size_bytes: int = 0
    files: List[FileInfo] = field(default_factory=list)
    file_types: Dict[str, int] = field(default_factory=dict)
    directories: List[str] = field(default_factory=list)


# File extensions to analyze by language
LANGUAGE_EXTENSIONS: Dict[str, Set[str]] = {
    "python": {".py", ".pyw"},
    "javascript": {".js", ".mjs", ".cjs"},
    "typescript": {".ts", ".tsx"},
    "java": {".java"},
    "go": {".go"},
    "rust": {".rs"},
    "c": {".c", ".h"},
    "cpp": {".cpp", ".hpp", ".cc", ".hh", ".cxx"},
    "csharp": {".cs"},
    "ruby": {".rb"},
    "php": {".php"},
    "swift": {".swift"},
    "kotlin": {".kt", ".kts"},
}

# Directories to ignore during analysis
IGNORED_DIRECTORIES: Set[str] = {
    "__pycache__",
    "node_modules",
    ".git",
    ".svn",
    ".hg",
    "venv",
    "env",
    ".venv",
    ".env",
    "dist",
    "build",
    "target",
    ".idea",
    ".vscode",
    "vendor",
    "packages",
    ".next",
    ".nuxt",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
    "egg-info",
    ".tox",
}

# Files to ignore
IGNORED_FILES: Set[str] = {
    ".DS_Store",
    "Thumbs.db",
    ".gitignore",
    ".gitattributes",
    "package-lock.json",
    "yarn.lock",
    "poetry.lock",
    "Pipfile.lock",
}


def get_all_extensions() -> Set[str]:
    """Get all supported file extensions."""
    all_extensions = set()
    for extensions in LANGUAGE_EXTENSIONS.values():
        all_extensions.update(extensions)
    return all_extensions


def get_language_from_extension(extension: str) -> Optional[str]:
    """
    Get the programming language from file extension.

    Args:
        extension: File extension (e.g., ".py")

    Returns:
        Language name or None if not recognized
    """
    for language, extensions in LANGUAGE_EXTENSIONS.items():
        if extension.lower() in extensions:
            return language
    return None


def should_ignore_path(path: Path) -> bool:
    """
    Check if a path should be ignored during analysis.

    Args:
        path: Path to check

    Returns:
        True if path should be ignored
    """
    # Check directory names
    for part in path.parts:
        if part in IGNORED_DIRECTORIES:
            return True
        if part.startswith(".") and part not in {"."}:
            # Ignore hidden directories except current dir
            if len(part) > 1:
                return True

    # Check file names
    if path.name in IGNORED_FILES:
        return True

    return False


def is_analyzable_file(file_path: Path) -> bool:
    """
    Check if a file should be analyzed.

    Args:
        file_path: Path to the file

    Returns:
        True if file should be analyzed
    """
    if should_ignore_path(file_path):
        return False

    extension = file_path.suffix.lower()
    return extension in get_all_extensions()


def count_lines(content: str) -> int:
    """
    Count non-empty lines in content.

    Args:
        content: File content

    Returns:
        Number of non-empty lines
    """
    lines = content.splitlines()
    return len([line for line in lines if line.strip()])


def read_file_safe(file_path: Path, max_size_mb: int = 5) -> Optional[str]:
    """
    Safely read a file with size limit.

    Args:
        file_path: Path to the file
        max_size_mb: Maximum file size in MB

    Returns:
        File content or None if file is too large or unreadable
    """
    try:
        size = file_path.stat().st_size
        if size > max_size_mb * 1024 * 1024:
            return None

        # Try different encodings
        encodings = ["utf-8", "latin-1", "cp1252"]
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        return None
    except (IOError, OSError):
        return None


def scan_directory(root_path: str) -> ProjectStructure:
    """
    Scan a directory and collect information about all analyzable files.

    Args:
        root_path: Root directory to scan

    Returns:
        ProjectStructure with all file information
    """
    root = Path(root_path)
    structure = ProjectStructure(root_path=root_path)

    if not root.exists() or not root.is_dir():
        return structure

    seen_dirs: Set[str] = set()

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue

        if not is_analyzable_file(file_path):
            continue

        # Track directories
        rel_dir = str(file_path.parent.relative_to(root))
        if rel_dir not in seen_dirs:
            seen_dirs.add(rel_dir)
            structure.directories.append(rel_dir)

        # Read file content
        content = read_file_safe(file_path)
        if content is None:
            continue

        # Create file info
        extension = file_path.suffix.lower()
        lines = count_lines(content)
        size = file_path.stat().st_size

        file_info = FileInfo(
            path=str(file_path),
            relative_path=str(file_path.relative_to(root)),
            extension=extension,
            size_bytes=size,
            lines=lines,
            content=content,
        )

        structure.files.append(file_info)
        structure.total_files += 1
        structure.total_lines += lines
        structure.total_size_bytes += size

        # Track file types
        structure.file_types[extension] = structure.file_types.get(extension, 0) + 1

    return structure


def get_file_metrics(file_info: FileInfo) -> Dict:
    """
    Get basic metrics for a single file.

    Args:
        file_info: FileInfo object

    Returns:
        Dictionary of metrics
    """
    content = file_info.content
    lines = content.splitlines()

    total_lines = len(lines)
    empty_lines = len([l for l in lines if not l.strip()])
    comment_lines = 0

    # Basic comment detection
    language = get_language_from_extension(file_info.extension)

    if language in {"python", "ruby", "php"}:
        comment_lines = len([l for l in lines if l.strip().startswith("#")])
    elif language in {"javascript", "typescript", "java", "go", "rust", "c", "cpp", "csharp", "swift", "kotlin"}:
        comment_lines = len([l for l in lines if l.strip().startswith("//") or l.strip().startswith("/*") or l.strip().startswith("*")])

    code_lines = total_lines - empty_lines - comment_lines

    return {
        "path": file_info.relative_path,
        "extension": file_info.extension,
        "language": language,
        "total_lines": total_lines,
        "code_lines": max(0, code_lines),
        "empty_lines": empty_lines,
        "comment_lines": comment_lines,
        "size_bytes": file_info.size_bytes,
    }
