# NEXT TASK FOR CLI: CAD Performance Manager + PDM Integration

**From**: Claude Chat  
**Priority**: HIGH  
**Type**: New Feature - Complete CAD Automation System  
**Estimated Files**: 8 new adapters  

---

## 🎯 OBJECTIVE

Build a complete CAD automation system that:
1. Manages SolidWorks PDM check-out/check-in
2. Handles 20,000+ part assemblies efficiently
3. Monitors system resources and auto-adjusts settings
4. Queues and processes batch jobs with resume capability
5. Validates changes via Inspector Agent
6. Shows notifications in Web UI

---

## 📁 FILES TO CREATE

### 1. PDM Adapter (CRITICAL)
**File**: `agents/cad_agent/adapters/pdm_adapter.py`  
**Lines**: ~300

```python
"""
SolidWorks PDM Adapter
Manages file checkout/checkin, versioning, and state queries.

Uses: SolidWorks PDM API via COM
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import pythoncom
import win32com.client

logger = logging.getLogger("cad.pdm-adapter")


class PDMState(Enum):
    """PDM workflow states."""
    IN_WORK = "In Work"
    PENDING_APPROVAL = "Pending Approval"
    RELEASED = "Released"
    OBSOLETE = "Obsolete"


@dataclass
class FileStatus:
    """Status of a file in PDM."""
    path: str
    state: PDMState
    checked_out_by: Optional[str]
    is_available: bool
    version: int
    

class PDMAdapter:
    """
    Manages SolidWorks PDM operations for bot automation.
    
    Usage:
        pdm = PDMAdapter(vault_name="MyVault")
        
        # Check what's available
        status = pdm.get_availability(file_paths)
        
        # Check out
        pdm.batch_checkout(status["available"])
        
        # After editing...
        pdm.batch_checkin(files, comment="Updated by Vulcan Bot")
    """
    
    def __init__(self, vault_name: str):
        self.vault_name = vault_name
        self._vault = None
        self._connection = None
        
    def connect(self, username: str = None, password: str = None) -> bool:
        """Connect to PDM vault."""
        try:
            pythoncom.CoInitialize()
            
            # Get PDM type library
            pdm_app = win32com.client.Dispatch("ConisioLib.EdmVault")
            
            # Login to vault
            if username and password:
                pdm_app.LoginAuto(self.vault_name, 0)  # Or use Login(vault, user, pass)
            else:
                pdm_app.LoginAuto(self.vault_name, 0)
                
            self._vault = pdm_app
            logger.info(f"Connected to PDM vault: {self.vault_name}")
            return True
            
        except Exception as e:
            logger.error(f"PDM connection failed: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from vault."""
        self._vault = None
        pythoncom.CoUninitialize()
        
    def get_file_status(self, file_path: str) -> FileStatus:
        """Get status of a single file."""
        try:
            file_obj = self._vault.GetFileFromPath(file_path)
            if not file_obj:
                return FileStatus(
                    path=file_path,
                    state=PDMState.IN_WORK,
                    checked_out_by=None,
                    is_available=False,
                    version=0
                )
            
            # Get state
            state_name = file_obj.CurrentState.Name
            state = PDMState(state_name) if state_name in [s.value for s in PDMState] else PDMState.IN_WORK
            
            # Check if locked
            locked_by = file_obj.LockedByUser.Name if file_obj.IsLocked else None
            
            # Is it available for us?
            is_available = (
                state == PDMState.IN_WORK and
                (locked_by is None or locked_by == self._vault.LoginUserName)
            )
            
            return FileStatus(
                path=file_path,
                state=state,
                checked_out_by=locked_by,
                is_available=is_available,
                version=file_obj.CurrentVersion
            )
            
        except Exception as e:
            logger.error(f"Error getting status for {file_path}: {e}")
            return FileStatus(
                path=file_path,
                state=PDMState.IN_WORK,
                checked_out_by=None,
                is_available=False,
                version=0
            )
            
    def get_availability(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Check availability of multiple files.
        
        Returns:
            {
                "available": [...],
                "checked_out_by_others": [...],
                "released": [...],
                "not_found": [...]
            }
        """
        result = {
            "available": [],
            "checked_out_by_others": [],
            "released": [],
            "not_found": []
        }
        
        for path in file_paths:
            status = self.get_file_status(path)
            
            if status.version == 0:
                result["not_found"].append(path)
            elif status.state == PDMState.RELEASED:
                result["released"].append(path)
            elif status.checked_out_by and status.checked_out_by != self._vault.LoginUserName:
                result["checked_out_by_others"].append(path)
            elif status.is_available:
                result["available"].append(path)
                
        logger.info(f"Availability: {len(result['available'])} available, "
                   f"{len(result['checked_out_by_others'])} locked, "
                   f"{len(result['released'])} released")
                   
        return result
        
    def get_latest(self, file_paths: List[str]) -> Dict[str, bool]:
        """Get latest version of files from vault."""
        results = {}
        
        for path in file_paths:
            try:
                file_obj = self._vault.GetFileFromPath(path)
                folder = self._vault.GetFolderFromPath(path.rsplit("\\", 1)[0])
                
                # Get latest
                file_obj.GetFileCopy(0, folder.LocalPath)
                results[path] = True
                
            except Exception as e:
                logger.error(f"Get latest failed for {path}: {e}")
                results[path] = False
                
        return results
        
    def batch_checkout(self, file_paths: List[str]) -> Dict[str, bool]:
        """Check out multiple files."""
        results = {}
        
        for path in file_paths:
            try:
                file_obj = self._vault.GetFileFromPath(path)
                folder = self._vault.GetFolderFromPath(path.rsplit("\\", 1)[0])
                
                # Check out
                file_obj.LockFile(folder.ID, 0)
                results[path] = True
                logger.debug(f"Checked out: {path}")
                
            except Exception as e:
                logger.error(f"Checkout failed for {path}: {e}")
                results[path] = False
                
        success = sum(1 for v in results.values() if v)
        logger.info(f"Checked out {success}/{len(file_paths)} files")
        
        return results
        
    def batch_checkin(
        self, 
        file_paths: List[str], 
        comment: str = "Updated by Vulcan Bot"
    ) -> Dict[str, bool]:
        """Check in multiple files with comment."""
        results = {}
        
        for path in file_paths:
            try:
                file_obj = self._vault.GetFileFromPath(path)
                folder = self._vault.GetFolderFromPath(path.rsplit("\\", 1)[0])
                
                # Check in with comment
                file_obj.UnlockFile(folder.ID, comment)
                results[path] = True
                logger.debug(f"Checked in: {path}")
                
            except Exception as e:
                logger.error(f"Checkin failed for {path}: {e}")
                results[path] = False
                
        success = sum(1 for v in results.values() if v)
        logger.info(f"Checked in {success}/{len(file_paths)} files")
        
        return results
        
    def undo_checkout(self, file_paths: List[str]) -> Dict[str, bool]:
        """Undo checkout (discard changes)."""
        results = {}
        
        for path in file_paths:
            try:
                file_obj = self._vault.GetFileFromPath(path)
                folder = self._vault.GetFolderFromPath(path.rsplit("\\", 1)[0])
                
                # Undo checkout
                file_obj.UndoLockFile(folder.ID)
                results[path] = True
                
            except Exception as e:
                logger.error(f"Undo checkout failed for {path}: {e}")
                results[path] = False
                
        return results
        
    def get_where_used(self, file_path: str) -> List[str]:
        """Get list of assemblies/drawings that reference this file."""
        try:
            file_obj = self._vault.GetFileFromPath(file_path)
            refs = file_obj.GetReferencedByFiles()
            
            return [ref.Path for ref in refs] if refs else []
            
        except Exception as e:
            logger.error(f"Where-used query failed: {e}")
            return []


# Singleton
_pdm: Optional[PDMAdapter] = None

def get_pdm_adapter(vault_name: str = None) -> PDMAdapter:
    global _pdm
    if _pdm is None:
        vault = vault_name or "DefaultVault"  # Configure via env
        _pdm = PDMAdapter(vault)
    return _pdm
```

