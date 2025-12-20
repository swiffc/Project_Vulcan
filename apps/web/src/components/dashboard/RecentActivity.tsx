"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "../ui/Card";
import { Badge } from "../ui/Badge";
import { formatDistanceToNow } from "date-fns";

interface Activity {
  id: string;
  type: "trade" | "cad" | "chat" | "system";
  title: string;
  description: string;
  timestamp: Date;
  status: "success" | "error" | "pending";
}

// Mock data - would come from API in production
const mockActivities: Activity[] = [
  {
    id: "1",
    type: "trade",
    title: "GBP/USD Analysis",
    description: "Bearish setup detected - Q2 manipulation",
    timestamp: new Date(Date.now() - 1000 * 60 * 15),
    status: "success",
  },
  {
    id: "2",
    type: "cad",
    title: "Flange_01.SLDPRT",
    description: "Part built from PDF drawing",
    timestamp: new Date(Date.now() - 1000 * 60 * 45),
    status: "success",
  },
  {
    id: "3",
    type: "system",
    title: "System Backup",
    description: "Daily backup to Google Drive",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2),
    status: "success",
  },
  {
    id: "4",
    type: "trade",
    title: "Weekly Review",
    description: "3 wins, 1 loss - 2.5R total",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5),
    status: "success",
  },
  {
    id: "5",
    type: "cad",
    title: "ECN-2025-001",
    description: "Bore diameter updated",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24),
    status: "success",
  },
];

const typeIcons = {
  trade: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
    </svg>
  ),
  cad: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
    </svg>
  ),
  chat: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
    </svg>
  ),
  system: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  ),
};

const typeColors = {
  trade: "bg-green-500/20 text-green-400",
  cad: "bg-blue-500/20 text-blue-400",
  chat: "bg-purple-500/20 text-purple-400",
  system: "bg-amber-500/20 text-amber-400",
};

export function RecentActivity() {
  const [activities] = useState<Activity[]>(mockActivities);

  return (
    <Card>
      <CardHeader title="Recent Activity" subtitle="Latest actions across all domains" />
      <CardContent className="divide-y divide-white/5 -mx-4">
        {activities.map((activity) => (
          <div
            key={activity.id}
            className="flex items-start gap-3 px-4 py-3 hover:bg-white/5 transition-colors"
          >
            <div className={`w-8 h-8 rounded-lg ${typeColors[activity.type]} flex items-center justify-center`}>
              {typeIcons[activity.type]}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <p className="text-sm font-medium text-white truncate">{activity.title}</p>
                <Badge
                  variant={activity.status === "success" ? "success" : activity.status === "error" ? "error" : "warning"}
                  size="sm"
                >
                  {activity.status}
                </Badge>
              </div>
              <p className="text-xs text-white/50 truncate">{activity.description}</p>
            </div>
            <span className="text-xs text-white/30 whitespace-nowrap">
              {formatDistanceToNow(activity.timestamp, { addSuffix: true })}
            </span>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
