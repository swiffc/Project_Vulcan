"""
Autonomous Feedback Loop - Phase 20 Task 24

Fully automated learning cycle that:
1. Analyzes strategy performance weekly
2. Evolves low-performing strategies
3. Notifies about improvements
4. Logs learning activities

This is the "AI Operating System" autonomous learning component.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger("core.feedback_loop")

# Learning logs directory
LEARNING_LOGS_DIR = Path(__file__).parent.parent / "data" / "learning_logs"
LEARNING_LOGS_DIR.mkdir(parents=True, exist_ok=True)


class FeedbackLoop:
    """
    Autonomous learning loop for strategy evolution.

    Runs weekly (typically Sunday midnight) to:
    1. Trigger strategy analysis
    2. Identify low performers
    3. Evolve failing strategies
    4. Log all learning activities
    """

    def __init__(self):
        self._db = None
        self._evolution = None
        self._analyzer = None
        self._last_run: Optional[datetime] = None

    def _get_db(self):
        """Lazy load database adapter."""
        if self._db is None:
            from core.database_adapter import get_db_adapter
            self._db = get_db_adapter()
        return self._db

    def _get_evolution(self):
        """Lazy load evolution module."""
        if self._evolution is None:
            from agents.cad_agent.strategy_evolution import get_strategy_evolution
            self._evolution = get_strategy_evolution()
        return self._evolution

    def _get_analyzer(self):
        """Lazy load strategy analyzer."""
        if self._analyzer is None:
            from agents.review_agent.src.strategy_analyzer import get_strategy_analyzer
            self._analyzer = get_strategy_analyzer()
        return self._analyzer

    async def run_cycle(self, force: bool = False) -> Dict[str, Any]:
        """
        Run one complete learning cycle.

        Args:
            force: Run even if recently executed

        Returns:
            Cycle results with statistics
        """
        cycle_start = datetime.utcnow()

        # Check if we should run
        if not force and self._last_run:
            hours_since_last = (cycle_start - self._last_run).total_seconds() / 3600
            if hours_since_last < 24:  # At least 24 hours between runs
                logger.info(f"Skipping cycle - only {hours_since_last:.1f} hours since last run")
                return {"skipped": True, "reason": "Too soon since last run"}

        logger.info("Starting feedback loop cycle...")

        results = {
            "cycle_start": cycle_start.isoformat(),
            "cycle_end": None,
            "strategies_analyzed": 0,
            "strategies_evolved": 0,
            "top_performers": [],
            "evolved_strategies": [],
            "errors": []
        }

        try:
            # Step 1: Analyze all strategies
            logger.info("Step 1: Analyzing strategy performance...")
            try:
                analyzer = self._get_analyzer()
                analysis = await analyzer.analyze_all_strategies()
                results["strategies_analyzed"] = analysis.get("total_strategies", 0)
                results["top_performers"] = analysis.get("top_strategies", [])[:5]
            except Exception as e:
                logger.warning(f"Strategy analysis skipped: {e}")
                results["errors"].append(f"Analysis error: {e}")

            # Step 2: Evolve low performers
            logger.info("Step 2: Evolving low-performing strategies...")
            try:
                evolution = self._get_evolution()
                evolved = await evolution.batch_evolve(
                    threshold=50.0,
                    min_usage=3,
                    max_evolutions=5
                )
                results["strategies_evolved"] = len(evolved)
                results["evolved_strategies"] = [
                    {"id": s.get("id"), "name": s.get("name"), "version": s.get("version")}
                    for s in evolved
                ]
            except Exception as e:
                logger.warning(f"Evolution skipped: {e}")
                results["errors"].append(f"Evolution error: {e}")

            # Step 3: Generate summary report
            logger.info("Step 3: Generating learning report...")
            report = self._generate_report(results)
            results["report"] = report

            # Step 4: Log the cycle
            cycle_end = datetime.utcnow()
            results["cycle_end"] = cycle_end.isoformat()
            results["duration_seconds"] = (cycle_end - cycle_start).total_seconds()

            self._save_log(results)
            self._last_run = cycle_end

            logger.info(f"Feedback loop complete: {results['strategies_evolved']} evolved, "
                       f"{results['strategies_analyzed']} analyzed in {results['duration_seconds']:.1f}s")

        except Exception as e:
            logger.error(f"Feedback loop error: {e}")
            results["errors"].append(f"Critical error: {e}")
            results["cycle_end"] = datetime.utcnow().isoformat()

        return results

    def _generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable learning report."""
        lines = [
            "=" * 50,
            "VULCAN LEARNING CYCLE REPORT",
            f"Date: {results['cycle_start']}",
            "=" * 50,
            "",
            f"Strategies Analyzed: {results['strategies_analyzed']}",
            f"Strategies Evolved: {results['strategies_evolved']}",
            "",
        ]

        if results.get("top_performers"):
            lines.append("TOP PERFORMERS:")
            for i, s in enumerate(results["top_performers"], 1):
                lines.append(f"  {i}. {s.get('name', 'Unknown')} - {s.get('score', 0):.1f}%")
            lines.append("")

        if results.get("evolved_strategies"):
            lines.append("EVOLVED THIS CYCLE:")
            for s in results["evolved_strategies"]:
                lines.append(f"  - {s.get('name', 'Unknown')} (v{s.get('version', '?')})")
            lines.append("")

        if results.get("errors"):
            lines.append("ERRORS:")
            for err in results["errors"]:
                lines.append(f"  ! {err}")
            lines.append("")

        lines.append("=" * 50)
        return "\n".join(lines)

    def _save_log(self, results: Dict[str, Any]):
        """Save cycle log to file."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        log_file = LEARNING_LOGS_DIR / f"cycle_{timestamp}.json"

        try:
            with open(log_file, "w") as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Saved learning log to {log_file}")
        except Exception as e:
            logger.error(f"Failed to save learning log: {e}")

    def get_recent_logs(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent learning cycle logs."""
        logs = []
        log_files = sorted(LEARNING_LOGS_DIR.glob("cycle_*.json"), reverse=True)

        for log_file in log_files[:count]:
            try:
                with open(log_file) as f:
                    logs.append(json.load(f))
            except Exception as e:
                logger.error(f"Failed to read log {log_file}: {e}")

        return logs

    def get_learning_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get aggregate learning statistics."""
        logs = self.get_recent_logs(count=100)
        cutoff = datetime.utcnow() - timedelta(days=days)

        recent_logs = [
            l for l in logs
            if datetime.fromisoformat(l.get("cycle_start", "2000-01-01")) >= cutoff
        ]

        if not recent_logs:
            return {"cycles": 0, "message": "No learning cycles in period"}

        return {
            "cycles": len(recent_logs),
            "total_evolved": sum(l.get("strategies_evolved", 0) for l in recent_logs),
            "total_analyzed": sum(l.get("strategies_analyzed", 0) for l in recent_logs),
            "avg_duration": sum(l.get("duration_seconds", 0) for l in recent_logs) / len(recent_logs),
            "last_run": recent_logs[0].get("cycle_end"),
            "errors": sum(len(l.get("errors", [])) for l in recent_logs)
        }


# Singleton
_feedback_loop: Optional[FeedbackLoop] = None


def get_feedback_loop() -> FeedbackLoop:
    """Get or create feedback loop singleton."""
    global _feedback_loop
    if _feedback_loop is None:
        _feedback_loop = FeedbackLoop()
    return _feedback_loop


# ===== SCHEDULED EXECUTION =====

async def run_weekly_cycle():
    """
    Entry point for weekly scheduled execution.
    Call this from a cron job or scheduler.
    """
    loop = get_feedback_loop()
    return await loop.run_cycle()


async def trigger_manual_cycle():
    """Manually trigger a learning cycle."""
    loop = get_feedback_loop()
    return await loop.run_cycle(force=True)


def setup_scheduler():
    """
    Set up APScheduler for weekly execution.
    Call this on application startup.
    """
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger

        scheduler = AsyncIOScheduler()

        # Run every Sunday at midnight UTC
        scheduler.add_job(
            run_weekly_cycle,
            CronTrigger(day_of_week="sun", hour=0, minute=0),
            id="feedback_loop_weekly",
            replace_existing=True
        )

        scheduler.start()
        logger.info("Feedback loop scheduler started (runs Sunday 00:00 UTC)")
        return scheduler

    except ImportError:
        logger.warning("APScheduler not installed - weekly cycle disabled")
        return None


# ===== CLI INTERFACE =====

if __name__ == "__main__":
    import sys

    async def main():
        if len(sys.argv) > 1 and sys.argv[1] == "--force":
            print("Forcing learning cycle...")
            results = await trigger_manual_cycle()
        else:
            print("Running learning cycle (will skip if recently run)...")
            results = await run_weekly_cycle()

        print("\n" + results.get("report", "No report generated"))
        print(f"\nCycle completed in {results.get('duration_seconds', 0):.1f} seconds")

    asyncio.run(main())