---

### 2. Job Queue (CRITICAL)
**File**: `agents/cad_agent/adapters/job_queue.py`  
**Lines**: ~250

```python
"""
CAD Job Queue
Manages batch processing with resume capability.

Features:
- Priority queue
- Resume interrupted jobs
- Progress tracking
- Batch grouping (restart SW every N files)
"""

import json
import logging
import time
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import uuid

logger = logging.getLogger("cad.job-queue")


class JobStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Job:
    """Single file operation."""
    id: str
    file_path: str
    operation: str  # "update_dimension", "add_feature", etc.
    parameters: Dict[str, Any]
    status: JobStatus = JobStatus.PENDING
    error: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    
@dataclass
class BatchJob:
    """Collection of jobs with metadata."""
    id: str
    name: str
    jobs: List[Job]
    created_at: float
    batch_size: int = 50  # Restart SW every N files
    current_index: int = 0
    status: JobStatus = JobStatus.PENDING
    

class JobQueue:
    """
    Manages CAD batch jobs with persistence.
    
    Usage:
        queue = JobQueue()
        
        # Create batch
        batch = queue.create_batch(
            name="Update brackets",
            files=["part1.sldprt", "part2.sldprt"],
            operation="update_dimension",
            parameters={"dimension": "D1@Sketch1", "value": 25.0}
        )
        
        # Process
        queue.process_batch(batch.id, processor_func)
        
        # Check progress
        progress = queue.get_progress(batch.id)
    """
    
    def __init__(self, state_file: str = None):
        self.state_file = state_file or Path.home() / ".vulcan" / "job_queue.json"
        self.batches: Dict[str, BatchJob] = {}
        self._load_state()
        
    def _load_state(self):
        """Load persisted state for resume capability."""
        try:
            if Path(self.state_file).exists():
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    # Reconstruct batches from saved state
                    for batch_data in data.get("batches", []):
                        jobs = [Job(**j) for j in batch_data.pop("jobs", [])]
                        batch = BatchJob(**batch_data, jobs=jobs)
                        self.batches[batch.id] = batch
                logger.info(f"Loaded {len(self.batches)} batches from state")
        except Exception as e:
            logger.warning(f"Could not load state: {e}")
            
    def _save_state(self):
        """Persist state for resume capability."""
        try:
            Path(self.state_file).parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "batches": [
                    {**asdict(b), "jobs": [asdict(j) for j in b.jobs]}
                    for b in self.batches.values()
                    if b.status != JobStatus.COMPLETED
                ]
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Could not save state: {e}")
            
    def create_batch(
        self,
        name: str,
        files: List[str],
        operation: str,
        parameters: Dict[str, Any],
        batch_size: int = 50
    ) -> BatchJob:
        """Create a new batch job."""
        batch_id = str(uuid.uuid4())[:8]
        
        jobs = [
            Job(
                id=f"{batch_id}-{i}",
                file_path=file,
                operation=operation,
                parameters=parameters
            )
            for i, file in enumerate(files)
        ]
        
        batch = BatchJob(
            id=batch_id,
            name=name,
            jobs=jobs,
            created_at=time.time(),
            batch_size=batch_size
        )
        
        self.batches[batch_id] = batch
        self._save_state()
        
        logger.info(f"Created batch {batch_id}: {len(jobs)} jobs")
        return batch
        
    def process_batch(
        self,
        batch_id: str,
        processor: Callable[[Job], bool],
        on_progress: Callable[[int, int], None] = None,
        on_batch_complete: Callable[[], None] = None
    ) -> Dict[str, Any]:
        """
        Process a batch job.
        
        Args:
            batch_id: Batch to process
            processor: Function that processes a single job, returns success bool
            on_progress: Callback(current, total) for progress updates
            on_batch_complete: Called every batch_size files (for SW restart)
        """
        batch = self.batches.get(batch_id)
        if not batch:
            return {"error": "Batch not found"}
            
        batch.status = JobStatus.IN_PROGRESS
        
        results = {
            "completed": 0,
            "failed": 0,
            "skipped": 0
        }
        
        for i, job in enumerate(batch.jobs[batch.current_index:], batch.current_index):
            # Skip already processed
            if job.status in [JobStatus.COMPLETED, JobStatus.SKIPPED]:
                continue
                
            job.status = JobStatus.IN_PROGRESS
            job.started_at = time.time()
            
            try:
                success = processor(job)
                
                if success:
                    job.status = JobStatus.COMPLETED
                    results["completed"] += 1
                else:
                    job.status = JobStatus.FAILED
                    results["failed"] += 1
                    
            except Exception as e:
                job.status = JobStatus.FAILED
                job.error = str(e)
                results["failed"] += 1
                logger.error(f"Job {job.id} failed: {e}")
                
            job.completed_at = time.time()
            batch.current_index = i + 1
            
            # Progress callback
            if on_progress:
                on_progress(i + 1, len(batch.jobs))
                
            # Batch complete callback (for SW restart)
            if (i + 1) % batch.batch_size == 0 and on_batch_complete:
                logger.info(f"Batch checkpoint at {i + 1} files - triggering restart")
                on_batch_complete()
                
            # Save state periodically
            if (i + 1) % 10 == 0:
                self._save_state()
                
        batch.status = JobStatus.COMPLETED
        self._save_state()
        
        return results
        
    def get_progress(self, batch_id: str) -> Dict[str, Any]:
        """Get progress of a batch."""
        batch = self.batches.get(batch_id)
        if not batch:
            return {"error": "Batch not found"}
            
        completed = sum(1 for j in batch.jobs if j.status == JobStatus.COMPLETED)
        failed = sum(1 for j in batch.jobs if j.status == JobStatus.FAILED)
        
        return {
            "batch_id": batch_id,
            "name": batch.name,
            "total": len(batch.jobs),
            "completed": completed,
            "failed": failed,
            "pending": len(batch.jobs) - completed - failed,
            "percent": round(completed / len(batch.jobs) * 100, 1),
            "status": batch.status.value
        }
        
    def get_resumable_batches(self) -> List[Dict[str, Any]]:
        """Get batches that can be resumed."""
        return [
            self.get_progress(b.id)
            for b in self.batches.values()
            if b.status == JobStatus.IN_PROGRESS
        ]
        
    def cancel_batch(self, batch_id: str) -> bool:
        """Cancel a batch and undo any pending checkouts."""
        batch = self.batches.get(batch_id)
        if not batch:
            return False
            
        batch.status = JobStatus.FAILED
        self._save_state()
        return True


# Singleton
_queue: Optional[JobQueue] = None

def get_job_queue() -> JobQueue:
    global _queue
    if _queue is None:
        _queue = JobQueue()
    return _queue
```

