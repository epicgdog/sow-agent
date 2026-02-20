#!/usr/bin/env python3
"""
Runner - Entry point for running agent system on external projects.

Responsibilities:
- Accept target project (GitHub URL or local path)
- Create fresh workspace per run
- Coordinate agent execution loop
- Exit with PASS or FAIL status

Does NOT:
- Modify agent code or prompts
- Interact with git/GitHub directly (delegates to adapter)
- Add agent logic to target projects
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from workspace_manager import WorkspaceManager
from project_adapter import ProjectAdapter, LocalProjectAdapter


def run_agents_on_project(workspace: Path, user_prompt: str = "Implement SOW requirements") -> str:
    """
    Invoke the existing AgentCore orchestration on the workspace
    
    Args:
        workspace: Path to workspace directory
        user_prompt: Prompt to pass to agents
        
    Returns:
        Final status from QA Judge (PASS or FAIL: reason)
    """
    # Change to workspace directory so agents operate in correct context
    original_cwd = os.getcwd()
    
    try:
        # Move to workspace root so agents can access src/, sow/, etc.
        os.chdir(workspace)
        
        # Import AgentCore app (existing implementation)
        from main import app
        
        # Create a mock payload and context for the entrypoint
        class MockContext:
            session_id = "runner_session"
        
        payload = {
            "prompt": user_prompt,
            "user_id": "runner"
        }
        
        # Collect output from agent stream
        output_parts = []
        
        # Run the existing agent workflow
        import asyncio
        async def run_workflow():
            async for chunk in app.entrypoint(payload, MockContext()):
                output_parts.append(chunk)
                print(chunk, end='', flush=True)
        
        asyncio.run(run_workflow())
        
        full_output = "".join(output_parts)
        
        # Extract final QA result
        # Look for PASS or FAIL in the output
        if "PASS" in full_output:
            return "PASS"
        elif "FAIL:" in full_output:
            # Extract failure reason
            fail_idx = full_output.rfind("FAIL:")
            reason = full_output[fail_idx:fail_idx+200].split('\n')[0]
            return reason
        else:
            return "FAIL: Unable to determine QA result"
    
    finally:
        os.chdir(original_cwd)


def main():
    """Main entry point for runner"""
    parser = argparse.ArgumentParser(
        description="Run SOW compliance agents on external projects"
    )
    parser.add_argument(
        "project",
        help="Project source (GitHub URL or local path)"
    )
    parser.add_argument(
        "--sow",
        default="sow_reference.md",
        help="Path to SOW reference document (default: sow_reference.md)"
    )
    parser.add_argument(
        "--prompt",
        default="Implement all SOW requirements",
        help="Prompt to pass to agents"
    )
    parser.add_argument(
        "--keep-workspace",
        action="store_true",
        help="Keep workspace directory after run"
    )
    parser.add_argument(
        "--workspace-dir",
        default="./workspaces",
        help="Base directory for workspaces (default: ./workspaces)"
    )
    
    args = parser.parse_args()
    
    print(f"🚀 SOW Agent Runner")
    print(f"Project: {args.project}")
    print(f"SOW: {args.sow}")
    print("-" * 60)
    
    # Initialize components
    workspace_manager = WorkspaceManager(base_dir=args.workspace_dir)
    
    # Use LocalProjectAdapter for simplicity (can extend to full ProjectAdapter)
    if args.project.startswith("https://") or args.project.startswith("git@"):
        adapter = ProjectAdapter()
    else:
        adapter = LocalProjectAdapter()
    
    try:
        # Step 1: Fetch project
        print("\n📦 Fetching project...")
        project_path = adapter.fetch_project(args.project)
        print(f"✓ Project fetched: {project_path}")
        
        # Step 2: Create workspace
        print("\n🏗️  Creating workspace...")
        workspace = workspace_manager.create_workspace()
        print(f"✓ Workspace created: {workspace}")
        
        # Step 3: Copy project to workspace
        print("\n📋 Copying project to workspace...")
        workspace_manager.copy_project_to_workspace(project_path, workspace)
        print(f"✓ Project copied to {workspace / 'src'}")
        
        # Step 4: Copy SOW to workspace
        sow_path = Path(args.sow)
        if sow_path.exists():
            workspace_manager.copy_sow_to_workspace(sow_path, workspace)
            print(f"✓ SOW copied to workspace")
        else:
            print(f"⚠️  SOW file not found: {sow_path}")
        
        # Step 5: Create snapshot
        print("\n📸 Creating snapshot...")
        workspace_manager.create_snapshot(workspace)
        print(f"✓ Snapshot created")
        
        # Step 6: Run agents
        print("\n🤖 Running agent workflow...")
        print("=" * 60)
        
        final_status = run_agents_on_project(workspace, args.prompt)
        
        print("=" * 60)
        print(f"\n📊 Final Status: {final_status}")
        
        # Step 7: Cleanup (optional)
        if not args.keep_workspace:
            print(f"\n🧹 Cleaning up workspace...")
            workspace_manager.cleanup_workspace(workspace)
            print(f"✓ Workspace removed")
        else:
            print(f"\n💾 Workspace preserved: {workspace}")
        
        # Exit with appropriate code
        if final_status.startswith("PASS"):
            print("\n✅ SUCCESS")
            sys.exit(0)
        else:
            print("\n❌ FAILED")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
