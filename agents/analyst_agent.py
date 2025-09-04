"""Analyst Agent for data processing and analysis using Parallel.ai Task API."""

import asyncio
import os
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from parallel import AsyncParallel
from agents.base_agent import BaseAgent
from config import settings


class AnalysisResult(BaseModel):
    """Schema for analysis results."""
    summary: str = Field(description="Summary of the analysis")
    key_findings: List[str] = Field(description="Key findings from the analysis")
    insights: List[str] = Field(description="Insights derived from the data")
    confidence_score: float = Field(description="Confidence score (0-1)")
    data_sources: List[str] = Field(description="Sources of the analyzed data")


class AnalystAgent(BaseAgent):
    """Agent responsible for data analysis and processing."""
    
    def __init__(self, shared_knowledge):
        super().__init__(
            name="AnalystAgent",
            role="Data Analysis Specialist",
            shared_knowledge=shared_knowledge
        )
        self.api_key = settings.parallel_api_key
        self.client = AsyncParallel(api_key=self.api_key)
    
    def _get_instructions(self) -> str:
        """Get analyst agent instructions."""
        return """
        You are a specialized analyst agent responsible for processing and analyzing data.
        Your primary tasks include:
        1. Analyzing search results and raw data
        2. Extracting meaningful insights and patterns
        3. Performing structured data analysis using Parallel.ai Task API
        4. Storing analysis results in the analysis memory
        5. Providing processed data to the critic agent
        
        Focus on accuracy, objectivity, and data-driven insights.
        Always provide confidence scores for your analysis.
        """
    
    async def analyze_data(self, data: Dict[str, Any], analysis_type: str = "general",
                          processor: str = "core") -> Dict[str, Any]:
        """Analyze data using Parallel.ai Task API."""
        try:
            # Create analysis prompt
            analysis_prompt = self._create_analysis_prompt(data, analysis_type)
            
            # Use the parallel-web client for task execution
            task_result = await self.client.task_run.execute(
                input=analysis_prompt,
                processor=processor,
                output="Structured analysis results"
            )
            
            # Store in analysis memory
            analysis_id = f"analysis_{len(self.shared_knowledge.analysis_memory.get_all_analysis_ids())}"
            self.shared_knowledge.analysis_memory.store_analytics_result(
                analysis_id, task_result, analysis_type
            )
            
            # Update shared knowledge
            self.update_shared_knowledge(
                f"analysis_{analysis_id}",
                task_result,
                {"analysis_type": analysis_type, "processor": processor}
            )
            
            self.log_activity("data_analysis", {
                "analysis_type": analysis_type,
                "processor": processor,
                "analysis_id": analysis_id
            })
            
            return {
                "output": task_result.output,
                "processor": processor
            }
        
        except Exception as e:
            self.log_activity("analysis_error", {"analysis_type": analysis_type, "error": str(e)})
            raise
    
    def _create_analysis_prompt(self, data: Dict[str, Any], analysis_type: str) -> str:
        """Create analysis prompt based on data and analysis type."""
        if analysis_type == "search_results":
            return f"""
            Analyze the following search results and provide insights:
            
            Data: {data}
            
            Please provide:
            1. A comprehensive summary
            2. Key findings
            3. Insights and patterns
            4. Confidence score
            5. Data sources
            """
        
        elif analysis_type == "market_research":
            return f"""
            Perform market research analysis on the following data:
            
            Data: {data}
            
            Please provide:
            1. Market overview
            2. Key trends and patterns
            3. Competitive insights
            4. Opportunities and threats
            5. Confidence assessment
            """
        
        else:
            return f"""
            Analyze the following data and provide comprehensive insights:
            
            Data: {data}
            
            Please provide:
            1. Summary of findings
            2. Key insights
            3. Patterns and trends
            4. Confidence score
            5. Data sources
            """
    
    async def process_search_results(self, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Process search results from Search Agent."""
        analysis_result = await self.analyze_data(search_results, "search_results")
        
        # Extract insights
        insights = analysis_result.get("output", {}).get("parsed", {}).get("insights", [])
        topic = "search_analysis"
        self.shared_knowledge.analysis_memory.store_insights(topic, insights)
        
        return analysis_result
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process an analysis task."""
        task_type = task.get("type", "analyze")
        data = task.get("data", {})
        analysis_type = task.get("analysis_type", "general")
        processor = task.get("processor", "core")
        
        if task_type == "analyze":
            result = await self.analyze_data(data, analysis_type, processor)
            return {
                "agent": self.name,
                "task_type": task_type,
                "analysis_type": analysis_type,
                "result": result,
                "status": "completed"
            }
        
        elif task_type == "process_search":
            result = await self.process_search_results(data)
            return {
                "agent": self.name,
                "task_type": task_type,
                "result": result,
                "status": "completed"
            }
        
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    def get_analysis_history(self) -> List[str]:
        """Get analysis history from memory."""
        return self.shared_knowledge.analysis_memory.get_all_analysis_ids()
    
    def get_insights(self, topic: str) -> Optional[List[str]]:
        """Get insights for a specific topic."""
        return self.shared_knowledge.analysis_memory.get_insights(topic)
