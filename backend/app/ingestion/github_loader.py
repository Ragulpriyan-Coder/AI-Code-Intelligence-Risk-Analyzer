"""
GitHub repository loader for code ingestion.
"""
import os
import stat
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse
import re
import time

from git import Repo, GitCommandError


def robust_rmtree(path: str, max_retries: int = 3) -> bool:
    """
    Robustly remove a directory tree, handling Windows permission issues.

    Args:
        path: Path to directory to remove
        max_retries: Maximum number of retry attempts

    Returns:
        True if successful, False otherwise
    """
    def on_rm_error(func, path, exc_info):
        """Error handler for shutil.rmtree that handles permission errors."""
        # Try to fix permission issues on Windows
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception:
            pass

    for attempt in range(max_retries):
        try:
            if os.path.exists(path):
                shutil.rmtree(path, onerror=on_rm_error)
            return True
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(0.5)  # Brief pause before retry
            else:
                # Final attempt: try to remove files one by one
                try:
                    for root, dirs, files in os.walk(path, topdown=False):
                        for name in files:
                            try:
                                file_path = os.path.join(root, name)
                                os.chmod(file_path, stat.S_IWRITE)
                                os.remove(file_path)
                            except Exception:
                                pass
                        for name in dirs:
                            try:
                                os.rmdir(os.path.join(root, name))
                            except Exception:
                                pass
                    os.rmdir(path)
                    return True
                except Exception:
                    return False
    return False

from app.core.config import settings
from app.utils.file_utils import scan_directory, ProjectStructure


@dataclass
class RepoInfo:
    """Information about a loaded repository."""
    url: str
    name: str
    owner: str
    branch: str
    local_path: str
    is_valid: bool = True
    error_message: Optional[str] = None


def parse_github_url(url: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Parse a GitHub URL to extract owner and repo name.

    Args:
        url: GitHub repository URL

    Returns:
        Tuple of (owner, repo_name, error_message)
    """
    # Clean the URL
    url = url.strip()

    # Handle various GitHub URL formats
    patterns = [
        # https://github.com/owner/repo
        r"https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$",
        # git@github.com:owner/repo.git
        r"git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$",
        # github.com/owner/repo
        r"github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$",
    ]

    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            owner = match.group(1)
            repo = match.group(2)
            return owner, repo, None

    return None, None, "Invalid GitHub URL format"


def normalize_github_url(url: str) -> str:
    """
    Normalize a GitHub URL to HTTPS format.

    Args:
        url: GitHub repository URL

    Returns:
        Normalized HTTPS URL
    """
    owner, repo, error = parse_github_url(url)

    if error or not owner or not repo:
        return url

    return f"https://github.com/{owner}/{repo}.git"


def clone_repository(
    url: str,
    branch: str = "main",
    target_dir: Optional[str] = None
) -> RepoInfo:
    """
    Clone a GitHub repository to local storage.

    Args:
        url: GitHub repository URL
        branch: Branch to clone (default: main)
        target_dir: Optional target directory

    Returns:
        RepoInfo with clone results
    """
    owner, repo_name, error = parse_github_url(url)

    if error:
        return RepoInfo(
            url=url,
            name="",
            owner="",
            branch=branch,
            local_path="",
            is_valid=False,
            error_message=error
        )

    # Create target directory
    if target_dir:
        local_path = Path(target_dir)
    else:
        temp_base = Path(settings.TEMP_REPO_DIR)
        temp_base.mkdir(parents=True, exist_ok=True)
        local_path = temp_base / f"{owner}_{repo_name}"

    # Remove existing directory if present
    if local_path.exists():
        robust_rmtree(str(local_path))

    normalized_url = normalize_github_url(url)

    try:
        # Try to clone with specified branch
        Repo.clone_from(
            normalized_url,
            local_path,
            branch=branch,
            depth=1,  # Shallow clone for speed
            single_branch=True
        )

        return RepoInfo(
            url=url,
            name=repo_name,
            owner=owner,
            branch=branch,
            local_path=str(local_path),
            is_valid=True
        )

    except GitCommandError as e:
        # Try with 'master' branch if 'main' fails
        if branch == "main":
            try:
                Repo.clone_from(
                    normalized_url,
                    local_path,
                    branch="master",
                    depth=1,
                    single_branch=True
                )

                return RepoInfo(
                    url=url,
                    name=repo_name,
                    owner=owner,
                    branch="master",
                    local_path=str(local_path),
                    is_valid=True
                )
            except GitCommandError:
                pass

        return RepoInfo(
            url=url,
            name=repo_name or "",
            owner=owner or "",
            branch=branch,
            local_path="",
            is_valid=False,
            error_message=f"Failed to clone repository: {str(e)}"
        )


def load_repository(url: str, branch: str = "main") -> Tuple[RepoInfo, Optional[ProjectStructure]]:
    """
    Load a GitHub repository and scan its structure.

    Args:
        url: GitHub repository URL
        branch: Branch to load

    Returns:
        Tuple of (RepoInfo, ProjectStructure or None)
    """
    repo_info = clone_repository(url, branch)

    if not repo_info.is_valid:
        return repo_info, None

    # Scan the repository structure
    structure = scan_directory(repo_info.local_path)

    return repo_info, structure


def cleanup_repository(local_path: str) -> bool:
    """
    Remove a cloned repository from local storage.

    Args:
        local_path: Path to the repository

    Returns:
        True if cleanup successful
    """
    return robust_rmtree(local_path)


def cleanup_all_temp_repos() -> int:
    """
    Remove all temporary repositories.

    Returns:
        Number of repositories cleaned up
    """
    temp_base = Path(settings.TEMP_REPO_DIR)

    if not temp_base.exists():
        return 0

    count = 0
    for item in temp_base.iterdir():
        if item.is_dir():
            if robust_rmtree(str(item)):
                count += 1

    return count


def get_repo_size_estimate(url: str) -> Optional[int]:
    """
    Estimate repository size without cloning (using GitHub API).
    This is a placeholder - would need GitHub API token for actual implementation.

    Args:
        url: GitHub repository URL

    Returns:
        Estimated size in KB or None
    """
    # This would require GitHub API access
    # For now, return None to indicate unknown
    return None
