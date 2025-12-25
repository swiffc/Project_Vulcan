import pytest
from core.api import app
from fastapi.testclient import TestClient
import httpx
from unittest.mock import patch, MagicMock

client = TestClient(app)


@pytest.mark.asyncio
async def test_cad_context_injection():
    """Test that CAD context is injected into chat prompts."""

    # Mock Desktop Server response
    mock_event = {
        "timestamp": "2025-12-24T12:00:00",
        "features": [{"name": "Flange123", "type": "Extrusion"}],
    }

    with patch("httpx.AsyncClient.get") as mock_get:
        # Mock the events/latest call
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_event
        mock_get.return_value = mock_resp

        # Mock LLM generation
        with patch("core.llm.llm.generate") as mock_gen:
            mock_gen.return_value = "I see you have selected Flange123."

            # Trigger a CAD chat
            # Note: We need to bypass API key if possible or provide it
            # For testing, we'll assume API_KEY is set or mocked

            response = client.post(
                "/chat",
                json={
                    "messages": [
                        {"role": "user", "content": "Tell me about this flange"}
                    ],
                    "agent": "cad",
                },
                headers={
                    "X-API-Key": "test_key"
                },  # This needs to match os.environ.get("API_KEY")
            )

            # If 401, we need to mock the API key check
            if response.status_code == 401:
                with patch("core.api.get_api_key", return_value="test_key"):
                    response = client.post(
                        "/chat",
                        json={
                            "messages": [
                                {"role": "user", "content": "Tell me about this flange"}
                            ],
                            "agent": "cad",
                        },
                        headers={"X-API-Key": "test_key"},
                    )

            # Check if llm.generate was called with the context
            # The context should contain "Flange123"
            _, kwargs = mock_gen.call_args
            system_prompt = kwargs.get("system", "")

            assert "CURRENT SOLIDWORKS CONTEXT" in system_prompt
            assert "Flange123" in system_prompt
            assert response.status_code == 200
            assert "Flange123" in response.json()["response"]
