"""Verification memory for storing fact-checking and validation results."""

from typing import Any, Dict, List, Optional
from datetime import datetime
from memory.base import BaseMemory


class VerificationMemory(BaseMemory):
    """Memory component for storing verification and validation results."""
    
    def __init__(self):
        super().__init__("VerificationMemory")
        self.fact_checks: Dict[str, Dict[str, Any]] = {}
        self.validations: Dict[str, Dict[str, Any]] = {}
        self.cross_references: Dict[str, List[str]] = {}
    
    def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> None:
        """Store verification data."""
        self.data[key] = value
        if metadata:
            self.metadata[key] = metadata
        self.updated_at = datetime.now()
    
    def store_fact_check(self, claim_id: str, claim: str, result: Dict[str, Any]) -> None:
        """Store fact-checking results."""
        self.fact_checks[claim_id] = {
            "claim": claim,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        self.metadata[f"fact_check_{claim_id}"] = {
            "verification_status": result.get("status", "unknown"),
            "confidence": result.get("confidence", 0.0),
            "sources_count": len(result.get("sources", []))
        }
    
    def store_validation(self, data_id: str, validation_result: Dict[str, Any]) -> None:
        """Store data validation results."""
        self.validations[data_id] = validation_result
        self.metadata[f"validation_{data_id}"] = {
            "is_valid": validation_result.get("is_valid", False),
            "validation_type": validation_result.get("type", "unknown"),
            "timestamp": datetime.now().isoformat()
        }
    
    def store_cross_reference(self, topic: str, sources: List[str]) -> None:
        """Store cross-reference information."""
        self.cross_references[topic] = sources
        self.metadata[f"cross_ref_{topic}"] = {
            "source_count": len(sources),
            "timestamp": datetime.now().isoformat()
        }
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from memory."""
        return self.data.get(key)
    
    def get_fact_check(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """Get fact-check result by claim ID."""
        return self.fact_checks.get(claim_id)
    
    def get_validation(self, data_id: str) -> Optional[Dict[str, Any]]:
        """Get validation result by data ID."""
        return self.validations.get(data_id)
    
    def get_cross_reference(self, topic: str) -> Optional[List[str]]:
        """Get cross-reference sources for a topic."""
        return self.cross_references.get(topic)
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search through stored verification data."""
        results = []
        
        # Search in fact checks
        for claim_id, fact_check in self.fact_checks.items():
            if query.lower() in fact_check["claim"].lower():
                results.append({
                    "type": "fact_check",
                    "key": claim_id,
                    "data": fact_check,
                    "metadata": self.metadata.get(f"fact_check_{claim_id}")
                })
        
        # Search in validations
        for data_id, validation in self.validations.items():
            if query.lower() in data_id.lower():
                results.append({
                    "type": "validation",
                    "key": data_id,
                    "data": validation,
                    "metadata": self.metadata.get(f"validation_{data_id}")
                })
        
        return results
    
    def get_verification_summary(self) -> Dict[str, Any]:
        """Get summary of verification results."""
        total_fact_checks = len(self.fact_checks)
        total_validations = len(self.validations)
        
        verified_claims = sum(1 for fc in self.fact_checks.values() 
                            if fc["result"].get("status") == "verified")
        valid_data = sum(1 for v in self.validations.values() 
                        if v.get("is_valid", False))
        
        return {
            "total_fact_checks": total_fact_checks,
            "verified_claims": verified_claims,
            "total_validations": total_validations,
            "valid_data": valid_data,
            "verification_rate": verified_claims / total_fact_checks if total_fact_checks > 0 else 0,
            "validation_rate": valid_data / total_validations if total_validations > 0 else 0
        }
    
    def get_all_claim_ids(self) -> List[str]:
        """Get all fact-check claim IDs."""
        return list(self.fact_checks.keys())
    
    def get_all_data_ids(self) -> List[str]:
        """Get all validation data IDs."""
        return list(self.validations.keys())