---

### 3. Performance Manager (CRITICAL)
**File**: `agents/cad_agent/adapters/performance_manager.py`  
**Lines**: ~400

```python
"""
CAD Performance Manager
Monitors system resources and auto-adjusts SolidWorks settings.

Features:
- RAM/GPU/CPU monitoring
- Dynamic graphics quality
- Auto-restart SW when memory high
- Lightweight mode management
"""

import logging
import time
import threading
from typing import Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum

try:
    import psutil
except ImportError:
    psutil = None

try:
    import GPUtil
except ImportError:
    GPUtil = None

logger = logging.getLogger("cad.performance-manager")


class PerformanceTier(Enum):
    """Graphics/performance tiers."""
    FULL = "full"           # All effects, high quality
    REDUCED = "reduced"     # No shadows, basic shading
    MINIMAL = "minimal"     # Wireframe, max performance
    SURVIVAL = "survival"   # Emergency mode


@dataclass
class SystemMetrics:
    """Current system resource usage."""
    ram_percent: float
    ram_available_gb: float
    cpu_percent: float
    gpu_percent: Optional[float]
    gpu_memory_percent: Optional[float]
    timestamp: float
    

@dataclass
class Thresholds:
    """Resource thresholds for tier switching."""
    ram_reduced: float = 60.0    # Switch to reduced at 60%
    ram_minimal: float = 75.0    # Switch to minimal at 75%
    ram_survival: float = 85.0   # Emergency at 85%
    ram_restart: float = 90.0    # Force restart at 90%
    gpu_reduced: float = 70.0
    gpu_minimal: float = 85.0
    cpu_high: float = 95.0


class PerformanceManager:
    """
    Monitors system and manages CAD performance.
    
    Usage:
        pm = PerformanceManager()
        pm.start_monitoring()
        
        # Check current state
        tier = pm.current_tier
        metrics = pm.get_metrics()
        
        # Set callbacks
        pm.on_tier_change = lambda old, new: print(f"Switched to {new}")
        pm.on_restart_needed = lambda: restart_solidworks()
    """
    
    def __init__(self, thresholds: Thresholds = None):
        self.thresholds = thresholds or Thresholds()
        self.current_tier = PerformanceTier.FULL
        self._metrics: Optional[SystemMetrics] = None
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Callbacks
        self.on_tier_change: Optional[Callable[[PerformanceTier, PerformanceTier], None]] = None
        self.on_restart_needed: Optional[Callable[[], None]] = None
        self.on_metrics_update: Optional[Callable[[SystemMetrics], None]] = None
        
    def get_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        ram = psutil.virtual_memory() if psutil else None
        cpu = psutil.cpu_percent() if psutil else 0
        
        gpu_percent = None
        gpu_mem_percent = None
        
        if GPUtil:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_percent = gpus[0].load * 100
                    gpu_mem_percent = gpus[0].memoryUtil * 100
            except:
                pass
                
        return SystemMetrics(
            ram_percent=ram.percent if ram else 0,
            ram_available_gb=ram.available / (1024**3) if ram else 0,
            cpu_percent=cpu,
            gpu_percent=gpu_percent,
            gpu_memory_percent=gpu_mem_percent,
            timestamp=time.time()
        )
        
    def evaluate_tier(self, metrics: SystemMetrics) -> PerformanceTier:
        """Determine appropriate tier based on metrics."""
        t = self.thresholds
        
        # Check RAM first (most critical)
        if metrics.ram_percent >= t.ram_survival:
            return PerformanceTier.SURVIVAL
        elif metrics.ram_percent >= t.ram_minimal:
            return PerformanceTier.MINIMAL
        elif metrics.ram_percent >= t.ram_reduced:
            return PerformanceTier.REDUCED
            
        # Check GPU if available
        if metrics.gpu_memory_percent:
            if metrics.gpu_memory_percent >= t.gpu_minimal:
                return PerformanceTier.MINIMAL
            elif metrics.gpu_memory_percent >= t.gpu_reduced:
                return PerformanceTier.REDUCED
                
        return PerformanceTier.FULL
        
    def check_restart_needed(self, metrics: SystemMetrics) -> bool:
        """Check if SW restart is needed to free memory."""
        return metrics.ram_percent >= self.thresholds.ram_restart
        
    def _monitor_loop(self, interval: float = 5.0):
        """Background monitoring loop."""
        while self._monitoring:
            try:
                metrics = self.get_metrics()
                self._metrics = metrics
                
                if self.on_metrics_update:
                    self.on_metrics_update(metrics)
                    
                # Evaluate tier
                new_tier = self.evaluate_tier(metrics)
                if new_tier != self.current_tier:
                    old_tier = self.current_tier
                    self.current_tier = new_tier
                    logger.warning(f"Performance tier: {old_tier.value} → {new_tier.value}")
                    
                    if self.on_tier_change:
                        self.on_tier_change(old_tier, new_tier)
                        
                # Check restart
                if self.check_restart_needed(metrics):
                    logger.critical(f"RAM at {metrics.ram_percent}% - restart needed!")
                    if self.on_restart_needed:
                        self.on_restart_needed()
                        
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                
            time.sleep(interval)
            
    def start_monitoring(self, interval: float = 5.0):
        """Start background monitoring."""
        if self._monitoring:
            return
            
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()
        logger.info("Performance monitoring started")
        
    def stop_monitoring(self):
        """Stop background monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
        logger.info("Performance monitoring stopped")
        
    def get_recommended_settings(self) -> Dict[str, any]:
        """Get recommended SW settings for current tier."""
        settings = {
            PerformanceTier.FULL: {
                "image_quality": 10,
                "antialiasing": True,
                "shadows": True,
                "realview": True,
                "ambient_occlusion": True,
                "lightweight_mode": False
            },
            PerformanceTier.REDUCED: {
                "image_quality": 5,
                "antialiasing": False,
                "shadows": False,
                "realview": True,
                "ambient_occlusion": False,
                "lightweight_mode": False
            },
            PerformanceTier.MINIMAL: {
                "image_quality": 1,
                "antialiasing": False,
                "shadows": False,
                "realview": False,
                "ambient_occlusion": False,
                "lightweight_mode": True
            },
            PerformanceTier.SURVIVAL: {
                "image_quality": 1,
                "antialiasing": False,
                "shadows": False,
                "realview": False,
                "ambient_occlusion": False,
                "lightweight_mode": True,
                "wireframe": True,
                "suppress_inactive": True
            }
        }
        
        return settings.get(self.current_tier, settings[PerformanceTier.FULL])


# Singleton
_pm: Optional[PerformanceManager] = None

def get_performance_manager() -> PerformanceManager:
    global _pm
    if _pm is None:
        _pm = PerformanceManager()
    return _pm
```

