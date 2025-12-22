"use client";

import { Plus, Upload, Search, FileText, Box, Download } from "lucide-react";

export default function QuickActions() {
  const actions = [
    { name: "New Part", icon: Plus, color: "emerald" },
    { name: "Import PDF", icon: Upload, color: "blue" },
    { name: "Search Drawings", icon: Search, color: "purple" },
    { name: "Open Assembly", icon: Box, color: "orange" },
    { name: "Export STEP", icon: Download, color: "cyan" },
    { name: "Create BOM", icon: FileText, color: "pink" },
  ];

  const getColorClasses = (color: string) => {
    const colors: any = {
      emerald: "bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30",
      blue: "bg-blue-500/20 text-blue-400 hover:bg-blue-500/30",
      purple: "bg-purple-500/20 text-purple-400 hover:bg-purple-500/30",
      orange: "bg-orange-500/20 text-orange-400 hover:bg-orange-500/30",
      cyan: "bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30",
      pink: "bg-pink-500/20 text-pink-400 hover:bg-pink-500/30",
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="glass-base p-6">
      <h2 className="text-xl font-bold text-white mb-4">Quick Actions</h2>

      <div className="grid grid-cols-2 gap-3">
        {actions.map((action) => {
          const Icon = action.icon;
          return (
            <button
              key={action.name}
              className={`flex flex-col items-center justify-center p-4 rounded-lg transition-all ${getColorClasses(
                action.color
              )}`}
            >
              <Icon className="w-6 h-6 mb-2" />
              <span className="text-sm font-medium">{action.name}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
