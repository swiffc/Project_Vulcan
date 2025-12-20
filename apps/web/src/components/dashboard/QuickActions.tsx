"use client";

import Link from "next/link";
import { Card, CardHeader, CardContent } from "../ui/Card";

interface QuickAction {
  label: string;
  description: string;
  href?: string;
  onClick?: () => void;
  icon: React.ReactNode;
  color: string;
}

const actions: QuickAction[] = [
  {
    label: "Scan Markets",
    description: "Analyze trading pairs",
    href: "/trading",
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
    ),
    color: "from-green-500 to-emerald-600",
  },
  {
    label: "New CAD Part",
    description: "Upload PDF drawing",
    href: "/cad",
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
    color: "from-blue-500 to-indigo-600",
  },
  {
    label: "Trade Journal",
    description: "Log your trades",
    href: "/trading?tab=journal",
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
    ),
    color: "from-purple-500 to-violet-600",
  },
  {
    label: "Weekly Review",
    description: "Performance summary",
    href: "/trading?tab=performance",
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    color: "from-amber-500 to-orange-600",
  },
  {
    label: "ECN Tracker",
    description: "Revision history",
    href: "/cad?tab=ecn",
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
      </svg>
    ),
    color: "from-cyan-500 to-teal-600",
  },
  {
    label: "Export Files",
    description: "STEP/PDF to Drive",
    href: "/cad?tab=export",
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
      </svg>
    ),
    color: "from-pink-500 to-rose-600",
  },
];

export function QuickActions() {
  return (
    <Card>
      <CardHeader title="Quick Actions" subtitle="Jump to common tasks" />
      <CardContent className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {actions.map((action) => (
          <Link
            key={action.label}
            href={action.href || "#"}
            className="group flex items-center gap-3 p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-all"
          >
            <div
              className={`w-10 h-10 rounded-lg bg-gradient-to-br ${action.color} flex items-center justify-center text-white shadow-lg group-hover:scale-110 transition-transform`}
            >
              {action.icon}
            </div>
            <div>
              <p className="text-sm font-medium text-white group-hover:text-vulcan-accent transition-colors">
                {action.label}
              </p>
              <p className="text-xs text-white/40">{action.description}</p>
            </div>
          </Link>
        ))}
      </CardContent>
    </Card>
  );
}
