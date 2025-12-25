import asyncio
import logging
from typing import Optional, Dict, Any
from core.voice_adapter import get_voice_adapter
from core.orchestrator_adapter import get_orchestrator, TaskRequest, AgentType
import httpx
import os

logger = logging.getLogger("core.hands_free")


class HandsFreeLoop:
    """
    Background loop for hands-free voice command processing.
    Listens for speech, fetches desktop context, and executes via orchestrator.
    """

    def __init__(self, desktop_url: str = "http://localhost:8000"):
        self.desktop_url = desktop_url
        self.voice = get_voice_adapter(mode="api")
        self.orchestrator = get_orchestrator()
        self.is_running = False
        self._task = None

    async def start(self):
        """Start the background listening loop."""
        if self.is_running:
            return

        self.is_running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("Hands-Free Voice Loop started")

    async def stop(self):
        """Stop the background listening loop."""
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Hands-Free Voice Loop stopped")

    async def _loop(self):
        """Internal loop logic."""
        while self.is_running:
            try:
                # 1. Listen for voice (Wait for wake word or just record if in active mode)
                # For this implementation, we'll assume the user triggers recording or use a short gap
                logger.debug("Listening for voice...")

                # In a real scenario, we might use a wake-word engine like Porcupine
                # Here we simulate a recording session
                transcript = await self.voice.record_and_transcribe(duration_seconds=3)

                if not transcript.text or len(transcript.text) < 3:
                    await asyncio.sleep(1)
                    continue

                logger.info(f"Voice Command Detected: {transcript.text}")

                # 2. Fetch Desktop Context (SolidWorks, etc.)
                context = await self._fetch_desktop_context()

                # 3. Parse and Route
                # Inject context into command parsing
                command = self.voice.parse_command(transcript.text, context=context)

                # 4. Execute via Orchestrator
                request = TaskRequest(
                    message=transcript.text,
                    context=context,
                    preferred_agent=self._map_intent_to_agent(command.get("intent")),
                )

                result = await self.orchestrator.route(request)
                logger.info(f"Command Result: {result.success}")

            except Exception as e:
                logger.error(f"Error in hands-free loop: {e}")
                await asyncio.sleep(5)  # Prevent rapid failure loops

    async def _fetch_desktop_context(self) -> Dict[str, Any]:
        """Fetch latest selection/context from desktop server."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(
                    f"{self.desktop_url}/api/solidworks/events/latest"
                )
                if resp.status_code == 200:
                    return resp.json()
        except Exception as e:
            logger.warning(f"Could not fetch desktop context: {e}")
        return {}

    def _map_intent_to_agent(self, intent: str) -> AgentType:
        """Map voice intent to agent type."""
        if intent and intent.startswith("cad_"):
            return AgentType.CAD
        if intent and intent.startswith("trading_"):
            return AgentType.TRADING
        if intent and intent.startswith("system_"):
            return AgentType.SYSTEM
        return AgentType.GENERAL


# Singleton instance
_hands_free: Optional[HandsFreeLoop] = None


def get_hands_free_loop(desktop_url: str = None) -> HandsFreeLoop:
    global _hands_free
    if _hands_free is None:
        url = desktop_url or os.getenv("DESKTOP_SERVER_URL", "http://localhost:8000")
        _hands_free = HandsFreeLoop(desktop_url=url)
    return _hands_free
