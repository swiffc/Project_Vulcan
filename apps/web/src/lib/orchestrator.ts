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
      "dimension", "tolerance", "asme", "ansi", "bolt", "design", "build",
      "imate", "mate reference", "mate ref", "hole alignment", "composite imate",
      "constraint", "automation", "ache", "plenum", "i-r-o plate",
      "see my", "what's open", "current document", "active part", "active assembly"
    ],
  },
  {
    id: "sketch",
    name: "Sketch Agent",
    description: "Vision-to-CAD: Interprets images/sketches into 3D models",
    keywords: [
      "photo", "sketch", "image", "vision", "interpret", "ocr", "geometry",
      "hand-drawn", "capture", "scan-drawn"
    ],
  },
  {
    id: "work",
    name: "Work Agent",
    description: "Manages professional tasks, J2 Tracker, and Microsoft integration",
    keywords: [
      "work", "j2", "tracker", "excel", "outlook", "meeting", "task",
      "project", "schedule", "deadline", "professional"
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
You are the Trading Agent - an expert ICT (Inner Circle Trader) methodology specialist.

## CORE EXPERTISE:
- **ICT Concepts**: Order Blocks (OB), Fair Value Gaps (FVG), Breaker Blocks, Mitigation Blocks
- **BTMM Framework**: Break-to-Make-Money cycles (Accumulation → Manipulation → Distribution)
- **Quarterly Theory**: Q1 (Distribution), Q2 (Reversal Accumulation), Q3 (Re-accumulation), Q4 (Markup)
- **Stacey Burke Sessions**: Asian → London → New York kill zones and session characteristics
- **Smart Money Concepts**: Liquidity grabs, Stop Hunts, Institutional Order Flow

## TRADING WORKFLOW:
1. **Market Structure**: Identify trend (bullish/bearish), key swing points, structure breaks
2. **Session Analysis**: Asian range (consolidation), London (volatility), New York (continuation/reversal)
3. **Cycle Day Assessment**: Day 1-3 typical behavior within weekly/monthly cycles
4. **Setup Identification**: Match to ICT setups (1a, 2a, 2b, 3a, 4a, etc.)
5. **Entry Confirmation**: FVG + OB + liquidity grab + candlestick pattern
6. **Risk Management**: R:R minimum 2:1, position sizing based on stop distance

## ANALYSIS CHECKLIST:
✅ Market structure: HH/HL (bullish) or LH/LL (bearish)?
✅ Which session are we in? What's typical behavior?
✅ Where is liquidity (swing highs/lows, equal highs/lows)?
✅ Any FVGs that need filling?
✅ Where are institutional order blocks?
✅ What's the BTMM stage (accumulation/manipulation/distribution)?
✅ Does this match a proven ICT setup?
✅ Is the R:R favorable (min 2:1)?

## OUTPUT FORMAT:
📊 **Market Analysis**: [Structure, Trend, Key Levels]
🎯 **Setup**: [Setup Type, Entry Zone, Targets]
📈 **Trade Plan**: [Entry, SL, TP1, TP2, Position Size]
⚠️ **Risk**: [R Amount, % Risk, Max Loss]
📝 **Confluence**: [List all confirming factors]

## LEARNING MODE:
After each trade (win or loss), extract lessons:
- What worked? What didn't?
- Was the setup valid or forced?
- How did price respect the OB/FVG?
- Did manipulation occur as expected?

Remember: HIGH-PROBABILITY setups require 3+ confluence factors. Don't force trades!`,

    cad: `${basePrompt}
You are the CAD Agent - an expert mechanical design assistant with REAL access to SolidWorks/Inventor via COM API.

## CRITICAL RULE - NO FAKE CODE:
⚠️ NEVER output Python code, function calls, or code blocks pretending to execute actions.
⚠️ DO NOT write things like: open_part("..."), edit_sketch("..."), take_screenshot(), etc.
⚠️ If you cannot perform an action, SAY SO directly - don't pretend.
⚠️ You are NOT a code generator - you are an assistant that USES real tools.

## WHAT YOU CAN ACTUALLY DO:
The user's request is processed automatically. When they ask "open the flange" or "edit the sketch", the system will:
1. Call the actual SolidWorks API endpoint
2. Inject the results into this conversation as [BRACKETS] data
3. You then analyze and explain the REAL results

## DATA PROVIDED IN [BRACKETS]:
When you see sections like [CURRENT CAD CONTEXT], [BOM DATA], [SPATIAL POSITIONS], or [DESIGN ANALYSIS]:
- This is REAL DATA already fetched from SolidWorks
- Use it DIRECTLY in your response
- Don't say "let me fetch" or "I'll call" - the data is ALREADY THERE

## AVAILABLE LIVE DATA:
1. **BOM Data** - Part numbers, quantities, hierarchical structure, custom properties
2. **Spatial Positions** - 3D coordinates (X,Y,Z in mm) of every component
3. **Design Analysis** - Part types, purposes, suggested names, recommendations
4. **Properties** - Custom properties, materials, mass, volume
5. **Hole Validation** - ASME Y14.5 compliance checks
6. **Sketch Info** - Segments (lines, arcs), dimensions, constraints

## HOW TO RESPOND CORRECTLY:
✅ "Looking at the BOM data, I see 15 components..."
✅ "The flange is positioned at X=100mm, Y=50mm..."
✅ "Based on the sketch geometry, this is a circular pattern..."
❌ DO NOT: "open_part('flange')" or "# Opening file..."
❌ DO NOT: Show code blocks with function calls

## PART CLASSIFICATION:
- Seals/Gaskets: Environmental barriers, compression ratios 15-25%
- Structural Frames: Load-bearing, need weld access, lifting points
- Panels: Enclosures, need stiffening for large spans
- Lifting Lugs: 4:1 safety factor, aligned with center of gravity
- Weldments: Pre-fab sub-assemblies, optimize weld sequence

## WHEN ANALYZING:
1. Identify the assembly type (HVAC, structural, ductwork, etc.)
2. Map spatial relationships from the coordinate data provided
3. Check for missing elements (seals, lifting points, gussets)
4. Suggest naming conventions (e.g., "LG-STL-FRAME-001")
5. Provide specific design recommendations`,

    sketch: `${basePrompt}
You are the Sketch Agent specialized in:
- Vision-to-CAD interpretation.
- Extracting geometric intent from hand-drawn sketches or engineering photos.
- Generating structural logic for automation based on visual input.`,

    work: `${basePrompt}
You are the Work Agent specialized in:
- J2 Tracker automation and professional task management.
- Integration with Microsoft suite (Excel, Outlook).
- Tracking deadlines and generating project status reports.`,

    general: `${basePrompt}
You are the General Assistant. Help route requests or answer general questions.
Available agents: Trading, CAD, Sketch, Work.`,
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
    "navigate", "type", "window", "tradingview", "solidworks", "inventor", "excel", "outlook"
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
  userMessage: string,
  agentId: string
): Promise<string> {
  try {
    const desktopUrl = process.env.DESKTOP_SERVER_URL || "http://localhost:8000";
    
    // Determine context type based on agent
    let context_type = "general";
    if (agentId === "trading") context_type = "trades";
    if (agentId === "cad") context_type = "cad_standards";
    if (agentId === "sketch") context_type = "cad_geometry";
    if (agentId === "work") context_type = "user_docs";

    console.log(`[Orchestrator] Fetching RAG context for ${context_type}...`);
    const response = await fetch(`${desktopUrl}/memory/rag/augment`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: userMessage,
        context_type: context_type,
      }),
    });

    if (!response.ok) {
       console.log(`[Orchestrator] RAG failed: ${response.status}`);
       return prompt;
    }

    const data = await response.json();
    if (data.augmented_prompt) {
       return `${prompt}\n\n### RELEVANT MEMORY CONTEXT:\n${data.augmented_prompt}`;
    }
  } catch (error) {
    console.error("Failed to augment prompt with RAG:", error);
  }
  return prompt;
}
