"""Agent orchestrator for managing the multi-agent system."""

import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime
from memory.shared_knowledge import SharedKnowledgeRepository
from agents import SearchAgent, AnalystAgent, CriticAgent, WriterAgent
from coordination.workflow_engine import WorkflowEngine
from coordination.task_coordinator import TaskCoordinator


class AgentOrchestrator:
    """Orchestrates the multi-agent deep research system."""
    
    def __init__(self):
        # Initialize shared knowledge repository
        self.shared_knowledge = SharedKnowledgeRepository()
        
        # Initialize workflow engine and task coordinator
        self.workflow_engine = WorkflowEngine()
        self.task_coordinator = TaskCoordinator(self.workflow_engine)
        
        # Initialize agents
        self.agents = {
            "SearchAgent": SearchAgent(self.shared_knowledge),
            "AnalystAgent": AnalystAgent(self.shared_knowledge),
            "CriticAgent": CriticAgent(self.shared_knowledge),
            "WriterAgent": WriterAgent(self.shared_knowledge)
        }
        
        # System status
        self.system_status = {
            "initialized": True,
            "started_at": datetime.now().isoformat(),
            "agents": list(self.agents.keys()),
            "active_workflows": 0,
            "total_tasks_completed": 0
        }
    
    async def start_system(self) -> None:
        """Start the multi-agent system."""
        self.system_status["status"] = "running"
        self.system_status["started_at"] = datetime.now().isoformat()
        
        # Start background task processing
        asyncio.create_task(self._process_background_tasks())
    
    async def stop_system(self) -> None:
        """Stop the multi-agent system."""
        self.system_status["status"] = "stopped"
        self.system_status["stopped_at"] = datetime.now().isoformat()
    
    async def _process_background_tasks(self) -> None:
        """Process background tasks continuously."""
        while self.system_status.get("status") == "running":
            try:
                await self.task_coordinator.process_task_queue(self.agents)
                await asyncio.sleep(1)  # Check every second
            except Exception as e:
                print(f"Error in background task processing: {e}")
                await asyncio.sleep(5)  # Wait longer on error
    
    async def research(self, query: str, processor_config: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Perform a complete research task."""
        try:
            result = await self.task_coordinator.execute_research_task(
                query, self.agents, processor_config
            )
            
            self.system_status["total_tasks_completed"] += 1
            
            return {
                "success": True,
                "query": query,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "success": False,
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def analyze_data(self, data: Dict[str, Any], analysis_type: str = "general") -> Dict[str, Any]:
        """Perform data analysis."""
        try:
            result = await self.task_coordinator.execute_analysis_task(
                data, self.agents, analysis_type
            )
            
            return {
                "success": True,
                "analysis_type": analysis_type,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "success": False,
                "analysis_type": analysis_type,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_content(self, data: Dict[str, Any], content_type: str = "report") -> Dict[str, Any]:
        """Generate content."""
        try:
            result = await self.task_coordinator.execute_content_task(
                data, self.agents, content_type
            )
            
            return {
                "success": True,
                "content_type": content_type,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "success": False,
                "content_type": content_type,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def add_research_task(self, query: str, processor_config: Optional[Dict[str, str]] = None) -> str:
        """Add a research task to the queue."""
        task = {
            "type": "research",
            "query": query,
            "processor_config": processor_config
        }
        return self.task_coordinator.add_task_to_queue(task)
    
    def add_analysis_task(self, data: Dict[str, Any], analysis_type: str = "general") -> str:
        """Add an analysis task to the queue."""
        task = {
            "type": "analysis",
            "data": data,
            "analysis_type": analysis_type
        }
        return self.task_coordinator.add_task_to_queue(task)
    
    def add_content_task(self, data: Dict[str, Any], content_type: str = "report") -> str:
        """Add a content generation task to the queue."""
        task = {
            "type": "content",
            "data": data,
            "content_type": content_type
        }
        return self.task_coordinator.add_task_to_queue(task)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the current system status."""
        status = self.system_status.copy()
        status.update({
            "queue_status": self.task_coordinator.get_queue_status(),
            "knowledge_summary": self.shared_knowledge.get_knowledge_summary(),
            "workflow_history": self.workflow_engine.get_workflow_history()
        })
        return status
    
    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific agent."""
        if agent_name in self.agents:
            return self.agents[agent_name].get_status()
        return None
    
    def get_all_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """Get the status of all agents."""
        return {
            agent_name: agent.get_status()
            for agent_name, agent in self.agents.items()
        }
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific task."""
        return self.task_coordinator.get_task_status(task_id)
    
    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get a summary of all knowledge in the system."""
        return self.shared_knowledge.get_knowledge_summary()
    
    def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """Search through all system knowledge."""
        return self.shared_knowledge.search(query)
    
    def export_knowledge(self, format: str = "json") -> str:
        """Export all system knowledge."""
        return self.shared_knowledge.export_knowledge(format)
