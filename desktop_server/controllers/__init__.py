# Desktop Control Server Controllers
from .mouse import router as mouse_router
from .keyboard import router as keyboard_router
from .screen import router as screen_router
from .window import router as window_router

# TradingView browser controller (requires Playwright)
try:
    from .tradingview import router as tradingview_router

    TRADINGVIEW_AVAILABLE = True
except ImportError:
    TRADINGVIEW_AVAILABLE = False
    tradingview_router = None

# Browser automation controller (requires Playwright)
try:
    from .browser import router as browser_router

    BROWSER_AVAILABLE = True
except ImportError:
    BROWSER_AVAILABLE = False
    browser_router = None

# J2 Tracker controller (requires browser controller)
try:
    from .j2_tracker import router as j2_tracker_router

    J2_AVAILABLE = True
except ImportError:
    J2_AVAILABLE = False
    j2_tracker_router = None

# Memory/RAG controller
try:
    from .memory import router as memory_router

    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    memory_router = None

# CAD Validation controller
try:
    from .cad_validation import router as cad_validation_router

    CAD_VALIDATION_AVAILABLE = True
except ImportError:
    CAD_VALIDATION_AVAILABLE = False
    cad_validation_router = None

from .recorder import router as recorder_router
from .verifier import router as verifier_router

# Events controller
try:
    from .events_controller import router as events_router

    EVENTS_AVAILABLE = True
except ImportError:
    EVENTS_AVAILABLE = False
    events_router = None

__all__ = [
    "mouse_router",
    "keyboard_router",
    "screen_router",
    "window_router",
    "tradingview_router",
    "TRADINGVIEW_AVAILABLE",
    "browser_router",
    "BROWSER_AVAILABLE",
    "j2_tracker_router",
    "J2_AVAILABLE",
    "events_router",
    "EVENTS_AVAILABLE",
    "memory_router",
    "MEMORY_AVAILABLE",
    "cad_validation_router",
    "CAD_VALIDATION_AVAILABLE",
    "recorder_router",
    "verifier_router",
]
