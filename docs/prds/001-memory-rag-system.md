# PRD-001: Memory & RAG System

**Status**: Draft
**Author**: Project Vulcan
**Created**: 2024-12-19
**Priority**: High

---

## 1. Overview

Add persistent memory and semantic search capabilities to Project Vulcan, enabling:

- **Vector Memory**: Semantic search over lessons and journal entries
- **RAG over Journals**: Retrieve relevant past context before answering
- **Automated Reviews**: Weekly agent summarizes performance and updates strategies

---

## 2. Problem Statement

Currently, the agent has no memory of past trades, lessons learned, or performance patterns. Users must manually recall and reference past experiences.

**Pain Points:**

- "What trades did I take where I ignored Burke confirmation?" → No way to search
- "What's my win rate on Wednesday Q3 setups?" → Manual calculation
- "Update my strategy based on last month's performance" → Manual review

---

## 3. Proposed Solution

### 3.1 Vector Database (Chroma - Free, Local)

Use Chroma for local vector storage (no API costs, no data leaving machine).

```text
┌─────────────────────────────────────────────────────────────────┐
│                      MEMORY LAYER                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │   Chroma    │    │  Embedding  │    │   SQLite    │        │
│  │  (Vectors)  │◄───│   Model     │◄───│  (Metadata) │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│         │                                      │               │
│         └──────────────┬───────────────────────┘               │
│                        ▼                                        │
│              ┌─────────────────┐                               │
│              │   RAG Engine    │                               │
│              │ (Query + Rank)  │                               │
│              └────────┬────────┘                               │
│                       │                                         │
└───────────────────────┼─────────────────────────────────────────┘
                        ▼
              ┌─────────────────┐
              │   Agent Query   │
              │ "Find all trades│
              │  where I ignored│
              │  Burke..."      │
              └─────────────────┘
```

### 3.2 Data to Index

| Collection | Source | Fields to Embed |
|------------|--------|-----------------|
| `trades` | Trade journal entries | Setup type, rationale, lessons |
| `lessons` | Extracted lessons | Lesson text, context |
| `analyses` | Daily/weekly analyses | Market bias, key levels |
| `cad_jobs` | CAD work logs | Commands, parameters, outcomes |

### 3.3 RAG Pipeline

1. **Ingest**: After each trade/CAD job, embed and store
2. **Query**: Convert user question to embedding
3. **Retrieve**: Find top-k similar entries
4. **Augment**: Add retrieved context to prompt
5. **Generate**: Answer with context

---

## 4. Technical Specification

### 4.1 New Files

```text
Project_Vulcan/
├── core/
│   └── memory/
│       ├── __init__.py
│       ├── chroma_store.py      # Vector DB operations (~100 lines)
│       ├── embeddings.py        # Embedding model (~50 lines)
│       ├── rag_engine.py        # RAG pipeline (~100 lines)
│       └── ingest.py            # Data ingestion (~80 lines)
├── agents/
│   └── review-agent/
│       ├── src/
│       │   └── weekly_review.py # Weekly performance review (~150 lines)
│       └── templates/
│           └── weekly_summary.md
└── config/
    └── memory.yaml              # Memory configuration
```

### 4.2 Dependencies

Add to `desktop-server/requirements.txt`:

```txt
# Vector Memory & RAG
chromadb==0.4.22
sentence-transformers==2.2.2
```

### 4.3 Chroma Store API

```python
# core/memory/chroma_store.py

class VulcanMemory:
    """Vector memory store using Chroma."""

    def __init__(self, persist_dir: str = "./storage/chroma"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.trades = self.client.get_or_create_collection("trades")
        self.lessons = self.client.get_or_create_collection("lessons")

    def add_trade(self, trade_id: str, content: str, metadata: dict):
        """Add a trade to memory."""
        self.trades.add(
            ids=[trade_id],
            documents=[content],
            metadatas=[metadata]
        )

    def search_trades(self, query: str, n_results: int = 5) -> list:
        """Semantic search over trades."""
        return self.trades.query(
            query_texts=[query],
            n_results=n_results
        )

    def add_lesson(self, lesson_id: str, content: str, metadata: dict):
        """Add a lesson learned."""
        self.lessons.add(
            ids=[lesson_id],
            documents=[content],
            metadatas=[metadata]
        )

    def search_lessons(self, query: str, n_results: int = 5) -> list:
        """Find relevant lessons."""
        return self.lessons.query(
            query_texts=[query],
            n_results=n_results
        )
```

### 4.4 RAG Engine

