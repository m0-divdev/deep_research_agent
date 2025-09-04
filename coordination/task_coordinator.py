"""Task coordinator for managing agent tasks and communication."""

import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime
from coordination.workflow_engine import WorkflowEngine, WorkflowStep


class TaskCoordinator:
    """Coordinates tasks between agents without a message bus."""
    
    def __init__(self, workflow_engine: WorkflowEngine):
        self.workflow_engine = workflow_engine
        self.task_queue: List[Dict[str, Any]] = []
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.task_history: List[Dict[str, Any]] = []
    
    def create_research_workflow(self, research_query: str, 
                                processor_config: Optional[Dict[str, str]] = None) -> str:
        """Create a complete research workflow."""
        processor_config = processor_config or {
            "search": "base",
            "analysis": "core", 
            "verification": "pro",
            "content": "lite"
        }
        
        workflow_id = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Complete research pipeline with all agents
        steps = [
            {
                "step_id": "search_step",
                "agent_name": "SearchAgent",
                "task": {
                    "type": "search",
                    "query": research_query,
                    "processor": processor_config["search"]
                },
                "dependencies": []
            },
            {
                "step_id": "analysis_step",
                "agent_name": "AnalystAgent",
                "task": {
                    "type": "analyze",
                    "data": None,  # Will be populated from search step
                    "analysis_type": "research_analysis"
                },
                "dependencies": ["search_step"]
            },
            {
                "step_id": "verification_step",
                "agent_name": "CriticAgent",
                "task": {
                    "type": "validate",
                    "data": None  # Will be populated from analysis step
                },
                "dependencies": ["analysis_step"]
            },
            {
                "step_id": "content_step",
                "agent_name": "WriterAgent",
                "task": {
                    "type": "generate",
                    "data": None,  # Will be populated from verification step
                    "content_type": "research_report"
                },
                "dependencies": ["verification_step"]
            }
        ]
        
        return self.workflow_engine.create_workflow(workflow_id, steps)
    
    def create_analysis_workflow(self, data: Dict[str, Any], 
                                analysis_type: str = "general") -> str:
        """Create an analysis-only workflow."""
        workflow_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        steps = [
            {
                "step_id": "analysis_step",
                "agent_name": "AnalystAgent",
                "task": {
                    "type": "analyze",
                    "data": data,
                    "analysis_type": analysis_type
                },
                "dependencies": []
            },
            {
                "step_id": "verification_step",
                "agent_name": "CriticAgent",
                "task": {
                    "type": "validate",
                    "data": None  # Will be populated from previous step
                },
                "dependencies": ["analysis_step"]
            }
        ]
        
        return self.workflow_engine.create_workflow(workflow_id, steps)
    
    def create_content_workflow(self, data: Dict[str, Any], 
                               content_type: str = "report") -> str:
        """Create a content generation workflow."""
        workflow_id = f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        steps = [
            {
                "step_id": "content_step",
                "agent_name": "WriterAgent",
                "task": {
                    "type": "generate",
                    "data": data,
                    "content_type": content_type
                },
                "dependencies": []
            }
        ]
        
        return self.workflow_engine.create_workflow(workflow_id, steps)
    
    async def execute_research_task(self, query: str, agents: Dict[str, Any],
                                   processor_config: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Execute a complete research task."""
        workflow_id = self.create_research_workflow(query, processor_config)
        return await self.workflow_engine.execute_workflow(workflow_id, agents)
    
    async def execute_analysis_task(self, data: Dict[str, Any], agents: Dict[str, Any],
                                   analysis_type: str = "general") -> Dict[str, Any]:
        """Execute an analysis task."""
        workflow_id = self.create_analysis_workflow(data, analysis_type)
        return await self.workflow_engine.execute_workflow(workflow_id, agents)
    
    async def execute_content_task(self, data: Dict[str, Any], agents: Dict[str, Any],
                                  content_type: str = "report") -> Dict[str, Any]:
        """Execute a content generation task."""
        workflow_id = self.create_content_workflow(data, content_type)
        return await self.workflow_engine.execute_workflow(workflow_id, agents)
    
    def add_task_to_queue(self, task: Dict[str, Any]) -> str:
        """Add a task to the execution queue."""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        task["task_id"] = task_id
        task["created_at"] = datetime.now().isoformat()
        task["status"] = "queued"
        
        self.task_queue.append(task)
        return task_id
    
    async def process_task_queue(self, agents: Dict[str, Any]) -> None:
        """Process tasks in the queue."""
        while self.task_queue:
            task = self.task_queue.pop(0)
            task_id = task["task_id"]
            
            try:
                self.active_tasks[task_id] = task
                task["status"] = "processing"
                task["started_at"] = datetime.now().isoformat()
                
                # Determine task type and execute appropriate workflow
                task_type = task.get("type", "research")
                
                if task_type == "research":
                    result = await self.execute_research_task(
                        task["query"], agents, task.get("processor_config")
                    )
                elif task_type == "analysis":
                    result = await self.execute_analysis_task(
                        task["data"], agents, task.get("analysis_type", "general")
                    )
                elif task_type == "content":
                    result = await self.execute_content_task(
                        task["data"], agents, task.get("content_type", "report")
                    )
                else:
                    raise ValueError(f"Unknown task type: {task_type}")
                
                task["status"] = "completed"
                task["result"] = result
                task["completed_at"] = datetime.now().isoformat()
                
            except Exception as e:
                task["status"] = "failed"
                task["error"] = str(e)
                task["completed_at"] = datetime.now().isoformat()
            
            finally:
                # Move to history
                self.task_history.append(task)
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific task."""
        # Check active tasks
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        # Check history
        for task in self.task_history:
            if task["task_id"] == task_id:
                return task
        
        return None
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get the current status of the task queue."""
        return {
            "queue_length": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.task_history),
            "queue": [task["task_id"] for task in self.task_queue],
            "active": list(self.active_tasks.keys())
        }
    
    def get_task_history(self) -> List[Dict[str, Any]]:
        """Get task execution history."""
        return self.task_history
