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
      "constraint", "automation", "ache", "plenum", "i-r-o plate"
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
You are the Trading Agent specialized in:
- ICT concepts (Order Blocks, FVG) and BTMM cycles.
- Quarterly Theory and Stacey Burke session setups.

When analyzing setups, follow checking steps for confluence and log lessons.`,

    cad: `${basePrompt}
You are the CAD Agent specialized in:
- SolidWorks/Inventor automation via COM API.
- ASME Y14.5 standards and technical drawing validation.
- iMate and Mate Reference automation for hole alignment.

Reference strategy files for dimensions and take screenshots for every operation.

IMATE/MATE REFERENCE AUTOMATION:
- "add iMates for assembly <filepath>" - Auto-create Insert, Mate, and Composite iMates for hole alignment in Inventor
- "create mate references for assembly <filepath>" - Auto-create Concentric + Coincident Mate References in SolidWorks
- "verify hole alignment for assembly <filepath>" - Check alignment and report mis-aligned holes (±1/16" tolerance)
- Supports both Inventor (iMates) and SolidWorks (Mate References)
- Composite iMates group multiple hole iMates for bolt patterns`,

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
