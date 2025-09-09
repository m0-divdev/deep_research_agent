"""Analysis memory for storing processed data and analytics results."""

from typing import Any, Dict, List, Optional
from datetime import datetime
from memory.base import BaseMemory


class AnalysisMemory(BaseMemory):
    """Memory component for storing analysis results and processed data."""
    
    def __init__(self):
        super().__init__("AnalysisMemory")
        self.analytics_results: Dict[str, Any] = {}
        self.processed_data: Dict[str, Any] = {}
        self.insights: Dict[str, List[str]] = {}
    
    def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> None:
        """Store analysis data."""
        self.data[key] = value
        if metadata:
            self.metadata[key] = metadata
        self.updated_at = datetime.now()
    
    def store_analytics_result(self, analysis_id: str, result: Any, method: str = "default") -> None:
        """Store analytics processing results."""
        self.analytics_results[analysis_id] = result
        self.metadata[f"analytics_{analysis_id}"] = {
            "method": method,
            "timestamp": datetime.now().isoformat(),
            "result_type": type(result).__name__
        }
    
    def store_processed_data(self, data_id: str, processed_data: Any, processing_type: str = "default") -> None:
        """Store processed/transformed data."""
        self.processed_data[data_id] = processed_data
        self.metadata[f"processed_{data_id}"] = {
            "processing_type": processing_type,
            "timestamp": datetime.now().isoformat(),
            "data_type": type(processed_data).__name__
        }
    
    def store_insights(self, topic: str, insights: List[str], confidence: float = 0.0) -> None:
        """Store extracted insights."""
        self.insights[topic] = insights
        self.metadata[f"insights_{topic}"] = {
            "confidence": confidence,
            "insight_count": len(insights),
            "timestamp": datetime.now().isoformat()
        }
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from memory."""
        return self.data.get(key)
    
    def get_analytics_result(self, analysis_id: str) -> Optional[Any]:
        """Get analytics result by ID."""
        return self.analytics_results.get(analysis_id)
    
    def get_processed_data(self, data_id: str) -> Optional[Any]:
        """Get processed data by ID."""
        return self.processed_data.get(data_id)
    
    def get_insights(self, topic: str) -> Optional[List[str]]:
        """Get insights for a specific topic."""
        return self.insights.get(topic)
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search through stored analysis data."""
        results = []
        
        # Search in analytics results
        for analysis_id, result in self.analytics_results.items():
            if query.lower() in analysis_id.lower():
                results.append({
                    "type": "analytics_result",
                    "key": analysis_id,
                    "data": result,
                    "metadata": self.metadata.get(f"analytics_{analysis_id}")
                })
        
        # Search in insights
        for topic, insights_list in self.insights.items():
            if query.lower() in topic.lower():
                results.append({
                    "type": "insights",
                    "key": topic,
                    "data": insights_list,
                    "metadata": self.metadata.get(f"insights_{topic}")
                })
        
        return results
    
    def get_all_analysis_ids(self) -> List[str]:
        """Get all analytics analysis IDs."""
        return list(self.analytics_results.keys())
    
    def get_all_topics(self) -> List[str]:
        """Get all insight topics."""
        return list(self.insights.keys())
    
    def get_insights_summary(self) -> Dict[str, int]:
        """Get summary of insights by topic."""
        return {topic: len(insights) for topic, insights in self.insights.items()}
