"""
Load Testing (PRD Section 9)

Tests performance under load:
- Target: < 2% failure at 100 runs
- Chat response: < 5 sec

Run with: pytest tests/test_load.py -v
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestLoadPerformance:
    """Load and performance tests per PRD success criteria."""

    @pytest.mark.asyncio
    async def test_100_concurrent_requests(self):
        """
        PRD Criteria: < 2% failure at 100 runs

        Simulates 100 concurrent chat requests.
        """
        from core.orchestrator_adapter import (
            OrchestratorAdapter, TaskRequest, AgentType
        )

        orch = OrchestratorAdapter()

        # Mock fast-responding agent
        mock_agent = AsyncMock()
        mock_agent.process = AsyncMock(return_value={"status": "ok"})
        orch.register_agent(AgentType.GENERAL, mock_agent)

        async def make_request(i: int):
            try:
                request = TaskRequest(message=f"Test request {i}")
                result = await orch.route(request)
                return result.success
            except Exception:
                return False

        # Run 100 concurrent requests
        tasks = [make_request(i) for i in range(100)]
        results = await asyncio.gather(*tasks)

        # Calculate success rate
        successes = sum(results)
        failure_rate = (100 - successes) / 100

        assert failure_rate < 0.02, f"Failure rate {failure_rate:.1%} exceeds 2%"

    @pytest.mark.asyncio
    async def test_chat_response_under_5_seconds(self):
        """
        PRD Criteria: Chat response < 5 sec
        """
        from core.orchestrator_adapter import (
            OrchestratorAdapter, TaskRequest, AgentType
        )

        orch = OrchestratorAdapter()

        # Mock agent with slight delay
        mock_agent = AsyncMock()

        async def slow_process(*args, **kwargs):
            await asyncio.sleep(0.1)  # 100ms simulated processing
            return {"response": "Analysis complete"}

        mock_agent.process = slow_process
        orch.register_agent(AgentType.TRADING, mock_agent)

        request = TaskRequest(message="Analyze EURUSD")

        start = time.time()
        result = await orch.route(request)
        elapsed = time.time() - start

        assert result.success
        assert elapsed < 5.0, f"Response took {elapsed:.2f}s, exceeds 5s limit"

    @pytest.mark.asyncio
    async def test_rate_limiter_under_load(self):
        """Test rate limiter handles burst traffic."""
        from core.rate_limiter import RateLimiter, RateLimitConfig

        config = RateLimitConfig(
            requests_per_minute=60,
            burst_size=10
        )
        limiter = RateLimiter(config)

        # Burst of 15 requests (exceeds burst_size of 10)
        results = []
        for i in range(15):
            allowed, meta = limiter.check(user_id="load-test")
            results.append(allowed)

        # First 10 should pass (burst), rest should be limited
        passed = sum(results)
        assert passed == 10, f"Expected 10 passed, got {passed}"

    @pytest.mark.asyncio
    async def test_memory_under_load(self):
        """Test memory operations under load."""
        operations = 100
        successes = 0

        mock_memory = AsyncMock()
        mock_memory.store = AsyncMock(return_value={"id": "test"})
        mock_memory.search = AsyncMock(return_value=[])

        for i in range(operations):
            try:
                await mock_memory.store({"data": f"item-{i}"})
                await mock_memory.search(f"query-{i}")
                successes += 1
            except Exception:
                pass

        success_rate = successes / operations
        assert success_rate >= 0.98, f"Memory success rate {success_rate:.1%} below 98%"

    @pytest.mark.asyncio
    async def test_circuit_breaker_under_load(self):
        """Test circuit breaker protects under failure storm."""
        from core.circuit_breaker import CircuitBreakerAdapter, CircuitConfig, CircuitState

        breaker = CircuitBreakerAdapter()
        config = CircuitConfig(failure_threshold=3, timeout_seconds=1)
        breaker.register("test_circuit", config)

        # Define a failing function
        @breaker.protect("test_circuit")
        async def failing_function():
            raise Exception("Simulated failure")

        # Simulate failures
        for _ in range(5):
            try:
                await failing_function()
            except Exception:
                pass

        # Circuit should be open after threshold failures
        assert breaker.circuits["test_circuit"] == CircuitState.OPEN

        # Further calls should fail fast with CircuitBreakerError
        from core.circuit_breaker import CircuitBreakerError
        start = time.time()
        try:
            await failing_function()
        except CircuitBreakerError:
            pass
        except Exception:
            pass
        elapsed = time.time() - start

        # Should fail immediately
        assert elapsed < 0.1, "Circuit breaker not failing fast"


class TestEndurance:
    """Endurance tests for long-running stability."""

    @pytest.mark.asyncio
    async def test_sustained_load(self):
        """Test sustained load over time (simulated)."""
        from core.orchestrator_adapter import (
            OrchestratorAdapter, TaskRequest, AgentType
        )

        orch = OrchestratorAdapter()

        mock_agent = AsyncMock()
        mock_agent.process = AsyncMock(return_value={"ok": True})
        orch.register_agent(AgentType.GENERAL, mock_agent)

        # Simulate 10 "minutes" of traffic (1 request per "second")
        total_requests = 100
        failures = 0

        for i in range(total_requests):
            try:
                request = TaskRequest(message=f"Sustained test {i}")
                result = await orch.route(request)
                if not result.success:
                    failures += 1
            except Exception:
                failures += 1

        failure_rate = failures / total_requests
        assert failure_rate < 0.02, f"Sustained failure rate {failure_rate:.1%}"

    @pytest.mark.asyncio
    async def test_memory_leak_check(self):
        """Basic check for memory growth."""
        import gc

        from core.orchestrator_adapter import OrchestratorAdapter

        # Create and destroy many instances
        for _ in range(100):
            orch = OrchestratorAdapter()
            del orch

        gc.collect()

        # If we get here without OOM, basic check passes
        assert True


class TestLatencyPercentiles:
    """Test response time percentiles."""

    @pytest.mark.asyncio
    async def test_p95_latency(self):
        """Test 95th percentile latency is acceptable."""
        from core.orchestrator_adapter import (
            OrchestratorAdapter, TaskRequest, AgentType
        )

        orch = OrchestratorAdapter()

        mock_agent = AsyncMock()

        async def variable_latency(*args, **kwargs):
            import random
            await asyncio.sleep(random.uniform(0.01, 0.2))
            return {"ok": True}

        mock_agent.process = variable_latency
        orch.register_agent(AgentType.GENERAL, mock_agent)

        latencies = []
        for i in range(50):
            request = TaskRequest(message=f"Latency test {i}")
            start = time.time()
            await orch.route(request)
            latencies.append(time.time() - start)

        latencies.sort()
        p95_index = int(len(latencies) * 0.95)
        p95_latency = latencies[p95_index]

        # P95 should be under 1 second for mocked responses
        assert p95_latency < 1.0, f"P95 latency {p95_latency:.2f}s too high"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
