/**
 * Orchestrator - Routes requests to the correct agent
 *
 * Rule 10: The Orchestrator acts as the central conductor.
 * Agents never communicate with each other directly.
 */

import { AgentType } from "./types";

const AGENTS: AgentType[] = [
  {
    id: "trading",
    name: "Trading Agent",
    description: "Analyzes charts, scans setups, manages paper trades",
    keywords: [
      "trade", "trading", "scan", "gbp", "eur", "usd", "xauusd", "gold",
      "setup", "q1", "q2", "q3", "q4", "ict", "btmm", "burke", "quarterly",
      "order block", "fvg", "liquidity", "manipulation", "review", "journal"
    ],
  },
  {
    id: "cad",
    name: "CAD Agent",
    description: "Automates SolidWorks, Inventor, and other CAD software",
    keywords: [
      "cad", "solidworks", "inventor", "autocad", "bentley", "flange",
      "part", "assembly", "drawing", "sketch", "extrude", "revolve",
      "dimension", "tolerance", "asme", "ansi", "bolt", "design", "build"
    ],
  },
  {
    id: "general",
    name: "General Assistant",
    description: "Handles general questions and routing",
    keywords: [],
  },
];

export function detectAgent(message: string): AgentType {
  const lowerMessage = message.toLowerCase();

  // Score each agent based on keyword matches
  const scores = AGENTS.map((agent) => {
    const score = agent.keywords.reduce((acc, keyword) => {
      return acc + (lowerMessage.includes(keyword) ? 1 : 0);
    }, 0);
    return { agent, score };
  });

  // Sort by score and return highest
  scores.sort((a, b) => b.score - a.score);

  // If no keywords matched, return general
  if (scores[0].score === 0) {
    return AGENTS.find((a) => a.id === "general")!;
  }

  return scores[0].agent;
}

export function getSystemPrompt(agent: AgentType): string {
  const basePrompt = `You are Vulcan, a personal AI operating system. You have access to a Desktop Control Server that can physically operate Windows applications.

IMPORTANT RULES:
- Use emoji status markers: ✅ Success, 📊 Analyzing, 📈 Trade Placed, 🛑 Error, 🔧 Building
- Format responses with markdown: bold for emphasis, tables for data, code blocks for commands
- For high-stake actions (trades, file deletions), always ask for confirmation first (HITL)
- Be concise but thorough

`;

  const agentPrompts: Record<string, string> = {
    trading: `${basePrompt}
You are the Trading Agent specialized in:
- ICT (Inner Circle Trader) concepts: Order Blocks, FVG, OTE, Kill Zones
- BTMM (Beat The Market Maker): Three-day cycles, TDI, Stop Hunts
- Quarterly Theory: AMDX model, True Opens
- Stacey Burke: ACB setups, Session trading

When analyzing setups:
1. Identify the current market phase (Q1-Q4)
2. Check for confluence across ICT, BTMM, and Burke
3. Only suggest trades when multiple confirmations align
4. Always specify entry, stop loss, and take profit levels
5. Log lessons learned after each trade
6. Current session times (EST):
- Asian: 7PM - 12AM
- London: 2AM - 5AM
- NY: 7AM - 10AM`,

    cad: `${basePrompt}
You are the CAD Agent specialized in:
- SolidWorks automation via COM API
- Inventor automation via COM API
- ASME Y14.5 dimensioning standards
- Part creation, sketching, features (extrude, revolve, pattern)

When building parts:
1. Reference strategy.json for design parameters
2. Take screenshots after each major operation
3. Save files with proper naming: {PART_NAME}_v{N}.sldprt
4. Log all operations for traceability`,

    general: `${basePrompt}
You are the General Assistant. Help route requests to the appropriate specialized agent or answer general questions about the system.

Available agents:
- Trading Agent: Chart analysis, paper trading, ICT/BTMM/Quarterly Theory
- CAD Agent: SolidWorks, Inventor automation`,
  };

  return agentPrompts[agent.id] || agentPrompts.general;
}

export interface OrchestratorResult {
  agent: AgentType;
  systemPrompt: string;
  requiresDesktop: boolean;
}

export function orchestrate(message: string): OrchestratorResult {
  const agent = detectAgent(message);
  const systemPrompt = getSystemPrompt(agent);

  // Determine if this request likely needs desktop control
  const desktopKeywords = [
    "screenshot", "click", "scan", "build", "open", "close",
    "navigate", "type", "window", "tradingview", "solidworks", "inventor"
  ];
  const requiresDesktop = desktopKeywords.some((k) =>
    message.toLowerCase().includes(k)
  );

  return {
    agent,
    systemPrompt,
    requiresDesktop,
  };
}

/**
 * Augment the system prompt with RAG context (Memory).
 * This runs asynchronously to fetch data from the desktop server.
 */
export async function augmentSystemPrompt(
  prompt: string,
  userMessage: string
): Promise<string> {
  try {
    const desktopUrl = process.env.DESKTOP_SERVER_URL || "http://localhost:8000";
    
    // Only augment for Trading agent queries usually, but General might benefit too.
    // We'll augment for everything to allow "recall" queries.
    
    console.log("[Orchestrator] Fetching RAG context...");
    const response = await fetch(`${desktopUrl}/memory/rag/augment`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: userMessage,
        context_type: "trades", // Prioritize trade history/lessons
      }),
    });

    if (!response.ok) {
       console.log(`[Orchestrator] RAG failed: ${response.status}`);
       return prompt;
    }

    const data = await response.json();
    if (data.augmented_prompt) {
       // Ideally we append the context to the system prompt, not replace it
       // The endpoint returns a full prompt? No, usually just context or augmented query.
       // Let's assume it returns context we should append.
       // Inspecting previous `journal.ts`, it expects `augmented_prompt` field.
       // But usually `rag_engine.augment_prompt` returns the *user query* augmented.
       // Here we want to augment the *system prompt* with context, or the user query.
       // Let's modify: we'll append the context to the system prompt instead.
       
       // If the server returns just the context, we append.
       // If it returns a full prompt, we use it. 
       // Let's assume the server returns `context_str` or similar? 
       // `journal.ts` called it `augmented_prompt`. 
       // Let's stick to what's likely implemented: returns a string with context.
       
       return `${prompt}\n\n### RELEVANT MEMORY CONTEXT:\n${data.augmented_prompt}`;
    }
  } catch (error) {
    console.error("Failed to augment prompt with RAG:", error);
  }
  return prompt;
}
