"use client";

import { useState, useEffect } from "react";

interface ServerStatus {
  status: "connected" | "disconnected" | "checking";
  tailscaleIp?: string;
}

export function StatusBar() {
  const [serverStatus, setServerStatus] = useState<ServerStatus>({
    status: "checking",
  });

  useEffect(() => {
    const checkServer = async () => {
      try {
        const response = await fetch("/api/desktop/health");
        if (response.ok) {
          const data = await response.json();
          setServerStatus({
            status: "connected",
            tailscaleIp: data.tailscale_ip,
          });
        } else {
          setServerStatus({ status: "disconnected" });
        }
      } catch {
        setServerStatus({ status: "disconnected" });
      }
    };

    checkServer();
    const interval = setInterval(checkServer, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  const statusColors = {
    connected: "bg-vulcan-success",
    disconnected: "bg-vulcan-error",
    checking: "bg-vulcan-warning animate-pulse",
  };

  const statusText = {
    connected: "Desktop Connected",
    disconnected: "Desktop Offline",
    checking: "Checking...",
  };

  return (
    <div className="flex items-center gap-4 text-xs">
      {/* Desktop Server Status */}
      <div className="flex items-center gap-2">
        <span
          className={`w-2 h-2 rounded-full ${statusColors[serverStatus.status]}`}
        />
        <span className="text-white/50">{statusText[serverStatus.status]}</span>
        {serverStatus.tailscaleIp && (
          <span className="text-white/30">({serverStatus.tailscaleIp})</span>
        )}
      </div>

      {/* Time */}
      <div className="text-white/30">
        {new Date().toLocaleDateString("en-US", {
          weekday: "short",
          month: "short",
          day: "numeric",
        })}
      </div>
    </div>
  );
}
