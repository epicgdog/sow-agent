"""
Project Adapter - Fetches/copies project code into workspace.

Responsibilities:
- Fetch code from GitHub URL or local path
- Copy code into workspace/src
- No analysis, validation, or agent calls
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Union


class ProjectAdapter:
    """Adapter for fetching project code from various sources"""
    
    def fetch_project(self, source: str) -> Path:
        """
        Fetch project from source (GitHub URL or local path)
        
        Args:
            source: GitHub URL (https://github.com/...) or local path
            
        Returns:
            Path to fetched project directory
            
        Raises:
            ValueError: If source format is invalid
            RuntimeError: If fetch fails
        """
        if source.startswith("https://github.com/") or source.startswith("git@github.com:"):
            return self._fetch_from_github(source)
        elif os.path.exists(source):
            return Path(source)
        else:
            raise ValueError(f"Invalid source: {source}. Must be GitHub URL or valid local path")
    
    def _fetch_from_github(self, github_url: str) -> Path:
        """
        Clone GitHub repository to temporary directory
        
        Args:
            github_url: GitHub repository URL
            
        Returns:
            Path to cloned repository
            
        Raises:
            RuntimeError: If git clone fails
        """
        # Create temporary directory for clone
        temp_dir = Path(tempfile.mkdtemp(prefix="sow_agent_clone_"))
        
        try:
            # Clone repository
            result = subprocess.run(
                ["git", "clone", "--depth", "1", github_url, str(temp_dir)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Git clone failed: {result.stderr}")
            
            return temp_dir
            
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Git clone timed out for {github_url}")
        except FileNotFoundError:
            raise RuntimeError("Git is not installed or not in PATH")
        except Exception as e:
            # Cleanup on failure
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)
            raise RuntimeError(f"Failed to fetch from GitHub: {str(e)}")


class LocalProjectAdapter(ProjectAdapter):
    """Simplified adapter for local projects only"""
    
    def fetch_project(self, source: str) -> Path:
        """
        Validate and return local project path
        
        Args:
            source: Local directory path
            
        Returns:
            Path to project directory
            
        Raises:
            ValueError: If path doesn't exist
        """
        path = Path(source)
        if not path.exists():
            raise ValueError(f"Local path does not exist: {source}")
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {source}")
        
        return path