---

### 4. SolidWorks Settings Controller (CRITICAL)
**File**: `agents/cad_agent/adapters/solidworks_settings.py`  
**Lines**: ~200

```python
"""
SolidWorks Settings Controller
Applies performance settings to SolidWorks via COM API.
"""

import logging
from typing import Dict, Any, Optional
import pythoncom
import win32com.client

logger = logging.getLogger("cad.sw-settings")


class SolidWorksSettings:
    """
    Controls SolidWorks performance settings.
    
    Usage:
        sw_settings = SolidWorksSettings()
        sw_settings.connect()
        
        # Apply tier settings
        sw_settings.apply_settings({
            "image_quality": 5,
            "shadows": False,
            "lightweight_mode": True
        })
        
        # Or use presets
        sw_settings.apply_performance_tier("minimal")
    """
    
    # SolidWorks user preference constants
    SW_IMAGE_QUALITY = 1  # swImageQualityValue
    SW_ANTI_ALIAS = 2
    SW_SHADOWS = 3
    SW_REALVIEW = 4
    
    def __init__(self):
        self._app = None
        
    def connect(self) -> bool:
        """Connect to running SolidWorks instance."""
        try:
            pythoncom.CoInitialize()
            self._app = win32com.client.GetActiveObject("SldWorks.Application")
            logger.info("Connected to SolidWorks")
            return True
        except Exception as e:
            logger.error(f"Could not connect to SolidWorks: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from SolidWorks."""
        self._app = None
        pythoncom.CoUninitialize()
        
    def apply_settings(self, settings: Dict[str, Any]) -> bool:
        """Apply a dictionary of settings."""
        if not self._app:
            logger.error("Not connected to SolidWorks")
            return False
            
        try:
            # Image quality (1-10)
            if "image_quality" in settings:
                self._app.SetUserPreferenceIntegerValue(
                    self.SW_IMAGE_QUALITY,
                    settings["image_quality"]
                )
                
            # Anti-aliasing
            if "antialiasing" in settings:
                self._app.SetUserPreferenceToggle(
                    self.SW_ANTI_ALIAS,
                    settings["antialiasing"]
                )
                
            # Shadows
            if "shadows" in settings:
                self._app.SetUserPreferenceToggle(
                    self.SW_SHADOWS,
                    settings["shadows"]
                )
                
            # RealView
            if "realview" in settings:
                self._app.SetUserPreferenceToggle(
                    self.SW_REALVIEW,
                    settings["realview"]
                )
                
            logger.info(f"Applied settings: {settings}")
            return True
            
        except Exception as e:
            logger.error(f"Error applying settings: {e}")
            return False
            
    def set_lightweight_mode(self, enabled: bool) -> bool:
        """Enable/disable lightweight component loading."""
        if not self._app:
            return False
            
        try:
            doc = self._app.ActiveDoc
            if doc and doc.GetType() == 2:  # Assembly
                doc.SetLightweightComponents(enabled)
                logger.info(f"Lightweight mode: {enabled}")
            return True
        except Exception as e:
            logger.error(f"Error setting lightweight mode: {e}")
            return False
            
    def set_large_assembly_mode(self, enabled: bool) -> bool:
        """Enable/disable Large Assembly Mode."""
        if not self._app:
            return False
            
        try:
            # swUserPreferenceToggle_e.swLargeAssemblyMode
            self._app.SetUserPreferenceToggle(100, enabled)
            logger.info(f"Large Assembly Mode: {enabled}")
            return True
        except Exception as e:
            logger.error(f"Error setting large assembly mode: {e}")
            return False
            
    def suppress_components(self, component_names: list) -> int:
        """Suppress specified components in active assembly."""
        if not self._app:
            return 0
            
        try:
            doc = self._app.ActiveDoc
            if not doc or doc.GetType() != 2:
                return 0
                
            count = 0
            for comp in doc.GetComponents(False):
                if comp.Name in component_names:
                    comp.SetSuppression(0)  # Suppressed
                    count += 1
                    
            logger.info(f"Suppressed {count} components")
            return count
            
        except Exception as e:
            logger.error(f"Error suppressing components: {e}")
            return 0
            
    def restart_solidworks(self) -> bool:
        """Close and restart SolidWorks to free memory."""
        try:
            if self._app:
                # Close all documents
                self._app.CloseAllDocuments(True)
                
                # Quit
                self._app.ExitApp()
                self._app = None
                
            # Wait a moment
            import time
            time.sleep(3)
            
            # Start fresh instance
            pythoncom.CoInitialize()
            self._app = win32com.client.Dispatch("SldWorks.Application")
            self._app.Visible = True
            
            logger.info("SolidWorks restarted")
            return True
            
        except Exception as e:
            logger.error(f"Error restarting SolidWorks: {e}")
            return False


# Singleton
_sw_settings: Optional[SolidWorksSettings] = None

def get_solidworks_settings() -> SolidWorksSettings:
    global _sw_settings
    if _sw_settings is None:
        _sw_settings = SolidWorksSettings()
    return _sw_settings
```

