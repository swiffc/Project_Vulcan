# 🔥 PROJECT VULCAN — STRATEGIC UPDATE PLAN

**Document Version**: 1.0  
**Date**: December 20, 2025  
**Purpose**: Bridge current implementation to full PRD vision

---

## 📊 EXECUTIVE SUMMARY

### Current State vs Target State

| Layer | Current State | Target State (PRD) | Gap Level |
|-------|--------------|-------------------|-----------|
| **Interface** | Basic Next.js chat | Vulcan Chat Window with streaming, rich UX | 🟡 Medium |
| **Routing** | Simple orchestrator | CrewAI Task Router | 🔴 Major |
| **Management** | None | System Manager (David's Worker) daemon | 🔴 Missing |
| **Trading Agent** | TypeScript, partial | Full Python LLM strategy engine | 🟡 Medium |
| **CAD Agent** | Minimal src/ only | Full PDF→CAD pipeline with OCR | 🔴 Major |
| **Inspector Bot** | Basic judge.py | Full LLM-as-Judge with reports | 🟡 Medium |
| **MCP Desktop** | ✅ Working | ✅ Working (enhance with more tools) | 🟢 Good |
| **Memory Brain** | controllers/memory.py | MCP MemoryVec RAG server | 🟡 Medium |
| **Google Drive** | None | MCP GDrive Bridge | 🔴 Missing |
| **Metrics/Auth** | None | mcp-metrics + mcp-auth-hub | 🔴 Missing |

---

## 🏗️ PHASE 1: INFRASTRUCTURE FOUNDATION (Week 1)

### 1.1 Restructure Repository

**Current Structure:**
```
Project_Vulcan/
├── agents/
│   ├── trading-agent/     # TypeScript
│   ├── cad-agent/         # Minimal
│   ├── review-agent/      # Python
│   └── briefing-agent/    # Python
├── apps/web/              # Next.js
├── desktop-server/        # Python MCP
└── core/                  # Python
```

**Target Structure:**
```
Project_Vulcan/
├── agents/
│   ├── trading-bot/           # Python (rename + rewrite)
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── strategy_engine.py    # ICT/BTMM/Stacey Burke
│   │   │   ├── chart_analyzer.py
│   │   │   ├── journal.py
│   │   │   └── tradingview.py
│   │   ├── knowledge/
│   │   └── templates/
│   ├── cad-agent-ai/          # Python (rebuild)
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── pdf_parser.py         # OCR pipeline
│   │   │   ├── param_generator.py    # Feature extraction
│   │   │   ├── cad_executor.py       # CAD-MCP bridge
│   │   │   └── ecn_tracker.py        # Revision history
│   │   └── templates/
│   ├── inspector-bot/         # Python (enhance)
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── judge.py              # LLM audit
│   │   │   └── report_generator.py
│   │   └── templates/
│   ├── system-manager/        # NEW - David's Worker
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── scheduler.py          # Job scheduling
│   │   │   ├── backup.py             # Drive sync
│   │   │   ├── health_monitor.py     # Service health
│   │   │   └── metrics_collector.py
│   │   └── config/
│   └── core/                  # Shared libs
│       ├── __init__.py
│       ├── llm.py
│       ├── logging.py
│       └── patterns/
├── apps/
│   └── web/                   # Next.js (enhance)
│       ├── src/
│       │   ├── app/
│       │   │   ├── api/
│       │   │   │   ├── chat/
│       │   │   │   ├── desktop/
│       │   │   │   ├── trading/       # NEW
│       │   │   │   ├── cad/           # NEW
│       │   │   │   └── health/
│       │   │   └── dashboard/         # NEW - metrics UI
│       │   ├── components/
│       │   │   ├── Chat.tsx
│       │   │   ├── Dashboard.tsx      # NEW
│       │   │   └── StatusBar.tsx      # NEW
│       │   └── lib/
│       │       ├── orchestrator.ts    # CrewAI bridge
│       │       └── mcp-client.ts
│       └── package.json
├── mcp-servers/               # NEW - MCP server configs
│   ├── memory-vec/
│   │   ├── config.json
│   │   └── start.sh
│   ├── google-drive/
│   │   ├── config.json
│   │   └── start.sh
│   └── cad-mcp/
│       └── config.json
├── desktop-server/            # Keep + enhance
│   ├── mcp_server.py
│   ├── controllers/
│   │   ├── mouse.py
│   │   ├── keyboard.py
│   │   ├── screen.py
│   │   ├── memory.py          # Enhance for RAG
│   │   ├── recorder.py
│   │   ├── verifier.py
│   │   ├── window.py
│   │   └── ocr.py             # NEW - pytesseract
│   └── com/
│       ├── solidworks.py      # Enhance
│       └── inventor.py        # NEW
├── config/
│   ├── strategies/            # Trading strategies JSON
│   ├── cad-standards/         # GD&T rules
│   └── render.yaml            # Deployment config
├── storage/                   # gitignored
├── docs/
│   ├── prds/
│   │   └── PROJECT-VULCAN-PRD.md
│   └── architecture/
├── CLAUDE.md
├── RULES.md
├── REFERENCES.md
├── task.md
└── README.md
```

### 1.2 Create System Manager Agent

**File: `agents/system-manager/src/scheduler.py`**
```python
"""
System Manager - David's Worker
Background daemon for job scheduling, backups, and health monitoring.
"""

import asyncio
import schedule
from datetime import datetime
from typing import Callable, Dict
import logging

logger = logging.getLogger("system-manager")

class SystemManager:
    def __init__(self):
        self.jobs: Dict[str, Callable] = {}
        self.running = False
        
    def register_job(self, name: str, func: Callable, schedule_expr: str):
        """Register a scheduled job."""
        self.jobs[name] = {"func": func, "schedule": schedule_expr}
        logger.info(f"Registered job: {name} @ {schedule_expr}")
        
    async def run_forever(self):
        """Main daemon loop."""
        self.running = True
        logger.info("System Manager started")
        
        while self.running:
            schedule.run_pending()
            await asyncio.sleep(60)
            
    def stop(self):
        self.running = False
```

### 1.3 Update render.yaml for Multi-Service Deployment

**File: `render.yaml`**
```yaml
services:
  # Web Interface
  - type: web
    name: vulcan-web
    env: node
    rootDir: apps/web
    buildCommand: npm install && npm run build
    startCommand: npm start
    envVars:
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: DESKTOP_SERVER_URL
        sync: false
      - key: TAILSCALE_IP
        sync: false

  # Task Router / Orchestrator
  - type: worker
    name: vulcan-orchestrator
    env: python
    rootDir: agents
    buildCommand: pip install -r requirements.txt
    startCommand: python -m core.orchestrator
    envVars:
      - key: ANTHROPIC_API_KEY
        sync: false

  # System Manager Daemon
  - type: worker
    name: vulcan-system-manager
    env: python
    rootDir: agents/system-manager
    buildCommand: pip install -r requirements.txt
    startCommand: python -m src.main
    envVars:
      - key: GOOGLE_DRIVE_CREDENTIALS
        sync: false

  # Memory Brain Service
  - type: worker
    name: vulcan-memory
    env: python
    rootDir: mcp-servers/memory-vec
    startCommand: python -m mcp_memory_server --port 8770
```

---

## 🏗️ PHASE 2: TRADING BOT UPGRADE (Week 2)

### 2.1 Convert Trading Agent to Python

**Why Python?** Consistency with other agents, better LLM integration, easier MCP client usage.

**File: `agents/trading-bot/src/strategy_engine.py`**
```python
"""
Trading Strategy Engine
Implements ICT, BTMM, Quarterly Theory, and Stacey Burke strategies.
"""

from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone
from typing import Optional, List
import json

class Bias(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"

class SessionPhase(Enum):
    ACCUMULATION = "Q1"      # Structure forming
    MANIPULATION = "Q2"       # Judas swing
    DISTRIBUTION = "Q3"       # Main move
    CONTINUATION = "Q4"       # Manage/exit

@dataclass
class TradeSetup:
    pair: str
    timeframe: str
    setup_type: str
    bias: Bias
    confidence: float
    entry: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    confluence: List[str] = None
    screenshot_path: Optional[str] = None

class StrategyEngine:
    """Core strategy logic for ICT/BTMM/Quarterly Theory."""
    
    def __init__(self, config_path: str = "config/strategies/trading.json"):
        self.config = self._load_config(config_path)
        
    def _load_config(self, path: str) -> dict:
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._default_config()
            
    def _default_config(self) -> dict:
        return {
            "pairs": ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY"],
            "preferred_sessions": ["london", "new_york"],
            "risk_per_trade": 0.01,
            "max_daily_trades": 3
        }
    
    def get_current_phase(self) -> SessionPhase:
        """Determine current market phase based on Quarterly Theory."""
        now = datetime.now(timezone.utc)
        hour = now.hour
        minute = now.minute
        total_minutes = hour * 60 + minute
        
        # London Open = True Open (8:00 UTC)
        london_open = 8 * 60
        minutes_since_open = (total_minutes - london_open + 1440) % 1440
        quarter_duration = 360  # 6 hours
        
        if minutes_since_open < quarter_duration:
            return SessionPhase.ACCUMULATION
        elif minutes_since_open < quarter_duration * 2:
            return SessionPhase.MANIPULATION
        elif minutes_since_open < quarter_duration * 3:
            return SessionPhase.DISTRIBUTION
        else:
            return SessionPhase.CONTINUATION
            
    def get_phase_guidance(self, phase: SessionPhase) -> str:
        """Get action guidance for current phase."""
        guidance = {
            SessionPhase.ACCUMULATION: "Wait for structure. Identify key levels.",
            SessionPhase.MANIPULATION: "Watch for stop hunts. Prepare for reversal.",
            SessionPhase.DISTRIBUTION: "Main move phase. Execute with confluence.",
            SessionPhase.CONTINUATION: "Manage trades. Look for exits."
        }
        return guidance.get(phase, "")
        
    async def analyze_pair(self, pair: str, screenshot_base64: str) -> Optional[TradeSetup]:
        """Analyze a pair using LLM vision + strategy rules."""
        # This would call Claude API with the screenshot
        # Implementation connects to core/llm.py
        pass
```

### 2.2 Trading Bot Memory Integration

**File: `agents/trading-bot/src/journal.py`**
```python
"""
Trade Journal with RAG Memory
Logs trades and provides recall for lessons learned.
"""

import json
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, asdict

@dataclass
class TradeRecord:
    id: str
    pair: str
    session: str
    bias: str
    setup_type: str
    entry: float
    stop_loss: float
    take_profit: float
    result: str  # "win" | "loss" | "breakeven"
    r_multiple: float
    lesson: str
    timestamp: str
    screenshot_path: Optional[str] = None

class TradeJournal:
    """Trade journaling with memory integration."""
    
    def __init__(self, memory_client):
        self.memory = memory_client
        
    async def log_trade(self, trade: TradeRecord) -> str:
        """Log a trade to memory for future recall."""
        # Store in vector memory for RAG
        embedding_text = f"""
        Trade: {trade.pair} {trade.bias} {trade.setup_type}
        Result: {trade.result} ({trade.r_multiple}R)
        Lesson: {trade.lesson}
        Session: {trade.session}
        """
        
        await self.memory.store(
            key=f"trade:{trade.id}",
            content=embedding_text,
            metadata=asdict(trade)
        )
        
        return trade.id
        
    async def search_similar_trades(self, query: str, limit: int = 5) -> List[TradeRecord]:
        """Search past trades for similar setups."""
        results = await self.memory.search(query, limit=limit)
        return [TradeRecord(**r.metadata) for r in results]
        
    async def get_weekly_stats(self) -> dict:
        """Get statistics for the current week."""
        # Query memory for this week's trades
        trades = await self.memory.query(
            filter={"timestamp": {"$gte": self._week_start()}}
        )
        
        wins = sum(1 for t in trades if t.result == "win")
        losses = sum(1 for t in trades if t.result == "loss")
        total_r = sum(t.r_multiple for t in trades)
        
        return {
            "total_trades": len(trades),
            "wins": wins,
            "losses": losses,
            "win_rate": wins / len(trades) if trades else 0,
            "total_r": total_r,
            "avg_r": total_r / len(trades) if trades else 0
        }
```

---

## 🏗️ PHASE 3: CAD AGENT AI BUILD (Weeks 3-4)

### 3.1 PDF Parser with OCR

**File: `agents/cad-agent-ai/src/pdf_parser.py`**
```python
"""
PDF Parser for CAD Drawings
Extracts dimensions, GD&T, and part information from multi-page PDFs.
"""

import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import re
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Dimension:
    value: float
    unit: str
    tolerance_plus: Optional[float] = None
    tolerance_minus: Optional[float] = None
    gdt_symbol: Optional[str] = None

@dataclass
class DrawingPage:
    page_number: int
    part_name: str
    part_number: str
    revision: str
    dimensions: List[Dimension]
    material: Optional[str] = None
    notes: List[str] = None

class PDFParser:
    """Parse engineering drawings from PDF."""
    
    def __init__(self, dpi: int = 300):
        self.dpi = dpi
        self.dimension_pattern = re.compile(
            r'(\d+\.?\d*)\s*(mm|in|")?'
        )
        
    def parse_pdf(self, pdf_path: str) -> List[DrawingPage]:
        """Parse all pages of a PDF drawing."""
        images = convert_from_path(pdf_path, dpi=self.dpi)
        pages = []
        
        for i, image in enumerate(images):
            page = self._parse_page(image, i + 1)
            pages.append(page)
            
        return pages
        
    def _parse_page(self, image: Image, page_num: int) -> DrawingPage:
        """Parse a single page."""
        # OCR the entire page
        text = pytesseract.image_to_string(image)
        
        # Extract title block info
        part_name = self._extract_part_name(text)
        part_number = self._extract_part_number(text)
        revision = self._extract_revision(text)
        
        # Extract dimensions
        dimensions = self._extract_dimensions(text)
        
        # Extract notes
        notes = self._extract_notes(text)
        
        return DrawingPage(
            page_number=page_num,
            part_name=part_name,
            part_number=part_number,
            revision=revision,
            dimensions=dimensions,
            notes=notes
        )
        
    def _extract_dimensions(self, text: str) -> List[Dimension]:
        """Extract dimensional values from OCR text."""
        dimensions = []
        matches = self.dimension_pattern.findall(text)
        
        for value, unit in matches:
            dim = Dimension(
                value=float(value),
                unit=unit or "mm"
            )
            dimensions.append(dim)
            
        return dimensions
```

### 3.2 CAD Executor with ECN Tracking

**File: `agents/cad-agent-ai/src/cad_executor.py`**
```python
"""
CAD Executor
Bridges to CAD-MCP for SolidWorks/Inventor execution.
Tracks all modifications with ECN history.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import json

@dataclass
class ECNRecord:
    ecn_number: str
    description: str
    changes: List[str]
    applied_to: List[str]  # Part numbers affected
    timestamp: str
    applied_by: str = "vulcan-cad-agent"

class CADExecutor:
    """Execute CAD operations via MCP and track changes."""
    
    def __init__(self, mcp_client, memory_client):
        self.mcp = mcp_client
        self.memory = memory_client
        
    async def create_part(self, drawing: 'DrawingPage') -> dict:
        """Create a part from parsed drawing data."""
        # Build feature parameters
        params = self._build_feature_params(drawing)
        
        # Execute via CAD-MCP
        result = await self.mcp.call_tool(
            "cad.create_part",
            {
                "name": drawing.part_name,
                "number": drawing.part_number,
                "features": params
            }
        )
        
        # Log to memory
        await self._log_creation(drawing, result)
        
        return result
        
    async def apply_ecn(self, ecn: ECNRecord) -> dict:
        """Apply an ECN to parts, tracking cumulative history."""
        # Get prior ECN history from memory
        history = await self._get_ecn_history(ecn.applied_to)
        
        # Apply changes
        results = []
        for part_number in ecn.applied_to:
            result = await self.mcp.call_tool(
                "cad.modify_part",
                {
                    "part_number": part_number,
                    "changes": ecn.changes,
                    "ecn_number": ecn.ecn_number
                }
            )
            results.append(result)
            
        # Update ECN history in memory
        await self._store_ecn(ecn, history)
        
        return {
            "ecn": ecn.ecn_number,
            "parts_updated": len(results),
            "cumulative_ecns": len(history) + 1
        }
        
    async def _get_ecn_history(self, part_numbers: List[str]) -> List[ECNRecord]:
        """Retrieve ECN history for parts from memory."""
        history = []
        for pn in part_numbers:
            records = await self.memory.search(
                f"ecn:{pn}",
                filter={"type": "ecn"}
            )
            history.extend(records)
        return history
        
    async def _store_ecn(self, ecn: ECNRecord, prior_history: List[ECNRecord]):
        """Store ECN record with cumulative context."""
        embedding_text = f"""
        ECN: {ecn.ecn_number}
        Description: {ecn.description}
        Changes: {', '.join(ecn.changes)}
        Parts: {', '.join(ecn.applied_to)}
        Prior ECNs: {len(prior_history)}
        """
        
        await self.memory.store(
            key=f"ecn:{ecn.ecn_number}",
            content=embedding_text,
            metadata={
                "type": "ecn",
                **ecn.__dict__
            }
        )
```

---

## 🏗️ PHASE 4: INSPECTOR BOT & MEMORY BRAIN (Week 5)

### 4.1 Enhanced Inspector Bot

**File: `agents/inspector-bot/src/judge.py`**
```python
"""
Inspector Bot - LLM-as-a-Judge
Reviews agent outputs and generates quality reports.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class GradeLevel(Enum):
    EXCELLENT = "A"
    GOOD = "B"
    ACCEPTABLE = "C"
    NEEDS_WORK = "D"
    FAILED = "F"

@dataclass
class AuditResult:
    item_id: str
    item_type: str  # "trade" | "cad_part" | "assembly"
    grade: GradeLevel
    score: float  # 0-100
    findings: List[str]
    recommendations: List[str]
    timestamp: str

class InspectorBot:
    """LLM-powered audit agent."""
    
    def __init__(self, llm_client):
        self.llm = llm_client
        
    async def audit_trade(self, trade_record: dict) -> AuditResult:
        """Audit a trading decision."""
        prompt = f"""
        Analyze this trade and grade it:
        
        Pair: {trade_record['pair']}
        Setup: {trade_record['setup_type']}
        Bias: {trade_record['bias']}
        Result: {trade_record['result']} ({trade_record['r_multiple']}R)
        Lesson: {trade_record['lesson']}
        
        Grade on:
        1. Setup quality (was the entry valid?)
        2. Risk management (proper SL/TP?)
        3. Lesson quality (did they learn correctly?)
        
        Respond with JSON: {{"grade": "A-F", "score": 0-100, "findings": [...], "recommendations": [...]}}
        """
        
        response = await self.llm.complete(prompt)
        return self._parse_audit_response(response, trade_record['id'], "trade")
        
    async def audit_cad_assembly(self, assembly_data: dict) -> AuditResult:
        """Audit a CAD assembly against standards."""
        prompt = f"""
        Review this CAD assembly:
        
        Parts: {assembly_data['parts']}
        Assembly: {assembly_data['assembly_file']}
        Mass: {assembly_data.get('mass_properties', {})}
        
        Check:
        1. All parts present and mated correctly
        2. Mass properties reasonable
        3. Drawing standards followed
        
        Respond with JSON: {{"grade": "A-F", "score": 0-100, "findings": [...], "recommendations": [...]}}
        """
        
        response = await self.llm.complete(prompt)
        return self._parse_audit_response(response, assembly_data['job_id'], "assembly")
```

### 4.2 Memory Brain MCP Server

**File: `mcp-servers/memory-vec/config.json`**
```json
{
  "server_name": "vulcan-memory-brain",
  "port": 8770,
  "storage": {
    "type": "chromadb",
    "path": "/data/vulcan-memory",
    "collection": "vulcan_knowledge"
  },
  "embedding": {
    "model": "text-embedding-3-small",
    "dimensions": 1536
  },
  "tools": [
    {
      "name": "memory_store",
      "description": "Store a memory with embedding"
    },
    {
      "name": "memory_search",
      "description": "Semantic search over memories"
    },
    {
      "name": "memory_query",
      "description": "Structured query with filters"
    }
  ],
  "resources": [
    {
      "uri": "vulcan://memory/stats",
      "description": "Memory usage statistics"
    }
  ]
}
```

---

## 🏗️ PHASE 5: SYSTEM MANAGER & GOOGLE DRIVE (Week 6)

### 5.1 Google Drive MCP Bridge

**File: `mcp-servers/google-drive/config.json`**
```json
{
  "server_name": "vulcan-gdrive-bridge",
  "port": 8771,
  "credentials_path": "/secrets/gdrive-credentials.json",
  "default_folder": "Vulcan_Exports",
  "tools": [
    {
      "name": "drive_upload",
      "description": "Upload file to Google Drive"
    },
    {
      "name": "drive_download",
      "description": "Download file from Google Drive"
    },
    {
      "name": "drive_list",
      "description": "List files in a folder"
    },
    {
      "name": "drive_sync",
      "description": "Sync local directory to Drive folder"
    }
  ]
}
```

### 5.2 System Manager Full Implementation

**File: `agents/system-manager/src/main.py`**
```python
"""
System Manager - David's Worker
Main entry point for the background daemon.
"""

import asyncio
import schedule
from datetime import datetime
import logging

from .scheduler import SystemManager
from .backup import BackupService
from .health_monitor import HealthMonitor
from .metrics_collector import MetricsCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("system-manager")

async def main():
    """Initialize and run System Manager."""
    manager = SystemManager()
    backup = BackupService()
    health = HealthMonitor()
    metrics = MetricsCollector()
    
    # Register scheduled jobs
    
    # Daily: Backup to Drive at 2 AM
    schedule.every().day.at("02:00").do(backup.run_daily_backup)
    
    # Hourly: Health check all services
    schedule.every().hour.do(health.check_all_services)
    
    # Every 5 min: Collect metrics
    schedule.every(5).minutes.do(metrics.collect)
    
    # Weekly: Generate performance report (Friday 5 PM)
    schedule.every().friday.at("17:00").do(manager.generate_weekly_report)
    
    logger.info("🚀 System Manager started")
    logger.info(f"📅 Registered {len(schedule.get_jobs())} scheduled jobs")
    
    # Run forever
    await manager.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🏗️ PHASE 6: WEB INTERFACE UPGRADE (Week 6)

### 6.1 Enhanced Chat with Streaming

**File: `apps/web/src/components/Chat.tsx`** (Updated)
```tsx
'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  status?: '📊' | '📈' | '✅' | '🛑';
  attachments?: { type: string; url: string }[];
}

