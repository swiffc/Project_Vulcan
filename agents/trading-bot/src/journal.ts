/**
 * Trade Journal - Logging and memory integration
 *
 * Logs trades to the memory system for RAG retrieval
 * and weekly review generation.
 */

import { TradeResult } from "./index";

export class TradeJournal {
  private baseUrl: string;

  constructor(desktopServerUrl: string = "http://localhost:8000") {
    this.baseUrl = desktopServerUrl;
  }

  /**
   * Log a trade to memory
   */
  async logTrade(result: TradeResult): Promise<string> {
    try {
      const response = await fetch(`${this.baseUrl}/memory/trades/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pair: result.setup.pair,
          setup_type: result.setup.setup_type,
          rationale: result.setup.confluence.join(", "),
          result: result.result,
          r_multiple: result.r_multiple,
          lesson: result.lesson,
          day: this.getDayOfWeek(),
          session: this.getCurrentSession(),
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data.trade_id || "unknown";
    } catch (error) {
      console.error("Failed to log trade:", error);
      return `local_${Date.now()}`;
    }
  }

  /**
   * Log a lesson learned
   */
  async logLesson(
    content: string,
    category: string = "general",
    sourceTrade?: string
  ): Promise<string> {
    try {
      const response = await fetch(`${this.baseUrl}/memory/lessons/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content,
          category,
          source_trade: sourceTrade,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data.lesson_id || "unknown";
    } catch (error) {
      console.error("Failed to log lesson:", error);
      return `local_${Date.now()}`;
    }
  }

  /**
   * Search past trades
   */
  async searchTrades(query: string, limit: number = 5): Promise<any[]> {
    try {
      const response = await fetch(`${this.baseUrl}/memory/search/trades`, {
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
   * Search lessons
   */
  async searchLessons(query: string, limit: number = 5): Promise<any[]> {
    try {
      const response = await fetch(`${this.baseUrl}/memory/search/lessons`, {
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
   * Get weekly review
   */
  async getWeeklyReview(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/memory/review/weekly`, {
        method: "GET",
      });

      if (!response.ok) return null;

      return await response.json();
    } catch {
      return null;
    }
  }

  /**
   * Get augmented prompt with trade context
   */
  async getAugmentedPrompt(query: string): Promise<string> {
    try {
      const response = await fetch(`${this.baseUrl}/memory/rag/augment`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query,
          context_type: "trades",
        }),
      });

      if (!response.ok) return query;

      const data = await response.json();
      return data.augmented_prompt || query;
    } catch {
      return query;
    }
  }

  /**
   * Format trade for display
   */
  formatTradeEntry(result: TradeResult): string {
    const emoji = result.result === "win" ? "✅" : "❌";
    const rSign = result.r_multiple >= 0 ? "+" : "";

    return `## ${emoji} Trade: ${result.setup.pair}

**Setup:** ${result.setup.setup_type}
**Bias:** ${result.setup.bias}
**Result:** ${result.result.toUpperCase()} (${rSign}${result.r_multiple}R)
**Confidence:** ${result.setup.confidence}%

### Confluence
${result.setup.confluence.map((c) => `- ${c}`).join("\n")}

### Lesson Learned
${result.lesson}

---
*${result.timestamp.toISOString()}*`;
  }

  private getDayOfWeek(): string {
    const days = [
      "Sunday",
      "Monday",
      "Tuesday",
      "Wednesday",
      "Thursday",
      "Friday",
      "Saturday",
    ];
    return days[new Date().getUTCDay()];
  }

  private getCurrentSession(): string {
    const hour = new Date().getUTCHours();

    if (hour >= 0 && hour < 8) return "Asian";
    if (hour >= 8 && hour < 12) return "London";
    if (hour >= 12 && hour < 17) return "New York";
    if (hour >= 17 && hour < 21) return "NY PM";
    return "Asian";
  }
}
