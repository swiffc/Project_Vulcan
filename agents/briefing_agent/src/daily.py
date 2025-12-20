"""
Daily Briefing Agent
Aggregates system status, logs, and simulated data to generate a morning briefing.
"""

import sys
import glob
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core.llm import llm


class BriefingAgent:
    def __init__(self):
        self.output_dir = Path("storage/briefings")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.watchdog_log = Path("storage/logs/watchdog/watchdog.log")
        self.decision_logs = Path("storage/logs/decisions")

    def generate_briefing(self) -> str:
        """Generate the daily briefing markdown."""
        print("Gathering intel...")

        # 1. Check System Health (Watchdog)
        health_status = "Unknown"
        if self.watchdog_log.exists():
            with open(self.watchdog_log, "r") as f:
                lines = f.readlines()
                last_lines = lines[-10:] if lines else []
                health_status = "".join(last_lines)

        # 2. Check Recent Decisions
        recent_activity = []
        log_files = glob.glob(str(self.decision_logs / "*.jsonl"))
        for log_file in log_files:
            with open(log_file, "r") as f:
                for line in f:
                    if line.strip():
                        try:
                            recent_activity.append(json.loads(line))
                        except:
                            pass
        recent_activity = recent_activity[-5:]  # Last 5 actions

        # 3. Simulate Calendar/Trading Data (Mock for now)
        mock_calendar = ["09:00 AM - Team Sync", "02:00 PM - Deep Work Block"]
        mock_trading = "Market is OPEN. Sentiment: BULLISH."

        # 4. Generate with LLM
        prompt = f"""You are the Chief of Staff for Project Vulcan.
Generate a Daily Briefing for the user.

## System Status
Last Watchdog Logs:
{health_status}

## Recent Agent Activity
{json.dumps(recent_activity, indent=2)}

## Calendar
{mock_calendar}

## Market Status
{mock_trading}

Format as a clean, professional Markdown report.
Start with a "Good Morning" message.
Highlight any system warnings or critical decision logs.
End with a motivating quote.
"""

        print("Consulting LLM...")
        briefing = llm.generate(
            messages=[{"role": "user", "content": prompt}],
            system="You are an elite AI Chief of Staff. Be concise, professional, and helpful.",
            temperature=0.7,
        )

        # Save
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"daily_{date_str}.md"
        with open(self.output_dir / filename, "w", encoding="utf-8") as f:
            f.write(briefing)

        # Also save as latest
        with open(self.output_dir / "latest.md", "w", encoding="utf-8") as f:
            f.write(briefing)

        return briefing


if __name__ == "__main__":
    agent = BriefingAgent()
    report = agent.generate_briefing()
    print("\n--- DAILY BRIEFING ---\n")
    print(report)
