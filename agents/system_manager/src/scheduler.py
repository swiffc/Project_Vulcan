"""
System Manager - Scheduler
Background daemon for job scheduling.
"""

import asyncio
import logging
from datetime import datetime
from typing import Callable, Dict, Any

logger = logging.getLogger("system-manager.scheduler")


class SystemManager:
    """Core system manager with job scheduling."""

    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.running = False
        self._schedule_module = None

    def _get_schedule(self):
        """Lazy load schedule module."""
        if self._schedule_module is None:
            import schedule
            self._schedule_module = schedule
        return self._schedule_module

    def register_job(self, name: str, func: Callable, schedule_expr: str) -> None:
        """
        Register a scheduled job.

        Args:
            name: Unique job identifier
            func: Callable to execute
            schedule_expr: Human-readable schedule (e.g., "daily at 02:00")
        """
        self.jobs[name] = {"func": func, "schedule": schedule_expr, "last_run": None}
        logger.info(f"Registered job: {name} @ {schedule_expr}")

    async def run_forever(self) -> None:
        """Main daemon loop - runs scheduled jobs."""
        schedule = self._get_schedule()
        self.running = True
        logger.info("System Manager started")

        while self.running:
            schedule.run_pending()
            await asyncio.sleep(60)

    def stop(self) -> None:
        """Stop the daemon loop."""
        self.running = False
        logger.info("System Manager stopped")

    async def generate_weekly_report(self) -> dict:
        """Generate weekly performance report."""
        logger.info("Generating weekly report...")

        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "jobs_registered": len(self.jobs),
            "jobs_summary": {
                name: {
                    "schedule": job["schedule"],
                    "last_run": job["last_run"]
                }
                for name, job in self.jobs.items()
            }
        }

        return report
