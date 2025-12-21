import { NextResponse } from "next/server";

// In-memory metrics store (replace with Redis in production)
let metricsStore = {
  calls: {
    total: 0,
    cacheHits: 0,
    haiku: 0,
    sonnet: 0,
    opus: 0,
  },
  tokens: {
    input: 0,
    output: 0,
    cached: 0,
  },
  costs: {
    actual: 0,
    wouldBe: 0,
  },
  lastReset: new Date().toISOString(),
};

// Pricing per million tokens
const PRICING = {
  "claude-3-haiku-20240307": { input: 0.25, output: 1.25 },
  "claude-3-5-sonnet-20241022": { input: 3.0, output: 15.0 },
  "claude-sonnet-4-20250514": { input: 3.0, output: 15.0 },
  "claude-3-opus-20240229": { input: 15.0, output: 75.0 },
};

export async function GET() {
  // Calculate savings
  const savings = calculateSavings();

  return NextResponse.json({
    today: {
      totalCalls: metricsStore.calls.total,
      cacheHits: metricsStore.calls.cacheHits,
      tokensUsed: metricsStore.tokens.input + metricsStore.tokens.output,
      estimatedCost: metricsStore.costs.actual,
      savedAmount: metricsStore.costs.wouldBe - metricsStore.costs.actual,
    },
    routing: {
      haiku: metricsStore.calls.haiku,
      sonnet: metricsStore.calls.sonnet,
      opus: metricsStore.calls.opus,
    },
    savings: savings,
    lastReset: metricsStore.lastReset,
  });
}

export async function POST(request: Request) {
  try {
    const data = await request.json();
    const { event, model, tokensIn, tokensOut, cached, cacheHit } = data;

    if (event === "llm_call") {
      metricsStore.calls.total++;

      // Track cache hits
      if (cacheHit) {
        metricsStore.calls.cacheHits++;
      }

      // Track model usage
      if (model?.includes("haiku")) {
        metricsStore.calls.haiku++;
      } else if (model?.includes("opus")) {
        metricsStore.calls.opus++;
      } else {
        metricsStore.calls.sonnet++;
      }

      // Track tokens
      metricsStore.tokens.input += tokensIn || 0;
      metricsStore.tokens.output += tokensOut || 0;
      metricsStore.tokens.cached += cached || 0;

      // Calculate costs
      const pricing = PRICING[model as keyof typeof PRICING] || PRICING["claude-sonnet-4-20250514"];
      const actualCost =
        ((tokensIn || 0) / 1_000_000) * pricing.input +
        ((tokensOut || 0) / 1_000_000) * pricing.output;

      // What it would cost with Sonnet (baseline)
      const baselineCost =
        ((tokensIn || 0) / 1_000_000) * 3.0 +
        ((tokensOut || 0) / 1_000_000) * 15.0;

      metricsStore.costs.actual += actualCost;
      metricsStore.costs.wouldBe += cacheHit ? baselineCost : baselineCost;
    }

    if (event === "reset") {
      metricsStore = {
        calls: { total: 0, cacheHits: 0, haiku: 0, sonnet: 0, opus: 0 },
        tokens: { input: 0, output: 0, cached: 0 },
        costs: { actual: 0, wouldBe: 0 },
        lastReset: new Date().toISOString(),
      };
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json({ error: "Invalid request" }, { status: 400 });
  }
}

function calculateSavings() {
  const total = metricsStore.calls.total || 1;
  const cacheHitRate = (metricsStore.calls.cacheHits / total) * 100;

  // Calculate routing savings (Haiku vs Sonnet)
  const haikuRatio = metricsStore.calls.haiku / total;
  const routingSavings = haikuRatio * 92; // Haiku is 92% cheaper

  // Token optimization estimate (20-40%)
  const tokenSavings = 30;

  // Prompt caching estimate
  const cachedRatio = metricsStore.tokens.cached / (metricsStore.tokens.input || 1);
  const promptCachingSavings = cachedRatio * 90;

  // Total savings
  const totalCostReduction =
    metricsStore.costs.wouldBe > 0
      ? ((metricsStore.costs.wouldBe - metricsStore.costs.actual) /
          metricsStore.costs.wouldBe) *
        100
      : 0;

  return {
    redisCache: Math.min(cacheHitRate, 100),
    modelRouting: Math.min(routingSavings, 92),
    tokenOptimization: tokenSavings,
    promptCaching: Math.min(promptCachingSavings, 90),
    totalPercent: Math.min(Math.max(totalCostReduction, 0), 95),
  };
}
