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

try:
    from .solidworks_drawings import router as solidworks_drawings_router
    SOLIDWORKS_DRAWINGS_AVAILABLE = True
except ImportError:
    solidworks_drawings_router = None
    SOLIDWORKS_DRAWINGS_AVAILABLE = False

try:
    from .inventor_drawings import router as inventor_drawings_router
    INVENTOR_DRAWINGS_AVAILABLE = True
except ImportError:
    inventor_drawings_router = None
    INVENTOR_DRAWINGS_AVAILABLE = False

try:
    from .assembly_analyzer import router as assembly_analyzer_router
    ASSEMBLY_ANALYZER_AVAILABLE = True
except ImportError:
    assembly_analyzer_router = None
    ASSEMBLY_ANALYZER_AVAILABLE = False

try:
    from .feature_reader import router as feature_reader_router
    FEATURE_READER_AVAILABLE = True
except ImportError:
    feature_reader_router = None
    FEATURE_READER_AVAILABLE = False

try:
    from .inventor_feature_reader import router as inventor_feature_reader_router
    INVENTOR_FEATURE_READER_AVAILABLE = True
except ImportError:
    inventor_feature_reader_router = None
    INVENTOR_FEATURE_READER_AVAILABLE = False

try:
    from .assembly_component_analyzer import router as assembly_component_analyzer_router
    ASSEMBLY_COMPONENT_ANALYZER_AVAILABLE = True
except ImportError:
    assembly_component_analyzer_router = None
    ASSEMBLY_COMPONENT_ANALYZER_AVAILABLE = False

try:
    from .configuration_manager import router as configuration_router
    CONFIGURATION_AVAILABLE = True
except ImportError:
    configuration_router = None
    CONFIGURATION_AVAILABLE = False

try:
    from .measurement_tools import router as measurement_router
    MEASUREMENT_AVAILABLE = True
except ImportError:
    measurement_router = None
    MEASUREMENT_AVAILABLE = False

try:
    from .properties_reader import router as properties_router
    PROPERTIES_AVAILABLE = True
except ImportError:
    properties_router = None
    PROPERTIES_AVAILABLE = False

__all__ = [
    "solidworks_router",
    "solidworks_assembly_router",
    "inventor_router",
    "inventor_imates_router",
    "solidworks_mate_refs_router",
    "solidworks_drawings_router",
    "inventor_drawings_router",
    "assembly_analyzer_router",
    "feature_reader_router",
    "inventor_feature_reader_router",
    "assembly_component_analyzer_router",
    "configuration_router",
    "measurement_router",
    "properties_router",
    "SOLIDWORKS_AVAILABLE",
    "SOLIDWORKS_ASSEMBLY_AVAILABLE",
    "INVENTOR_AVAILABLE",
    "INVENTOR_IMATES_AVAILABLE",
    "SOLIDWORKS_MATE_REFS_AVAILABLE",
    "SOLIDWORKS_DRAWINGS_AVAILABLE",
    "INVENTOR_DRAWINGS_AVAILABLE",
    "ASSEMBLY_ANALYZER_AVAILABLE",
    "FEATURE_READER_AVAILABLE",
    "INVENTOR_FEATURE_READER_AVAILABLE",
    "ASSEMBLY_COMPONENT_ANALYZER_AVAILABLE",
    "CONFIGURATION_AVAILABLE",
    "MEASUREMENT_AVAILABLE",
    "PROPERTIES_AVAILABLE",
]
