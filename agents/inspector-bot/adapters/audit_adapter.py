"""
Audit Adapter
Thin wrapper for LLM-as-Judge functionality.

Packages Used:
- anthropic (Claude API)
- Already in requirements.txt
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("inspector.audit")


class Grade(Enum):
    A = "excellent"
    B = "good"
    C = "acceptable"
    D = "needs_work"
    F = "failed"


@dataclass
class AuditResult:
    item_id: str
    item_type: str  # trade, cad_part, assembly
    grade: Grade
    score: float  # 0-100
    findings: List[str]
    recommendations: List[str]


class AuditAdapter:
    """
    Adapter for LLM-powered auditing.
    Uses Claude to analyze and grade agent outputs.
    """
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
        
    async def audit_trade(self, trade_data: Dict) -> AuditResult:
        """Audit a trading decision."""
        prompt = self._build_trade_prompt(trade_data)
        
        if self.llm:
            response = await self.llm.complete(prompt)
            return self._parse_response(response, trade_data.get("id", ""), "trade")
        
        # Fallback if no LLM
        return AuditResult(
            item_id=trade_data.get("id", ""),
            item_type="trade",
            grade=Grade.C,
            score=70,
            findings=["LLM not available for full audit"],
            recommendations=["Connect LLM client for detailed analysis"]
        )
        
    async def audit_cad_job(self, job_data: Dict) -> AuditResult:
        """Audit a CAD job output."""
        prompt = self._build_cad_prompt(job_data)
        
        if self.llm:
            response = await self.llm.complete(prompt)
            return self._parse_response(response, job_data.get("job_id", ""), "cad_job")
        
        return AuditResult(
            item_id=job_data.get("job_id", ""),
            item_type="cad_job",
            grade=Grade.C,
            score=70,
            findings=["LLM not available"],
            recommendations=[]
        )
        
    def _build_trade_prompt(self, trade: Dict) -> str:
        """Build audit prompt for trade."""
        return f"""
        Analyze this trade and provide a grade (A-F) with score (0-100):
        
        Pair: {trade.get('pair')}
        Setup: {trade.get('setup_type')}
        Bias: {trade.get('bias')}
        Entry: {trade.get('entry')}
        Stop Loss: {trade.get('stop_loss')}
        Take Profit: {trade.get('take_profit')}
        Result: {trade.get('result')} ({trade.get('r_multiple')}R)
        Lesson: {trade.get('lesson')}
        
        Evaluate:
        1. Setup quality - Was entry valid per strategy rules?
        2. Risk management - Proper SL/TP placement?
        3. Lesson quality - Did they learn the right thing?
        
        Respond with JSON: {{"grade": "A-F", "score": 0-100, "findings": [...], "recommendations": [...]}}
        """
        
    def _build_cad_prompt(self, job: Dict) -> str:
        """Build audit prompt for CAD job."""
        return f"""
        Review this CAD job output:
        
        Parts Built: {job.get('parts_built')}
        Assembly: {job.get('assembly_file')}
        Mass Properties: {job.get('mass_properties')}
        Export Files: {job.get('export_files')}
        
        Check:
        1. All parts present and correctly mated
        2. Mass properties reasonable for material
        3. Export files complete
        
        Respond with JSON: {{"grade": "A-F", "score": 0-100, "findings": [...], "recommendations": [...]}}
        """
        
    def _parse_response(self, response: str, item_id: str, item_type: str) -> AuditResult:
        """Parse LLM response into AuditResult."""
        import json
        try:
            data = json.loads(response)
            return AuditResult(
                item_id=item_id,
                item_type=item_type,
                grade=Grade[data.get("grade", "C")],
                score=data.get("score", 70),
                findings=data.get("findings", []),
                recommendations=data.get("recommendations", [])
            )
        except:
            return AuditResult(
                item_id=item_id,
                item_type=item_type,
                grade=Grade.C,
                score=70,
                findings=["Failed to parse LLM response"],
                recommendations=[]
            )
