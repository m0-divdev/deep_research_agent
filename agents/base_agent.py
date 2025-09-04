"""Base agent class for all agents in the system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import asyncio
try:
    from agno import Agent
    from agno.models.openai import OpenAIChat
except ImportError:
    # Fallback for development
    class Agent:
        def __init__(self, **kwargs):
            self.name = kwargs.get('name', 'Agent')
            self.role = kwargs.get('role', 'Assistant')
        
        async def arun(self, message):
            return {"content": f"Mock response to: {message}"}
    
    class OpenAIChat:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id', 'gpt-4o')
from memory.shared_knowledge import SharedKnowledgeRepository


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, name: str, role: str, shared_knowledge: SharedKnowledgeRepository):
        self.name = name
        self.role = role
        self.shared_knowledge = shared_knowledge
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.task_history: List[Dict[str, Any]] = []
        
        # Initialize Agno agent
        self.agno_agent = Agent(
            name=name,
            role=role,
            model=OpenAIChat(id="gpt-4o"),
            instructions=self._get_instructions(),
            show_tool_calls=True,
            markdown=True
        )
    
    @abstractmethod
    def _get_instructions(self) -> str:
        """Get agent-specific instructions."""
        pass
    
    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task and return results."""
        pass
    
    def log_activity(self, activity: str, details: Optional[Dict] = None) -> None:
        """Log agent activity."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "activity": activity,
            "details": details or {}
        }
        self.task_history.append(log_entry)
        self.last_activity = datetime.now()
    
    def get_task_history(self) -> List[Dict[str, Any]]:
        """Get task history."""
        return self.task_history
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            "name": self.name,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "total_tasks": len(self.task_history),
            "status": "active"
        }
    
    async def run(self, message: str) -> Any:
        """Run the Agno agent with a message."""
        try:
            result = await self.agno_agent.arun(message)
            self.log_activity("agent_run", {"message": message, "success": True})
            return result
        except Exception as e:
            self.log_activity("agent_run", {"message": message, "error": str(e)})
            raise
    
    def update_shared_knowledge(self, key: str, value: Any, metadata: Optional[Dict] = None) -> None:
        """Update shared knowledge repository."""
        self.shared_knowledge.store(key, value, metadata)
        self.log_activity("knowledge_update", {"key": key, "metadata": metadata})
