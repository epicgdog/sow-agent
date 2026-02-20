import os
from strands import Agent
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from mcp_client.client import get_streamable_http_mcp_client
from model.load import load_model
from tools import list_project_files, read_sow_file, read_source_code, write_code_to_file

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
        system_prompt="""You are an Auditor agent. Your ONLY role is to read the SOW file and extract requirements.

STRICT RULES:
- You MUST ONLY read and analyze documents
- You are FORBIDDEN from writing code or files
- You are FORBIDDEN from making implementation decisions
- Output requirements in clear JSON format

Your output should be a structured JSON with all requirements, deliverables, and constraints.""",
        tools=[read_sow_file]
    )


def create_bridge_agent(session_manager=None):
    """Create the Bridge agent that reads current code state"""
    return Agent(
        model=load_model(),
        session_manager=session_manager,
        system_prompt="""You are a Bridge agent. Your ONLY role is to read and document the current 'As-Is' state of the codebase.

STRICT RULES:
- You MUST ONLY read existing code files
- You are FORBIDDEN from writing or modifying any code
- You are FORBIDDEN from making recommendations or plans
- Document what currently exists, not what should exist

Your output should describe the current state of the /src directory.""",
        tools=[read_source_code, list_project_files]
    )


def create_architect_agent(session_manager=None):
    """Create the Architect agent that creates implementation plans"""
    return Agent(
        model=load_model(),
        session_manager=session_manager,
        system_prompt="""You are an Architect agent. Your ONLY role is to create detailed technical implementation plans.

STRICT RULES:
- You MUST ONLY create plans and specifications
- You are FORBIDDEN from writing actual code or files
- You are FORBIDDEN from reading files directly
- You work with information provided to you by other agents

Your output should be a detailed technical plan specifying:
1. What files need to be created/modified
2. What code should go in each file
3. Implementation approach and structure""",
        tools=[]
    )


def create_artisan_agent(session_manager=None):
    """Create the Artisan agent that executes the plan"""
    return Agent(
        model=load_model(),
        session_manager=session_manager,
        system_prompt="""You are an Artisan agent. Your ONLY role is to write code to files based on the Architect's plan.

STRICT RULES:
- You MUST ONLY write code using the write_code_to_file tool
- You are FORBIDDEN from creating plans or making architectural decisions
- You are FORBIDDEN from reading SOW documents
- You MUST follow the Architect's plan exactly

Execute the plan step by step and report your progress.""",
        tools=[write_code_to_file]
    )


def create_qa_judge_agent(session_manager=None):
    """Create the QA Judge agent that validates compliance"""
    return Agent(
        model=load_model(),
        session_manager=session_manager,
        system_prompt="""You are a QA Judge agent. Your ONLY role is to compare the SOW requirements against the implemented code.

STRICT RULES:
- You MUST ONLY read and compare documents
- You are FORBIDDEN from writing code or files
- You are FORBIDDEN from making implementation suggestions
- You MUST output ONLY one of two formats:
  * "PASS" if all requirements are met
  * "FAIL: [specific reason]" if requirements are not met

Be specific about what is missing or incorrect in FAIL messages.""",
        tools=[read_sow_file, read_source_code]
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
    max_attempts = 3
    
    # Step 1: Auditor reads SOW
    yield "\n=== AUDITOR AGENT ===\n"
    auditor = create_auditor_agent(session_manager)
    auditor_output = []
    async for chunk in auditor.stream_async(f"Read and analyze the SOW requirements. User context: {user_prompt}"):
        auditor_output.append(chunk)
        yield chunk
    sow_requirements = "".join(auditor_output)
    
    # Step 2: Bridge reads current code state
    yield "\n\n=== BRIDGE AGENT ===\n"
    bridge = create_bridge_agent(session_manager)
    bridge_output = []
    async for chunk in bridge.stream_async("Read and document the current 'As-Is' state of the /src directory"):
        bridge_output.append(chunk)
        yield chunk
    current_state = "".join(bridge_output)
    
    # Self-Healing Loop
    for attempt in range(1, max_attempts + 1):
        yield f"\n\n=== ATTEMPT {attempt}/{max_attempts} ===\n"
        
        # Step 3: Architect creates plan
        yield "\n=== ARCHITECT AGENT ===\n"
        architect = create_architect_agent(session_manager)
        
        if attempt == 1:
            architect_prompt = f"""Create an implementation plan based on:

SOW REQUIREMENTS:
{sow_requirements}

CURRENT STATE:
{current_state}"""
        else:
            architect_prompt = f"""The previous implementation FAILED QA. Create a REVISED plan.

SOW REQUIREMENTS:
{sow_requirements}

PREVIOUS FAILURE:
{qa_result}

Fix the issues and create an improved plan."""
        
        architect_output = []
        async for chunk in architect.stream_async(architect_prompt):
            architect_output.append(chunk)
            yield chunk
        implementation_plan = "".join(architect_output)
        
        # Step 4: Artisan executes plan
        yield "\n\n=== ARTISAN AGENT ===\n"
        artisan = create_artisan_agent(session_manager)
        async for chunk in artisan.stream_async(f"Execute this implementation plan:\n\n{implementation_plan}"):
            yield chunk
        
        # Step 5: QA Judge validates
        yield "\n\n=== QA JUDGE AGENT ===\n"
        qa_judge = create_qa_judge_agent(session_manager)
        qa_output = []
        async for chunk in qa_judge.stream_async("Compare the SOW requirements against the implemented code in /src. Output PASS or FAIL: [reason]"):
            qa_output.append(chunk)
            yield chunk
        qa_result = "".join(qa_output).strip()
        
        # Check QA result
        if qa_result.startswith("PASS"):
            yield "\n\n=== ✅ SUCCESS ===\n"
            yield f"Implementation passed QA validation on attempt {attempt}/{max_attempts}\n"
            return
        elif qa_result.startswith("FAIL"):
            yield f"\n\n=== ❌ FAILED ATTEMPT {attempt}/{max_attempts} ===\n"
            if attempt < max_attempts:
                yield "Sending feedback to Architect for revision...\n"
            else:
                yield f"Maximum attempts reached. Final status: {qa_result}\n"
        else:
            yield f"\n\n=== ⚠️ UNCLEAR QA RESULT ===\n"
            yield f"QA Judge output: {qa_result}\n"
            if attempt >= max_attempts:
                yield "Maximum attempts reached.\n"
                return
    
    yield "\n=== WORKFLOW COMPLETE ===\n"


if __name__ == "__main__":
    app.run()
