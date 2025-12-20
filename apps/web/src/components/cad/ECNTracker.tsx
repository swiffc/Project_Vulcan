"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "../ui/Card";
import { Badge } from "../ui/Badge";

interface ECN {
  id: string;
  ecnNumber: string;
  title: string;
  status: "draft" | "review" | "approved" | "implemented";
  priority: "low" | "medium" | "high";
  createdAt: Date;
}

const mockECNs: ECN[] = [
  { id: "1", ecnNumber: "ECN-2024-001", title: "Bracket Thickness Increase", status: "approved", priority: "high", createdAt: new Date() },
  { id: "2", ecnNumber: "ECN-2024-002", title: "Material Change - Housing", status: "review", priority: "medium", createdAt: new Date() },
  { id: "3", ecnNumber: "ECN-2024-003", title: "Hole Pattern Update", status: "draft", priority: "low", createdAt: new Date() },
];

const statusColors = { draft: "default", review: "warning", approved: "success", implemented: "success" } as const;
const priorityColors = { low: "default", medium: "warning", high: "error" } as const;

export function ECNTracker() {
  const [ecns] = useState<ECN[]>(mockECNs);

  return (
    <div className="space-y-4 mt-4">
      <Card>
        <CardHeader title="Engineering Change Notices" subtitle="Track and manage part revisions" />
        <CardContent>
          <div className="space-y-3">
            {ecns.map((ecn) => (
              <div key={ecn.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                <div>
                  <p className="font-mono text-vulcan-accent">{ecn.ecnNumber}</p>
                  <p className="text-white">{ecn.title}</p>
                </div>
                <div className="flex gap-2">
                  <Badge variant={priorityColors[ecn.priority]}>{ecn.priority}</Badge>
                  <Badge variant={statusColors[ecn.status]}>{ecn.status}</Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
