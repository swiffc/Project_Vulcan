"""
Inspector Bot Adapters
Thin wrappers for LLM-as-Judge auditing.
"""

from .audit_adapter import AuditAdapter

__all__ = ["AuditAdapter"]
