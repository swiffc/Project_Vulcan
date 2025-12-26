"""
SolidWorks COM Bridge - Thread-Safe Connection Manager
======================================================
Provides thread-safe access to SolidWorks COM API with:
- Connection pooling for concurrent requests
- Early-binding type generation
- Automatic reconnection on failure
- Version detection and compatibility

This bridges the C++ SolidWorks API to Python via COM automation.
"""

import threading
import queue
import logging
from typing import Optional, Dict, Any, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from contextlib import contextmanager
from functools import wraps
from enum import Enum
import time

logger = logging.getLogger(__name__)

# COM imports
try:
    import win32com.client
    import pythoncom
    from win32com.client import gencache, constants
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False
    logger.warning("win32com not available - COM bridge disabled")


class SolidWorksVersion(Enum):
    """SolidWorks version identifiers."""
    SW2020 = 28
    SW2021 = 29
    SW2022 = 30
    SW2023 = 31
    SW2024 = 32
    SW2025 = 33
    UNKNOWN = 0


class DocumentType(Enum):
    """SolidWorks document types."""
    PART = 1
    ASSEMBLY = 2
    DRAWING = 3
    UNKNOWN = 0


@dataclass
class SolidWorksConnection:
    """Represents a single COM connection to SolidWorks."""
    app: Any = None
    thread_id: int = 0
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    version: SolidWorksVersion = SolidWorksVersion.UNKNOWN
    is_valid: bool = False

    def touch(self):
        """Update last used timestamp."""
        self.last_used = time.time()


class COMContext:
    """Context manager for thread-safe COM operations."""

    def __init__(self):
        self._initialized = False

    def __enter__(self):
        if COM_AVAILABLE:
            pythoncom.CoInitialize()
            self._initialized = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._initialized:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass
        return False


class SolidWorksBridge:
    """
    Thread-safe bridge to SolidWorks COM API.

    Features:
    - Per-thread COM initialization
    - Connection pooling with automatic cleanup
    - Retry logic for transient failures
    - Version detection and compatibility checks

    Usage:
        bridge = SolidWorksBridge()
        with bridge.connect() as sw:
            model = sw.ActiveDoc
            # ... use SolidWorks API
    """

    _instance: Optional['SolidWorksBridge'] = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern for bridge instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._connections: Dict[int, SolidWorksConnection] = {}
        self._connection_lock = threading.Lock()
        self._max_retries = 3
        self._retry_delay = 0.5
        self._connection_timeout = 300  # 5 minutes
        self._initialized = True

        logger.info("SolidWorks Bridge initialized")

    @contextmanager
    def connect(self):
        """
        Get a thread-safe connection to SolidWorks.

        Usage:
            with bridge.connect() as sw:
                model = sw.ActiveDoc
        """
        if not COM_AVAILABLE:
            raise RuntimeError("COM not available - win32com not installed")

        thread_id = threading.current_thread().ident
        conn = None

        try:
            # Initialize COM for this thread
            pythoncom.CoInitialize()

            # Get or create connection for this thread
            conn = self._get_or_create_connection(thread_id)

            if not conn.is_valid:
                raise RuntimeError("Failed to establish SolidWorks connection")

            conn.touch()
            yield conn.app

        finally:
            # Uninitialize COM for this thread
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass

    def _get_or_create_connection(self, thread_id: int) -> SolidWorksConnection:
        """Get existing or create new connection for thread."""
        with self._connection_lock:
            # Check for existing valid connection
            if thread_id in self._connections:
                conn = self._connections[thread_id]
                if self._validate_connection(conn):
                    return conn
                else:
                    # Remove invalid connection
                    del self._connections[thread_id]

            # Create new connection
            conn = self._create_connection(thread_id)
            if conn.is_valid:
                self._connections[thread_id] = conn

            return conn

    def _create_connection(self, thread_id: int) -> SolidWorksConnection:
        """Create a new SolidWorks COM connection."""
        conn = SolidWorksConnection(thread_id=thread_id)

        for attempt in range(self._max_retries):
            try:
                # Try to connect to running instance first
                try:
                    conn.app = win32com.client.GetActiveObject("SldWorks.Application")
                    logger.info(f"Connected to running SolidWorks instance (thread {thread_id})")
                except Exception:
                    # Launch new instance
                    conn.app = win32com.client.Dispatch("SldWorks.Application")
                    conn.app.Visible = True
                    logger.info(f"Launched new SolidWorks instance (thread {thread_id})")

                # Detect version
                conn.version = self._detect_version(conn.app)
                conn.is_valid = True
                return conn

            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self._max_retries - 1:
                    time.sleep(self._retry_delay)

        logger.error(f"Failed to create SolidWorks connection after {self._max_retries} attempts")
        return conn

    def _validate_connection(self, conn: SolidWorksConnection) -> bool:
        """Check if connection is still valid."""
        if not conn.is_valid or conn.app is None:
            return False

        # Check age
        age = time.time() - conn.last_used
        if age > self._connection_timeout:
            logger.info(f"Connection timed out (age: {age:.0f}s)")
            return False

        # Try to access app
        try:
            _ = conn.app.Visible
            return True
        except Exception:
            logger.warning("Connection validation failed - app not responding")
            return False

    def _detect_version(self, app) -> SolidWorksVersion:
        """Detect SolidWorks version from app object."""
        try:
            rev = app.RevisionNumber()
            major = int(str(rev).split('.')[0])
            for ver in SolidWorksVersion:
                if ver.value == major:
                    return ver
        except Exception:
            pass
        return SolidWorksVersion.UNKNOWN

    def get_active_document(self) -> Optional[Dict[str, Any]]:
        """Get info about active document."""
        with self.connect() as sw:
            doc = sw.ActiveDoc
            if not doc:
                return None

            doc_type = DocumentType.UNKNOWN
            try:
                type_val = doc.GetType()
                doc_type = DocumentType(type_val)
            except Exception:
                pass

            return {
                "name": doc.GetTitle() if hasattr(doc, 'GetTitle') else "Unknown",
                "path": doc.GetPathName() if hasattr(doc, 'GetPathName') else "",
                "type": doc_type.name,
                "saved": doc.GetSaveFlag() if hasattr(doc, 'GetSaveFlag') else False,
            }

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with SolidWorks connection.

        Args:
            func: Function that takes sw_app as first argument
            *args, **kwargs: Additional arguments for func

        Usage:
            def my_operation(sw, param1, param2):
                model = sw.ActiveDoc
                # ... do work
                return result

            result = bridge.execute(my_operation, "value1", param2="value2")
        """
        with self.connect() as sw:
            return func(sw, *args, **kwargs)

    def cleanup(self):
        """Clean up old connections."""
        with self._connection_lock:
            current_time = time.time()
            expired = [
                tid for tid, conn in self._connections.items()
                if current_time - conn.last_used > self._connection_timeout
            ]
            for tid in expired:
                logger.info(f"Cleaning up expired connection for thread {tid}")
                del self._connections[tid]

    @property
    def status(self) -> Dict[str, Any]:
        """Get bridge status."""
        with self._connection_lock:
            return {
                "com_available": COM_AVAILABLE,
                "active_connections": len(self._connections),
                "connections": [
                    {
                        "thread_id": conn.thread_id,
                        "version": conn.version.name,
                        "age_seconds": time.time() - conn.created_at,
                        "idle_seconds": time.time() - conn.last_used,
                        "is_valid": conn.is_valid,
                    }
                    for conn in self._connections.values()
                ]
            }


# Thread-safe decorator for COM operations
def com_operation(func):
    """
    Decorator for thread-safe COM operations.

    Usage:
        @com_operation
        def my_function(sw_app, param1, param2):
            # sw_app is automatically injected
            return sw_app.ActiveDoc.GetTitle()
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        bridge = get_bridge()
        return bridge.execute(func, *args, **kwargs)
    return wrapper


