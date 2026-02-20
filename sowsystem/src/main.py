import os
from strands import Agent
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from mcp_client.client import get_streamable_http_mcp_client
from model.load import load_model
from tools import list_project_files, read_sow_file, write_code_to_file

app = BedrockAgentCoreApp()
log = app.logger

MEMORY_ID = os.getenv("BEDROCK_AGENTCORE_MEMORY_ID")
REGION = os.getenv("AWS_REGION")

# Import AgentCore Gateway as Streamable HTTP MCP Client
mcp_client = get_streamable_http_mcp_client()


def create_auditor_agent(session_manager=None):
    """Create the Auditor agent that reads and analyzes the SOW"""
    return Agent(
        model=load_model(),
        session_manager=session_manager,
        system_prompt="You are an Auditor agent. Read the SOW file and analyze it. List all requirements and deliverables clearly.",
        tools=[read_sow_file, list_project_files]
    )


def create_architect_agent(session_manager=None):
    """Create the Architect agent that creates implementation plans"""
    return Agent(
        model=load_model(),
        session_manager=session_manager,
        system_prompt="You are an Architect agent. Based on the Auditor's findings, create a detailed implementation plan. Specify what files need to be created and what code should go in each file.",
        tools=[]
    )


def create_artisan_agent(session_manager=None):
    """Create the Artisan agent that executes the plan"""
    return Agent(
        model=load_model(),
        session_manager=session_manager,
        system_prompt="You are an Artisan agent. Execute the Architect's plan by writing code to files using the write_code_to_file tool. Report your progress and final status.",
        tools=[write_code_to_file]
    )


@app.entrypoint
async def invoke(payload, context):
    session_id = getattr(context, 'session_id', 'default')
    user_id = payload.get("user_id") or 'default-user'
    
    # Configure memory
    session_manager = None
    if MEMORY_ID:
        session_manager = AgentCoreMemorySessionManager(
            AgentCoreMemoryConfig(
                memory_id=MEMORY_ID,
                session_id=session_id,
                actor_id=user_id,
                retrieval_config={
                    f"/facts/{user_id}/": RetrievalConfig(top_k=10, relevance_score=0.4),
                    f"/preferences/{user_id}/": RetrievalConfig(top_k=5, relevance_score=0.5),
                    f"/summaries/{user_id}/{session_id}/": RetrievalConfig(top_k=5, relevance_score=0.4),
                    f"/episodes/{user_id}/{session_id}/": RetrievalConfig(top_k=5, relevance_score=0.4),
                }
            ),
            REGION
        )
    else:
        log.warning("MEMORY_ID is not set. Skipping memory session manager initialization.")

    user_prompt = payload.get("prompt")
    
    yield "=== AUDITOR AGENT ===\n"
    
    # Step 1: Auditor reads and analyzes SOW
    auditor = create_auditor_agent(session_manager)
    auditor_output = []
    
    async for chunk in auditor.stream_async(f"Read the SOW file and analyze the requirements. User request: {user_prompt}"):
        if "data" in chunk and isinstance(chunk["data"], str):
            auditor_output.append(chunk["data"])
            yield chunk["data"]
    
    auditor_result = "".join(auditor_output)
    yield "\n\n=== ARCHITECT AGENT ===\n"
    
    # Step 2: Architect creates plan based on Auditor's findings
    architect = create_architect_agent(session_manager)
    architect_output = []
    
    async for chunk in architect.stream_async(f"Based on these findings, create an implementation plan:\n\n{auditor_result}"):
        if "data" in chunk and isinstance(chunk["data"], str):
            architect_output.append(chunk["data"])
            yield chunk["data"]
    
    architect_result = "".join(architect_output)
    yield "\n\n=== ARTISAN AGENT ===\n"
    
    # Step 3: Artisan executes the plan
    artisan = create_artisan_agent(session_manager)
    
    async for chunk in artisan.stream_async(f"Execute this plan:\n\n{architect_result}"):
        if "data" in chunk and isinstance(chunk["data"], str):
            yield chunk["data"]
    
    yield "\n\n=== COMPLETE ===\n"


if __name__ == "__main__":
    app.run()
