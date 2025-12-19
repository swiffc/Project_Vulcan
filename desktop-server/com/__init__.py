# CAD COM Automation Adapters
from .solidworks_com import router as solidworks_router
from .inventor_com import router as inventor_router

__all__ = ['solidworks_router', 'inventor_router']
