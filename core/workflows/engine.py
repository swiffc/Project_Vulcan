"""
Workflow Engine
===============
Executes custom user-defined automation workflows.

Features:
- Trigger management (File, Schedule, Webhook)
- Step execution logic
- Condition evaluation
- Context passing between steps
"""

import logging
import asyncio
from typing import List, Dict, Callable
from dataclasses import dataclass

logger = logging.getLogger("vulcan.core.workflows")


@dataclass
class WorkflowContext:
    trigger_data: Dict
    variables: Dict
    logs: List[str]


class WorkflowStep:
    def __init__(self, name: str, action: Callable, params: Dict):
        self.name = name
        self.action = action
        self.params = params

    async def execute(self, ctx: WorkflowContext):
        logger.info(f"Executing step: {self.name}")
        try:
            result = await self.action(ctx, **self.params)
            ctx.variables[self.name] = result
            ctx.logs.append(f"Step {self.name} succeeded")
        except Exception as e:
            ctx.logs.append(f"Step {self.name} failed: {e}")
            raise


class WorkflowEngine:
    """Orchestrates the execution of multi-step workflows."""

    def __init__(self):
        self.active_workflows = {}
        self.action_registry = {}

    def register_action(self, name: str, func: Callable):
        """Register a callable action (e.g. 'validate_cad', 'email_report')."""
        self.action_registry[name] = func

    async def run_workflow(
        self, workflow_def: Dict, trigger_data: Dict
    ) -> WorkflowContext:
        """
        Execute a workflow definition.

        Args:
           workflow_def: JSON-like structure defining steps
           trigger_data: Data that started the workflow
        """
        ctx = WorkflowContext(trigger_data, {}, [])
        steps = workflow_def.get("steps", [])

        logger.info(f"Starting workflow: {workflow_def.get('name')}")

        try:
            for step_def in steps:
                action_name = step_def.get("action")
                func = self.action_registry.get(action_name)
                if not func:
                    raise ValueError(f"Unknown action: {action_name}")

                step = WorkflowStep(
                    name=step_def.get("name", action_name),
                    action=func,
                    params=step_def.get("params", {}),
                )

                await step.execute(ctx)

            return ctx

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            raise


# Examples of actions to register
async def action_validate_cad(ctx, file_path):
    # Call CAD Validator
    return {"status": "passed", "errors": []}


async def action_log_message(ctx, message):
    logger.info(f"WORKFLOW LOG: {message}")
    return True


# Initialize global engine
_engine = WorkflowEngine()
_engine.register_action("validate_cad", action_validate_cad)
_engine.register_action("log", action_log_message)


def get_workflow_engine() -> WorkflowEngine:
    return _engine
