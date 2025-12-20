"""
Inspector Bot Adapters
Thin wrappers for LLM-as-Judge auditing.
"""

from .audit_adapter import AuditAdapter
from .report_bridge import ReportBridge

__all__ = ["AuditAdapter", "ReportBridge"]
