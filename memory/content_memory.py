"""Content memory for storing generated content and templates."""

from typing import Any, Dict, List, Optional
from datetime import datetime
from memory.base import BaseMemory


class ContentMemory(BaseMemory):
    """Memory component for storing generated content and templates."""
    
    def __init__(self):
        super().__init__("ContentMemory")
        self.templates: Dict[str, str] = {}
        self.generated_content: Dict[str, Dict[str, Any]] = {}
        self.formatted_content: Dict[str, str] = {}
    
    def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> None:
        """Store content data."""
        self.data[key] = value
        if metadata:
            self.metadata[key] = metadata
        self.updated_at = datetime.now()
    
    def store_template(self, template_id: str, template: str, template_type: str = "default") -> None:
        """Store content templates."""
        self.templates[template_id] = template
        self.metadata[f"template_{template_id}"] = {
            "template_type": template_type,
            "timestamp": datetime.now().isoformat(),
            "template_length": len(template)
        }
    
    def store_generated_content(self, content_id: str, content: str, content_type: str = "report") -> None:
        """Store generated content."""
        self.generated_content[content_id] = {
            "content": content,
            "content_type": content_type,
            "timestamp": datetime.now().isoformat()
        }
        self.metadata[f"generated_{content_id}"] = {
            "content_type": content_type,
            "word_count": len(content.split()),
            "char_count": len(content)
        }
    
    def store_formatted_content(self, format_id: str, formatted_content: str, format_type: str = "markdown") -> None:
        """Store formatted content."""
        self.formatted_content[format_id] = formatted_content
        self.metadata[f"formatted_{format_id}"] = {
            "format_type": format_type,
            "timestamp": datetime.now().isoformat(),
            "content_length": len(formatted_content)
        }
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from memory."""
        return self.data.get(key)
    
    def get_template(self, template_id: str) -> Optional[str]:
        """Get template by ID."""
        return self.templates.get(template_id)
    
    def get_generated_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get generated content by ID."""
        return self.generated_content.get(content_id)
    
    def get_formatted_content(self, format_id: str) -> Optional[str]:
        """Get formatted content by ID."""
        return self.formatted_content.get(format_id)
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search through stored content."""
        results = []
        
        # Search in templates
        for template_id, template in self.templates.items():
            if query.lower() in template.lower():
                results.append({
                    "type": "template",
                    "key": template_id,
                    "data": template,
                    "metadata": self.metadata.get(f"template_{template_id}")
                })
        
        # Search in generated content
        for content_id, content_data in self.generated_content.items():
            if query.lower() in content_data["content"].lower():
                results.append({
                    "type": "generated_content",
                    "key": content_id,
                    "data": content_data,
                    "metadata": self.metadata.get(f"generated_{content_id}")
                })
        
        return results
    
    def get_content_summary(self) -> Dict[str, Any]:
        """Get summary of content generation."""
        return {
            "total_templates": len(self.templates),
            "total_generated_content": len(self.generated_content),
            "total_formatted_content": len(self.formatted_content),
            "content_types": list(set(
                content["content_type"] for content in self.generated_content.values()
            ))
        }
    
    def get_all_template_ids(self) -> List[str]:
        """Get all template IDs."""
        return list(self.templates.keys())
    
    def get_all_content_ids(self) -> List[str]:
        """Get all generated content IDs."""
        return list(self.generated_content.keys())
    
    def get_templates_by_type(self, template_type: str) -> Dict[str, str]:
        """Get templates filtered by type."""
        return {
            template_id: template for template_id, template in self.templates.items()
            if self.metadata.get(f"template_{template_id}", {}).get("template_type") == template_type
        }
