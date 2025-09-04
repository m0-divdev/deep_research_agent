"""Writer Agent for content generation using Parallel.ai Chat API."""

import asyncio
import os
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from parallel import AsyncParallel
from agents.base_agent import BaseAgent
from config import settings


class ContentTemplate(BaseModel):
    """Schema for content templates."""
    title: str = Field(description="Title of the content")
    introduction: str = Field(description="Introduction section")
    main_content: str = Field(description="Main content sections")
    conclusion: str = Field(description="Conclusion section")
    sources: List[str] = Field(description="List of sources")
    metadata: Dict[str, Any] = Field(description="Additional metadata")


class WriterAgent(BaseAgent):
    """Agent responsible for content generation and formatting."""
    
    def __init__(self, shared_knowledge):
        super().__init__(
            name="WriterAgent",
            role="Content Generation Specialist",
            shared_knowledge=shared_knowledge
        )
        self.api_key = settings.parallel_api_key
        self.client = AsyncParallel(api_key=self.api_key)
    
    def _get_instructions(self) -> str:
        """Get writer agent instructions."""
        return """
        You are a specialized writer agent responsible for content generation and formatting.
        Your primary tasks include:
        1. Generating comprehensive reports and content
        2. Using templates for consistent formatting
        3. Creating content using Parallel.ai Chat API
        4. Storing generated content in the content memory
        5. Formatting content for different output types
        
        Focus on clarity, accuracy, and engaging content.
        Always include proper citations and sources.
        """
    
    async def generate_content(self, data: Dict[str, Any], content_type: str = "report",
                              template_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate content using Parallel.ai Task API."""
        try:
            # Create content generation prompt
            prompt = self._create_content_prompt(data, content_type, template_id)
            
            # Use the parallel-web client for task execution
            task_result = await self.client.task_run.execute(
                input=prompt,
                processor="lite",  # Use lite processor for content generation
                output="Comprehensive research report with citations"
            )
            
            # Extract content from response
            content = str(task_result.output) if hasattr(task_result.output, '__str__') else str(task_result.output)
            
            # Store in content memory
            content_id = f"content_{len(self.shared_knowledge.content_memory.get_all_content_ids())}"
            self.shared_knowledge.content_memory.store_generated_content(
                content_id, content, content_type
            )
            
            # Update shared knowledge
            self.update_shared_knowledge(
                f"generated_content_{content_id}",
                task_result,
                {"content_type": content_type, "template_id": template_id}
            )
            
            self.log_activity("content_generation", {
                "content_type": content_type,
                "template_id": template_id,
                "content_id": content_id
            })
            
            return {
                "output": task_result.output,
                "content": content
            }
        
        except Exception as e:
            self.log_activity("content_generation_error", {
                "content_type": content_type, 
                "error": str(e)
            })
            raise
    
    def _create_content_prompt(self, data: Dict[str, Any], content_type: str,
                              template_id: Optional[str] = None) -> str:
        """Create content generation prompt."""
        base_prompt = f"""
        Generate a comprehensive {content_type} based on the following data:
        
        Data: {data}
        """
        
        if template_id:
            template = self.shared_knowledge.content_memory.get_template(template_id)
            if template:
                base_prompt += f"\n\nUse the following template as a guide:\n{template}"
        
        base_prompt += f"""
        
        Please create a well-structured {content_type} that includes:
        1. A compelling title
        2. An engaging introduction
        3. Detailed main content with clear sections
        4. A strong conclusion
        5. Proper citations and sources
        6. Relevant metadata
        
        Ensure the content is accurate, well-organized, and engaging.
        """
        
        return base_prompt
    
    async def format_content(self, content: str, format_type: str = "markdown") -> str:
        """Format content for different output types."""
        if format_type == "markdown":
            # Basic markdown formatting
            formatted = content.replace("\n\n", "\n\n---\n\n")
        elif format_type == "html":
            # Basic HTML formatting
            formatted = f"<div class='content'>{content}</div>"
        elif format_type == "plain":
            # Plain text formatting
            formatted = content
        else:
            formatted = content
        
        # Store formatted content
        format_id = f"format_{len(self.shared_knowledge.content_memory.get_all_content_ids())}"
        self.shared_knowledge.content_memory.store_formatted_content(
            format_id, formatted, format_type
        )
        
        return formatted
    
    def create_template(self, template_id: str, template: str, template_type: str = "report") -> None:
        """Create a content template."""
        self.shared_knowledge.content_memory.store_template(template_id, template, template_type)
        self.log_activity("template_creation", {
            "template_id": template_id,
            "template_type": template_type
        })
    
    async def process_verified_data(self, verified_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process verified data from Critic Agent to generate content."""
        # Extract key information from verified data
        content_data = {
            "verified_claims": verified_data.get("verified_claims", []),
            "analysis_results": verified_data.get("analysis_results", {}),
            "verification_summary": verified_data.get("verification_summary", {}),
            "sources": verified_data.get("sources", [])
        }
        
        # Generate content
        result = await self.generate_content(content_data, "research_report")
        
        return result
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a content generation task."""
        task_type = task.get("type", "generate")
        data = task.get("data", {})
        content_type = task.get("content_type", "report")
        template_id = task.get("template_id")
        format_type = task.get("format_type", "markdown")
        
        if task_type == "generate":
            result = await self.generate_content(data, content_type, template_id)
            return {
                "agent": self.name,
                "task_type": task_type,
                "content_type": content_type,
                "result": result,
                "status": "completed"
            }
        
        elif task_type == "format":
            content = data.get("content", "")
            formatted_content = await self.format_content(content, format_type)
            return {
                "agent": self.name,
                "task_type": task_type,
                "format_type": format_type,
                "result": {"formatted_content": formatted_content},
                "status": "completed"
            }
        
        elif task_type == "process_verified":
            result = await self.process_verified_data(data)
            return {
                "agent": self.name,
                "task_type": task_type,
                "result": result,
                "status": "completed"
            }
        
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    def get_content_summary(self) -> Dict[str, Any]:
        """Get content generation summary from memory."""
        return self.shared_knowledge.content_memory.get_content_summary()
    
    def get_available_templates(self) -> List[str]:
        """Get list of available templates."""
        return self.shared_knowledge.content_memory.get_all_template_ids()
