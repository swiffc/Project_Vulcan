"""
COM Adapters for CAD Applications.
Provides FastAPI routers for SolidWorks and Inventor automation.
"""

try:
    from .solidworks_com import router as solidworks_router
    SOLIDWORKS_AVAILABLE = True
except ImportError:
    solidworks_router = None
    SOLIDWORKS_AVAILABLE = False

try:
    from .solidworks_assembly import router as solidworks_assembly_router
    SOLIDWORKS_ASSEMBLY_AVAILABLE = True
except ImportError:
    solidworks_assembly_router = None
    SOLIDWORKS_ASSEMBLY_AVAILABLE = False

try:
    from .inventor_com import router as inventor_router
    INVENTOR_AVAILABLE = True
except ImportError:
    inventor_router = None
    INVENTOR_AVAILABLE = False

try:
    from .inventor_imates import router as inventor_imates_router
    INVENTOR_IMATES_AVAILABLE = True
except ImportError:
    inventor_imates_router = None
    INVENTOR_IMATES_AVAILABLE = False

try:
    from .solidworks_mate_references import router as solidworks_mate_refs_router
    SOLIDWORKS_MATE_REFS_AVAILABLE = True
except ImportError:
    solidworks_mate_refs_router = None
    SOLIDWORKS_MATE_REFS_AVAILABLE = False

__all__ = [
    "solidworks_router",
    "solidworks_assembly_router",
    "inventor_router",
    "inventor_imates_router",
    "solidworks_mate_refs_router",
    "SOLIDWORKS_AVAILABLE",
    "SOLIDWORKS_ASSEMBLY_AVAILABLE",
    "INVENTOR_AVAILABLE",
    "INVENTOR_IMATES_AVAILABLE",
    "SOLIDWORKS_MATE_REFS_AVAILABLE",
]
