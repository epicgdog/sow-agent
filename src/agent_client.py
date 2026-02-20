import boto3
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class AgentCoreClient:
    def __init__(
        self,
        agent_id: Optional[str] = None,
        agent_alias_id: Optional[str] = None,
        region: Optional[str] = None
    ):
        self.agent_id = agent_id or os.getenv("AGENT_ID")
        self.agent_alias_id = agent_alias_id or os.getenv("AGENT_ALIAS_ID")
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        
        self.client = boto3.client(
            "bedrock-agent-runtime",
            region_name=self.region
        )
    
    def invoke_agent(
        self,
        session_id: str,
        input_text: str,
        session_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Invoke the Bedrock agent with input text."""
        params = {
            "agentId": self.agent_id,
            "agentAliasId": self.agent_alias_id,
            "sessionId": session_id,
            "inputText": input_text
        }
        
        if session_state:
            params["sessionState"] = session_state
        
        response = self.client.invoke_agent(**params)
        return response
