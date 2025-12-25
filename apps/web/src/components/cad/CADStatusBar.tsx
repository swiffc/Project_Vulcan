"use client";

import { useEffect, useState } from "react";

interface ConnectionStatus {
  name: string;
  status: "connected" | "disconnected" | "checking";
  version?: string;
}

interface WatcherState {
  is_running: boolean;
  document_name: string | null;
  document_type: string;
  document_path: string | null;
}

export function CADStatusBar() {
  const [connections, setConnections] = useState<ConnectionStatus[]>([
    { name: "Desktop Server", status: "checking" },
    { name: "SolidWorks", status: "checking" },
    { name: "Inventor", status: "checking" },
  ]);
  const [activeJobs, setActiveJobs] = useState(0);
  const [lastCheck, setLastCheck] = useState<Date | null>(null);
  const [watcher, setWatcher] = useState<WatcherState | null>(null);
  const [tailscaleIp, setTailscaleIp] = useState<string | null>(null);

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

          // Phase 24.1: Watcher state for auto-launch
          if (data.watcher) {
            setWatcher(data.watcher);
          }

          // Tailscale connection status
          if (data.tailscale_ip) {
            setTailscaleIp(data.tailscale_ip);
          }
        } else {
          setConnections((prev) => prev.map((c) => ({ ...c, status: "disconnected" as const })));
          setWatcher(null);
        }
      } catch {
        setConnections((prev) => prev.map((c) => ({ ...c, status: "disconnected" as const })));
        setWatcher(null);
      }
    };

    checkConnections();
    const interval = setInterval(checkConnections, 5000); // Check every 5s for real-time updates
    return () => clearInterval(interval);
  }, []);

  const connectedCount = connections.filter((c) => c.status === "connected").length;

  // Document type icon
  const getDocTypeIcon = (type: string) => {
    switch (type) {
      case "part": return "M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4";
      case "assembly": return "M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10";
      case "drawing": return "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z";
      default: return "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z";
    }
  };

  return (
    <div className="bg-black/20 border-b border-white/10 px-6 py-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-6">
          {/* Connection Status */}
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

          {/* Tailscale Status */}
          {tailscaleIp && (
            <div className="flex items-center gap-2 px-2 py-0.5 rounded bg-blue-500/20 border border-blue-500/30">
              <svg className="w-3 h-3 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
              </svg>
              <span className="text-xs text-blue-400">Tailscale</span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-4">
          {/* Active Document (Phase 24.1) */}
          {watcher?.is_running && watcher?.document_name && (
            <div className="flex items-center gap-2 px-3 py-1 rounded-lg bg-white/5 border border-white/10">
              <svg className="w-4 h-4 text-vulcan-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={getDocTypeIcon(watcher.document_type)} />
              </svg>
              <span className="text-sm text-white/80 max-w-[200px] truncate">
                {watcher.document_name}
              </span>
              <span className="text-xs text-white/40 capitalize">
                ({watcher.document_type})
              </span>
            </div>
          )}

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
