import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

from agents.cad_agent.bom_manager import BOMManager
from core.model_router import ModelRouter, ModelTier
from core.queue_adapter import QueueAdapter
from core.circuit_breaker import CircuitBreakerAdapter


class TestIntegrationPhase21(unittest.TestCase):
    """
    End-to-End Integration Tests for Phase 21 Workflows.
    Simulates the lifecycle of a CAD Validation Job.
    """

    def setUp(self):
        self.queue = QueueAdapter()
        self.router = ModelRouter()
        self.bom_manager = BOMManager()
        self.breaker = CircuitBreakerAdapter()

    def test_cad_validation_workflow_integration(self):
        """
        Simulate a full flow:
        1. User submits Drawing Validation Job -> Queue
        2. Worker picks up job
        3. Worker routes request to correct AI Model
        4. Worker extracts BOM
        5. Worker calls external service (protected by Circuit Breaker)
        """

        async def run_workflow():
            # 1. Enqueue Job
            payload = {
                "drawing_id": "DWG-101",
                "bom_data": [{"part": "Bolt", "qty": 10}],
                "user_query": "Check for GD&T errors",
            }
            job_id = await self.queue.enqueue("cad_validation", "validate", payload)

            # 2. Worker Simulation (dequeue)
            # In real app, this happens in background worker. Here we manually process.
            job = self.queue.get_job(job_id)
            self.assertIsNotNone(job)

            # 3. Model Routing
            # The worker needs to know which LLM to use for the user's query
            routing_decision = self.router.route(
                payload["user_query"], agent_type="cad_agent"
            )

            # Assert correct routing logic (Engineering -> Claude)
            self.assertIn("claude", routing_decision.model.lower())

            # 4. BOM Processing
            # The worker validates the BOM data in the payload
            bom_analysis = self.bom_manager.process_bom(payload["bom_data"])
            self.assertEqual(bom_analysis.total_items, 10)

            # 5. External Call (Circuit Breaker protected)
            # Simulating a call to a cloud standards database
            mock_external_api = AsyncMock(return_value={"standards": ["ASME Y14.5"]})

            result = await self.breaker.run_with_fallback(
                "standards_db",
                mock_external_api,
                fallback_func=AsyncMock(
                    return_value={"standards": ["Offline Fallback"]}
                ),
            )

            self.assertEqual(result["standards"][0], "ASME Y14.5")

            return "Workflow Success"

        # Run the async workflow
        result = asyncio.run(run_workflow())
        self.assertEqual(result, "Workflow Success")


if __name__ == "__main__":
    unittest.main()
