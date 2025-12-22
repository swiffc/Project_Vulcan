"""
Queue Adapter - Command Batching System
Prevents overwhelming slow systems (CAD, Trading) with rapid commands.

Implements Rule: Section 6 - The Waiting Room pattern.
AI thinks in milliseconds, SolidWorks takes seconds.

Packages Used: asyncio (built-in)
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

logger = logging.getLogger("core.queue")


class Priority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class QueueTask:
    """A task in the queue."""
    id: str
    queue_name: str
    command: str
    payload: Dict[str, Any]
    priority: Priority = Priority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    retries: int = 0
    max_retries: int = 3


class QueueAdapter:
    """
    Async queue for managing command execution.
    
    Usage:
        queue = QueueAdapter()
        queue.register("cad", handler=cad_executor, concurrency=1)
        
        task_id = await queue.enqueue("cad", "extrude", {"depth": 10})
        result = await queue.wait_for(task_id)
    """
    
    def __init__(self):
        self.queues: Dict[str, deque] = {}
        self.handlers: Dict[str, Callable] = {}
        self.concurrency: Dict[str, int] = {}
        self.running: Dict[str, int] = {}
        self.tasks: Dict[str, QueueTask] = {}
        self._workers: Dict[str, asyncio.Task] = {}
        self._counter = 0
        
    def register(self, name: str, handler: Callable, concurrency: int = 1) -> None:
        """Register a queue with its handler."""
        self.queues[name] = deque()
        self.handlers[name] = handler
        self.concurrency[name] = concurrency
        self.running[name] = 0
        logger.info(f"📋 Registered queue: {name} (concurrency={concurrency})")
        
    async def enqueue(self, queue_name: str, command: str, 
                      payload: Dict = None, priority: Priority = Priority.NORMAL) -> str:
        """Add a task to the queue."""
        if queue_name not in self.queues:
            raise ValueError(f"Queue not registered: {queue_name}")
            
        self._counter += 1
        task_id = f"{queue_name}-{self._counter:06d}"
        
        task = QueueTask(
            id=task_id,
            queue_name=queue_name,
            command=command,
            payload=payload or {},
            priority=priority
        )
        
        self.tasks[task_id] = task
        self.queues[queue_name].append(task_id)
        
        # Sort by priority (higher first)
        self.queues[queue_name] = deque(sorted(
            self.queues[queue_name],
            key=lambda tid: self.tasks[tid].priority.value,
            reverse=True
        ))
        
        logger.debug(f"📥 Enqueued: {task_id} ({command})")
        
        # Start worker if not running
        await self._ensure_worker(queue_name)
        
        return task_id
        
    async def wait_for(self, task_id: str, timeout: float = 300) -> Any:
        """Wait for a task to complete."""
        if task_id not in self.tasks:
            raise ValueError(f"Task not found: {task_id}")
            
        start = datetime.utcnow()
        while True:
            task = self.tasks[task_id]
            
            if task.status == TaskStatus.COMPLETED:
                return task.result
            elif task.status == TaskStatus.FAILED:
                raise Exception(task.error)
            elif task.status == TaskStatus.CANCELLED:
                raise Exception("Task cancelled")
                
            # Check timeout
            elapsed = (datetime.utcnow() - start).total_seconds()
            if elapsed > timeout:
                raise TimeoutError(f"Task {task_id} timed out")
                
            await asyncio.sleep(0.1)
            
    async def cancel(self, task_id: str) -> bool:
        """Cancel a pending task."""
        if task_id not in self.tasks:
            return False
            
        task = self.tasks[task_id]
        if task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            return True
        return False
        
    async def _ensure_worker(self, queue_name: str) -> None:
        """Ensure worker is running for queue."""
        if queue_name not in self._workers or self._workers[queue_name].done():
            self._workers[queue_name] = asyncio.create_task(
                self._worker_loop(queue_name)
            )
            
    async def _worker_loop(self, queue_name: str) -> None:
        """Worker loop that processes queue."""
        while True:
            # Check if we can run more tasks
            if self.running[queue_name] >= self.concurrency[queue_name]:
                await asyncio.sleep(0.1)
                continue
                
            # Get next task
            if not self.queues[queue_name]:
                await asyncio.sleep(0.1)
                continue
                
            task_id = self.queues[queue_name].popleft()
            task = self.tasks.get(task_id)
            
            if not task or task.status == TaskStatus.CANCELLED:
                continue
                
            # Execute task
            asyncio.create_task(self._execute_task(task))
            
    async def _execute_task(self, task: QueueTask) -> None:
        """Execute a single task."""
        queue_name = task.queue_name
        self.running[queue_name] += 1
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        
        try:
            handler = self.handlers[queue_name]
            task.result = await handler(task.command, task.payload)
            task.status = TaskStatus.COMPLETED
            logger.debug(f"✅ Completed: {task.id}")
        except Exception as e:
            task.error = str(e)
            task.retries += 1
            
            if task.retries < task.max_retries:
                task.status = TaskStatus.PENDING
                self.queues[queue_name].appendleft(task.id)
                logger.warning(f"🔄 Retrying: {task.id} ({task.retries}/{task.max_retries})")
            else:
                task.status = TaskStatus.FAILED
                logger.error(f"❌ Failed: {task.id} - {e}")
        finally:
            task.completed_at = datetime.utcnow()
            self.running[queue_name] -= 1
            
    def get_status(self) -> Dict[str, Dict]:
        """Get queue status."""
        return {
            name: {
                "pending": len(self.queues[name]),
                "running": self.running[name],
                "concurrency": self.concurrency[name]
            }
            for name in self.queues
        }


# Singleton
_queue: Optional[QueueAdapter] = None

def get_queue() -> QueueAdapter:
    global _queue
    if _queue is None:
        _queue = QueueAdapter()
    return _queue
