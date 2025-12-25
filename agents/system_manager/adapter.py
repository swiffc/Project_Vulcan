"""
System Manager Adapter
Thin wrapper around APScheduler + psutil for background job orchestration.

Packages Used (via pip - NOT in project):
- APScheduler: Job scheduling
- psutil: System metrics
- aiohttp: Health checks

See REFERENCES.md for documentation links.
"""

import logging
from datetime import datetime
from typing import Callable, Dict, Optional

logger = logging.getLogger("system_manager")


class SchedulerAdapter:
    """Thin adapter wrapping APScheduler."""
    
    def __init__(self):
        # Lazy import - only load when needed
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        self._scheduler = AsyncIOScheduler()
        self._jobs: Dict[str, str] = {}
        
    def add_job(self, name: str, func: Callable, trigger: str, **kwargs):
        """Register a scheduled job."""
        job = self._scheduler.add_job(func, trigger, **kwargs, id=name)
        self._jobs[name] = job.id
        logger.info(f"📅 Registered: {name}")
        
    def start(self):
        """Start the scheduler."""
        self._scheduler.start()
        logger.info("🚀 Scheduler started")
        
    def stop(self):
        """Stop the scheduler."""
        self._scheduler.shutdown()
        logger.info("🛑 Scheduler stopped")


class MetricsAdapter:
    """Thin adapter wrapping psutil for system metrics."""
    
    def get_system_metrics(self) -> Dict:
        """Collect current system metrics."""
        import psutil
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "timestamp": datetime.utcnow().isoformat()
        }


class HealthAdapter:
    """Thin adapter for service health checks."""
    
    async def check_http(self, url: str, timeout: int = 5) -> Dict:
        """Check HTTP endpoint health."""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                    return {"status": "healthy" if resp.status == 200 else "degraded", "code": resp.status}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class SystemManagerAdapter:
    """
    Main adapter combining scheduler, metrics, and health.
    Entry point for System Manager functionality.
    """
    
    def __init__(self):
        self.scheduler = SchedulerAdapter()
        self.metrics = MetricsAdapter()
        self.health = HealthAdapter()
        
    def setup_default_jobs(self, backup_func: Callable, health_func: Callable):
        """Register default scheduled jobs per PRD."""
        # Daily backup at 2 AM
        self.scheduler.add_job("daily_backup", backup_func, "cron", hour=2)
        # Hourly health check
        self.scheduler.add_job("health_check", health_func, "interval", hours=1)
        # Metrics every 5 min
        self.scheduler.add_job("metrics", self.metrics.get_system_metrics, "interval", minutes=5)
        # Weekly standards update (Sunday at 3 AM)
        self.scheduler.add_job("standards_update", self.run_standards_update, "cron", day_of_week="sun", hour=3)
        
    def run_standards_update(self):
        """Run the standards update script."""
        import subprocess
        import sys
        
        script_path = "scripts/pull_external_standards.py"
        python_executable = sys.executable
        
        try:
            subprocess.run([python_executable, script_path], check=True)
            logger.info("Standards update script completed successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Standards update script failed: {e}")
        
    def start(self):
        self.scheduler.start()
        
    def stop(self):
        self.scheduler.stop()
