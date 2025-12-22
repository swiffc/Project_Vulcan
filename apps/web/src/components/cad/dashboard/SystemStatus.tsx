"use client";

import { CheckCircle2, AlertCircle, XCircle } from "lucide-react";

export default function SystemStatus() {
  const systems = [
    { name: "SolidWorks 2024", status: "connected", version: "SP 3.0" },
    { name: "Inventor 2024", status: "disconnected", version: "Update 2" },
    { name: "Desktop Server", status: "connected", latency: "12ms" },
    { name: "Vector Memory", status: "connected", docs: "1,247" },
    { name: "Google Drive", status: "synced", lastSync: "2 min ago" },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "connected":
      case "synced":
        return <CheckCircle2 className="w-5 h-5 text-emerald-400" />;
      case "disconnected":
        return <XCircle className="w-5 h-5 text-red-400" />;
      default:
        return <AlertCircle className="w-5 h-5 text-yellow-400" />;
    }
  };

  return (
    <div className="glass-base p-6">
      <h2 className="text-xl font-bold text-white mb-4">System Status</h2>
      
      <div className="space-y-3">
        {systems.map((system) => (
          <div
            key={system.name}
            className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
          >
            <div className="flex items-center space-x-3">
              {getStatusIcon(system.status)}
              <div>
                <p className="text-white font-medium">{system.name}</p>
                <p className="text-sm text-gray-400">
                  {system.version || system.latency || system.lastSync || system.docs}
                </p>
              </div>
            </div>
            
            <span
              className={`px-3 py-1 rounded-full text-xs font-medium ${
                system.status === "connected" || system.status === "synced"
                  ? "bg-emerald-500/20 text-emerald-400"
                  : system.status === "disconnected"
                  ? "bg-red-500/20 text-red-400"
                  : "bg-yellow-500/20 text-yellow-400"
              }`}
            >
              {system.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
