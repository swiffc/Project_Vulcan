"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardContent } from "../ui/Card";

interface CostMetrics {
  today: {
    totalCalls: number;
    cacheHits: number;
    tokensUsed: number;
    estimatedCost: number;
    savedAmount: number;
  };
  routing: {
    haiku: number;
    sonnet: number;
    opus: number;
  };
  savings: {
    redisCache: number;
    modelRouting: number;
    tokenOptimization: number;
    promptCaching: number;
    totalPercent: number;
  };
}

const defaultMetrics: CostMetrics = {
  today: {
    totalCalls: 0,
    cacheHits: 0,
    tokensUsed: 0,
    estimatedCost: 0,
    savedAmount: 0,
  },
  routing: { haiku: 0, sonnet: 0, opus: 0 },
  savings: {
    redisCache: 0,
    modelRouting: 0,
    tokenOptimization: 0,
    promptCaching: 0,
    totalPercent: 0,
  },
};

export function CostDashboard() {
  const [metrics, setMetrics] = useState<CostMetrics>(defaultMetrics);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await fetch("/api/metrics/cost", { cache: "no-store" });
        if (res.ok) {
          const data = await res.json();
          setMetrics(data);
        }
      } catch (error) {
        console.error("Failed to fetch cost metrics:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 60000); // Update every minute
    return () => clearInterval(interval);
  }, []);

  const cacheHitRate = metrics.today.totalCalls > 0
    ? ((metrics.today.cacheHits / metrics.today.totalCalls) * 100).toFixed(1)
    : "0";

  return (
    <Card className="glass-accent">
      <CardHeader
        title="Cost Optimization"
        subtitle="ULTIMATE Stack Active"
        icon={
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-green-600 flex items-center justify-center">
            <span className="text-sm">$</span>
          </div>
        }
      />
      <CardContent>
        {/* Savings Overview */}
        <div className="mb-4 p-4 rounded-xl bg-gradient-to-br from-emerald-500/20 to-green-600/10 border border-emerald-500/30">
          <div className="flex items-center justify-between mb-2">
            <span className="text-emerald-300 text-sm font-medium">Total Savings</span>
            <span className="text-2xl font-bold text-emerald-400">
              {metrics.savings.totalPercent.toFixed(0)}%
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-white/60 text-xs">Today saved:</span>
            <span className="text-emerald-300 font-medium">
              ${metrics.today.savedAmount.toFixed(4)}
            </span>
          </div>
        </div>

        {/* Savings Breakdown */}
        <div className="space-y-3 mb-4">
          <SavingsBar
            label="Redis Cache"
            value={metrics.savings.redisCache}
            color="from-blue-400 to-blue-600"
            icon="💾"
          />
          <SavingsBar
            label="Model Routing"
            value={metrics.savings.modelRouting}
            color="from-purple-400 to-purple-600"
            icon="🎯"
          />
          <SavingsBar
            label="Token Optimization"
            value={metrics.savings.tokenOptimization}
            color="from-amber-400 to-orange-600"
            icon="✂️"
          />
          <SavingsBar
            label="Prompt Caching"
            value={metrics.savings.promptCaching}
            color="from-pink-400 to-rose-600"
            icon="🔥"
          />
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-3">
          <StatBox
            label="API Calls"
            value={metrics.today.totalCalls.toString()}
            subtext={`${cacheHitRate}% cache hit`}
          />
          <StatBox
            label="Tokens Used"
            value={formatNumber(metrics.today.tokensUsed)}
            subtext={`$${metrics.today.estimatedCost.toFixed(4)}`}
          />
        </div>

        {/* Model Distribution */}
        <div className="mt-4 pt-4 border-t border-white/10">
          <p className="text-xs text-white/40 mb-2">Model Distribution</p>
          <div className="flex gap-2">
            <ModelChip
              name="Haiku"
              count={metrics.routing.haiku}
              color="bg-green-500/20 text-green-300"
            />
            <ModelChip
              name="Sonnet"
              count={metrics.routing.sonnet}
              color="bg-blue-500/20 text-blue-300"
            />
            <ModelChip
              name="Opus"
              count={metrics.routing.opus}
              color="bg-purple-500/20 text-purple-300"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function SavingsBar({
  label,
  value,
  color,
  icon,
}: {
  label: string;
  value: number;
  color: string;
  icon: string;
}) {
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="text-white/60 flex items-center gap-1">
          <span>{icon}</span> {label}
        </span>
        <span className="text-white/80 font-medium">{value.toFixed(0)}%</span>
      </div>
      <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
        <div
          className={`h-full bg-gradient-to-r ${color} rounded-full transition-all duration-500`}
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
    </div>
  );
}

function StatBox({
  label,
  value,
  subtext,
}: {
  label: string;
  value: string;
  subtext: string;
}) {
  return (
    <div className="p-3 rounded-lg bg-white/5 border border-white/10">
      <p className="text-xs text-white/40 mb-1">{label}</p>
      <p className="text-lg font-bold text-white">{value}</p>
      <p className="text-xs text-white/30">{subtext}</p>
    </div>
  );
}

function ModelChip({
  name,
  count,
  color,
}: {
  name: string;
  count: number;
  color: string;
}) {
  return (
    <div className={`px-2 py-1 rounded-full text-xs font-medium ${color}`}>
      {name}: {count}
    </div>
  );
}

function formatNumber(num: number): string {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
}