# Singleton accessor
_bridge_instance: Optional[SolidWorksBridge] = None
_bridge_lock = threading.Lock()


def get_bridge() -> SolidWorksBridge:
    """Get or create the SolidWorks bridge singleton."""
    global _bridge_instance
    if _bridge_instance is None:
        with _bridge_lock:
            if _bridge_instance is None:
                _bridge_instance = SolidWorksBridge()
    return _bridge_instance


# =============================================================================
# High-Level API Wrappers
# =============================================================================

class ModelOperations:
    """High-level model operations using the bridge."""

    def __init__(self, bridge: Optional[SolidWorksBridge] = None):
        self.bridge = bridge or get_bridge()

    def get_mass_properties(self) -> Optional[Dict[str, float]]:
        """Get mass properties of active document."""
        def _get_mass(sw):
            doc = sw.ActiveDoc
            if not doc:
                return None

            ext = doc.Extension
            if not ext:
                return None

            props = ext.CreateMassProperty()
            if not props:
                return None

            return {
                "mass_kg": props.Mass,
                "volume_m3": props.Volume,
                "surface_area_m2": props.SurfaceArea,
                "center_of_mass": list(props.CenterOfMass) if props.CenterOfMass else None,
            }

        return self.bridge.execute(_get_mass)

    def get_custom_properties(self, config: str = "") -> Dict[str, str]:
        """Get custom properties from active document."""
        def _get_props(sw, config_name):
            doc = sw.ActiveDoc
            if not doc:
                return {}

            mgr = doc.Extension.CustomPropertyManager[config_name]
            if not mgr:
                return {}

            props = {}
            names = mgr.GetNames()
            if names:
                for name in names:
                    try:
                        val_out = ""
                        resolved = ""
                        was_resolved = False
                        ret = mgr.Get5(name, False, val_out, resolved, was_resolved)
                        props[name] = resolved if resolved else val_out
                    except Exception:
                        pass

            return props

        return self.bridge.execute(_get_props, config)

    def set_custom_property(self, name: str, value: str, config: str = "") -> bool:
        """Set a custom property on active document."""
        def _set_prop(sw, prop_name, prop_value, config_name):
            doc = sw.ActiveDoc
            if not doc:
                return False

            mgr = doc.Extension.CustomPropertyManager[config_name]
            if not mgr:
                return False

            # Try to add (returns error if exists)
            ret = mgr.Add3(prop_name, 30, prop_value, 2)  # 30 = text, 2 = overwrite
            if ret != 0:
                # Try to set existing
                ret = mgr.Set2(prop_name, prop_value)

            return ret == 0

        return self.bridge.execute(_set_prop, name, value, config)


