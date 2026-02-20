"""
Workspace Manager - Creates and manages isolated workspace directories for agent runs.

Responsibilities:
- Create fresh workspace directory structure per run
- Copy project code into workspace
- Create read-only snapshot before agents run
- No AI or agent logic here
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


class WorkspaceManager:
    """Manages isolated workspace directories for agent execution"""
    
    def __init__(self, base_dir: str = "./workspaces"):
        """
        Initialize workspace manager
        
        Args:
            base_dir: Base directory where workspaces will be created
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def create_workspace(self, run_id: str = None) -> Path:
        """
        Create a fresh workspace directory with required structure
        
        Structure:
        /workspace/
            src/        (writable project code)
            snapshot/   (read-only copy of src)
            sow/        (SOW reference documents)
            metadata/   (run metadata)
            reports/    (output reports)
        
        Args:
            run_id: Optional run identifier, defaults to timestamp
            
        Returns:
            Path to workspace root
        """
        if run_id is None:
            run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        workspace = self.base_dir / run_id
        
        # Create directory structure
        (workspace / "src").mkdir(parents=True, exist_ok=True)
        (workspace / "snapshot").mkdir(exist_ok=True)
        (workspace / "sow").mkdir(exist_ok=True)
        (workspace / "metadata").mkdir(exist_ok=True)
        (workspace / "reports").mkdir(exist_ok=True)
        
        return workspace
    
    def copy_project_to_workspace(self, source_dir: Path, workspace: Path):
        """
        Copy project files into workspace/src
        
        Args:
            source_dir: Source directory containing project files
            workspace: Workspace root directory
        """
        src_dir = workspace / "src"
        
        # Copy all files from source to workspace/src
        if source_dir.is_dir():
            for item in source_dir.iterdir():
                if item.name in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']:
                    continue  # Skip common non-code directories
                
                dest = src_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
    
    def create_snapshot(self, workspace: Path):
        """
        Create read-only snapshot of workspace/src before agents run
        
        Args:
            workspace: Workspace root directory
        """
        src_dir = workspace / "src"
        snapshot_dir = workspace / "snapshot"
        
        # Clear existing snapshot
        if snapshot_dir.exists():
            shutil.rmtree(snapshot_dir)
        snapshot_dir.mkdir()
        
        # Copy src to snapshot
        if src_dir.exists():
            shutil.copytree(src_dir, snapshot_dir, dirs_exist_ok=True)
    
    def copy_sow_to_workspace(self, sow_file: Path, workspace: Path):
        """
        Copy SOW reference document into workspace
        
        Args:
            sow_file: Path to SOW reference file
            workspace: Workspace root directory
        """
        if sow_file.exists():
            shutil.copy2(sow_file, workspace / "sow" / "sow_reference.md")
    
    def cleanup_workspace(self, workspace: Path):
        """
        Remove workspace directory (optional cleanup)
        
        Args:
            workspace: Workspace root directory
        """
        if workspace.exists():
            shutil.rmtree(workspace)
