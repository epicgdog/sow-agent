"""
Datadog Tools - Graceful degradation wrapper for Datadog MCP tools.

Initializes the Datadog MCP client and returns tools for strands agents.
If credentials are missing or the connection fails, returns an empty list
so agents continue working without Datadog tools.
"""

import os
import logging

logger = logging.getLogger(__name__)


def get_datadog_tools():
    """
    Load Datadog MCP tools with graceful degradation.

    Returns:
        list: List of MCP tools if connection succeeds, empty list otherwise.
    """
    api_key = os.getenv("DD_API_KEY", "")
    app_key = os.getenv("DD_APPLICATION_KEY", "")

    if not api_key or not app_key:
        logger.warning(
            "DD_API_KEY or DD_APPLICATION_KEY not set. "
            "Datadog MCP tools will not be available."
        )
        return []

    try:
        from mcp_client.datadog_client import get_datadog_mcp_client

        client = get_datadog_mcp_client()
        # Return the client itself as a tool provider — strands Agent
        # accepts MCPClient directly in its tools list and manages
        # the lifecycle automatically.
        return [client]
    except Exception as e:
        logger.warning(f"Failed to initialize Datadog MCP client: {e}")
        return []


def get_datadog_mcp_client_instance():
    """
    Get the raw MCPClient instance for manual lifecycle management.

    Use this when you need to open/close the client explicitly
    (e.g., in the runner's workflow orchestration).

    Returns:
        MCPClient or None: The client if credentials are available, None otherwise.
    """
    api_key = os.getenv("DD_API_KEY", "")
    app_key = os.getenv("DD_APPLICATION_KEY", "")

    if not api_key or not app_key:
        return None

    try:
        from mcp_client.datadog_client import get_datadog_mcp_client
        return get_datadog_mcp_client()
    except Exception:
        return None
