"""
Agent Browser Python Wrapper

Python wrapper for agent-browser CLI - Browser automation for AI agents.
"""

from .agent_browser import AgentBrowser, AgentBrowserError
from .async_agent_browser import AsyncAgentBrowser

__version__ = "0.3.0"

__all__ = [
    "AgentBrowser",
    "AgentBrowserError",
    "AsyncAgentBrowser",
]
