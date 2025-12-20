"""
Voice Command Adapter - Whisper Integration

Thin wrapper around OpenAI Whisper for voice-to-text input.
Supports both local Whisper and OpenAI API.
"""

import os
import logging
import tempfile
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("core.voice")


@dataclass
class TranscriptionResult:
    """Result from voice transcription."""
    text: str
    language: str
    confidence: float
    duration_seconds: float


class VoiceAdapter:
    """
    Whisper-based voice command adapter.

    Supports:
    - Local Whisper model (offline)
    - OpenAI Whisper API (online)
    - Audio file or microphone input
    """

    def __init__(self, mode: str = "api"):
        """
        Initialize voice adapter.

        Args:
            mode: "api" for OpenAI API, "local" for local model
        """
        self.mode = mode
        self._model = None
        self._client = None

    def _init_local(self):
        """Lazy load local Whisper model."""
        if self._model is None:
            try:
                import whisper
                self._model = whisper.load_model("base")
                logger.info("Loaded local Whisper model")
            except ImportError:
                raise RuntimeError("whisper not installed. Run: pip install openai-whisper")

    def _init_api(self):
        """Lazy load OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                logger.info("Initialized OpenAI Whisper API client")
            except ImportError:
                raise RuntimeError("openai not installed. Run: pip install openai")

    async def transcribe_file(self, audio_path: str) -> TranscriptionResult:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to audio file (wav, mp3, m4a, etc.)

        Returns:
            TranscriptionResult with text and metadata.
        """
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if self.mode == "local":
            return await self._transcribe_local(path)
        else:
            return await self._transcribe_api(path)

    async def _transcribe_local(self, path: Path) -> TranscriptionResult:
        """Transcribe using local Whisper model."""
        self._init_local()

        result = self._model.transcribe(str(path))

        return TranscriptionResult(
            text=result["text"].strip(),
            language=result.get("language", "en"),
            confidence=1.0,  # Local model doesn't provide confidence
            duration_seconds=result.get("duration", 0.0)
        )

    async def _transcribe_api(self, path: Path) -> TranscriptionResult:
        """Transcribe using OpenAI Whisper API."""
        self._init_api()

        with open(path, "rb") as audio_file:
            response = self._client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json"
            )

        return TranscriptionResult(
            text=response.text.strip(),
            language=getattr(response, "language", "en"),
            confidence=1.0,
            duration_seconds=getattr(response, "duration", 0.0)
        )

    async def record_and_transcribe(
        self,
        duration_seconds: int = 5,
        sample_rate: int = 16000
    ) -> TranscriptionResult:
        """
        Record from microphone and transcribe.

        Args:
            duration_seconds: Recording duration
            sample_rate: Audio sample rate

        Returns:
            TranscriptionResult from recorded audio.
        """
        try:
            import sounddevice as sd
            import soundfile as sf
        except ImportError:
            raise RuntimeError(
                "sounddevice/soundfile not installed. "
                "Run: pip install sounddevice soundfile"
            )

        logger.info(f"Recording for {duration_seconds} seconds...")

        # Record audio
        recording = sd.rec(
            int(duration_seconds * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="float32"
        )
        sd.wait()

        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            sf.write(f.name, recording, sample_rate)
            temp_path = f.name

        try:
            result = await self.transcribe_file(temp_path)
            return result
        finally:
            # Cleanup temp file
            Path(temp_path).unlink(missing_ok=True)

    def parse_command(self, text: str) -> Dict[str, Any]:
        """
        Parse transcribed text into command structure.

        Args:
            text: Transcribed voice input

        Returns:
            Dict with intent and parameters.
        """
        text_lower = text.lower().strip()

        # Trading commands
        if any(kw in text_lower for kw in ["analyze", "analysis", "chart"]):
            pair = self._extract_pair(text_lower)
            return {"intent": "trading_analyze", "pair": pair}

        if any(kw in text_lower for kw in ["journal", "log trade", "record"]):
            return {"intent": "trading_journal", "raw": text}

        # CAD commands
        if any(kw in text_lower for kw in ["create", "build", "model", "sketch"]):
            return {"intent": "cad_create", "raw": text}

        if any(kw in text_lower for kw in ["open solidworks", "open inventor"]):
            return {"intent": "cad_open", "raw": text}

        # System commands
        if any(kw in text_lower for kw in ["status", "health", "check"]):
            return {"intent": "system_status"}

        if "backup" in text_lower:
            return {"intent": "system_backup"}

        # Default: general query
        return {"intent": "general", "query": text}

    def _extract_pair(self, text: str) -> Optional[str]:
        """Extract currency pair from text."""
        pairs = [
            "eurusd", "gbpusd", "usdjpy", "gbpjpy",
            "eurjpy", "audusd", "usdcad", "nzdusd"
        ]
        for pair in pairs:
            if pair in text.replace(" ", "").replace("/", ""):
                return pair.upper()
        return None


# Singleton instance
_voice: Optional[VoiceAdapter] = None


def get_voice_adapter(mode: str = "api") -> VoiceAdapter:
    """Get or create voice adapter singleton."""
    global _voice
    if _voice is None:
        _voice = VoiceAdapter(mode=mode)
    return _voice