```python
# core/memory/rag_engine.py

class RAGEngine:
    """Retrieval-Augmented Generation for Vulcan."""

    def __init__(self, memory: VulcanMemory):
        self.memory = memory

    def augment_prompt(self, user_query: str, context_type: str = "all") -> str:
        """Retrieve relevant context and augment the prompt."""
        context_parts = []

        if context_type in ["all", "trades"]:
            trades = self.memory.search_trades(user_query, n_results=3)
            if trades["documents"][0]:
                context_parts.append("## Relevant Past Trades\n" +
                    "\n".join(trades["documents"][0]))

        if context_type in ["all", "lessons"]:
            lessons = self.memory.search_lessons(user_query, n_results=3)
            if lessons["documents"][0]:
                context_parts.append("## Relevant Lessons\n" +
                    "\n".join(lessons["documents"][0]))

        if context_parts:
            return f"""## Retrieved Context
{chr(10).join(context_parts)}

## User Query
{user_query}"""
        return user_query
```

### 4.5 Weekly Review Agent

```python
# agents/review-agent/src/weekly_review.py

class WeeklyReviewAgent:
    """Automated weekly performance review."""

    def __init__(self, memory: VulcanMemory):
        self.memory = memory

    def generate_review(self, week_start: str, week_end: str) -> dict:
        """Generate weekly performance summary."""
        # Query all trades for the week
        trades = self.memory.search_trades(
            f"trades from {week_start} to {week_end}",
            n_results=50
        )

        # Calculate statistics
        stats = self._calculate_stats(trades)

        # Extract patterns
        patterns = self._identify_patterns(trades)

        # Generate recommendations
        recommendations = self._generate_recommendations(stats, patterns)

        return {
            "period": f"{week_start} to {week_end}",
            "statistics": stats,
            "patterns": patterns,
            "recommendations": recommendations
        }

    def update_strategy_json(self, recommendations: list):
        """Update strategy.json based on recommendations."""
        # Load current strategy
        # Apply recommendations
        # Save updated strategy
        pass
```

---

## 5. Example Queries

| Query | Expected Behavior |
|-------|-------------------|
| "Find all trades where I ignored Burke confirmation" | Search `lessons` + `trades` for "Burke", "ignored", "confirmation" |
| "What's my win rate on Wednesday setups?" | Filter `trades` by day, calculate win/loss ratio |
| "Show me similar setups to current GBP/USD chart" | Embed current analysis, find similar past analyses |
| "What lessons did I learn about Q2 manipulation?" | Search `lessons` for "Q2", "manipulation", "Judas swing" |

---

## 6. Configuration

```yaml
# config/memory.yaml

memory:
  provider: chroma
  persist_dir: ./storage/chroma

  collections:
    trades:
      embedding_model: all-MiniLM-L6-v2
      max_results: 10
    lessons:
      embedding_model: all-MiniLM-L6-v2
      max_results: 5
    analyses:
      embedding_model: all-MiniLM-L6-v2
      max_results: 5

  rag:
    context_window: 3
    include_metadata: true

  review:
    schedule: "0 18 * * 5"  # Every Friday at 6 PM
    auto_update_strategy: false  # Require approval
```

---

## 7. Integration Points

### 7.1 Trade Journal → Memory

After each trade is logged:

```python
# In trading-agent after trade completion
memory.add_trade(
    trade_id=f"trade_{timestamp}",
    content=f"{setup_type} on {pair}: {rationale}. Result: {result}. Lesson: {lesson}",
    metadata={
        "pair": pair,
        "setup_type": setup_type,
        "result": "win" | "loss",
        "day": "Wednesday",
        "session": "London",
        "r_multiple": 2.5
    }
)
```

### 7.2 Agent Query → RAG

Before any agent responds:

```python
# In orchestrator
augmented_query = rag_engine.augment_prompt(user_query)
response = agent.process(augmented_query)
```

### 7.3 Weekly Review → Strategy Update

```python
# Scheduled task (Friday 6 PM)
review = review_agent.generate_review(week_start, week_end)
# HITL: Present recommendations, await approval
if user_approved:
    review_agent.update_strategy_json(review["recommendations"])
```

---

## 8. Success Metrics

| Metric | Target |
|--------|--------|
| Semantic search accuracy | >80% relevant results in top-3 |
| Query latency | <500ms |
| Memory footprint | <500MB for 1 year of data |
| Weekly review generation | <30 seconds |

---

## 9. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Embedding model too large | Use `all-MiniLM-L6-v2` (22MB, fast) |
| Chroma data corruption | Daily backup to `storage/backups/` |
| Wrong context retrieved | Include confidence scores, allow filtering |
| Strategy auto-update errors | HITL approval required (Rule 8) |

---

## 10. Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Chroma (local)** | Free, private, fast | Limited scale | ✅ Selected |
| Pinecone (cloud) | Managed, scalable | API costs, data leaves machine | ❌ |
| Weaviate | Open source, powerful | Complex setup | ❌ |
| SQLite FTS5 | Simple | No semantic search | ❌ |

---

## 11. Implementation Plan

See `task.md` for detailed task breakdown.

**Phases:**

1. **Phase 1**: Chroma setup + basic storage
2. **Phase 2**: RAG engine + query augmentation
3. **Phase 3**: Weekly review agent
4. **Phase 4**: Integration with existing agents
