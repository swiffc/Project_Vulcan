"use client";

import { Card, CardHeader, CardContent } from "../ui/Card";
import { CircularProgress } from "../ui/Progress";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

// Mock performance data
const equityCurve = [
  { date: "Week 1", equity: 10000 },
  { date: "Week 2", equity: 10250 },
  { date: "Week 3", equity: 10100 },
  { date: "Week 4", equity: 10650 },
  { date: "Week 5", equity: 10400 },
  { date: "Week 6", equity: 11200 },
  { date: "Week 7", equity: 11450 },
  { date: "Week 8", equity: 11800 },
];

const weeklyReturns = [
  { week: "W1", value: 2.5 },
  { week: "W2", value: -1.5 },
  { week: "W3", value: 5.4 },
  { week: "W4", value: -2.3 },
  { week: "W5", value: 7.7 },
  { week: "W6", value: 2.2 },
  { week: "W7", value: 3.1 },
  { week: "W8", value: -0.8 },
];

const stats = {
  totalTrades: 47,
  winRate: 68,
  avgRMultiple: 1.45,
  profitFactor: 2.3,
  maxDrawdown: 5.2,
  totalReturn: 18.0,
  avgWin: 2.1,
  avgLoss: -0.9,
  bestTrade: 4.5,
  worstTrade: -2.0,
  expectancy: 0.84,
  sharpeRatio: 1.8,
};

export function Performance() {
  return (
    <div className="space-y-4 mt-4">
      {/* Key Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <Card>
          <CardContent className="text-center py-4">
            <CircularProgress value={stats.winRate} variant="success" size="sm" />
            <p className="text-xs text-white/50 mt-2">Win Rate</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="text-center py-4">
            <p className="text-2xl font-bold text-green-400">+{stats.totalReturn}%</p>
            <p className="text-xs text-white/50 mt-1">Total Return</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="text-center py-4">
            <p className="text-2xl font-bold text-vulcan-accent">{stats.avgRMultiple}R</p>
            <p className="text-xs text-white/50 mt-1">Avg R-Multiple</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="text-center py-4">
            <p className="text-2xl font-bold text-amber-400">{stats.profitFactor}</p>
            <p className="text-xs text-white/50 mt-1">Profit Factor</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="text-center py-4">
            <p className="text-2xl font-bold text-red-400">-{stats.maxDrawdown}%</p>
            <p className="text-xs text-white/50 mt-1">Max Drawdown</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="text-center py-4">
            <p className="text-2xl font-bold text-white">{stats.totalTrades}</p>
            <p className="text-xs text-white/50 mt-1">Total Trades</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Equity Curve */}
        <Card>
          <CardHeader title="Equity Curve" subtitle="Account balance over time" />
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={equityCurve}>
                <defs>
                  <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#34d399" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="date"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 10 }}
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 10 }}
                  domain={["dataMin - 500", "dataMax + 500"]}
                  tickFormatter={(value) => `$${(value / 1000).toFixed(1)}k`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(30, 27, 75, 0.9)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: "8px",
                    color: "white",
                  }}
                  formatter={(value: number) => [`$${value.toLocaleString()}`, "Equity"]}
                />
                <Area
                  type="monotone"
                  dataKey="equity"
                  stroke="#34d399"
                  strokeWidth={2}
                  fill="url(#colorEquity)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Weekly Returns */}
        <Card>
          <CardHeader title="Weekly Returns" subtitle="R-multiple per week" />
          <CardContent className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weeklyReturns}>
                <XAxis
                  dataKey="week"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 10 }}
                />
                <YAxis
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
                  formatter={(value: number) => [`${value > 0 ? "+" : ""}${value.toFixed(1)}R`, "Return"]}
                />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {weeklyReturns.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.value >= 0 ? "#34d399" : "#f87171"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader title="Win/Loss Stats" />
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-white/50">Average Win</span>
              <span className="text-green-400 font-medium">+{stats.avgWin}R</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/50">Average Loss</span>
              <span className="text-red-400 font-medium">{stats.avgLoss}R</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/50">Best Trade</span>
              <span className="text-green-400 font-medium">+{stats.bestTrade}R</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/50">Worst Trade</span>
              <span className="text-red-400 font-medium">{stats.worstTrade}R</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader title="Risk Metrics" />
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-white/50">Expectancy</span>
              <span className="text-white font-medium">{stats.expectancy}R</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/50">Sharpe Ratio</span>
              <span className="text-white font-medium">{stats.sharpeRatio}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/50">Max Drawdown</span>
              <span className="text-red-400 font-medium">-{stats.maxDrawdown}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/50">Profit Factor</span>
              <span className="text-white font-medium">{stats.profitFactor}</span>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader title="Monthly Breakdown" />
          <CardContent>
            <div className="grid grid-cols-6 gap-2">
              {["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].map((month, i) => {
                const value = i < 8 ? [5.2, 3.1, -1.2, 4.5, 2.8, -0.5, 3.2, 1.8][i] : null;
                return (
                  <div
                    key={month}
                    className={`text-center py-2 rounded-lg ${
                      value === null
                        ? "bg-white/5"
                        : value >= 0
                        ? "bg-green-500/20"
                        : "bg-red-500/20"
                    }`}
                  >
                    <p className="text-xs text-white/50">{month}</p>
                    <p
                      className={`font-medium ${
                        value === null
                          ? "text-white/20"
                          : value >= 0
                          ? "text-green-400"
                          : "text-red-400"
                      }`}
                    >
                      {value !== null ? `${value > 0 ? "+" : ""}${value}%` : "-"}
                    </p>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
