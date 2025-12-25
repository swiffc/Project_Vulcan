"use client";

import { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
  variant?: "default" | "interactive" | "status";
  onClick?: () => void;
}

export function Card({ children, className = "", variant = "default", onClick }: CardProps) {
  const baseStyles = "glass rounded-xl";

  const variants = {
    default: "p-4",
    interactive: "p-4 cursor-pointer transition-all hover:border-vulcan-accent/50 hover:shadow-lg hover:shadow-vulcan-accent/10",
    status: "p-3",
  };

  return (
    <div
      className={`${baseStyles} ${variants[variant]} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
}

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  icon?: ReactNode;
}

export function CardHeader({ title, subtitle, action, icon }: CardHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-3">
        {icon && <div>{icon}</div>}
        <div>
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          {subtitle && <p className="text-sm text-white/50">{subtitle}</p>}
        </div>
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export function CardContent({ children, className = "" }: CardContentProps) {
  return <div className={className}>{children}</div>;
}
