"""
Strategy Analyzer - Phase 20 Task 22

Weekly analysis to find "what works" in strategies.
Identifies patterns, top performers, and candidates for evolution.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger("review_agent.strategy_analyzer")


class StrategyAnalyzer:
    """
    Analyzes strategy performance to identify patterns.

    Generates insights like:
    - Top 5 strategies this week
    - Strategies to retire (low performance)
    - Common success patterns
    - Improvement opportunities
    """

    def __init__(self):
        self._db = None

    def _get_db(self):
        """Lazy load database adapter."""
        if self._db is None:
            from core.database_adapter import get_db_adapter
            self._db = get_db_adapter()
        return self._db

    async def analyze_all_strategies(self, days: int = 7) -> Dict[str, Any]:
        """
        Comprehensive analysis of all strategies.

        Returns:
            {
                "total_strategies": int,
                "total_executions": int,
                "overall_pass_rate": float,
                "top_strategies": List[Dict],
                "low_performers": List[Dict],
                "by_product_type": Dict[str, Dict],
                "recommendations": List[str]
            }
        """
        db = self._get_db()

        # Get all strategies
        strategies = db.list_strategies(is_experimental=False)
        total_strategies = len(strategies)

        if total_strategies == 0:
            return {
                "total_strategies": 0,
                "message": "No strategies found"
            }

        # Gather performance data
        all_performance = []
        strategy_stats = []

        for strategy in strategies:
            perf = db.get_strategy_performance(strategy["id"], days=days)
            if perf:
                all_performance.extend(perf)

                passed = sum(1 for p in perf if p.get("validation_passed"))
                pass_rate = (passed / len(perf)) * 100 if perf else 0

                strategy_stats.append({
                    "id": strategy["id"],
                    "name": strategy["name"],
                    "product_type": strategy["product_type"],
                    "executions": len(perf),
                    "passed": passed,
                    "failed": len(perf) - passed,
                    "pass_rate": pass_rate,
                    "score": strategy.get("performance_score", 0),
                    "usage_count": strategy.get("usage_count", 0)
                })

        # Calculate overall stats
        total_executions = len(all_performance)
        overall_passed = sum(1 for p in all_performance if p.get("validation_passed"))
        overall_pass_rate = (overall_passed / total_executions) * 100 if total_executions else 0

        # Sort by pass rate for top/bottom
        sorted_by_rate = sorted(strategy_stats, key=lambda x: x["pass_rate"], reverse=True)

        # Top performers (>= 80% pass rate, at least 3 executions)
        top_strategies = [
            s for s in sorted_by_rate
            if s["pass_rate"] >= 80 and s["executions"] >= 3
        ][:5]

        # Low performers (< 50% pass rate, at least 3 executions)
        low_performers = [
            s for s in sorted_by_rate
            if s["pass_rate"] < 50 and s["executions"] >= 3
        ][-5:]

        # By product type
        by_type = {}
        for s in strategy_stats:
            ptype = s["product_type"]
            if ptype not in by_type:
                by_type[ptype] = {"count": 0, "executions": 0, "passed": 0}
            by_type[ptype]["count"] += 1
            by_type[ptype]["executions"] += s["executions"]
            by_type[ptype]["passed"] += s["passed"]

        for ptype in by_type:
            execs = by_type[ptype]["executions"]
            if execs > 0:
                by_type[ptype]["pass_rate"] = (by_type[ptype]["passed"] / execs) * 100

        # Generate recommendations
        recommendations = self._generate_recommendations(
            strategy_stats, top_strategies, low_performers, by_type
        )

        return {
            "total_strategies": total_strategies,
            "total_executions": total_executions,
            "overall_pass_rate": overall_pass_rate,
            "top_strategies": top_strategies,
            "low_performers": low_performers,
            "by_product_type": by_type,
            "recommendations": recommendations,
            "analysis_date": datetime.utcnow().isoformat(),
            "period_days": days
        }

    def _generate_recommendations(
        self,
        all_stats: List[Dict],
        top: List[Dict],
        low: List[Dict],
        by_type: Dict
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Check for low performers needing evolution
        if len(low) > 0:
            names = ", ".join([s["name"] for s in low[:3]])
            recommendations.append(
                f"Consider evolving low-performing strategies: {names}"
            )

        # Check for unused strategies
        unused = [s for s in all_stats if s["executions"] == 0]
        if len(unused) > 5:
            recommendations.append(
                f"{len(unused)} strategies have never been used - consider cleanup"
            )

        # Product type insights
        for ptype, stats in by_type.items():
            if stats.get("pass_rate", 0) < 50 and stats["executions"] >= 5:
                recommendations.append(
                    f"'{ptype}' strategies have low overall pass rate ({stats['pass_rate']:.0f}%) - review category"
                )

        # Top performer insights
        if top:
            best = top[0]
            recommendations.append(
                f"Study top performer '{best['name']}' ({best['pass_rate']:.0f}%) for best practices"
            )

        if not recommendations:
            recommendations.append("All strategies performing within acceptable range")

        return recommendations

    async def get_weekly_report(self) -> str:
        """Generate a formatted weekly report."""
        analysis = await self.analyze_all_strategies(days=7)

        lines = [
            "=" * 60,
            "VULCAN STRATEGY ANALYSIS - WEEKLY REPORT",
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            "=" * 60,
            "",
            "SUMMARY",
            "-" * 40,
            f"Total Strategies: {analysis.get('total_strategies', 0)}",
            f"Total Executions: {analysis.get('total_executions', 0)}",
            f"Overall Pass Rate: {analysis.get('overall_pass_rate', 0):.1f}%",
            "",
        ]

        # Top performers
        if analysis.get("top_strategies"):
            lines.append("TOP PERFORMERS")
            lines.append("-" * 40)
            for i, s in enumerate(analysis["top_strategies"], 1):
                lines.append(f"{i}. {s['name']}")
                lines.append(f"   Pass Rate: {s['pass_rate']:.1f}% ({s['passed']}/{s['executions']})")
            lines.append("")

        # Low performers
        if analysis.get("low_performers"):
            lines.append("NEEDS ATTENTION")
            lines.append("-" * 40)
            for s in analysis["low_performers"]:
                lines.append(f"- {s['name']}: {s['pass_rate']:.1f}% ({s['failed']} failures)")
            lines.append("")

        # By product type
        if analysis.get("by_product_type"):
            lines.append("BY PRODUCT TYPE")
            lines.append("-" * 40)
            for ptype, stats in analysis["by_product_type"].items():
                rate = stats.get("pass_rate", 0)
                lines.append(f"- {ptype}: {stats['count']} strategies, {rate:.1f}% pass rate")
            lines.append("")

        # Recommendations
        if analysis.get("recommendations"):
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 40)
            for rec in analysis["recommendations"]:
                lines.append(f"* {rec}")
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)

    async def compare_strategies(
        self,
        strategy_ids: List[int]
    ) -> Dict[str, Any]:
        """Compare multiple strategies head-to-head."""
        db = self._get_db()

        comparisons = []
        for sid in strategy_ids:
            strategy = db.load_strategy(sid)
            if strategy:
                perf = db.get_strategy_performance(sid, days=30)
                passed = sum(1 for p in perf if p.get("validation_passed")) if perf else 0
                rate = (passed / len(perf)) * 100 if perf else 0

                comparisons.append({
                    "id": sid,
                    "name": strategy["name"],
                    "product_type": strategy["product_type"],
                    "version": strategy.get("version", 1),
                    "executions": len(perf) if perf else 0,
                    "pass_rate": rate,
                    "score": strategy.get("performance_score", 0)
                })

        # Sort by pass rate
        comparisons.sort(key=lambda x: x["pass_rate"], reverse=True)

        return {
            "strategies": comparisons,
            "winner": comparisons[0] if comparisons else None,
            "comparison_date": datetime.utcnow().isoformat()
        }

    def get_strategy_history(self, strategy_id: int) -> Dict[str, Any]:
        """Get detailed history for a single strategy."""
        db = self._get_db()

        strategy = db.load_strategy(strategy_id)
        if not strategy:
            return {"error": "Strategy not found"}

        versions = db.get_strategy_versions(strategy_id)
        performance = db.get_strategy_performance(strategy_id, days=90)

        # Weekly breakdown
        weekly = {}
        for perf in performance:
            date = perf.get("execution_date")
            if date:
                if isinstance(date, str):
                    date = datetime.fromisoformat(date)
                week = date.strftime("%Y-W%W")
                if week not in weekly:
                    weekly[week] = {"total": 0, "passed": 0}
                weekly[week]["total"] += 1
                if perf.get("validation_passed"):
                    weekly[week]["passed"] += 1

        return {
            "strategy": strategy,
            "versions": versions,
            "total_executions": len(performance),
            "weekly_breakdown": weekly,
            "version_history": [
                {
                    "version": v["version"],
                    "date": v.get("created_at"),
                    "reason": v.get("change_reason"),
                    "perf_before": v.get("performance_before"),
                    "perf_after": v.get("performance_after")
                }
                for v in versions
            ]
        }


# Singleton
_analyzer: Optional[StrategyAnalyzer] = None


def get_strategy_analyzer() -> StrategyAnalyzer:
    """Get or create analyzer singleton."""
    global _analyzer
    if _analyzer is None:
        _analyzer = StrategyAnalyzer()
    return _analyzer


# Convenience functions
async def analyze_strategies() -> Dict[str, Any]:
    """Analyze all strategies."""
    analyzer = get_strategy_analyzer()
    return await analyzer.analyze_all_strategies()


async def get_weekly_report() -> str:
    """Get formatted weekly report."""
    analyzer = get_strategy_analyzer()
    return await analyzer.get_weekly_report()
