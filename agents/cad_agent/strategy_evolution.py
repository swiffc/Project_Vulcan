"""
Strategy Evolution Module - Phase 20 Task 23

LLM-powered evolution of strategies based on performance feedback.
This is where the "learning" happens.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger("cad_agent.strategy_evolution")


class StrategyEvolution:
    """
    Evolves strategies based on performance data.

    When a strategy fails repeatedly, this module:
    1. Analyzes the failure patterns
    2. Prompts LLM to suggest improvements
    3. Creates a new version of the strategy
    4. Saves the old version for rollback
    """

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.model = model
        self._client = None
        self._db = None

    def _get_client(self):
        """Lazy load Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )
            except ImportError:
                logger.error("anthropic package not installed")
                raise
        return self._client

    def _get_db(self):
        """Lazy load database adapter."""
        if self._db is None:
            from core.database_adapter import get_db_adapter
            self._db = get_db_adapter()
        return self._db

    def _analyze_failures(self, performance_data: List[Dict]) -> Dict[str, Any]:
        """
        Analyze performance data to identify failure patterns.

        Returns:
            {
                "total_executions": int,
                "pass_rate": float,
                "common_errors": [{"type": str, "count": int, "percentage": float}],
                "avg_execution_time": float,
                "trend": "improving" | "declining" | "stable"
            }
        """
        if not performance_data:
            return {"total_executions": 0, "pass_rate": 0, "common_errors": [], "trend": "unknown"}

        total = len(performance_data)
        passed = sum(1 for p in performance_data if p.get("validation_passed"))
        pass_rate = (passed / total) * 100 if total > 0 else 0

        # Count error types
        error_counts = {}
        for perf in performance_data:
            errors = perf.get("errors_json") or []
            if isinstance(errors, str):
                try:
                    errors = json.loads(errors)
                except:
                    errors = []
            for err in errors:
                err_type = err.get("type", err.get("check", "unknown"))
                error_counts[err_type] = error_counts.get(err_type, 0) + 1

        common_errors = [
            {
                "type": err_type,
                "count": count,
                "percentage": (count / total) * 100
            }
            for err_type, count in sorted(error_counts.items(), key=lambda x: -x[1])[:5]
        ]

        # Calculate average execution time
        times = [p.get("execution_time", 0) for p in performance_data if p.get("execution_time")]
        avg_time = sum(times) / len(times) if times else 0

        # Determine trend (compare first half to second half)
        mid = len(performance_data) // 2
        if mid > 0:
            first_half = performance_data[:mid]
            second_half = performance_data[mid:]
            first_rate = sum(1 for p in first_half if p.get("validation_passed")) / len(first_half)
            second_rate = sum(1 for p in second_half if p.get("validation_passed")) / len(second_half)
            if second_rate > first_rate + 0.1:
                trend = "improving"
            elif second_rate < first_rate - 0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "unknown"

        return {
            "total_executions": total,
            "pass_rate": pass_rate,
            "common_errors": common_errors,
            "avg_execution_time": avg_time,
            "trend": trend
        }

    async def evolve_strategy(
        self,
        strategy_id: int,
        force: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Evolve a strategy based on its performance history.

        Args:
            strategy_id: ID of strategy to evolve
            force: Evolve even if performance is acceptable

        Returns:
            New evolved strategy, or None if evolution not needed
        """
        db = self._get_db()

        # Load current strategy
        strategy = db.load_strategy(strategy_id)
        if not strategy:
            logger.error(f"Strategy {strategy_id} not found")
            return None

        # Get performance history
        performance_data = db.get_strategy_performance(strategy_id, days=30)
        analysis = self._analyze_failures(performance_data)

        # Check if evolution is needed
        if not force:
            if analysis["pass_rate"] >= 80:
                logger.info(f"Strategy {strategy_id} has good performance ({analysis['pass_rate']:.1f}%), skipping evolution")
                return None
            if analysis["total_executions"] < 3:
                logger.info(f"Strategy {strategy_id} has insufficient data ({analysis['total_executions']} executions)")
                return None
            if analysis["trend"] == "improving":
                logger.info(f"Strategy {strategy_id} is improving, skipping evolution")
                return None

        logger.info(f"Evolving strategy {strategy_id} (pass rate: {analysis['pass_rate']:.1f}%)")

        # Save current version for rollback
        current_version = strategy.get("version", 1)
        db.save_strategy_version(
            strategy_id=strategy_id,
            version=current_version,
            schema_json=strategy.get("schema_json"),
            change_reason=f"Pre-evolution snapshot (pass rate: {analysis['pass_rate']:.1f}%)",
            perf_before=analysis["pass_rate"]
        )

        # Generate evolved strategy
        evolved = await self._generate_evolution(strategy, analysis)

        if evolved:
            # Update strategy in database
            evolved["version"] = current_version + 1
            evolved["id"] = strategy_id
            evolved["is_experimental"] = True  # New versions are experimental
            evolved["updated_at"] = datetime.utcnow().isoformat()

            db.save_strategy(evolved)
            logger.info(f"Strategy {strategy_id} evolved to version {evolved['version']}")

            return evolved

        return None

    async def _generate_evolution(
        self,
        strategy: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Use LLM to generate an improved version of the strategy."""
        client = self._get_client()

        # Build the evolution prompt
        error_summary = "\n".join([
            f"- {e['type']}: {e['count']} failures ({e['percentage']:.1f}%)"
            for e in analysis["common_errors"]
        ]) or "No specific error patterns identified"

        prompt = f"""You are a CAD engineering expert. A strategy is failing validation checks and needs improvement.

## Current Strategy
```json
{json.dumps(strategy.get("schema_json", strategy), indent=2)}
```

## Performance Analysis
- Total executions: {analysis['total_executions']}
- Pass rate: {analysis['pass_rate']:.1f}%
- Trend: {analysis['trend']}

## Common Failure Patterns
{error_summary}

## Task
Improve this strategy to address the failure patterns. Make specific changes to:
1. Fix the issues causing validation failures
2. Add missing constraints or specifications
3. Improve dimensions, tolerances, or material specs as needed
4. Keep changes minimal but effective

Output the COMPLETE improved strategy as valid JSON. Do not include explanations, only the JSON.
"""

        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text.strip()

            # Clean up markdown if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            evolved = json.loads(content)
            return evolved

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse evolved strategy JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Evolution generation failed: {e}")
            return None

    async def batch_evolve(
        self,
        threshold: float = 50.0,
        min_usage: int = 3,
        max_evolutions: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Evolve multiple low-performing strategies.

        Args:
            threshold: Minimum pass rate to skip evolution
            min_usage: Minimum usage count to consider
            max_evolutions: Maximum strategies to evolve in one batch

        Returns:
            List of evolved strategies
        """
        db = self._get_db()

        # Get candidates
        candidates = db.get_low_performing_strategies(threshold=threshold, min_usage=min_usage)
        logger.info(f"Found {len(candidates)} evolution candidates")

        evolved = []
        for strategy in candidates[:max_evolutions]:
            try:
                result = await self.evolve_strategy(strategy["id"])
                if result:
                    evolved.append(result)
            except Exception as e:
                logger.error(f"Failed to evolve strategy {strategy['id']}: {e}")

        logger.info(f"Evolved {len(evolved)} strategies")
        return evolved

    def should_evolve(self, strategy_id: int) -> Dict[str, Any]:
        """
        Check if a strategy should be evolved.

        Returns:
            {
                "should_evolve": bool,
                "reason": str,
                "pass_rate": float,
                "usage_count": int
            }
        """
        db = self._get_db()

        strategy = db.load_strategy(strategy_id)
        if not strategy:
            return {"should_evolve": False, "reason": "Strategy not found"}

        performance = db.get_strategy_performance(strategy_id, days=30)
        analysis = self._analyze_failures(performance)

        if analysis["total_executions"] < 3:
            return {
                "should_evolve": False,
                "reason": "Insufficient usage data",
                "pass_rate": analysis["pass_rate"],
                "usage_count": analysis["total_executions"]
            }

        if analysis["pass_rate"] >= 80:
            return {
                "should_evolve": False,
                "reason": "Performance is acceptable",
                "pass_rate": analysis["pass_rate"],
                "usage_count": analysis["total_executions"]
            }

        if analysis["trend"] == "improving":
            return {
                "should_evolve": False,
                "reason": "Performance is improving naturally",
                "pass_rate": analysis["pass_rate"],
                "usage_count": analysis["total_executions"]
            }

        return {
            "should_evolve": True,
            "reason": f"Low pass rate ({analysis['pass_rate']:.1f}%) with {len(analysis['common_errors'])} common errors",
            "pass_rate": analysis["pass_rate"],
            "usage_count": analysis["total_executions"],
            "common_errors": analysis["common_errors"]
        }


# Singleton
_evolution: Optional[StrategyEvolution] = None


def get_strategy_evolution() -> StrategyEvolution:
    """Get or create evolution singleton."""
    global _evolution
    if _evolution is None:
        _evolution = StrategyEvolution()
    return _evolution


# Convenience functions
async def evolve_strategy(strategy_id: int, force: bool = False) -> Optional[Dict]:
    """Evolve a single strategy."""
    evolution = get_strategy_evolution()
    return await evolution.evolve_strategy(strategy_id, force)


async def batch_evolve_strategies() -> List[Dict]:
    """Evolve all low-performing strategies."""
    evolution = get_strategy_evolution()
    return await evolution.batch_evolve()
