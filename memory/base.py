"""Base memory class for all memory components."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import json


class BaseMemory(ABC):
    """Abstract base class for all memory components."""
    
    def __init__(self, name: str):
        self.name = name
        self.data: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    @abstractmethod
    def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> None:
        """Store data in memory."""
        pass
    
    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from memory."""
        pass
    
    @abstractmethod
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for data in memory."""
        pass
    
    def update_metadata(self, key: str, metadata: Dict[str, Any]) -> None:
        """Update metadata for a stored item."""
        if key in self.metadata:
            self.metadata[key].update(metadata)
        else:
            self.metadata[key] = metadata
        self.updated_at = datetime.now()
    
    def get_all_keys(self) -> List[str]:
        """Get all keys in memory."""
        return list(self.data.keys())
    
    def clear(self) -> None:
        """Clear all data from memory."""
        self.data.clear()
        self.metadata.clear()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary."""
        return {
            "name": self.name,
            "data": self.data,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
