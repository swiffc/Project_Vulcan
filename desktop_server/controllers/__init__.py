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

__all__ = ['mouse_router', 'keyboard_router', 'screen_router', 'window_router', 'tradingview_router', 'TRADINGVIEW_AVAILABLE']
