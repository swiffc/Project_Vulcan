"""
Audit Logger - System Action Tracking

Logs all significant system actions to JSONL for compliance and debugging.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Literal
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger("core.audit_logger")

AUDIT_DIR = Path(__file__).parent.parent / "data" / "audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class AuditEntry:
    """A single audit log entry."""
    timestamp: str
    action: str
    category: str  # api, cad, trading, system, auth
    user: str
    resource: Optional[str]
    details: Dict[str, Any]
    success: bool
    error: Optional[str] = None
    ip_address: Optional[str] = None
    session_id: Optional[str] = None


class AuditLogger:
    """
    Audit logger for all system actions.

    Logs to:
    - JSONL files (one per day)
    - Console (warnings/errors only)

    Categories:
    - api: API calls
    - cad: CAD operations
    - trading: Trading actions
    - system: System events
    - auth: Authentication events
    - strategy: Strategy operations
    """

    def __init__(self):
        self._current_file: Optional[Path] = None
        self._current_date: Optional[str] = None

    def _get_file(self) -> Path:
        """Get current audit log file."""
        today = datetime.utcnow().strftime("%Y%m%d")
        if self._current_date != today:
            self._current_date = today
            self._current_file = AUDIT_DIR / f"audit_{today}.jsonl"
        return self._current_file

    def log(
        self,
        action: str,
        category: Literal["api", "cad", "trading", "system", "auth", "strategy"],
        user: str = "system",
        resource: str = None,
        details: Dict = None,
        success: bool = True,
        error: str = None,
        ip_address: str = None,
        session_id: str = None
    ):
        """Log an audit entry."""
        entry = AuditEntry(
            timestamp=datetime.utcnow().isoformat(),
            action=action,
            category=category,
            user=user,
            resource=resource,
            details=details or {},
            success=success,
            error=error,
            ip_address=ip_address,
            session_id=session_id
        )

        self._write(entry)

        # Log errors to console
        if not success:
            logger.warning(f"[AUDIT] {category}/{action} FAILED: {error}")

    def _write(self, entry: AuditEntry):
        """Write entry to JSONL file."""
        try:
            with open(self._get_file(), "a") as f:
                f.write(json.dumps(asdict(entry)) + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    # Convenience methods for common actions

    def log_api_call(
        self,
        endpoint: str,
        method: str,
        user: str = "anonymous",
        status_code: int = 200,
        error: str = None
    ):
        """Log an API call."""
        self.log(
            action=f"{method} {endpoint}",
            category="api",
            user=user,
            resource=endpoint,
            details={"method": method, "status_code": status_code},
            success=status_code < 400,
            error=error
        )

    def log_cad_operation(
        self,
        operation: str,
        file_path: str = None,
        result: str = None,
        error: str = None
    ):
        """Log a CAD operation."""
        self.log(
            action=operation,
            category="cad",
            resource=file_path,
            details={"result": result} if result else {},
            success=error is None,
            error=error
        )

    def log_strategy_action(
        self,
        action: str,
        strategy_id: int = None,
        strategy_name: str = None,
        details: Dict = None,
        error: str = None
    ):
        """Log a strategy action."""
        self.log(
            action=action,
            category="strategy",
            resource=f"strategy:{strategy_id}" if strategy_id else strategy_name,
            details=details or {},
            success=error is None,
            error=error
        )

    def log_auth(
        self,
        action: str,
        user: str,
        success: bool,
        ip_address: str = None,
        error: str = None
    ):
        """Log an authentication event."""
        self.log(
            action=action,
            category="auth",
            user=user,
            success=success,
            error=error,
            ip_address=ip_address
        )

    def log_system(
        self,
        action: str,
        details: Dict = None,
        error: str = None
    ):
        """Log a system event."""
        self.log(
            action=action,
            category="system",
            details=details or {},
            success=error is None,
            error=error
        )

    def query(
        self,
        date: str = None,
        category: str = None,
        action: str = None,
        user: str = None,
        success: bool = None,
        limit: int = 100
    ) -> list:
        """Query audit logs."""
        target_date = date or datetime.utcnow().strftime("%Y%m%d")
        log_file = AUDIT_DIR / f"audit_{target_date}.jsonl"

        if not log_file.exists():
            return []

        results = []
        try:
            with open(log_file) as f:
                for line in f:
                    if not line.strip():
                        continue
                    entry = json.loads(line)

                    # Apply filters
                    if category and entry.get("category") != category:
                        continue
                    if action and action not in entry.get("action", ""):
                        continue
                    if user and entry.get("user") != user:
                        continue
                    if success is not None and entry.get("success") != success:
                        continue

                    results.append(entry)

                    if len(results) >= limit:
                        break
        except Exception as e:
            logger.error(f"Failed to query audit logs: {e}")

        return results

    def get_stats(self, date: str = None) -> Dict[str, Any]:
        """Get audit statistics for a day."""
        entries = self.query(date=date, limit=10000)

        if not entries:
            return {"date": date, "total": 0}

        by_category = {}
        by_action = {}
        errors = 0

        for entry in entries:
            cat = entry.get("category", "unknown")
            by_category[cat] = by_category.get(cat, 0) + 1

            action = entry.get("action", "unknown")
            by_action[action] = by_action.get(action, 0) + 1

            if not entry.get("success"):
                errors += 1

        return {
            "date": date or datetime.utcnow().strftime("%Y%m%d"),
            "total": len(entries),
            "errors": errors,
            "error_rate": round(errors / len(entries) * 100, 2) if entries else 0,
            "by_category": by_category,
            "top_actions": dict(sorted(by_action.items(), key=lambda x: -x[1])[:10])
        }


# Singleton
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create audit logger singleton."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


# Convenience function
def audit(
    action: str,
    category: str,
    **kwargs
):
    """Quick audit log."""
    get_audit_logger().log(action=action, category=category, **kwargs)
