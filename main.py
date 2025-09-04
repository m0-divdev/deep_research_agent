"""Main application for the Deep Research Multi-Agent System."""

import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv

from coordination.agent_orchestrator import AgentOrchestrator
from config import settings

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Deep Research Multi-Agent System",
    description="A multi-agent system for deep research using Agno and Parallel.ai",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the orchestrator
orchestrator = AgentOrchestrator()

# Pydantic models for API
class ResearchRequest(BaseModel):
    query: str
    processor_config: Optional[Dict[str, str]] = None

class AnalysisRequest(BaseModel):
    data: Dict[str, Any]
    analysis_type: str = "general"

class ContentRequest(BaseModel):
    data: Dict[str, Any]
    content_type: str = "report"

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class SystemStatus(BaseModel):
    status: str
    agents: List[str]
    queue_status: Dict[str, Any]
    knowledge_summary: Dict[str, Any]

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup."""
    await orchestrator.start_system()
    print("Deep Research Multi-Agent System started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown the system."""
    await orchestrator.stop_system()
    print("Deep Research Multi-Agent System stopped.")

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Deep Research Multi-Agent System",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": orchestrator.system_status.get("started_at")}

@app.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Get the current system status."""
    status = orchestrator.get_system_status()
    return SystemStatus(**status)

@app.post("/research")
async def research(request: ResearchRequest):
    """Perform a complete research task."""
    try:
        result = await orchestrator.research(request.query, request.processor_config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/research/async", response_model=TaskResponse)
async def research_async(request: ResearchRequest):
    """Add a research task to the queue for asynchronous processing."""
    try:
        task_id = orchestrator.add_research_task(request.query, request.processor_config)
        return TaskResponse(
            task_id=task_id,
            status="queued",
            message="Research task added to queue"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    """Perform data analysis."""
    try:
        result = await orchestrator.analyze_data(request.data, request.analysis_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/async", response_model=TaskResponse)
async def analyze_async(request: AnalysisRequest):
    """Add an analysis task to the queue for asynchronous processing."""
    try:
        task_id = orchestrator.add_analysis_task(request.data, request.analysis_type)
        return TaskResponse(
            task_id=task_id,
            status="queued",
            message="Analysis task added to queue"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
async def generate_content(request: ContentRequest):
    """Generate content."""
    try:
        result = await orchestrator.generate_content(request.data, request.content_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/async", response_model=TaskResponse)
async def generate_content_async(request: ContentRequest):
    """Add a content generation task to the queue for asynchronous processing."""
    try:
        task_id = orchestrator.add_content_task(request.data, request.content_type)
        return TaskResponse(
            task_id=task_id,
            status="queued",
            message="Content generation task added to queue"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a specific task."""
    status = orchestrator.get_task_status(task_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return status

@app.get("/agents")
async def get_agents():
    """Get information about all agents."""
    return orchestrator.get_all_agent_status()

@app.get("/agents/{agent_name}")
async def get_agent_status(agent_name: str):
    """Get the status of a specific agent."""
    status = orchestrator.get_agent_status(agent_name)
    if status is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return status

@app.get("/knowledge")
async def get_knowledge_summary():
    """Get a summary of all knowledge in the system."""
    return orchestrator.get_knowledge_summary()

@app.get("/knowledge/search")
async def search_knowledge(q: str):
    """Search through all system knowledge."""
    results = orchestrator.search_knowledge(q)
    return {"query": q, "results": results}

@app.get("/knowledge/export")
async def export_knowledge(format: str = "json"):
    """Export all system knowledge."""
    try:
        exported_data = orchestrator.export_knowledge(format)
        return {"format": format, "data": exported_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflows")
async def get_workflows():
    """Get available workflows."""
    return {
        "available_workflows": orchestrator.workflow_engine.get_available_workflows(),
        "workflow_history": orchestrator.workflow_engine.get_workflow_history()
    }

@app.get("/workflows/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get the status of a specific workflow."""
    status = orchestrator.workflow_engine.get_workflow_status(workflow_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return status

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
