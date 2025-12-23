"""
Test endpoint for Sentry error tracking.
Trigger a test error to verify Sentry integration.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/test/sentry-error")
async def test_sentry_error():
    """
    Test endpoint to trigger a Sentry error.
    This helps verify that Sentry is properly configured.
    """
    raise Exception("Test error for Sentry - This is intentional!")


@router.get("/test/sentry-message")
async def test_sentry_message():
    """
    Test endpoint to send a message to Sentry.
    """
    import sentry_sdk

    sentry_sdk.capture_message("Test message from Vulcan Orchestrator", level="info")
    return {"status": "Message sent to Sentry"}
