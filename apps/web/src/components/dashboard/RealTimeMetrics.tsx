"use client";

import { useEffect, useState, useRef } from "react";
import { Card, CardHeader, CardContent } from "../ui/Card";

interface MetricPoint {
  time: string;
  value: number;
}

interface LiveMetrics {
  responseTime: MetricPoint[];
  tokensPerMinute: MetricPoint[];
  activeUsers: number;
  queueDepth: number;
  uptime: string;
}

export function RealTimeMetrics() {
  const [metrics, setMetrics] = useState<LiveMetrics>({
    responseTime: [],
    tokensPerMinute: [],
    activeUsers: 1,
    queueDepth: 0,
    uptime: "0d 0h 0m",
  });
  const [currentResponseTime, setCurrentResponseTime] = useState(0);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    // Simulate real-time metrics (replace with actual API)
    const generateMetrics = () => {
      const now = new Date().toLocaleTimeString();
      const newResponseTime = Math.random() * 500 + 200;
      const newTokens = Math.floor(Math.random() * 1000 + 500);

      setCurrentResponseTime(newResponseTime);
      setMetrics((prev) => ({
        ...prev,
        responseTime: [...prev.responseTime.slice(-19), { time: now, value: newResponseTime }],
        tokensPerMinute: [...prev.tokensPerMinute.slice(-19), { time: now, value: newTokens }],
        activeUsers: Math.floor(Math.random() * 3) + 1,
        queueDepth: Math.floor(Math.random() * 5),
      }));
    };

    generateMetrics();
    const interval = setInterval(generateMetrics, 3000);
    return () => clearInterval(interval);
  }, []);

  // Draw sparkline
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || metrics.responseTime.length < 2) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const data = metrics.responseTime.map((p) => p.value);
    const max = Math.max(...data) * 1.1;
    const min = Math.min(...data) * 0.9;

    ctx.clearRect(0, 0, width, height);

    // Draw gradient fill
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, "rgba(99, 102, 241, 0.3)");
    gradient.addColorStop(1, "rgba(99, 102, 241, 0)");

    ctx.beginPath();
    ctx.moveTo(0, height);

    data.forEach((value, i) => {
      const x = (i / (data.length - 1)) * width;
      const y = height - ((value - min) / (max - min)) * height;
      ctx.lineTo(x, y);
    });

    ctx.lineTo(width, height);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();

    // Draw line
    ctx.beginPath();
    data.forEach((value, i) => {
      const x = (i / (data.length - 1)) * width;
      const y = height - ((value - min) / (max - min)) * height;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });

    ctx.strokeStyle = "#6366f1";
    ctx.lineWidth = 2;
    ctx.stroke();

    // Draw current point
    const lastX = width;
    const lastY = height - ((data[data.length - 1] - min) / (max - min)) * height;
    ctx.beginPath();
    ctx.arc(lastX, lastY, 4, 0, Math.PI * 2);
    ctx.fillStyle = "#6366f1";
    ctx.fill();
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 2;
    ctx.stroke();
  }, [metrics.responseTime]);

  return (
    <Card>
      <CardHeader
        title="Real-Time Performance"
        subtitle="Live system metrics"
        icon={
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-400 to-violet-600 flex items-center justify-center animate-pulse">
            <span className="text-sm">📊</span>
          </div>
        }
      />
      <CardContent>
        {/* Response Time Chart */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-white/40">Response Time</span>
            <span className="text-sm font-bold text-indigo-400">
              {currentResponseTime.toFixed(0)}ms
            </span>
          </div>
          <canvas
            ref={canvasRef}
            width={300}
            height={60}
            className="w-full h-15 rounded-lg bg-white/5"
          />
        </div>

        {/* Live Stats */}
        <div className="grid grid-cols-3 gap-2">
          <LiveStat
            icon="👤"
            label="Active"
            value={metrics.activeUsers.toString()}
            pulse
          />
          <LiveStat
            icon="📋"
            label="Queue"
            value={metrics.queueDepth.toString()}
            color={metrics.queueDepth > 3 ? "text-amber-400" : "text-white"}
          />
          <LiveStat
            icon="⏱️"
            label="Uptime"
            value="99.9%"
          />
        </div>

        {/* Status Indicators */}
        <div className="mt-4 pt-4 border-t border-white/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs text-white/60">All systems operational</span>
            </div>
            <span className="text-xs text-white/30">
              Last update: {new Date().toLocaleTimeString()}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function LiveStat({
  icon,
  label,
  value,
  color = "text-white",
  pulse = false,
}: {
  icon: string;
  label: string;
  value: string;
  color?: string;
  pulse?: boolean;
}) {
  return (
    <div className="p-2 rounded-lg bg-white/5 text-center">
      <span className={pulse ? "animate-pulse" : ""}>{icon}</span>
      <p className={`text-lg font-bold ${color}`}>{value}</p>
      <p className="text-xs text-white/40">{label}</p>
    </div>
  );
}
