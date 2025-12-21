"""
Performance Manager Adapter
Monitors RAM/GPU and auto-switches performance tiers.

Phase 11: CAD Performance Manager for 20K+ Part Assemblies
Packages Used: psutil, GPUtil
"""

import logging
import asyncio
from typing import Dict, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger("cad_agent.performance")


class PerformanceTier(Enum):
    """Performance tiers for SolidWorks graphics."""
    FULL = "full"           # All effects, max quality
    REDUCED = "reduced"     # Disable shadows, anti-aliasing
    MINIMAL = "minimal"     # Wireframe, no textures
    SURVIVAL = "survival"   # Large assembly mode, hide parts


@dataclass
class SystemMetrics:
    """Current system performance metrics."""
    ram_percent: float = 0.0
    ram_used_gb: float = 0.0
    ram_total_gb: float = 0.0
    gpu_percent: float = 0.0
    gpu_memory_used_mb: float = 0.0
    gpu_memory_total_mb: float = 0.0
    cpu_percent: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            "ram_percent": self.ram_percent,
            "ram_used_gb": round(self.ram_used_gb, 2),
            "ram_total_gb": round(self.ram_total_gb, 2),
            "gpu_percent": self.gpu_percent,
            "gpu_memory_used_mb": round(self.gpu_memory_used_mb, 0),
            "gpu_memory_total_mb": round(self.gpu_memory_total_mb, 0),
            "cpu_percent": self.cpu_percent,
            "timestamp": self.timestamp.isoformat()
        }


# RAM thresholds from task.md
RAM_THRESHOLDS = {
    60: PerformanceTier.REDUCED,   # 60% RAM -> REDUCED mode
    75: PerformanceTier.MINIMAL,   # 75% RAM -> MINIMAL mode
    85: PerformanceTier.SURVIVAL,  # 85% RAM -> SURVIVAL mode
    90: "RESTART"                  # 90% RAM -> Force restart SW
}


class PerformanceManager:
    """
    Monitors system resources and auto-adjusts SolidWorks performance.

    Usage:
        manager = PerformanceManager()
        await manager.start_monitoring()

        # Register callback for tier changes
        manager.on_tier_change(lambda tier: print(f"Tier: {tier}"))

        # Check current metrics
        metrics = manager.get_metrics()
    """

    def __init__(self):
        self._psutil = None
        self._gputil = None
        self._current_tier = PerformanceTier.FULL
        self._metrics = SystemMetrics()
        self._monitoring = False
        self._callbacks: List[Callable] = []
        self._restart_callback: Optional[Callable] = None
        self._monitor_task: Optional[asyncio.Task] = None

    def _lazy_import(self):
        """Lazy import heavy packages."""
        if self._psutil is None:
            try:
                import psutil
                self._psutil = psutil
            except ImportError:
                logger.warning("psutil not installed: pip install psutil")

        if self._gputil is None:
            try:
                import GPUtil
                self._gputil = GPUtil
            except ImportError:
                logger.warning("GPUtil not installed: pip install GPUtil")

    def get_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        self._lazy_import()

        metrics = SystemMetrics()

        # RAM metrics
        if self._psutil:
            mem = self._psutil.virtual_memory()
            metrics.ram_percent = mem.percent
            metrics.ram_used_gb = mem.used / (1024**3)
            metrics.ram_total_gb = mem.total / (1024**3)
            metrics.cpu_percent = self._psutil.cpu_percent(interval=0.1)

        # GPU metrics
        if self._gputil:
            gpus = self._gputil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Primary GPU
                metrics.gpu_percent = gpu.load * 100
                metrics.gpu_memory_used_mb = gpu.memoryUsed
                metrics.gpu_memory_total_mb = gpu.memoryTotal

        self._metrics = metrics
        return metrics

    def get_recommended_tier(self, metrics: Optional[SystemMetrics] = None) -> PerformanceTier:
        """Determine recommended tier based on RAM usage."""
        if metrics is None:
            metrics = self.get_metrics()

        ram = metrics.ram_percent

        if ram >= 90:
            return None  # Signal restart needed
        elif ram >= 85:
            return PerformanceTier.SURVIVAL
        elif ram >= 75:
            return PerformanceTier.MINIMAL
        elif ram >= 60:
            return PerformanceTier.REDUCED
        else:
            return PerformanceTier.FULL

    def on_tier_change(self, callback: Callable[[PerformanceTier], None]):
        """Register callback for tier changes."""
        self._callbacks.append(callback)

    def on_restart_needed(self, callback: Callable[[], None]):
        """Register callback for when restart is needed (90%+ RAM)."""
        self._restart_callback = callback

    async def start_monitoring(self, interval_seconds: float = 5.0):
        """Start background monitoring loop."""
        if self._monitoring:
            return

        self._monitoring = True
        logger.info("Starting performance monitoring")

        async def monitor_loop():
            while self._monitoring:
                try:
                    metrics = self.get_metrics()
                    recommended = self.get_recommended_tier(metrics)

                    if recommended is None:
                        # 90%+ RAM - trigger restart
                        logger.warning("RAM critical (90%+) - restart needed!")
                        if self._restart_callback:
                            self._restart_callback()
                    elif recommended != self._current_tier:
                        old_tier = self._current_tier
                        self._current_tier = recommended
                        logger.info(f"Tier change: {old_tier.value} -> {recommended.value}")
                        for callback in self._callbacks:
                            callback(recommended)

                except Exception as e:
                    logger.error(f"Monitoring error: {e}")

                await asyncio.sleep(interval_seconds)

        self._monitor_task = asyncio.create_task(monitor_loop())

    async def stop_monitoring(self):
        """Stop background monitoring."""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped performance monitoring")

    @property
    def current_tier(self) -> PerformanceTier:
        return self._current_tier

    def set_tier(self, tier: PerformanceTier):
        """Manually set performance tier."""
        if tier != self._current_tier:
            old = self._current_tier
            self._current_tier = tier
            logger.info(f"Manual tier change: {old.value} -> {tier.value}")
            for callback in self._callbacks:
                callback(tier)


# Singleton
_manager: Optional[PerformanceManager] = None

def get_performance_manager() -> PerformanceManager:
    global _manager
    if _manager is None:
        _manager = PerformanceManager()
    return _manager
