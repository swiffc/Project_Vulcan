/**
 * Enhanced Session Clock Component
 * BTMM-aware session tracking with kill zone indicators
 */

"use client";

import { useState, useEffect } from "react";
import type { SessionName } from "@/lib/trading/types";
import { SESSIONS, KILL_ZONES, TRUE_OPENS, SESSION_LABELS } from "@/lib/trading/constants";

interface SessionInfo {
  name: SessionName;
  isActive: boolean;
  isKillZone: boolean;
  progress: number; // 0-100 percentage through session
}

export function EnhancedSessionClock() {
  const [time, setTime] = useState(new Date());
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const interval = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  if (!mounted) {
    return (
      <div className="flex items-center gap-4 px-4 py-2">
        <div className="w-32 h-8 bg-white/10 rounded animate-pulse" />
        <div className="w-48 h-8 bg-white/10 rounded animate-pulse" />
      </div>
    );
  }

  const estTime = getESTTime(time);
  const sessions = getSessionInfo(estTime);
  const activeSession = sessions.find((s) => s.isActive);
  const isInKillZone = sessions.some((s) => s.isKillZone);

  return (
    <div className="flex items-center gap-4">
      {/* Multi-Timezone Clock */}
      <div className="flex items-center gap-3 text-xs">
        <TimeDisplay label="EST" time={formatTime(time, "America/New_York")} isMain />
        <div className="w-px h-6 bg-white/10" />
        <TimeDisplay label="UTC" time={formatTime(time, "UTC")} />
        <div className="w-px h-6 bg-white/10" />
        <TimeDisplay label="LON" time={formatTime(time, "Europe/London")} />
        <div className="hidden lg:block w-px h-6 bg-white/10" />
        <TimeDisplay label="TKY" time={formatTime(time, "Asia/Tokyo")} className="hidden lg:block" />
      </div>

      {/* Session Pills */}
      <div className="flex items-center gap-1.5">
        {sessions.map((session) => (
          <SessionPill
            key={session.name}
            session={session}
            config={SESSIONS[session.name]}
          />
        ))}
      </div>

      {/* Kill Zone / True Open Indicator */}
      {isInKillZone && (
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-trading-bearish/20 border border-trading-bearish/40">
          <div className="w-2 h-2 rounded-full bg-trading-bearish animate-pulse" />
          <span className="text-xs font-bold text-trading-bearish">KILL ZONE</span>
        </div>
      )}

      {/* True Open Countdown */}
      <TrueOpenCountdown estTime={estTime} />
    </div>
  );
}

function TimeDisplay({
  label,
  time,
  isMain = false,
  className = "",
}: {
  label: string;
  time: string;
  isMain?: boolean;
  className?: string;
}) {
  return (
    <div className={`text-center ${className}`}>
      <div className="text-white/40 text-[10px] uppercase tracking-wider">{label}</div>
      <div className={`font-mono ${isMain ? "text-white font-semibold" : "text-white/70"}`}>
        {time}
      </div>
    </div>
  );
}

function SessionPill({
  session,
  config,
}: {
  session: SessionInfo;
  config: { start: string; end: string; color: string };
}) {
  const labelMap: Record<SessionName, string> = {
    asian: "ASIA",
    london: "LDN",
    newyork: "NY",
    gap: "GAP",
  };

  return (
    <div
      className={`relative px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
        session.isActive
          ? session.isKillZone
            ? "bg-trading-bearish/30 text-trading-bearish border border-trading-bearish/50"
            : "text-white border"
          : "bg-white/5 text-white/30 border border-transparent"
      }`}
      style={{
        borderColor: session.isActive && !session.isKillZone ? config.color : undefined,
        backgroundColor: session.isActive && !session.isKillZone ? `${config.color}20` : undefined,
        color: session.isActive && !session.isKillZone ? config.color : undefined,
      }}
      title={`${SESSION_LABELS[session.name]} (${config.start} - ${config.end} EST)`}
    >
      {labelMap[session.name]}

      {/* Progress bar for active session */}
      {session.isActive && (
        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-black/20 rounded-b overflow-hidden">
          <div
            className="h-full transition-all duration-1000"
            style={{
              width: `${session.progress}%`,
              backgroundColor: session.isKillZone ? "var(--trading-bearish)" : config.color,
            }}
          />
        </div>
      )}
    </div>
  );
}

