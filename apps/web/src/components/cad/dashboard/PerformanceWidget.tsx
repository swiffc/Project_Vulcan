"use client";

import { HardDrive, Cpu, Gauge } from "lucide-react";
import { useEffect, useState } from "react";

export default function PerformanceWidget() {
  const [metrics, setMetrics] = useState({
    ram: 45,
    gpu: 32,
    tier: "FULL",
    parts: 1847,
  });

  return (
    <div className="glass-base p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white">Performance</h2>
        <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-sm font-medium">
          {metrics.tier} Mode
        </span>
      </div>

      <div className="space-y-4">
        {/* RAM Usage */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <HardDrive className="w-4 h-4 text-blue-400" />
              <span className="text-gray-300 text-sm">RAM Usage</span>
            </div>
            <span className="text-white font-medium">{metrics.ram}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${metrics.ram}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-1">7.2 GB / 16 GB</p>
        </div>

        {/* GPU Usage */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <Cpu className="w-4 h-4 text-purple-400" />
              <span className="text-gray-300 text-sm">GPU Usage</span>
            </div>
            <span className="text-white font-medium">{metrics.gpu}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${metrics.gpu}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-1">RTX 3060 • 2.5 GB / 8 GB</p>
        </div>

        {/* Part Count */}
        <div className="flex items-center justify-between p-3 rounded-lg bg-white/5">
          <div className="flex items-center space-x-2">
            <Gauge className="w-4 h-4 text-emerald-400" />
            <span className="text-gray-300 text-sm">Assembly Parts</span>
          </div>
          <span className="text-white font-medium">{metrics.parts.toLocaleString()}</span>
        </div>

        {/* Tier Warning (if needed) */}
        {metrics.ram > 75 && (
          <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
            <p className="text-yellow-400 text-sm">
              ⚠️ High RAM usage detected. Consider switching to REDUCED mode.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
