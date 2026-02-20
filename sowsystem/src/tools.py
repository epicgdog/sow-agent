import os
from strands import tool
from typing import List


@tool
def list_project_files() -> List[str]:
    """List all files in the current directory"""
    try:
        files = os.listdir('.')
        return [f for f in files if os.path.isfile(f)]
    except Exception as e:
        return [f"Error listing files: {str(e)}"]


@tool
def read_sow_file() -> str:
    """Read the content of sow_reference.md file"""
    try:
        with open('sow_reference.md', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Error: sow_reference.md file not found"
    except Exception as e:
        return f"Error reading file: {str(e)}"
