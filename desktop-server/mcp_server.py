"""
Project Vulcan - Desktop Control MCP Server
Standardized Model Context Protocol server for desktop automation.
Replaces the legacy FastAPI wrapper with a direct MCP interface.

Tools:
- mouse_move(x, y)
- mouse_click(button)
- type_text(text)
- press_key(key)
- get_screen_info()
- get_logs()

Resources:
- vulcan://logs (Stream of recent actions)
- vulcan://screen (Current screen state/metadata)
"""

import sys
import logging
import asyncio
from datetime import datetime
from typing import Optional, List

# Try to import FastMCP, handling potential version differences
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    # If using a different version or structure, fallback might be needed
    # For now, we assume the user installed the correct 'mcp' package with FastMCP support
    raise ImportError("FastMCP not found. Ensure 'mcp' is installed.")

import pyautogui
import socket

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vulcan-mcp")

# Initialize Server
mcp = FastMCP("Vulcan Desktop Control")

# Global State
KILL_SWITCH_ACTIVE = False
ACTION_LOG = []
COMMAND_QUEUE = asyncio.Queue()

# --- Helper Functions ---


def check_kill_switch() -> bool:
    """Check if mouse is in corner (Safety Feature)."""
    global KILL_SWITCH_ACTIVE
    x, y = pyautogui.position()
    if x <= 10 and y <= 10:
        KILL_SWITCH_ACTIVE = True
        logger.warning("KILL SWITCH ACTIVATED")
        return True
    return False


def log_action(action_type: str, details: dict):
    """Log an action to the internal log."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "type": action_type,
        "details": details,
    }
    ACTION_LOG.append(entry)
    logger.info(f"Action: {action_type} - {details}")


# --- MCP Tools ---


@mcp.tool()
def mouse_move(x: int, y: int, duration: float = 0.5) -> str:
    """Move the mouse cursor to a specific (x, y) coordinate."""
    if check_kill_switch():
        return "Error: Kill Switch Active. Move mouse away from top-left corner."

    log_action("mouse_move", {"x": x, "y": y})
    pyautogui.moveTo(x, y, duration=duration)
    return f"Moved to ({x}, {y})"


@mcp.tool()
def mouse_click(
    x: Optional[int] = None,
    y: Optional[int] = None,
    button: str = "left",
    clicks: int = 1,
) -> str:
    """Click the mouse button. Optional coordinates."""
    if check_kill_switch():
        return "Error: Kill Switch Active."

    log_action("mouse_click", {"x": x, "y": y, "button": button, "clicks": clicks})

    if x is not None and y is not None:
        pyautogui.click(x, y, button=button, clicks=clicks)
        return f"Clicked {button} at ({x}, {y})"
    else:
        pyautogui.click(button=button, clicks=clicks)
        return f"Clicked {button} at current position"


@mcp.tool()
def type_text(text: str, interval: float = 0.0) -> str:
    """Type a string of text."""
    if check_kill_switch():
        return "Error: Kill Switch Active."

    log_action("type_text", {"text_len": len(text)})
    pyautogui.write(text, interval=interval)
    return "Typed text"


@mcp.tool()
def press_key(key: str) -> str:
    """Press a single key (e.g., 'enter', 'esc', 'space')."""
    if check_kill_switch():
        return "Error: Kill Switch Active."

    log_action("press_key", {"key": key})
    pyautogui.press(key)
    return f"Pressed {key}"


@mcp.tool()
def get_screen_info() -> dict:
    """Get screen resolution and current mouse position."""
    width, height = pyautogui.size()
    x, y = pyautogui.position()
    return {"width": width, "height": height, "mouse_x": x, "mouse_y": y}


# --- Resources ---


@mcp.resource("vulcan://logs")
def get_recent_logs() -> str:
    """Get the specific logs of desktop actions."""
    return str(ACTION_LOG[-20:])


@mcp.resource("vulcan://status")
def get_status() -> str:
    """Get current system status include kill switch state."""
    return f"Status: Running\nKill Switch: {KILL_SWITCH_ACTIVE}\nTailscale IP: {get_tailscale_ip()}"


# --- Network Utilities ---


def get_tailscale_ip() -> Optional[str]:
    """Get the Tailscale IP address if available."""
    try:
        hostname = socket.gethostname()
        # This is a basic check, might need refinement for actual Tailscale interfaces
        return socket.gethostbyname(hostname)
    except Exception:
        return "Unknown"


if __name__ == "__main__":
    # When running directly, FastMCP usually handles the serving via built-in CLI or run method
    # Use 'mcp run mcp_server.py' or similar if supported, or rely on FastMCP's internal runner
    print("Starting Vulcan Desktop MCP Server...")
    mcp.run()