---

### 5. Reference Tracker (IMPORTANT)
**File**: `agents/cad_agent/adapters/reference_tracker.py`  
**Lines**: ~150

```python
"""
Reference Tracker
Tracks where-used relationships and dependencies.
"""

import logging
from typing import List, Dict, Set
from dataclasses import dataclass

logger = logging.getLogger("cad.reference-tracker")


@dataclass
class ImpactReport:
    """Report of what will be affected by changes."""
    target_files: List[str]
    affected_assemblies: List[str]
    affected_drawings: List[str]
    total_impact: int
    

class ReferenceTracker:
    """
    Tracks file dependencies for impact analysis.
    
    Usage:
        tracker = ReferenceTracker(pdm_adapter)
        
        # Before making changes
        impact = tracker.analyze_impact(["part1.sldprt", "part2.sldprt"])
        print(f"This will affect {impact.total_impact} files")
    """
    
    def __init__(self, pdm_adapter):
        self.pdm = pdm_adapter
        
    def get_where_used(self, file_path: str) -> List[str]:
        """Get all files that reference this file."""
        return self.pdm.get_where_used(file_path)
        
    def analyze_impact(self, file_paths: List[str]) -> ImpactReport:
        """Analyze total impact of modifying files."""
        all_affected: Set[str] = set()
        assemblies: Set[str] = set()
        drawings: Set[str] = set()
        
        for path in file_paths:
            refs = self.get_where_used(path)
            for ref in refs:
                all_affected.add(ref)
                if ref.lower().endswith('.sldasm'):
                    assemblies.add(ref)
                elif ref.lower().endswith('.slddrw'):
                    drawings.add(ref)
                    
        return ImpactReport(
            target_files=file_paths,
            affected_assemblies=list(assemblies),
            affected_drawings=list(drawings),
            total_impact=len(all_affected)
        )
        
    def get_dependency_tree(self, file_path: str, depth: int = 3) -> Dict:
        """Get full dependency tree."""
        # Recursive where-used up to depth
        tree = {"file": file_path, "used_by": []}
        
        if depth > 0:
            refs = self.get_where_used(file_path)
            for ref in refs:
                tree["used_by"].append(
                    self.get_dependency_tree(ref, depth - 1)
                )
                
        return tree
```

