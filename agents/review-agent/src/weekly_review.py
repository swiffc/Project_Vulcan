"""
Weekly Review Agent

Automated performance review that runs weekly (configurable).
Summarizes trading performance, identifies patterns, and generates recommendations.
HITL required for strategy updates (Rule 8).
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core.memory import VulcanMemory


class WeeklyReviewAgent:
    """Automated weekly performance review."""

    def __init__(self, memory: VulcanMemory, strategy_path: Optional[str] = None):
        """Initialize the review agent.

        Args:
            memory: VulcanMemory instance
            strategy_path: Path to strategy.json file
        """
        self.memory = memory
        self.strategy_path = strategy_path or "./config/strategy.json"

    def generate_review(self, week_start: str, week_end: str) -> Dict[str, Any]:
        """Generate weekly performance summary.

        Args:
            week_start: Start date (YYYY-MM-DD)
            week_end: End date (YYYY-MM-DD)

        Returns:
            Complete review with statistics, patterns, and recommendations
        """
        trades = self._get_trades_for_period(week_start, week_end)

        if not trades:
            return {
                "period": f"{week_start} to {week_end}",
                "statistics": {"total_trades": 0},
                "patterns": [],
                "recommendations": ["No trades found for this period."],
            }

        stats = self._calculate_stats(trades)
        patterns = self._identify_patterns(trades)
        recommendations = self._generate_recommendations(stats, patterns)

        return {
            "period": f"{week_start} to {week_end}",
            "statistics": stats,
            "patterns": patterns,
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat(),
        }

    def _get_trades_for_period(self, start: str, end: str) -> List[Dict]:
        """Get all trades for the specified period."""
        return self.memory.get_trades_by_date_range(start, end)

    def _calculate_stats(self, trades: List[Dict]) -> Dict[str, Any]:
        """Calculate performance statistics.

        Returns:
            Dict with win_rate, total_r, avg_r, best_trade, worst_trade, etc.
        """
        total = len(trades)
        wins = sum(1 for t in trades if t["metadata"].get("result") == "win")
        losses = total - wins

        r_multiples = [
            t["metadata"].get("r_multiple", 0)
            for t in trades
            if t["metadata"].get("r_multiple") is not None
        ]

        total_r = sum(r_multiples)
        avg_r = total_r / total if total > 0 else 0

        # Group by setup type
        by_setup = defaultdict(lambda: {"wins": 0, "losses": 0, "r": 0})
        for t in trades:
            setup = t["metadata"].get("setup_type", "unknown")
            if t["metadata"].get("result") == "win":
                by_setup[setup]["wins"] += 1
            else:
                by_setup[setup]["losses"] += 1
            by_setup[setup]["r"] += t["metadata"].get("r_multiple", 0)

        # Group by day
        by_day = defaultdict(lambda: {"wins": 0, "losses": 0})
        for t in trades:
            day = t["metadata"].get("day", "unknown")
            if t["metadata"].get("result") == "win":
                by_day[day]["wins"] += 1
            else:
                by_day[day]["losses"] += 1

        # Group by session
        by_session = defaultdict(lambda: {"wins": 0, "losses": 0})
        for t in trades:
            session = t["metadata"].get("session", "unknown")
            if t["metadata"].get("result") == "win":
                by_session[session]["wins"] += 1
            else:
                by_session[session]["losses"] += 1

        return {
            "total_trades": total,
            "wins": wins,
            "losses": losses,
            "win_rate": round(wins / total * 100, 1) if total > 0 else 0,
            "total_r": round(total_r, 2),
            "average_r": round(avg_r, 2),
            "best_r": max(r_multiples) if r_multiples else 0,
            "worst_r": min(r_multiples) if r_multiples else 0,
            "by_setup": dict(by_setup),
            "by_day": dict(by_day),
            "by_session": dict(by_session),
        }

    def _identify_patterns(self, trades: List[Dict]) -> List[Dict[str, Any]]:
        """Identify performance patterns.

        Returns:
            List of pattern observations with confidence scores
        """
        patterns = []
        stats = self._calculate_stats(trades)

        # Best performing setup
        best_setup = None
        best_setup_wr = 0
        for setup, data in stats["by_setup"].items():
            total = data["wins"] + data["losses"]
            if total >= 2:  # Minimum sample size
                wr = data["wins"] / total
                if wr > best_setup_wr:
                    best_setup_wr = wr
                    best_setup = setup

        if best_setup and best_setup_wr > 0.6:
            patterns.append(
                {
                    "type": "strong_setup",
                    "description": f"{best_setup} has {best_setup_wr*100:.0f}% win rate",
                    "confidence": "high" if best_setup_wr > 0.7 else "medium",
                    "action": f"Continue focusing on {best_setup} setups",
                }
            )

        # Worst performing setup
        for setup, data in stats["by_setup"].items():
            total = data["wins"] + data["losses"]
            if total >= 2:
                wr = data["wins"] / total
                if wr < 0.4:
                    patterns.append(
                        {
                            "type": "weak_setup",
                            "description": f"{setup} has only {wr*100:.0f}% win rate",
                            "confidence": "high" if wr < 0.3 else "medium",
                            "action": f"Review {setup} criteria or reduce position size",
                        }
                    )

        # Best performing day
        for day, data in stats["by_day"].items():
            total = data["wins"] + data["losses"]
            if total >= 2:
                wr = data["wins"] / total
                if wr > 0.7:
                    patterns.append(
                        {
                            "type": "strong_day",
                            "description": f"{day} has {wr*100:.0f}% win rate",
                            "confidence": "medium",
                            "action": f"Consider increasing size on {day}",
                        }
                    )
                elif wr < 0.3:
                    patterns.append(
                        {
                            "type": "weak_day",
                            "description": f"{day} has only {wr*100:.0f}% win rate",
                            "confidence": "medium",
                            "action": f"Avoid trading or reduce size on {day}",
                        }
                    )

        # Session performance
        for session, data in stats["by_session"].items():
            total = data["wins"] + data["losses"]
            if total >= 2:
                wr = data["wins"] / total
                if wr > 0.7:
                    patterns.append(
                        {
                            "type": "strong_session",
                            "description": f"{session} session has {wr*100:.0f}% win rate",
                            "confidence": "medium",
                            "action": f"Focus on {session} session",
                        }
                    )

        return patterns

    def _generate_recommendations(
        self, stats: Dict[str, Any], patterns: List[Dict]
    ) -> List[str]:
        """Generate actionable recommendations.

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Overall performance
        if stats["win_rate"] >= 60:
            recommendations.append(
                f"Strong week with {stats['win_rate']}% win rate. "
                "Maintain current approach."
            )
        elif stats["win_rate"] < 40:
            recommendations.append(
                f"Below target with {stats['win_rate']}% win rate. "
                "Review trade selection criteria."
            )

        # R performance
        if stats["total_r"] > 0:
            recommendations.append(
                f"Positive week: +{stats['total_r']}R total. "
                f"Average trade: {stats['average_r']}R."
            )
        else:
            recommendations.append(
                f"Negative week: {stats['total_r']}R total. " "Review risk management."
            )

        # Pattern-based recommendations
        for pattern in patterns:
            if pattern["confidence"] == "high":
                recommendations.append(pattern["action"])

        return recommendations

    def format_as_markdown(self, review: Dict[str, Any]) -> str:
        """Format review as markdown for display.

        Args:
            review: Review dict from generate_review()

        Returns:
            Formatted markdown string
        """
        stats = review["statistics"]

        md = f"""# Weekly Trading Review

**Period:** {review['period']}
**Generated:** {review.get('generated_at', 'N/A')}

---

## Performance Summary

| Metric | Value |
|--------|-------|
| Total Trades | {stats.get('total_trades', 0)} |
| Wins | {stats.get('wins', 0)} |
| Losses | {stats.get('losses', 0)} |
| Win Rate | {stats.get('win_rate', 0)}% |
| Total R | {stats.get('total_r', 0)} |
| Average R | {stats.get('average_r', 0)} |
| Best Trade | {stats.get('best_r', 0)}R |
| Worst Trade | {stats.get('worst_r', 0)}R |

---

## Patterns Identified

"""
        for pattern in review.get("patterns", []):
            md += f"- **{pattern['type']}**: {pattern['description']} "
            md += f"(Confidence: {pattern['confidence']})\n"

        md += "\n---\n\n## Recommendations\n\n"
        for rec in review.get("recommendations", []):
            md += f"- {rec}\n"

        return md

    def update_strategy_json(
        self, recommendations: List[str], require_approval: bool = True
    ) -> Dict[str, Any]:
        """Update strategy.json based on recommendations.

        IMPORTANT: Requires HITL approval per Rule 8.

        Args:
            recommendations: List of recommendation strings
            require_approval: If True, returns proposed changes without applying

        Returns:
            Dict with current strategy and proposed updates
        """
        strategy_file = Path(self.strategy_path)

        if strategy_file.exists():
            with open(strategy_file) as f:
                current_strategy = json.load(f)
        else:
            current_strategy = {
                "version": "1.0",
                "last_updated": None,
                "setups": {},
                "risk_rules": {},
                "session_preferences": {},
            }

        # Generate proposed updates based on recommendations
        proposed_updates = {
            "last_updated": datetime.now().isoformat(),
            "last_review_recommendations": recommendations,
        }

        result = {
            "current_strategy": current_strategy,
            "proposed_updates": proposed_updates,
            "require_approval": require_approval,
        }

        if not require_approval:
            # Apply updates
            current_strategy.update(proposed_updates)
            with open(strategy_file, "w") as f:
                json.dump(current_strategy, f, indent=2)
            result["applied"] = True

        return result


