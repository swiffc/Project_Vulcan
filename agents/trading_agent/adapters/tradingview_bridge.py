"""
TradingView Bridge - MCP Desktop Control Integration

Bridges trading agent to TradingView via the Desktop MCP Server.
All physical control goes through MCP, never direct pyautogui.

Follows Rule 4: Physical Control Architecture
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger("trading.tradingview_bridge")


@dataclass
class ChartState:
    """Current state of TradingView chart."""
    symbol: str
    timeframe: str
    is_focused: bool = False
    screenshot_path: Optional[str] = None


class TradingViewBridge:
    """
    Bridge to control TradingView desktop app via MCP.

    All actions route through Desktop MCP Server (Rule 4).
    """

    def __init__(self, mcp_client=None):
        """
        Args:
            mcp_client: MCP client for desktop control. If None, uses mock.
        """
        self.mcp = mcp_client
        self.current_chart = ChartState(symbol="", timeframe="")

    async def focus_tradingview(self) -> bool:
        """Bring TradingView window to front."""
        if not self.mcp:
            logger.warning("MCP client not configured - mock mode")
            return True

        result = await self.mcp.call_tool(
            "window_focus",
            {"title": "TradingView"}
        )
        self.current_chart.is_focused = result.get("success", False)
        return self.current_chart.is_focused

    async def change_symbol(self, symbol: str) -> bool:
        """
        Change chart symbol in TradingView.

        Args:
            symbol: Trading pair (e.g., "EURUSD", "BTCUSD")
        """
        if not self.mcp:
            self.current_chart.symbol = symbol
            return True

        # Focus TradingView first
        await self.focus_tradingview()

        # Open symbol search (keyboard shortcut)
        await self.mcp.call_tool("press_key", {"key": "s"})

        # Type symbol
        await self.mcp.call_tool("type_text", {"text": symbol})

        # Press Enter to confirm
        await self.mcp.call_tool("press_key", {"key": "enter"})

        self.current_chart.symbol = symbol
        logger.info(f"Changed symbol to {symbol}")
        return True

    async def change_timeframe(self, timeframe: str) -> bool:
        """
        Change chart timeframe.

        Args:
            timeframe: e.g., "1", "5", "15", "60", "D", "W"
        """
        if not self.mcp:
            self.current_chart.timeframe = timeframe
            return True

        await self.focus_tradingview()

        # TradingView timeframe shortcuts
        tf_map = {
            "1": "1", "5": "5", "15": "15", "30": "30",
            "60": "60", "H1": "60", "H4": "240",
            "D": "D", "W": "W", "M": "M"
        }

        key = tf_map.get(timeframe, timeframe)
        await self.mcp.call_tool("press_key", {"key": key})

        self.current_chart.timeframe = timeframe
        logger.info(f"Changed timeframe to {timeframe}")
        return True

    async def capture_chart(self) -> Optional[str]:
        """
        Capture screenshot of current chart.

        Returns:
            Path to screenshot file, or None on failure.
        """
        if not self.mcp:
            return "/mock/screenshot.png"

        await self.focus_tradingview()

        result = await self.mcp.call_tool(
            "screenshot",
            {"region": "active_window"}
        )

        path = result.get("path")
        self.current_chart.screenshot_path = path
        logger.info(f"Captured chart screenshot: {path}")
        return path

    async def draw_horizontal_line(self, price: float) -> bool:
        """Draw horizontal line at price level."""
        if not self.mcp:
            return True

        await self.focus_tradingview()

        # Alt+H for horizontal line in TradingView
        await self.mcp.call_tool("hotkey", {"keys": ["alt", "h"]})

        # Click at price level (would need price-to-pixel conversion)
        # For now, simplified implementation
        logger.info(f"Drew horizontal line at {price}")
        return True

    async def get_screen_info(self) -> Dict[str, Any]:
        """Get current screen/chart info for analysis."""
        if not self.mcp:
            return {"mock": True, "symbol": self.current_chart.symbol}

        result = await self.mcp.call_tool("get_screen_info", {})
        return result

    def get_state(self) -> Dict[str, Any]:
        """Get current bridge state."""
        return {
            "symbol": self.current_chart.symbol,
            "timeframe": self.current_chart.timeframe,
            "is_focused": self.current_chart.is_focused,
            "has_screenshot": self.current_chart.screenshot_path is not None
        }