export default function VulcanChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);

    // Stream response
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: input }),
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let assistantContent = '';

    setMessages(prev => [...prev, { role: 'assistant', content: '', status: '📊' }]);

    while (reader) {
      const { done, value } = await reader.read();
      if (done) break;

      assistantContent += decoder.decode(value);
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: 'assistant',
          content: assistantContent,
          status: '📊'
        };
        return updated;
      });
    }

    // Mark complete
    setMessages(prev => {
      const updated = [...prev];
      updated[updated.length - 1].status = '✅';
      return updated;
    });
    setIsStreaming(false);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-700 flex items-center justify-between">
        <h1 className="text-xl font-bold">🔥 Vulcan AI</h1>
        <div className="flex gap-2">
          <span className="px-2 py-1 bg-green-600 rounded text-sm">Desktop: Online</span>
          <span className="px-2 py-1 bg-blue-600 rounded text-sm">Memory: Active</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-lg ${
              msg.role === 'user' ? 'bg-blue-600' : 'bg-gray-700'
            }`}>
              {msg.status && <span className="mr-2">{msg.status}</span>}
              {msg.content}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask Vulcan anything..."
            className="flex-1 p-3 bg-gray-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isStreaming}
          />
          <button
            onClick={sendMessage}
            disabled={isStreaming}
            className="px-6 py-3 bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isStreaming ? '...' : 'Send'}
          </button>
        </div>
        {/* Quick Actions */}
        <div className="flex gap-2 mt-2">
          <button className="px-3 py-1 bg-gray-700 rounded text-sm hover:bg-gray-600">
            📈 Scan EUR/USD
          </button>
          <button className="px-3 py-1 bg-gray-700 rounded text-sm hover:bg-gray-600">
            🏗️ Build Assembly
          </button>
          <button className="px-3 py-1 bg-gray-700 rounded text-sm hover:bg-gray-600">
            📊 Weekly Report
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

## 📋 MIGRATION CHECKLIST

### Week 1: Infrastructure
- [ ] Restructure repository to new layout
- [ ] Create `agents/system-manager/` skeleton
- [ ] Update `render.yaml` for multi-service
- [ ] Set up `mcp-servers/` configurations
- [ ] Update `requirements.txt` files

### Week 2: Trading Bot
- [ ] Convert TypeScript agents to Python
- [ ] Implement `strategy_engine.py`
- [ ] Implement `journal.py` with memory integration
- [ ] Create trading strategy JSON configs
- [ ] Test TradingView control via MCP

### Week 3-4: CAD Agent AI
- [ ] Build `pdf_parser.py` with OCR
- [ ] Build `param_generator.py`
- [ ] Build `cad_executor.py` with ECN tracking
- [ ] Integrate with CAD-MCP
- [ ] Test end-to-end PDF → Part flow

### Week 5: Inspector & Memory
- [ ] Enhance `judge.py` for comprehensive audits
- [ ] Set up Memory Brain MCP server
- [ ] Connect all agents to memory
- [ ] Test RAG recall functionality

### Week 6: System Manager & Web
- [ ] Implement System Manager daemon
- [ ] Set up Google Drive MCP bridge
- [ ] Upgrade web interface with streaming
- [ ] Build metrics dashboard
- [ ] Full end-to-end testing

### Week 7: Testing & Documentation
- [ ] Unit tests for all agents
- [ ] Integration tests for workflows
- [ ] Performance/stress tests
- [ ] Update README, RULES, CLAUDE.md
- [ ] Create deployment runbook

---

## 🎯 SUCCESS CRITERIA

| Metric | Target |
|--------|--------|
| Chat response time | < 5 seconds |
| Trading Bot PDF reports | Daily/weekly automated |
| CAD reconstruction accuracy | > 90% |
| Inspector Bot coherence | Clear problems & fixes |
| System Manager uptime | > 7 days continuous |
| Memory recall relevance | > 85% accuracy |

---

## 📚 REFERENCES

- MCP Docs: https://modelcontextprotocol.org
- CAD-MCP: https://github.com/daobataotie/CAD-MCP
- Anthropic MCP Servers: https://github.com/anthropics/mcp-servers
- Render IaC: https://render.com/docs/infrastructure-as-code

---

**Next Step**: Confirm this plan, then I'll begin implementing Phase 1 by pushing the restructured repository.