function TrueOpenCountdown({ estTime }: { estTime: { hours: number; minutes: number } }) {
  const trueOpens = [
    { name: "Daily", time: "17:00", hour: 17, minute: 0 },
    { name: "LDN", time: "01:30", hour: 1, minute: 30 },
    { name: "NY", time: "07:30", hour: 7, minute: 30 },
  ];

  // Find next true open
  const currentMinutes = estTime.hours * 60 + estTime.minutes;
  let nextOpen = trueOpens[0];
  let minDiff = Infinity;

  for (const open of trueOpens) {
    const openMinutes = open.hour * 60 + open.minute;
    let diff = openMinutes - currentMinutes;
    if (diff < 0) diff += 24 * 60; // Wrap around to next day
    if (diff > 0 && diff < 60 && diff < minDiff) {
      // Within 60 minutes
      minDiff = diff;
      nextOpen = open;
    }
  }

  // Only show if within 60 minutes of a true open
  if (minDiff === Infinity || minDiff > 60) return null;

  return (
    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-trading-info/20 border border-trading-info/40">
      <svg className="w-3.5 h-3.5 text-trading-info" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span className="text-xs font-medium text-trading-info">
        {nextOpen.name} Open in {minDiff}m
      </span>
    </div>
  );
}

// Helper functions
function formatTime(date: Date, tz: string): string {
  return date.toLocaleTimeString("en-US", {
    timeZone: tz,
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

function getESTTime(date: Date): { hours: number; minutes: number } {
  const estString = date.toLocaleTimeString("en-US", {
    timeZone: "America/New_York",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
  const [hours, minutes] = estString.split(":").map(Number);
  return { hours, minutes };
}

function parseTime(timeStr: string): { hour: number; minute: number } {
  const [hour, minute] = timeStr.split(":").map(Number);
  return { hour, minute };
}

function isTimeInRange(
  current: { hours: number; minutes: number },
  start: string,
  end: string
): boolean {
  const startTime = parseTime(start);
  const endTime = parseTime(end);
  const currentMinutes = current.hours * 60 + current.minutes;
  const startMinutes = startTime.hour * 60 + startTime.minute;
  const endMinutes = endTime.hour * 60 + endTime.minute;

  if (startMinutes < endMinutes) {
    // Normal range (e.g., 08:00 - 17:00)
    return currentMinutes >= startMinutes && currentMinutes < endMinutes;
  } else {
    // Overnight range (e.g., 19:00 - 02:00)
    return currentMinutes >= startMinutes || currentMinutes < endMinutes;
  }
}

function getSessionProgress(
  current: { hours: number; minutes: number },
  start: string,
  end: string
): number {
  const startTime = parseTime(start);
  const endTime = parseTime(end);
  const currentMinutes = current.hours * 60 + current.minutes;
  let startMinutes = startTime.hour * 60 + startTime.minute;
  let endMinutes = endTime.hour * 60 + endTime.minute;

  // Handle overnight sessions
  if (endMinutes < startMinutes) {
    endMinutes += 24 * 60;
    if (currentMinutes < startMinutes) {
      // We're past midnight
      const adjustedCurrent = currentMinutes + 24 * 60;
      return ((adjustedCurrent - startMinutes) / (endMinutes - startMinutes)) * 100;
    }
  }

  const elapsed = currentMinutes - startMinutes;
  const total = endMinutes - startMinutes;
  return Math.min(100, Math.max(0, (elapsed / total) * 100));
}

function getSessionInfo(estTime: { hours: number; minutes: number }): SessionInfo[] {
  const sessionNames: SessionName[] = ["asian", "london", "newyork", "gap"];

  return sessionNames.map((name) => {
    const config = SESSIONS[name];
    const isActive = isTimeInRange(estTime, config.start, config.end);
    const progress = isActive ? getSessionProgress(estTime, config.start, config.end) : 0;

    // Check if in kill zone for this session
    let isKillZone = false;
    if (name === "london") {
      isKillZone = isTimeInRange(estTime, KILL_ZONES.london.start, KILL_ZONES.london.end);
    } else if (name === "newyork") {
      isKillZone = isTimeInRange(estTime, KILL_ZONES.newyork.start, KILL_ZONES.newyork.end);
    }

    return { name, isActive, isKillZone, progress };
  });
}