class SketchOperations:
    """High-level sketch operations using the bridge."""

    def __init__(self, bridge: Optional[SolidWorksBridge] = None):
        self.bridge = bridge or get_bridge()

    def create_sketch_on_plane(self, plane: str = "Front") -> bool:
        """Create a new sketch on specified plane."""
        def _create_sketch(sw, plane_name):
            doc = sw.ActiveDoc
            if not doc:
                return False

            # Select plane
            plane_map = {
                "Front": "Front Plane",
                "Top": "Top Plane",
                "Right": "Right Plane",
            }
            plane_feature = plane_map.get(plane_name, plane_name)

            doc.Extension.SelectByID2(plane_feature, "PLANE", 0, 0, 0, False, 0, None, 0)
            doc.SketchManager.InsertSketch(True)

            return True

        return self.bridge.execute(_create_sketch, plane)

    def draw_rectangle(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        """Draw a rectangle in active sketch."""
        def _draw_rect(sw, x1, y1, x2, y2):
            doc = sw.ActiveDoc
            if not doc:
                return False

            sm = doc.SketchManager
            # Corner rectangle (type 0)
            rect = sm.CreateCornerRectangle(x1, y1, 0, x2, y2, 0)
            return rect is not None

        return self.bridge.execute(_draw_rect, x1, y1, x2, y2)

    def draw_circle(self, cx: float, cy: float, radius: float) -> bool:
        """Draw a circle in active sketch."""
        def _draw_circle(sw, cx, cy, r):
            doc = sw.ActiveDoc
            if not doc:
                return False

            sm = doc.SketchManager
            circle = sm.CreateCircle(cx, cy, 0, cx + r, cy, 0)
            return circle is not None

        return self.bridge.execute(_draw_circle, cx, cy, radius)


class FeatureOperations:
    """High-level feature operations using the bridge."""

    def __init__(self, bridge: Optional[SolidWorksBridge] = None):
        self.bridge = bridge or get_bridge()

    def extrude(self, depth: float, direction: int = 1) -> bool:
        """Extrude active sketch."""
        def _extrude(sw, depth, direction):
            doc = sw.ActiveDoc
            if not doc:
                return False

            fm = doc.FeatureManager

            # End condition: Blind = 0
            # Direction: 1 = one direction, 2 = both directions
            feature = fm.FeatureExtrusion3(
                True,           # Single direction
                False,          # Flip
                direction == 2, # Both directions
                0,              # End type 1 (Blind)
                0,              # End type 2 (Blind)
                depth,          # Depth 1
                depth if direction == 2 else 0,  # Depth 2
                False, False,   # Draft
                False, False,   # Draft outward
                0, 0,           # Draft angles
                False, False,   # Offset
                False, False,   # Translate
                0, 0,           # Offset distances
                False,          # Thin feature
                0, 0,           # Thin walls
                False,          # Cap end
                False,          # Merge
                True,           # Normal cut
                False,          # Flip cut direction
                False           # Optimize
            )
            return feature is not None

        return self.bridge.execute(_extrude, depth, direction)

    def fillet(self, radius: float) -> bool:
        """Apply fillet to selected edges."""
        def _fillet(sw, radius):
            doc = sw.ActiveDoc
            if not doc:
                return False

            fm = doc.FeatureManager
            feature = fm.FeatureFillet3(
                195,    # Options
                radius, # Radius
                0,      # Fillet type
                0,      # Overflow
                0, 0,   # Radius type
                0, 0,   # Point settings
                0, 0,   # Tangent settings
                False, False, False,  # Flags
                False, False, False,  # More flags
                False, False          # Even more flags
            )
            return feature is not None

        return self.bridge.execute(_fillet, radius)


# =============================================================================
# Export for external use
# =============================================================================

__all__ = [
    "SolidWorksBridge",
    "get_bridge",
    "com_operation",
    "COMContext",
    "SolidWorksVersion",
    "DocumentType",
    "ModelOperations",
    "SketchOperations",
    "FeatureOperations",
    "COM_AVAILABLE",
]
