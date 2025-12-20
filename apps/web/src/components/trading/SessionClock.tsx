"use client";

import { useState, useEffect } from "react";

interface Session {
  name: string;
  start: number; // UTC hour
  end: number; // UTC hour
  color: string;
  active: boolean;
}

const sessions: Session[] = [
  { name: "Sydney", start: 21, end: 6, color: "bg-blue-500", active: false },
  { name: "Tokyo", start: 0, end: 9, color: "bg-red-500", active: false },
  { name: "London", start: 7, end: 16, color: "bg-amber-500", active: false },
  { name: "New York", start: 12, end: 21, color: "bg-green-500", active: false },
];

function getActiveSessions(hour: number): string[] {
  return sessions
    .filter((s) => {
      if (s.start < s.end) {
        return hour >= s.start && hour < s.end;
      } else {
        // Overnight session (e.g., Sydney 21:00 - 06:00)
        return hour >= s.start || hour < s.end;
      }
    })
    .map((s) => s.name);
}

export function SessionClock() {
  const [time, setTime] = useState(new Date());
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const interval = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  if (!mounted) {
    return (
      <div className="flex items-center gap-4 px-4 py-2 rounded-xl bg-white/5 border border-white/10">
        <div className="w-24 h-6 bg-white/10 rounded animate-pulse" />
      </div>
    );
  }

  const utcHour = time.getUTCHours();
  const activeSessions = getActiveSessions(utcHour);

  const formatTime = (date: Date, tz: string) => {
    return date.toLocaleTimeString("en-US", {
      timeZone: tz,
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  };

  return (
    <div className="flex items-center gap-4 px-4 py-2 rounded-xl bg-white/5 border border-white/10">
      {/* Current Times */}
      <div className="flex items-center gap-3 text-xs">
        <div className="text-center">
          <div className="text-white/40">UTC</div>
          <div className="text-white font-mono">{formatTime(time, "UTC")}</div>
        </div>
        <div className="w-px h-6 bg-white/10" />
        <div className="text-center">
          <div className="text-white/40">NY</div>
          <div className="text-white font-mono">{formatTime(time, "America/New_York")}</div>
        </div>
        <div className="w-px h-6 bg-white/10" />
        <div className="text-center">
          <div className="text-white/40">LON</div>
          <div className="text-white font-mono">{formatTime(time, "Europe/London")}</div>
        </div>
      </div>

      {/* Active Sessions */}
      <div className="flex items-center gap-1">
        {sessions.map((session) => {
          const isActive = activeSessions.includes(session.name);
          return (
            <div
              key={session.name}
              className={`px-2 py-1 rounded text-xs font-medium transition-all ${
                isActive
                  ? `${session.color} text-white shadow-lg`
                  : "bg-white/5 text-white/30"
              }`}
              title={session.name}
            >
              {session.name.slice(0, 3).toUpperCase()}
            </div>
          );
        })}
      </div>

      {/* Killzone Indicator */}
      {(utcHour >= 7 && utcHour <= 10) || (utcHour >= 12 && utcHour <= 15) ? (
        <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-red-500/20 border border-red-500/50">
          <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
          <span className="text-xs font-medium text-red-400">KILLZONE</span>
        </div>
      ) : null}
    </div>
  );
}