---

### 6. Audit Logger (IMPORTANT)
**File**: `agents/cad_agent/adapters/audit_logger.py`  
**Lines**: ~150

```python
"""
Audit Logger
Detailed logging of all CAD operations for traceability.
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger("cad.audit")


@dataclass
class AuditEntry:
    """Single audit log entry."""
    timestamp: float
    action: str
    file_path: Optional[str]
    user: str
    details: Dict[str, Any]
    success: bool
    error: Optional[str] = None
    

class AuditLogger:
    """
    Logs all CAD operations for audit trail.
    
    Usage:
        audit = AuditLogger()
        
        audit.log_action(
            action="checkout",
            file_path="bracket.sldprt",
            details={"batch_id": "abc123"}
        )
    """
    
    def __init__(self, log_dir: str = None):
        self.log_dir = Path(log_dir or Path.home() / ".vulcan" / "audit")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.entries: List[AuditEntry] = []
        self.user = "VulcanBot"
        
    def log_action(
        self,
        action: str,
        file_path: str = None,
        details: Dict[str, Any] = None,
        success: bool = True,
        error: str = None
    ):
        """Log an action."""
        entry = AuditEntry(
            timestamp=time.time(),
            action=action,
            file_path=file_path,
            user=self.user,
            details=details or {},
            success=success,
            error=error
        )
        
        self.entries.append(entry)
        
        # Also log to Python logger
        msg = f"{action}: {file_path or 'N/A'}"
        if success:
            logger.info(msg)
        else:
            logger.error(f"{msg} - {error}")
            
    def save_session(self, session_id: str):
        """Save current session to file."""
        log_file = self.log_dir / f"{session_id}.json"
        
        with open(log_file, 'w') as f:
            json.dump(
                [asdict(e) for e in self.entries],
                f,
                indent=2
            )
            
        logger.info(f"Audit log saved: {log_file}")
        
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session."""
        return {
            "total_actions": len(self.entries),
            "successful": sum(1 for e in self.entries if e.success),
            "failed": sum(1 for e in self.entries if not e.success),
            "actions": list(set(e.action for e in self.entries))
        }


# Singleton
_audit: Optional[AuditLogger] = None

def get_audit_logger() -> AuditLogger:
    global _audit
    if _audit is None:
        _audit = AuditLogger()
    return _audit
```

---

### 7. Notification Store (IMPORTANT)
**File**: `agents/cad_agent/adapters/notification_store.py`  
**Lines**: ~100

```python
"""
Notification Store
Stores notifications for Web UI display.
"""

import time
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class NotificationType(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Notification:
    """Single notification."""
    id: str
    type: NotificationType
    title: str
    message: str
    timestamp: float
    read: bool = False
    batch_id: Optional[str] = None
    

class NotificationStore:
    """
    Stores notifications for Web UI.
    
    Usage:
        store = NotificationStore()
        
        store.add("Job started", "Processing 500 parts", NotificationType.INFO)
        
        # In Web UI
        notifications = store.get_unread()
    """
    
    def __init__(self):
        self.notifications: List[Notification] = []
        self._counter = 0
        
    def add(
        self,
        title: str,
        message: str,
        type: NotificationType = NotificationType.INFO,
        batch_id: str = None
    ) -> Notification:
        """Add a notification."""
        self._counter += 1
        
        notif = Notification(
            id=f"n-{self._counter}",
            type=type,
            title=title,
            message=message,
            timestamp=time.time(),
            batch_id=batch_id
        )
        
        self.notifications.append(notif)
        return notif
        
    def get_unread(self) -> List[Dict]:
        """Get all unread notifications."""
        return [
            asdict(n) for n in self.notifications
            if not n.read
        ]
        
    def get_all(self, limit: int = 50) -> List[Dict]:
        """Get recent notifications."""
        return [asdict(n) for n in self.notifications[-limit:]]
        
    def mark_read(self, notification_id: str):
        """Mark notification as read."""
        for n in self.notifications:
            if n.id == notification_id:
                n.read = True
                break
                
    def mark_all_read(self):
        """Mark all as read."""
        for n in self.notifications:
            n.read = True


# Singleton
_store: Optional[NotificationStore] = None

def get_notification_store() -> NotificationStore:
    global _store
    if _store is None:
        _store = NotificationStore()
    return _store
```

