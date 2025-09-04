"""Critic Agent for verification and fact-checking using Parallel.ai Task API."""

import asyncio
import os
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from parallel import AsyncParallel
from agents.base_agent import BaseAgent
from config import settings


class VerificationResult(BaseModel):
    """Schema for verification results."""
    claim: str = Field(description="The claim being verified")
    status: str = Field(description="Verification status: verified, disputed, unverified")
    confidence: float = Field(description="Confidence score (0-1)")
    evidence: List[str] = Field(description="Supporting or contradicting evidence")
    sources: List[str] = Field(description="Sources used for verification")
    reasoning: str = Field(description="Explanation of verification reasoning")


class CriticAgent(BaseAgent):
    """Agent responsible for verification and fact-checking."""
    
    def __init__(self, shared_knowledge):
        super().__init__(
            name="CriticAgent",
            role="Verification and Fact-Checking Specialist",
            shared_knowledge=shared_knowledge
        )
        self.api_key = settings.parallel_api_key
        self.client = AsyncParallel(api_key=self.api_key)
    
    def _get_instructions(self) -> str:
        """Get critic agent instructions."""
        return """
        You are a specialized critic agent responsible for verification and fact-checking.
        Your primary tasks include:
        1. Verifying claims and facts from analysis results
        2. Cross-referencing information from multiple sources
        3. Performing fact-checking using Parallel.ai Task API
        4. Storing verification results in the verification memory
        5. Providing validated data to the writer agent
        
        Focus on accuracy, objectivity, and thorough verification.
        Always provide evidence and reasoning for your conclusions.
        """
    
    async def verify_claim(self, claim: str, context: Optional[str] = None,
                          processor: str = "pro") -> Dict[str, Any]:
        """Verify a claim using Parallel.ai Task API."""
        try:
            # Create verification prompt
            verification_prompt = self._create_verification_prompt(claim, context)
            
            # Use the parallel-web client for task execution
            task_result = await self.client.task_run.execute(
                input=verification_prompt,
                processor=processor,
                output="Verification results with evidence and confidence scores"
            )
            
            # Store in verification memory
            claim_id = f"claim_{len(self.shared_knowledge.verification_memory.get_all_claim_ids())}"
            
            self.shared_knowledge.verification_memory.store_fact_check(
                claim_id, claim, task_result.output
            )
            
            # Update shared knowledge
            self.update_shared_knowledge(
                f"verification_{claim_id}",
                task_result,
                {"claim": claim, "processor": processor}
            )
            
            self.log_activity("claim_verification", {
                "claim": claim,
                "processor": processor,
                "claim_id": claim_id,
                "status": task_result.output.get("status", "unknown")
            })
            
            return {
                "output": task_result.output,
                "processor": processor
            }
        
        except Exception as e:
            self.log_activity("verification_error", {"claim": claim, "error": str(e)})
            raise
    
    def _create_verification_prompt(self, claim: str, context: Optional[str] = None) -> str:
        """Create verification prompt for a claim."""
        base_prompt = f"""
        Verify the following claim and provide a comprehensive verification report:
        
        Claim: {claim}
        """
        
        if context:
            base_prompt += f"\nContext: {context}"
        
        base_prompt += """
        
        Please provide:
        1. The claim being verified
        2. Verification status (verified, disputed, unverified)
        3. Confidence score (0-1)
        4. Supporting or contradicting evidence
        5. Sources used for verification
        6. Detailed reasoning for your conclusion
        
        Be thorough and objective in your verification process.
        """
        
        return base_prompt
    
    async def cross_reference_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-reference data from multiple sources."""
        cross_references = {}
        
        # Extract key claims from the data
        claims = self._extract_claims(data)
        
        for claim in claims:
            try:
                verification_result = await self.verify_claim(claim)
                cross_references[claim] = verification_result
            except Exception as e:
                cross_references[claim] = {"error": str(e)}
        
        # Store cross-reference results
        topic = "cross_reference_analysis"
        sources = list(cross_references.keys())
        self.shared_knowledge.verification_memory.store_cross_reference(topic, sources)
        
        return cross_references
    
    def _extract_claims(self, data: Dict[str, Any]) -> List[str]:
        """Extract verifiable claims from data."""
        claims = []
        
        # Extract from analysis results
        if "output" in data and "parsed" in data["output"]:
            parsed = data["output"]["parsed"]
            if "key_findings" in parsed:
                claims.extend(parsed["key_findings"])
            if "insights" in parsed:
                claims.extend(parsed["insights"])
        
        # Extract from search results
        if "results" in data:
            for result in data["results"]:
                if "excerpt" in result:
                    # Simple claim extraction - in practice, you'd use NLP
                    claims.append(result["excerpt"][:100] + "...")
        
        return claims[:5]  # Limit to 5 claims for efficiency
    
    async def validate_data_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the quality and reliability of data."""
        validation_result = {
            "is_valid": True,
            "type": "data_quality",
            "issues": [],
            "confidence": 1.0
        }
        
        # Check for required fields
        required_fields = ["data", "sources", "timestamp"]
        for field in required_fields:
            if field not in data:
                validation_result["issues"].append(f"Missing required field: {field}")
                validation_result["is_valid"] = False
        
        # Check data freshness
        if "timestamp" in data:
            # Simple freshness check - in practice, you'd parse and compare dates
            validation_result["confidence"] *= 0.9
        
        # Store validation result
        data_id = f"validation_{len(self.shared_knowledge.verification_memory.get_all_data_ids())}"
        self.shared_knowledge.verification_memory.store_validation(data_id, validation_result)
        
        return validation_result
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a verification task."""
        task_type = task.get("type", "verify")
        data = task.get("data", {})
        claim = task.get("claim", "")
        processor = task.get("processor", "pro")
        
        if task_type == "verify":
            result = await self.verify_claim(claim, data.get("context"), processor)
            return {
                "agent": self.name,
                "task_type": task_type,
                "claim": claim,
                "result": result,
                "status": "completed"
            }
        
        elif task_type == "cross_reference":
            result = await self.cross_reference_data(data)
            return {
                "agent": self.name,
                "task_type": task_type,
                "result": result,
                "status": "completed"
            }
        
        elif task_type == "validate":
            result = await self.validate_data_quality(data)
            return {
                "agent": self.name,
                "task_type": task_type,
                "result": result,
                "status": "completed"
            }
        
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    def get_verification_summary(self) -> Dict[str, Any]:
        """Get verification summary from memory."""
        return self.shared_knowledge.verification_memory.get_verification_summary()
    
    def get_verified_claims(self) -> List[str]:
        """Get list of verified claims."""
        return self.shared_knowledge.verification_memory.get_all_claim_ids()
