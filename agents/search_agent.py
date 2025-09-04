"""Search Agent for information retrieval using Parallel.ai Search API."""

import asyncio
import os
from typing import Any, Dict, List, Optional
from parallel import AsyncParallel
from agents.base_agent import BaseAgent
from config import settings


class SearchAgent(BaseAgent):
    """Agent responsible for web search and information retrieval."""
    
    def __init__(self, shared_knowledge):
        super().__init__(
            name="SearchAgent",
            role="Information Retrieval Specialist",
            shared_knowledge=shared_knowledge
        )
        self.api_key = settings.parallel_api_key
        self.client = AsyncParallel(api_key=self.api_key)
    
    def _get_instructions(self) -> str:
        """Get search agent instructions."""
        return """
        You are a specialized search agent responsible for gathering information from the web.
        Your primary tasks include:
        1. Performing web searches using Parallel.ai Search API
        2. Extracting relevant information from search results
        3. Storing search results in the search memory
        4. Providing structured data to the analyst agent
        
        Always include sources and citations in your responses.
        Focus on accuracy and relevance of information.
        """
    
    async def search_web(self, query: str, processor: str = "base", 
                        max_results: int = 10) -> Dict[str, Any]:
        """Perform web search using Parallel.ai Search API."""
        try:
            # Use the parallel-web client for search
            search_result = await self.client.task_run.execute(
                input=query,
                processor=processor,
                output=f"Web search results for: {query}"
            )
            
            # Store in search memory  
            results_data = search_result.output if hasattr(search_result, 'output') else search_result
            self.shared_knowledge.search_memory.store_search_results(
                query, [results_data], processor
            )
            
            # Update shared knowledge
            self.update_shared_knowledge(
                f"search_{query}",
                search_result,
                {"processor": processor, "result_count": 1}
            )
            
            self.log_activity("web_search", {
                "query": query,
                "processor": processor,
                "results_count": 1
            })
            
            return {
                "results": results_data,
                "query": query,
                "processor": processor
            }
        
        except Exception as e:
            self.log_activity("web_search_error", {"query": query, "error": str(e)})
            raise
    
    async def search_multiple_queries(self, queries: List[str], 
                                    processor: str = "base") -> Dict[str, Any]:
        """Search multiple queries and aggregate results."""
        results = {}
        
        for query in queries:
            try:
                result = await self.search_web(query, processor)
                results[query] = result
            except Exception as e:
                results[query] = {"error": str(e)}
        
        # Store aggregated results
        self.update_shared_knowledge(
            "multi_search_results",
            results,
            {"query_count": len(queries), "processor": processor}
        )
        
        return results
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a search task."""
        task_type = task.get("type", "search")
        query = task.get("query", "")
        processor = task.get("processor", "base")
        
        if task_type == "search":
            result = await self.search_web(query, processor)
            return {
                "agent": self.name,
                "task_type": task_type,
                "query": query,
                "result": result,
                "status": "completed"
            }
        
        elif task_type == "multi_search":
            queries = task.get("queries", [])
            result = await self.search_multiple_queries(queries, processor)
            return {
                "agent": self.name,
                "task_type": task_type,
                "queries": queries,
                "result": result,
                "status": "completed"
            }
        
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    def get_search_history(self) -> List[Dict[str, Any]]:
        """Get search history from memory."""
        return self.shared_knowledge.search_memory.get_all_queries()
    
    def get_search_results(self, query: str) -> Optional[List[Dict]]:
        """Get search results for a specific query."""
        return self.shared_knowledge.search_memory.get_search_results(query)
