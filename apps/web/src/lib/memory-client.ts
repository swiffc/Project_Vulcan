/**
 * Memory Client - Proxy to Python Memory/RAG System
 *
 * Communicates with the Desktop Server's memory endpoints
 * for context retrieval and trade logging.
 */

const DESKTOP_SERVER_URL =
  process.env.DESKTOP_SERVER_URL || "http://localhost:8000";

export interface TradeData {
  pair: string;
  setup_type: string;
  rationale: string;
  result: "win" | "loss";
  r_multiple: number;
  lesson: string;
  day?: string;
  session?: string;
}

export interface SearchResult {
  id: string;
  content: string;
  metadata: Record<string, any>;
  distance?: number;
}

/**
 * Search trades by natural language query
 */
export async function searchTrades(
  query: string,
  limit: number = 5
): Promise<SearchResult[]> {
  try {
    const response = await fetch(`${DESKTOP_SERVER_URL}/memory/search/trades`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, n_results: limit }),
    });

    if (!response.ok) return [];
    const data = await response.json();
    return data.results || [];
  } catch {
    return [];
  }
}

/**
 * Search lessons by natural language query
 */
export async function searchLessons(
  query: string,
  limit: number = 5
): Promise<SearchResult[]> {
  try {
    const response = await fetch(`${DESKTOP_SERVER_URL}/memory/search/lessons`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, n_results: limit }),
    });

    if (!response.ok) return [];
    const data = await response.json();
    return data.results || [];
  } catch {
    return [];
  }
}

/**
 * Get augmented prompt with RAG context
 */
export async function getAugmentedPrompt(
  query: string,
  contextType: "all" | "trades" | "lessons" = "all"
): Promise<string> {
  try {
    const response = await fetch(`${DESKTOP_SERVER_URL}/memory/rag/augment`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, context_type: contextType }),
    });

    if (!response.ok) return query;
    const data = await response.json();
    return data.augmented_prompt || query;
  } catch {
    return query;
  }
}

/**
 * Log a trade to memory
 */
export async function logTrade(trade: TradeData): Promise<string | null> {
  try {
    const response = await fetch(`${DESKTOP_SERVER_URL}/memory/trades/add`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(trade),
    });

    if (!response.ok) return null;
    const data = await response.json();
    return data.trade_id || null;
  } catch {
    return null;
  }
}

/**
 * Log a lesson to memory
 */
export async function logLesson(
  content: string,
  category: string = "general",
  sourceTrade?: string
): Promise<string | null> {
  try {
    const response = await fetch(`${DESKTOP_SERVER_URL}/memory/lessons/add`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        content,
        category,
        source_trade: sourceTrade,
      }),
    });

    if (!response.ok) return null;
    const data = await response.json();
    return data.lesson_id || null;
  } catch {
    return null;
  }
}

/**
 * Get weekly review
 */
export async function getWeeklyReview(): Promise<any> {
  try {
    const response = await fetch(`${DESKTOP_SERVER_URL}/memory/review/weekly`, {
      method: "GET",
    });

    if (!response.ok) return null;
    return await response.json();
  } catch {
    return null;
  }
}
