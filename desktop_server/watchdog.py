"""
Vulcan Watchdog
Rule 12: Automated Recovery.
- Monitors the MCP Server process.
- Restarts it if it crashes or becomes unresponsive.
- Logs uptime and crash events.
"""

import sys
import time
import subprocess
import psutil
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
log_dir = Path("storage/logs/watchdog")
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(log_dir / "watchdog.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("watchdog")

SERVER_SCRIPT = "mcp_server.py"
MAX_RESTARTS = 5
RESTART_WINDOW = 600  # 10 minutes


class Watchdog:
    def __init__(self):
        self.process = None
        self.restart_count = 0
        self.last_restart_time = 0

    def start_server(self):
        """Start the MCP server subprocess."""
        logger.info(f"Starting {SERVER_SCRIPT}...")
        try:
            # We assume python is in path or venv is active
            self.process = subprocess.Popen(
                [sys.executable, SERVER_SCRIPT],
                cwd=str(Path(__file__).parent),
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
            logger.info(f"Server started with PID: {self.process.pid}")
        except Exception as e:
            logger.error(f"Failed to start server: {e}")

    def monitor(self):
        """Monitor loop."""
        print(f"Watchdog active using python executable: {sys.executable}")
        self.start_server()

        while True:
            try:
                if self.process:
                    return_code = self.process.poll()
                    if return_code is not None:
                        logger.warning(f"Server process ended with code {return_code}")
                        self.handle_crash()

                    # Optional: Check memory usage or responsiveness here
                    # For now, we trust the process existence
                else:
                    self.start_server()

                time.sleep(5)
            except KeyboardInterrupt:
                logger.info("Watchdog stopped by user.")
                if self.process:
                    self.process.terminate()
                break
            except Exception as e:
                logger.error(f"Watchdog error: {e}")
                time.sleep(5)

    def handle_crash(self):
        """Handle server crash logic."""
        now = time.time()

        # Reset counter if outside window
        if now - self.last_restart_time > RESTART_WINDOW:
            self.restart_count = 0

        self.restart_count += 1
        self.last_restart_time = now

        if self.restart_count > MAX_RESTARTS:
            logger.critical("Maximum restart limit reached. Aborting.")
            print("CRITICAL: Server is crashing repeatedly. Watchdog aborting.")
            sys.exit(1)

        logger.warning(
            f"Restarting server (Attempt {self.restart_count}/{MAX_RESTARTS})..."
        )
        time.sleep(2)  # Give it a moment to release resources
        self.start_server()


if __name__ == "__main__":
    dog = Watchdog()
    dog.monitor()
