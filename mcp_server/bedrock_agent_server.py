#!/usr/bin/env python3
import json
import sys
import boto3
from typing import Any
from dotenv import load_dotenv
import os

load_dotenv()


def create_bedrock_client():
    return boto3.client(
        "bedrock-agent-runtime",
        region_name=os.getenv("AWS_REGION", "us-west-2")
    )


def handle_request(request: dict) -> dict:
    method = request.get("method")
    
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "invoke_bedrock_agent",
                    "description": "Invoke AWS Bedrock Agent with a prompt",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "agent_id": {"type": "string", "description": "Agent ID"},
                            "agent_alias_id": {"type": "string", "description": "Agent Alias ID"},
                            "session_id": {"type": "string", "description": "Session ID"},
                            "input_text": {"type": "string", "description": "Input prompt"}
                        },
                        "required": ["agent_id", "agent_alias_id", "session_id", "input_text"]
                    }
                }
            ]
        }
    
    elif method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "invoke_bedrock_agent":
            client = create_bedrock_client()
            
            response = client.invoke_agent(
                agentId=arguments["agent_id"],
                agentAliasId=arguments["agent_alias_id"],
                sessionId=arguments["session_id"],
                inputText=arguments["input_text"]
            )
            
            # Process streaming response
            result = []
            event_stream = response.get("completion", [])
            for event in event_stream:
                if "chunk" in event:
                    chunk = event["chunk"]
                    if "bytes" in chunk:
                        result.append(chunk["bytes"].decode("utf-8"))
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "".join(result)
                    }
                ]
            }
    
    return {"error": "Unknown method"}


def main():
    for line in sys.stdin:
        try:
            request = json.loads(line)
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except Exception as e:
            error_response = {"error": str(e)}
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()
