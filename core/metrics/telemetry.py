"""
Telemetry - Track token usage, latency, and cost

Provides observability for AI operations.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger("core.metrics.telemetry")

TELEMETRY_DIR = Path(__file__).parent.parent.parent / "data" / "telemetry"
TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class APICall:
    """Record of a single API call."""
    timestamp: datetime
    model: str
    endpoint: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    success: bool
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def cost(self) -> float:
        """Estimate cost based on model pricing."""
        # Pricing per 1M tokens (approximate)
        pricing = {
            "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
            "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
            "claude-opus-4-20250514": {"input": 15.0, "output": 75.0},
            "gpt-4": {"input": 30.0, "output": 60.0},
            "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
        }

        rates = pricing.get(self.model, {"input": 3.0, "output": 15.0})
        input_cost = (self.input_tokens / 1_000_000) * rates["input"]
        output_cost = (self.output_tokens / 1_000_000) * rates["output"]
        return input_cost + output_cost


class Telemetry:
    """
    Telemetry collector for AI operations.

    Tracks:
    - Token usage per model
    - API latency
    - Cost estimation
    - Error rates
    """

    def __init__(self):
        self._calls: List[APICall] = []
        self._daily_file: Optional[Path] = None
        self._load_today()

    def _get_daily_file(self) -> Path:
        """Get today's telemetry file."""
        today = datetime.utcnow().strftime("%Y%m%d")
        return TELEMETRY_DIR / f"telemetry_{today}.json"

    def _load_today(self):
        """Load today's telemetry data."""
        self._daily_file = self._get_daily_file()
        if self._daily_file.exists():
            try:
                with open(self._daily_file) as f:
                    data = json.load(f)
                    for call_data in data.get("calls", []):
                        call_data["timestamp"] = datetime.fromisoformat(call_data["timestamp"])
                        self._calls.append(APICall(**call_data))
            except Exception as e:
                logger.error(f"Failed to load telemetry: {e}")

    def _save(self):
        """Save telemetry to disk."""
        try:
            data = {
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
                "calls": [
                    {**asdict(c), "timestamp": c.timestamp.isoformat()}
                    for c in self._calls
                ]
            }
            with open(self._get_daily_file(), "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save telemetry: {e}")

    def record(
        self,
        model: str,
        endpoint: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float,
        success: bool = True,
        error: str = None,
        metadata: Dict = None
    ) -> APICall:
        """Record an API call."""
        call = APICall(
            timestamp=datetime.utcnow(),
            model=model,
            endpoint=endpoint,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            success=success,
            error=error,
            metadata=metadata or {}
        )

        self._calls.append(call)
        self._save()

        # Log high-cost calls
        if call.cost > 0.10:
            logger.warning(f"High-cost API call: ${call.cost:.4f} ({model}, {call.total_tokens} tokens)")

        return call

    def get_daily_stats(self, date: datetime = None) -> Dict[str, Any]:
        """Get statistics for a specific day."""
        target_date = (date or datetime.utcnow()).date()
        day_calls = [
            c for c in self._calls
            if c.timestamp.date() == target_date
        ]

        if not day_calls:
            return {"date": str(target_date), "calls": 0}

        total_tokens = sum(c.total_tokens for c in day_calls)
        total_cost = sum(c.cost for c in day_calls)
        avg_latency = sum(c.latency_ms for c in day_calls) / len(day_calls)
        errors = sum(1 for c in day_calls if not c.success)

        by_model = defaultdict(lambda: {"calls": 0, "tokens": 0, "cost": 0})
        for c in day_calls:
            by_model[c.model]["calls"] += 1
            by_model[c.model]["tokens"] += c.total_tokens
            by_model[c.model]["cost"] += c.cost

        return {
            "date": str(target_date),
            "calls": len(day_calls),
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 4),
            "avg_latency_ms": round(avg_latency, 2),
            "errors": errors,
            "error_rate": round(errors / len(day_calls) * 100, 2) if day_calls else 0,
            "by_model": dict(by_model)
        }

    def get_weekly_stats(self) -> Dict[str, Any]:
        """Get statistics for the past 7 days."""
        cutoff = datetime.utcnow() - timedelta(days=7)
        week_calls = [c for c in self._calls if c.timestamp >= cutoff]

        if not week_calls:
            return {"period": "7 days", "calls": 0}

        total_cost = sum(c.cost for c in week_calls)
        total_tokens = sum(c.total_tokens for c in week_calls)

        return {
            "period": "7 days",
            "calls": len(week_calls),
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 4),
            "avg_daily_cost": round(total_cost / 7, 4),
            "avg_tokens_per_call": round(total_tokens / len(week_calls), 0) if week_calls else 0
        }

    def get_model_breakdown(self) -> Dict[str, Dict]:
        """Get usage breakdown by model."""
        breakdown = defaultdict(lambda: {"calls": 0, "tokens": 0, "cost": 0, "errors": 0})

        for call in self._calls:
            breakdown[call.model]["calls"] += 1
            breakdown[call.model]["tokens"] += call.total_tokens
            breakdown[call.model]["cost"] += call.cost
            if not call.success:
                breakdown[call.model]["errors"] += 1

        return dict(breakdown)

    def estimate_monthly_cost(self) -> float:
        """Estimate monthly cost based on current usage."""
        weekly = self.get_weekly_stats()
        return weekly.get("total_cost", 0) * 4.33  # Weeks per month


# Singleton
_telemetry: Optional[Telemetry] = None


def get_telemetry() -> Telemetry:
    """Get or create telemetry singleton."""
    global _telemetry
    if _telemetry is None:
        _telemetry = Telemetry()
    return _telemetry
