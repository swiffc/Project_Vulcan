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

try:
    from .document_exporter import router as document_exporter_router
    DOCUMENT_EXPORTER_AVAILABLE = True
except ImportError:
    document_exporter_router = None
    DOCUMENT_EXPORTER_AVAILABLE = False

try:
    from .bom_manager import router as bom_router
    BOM_AVAILABLE = True
except ImportError:
    bom_router = None
    BOM_AVAILABLE = False

try:
    from .solidworks_batch import router as solidworks_batch_router
    SOLIDWORKS_BATCH_AVAILABLE = True
except ImportError:
    solidworks_batch_router = None
    SOLIDWORKS_BATCH_AVAILABLE = False

try:
    from .solidworks_advanced import router as solidworks_advanced_router
    SOLIDWORKS_ADVANCED_AVAILABLE = True
except ImportError:
    solidworks_advanced_router = None
    SOLIDWORKS_ADVANCED_AVAILABLE = False

try:
    from .solidworks_simulation import router as solidworks_simulation_router
    SOLIDWORKS_SIMULATION_AVAILABLE = True
except ImportError:
    solidworks_simulation_router = None
    SOLIDWORKS_SIMULATION_AVAILABLE = False

try:
    from .solidworks_pdm import router as solidworks_pdm_router
    SOLIDWORKS_PDM_AVAILABLE = True
except ImportError:
    solidworks_pdm_router = None
    SOLIDWORKS_PDM_AVAILABLE = False

try:
    from .solidworks_constraints import router as solidworks_constraints_router
    SOLIDWORKS_CONSTRAINTS_AVAILABLE = True
except ImportError:
    solidworks_constraints_router = None
    SOLIDWORKS_CONSTRAINTS_AVAILABLE = False

try:
    from .solidworks_tolerances import router as solidworks_tolerances_router
    SOLIDWORKS_TOLERANCES_AVAILABLE = True
except ImportError:
    solidworks_tolerances_router = None
    SOLIDWORKS_TOLERANCES_AVAILABLE = False

try:
    from .solidworks_threads import router as solidworks_threads_router
    SOLIDWORKS_THREADS_AVAILABLE = True
except ImportError:
    solidworks_threads_router = None
    SOLIDWORKS_THREADS_AVAILABLE = False

try:
    from .solidworks_motion import router as solidworks_motion_router
    SOLIDWORKS_MOTION_AVAILABLE = True
except ImportError:
    solidworks_motion_router = None
    SOLIDWORKS_MOTION_AVAILABLE = False

try:
    from .solidworks_optimization import router as solidworks_optimization_router
    SOLIDWORKS_OPTIMIZATION_AVAILABLE = True
except ImportError:
    solidworks_optimization_router = None
    SOLIDWORKS_OPTIMIZATION_AVAILABLE = False

try:
    from .solidworks_surfaces import router as solidworks_surfaces_router
    SOLIDWORKS_SURFACES_AVAILABLE = True
except ImportError:
    solidworks_surfaces_router = None
    SOLIDWORKS_SURFACES_AVAILABLE = False

try:
    from .solidworks_equations import router as solidworks_equations_router
    SOLIDWORKS_EQUATIONS_AVAILABLE = True
except ImportError:
    solidworks_equations_router = None
    SOLIDWORKS_EQUATIONS_AVAILABLE = False

try:
    from .solidworks_display import router as solidworks_display_router
    SOLIDWORKS_DISPLAY_AVAILABLE = True
except ImportError:
    solidworks_display_router = None
    SOLIDWORKS_DISPLAY_AVAILABLE = False

try:
    from .solidworks_materials import router as solidworks_materials_router
    SOLIDWORKS_MATERIALS_AVAILABLE = True
except ImportError:
    solidworks_materials_router = None
    SOLIDWORKS_MATERIALS_AVAILABLE = False

try:
    from .solidworks_bodies import router as solidworks_bodies_router
    SOLIDWORKS_BODIES_AVAILABLE = True
except ImportError:
    solidworks_bodies_router = None
    SOLIDWORKS_BODIES_AVAILABLE = False

try:
    from .solidworks_rendering import router as solidworks_rendering_router
    SOLIDWORKS_RENDERING_AVAILABLE = True
except ImportError:
    solidworks_rendering_router = None
    SOLIDWORKS_RENDERING_AVAILABLE = False

try:
    from .solidworks_sensors import router as solidworks_sensors_router
    SOLIDWORKS_SENSORS_AVAILABLE = True
except ImportError:
    solidworks_sensors_router = None
    SOLIDWORKS_SENSORS_AVAILABLE = False

try:
    from .solidworks_macros import router as solidworks_macros_router
    SOLIDWORKS_MACROS_AVAILABLE = True
except ImportError:
    solidworks_macros_router = None
    SOLIDWORKS_MACROS_AVAILABLE = False

try:
    from .solidworks_design_tables import router as solidworks_design_tables_router
    SOLIDWORKS_DESIGN_TABLES_AVAILABLE = True
except ImportError:
    solidworks_design_tables_router = None
    SOLIDWORKS_DESIGN_TABLES_AVAILABLE = False

try:
    from .solidworks_pack_and_go import router as solidworks_pack_and_go_router
    SOLIDWORKS_PACK_AND_GO_AVAILABLE = True
except ImportError:
    solidworks_pack_and_go_router = None
    SOLIDWORKS_PACK_AND_GO_AVAILABLE = False

try:
    from .solidworks_reference_geometry import router as solidworks_reference_geometry_router
    SOLIDWORKS_REFERENCE_GEOMETRY_AVAILABLE = True
except ImportError:
    solidworks_reference_geometry_router = None
    SOLIDWORKS_REFERENCE_GEOMETRY_AVAILABLE = False

__all__ = [
    "solidworks_router",
    "solidworks_advanced_router",
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
    "document_exporter_router",
    "bom_router",
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
    "DOCUMENT_EXPORTER_AVAILABLE",
    "BOM_AVAILABLE",
    "solidworks_batch_router",
    "SOLIDWORKS_BATCH_AVAILABLE",
    "solidworks_advanced_router",
    "SOLIDWORKS_ADVANCED_AVAILABLE",
    "solidworks_simulation_router",
    "SOLIDWORKS_SIMULATION_AVAILABLE",
    "solidworks_pdm_router",
    "SOLIDWORKS_PDM_AVAILABLE",
    "solidworks_constraints_router",
    "SOLIDWORKS_CONSTRAINTS_AVAILABLE",
    "solidworks_tolerances_router",
    "SOLIDWORKS_TOLERANCES_AVAILABLE",
    "solidworks_threads_router",
    "SOLIDWORKS_THREADS_AVAILABLE",
    "solidworks_motion_router",
    "SOLIDWORKS_MOTION_AVAILABLE",
    "solidworks_optimization_router",
    "SOLIDWORKS_OPTIMIZATION_AVAILABLE",
    "solidworks_surfaces_router",
    "SOLIDWORKS_SURFACES_AVAILABLE",
]
