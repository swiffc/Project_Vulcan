"""
Strategy Scoring - Quantitative Performance Formula

Calculates strategy scores based on:
- Validation pass rate (accuracy)
- Execution time (speed)
- Error patterns (quality)
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger("core.metrics.strategy_scoring")


class StrategyScorer:
    """
    Calculates quantitative scores for strategies.

    Score Formula:
    score = (accuracy * 0.6) + (speed_score * 0.2) + (quality_score * 0.2)

    Where:
    - accuracy: Validation pass rate (0-100)
    - speed_score: Normalized execution time (100 = fastest, 0 = slowest)
    - quality_score: Based on error severity and patterns
    """

    def __init__(self):
        self._db = None

    def _get_db(self):
        """Lazy load database adapter."""
        if self._db is None:
            from core.database_adapter import get_db_adapter
            self._db = get_db_adapter()
        return self._db

    def calculate_score(
        self,
        strategy_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive score for a strategy.

        Returns:
            {
                "overall_score": float (0-100),
                "accuracy_score": float,
                "speed_score": float,
                "quality_score": float,
                "components": {detailed breakdown}
            }
        """
        db = self._get_db()
        performance = db.get_strategy_performance(strategy_id, days=days)

        if not performance:
            return {
                "overall_score": 0,
                "message": "No performance data available",
                "executions": 0
            }

        # Calculate accuracy (60% weight)
        accuracy = self._calculate_accuracy(performance)

        # Calculate speed score (20% weight)
        speed = self._calculate_speed_score(performance)

        # Calculate quality score (20% weight)
        quality = self._calculate_quality_score(performance)

        # Weighted combination
        overall = (accuracy * 0.6) + (speed * 0.2) + (quality * 0.2)

        return {
            "overall_score": round(overall, 2),
            "accuracy_score": round(accuracy, 2),
            "speed_score": round(speed, 2),
            "quality_score": round(quality, 2),
            "executions": len(performance),
            "period_days": days,
            "components": {
                "passed": sum(1 for p in performance if p.get("validation_passed")),
                "failed": sum(1 for p in performance if not p.get("validation_passed")),
                "avg_time": self._avg_time(performance),
                "error_types": self._count_error_types(performance)
            }
        }

    def _calculate_accuracy(self, performance: List[Dict]) -> float:
        """Calculate pass rate as percentage."""
        if not performance:
            return 0

        passed = sum(1 for p in performance if p.get("validation_passed"))
        return (passed / len(performance)) * 100

    def _calculate_speed_score(self, performance: List[Dict]) -> float:
        """
        Calculate speed score based on execution time.

        Uses a target time approach:
        - < 10 seconds: 100
        - 10-30 seconds: 80-100
        - 30-60 seconds: 50-80
        - > 60 seconds: 0-50
        """
        times = [p.get("execution_time", 0) for p in performance if p.get("execution_time")]
        if not times:
            return 50  # Neutral score if no data

        avg_time = sum(times) / len(times)

        if avg_time < 10:
            return 100
        elif avg_time < 30:
            return 80 + (30 - avg_time) * 1.0
        elif avg_time < 60:
            return 50 + (60 - avg_time) * 1.0
        else:
            return max(0, 50 - (avg_time - 60) * 0.5)

    def _calculate_quality_score(self, performance: List[Dict]) -> float:
        """
        Calculate quality score based on error patterns.

        Considers:
        - Error severity (critical errors penalize more)
        - Error diversity (many different errors = worse)
        - Improvement trend
        """
        if not performance:
            return 50  # Neutral

        # Count errors by type
        error_types = self._count_error_types(performance)
        total_errors = sum(error_types.values())

        if total_errors == 0:
            return 100  # Perfect quality

        # Penalty for error diversity (more types = worse)
        diversity_penalty = min(len(error_types) * 5, 30)

        # Penalty for total errors
        error_penalty = min(total_errors * 2, 40)

        # Check for critical errors
        critical_keywords = ["tolerance", "interference", "gdt", "material"]
        critical_count = sum(
            count for err_type, count in error_types.items()
            if any(kw in err_type.lower() for kw in critical_keywords)
        )
        critical_penalty = critical_count * 5

        quality = 100 - diversity_penalty - error_penalty - critical_penalty
        return max(0, quality)

    def _avg_time(self, performance: List[Dict]) -> float:
        """Calculate average execution time."""
        times = [p.get("execution_time", 0) for p in performance if p.get("execution_time")]
        return sum(times) / len(times) if times else 0

    def _count_error_types(self, performance: List[Dict]) -> Dict[str, int]:
        """Count occurrences of each error type."""
        counts = {}
        for perf in performance:
            errors = perf.get("errors_json") or []
            if isinstance(errors, str):
                try:
                    import json
                    errors = json.loads(errors)
                except:
                    continue

            for err in errors:
                err_type = err.get("type", err.get("check", "unknown"))
                counts[err_type] = counts.get(err_type, 0) + 1

        return counts

    def rank_strategies(
        self,
        product_type: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Rank all strategies by score.

        Returns sorted list with scores.
        """
        db = self._get_db()
        strategies = db.list_strategies(product_type=product_type, is_experimental=False)

        rankings = []
        for strategy in strategies:
            score_data = self.calculate_score(strategy["id"])
            rankings.append({
                "id": strategy["id"],
                "name": strategy["name"],
                "product_type": strategy["product_type"],
                "overall_score": score_data["overall_score"],
                "accuracy": score_data.get("accuracy_score", 0),
                "executions": score_data.get("executions", 0)
            })

        rankings.sort(key=lambda x: x["overall_score"], reverse=True)
        return rankings[:limit]

    def get_improvement_needed(
        self,
        strategy_id: int,
        target_score: float = 80.0
    ) -> Dict[str, Any]:
        """
        Calculate what improvements are needed to reach target score.
        """
        current = self.calculate_score(strategy_id)

        if current["overall_score"] >= target_score:
            return {
                "meets_target": True,
                "current_score": current["overall_score"],
                "target_score": target_score
            }

        gap = target_score - current["overall_score"]

        improvements = []

        # Check each component
        if current["accuracy_score"] < 80:
            needed = min(100, current["accuracy_score"] + (gap / 0.6))
            improvements.append({
                "component": "accuracy",
                "current": current["accuracy_score"],
                "target": round(needed, 1),
                "action": "Improve validation pass rate"
            })

        if current["speed_score"] < 70:
            improvements.append({
                "component": "speed",
                "current": current["speed_score"],
                "target": 70,
                "action": "Optimize execution time"
            })

        if current["quality_score"] < 70:
            improvements.append({
                "component": "quality",
                "current": current["quality_score"],
                "target": 70,
                "action": "Reduce error diversity and critical errors"
            })

        return {
            "meets_target": False,
            "current_score": current["overall_score"],
            "target_score": target_score,
            "gap": round(gap, 2),
            "improvements": improvements
        }


# Singleton
_scorer: Optional[StrategyScorer] = None


def get_strategy_scorer() -> StrategyScorer:
    """Get or create scorer singleton."""
    global _scorer
    if _scorer is None:
        _scorer = StrategyScorer()
    return _scorer
