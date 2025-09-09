"""Shared knowledge repository for persistent storage of all system knowledge."""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json
from memory.base import BaseMemory
from memory.search_memory import SearchMemory
from memory.analysis_memory import AnalysisMemory
from memory.verification_memory import VerificationMemory
from memory.content_memory import ContentMemory


class SharedKnowledgeRepository(BaseMemory):
    """Central repository for all system knowledge and data."""
    
    def __init__(self):
        super().__init__("SharedKnowledgeRepository")
        self.knowledge_graph: Dict[str, Dict[str, Any]] = {}
        self.relationships: Dict[str, List[str]] = {}
        self.knowledge_sources: Dict[str, str] = {}
        
        # Initialize memory components
        self.search_memory = SearchMemory()
        self.analysis_memory = AnalysisMemory()
        self.verification_memory = VerificationMemory()
        self.content_memory = ContentMemory()
    
    def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> None:
        """Store knowledge in the repository."""
        self.data[key] = value
        if metadata:
            self.metadata[key] = metadata
        self.updated_at = datetime.now()
    
    def add_knowledge_node(self, node_id: str, node_data: Dict[str, Any], 
                          source: str = "unknown") -> None:
        """Add a knowledge node to the repository."""
        self.knowledge_graph[node_id] = {
            "data": node_data,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "access_count": 0
        }
        self.knowledge_sources[node_id] = source
        self.metadata[f"node_{node_id}"] = {
            "source": source,
            "created_at": datetime.now().isoformat(),
            "data_type": type(node_data).__name__
        }
    
    def add_relationship(self, from_node: str, to_node: str, 
                        relationship_type: str = "related") -> None:
        """Add a relationship between knowledge nodes."""
        if from_node not in self.relationships:
            self.relationships[from_node] = []
        
        relationship = {
            "target": to_node,
            "type": relationship_type,
            "timestamp": datetime.now().isoformat()
        }
        self.relationships[from_node].append(relationship)
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from the repository."""
        return self.data.get(key)
    
    def get_knowledge_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a knowledge node by ID."""
        if node_id in self.knowledge_graph:
            # Increment access count
            self.knowledge_graph[node_id]["access_count"] += 1
            return self.knowledge_graph[node_id]
        return None
    
    def get_relationships(self, node_id: str) -> List[Dict[str, Any]]:
        """Get relationships for a specific node."""
        return self.relationships.get(node_id, [])
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search through all knowledge in the repository."""
        results = []
        
        # Search in knowledge graph
        for node_id, node_data in self.knowledge_graph.items():
            if query.lower() in node_id.lower() or \
               query.lower() in str(node_data["data"]).lower():
                results.append({
                    "type": "knowledge_node",
                    "key": node_id,
                    "data": node_data,
                    "metadata": self.metadata.get(f"node_{node_id}")
                })
        
        # Search in all memory components
        results.extend(self.search_memory.search(query))
        results.extend(self.analysis_memory.search(query))
        results.extend(self.verification_memory.search(query))
        results.extend(self.content_memory.search(query))
        
        return results
    
    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of all knowledge."""
        return {
            "total_knowledge_nodes": len(self.knowledge_graph),
            "total_relationships": sum(len(rels) for rels in self.relationships.values()),
            "search_memory": {
                "queries": len(self.search_memory.get_all_queries()),
                "sources": len(self.search_memory.get_all_sources())
            },
            "analysis_memory": {
                "analysis_results": len(self.analysis_memory.get_all_analysis_ids()),
                "topics": len(self.analysis_memory.get_all_topics())
            },
            "verification_memory": self.verification_memory.get_verification_summary(),
            "content_memory": self.content_memory.get_content_summary(),
            "sources": list(set(self.knowledge_sources.values()))
        }
    
    def export_knowledge(self, format: str = "json") -> str:
        """Export all knowledge in specified format."""
        if format == "json":
            return json.dumps({
                "knowledge_graph": self.knowledge_graph,
                "relationships": self.relationships,
                "search_memory": self.search_memory.to_dict(),
                "analysis_memory": self.analysis_memory.to_dict(),
                "verification_memory": self.verification_memory.to_dict(),
                "content_memory": self.content_memory.to_dict(),
                "metadata": self.metadata
            }, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_knowledge(self, data: str, format: str = "json") -> None:
        """Import knowledge from specified format."""
        if format == "json":
            imported_data = json.loads(data)
            self.knowledge_graph.update(imported_data.get("knowledge_graph", {}))
            self.relationships.update(imported_data.get("relationships", {}))
            # Note: Memory components would need individual import methods
        else:
            raise ValueError(f"Unsupported import format: {format}")
    
    def get_most_accessed_nodes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently accessed knowledge nodes."""
        nodes_with_access = [
            (node_id, node_data["access_count"])
            for node_id, node_data in self.knowledge_graph.items()
        ]
        nodes_with_access.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {
                "node_id": node_id,
                "access_count": access_count,
                "data": self.knowledge_graph[node_id]
            }
            for node_id, access_count in nodes_with_access[:limit]
        ]
