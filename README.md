# sow-agent

AWS Bedrock AgentCore development environment for Python.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure AWS credentials:
```bash
cp .env.example .env
# Edit .env with your AWS credentials and agent details
```

4. Configure AWS CLI (alternative to .env):
```bash
aws configure
```

## Usage

```python
from src.agent_client import AgentCoreClient

client = AgentCoreClient()
response = client.invoke_agent(
    session_id="unique-session-id",
    input_text="Your prompt here"
)
```