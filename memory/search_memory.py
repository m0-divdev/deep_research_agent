"""Search memory for storing web search results and API data."""

from typing import Any, Dict, List, Optional
from datetime import datetime
from memory.base import BaseMemory


class SearchMemory(BaseMemory):
    """Memory component for storing search results and web data."""
    
    def __init__(self):
        super().__init__("SearchMemory")
        self.search_results: Dict[str, List[Dict]] = {}
        self.api_responses: Dict[str, Any] = {}
        self.parsed_data: Dict[str, Any] = {}
    
    def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> None:
        """Store search data."""
        self.data[key] = value
        if metadata:
            self.metadata[key] = metadata
        self.updated_at = datetime.now()
    
    def store_search_results(self, query: str, results: List[Dict], processor: str = "base") -> None:
        """Store search results from Parallel.ai Search API."""
        self.search_results[query] = results
        self.metadata[f"search_{query}"] = {
            "processor": processor,
            "result_count": len(results),
            "timestamp": datetime.now().isoformat()
        }
    
    def store_api_response(self, endpoint: str, response: Any) -> None:
        """Store API response data."""
        self.api_responses[endpoint] = response
        self.metadata[f"api_{endpoint}"] = {
            "timestamp": datetime.now().isoformat(),
            "response_type": type(response).__name__
        }
    
    def store_parsed_data(self, source: str, parsed_data: Any) -> None:
        """Store parsed data from web crawler or parser."""
        self.parsed_data[source] = parsed_data
        self.metadata[f"parsed_{source}"] = {
            "timestamp": datetime.now().isoformat(),
            "data_type": type(parsed_data).__name__
        }
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from memory."""
        return self.data.get(key)
    
    def get_search_results(self, query: str) -> Optional[List[Dict]]:
        """Get search results for a specific query."""
        return self.search_results.get(query)
    
    def get_api_response(self, endpoint: str) -> Optional[Any]:
        """Get API response for a specific endpoint."""
        return self.api_responses.get(endpoint)
    
    def get_parsed_data(self, source: str) -> Optional[Any]:
        """Get parsed data from a specific source."""
        return self.parsed_data.get(source)
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search through stored data."""
        results = []
        
        # Search in search results
        for search_query, results_data in self.search_results.items():
            if query.lower() in search_query.lower():
                results.append({
                    "type": "search_results",
                    "key": search_query,
                    "data": results_data,
                    "metadata": self.metadata.get(f"search_{search_query}")
                })
        
        # Search in parsed data
        for source, data in self.parsed_data.items():
            if query.lower() in source.lower():
                results.append({
                    "type": "parsed_data",
                    "key": source,
                    "data": data,
                    "metadata": self.metadata.get(f"parsed_{source}")
                })
        
        return results
    
    def get_all_queries(self) -> List[str]:
        """Get all stored search queries."""
        return list(self.search_results.keys())
    
    def get_all_sources(self) -> List[str]:
        """Get all parsed data sources."""
        return list(self.parsed_data.keys())