---

### 8. CAD Orchestrator (Ties It All Together)
**File**: `agents/cad_agent/adapters/cad_orchestrator.py`  
**Lines**: ~300

```python
"""
CAD Orchestrator
Coordinates all CAD operations: PDM, Jobs, Performance, Validation.
"""

import logging
from typing import List, Dict, Any, Optional

from .pdm_adapter import get_pdm_adapter, PDMAdapter
from .job_queue import get_job_queue, JobQueue, Job
from .performance_manager import get_performance_manager, PerformanceManager
from .solidworks_settings import get_solidworks_settings, SolidWorksSettings
from .reference_tracker import ReferenceTracker
from .audit_logger import get_audit_logger, AuditLogger
from .notification_store import get_notification_store, NotificationStore, NotificationType

logger = logging.getLogger("cad.orchestrator")


class CADOrchestrator:
    """
    Main coordinator for CAD batch operations.
    
    Usage:
        orch = CADOrchestrator(vault_name="MyVault")
        
        result = orch.run_batch_job(
            name="Update brackets",
            files=["part1.sldprt", "part2.sldprt"],
            operation="update_dimension",
            parameters={"dim": "D1@Sketch1", "value": 25.0}
        )
    """
    
    def __init__(self, vault_name: str):
        self.pdm: PDMAdapter = get_pdm_adapter(vault_name)
        self.queue: JobQueue = get_job_queue()
        self.perf: PerformanceManager = get_performance_manager()
        self.sw: SolidWorksSettings = get_solidworks_settings()
        self.audit: AuditLogger = get_audit_logger()
        self.notifications: NotificationStore = get_notification_store()
        self.ref_tracker: Optional[ReferenceTracker] = None
        
    def initialize(self) -> bool:
        """Initialize all connections."""
        # Connect to PDM
        if not self.pdm.connect():
            self.notifications.add(
                "Connection Failed",
                "Could not connect to PDM vault",
                NotificationType.ERROR
            )
            return False
            
        # Connect to SolidWorks
        if not self.sw.connect():
            self.notifications.add(
                "Connection Failed", 
                "Could not connect to SolidWorks",
                NotificationType.ERROR
            )
            return False
            
        # Start performance monitoring
        self.perf.start_monitoring()
        self.perf.on_tier_change = self._on_tier_change
        self.perf.on_restart_needed = self._on_restart_needed
        
        # Initialize reference tracker
        self.ref_tracker = ReferenceTracker(self.pdm)
        
        self.notifications.add(
            "System Ready",
            "CAD Orchestrator initialized",
            NotificationType.SUCCESS
        )
        
        return True
        
    def _on_tier_change(self, old_tier, new_tier):
        """Handle performance tier change."""
        settings = self.perf.get_recommended_settings()
        self.sw.apply_settings(settings)
        
        self.notifications.add(
            "Performance Adjusted",
            f"Switched from {old_tier.value} to {new_tier.value}",
            NotificationType.WARNING
        )
        
    def _on_restart_needed(self):
        """Handle restart needed."""
        self.notifications.add(
            "Restarting SolidWorks",
            "Memory usage critical - restarting to free resources",
            NotificationType.WARNING
        )
        self.sw.restart_solidworks()
        
    def run_batch_job(
        self,
        name: str,
        files: List[str],
        operation: str,
        parameters: Dict[str, Any],
        processor: callable
    ) -> Dict[str, Any]:
        """
        Run a complete batch job with PDM handling.
        
        Args:
            name: Job name for display
            files: List of file paths
            operation: Operation type
            parameters: Parameters for operation
            processor: Function to process each file
        """
        self.audit.log_action("batch_start", details={"name": name, "count": len(files)})
        
        # 1. Pre-flight: Check availability
        self.notifications.add(
            "Job Started",
            f"Checking availability of {len(files)} files...",
            NotificationType.INFO
        )
        
        availability = self.pdm.get_availability(files)
        available = availability["available"]
        
        if not available:
            self.notifications.add(
                "No Files Available",
                f"0 files available. {len(availability['checked_out_by_others'])} locked by others.",
                NotificationType.ERROR
            )
            return {"error": "No files available"}
            
        # 2. Impact analysis
        impact = self.ref_tracker.analyze_impact(available)
        self.audit.log_action("impact_analysis", details={
            "assemblies_affected": len(impact.affected_assemblies),
            "drawings_affected": len(impact.affected_drawings)
        })
        
        # 3. Get latest & checkout
        self.pdm.get_latest(available)
        checkout_results = self.pdm.batch_checkout(available)
        checked_out = [f for f, success in checkout_results.items() if success]
        
        self.notifications.add(
            "Files Checked Out",
            f"Checked out {len(checked_out)} files",
            NotificationType.INFO
        )
        
        # 4. Create and process batch
        batch = self.queue.create_batch(
            name=name,
            files=checked_out,
            operation=operation,
            parameters=parameters
        )
        
        def on_progress(current, total):
            if current % 10 == 0:
                self.notifications.add(
                    "Progress",
                    f"Processed {current}/{total} files",
                    NotificationType.INFO,
                    batch_id=batch.id
                )
                
        def on_batch_checkpoint():
            # Restart SW every batch_size files
            self.sw.restart_solidworks()
            self.sw.connect()
            
        results = self.queue.process_batch(
            batch.id,
            processor=processor,
            on_progress=on_progress,
            on_batch_complete=on_batch_checkpoint
        )
        
        # 5. Check in all files
        self.pdm.batch_checkin(
            checked_out,
            comment=f"Vulcan Bot: {name}"
        )
        
        self.notifications.add(
            "Files Checked In",
            f"Checked in {len(checked_out)} files",
            NotificationType.SUCCESS
        )
        
        # 6. Trigger validation (Inspector Agent)
        # This would call your inspector agent
        # inspector.validate_files(checked_out)
        
        self.notifications.add(
            "Job Complete",
            f"Completed: {results['completed']} success, {results['failed']} failed",
            NotificationType.SUCCESS,
            batch_id=batch.id
        )
        
        # Save audit log
        self.audit.save_session(batch.id)
        
        return {
            "batch_id": batch.id,
            "results": results,
            "impact": {
                "assemblies": len(impact.affected_assemblies),
                "drawings": len(impact.affected_drawings)
            }
        }
        
    def shutdown(self):
        """Clean shutdown."""
        self.perf.stop_monitoring()
        self.pdm.disconnect()
        self.sw.disconnect()


# Singleton
_orchestrator: Optional[CADOrchestrator] = None

def get_cad_orchestrator(vault_name: str = None) -> CADOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        vault = vault_name or "DefaultVault"
        _orchestrator = CADOrchestrator(vault)
    return _orchestrator
```

