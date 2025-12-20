"""
System Manager - David's Worker
Main entry point for the background daemon.
"""

import asyncio
import logging
import os

# Lazy import schedule to avoid startup overhead
schedule = None

from .scheduler import SystemManager
from .backup import BackupService
from .health_monitor import HealthMonitor
from .metrics_collector import MetricsCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger("system-manager")


def get_schedule():
    """Lazy load schedule module."""
    global schedule
    if schedule is None:
        import schedule as _schedule
        schedule = _schedule
    return schedule


async def main():
    """Initialize and run System Manager."""
    logger.info("🚀 Initializing System Manager...")

    # Initialize components
    manager = SystemManager()
    backup = BackupService()
    health = HealthMonitor()
    metrics = MetricsCollector()

    # Configure backup paths
    backup.add_backup_path("storage/trades")
    backup.add_backup_path("storage/cad_jobs")
    backup.add_backup_path("storage/reports")

    # Register services for health monitoring
    health.register_service("vulcan-web", os.getenv("WEB_URL"))
    health.register_service("vulcan-desktop", os.getenv("DESKTOP_SERVER_URL"))
    health.register_service("vulcan-memory", os.getenv("MEMORY_SERVER_URL"))

    # Get schedule module
    sched = get_schedule()

    # Register scheduled jobs

    # Daily: Backup to Drive at 2 AM
    sched.every().day.at("02:00").do(backup.run_daily_backup)
    logger.info("📅 Scheduled: Daily backup @ 02:00")

    # Hourly: Health check all services
    sched.every().hour.do(health.check_all_services)
    logger.info("📅 Scheduled: Hourly health checks")

    # Every 5 min: Collect metrics
    sched.every(5).minutes.do(metrics.collect)
    logger.info("📅 Scheduled: Metrics collection every 5 min")

    # Weekly: Generate performance report (Friday 5 PM)
    sched.every().friday.at("17:00").do(
        lambda: asyncio.create_task(manager.generate_weekly_report())
    )
    logger.info("📅 Scheduled: Weekly report @ Friday 17:00")

    logger.info(f"✅ System Manager started with {len(sched.get_jobs())} scheduled jobs")

    # Run initial health check
    health.check_all_services()

    # Run forever
    await manager.run_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("System Manager stopped by user")
