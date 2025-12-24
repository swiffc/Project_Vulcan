"""
Export Adapter
==============
Handles exporting of Vulcan strategies and artifacts to various formats.

Features:
- Export strategies to JSON
- Export CAD plans to Markdown
- Backup/Archive functionality
"""

import json
import os
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger("vulcan.core.export")


class ExportAdapter:
    """Adapter for exporting system artifacts."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.strategies_dir = os.path.join("data", "cad-strategies")

        # Ensure directories exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.strategies_dir, exist_ok=True)

    def export_strategy(self, name: str, strategy_data: Dict[str, Any]) -> str:
        """
        Export a CAD strategy to a JSON file.

        Args:
            name: Name of the strategy (e.g., 'nozzle_repad')
            strategy_data: The dictionary content of the strategy

        Returns:
            Absolute path to the exported file
        """
        filename = f"{name}.json"
        # Sanitize filename
        filename = "".join(
            [c for c in filename if c.isalpha() or c.isdigit() or c in "._-"]
        )

        filepath = os.path.join(self.strategies_dir, filename)

        try:
            with open(filepath, "w") as f:
                json.dump(strategy_data, f, indent=2)
            logger.info(f"Successfully exported strategy to {filepath}")
            return os.path.abspath(filepath)
        except Exception as e:
            logger.error(f"Failed to export strategy {name}: {e}")
            raise

    def export_plan(self, plan_name: str, markdown_content: str) -> str:
        """
        Export a generated plan to a Markdown file.
        """
        filename = f"PLAN_{plan_name}.md"
        filepath = os.path.join(self.output_dir, filename)

        try:
            with open(filepath, "w") as f:
                f.write(markdown_content)
            return os.path.abspath(filepath)
        except Exception as e:
            logger.error(f"Failed to export plan {plan_name}: {e}")
            raise


# Singleton instance
_exporter = ExportAdapter()


def get_export_adapter() -> ExportAdapter:
    return _exporter