---

## 📋 REQUIREMENTS UPDATE

Add to `requirements.txt`:
```
GPUtil==1.4.0  # GPU monitoring
```

---

## ✅ ACCEPTANCE CRITERIA

1. **PDM Integration**
   - [ ] Can check file availability
   - [ ] Can batch checkout/checkin
   - [ ] Handles locked files gracefully
   - [ ] Tracks versions via PDM

2. **Job Queue**
   - [ ] Creates batch jobs
   - [ ] Resumes interrupted jobs
   - [ ] Tracks progress
   - [ ] Restarts SW every N files

3. **Performance Manager**
   - [ ] Monitors RAM/GPU/CPU
   - [ ] Auto-adjusts SW settings
   - [ ] Triggers restart when critical
   - [ ] Background monitoring thread

4. **Notifications**
   - [ ] Stores notifications for Web UI
   - [ ] Shows progress updates
   - [ ] Shows errors/warnings
   - [ ] Marks as read

5. **Audit Trail**
   - [ ] Logs all actions
   - [ ] Saves to file
   - [ ] Includes timestamps and details

---

### 9. Flatter Files Adapter (NEW)
**File**: `agents/cad_agent/adapters/flatter_files_adapter.py`  
**Lines**: ~350

**SEE**: `NEXT_TASK_FLATTER_FILES.md` for full implementation

Capabilities:
- Search drawings by part number/description
- Get PDF/STEP/DXF download URLs
- Get assembly BOM structure
- Get revision history
- Get markup annotations
- Check uploader status

---

## 📋 REQUIREMENTS UPDATE

Add to `requirements.txt`:
```
GPUtil==1.4.0  # GPU monitoring
requests>=2.28.0  # For Flatter Files API
```

---

## 📋 ENVIRONMENT VARIABLES

Add to `.env`:
```
FLATTER_FILES_API_KEY=your-api-key-here
```

---

## ✅ ACCEPTANCE CRITERIA

1. **PDM Integration**
   - [ ] Can check file availability
   - [ ] Can batch checkout/checkin
   - [ ] Handles locked files gracefully
   - [ ] Tracks versions via PDM

2. **Job Queue**
   - [ ] Creates batch jobs
   - [ ] Resumes interrupted jobs
   - [ ] Tracks progress
   - [ ] Restarts SW every N files

3. **Performance Manager**
   - [ ] Monitors RAM/GPU/CPU
   - [ ] Auto-adjusts SW settings
   - [ ] Triggers restart when critical
   - [ ] Background monitoring thread

4. **Notifications**
   - [ ] Stores notifications for Web UI
   - [ ] Shows progress updates
   - [ ] Shows errors/warnings
   - [ ] Marks as read

5. **Audit Trail**
   - [ ] Logs all actions
   - [ ] Saves to file
   - [ ] Includes timestamps and details

6. **Flatter Files Integration (NEW)**
   - [ ] Search drawings by part number
   - [ ] Get PDF/STEP/DXF URLs
   - [ ] Get assembly BOM
   - [ ] Get revision history
   - [ ] Get markups

---

## 🗑️ DELETE THIS FILE AFTER COMPLETING

---