def get_last_week_dates() -> tuple:
    """Get start and end dates for last week."""
    today = datetime.now()
    # Find last Monday
    days_since_monday = today.weekday()
    last_monday = today - timedelta(days=days_since_monday + 7)
    last_sunday = last_monday + timedelta(days=6)
    return (last_monday.strftime("%Y-%m-%d"), last_sunday.strftime("%Y-%m-%d"))


if __name__ == "__main__":
    import os

    # Ensure storage directory exists
    review_dir = Path("storage/reviews")
    review_dir.mkdir(parents=True, exist_ok=True)

    try:
        print("Initializing Vulcan Memory...")
        memory = VulcanMemory()

        agent = WeeklyReviewAgent(memory)

        start_date, end_date = get_last_week_dates()
        print(f"Generating review for period: {start_date} to {end_date}")

        review = agent.generate_review(start_date, end_date)

        # Save JSON
        json_path = review_dir / f"review_{end_date}.json"
        with open(json_path, "w") as f:
            json.dump(review, f, indent=2)

        # Save Markdown
        md_content = agent.format_as_markdown(review)
        md_path = review_dir / f"Weekly_Review_{end_date}.md"
        with open(md_path, "w") as f:
            f.write(md_content)

        print(f"Review generated successfully!")
        print(f"Markdown: {md_path}")
        print(f"JSON: {json_path}")

    except Exception as e:
        print(f"Error generating review: {e}")
        sys.exit(1)
