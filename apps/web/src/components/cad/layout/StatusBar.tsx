"use client";

import { useEffect, useState } from "react";
import { Activity, HardDrive, Cpu } from "lucide-react";

export default function StatusBar() {
  const [stats, setStats] = useState({
    ramUsage: 45,
    gpuUsage: 32,
    tier: "FULL",
    activeJobs: 2,
  });

  return (
    <footer className="glass-base border-t border-white/10 px-6 py-2">
      <div className="flex items-center justify-between text-sm">
        {/* Left: Performance Stats */}
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <HardDrive className="w-4 h-4 text-blue-400" />
            <span className="text-gray-400">RAM:</span>
            <span className="text-white font-medium">{stats.ramUsage}%</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-purple-400" />
            <span className="text-gray-400">GPU:</span>
            <span className="text-white font-medium">{stats.gpuUsage}%</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-emerald-400" />
            <span className="text-gray-400">Tier:</span>
            <span className="text-emerald-400 font-medium">{stats.tier}</span>
          </div>
        </div>

        {/* Right: Active Jobs */}
        <div className="flex items-center space-x-4">
          <span className="text-gray-400">
            Active Jobs: <span className="text-white font-medium">{stats.activeJobs}</span>
          </span>
          
          <div className="w-px h-4 bg-white/20" />
          
          <span className="text-gray-500 text-xs">
            Project Vulcan CAD v1.0 • Phase 16 Complete
          </span>
        </div>
      </div>
    </footer>
  );
}
