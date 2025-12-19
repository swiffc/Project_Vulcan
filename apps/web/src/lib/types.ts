export type MessageRole = "user" | "assistant";
export type MessageStatus = "streaming" | "complete" | "error";

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  status: MessageStatus;
  screenshot?: string; // Base64 encoded
}

export interface ChatRequest {
  messages: Array<{
    role: MessageRole;
    content: string;
  }>;
}

export interface AgentType {
  id: "trading" | "cad" | "life" | "general";
  name: string;
  description: string;
  keywords: string[];
}

export interface DesktopAction {
  type: "screenshot" | "click" | "type" | "window";
  params: Record<string, any>;
}

export interface TradeSetup {
  pair: string;
  timeframe: string;
  setup_type: string;
  bias: "bullish" | "bearish" | "neutral";
  confidence: number;
  entry?: number;
  stop_loss?: number;
  take_profit?: number;
}
