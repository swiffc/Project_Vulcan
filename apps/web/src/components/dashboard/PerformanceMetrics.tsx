"use client";

import { Card, CardHeader, CardContent } from "../ui/Card";
import { CircularProgress } from "../ui/Progress";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

// Mock data for charts
const responseTimeData = [
  { name: "Mon", value: 120 },
  { name: "Tue", value: 180 },
  { name: "Wed", value: 150 },
  { name: "Thu", value: 220 },
  { name: "Fri", value: 140 },
  { name: "Sat", value: 100 },
  { name: "Sun", value: 90 },
];

const apiCostData = [
  { name: "Mon", cost: 0.45 },
  { name: "Tue", cost: 0.62 },
  { name: "Wed", cost: 0.38 },
  { name: "Thu", cost: 0.89 },
  { name: "Fri", cost: 0.55 },
  { name: "Sat", cost: 0.22 },
  { name: "Sun", cost: 0.15 },
];

export function PerformanceMetrics() {
  const uptime = 99.8;
  const cacheHitRate = 67;
  const weeklyApiCost = 3.26;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Uptime & Cache Stats */}
      <Card>
        <CardHeader title="System Health" subtitle="Uptime & efficiency" />
        <CardContent className="flex justify-around items-center py-4">
          <div className="text-center">
            <CircularProgress value={uptime} variant="success" label="Uptime" />
          </div>
          <div className="text-center">
            <CircularProgress value={cacheHitRate} variant="info" label="Cache Hit" />
          </div>
        </CardContent>
      </Card>

      {/* API Cost Summary */}
      <Card>
        <CardHeader
          title="API Costs"
          subtitle="This week"
          action={
            <span className="text-lg font-bold text-vulcan-accent">
              ${weeklyApiCost.toFixed(2)}
            </span>
          }
        />
        <CardContent className="h-32">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={apiCostData}>
              <defs>
                <linearGradient id="colorCost" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#818cf8" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#818cf8" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="name"
                axisLine={false}
                tickLine={false}
                tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 10 }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(30, 27, 75, 0.9)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: "8px",
                  color: "white",
                }}
                formatter={(value: number) => [`$${value.toFixed(2)}`, "Cost"]}
              />
              <Area
                type="monotone"
                dataKey="cost"
                stroke="#818cf8"
                strokeWidth={2}
                fill="url(#colorCost)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Response Time Chart */}
      <Card className="md:col-span-2">
        <CardHeader title="Response Time" subtitle="Average latency (ms)" />
        <CardContent className="h-40">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={responseTimeData}>
              <defs>
                <linearGradient id="colorLatency" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#34d399" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="name"
                axisLine={false}
                tickLine={false}
                tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 10 }}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 10 }}
                domain={[0, "auto"]}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(30, 27, 75, 0.9)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: "8px",
                  color: "white",
                }}
                formatter={(value: number) => [`${value}ms`, "Latency"]}
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#34d399"
                strokeWidth={2}
                fill="url(#colorLatency)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
