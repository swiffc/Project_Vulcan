"use client";

import { ReactNode } from "react";

interface BadgeProps {
  children: ReactNode;
  variant?: "default" | "success" | "warning" | "error" | "info";
  size?: "sm" | "md";
  dot?: boolean;
  className?: string;
}

export function Badge({
  children,
  variant = "default",
  size = "sm",
  dot,
  className = "",
}: BadgeProps) {
  const variants = {
    default: "bg-white/10 text-white/70",
    success: "bg-vulcan-success/20 text-vulcan-success",
    warning: "bg-vulcan-warning/20 text-vulcan-warning",
    error: "bg-vulcan-error/20 text-vulcan-error",
    info: "bg-vulcan-accent/20 text-vulcan-accent",
  };

  const sizes = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-3 py-1 text-sm",
  };

  const dotColors = {
    default: "bg-white/50",
    success: "bg-vulcan-success",
    warning: "bg-vulcan-warning",
    error: "bg-vulcan-error",
    info: "bg-vulcan-accent",
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-medium ${variants[variant]} ${sizes[size]} ${className}`}
    >
      {dot && (
        <span className={`w-1.5 h-1.5 rounded-full ${dotColors[variant]}`} />
      )}
      {children}
    </span>
  );
}

// Status dot component
interface StatusDotProps {
  status: "online" | "offline" | "degraded" | "checking";
  className?: string;
}

export function StatusDot({ status, className = "" }: StatusDotProps) {
  const colors = {
    online: "bg-vulcan-success",
    offline: "bg-vulcan-error",
    degraded: "bg-vulcan-warning",
    checking: "bg-vulcan-accent animate-pulse",
  };

  return (
    <span className={`w-2 h-2 rounded-full ${colors[status]} ${className}`} />
  );
}
