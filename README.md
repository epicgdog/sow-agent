# sow-agent

AWS Bedrock AgentCore multi-agent system for SOW compliance checking.

## Prerequisites

- Python 3.9 or higher
- AWS account with Bedrock access
- AWS credentials (provided by hackathon organizers)
- Git (for GitHub project support)

## Installation

1. Clone or download this repository

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install AgentCore CLI:
```bash
pip install bedrock-agentcore-starter-toolkit
```

4. Install project dependencies:
```bash
pip install -r requirements.txt
```

5. Configure AWS credentials:
```bash
cp .env.example .env
# Edit .env with your AWS credentials
```

Required environment variables in `.env`:
```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
```

6. Verify AWS credentials:
```bash
aws sts get-caller-identity
```

## Running the Agent System

### Option 1: Direct Development Mode

Test the agents in development mode:

1. Start the development server (in one terminal):
```bash
cd sowsystem
agentcore dev
```

2. Test the agent (in another terminal):
```bash
cd sowsystem
agentcore invoke --dev "Analyze the SOW and create implementation files"
```

### Option 2: Run on External Projects

Use the runner to execute agents on any project (GitHub or local):

```bash
cd sowsystem
python runner.py /path/to/project --sow sow_reference.md
```

Or with a GitHub repository:
```bash
python runner.py https://github.com/username/repo --sow sow_reference.md
```

**Runner Options:**
- `--prompt "Custom prompt"` - Custom prompt for agents (default: "Implement all SOW requirements")
- `--keep-workspace` - Preserve workspace after run for inspection
- `--workspace-dir ./my-workspaces` - Custom workspace location

**What the runner does:**
1. Fetches the project (clones from GitHub or copies from local path)
2. Creates an isolated workspace with proper structure
3. Runs the 5-agent workflow (Auditor → Bridge → Architect → Artisan → QA Judge)
4. Retries up to 3 times if QA fails
5. Exits with status code 0 (PASS) or 1 (FAIL)

## How It Works

The system uses five specialized agents that run in sequence with a self-healing loop:

1. **Auditor Agent** - Reads `sow_reference.md` and outputs requirement JSON (read-only)
2. **Bridge Agent** - Reads current code in `/src` to identify 'As-Is' state (read-only)
3. **Architect Agent** - Creates technical implementation plan (no file access)
4. **Artisan Agent** - Writes code to files using `write_code_to_file` tool (write-only)
5. **QA Judge Agent** - Validates compliance, outputs PASS or FAIL: [reason] (read-only)

**Self-Healing Loop:**
- Max 3 attempts per run
- If QA Judge returns FAIL, feedback goes to Architect for revised plan
- If QA Judge returns PASS, workflow exits successfully

**Safety Guardrails:**
Each agent has strict system prompts forbidding actions outside its role.

## Project Structure

```
sow-agent/
├── sowsystem/
│   ├── runner.py              # Entry point for external projects
│   ├── workspace_manager.py   # Workspace creation and management
│   ├── project_adapter.py     # Project fetching (GitHub/local)
│   └── src/
│       ├── main.py            # Multi-agent orchestration
│       ├── tools.py           # Custom Python tools
│       └── model/
│           └── load.py        # Model configuration
├── requirements.txt           # Python dependencies
└── .env                       # AWS credentials (create from .env.example)
```

## Architecture

**Workspace Structure:**
```
/workspace/
    src/        (writable project code - agents work here)
    snapshot/   (read-only copy of original src)
    sow/        (SOW reference documents)
    metadata/   (run metadata)
    reports/    (output reports)
```

**Component Responsibilities:**
- `runner.py` - Coordinates workflow, no agent logic
- `workspace_manager.py` - File operations only, no AI
- `project_adapter.py` - Fetches code, no analysis
- `src/main.py` - Agent orchestration (DO NOT MODIFY)

## Troubleshooting

### Model Access Issues
If you get "ResourceNotFoundException" errors about model access:
- Contact hackathon organizers to enable Bedrock model access for your AWS account
- Current model: `amazon.nova-lite-v1:0`

### Permission Issues
Ensure your AWS credentials have:
- `bedrock:InvokeModel` permission
- `bedrock:InvokeModelWithResponseStream` permission

### Git Clone Issues
If GitHub cloning fails:
- Ensure git is installed: `git --version`
- Check network connectivity
- Try using local path instead: `python runner.py /path/to/local/project`

## Current SOW Requirements

The system validates against these requirements (from `sow_reference.md`):
- Build a Bedrock agent that reads local files
- Create a tool to identify missing security headers in Python code
- Generate compliance reports comparing code against requirements
- Use Python 3.10+, Amazon Nova/Claude models, store code in `/src`
