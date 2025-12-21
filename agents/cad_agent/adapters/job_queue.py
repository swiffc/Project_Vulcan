"""
Job Queue Adapter
Batch processing for CAD files with resume capability.

Phase 11: CAD Performance Manager for 20K+ Part Assemblies
Handles: Export, rebuild, update operations on many files
"""

import json
import logging
import asyncio
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum
import uuid

logger = logging.getLogger("cad_agent.job-queue")


class JobStatus(Enum):
    """Job status states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class JobType(Enum):
    """Types of CAD jobs."""
    EXPORT_STEP = "export_step"
    EXPORT_PDF = "export_pdf"
    REBUILD = "rebuild"
    UPDATE_REFS = "update_refs"
    CHECK_HEALTH = "check_health"
    CUSTOM = "custom"


@dataclass
class Job:
    """A single CAD job in the queue."""
    id: str
    type: JobType
    file_path: str
    status: JobStatus = JobStatus.PENDING
    priority: int = 0  # Higher = more urgent
    params: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "file_path": self.file_path,
            "status": self.status.value,
            "priority": self.priority,
            "params": self.params,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Job":
        return cls(
            id=data["id"],
            type=JobType(data["type"]),
            file_path=data["file_path"],
            status=JobStatus(data["status"]),
            priority=data.get("priority", 0),
            params=data.get("params", {}),
            result=data.get("result"),
            error=data.get("error"),
            created_at=datetime.fromisoformat(data["created_at"]),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3)
        )


@dataclass
class BatchJob:
    """A batch of related jobs."""
    id: str
    name: str
    jobs: List[str] = field(default_factory=list)  # Job IDs
    total: int = 0
    completed: int = 0
    failed: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    restart_sw_every: int = 50  # Restart SW every N files

    @property
    def progress(self) -> float:
        return (self.completed / self.total * 100) if self.total > 0 else 0

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "jobs": self.jobs,
            "total": self.total,
            "completed": self.completed,
            "failed": self.failed,
            "progress": round(self.progress, 1),
            "created_at": self.created_at.isoformat(),
            "restart_sw_every": self.restart_sw_every
        }


class JobQueueAdapter:
    """
    Manages CAD job queue with persistence and resume.

    Usage:
        queue = JobQueueAdapter()

        # Add batch export job
        batch_id = queue.create_batch("Export Assembly", files, JobType.EXPORT_STEP)

        # Process jobs
        await queue.process_batch(batch_id, processor_func)

        # Resume after restart
        queue.load()
        await queue.resume_pending()
    """

    def __init__(self, storage_path: str = "storage/job_queue.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self.jobs: Dict[str, Job] = {}
        self.batches: Dict[str, BatchJob] = {}
        self._processing = False
        self._current_batch: Optional[str] = None
        self._on_progress: Optional[Callable] = None
        self._on_complete: Optional[Callable] = None
        self._files_since_restart = 0

    def create_job(self, job_type: JobType, file_path: str,
                   priority: int = 0, params: Dict = None) -> Job:
        """Create a single job."""
        job = Job(
            id=str(uuid.uuid4())[:8],
            type=job_type,
            file_path=file_path,
            priority=priority,
            params=params or {}
        )
        self.jobs[job.id] = job
        self._save()
        return job

    def create_batch(self, name: str, file_paths: List[str],
                     job_type: JobType, params: Dict = None,
                     restart_every: int = 50) -> str:
        """Create a batch of jobs."""
        batch_id = str(uuid.uuid4())[:8]

        batch = BatchJob(
            id=batch_id,
            name=name,
            total=len(file_paths),
            restart_sw_every=restart_every
        )

        for i, path in enumerate(file_paths):
            job = self.create_job(job_type, path, priority=-i, params=params)
            batch.jobs.append(job.id)

        self.batches[batch_id] = batch
        self._save()

        logger.info(f"Created batch '{name}' with {len(file_paths)} jobs")
        return batch_id

    def on_progress(self, callback: Callable[[BatchJob, Job], None]):
        """Register progress callback."""
        self._on_progress = callback

    def on_complete(self, callback: Callable[[BatchJob], None]):
        """Register batch complete callback."""
        self._on_complete = callback

    async def process_batch(self, batch_id: str,
                           processor: Callable[[Job], Dict],
                           restart_callback: Callable = None) -> BatchJob:
        """
        Process all jobs in a batch.

        Args:
            batch_id: Batch to process
            processor: Function that processes a job and returns result
            restart_callback: Called when SW needs restart
        """
        batch = self.batches.get(batch_id)
        if not batch:
            raise ValueError(f"Batch not found: {batch_id}")

        self._processing = True
        self._current_batch = batch_id
        self._files_since_restart = 0

        for job_id in batch.jobs:
            if not self._processing:
                logger.info("Processing paused")
                break

            job = self.jobs.get(job_id)
            if not job or job.status in [JobStatus.COMPLETED, JobStatus.CANCELLED]:
                continue

            # Check if restart needed
            if self._files_since_restart >= batch.restart_sw_every:
                logger.warning(f"Restarting SW after {self._files_since_restart} files")
                if restart_callback:
                    await restart_callback()
                self._files_since_restart = 0
                await asyncio.sleep(5)  # Wait for SW to restart

            # Process job
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now()
            self._save()

            try:
                result = await processor(job)
                job.status = JobStatus.COMPLETED
                job.result = result
                job.completed_at = datetime.now()
                batch.completed += 1
                self._files_since_restart += 1

                logger.info(f"Job {job.id} completed: {job.file_path}")

            except Exception as e:
                job.error = str(e)
                job.retry_count += 1

                if job.retry_count >= job.max_retries:
                    job.status = JobStatus.FAILED
                    batch.failed += 1
                    logger.error(f"Job {job.id} failed: {e}")
                else:
                    job.status = JobStatus.PENDING
                    logger.warning(f"Job {job.id} retry {job.retry_count}")

            self._save()

            if self._on_progress:
                self._on_progress(batch, job)

        self._processing = False
        self._current_batch = None

        if self._on_complete:
            self._on_complete(batch)

        logger.info(f"Batch '{batch.name}' complete: "
                   f"{batch.completed}/{batch.total} succeeded, "
                   f"{batch.failed} failed")

        return batch

    def pause(self):
        """Pause processing."""
        self._processing = False
        logger.info("Job queue paused")

    def resume(self):
        """Resume processing."""
        self._processing = True
        logger.info("Job queue resumed")

    async def resume_pending(self, processor: Callable[[Job], Dict],
                            restart_callback: Callable = None):
        """Resume any incomplete batches after restart."""
        for batch_id, batch in self.batches.items():
            pending = [j for j in batch.jobs
                      if self.jobs.get(j) and
                      self.jobs[j].status == JobStatus.PENDING]
            if pending:
                logger.info(f"Resuming batch '{batch.name}' with {len(pending)} pending")
                await self.process_batch(batch_id, processor, restart_callback)

    def get_batch_status(self, batch_id: str) -> Optional[Dict]:
        """Get batch progress status."""
        batch = self.batches.get(batch_id)
        if not batch:
            return None
        return batch.to_dict()

    def get_pending_count(self) -> int:
        """Get count of pending jobs."""
        return sum(1 for j in self.jobs.values() if j.status == JobStatus.PENDING)

    def cancel_batch(self, batch_id: str):
        """Cancel all pending jobs in a batch."""
        batch = self.batches.get(batch_id)
        if not batch:
            return

        for job_id in batch.jobs:
            job = self.jobs.get(job_id)
            if job and job.status == JobStatus.PENDING:
                job.status = JobStatus.CANCELLED

        self._save()
        logger.info(f"Cancelled batch: {batch.name}")

    def _save(self):
        """Save queue state to disk."""
        data = {
            "jobs": {k: v.to_dict() for k, v in self.jobs.items()},
            "batches": {k: v.to_dict() for k, v in self.batches.items()},
            "current_batch": self._current_batch
        }
        self.storage_path.write_text(json.dumps(data, indent=2))

    def load(self):
        """Load queue state from disk."""
        if not self.storage_path.exists():
            return

        try:
            data = json.loads(self.storage_path.read_text())
            self.jobs = {k: Job.from_dict(v) for k, v in data.get("jobs", {}).items()}
            # Note: BatchJob.from_dict would need implementation
            self._current_batch = data.get("current_batch")
            logger.info(f"Loaded queue: {len(self.jobs)} jobs, {len(self.batches)} batches")
        except Exception as e:
            logger.error(f"Failed to load queue: {e}")


# Singleton
_queue: Optional[JobQueueAdapter] = None

def get_job_queue() -> JobQueueAdapter:
    global _queue
    if _queue is None:
        _queue = JobQueueAdapter()
        _queue.load()
    return _queue
