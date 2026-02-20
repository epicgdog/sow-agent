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


@tool
def read_source_code(directory: str = "src") -> str:
    """Read all Python files in the specified directory"""
    try:
        code_files = {}
        if not os.path.exists(directory):
            return f"Error: Directory {directory} does not exist"
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r') as f:
                        code_files[filepath] = f.read()
        
        if not code_files:
            return f"No Python files found in {directory}"
        
        result = []
        for filepath, content in code_files.items():
            result.append(f"=== {filepath} ===\n{content}\n")
        
        return "\n".join(result)
    except Exception as e:
        return f"Error reading source code: {str(e)}"


@tool
def write_code_to_file(filename: str, content: str) -> str:
    """Write code content to a specified file"""
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(filename, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Error writing to {filename}: {str(e)}"
