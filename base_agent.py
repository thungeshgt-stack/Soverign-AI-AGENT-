"""
Base class all agents inherit from. Agents call tools; they should not
embed heavy logic that belongs in tools/ or rag/.
"""
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    name: str = "base_agent"
    display_name: str = "Base Agent"

    @abstractmethod
    def run(self, task) -> dict:
        """Execute the agent against a Task, return a result dict."""
        raise NotImplementedError
