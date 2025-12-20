"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardContent } from "../ui/Card";
import { StatusDot } from "../ui/Badge";

interface ServiceStatus {
  name: string;
  status: "online" | "offline" | "checking";
  latency?: number;
  details?: string;
}

export function SystemStatus() {
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: "Desktop Server", status: "checking", details: "TradingView/SolidWorks control" },
    { name: "Memory Brain", status: "checking", details: "Redis + ChromaDB" },
    { name: "Trading Agent", status: "checking", details: "ICT/BTMM analysis" },
    { name: "CAD Agent", status: "checking", details: "PDF → Part automation" },
  ]);

  useEffect(() => {
    const checkServices = async () => {
      // Check Desktop Server
      try {
        const start = Date.now();
        const res = await fetch("/api/desktop/health", { cache: "no-store" });
        const latency = Date.now() - start;
        setServices((prev) =>
          prev.map((s) =>
            s.name === "Desktop Server"
              ? { ...s, status: res.ok ? "online" : "offline", latency }
              : s
          )
        );
      } catch {
        setServices((prev) =>
          prev.map((s) =>
            s.name === "Desktop Server" ? { ...s, status: "offline" } : s
          )
        );
      }

      // Check Main API (proxy for Memory Brain)
      try {
        const start = Date.now();
        const res = await fetch("/api/health", { cache: "no-store" });
        const latency = Date.now() - start;

        // Update Memory Brain and Agents based on main API
        setServices((prev) =>
          prev.map((s) => {
            if (s.name === "Memory Brain") {
              return { ...s, status: res.ok ? "online" : "offline", latency };
            }
            if (s.name === "Trading Agent" || s.name === "CAD Agent") {
              return { ...s, status: res.ok ? "online" : "offline" };
            }
            return s;
          })
        );
      } catch {
        setServices((prev) =>
          prev.map((s) =>
            s.name !== "Desktop Server" ? { ...s, status: "offline" } : s
          )
        );
      }
    };

    checkServices();
    const interval = setInterval(checkServices, 30000);
    return () => clearInterval(interval);
  }, []);

  const onlineCount = services.filter((s) => s.status === "online").length;

  return (
    <Card>
      <CardHeader
        title="System Status"
        subtitle={`${onlineCount}/${services.length} services online`}
      />
      <CardContent className="grid grid-cols-2 gap-3">
        {services.map((service) => (
          <div
            key={service.name}
            className="flex items-center justify-between p-3 rounded-lg bg-white/5"
          >
            <div className="flex items-center gap-3">
              <StatusDot status={service.status} />
              <div>
                <p className="text-sm font-medium text-white">{service.name}</p>
                <p className="text-xs text-white/40">{service.details}</p>
              </div>
            </div>
            {service.latency && (
              <span className="text-xs text-white/30">{service.latency}ms</span>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
