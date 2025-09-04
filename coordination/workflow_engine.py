"""Workflow engine for orchestrating multi-agent tasks."""

import asyncio
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStep:
    """Represents a single step in a workflow."""
    
    def __init__(self, step_id: str, agent_name: str, task: Dict[str, Any],
                 dependencies: Optional[List[str]] = None):
        self.step_id = step_id
        self.agent_name = agent_name
        self.task = task
        self.dependencies = dependencies or []
        self.status = TaskStatus.PENDING
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None


class WorkflowEngine:
    """Engine for managing and executing multi-agent workflows."""
    
    def __init__(self):
        self.workflows: Dict[str, List[WorkflowStep]] = {}
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.workflow_history: List[Dict[str, Any]] = []
    
    def create_workflow(self, workflow_id: str, steps: List[Dict[str, Any]]) -> str:
        """Create a new workflow."""
        workflow_steps = []
        
        for step_config in steps:
            step = WorkflowStep(
                step_id=step_config["step_id"],
                agent_name=step_config["agent_name"],
                task=step_config["task"],
                dependencies=step_config.get("dependencies", [])
            )
            workflow_steps.append(step)
        
        self.workflows[workflow_id] = workflow_steps
        return workflow_id
    
    async def execute_workflow(self, workflow_id: str, agents: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow with the given agents."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow_steps = self.workflows[workflow_id]
        self.active_workflows[workflow_id] = {
            "status": "running",
            "started_at": datetime.now(),
            "steps": {step.step_id: step for step in workflow_steps}
        }
        
        try:
            # Execute steps in dependency order
            results = await self._execute_steps(workflow_steps, agents)
            
            # Mark workflow as completed
            self.active_workflows[workflow_id]["status"] = "completed"
            self.active_workflows[workflow_id]["completed_at"] = datetime.now()
            
            # Store in history
            self.workflow_history.append({
                "workflow_id": workflow_id,
                "status": "completed",
                "started_at": self.active_workflows[workflow_id]["started_at"].isoformat(),
                "completed_at": self.active_workflows[workflow_id]["completed_at"].isoformat(),
                "results": results
            })
            
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "results": results
            }
        
        except Exception as e:
            # Mark workflow as failed
            self.active_workflows[workflow_id]["status"] = "failed"
            self.active_workflows[workflow_id]["error"] = str(e)
            
            # Store in history
            self.workflow_history.append({
                "workflow_id": workflow_id,
                "status": "failed",
                "started_at": self.active_workflows[workflow_id]["started_at"].isoformat(),
                "error": str(e)
            })
            
            raise
    
    async def _execute_steps(self, steps: List[WorkflowStep], agents: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow steps in dependency order."""
        results = {}
        completed_steps = set()
        
        # Debug: Print step information
        print(f"🔄 Executing workflow with {len(steps)} steps:")
        for step in steps:
            print(f"  📝 Step: {step.step_id}, Dependencies: {step.dependencies}, Agent: {step.agent_name}")
        
        while len(completed_steps) < len(steps):
            # Find steps that can be executed (dependencies satisfied)
            ready_steps = []
            for step in steps:
                if (step.status == TaskStatus.PENDING and 
                    all(dep in completed_steps for dep in step.dependencies)):
                    ready_steps.append(step)
            
            print(f"  ✅ Ready steps: {[s.step_id for s in ready_steps]}")
            print(f"  ✔️  Completed steps: {completed_steps}")
            
            if not ready_steps:
                # Check for circular dependencies or missing dependencies
                remaining_steps = [s for s in steps if s.status == TaskStatus.PENDING]
                if remaining_steps:
                    print(f"Remaining steps: {[s.step_id for s in remaining_steps]}")
                    for step in remaining_steps:
                        missing_deps = [dep for dep in step.dependencies if dep not in completed_steps]
                        print(f"  {step.step_id} missing dependencies: {missing_deps}")
                    raise Exception(f"Circular dependency or missing dependency in workflow")
                break
            
            # Execute ready steps in parallel
            tasks = []
            for step in ready_steps:
                if step.agent_name in agents:
                    # Get previous results for this step
                    previous_results = None
                    if step.dependencies:
                        # Get the result from the last dependency
                        last_dependency = step.dependencies[-1]
                        if last_dependency in results:
                            previous_results = results[last_dependency]
                    
                    task = self._execute_step(step, agents[step.agent_name], previous_results)
                    tasks.append(task)
                else:
                    step.status = TaskStatus.FAILED
                    step.error = f"Agent {step.agent_name} not found"
            
            if tasks:
                step_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(step_results):
                    step = ready_steps[i]
                    if isinstance(result, Exception):
                        step.status = TaskStatus.FAILED
                        step.error = str(result)
                        print(f"  ❌ Step {step.step_id} failed: {step.error}")
                    else:
                        step.status = TaskStatus.COMPLETED
                        step.result = result
                        results[step.step_id] = result
                        completed_steps.add(step.step_id)
                        print(f"  ✅ Step {step.step_id} completed successfully")
        
        return results
    
    async def _execute_step(self, step: WorkflowStep, agent: Any, previous_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a single workflow step."""
        step.status = TaskStatus.IN_PROGRESS
        step.started_at = datetime.now()
        
        try:
            # Update task data with previous results if needed
            task_data = step.task.copy()
            if task_data.get("data") is None and previous_results:
                # Pass the result from the previous step
                task_data["data"] = previous_results
            
            result = await agent.process_task(task_data)
            step.completed_at = datetime.now()
            return result
        except Exception as e:
            step.status = TaskStatus.FAILED
            step.error = str(e)
            step.completed_at = datetime.now()
            raise
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow."""
        if workflow_id in self.active_workflows:
            return self.active_workflows[workflow_id]
        return None
    
    def get_workflow_history(self) -> List[Dict[str, Any]]:
        """Get workflow execution history."""
        return self.workflow_history
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id]["status"] = "cancelled"
            return True
        return False
    
    def get_available_workflows(self) -> List[str]:
        """Get list of available workflows."""
        return list(self.workflows.keys())
