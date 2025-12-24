import unittest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

# Target Modules
from agents.cad_agent.bom_manager import BOMManager, BOMItem
from agents.cad_agent.format_converter import FormatConverter
from core.model_router import ModelRouter, ModelTier, ModelProvider
from core.queue_adapter import QueueAdapter, TaskStatus
from core.circuit_breaker import (
    CircuitBreakerAdapter,
    CircuitState,
    CircuitBreakerError,
)


class TestPhase21Enhancements(unittest.TestCase):
    """
    Comprehensive tests for Phase 21 Gap Analysis deliverables.
    Covering: BOM, Formats, Routing, Queues, Resilience.
    """

    # --- GAP 19: BOM MANAGER TESTS ---
    def test_bom_manager_normalization(self):
        manager = BOMManager()
        raw_items = [
            {"PART NO": "123-ABC", "QTY": "5", "DESC": "Bolt"},
            {"Material": "Steel", "Quantity": 2, "Part Number": "456-DEF"},
        ]

        analysis = manager.process_bom(raw_items)

        self.assertEqual(len(analysis.items), 2)
        self.assertEqual(analysis.items[0]["part_number"], "123-ABC")
        self.assertEqual(analysis.items[0]["quantity"], 5)
        self.assertEqual(analysis.items[1]["material"], "Steel")

    def test_bom_cost_estimation(self):
        manager = BOMManager()
        # Mocking the internal cost estimator if strictly needed,
        # but the class has a simple default "standard part" logic.

        raw_items = [{"description": "Screw M5", "quantity": 10}]
        analysis = manager.process_bom(raw_items)

        # Should be classified as standard due to "Screw"
        self.assertTrue(analysis.standard_parts_count > 0)
        self.assertGreater(analysis.total_cost, 0)

    # --- GAP 3: FORMAT CONVERTER TESTS ---
    @patch("agents.cad_agent.format_converter.os.path.exists")
    def test_format_converter_logic(self, mock_exists):
        mock_exists.return_value = True
        converter = FormatConverter()

        # Simulate missing backend
        converter.has_cadquery = False
        result = converter.convert_to_stl("test.step")
        self.assertIsNone(result, "Should fail gracefully without backend")

    # --- GAP 4: MODEL ROUTER TESTS ---
    def test_router_domain_detection(self):
        router = ModelRouter()

        cad_msg = "Please extrude this sketch by 5mm and export to STEP."
        trade_msg = "Analyze the quarterly theory for GBPUSD."
        general_msg = "Hello, how are you?"

        self.assertEqual(router.detect_domain(cad_msg), "cad")
        self.assertEqual(router.detect_domain(trade_msg), "trading")
        self.assertEqual(router.detect_domain(general_msg), "general")

    def test_router_decision(self):
        router = ModelRouter()

        # Engineering -> Claude
        decision = router.route("Check tolerance on this BOM", agent_type="cad_agent")
        self.assertEqual(decision.provider, ModelProvider.ANTHROPIC)
        self.assertEqual(decision.model, ModelTier.SONNET.value)

        # Trading -> GPT-4o
        decision = router.route(
            "What is the bias for today?", agent_type="trading_agent"
        )
        self.assertEqual(decision.provider, ModelProvider.OPENAI)
        self.assertEqual(decision.model, ModelTier.GPT4O.value)

    # --- GAP 9: QUEUE ADAPTER TESTS ---
    def test_queue_lifecycle(self):
        async def run_async_test():
            queue = QueueAdapter()

            # 1. Register Handler
            mock_handler = AsyncMock(return_value="Success")
            queue.register("test_queue", mock_handler, concurrency=1)

            # 2. Enqueue
            job_id = await queue.enqueue("test_queue", "do_something")
            self.assertIsNotNone(job_id)

            # 3. List (Should be PENDING or RUNNING)
            jobs = queue.list_jobs()
            self.assertIn(job_id, [j.id for j in jobs])

            # 4. Wait for completion
            result = await queue.wait_for(job_id, timeout=2.0)
            self.assertEqual(result, "Success")

            # 5. Verify status logic
            final_job = queue.tasks[job_id]
            self.assertEqual(final_job.status.value, "completed")

        asyncio.run(run_async_test())

    # --- GAP 13: CIRCUIT BREAKER TESTS ---
    def test_circuit_breaker_fallback(self):
        async def run_resilience_test():
            breaker = CircuitBreakerAdapter()
            breaker.register("unstable_service")

            async def failing_func():
                raise ValueError("Service Down")

            async def fallback_func():
                return "Fallback Active"

            # Execute with fallback
            result = await breaker.run_with_fallback(
                "unstable_service", failing_func, fallback_func
            )

            self.assertEqual(result, "Fallback Active")

            # Verify failure was recorded
            stats = breaker.stats["unstable_service"]
            self.assertEqual(stats.failures, 1)

        asyncio.run(run_resilience_test())


if __name__ == "__main__":
    unittest.main()
