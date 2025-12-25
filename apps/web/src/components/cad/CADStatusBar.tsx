"use client";

import { useEffect, useState } from "react";

interface ConnectionStatus {
  name: string;
  status: "connected" | "disconnected" | "checking";
  version?: string;
}

export function CADStatusBar() {
  const [connections, setConnections] = useState<ConnectionStatus[]>([
    { name: "Desktop Server", status: "checking" },
    { name: "SolidWorks", status: "checking" },
    { name: "Inventor", status: "checking" },
  ]);
  const [activeJobs, setActiveJobs] = useState(0);
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  useEffect(() => {
    const checkConnections = async () => {
      try {
        const res = await fetch("/api/desktop/health", { cache: "no-store" });
        setLastCheck(new Date());

        if (res.ok) {
          const data = await res.json();

          // Parse various response formats from desktop server
          const isDesktopConnected = data.status === "ok" || data.status === "healthy" || res.ok;
          const swConnected = data.solidworks?.connected ?? data.cad?.solidworks ?? false;
          const invConnected = data.inventor?.connected ?? data.cad?.inventor ?? false;
          const swVersion = data.solidworks?.version ?? data.cad?.sw_version ?? "";
          const invVersion = data.inventor?.version ?? data.cad?.inv_version ?? "";

          setConnections([
            {
              name: "Desktop Server",
              status: isDesktopConnected ? "connected" : "disconnected",
              version: data.version || "1.0"
            },
            {
              name: "SolidWorks",
              status: swConnected ? "connected" : "disconnected",
              version: swVersion
            },
            {
              name: "Inventor",
              status: invConnected ? "connected" : "disconnected",
              version: invVersion
            },
          ]);
          setActiveJobs(data.activeJobs ?? data.active_jobs ?? data.queue_depth ?? 0);
        } else {
          setConnections((prev) => prev.map((c) => ({ ...c, status: "disconnected" as const })));
        }
      } catch {
        setConnections((prev) => prev.map((c) => ({ ...c, status: "disconnected" as const })));
      }
    };

    checkConnections();
    const interval = setInterval(checkConnections, 15000); // Check every 15s
    return () => clearInterval(interval);
  }, []);

  const connectedCount = connections.filter((c) => c.status === "connected").length;

  return (
    <div className="bg-black/20 border-b border-white/10 px-6 py-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-6">
          {connections.map((conn) => (
            <div key={conn.name} className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  conn.status === "connected"
                    ? "bg-emerald-400"
                    : conn.status === "checking"
                    ? "bg-amber-400 animate-pulse"
                    : "bg-red-400"
                }`}
              />
              <span className="text-sm text-white/70">{conn.name}</span>
              {conn.version && (
                <span className="text-xs text-white/30">v{conn.version}</span>
              )}
            </div>
          ))}
        </div>

        <div className="flex items-center gap-4">
          {activeJobs > 0 && (
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-vulcan-accent/20 text-vulcan-accent text-sm">
              <div className="w-2 h-2 rounded-full bg-vulcan-accent animate-pulse" />
              {activeJobs} active job{activeJobs !== 1 ? "s" : ""}
            </div>
          )}
          <div className="text-sm text-white/50">
            {connectedCount}/{connections.length} connected
          </div>
        </div>
      </div>
    </div>
  );
}
