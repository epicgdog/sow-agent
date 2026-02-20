"""
Datadog MCP Client - Connects to the hosted Datadog MCP server via Streamable HTTP.

Provides 20 Datadog tools (logs, metrics, traces, incidents, notebooks, etc.)
to strands agents for observability-driven self-healing.

Uses DD_API_KEY + DD_APPLICATION_KEY headers for authentication.
Endpoint: https://mcp.{DD_SITE}/api/unstable/mcp-server/mcp
"""

import os
from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp.mcp_client import MCPClient


def get_datadog_mcp_client() -> MCPClient:
    """
    Creates an MCPClient connected to the Datadog MCP server.

    Reads credentials from environment variables:
        - DD_API_KEY: Datadog API key
        - DD_APPLICATION_KEY: Datadog Application key
        - DD_SITE: Datadog site (default: datadoghq.com)

    Returns:
        MCPClient compatible with strands Agent(tools=[...])
    """
    api_key = os.getenv("DD_API_KEY", "")
    app_key = os.getenv("DD_APPLICATION_KEY", "")
    site = os.getenv("DD_SITE", "datadoghq.com")

    url = f"https://mcp.{site}/api/unstable/mcp-server/mcp"

    headers = {
        "DD-API-KEY": api_key,
        "DD-APPLICATION-KEY": app_key,
    }

    return MCPClient(lambda: streamablehttp_client(url, headers=headers))
