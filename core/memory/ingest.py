"""
Data Ingestion Module

Handles ingesting trades, lessons, and analyses into memory.
Parses markdown journal entries and extracts structured data.
"""

import re
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from .chroma_store import VulcanMemory


class TradeIngestor:
    """Ingests trade journal entries into memory."""

    def __init__(self, memory: VulcanMemory):
        self.memory = memory

    def ingest_trade(
        self,
        pair: str,
        setup_type: str,
        rationale: str,
        result: str,
        r_multiple: float,
        lesson: str,
        day: Optional[str] = None,
        session: Optional[str] = None,
        trade_id: Optional[str] = None
    ) -> str:
        """Ingest a single trade into memory.

        Args:
            pair: Trading pair (e.g., "GBP/USD", "XAUUSD")
            setup_type: Type of setup (e.g., "ICT OB", "BTMM Stop Hunt")
            rationale: Why the trade was taken
            result: "win" or "loss"
            r_multiple: Risk-reward achieved
            lesson: Lesson learned from this trade
            day: Day of week
            session: Trading session (London, NY, etc.)
            trade_id: Optional custom ID

        Returns:
            The trade ID
        """
        if trade_id is None:
            trade_id = f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

        content = f"{setup_type} on {pair}: {rationale}. Result: {result} ({r_multiple}R). Lesson: {lesson}"

        metadata = {
            "pair": pair,
            "setup_type": setup_type,
            "result": result,
            "r_multiple": r_multiple,
            "day": day or datetime.now().strftime("%A"),
            "session": session or "unknown"
        }

        self.memory.add_trade(trade_id, content, metadata)
        return trade_id

    def ingest_from_journal_entry(self, markdown_content: str) -> Optional[str]:
        """Parse a markdown journal entry and ingest.

        Expected format from trade-journal-entry.md template.
        """
        # Extract fields using regex patterns
        pair_match = re.search(r"Pair:\s*(.+)", markdown_content)
        setup_match = re.search(r"Setup Type:\s*(.+)", markdown_content)
        result_match = re.search(r"Result:\s*(Win|Loss)", markdown_content, re.IGNORECASE)
        r_match = re.search(r"R-Multiple:\s*([\d.+-]+)", markdown_content)
        lesson_match = re.search(r"Lesson[s]?:\s*(.+?)(?:\n#|\Z)", markdown_content, re.DOTALL)

        if not all([pair_match, setup_match, result_match]):
            return None

        return self.ingest_trade(
            pair=pair_match.group(1).strip(),
            setup_type=setup_match.group(1).strip(),
            rationale=self._extract_section(markdown_content, "Rationale") or "",
            result=result_match.group(1).lower(),
            r_multiple=float(r_match.group(1)) if r_match else 0.0,
            lesson=lesson_match.group(1).strip() if lesson_match else ""
        )

    def _extract_section(self, content: str, section_name: str) -> Optional[str]:
        """Extract content from a markdown section."""
        pattern = rf"#{1,3}\s*{section_name}\s*\n(.*?)(?:\n#|\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else None


class LessonIngestor:
    """Ingests lessons learned into memory."""

    def __init__(self, memory: VulcanMemory):
        self.memory = memory

    def ingest_lesson(
        self,
        content: str,
        category: str = "general",
        source_trade: Optional[str] = None,
        severity: str = "normal"
    ) -> str:
        """Ingest a lesson learned.

        Args:
            content: The lesson text
            category: Category (e.g., "entry", "exit", "psychology", "risk")
            source_trade: ID of the trade this lesson came from
            severity: Importance level ("critical", "high", "normal", "low")

        Returns:
            The lesson ID
        """
        lesson_id = f"lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

        metadata = {
            "category": category,
            "severity": severity,
            "source_trade": source_trade
        }

        self.memory.add_lesson(lesson_id, content, metadata)
        return lesson_id


class AnalysisIngestor:
    """Ingests market analyses into memory."""

    def __init__(self, memory: VulcanMemory):
        self.memory = memory

    def ingest_analysis(
        self,
        content: str,
        pairs: List[str],
        bias: str,
        timeframe: str = "daily",
        date: Optional[str] = None
    ) -> str:
        """Ingest a market analysis.

        Args:
            content: The analysis text
            pairs: Pairs analyzed
            bias: Market bias (bullish, bearish, neutral)
            timeframe: Analysis timeframe
            date: Date of analysis

        Returns:
            The analysis ID
        """
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

        metadata = {
            "pairs": ",".join(pairs),
            "bias": bias,
            "timeframe": timeframe,
            "date": date or datetime.now().strftime("%Y-%m-%d")
        }

        self.memory.add_analysis(analysis_id, content, metadata)
        return analysis_id


class CADIngestor:
    """Ingests CAD job logs into memory."""

    def __init__(self, memory: VulcanMemory):
        self.memory = memory

    def ingest_cad_job(
        self,
        description: str,
        software: str,
        commands: List[str],
        outcome: str,
        job_id: Optional[str] = None
    ) -> str:
        """Ingest a CAD job log.

        Args:
            description: What was created/modified
            software: CAD software used (SolidWorks, Inventor, etc.)
            commands: List of commands executed
            outcome: Success/failure and any notes

        Returns:
            The job ID
        """
        if job_id is None:
            job_id = f"cad_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

        content = f"{description}. Commands: {', '.join(commands)}. Outcome: {outcome}"

        metadata = {
            "software": software,
            "command_count": len(commands),
            "success": "success" in outcome.lower()
        }

        self.memory.add_cad_job(job_id, content, metadata)
        return job_id
