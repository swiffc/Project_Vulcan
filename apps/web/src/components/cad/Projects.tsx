"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "../ui/Card";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";

interface Project {
  id: string;
  name: string;
  customer: string;
  status: "active" | "pending" | "completed";
  partsCount: number;
  lastModified: Date;
}

const mockProjects: Project[] = [
  { id: "1", name: "Assembly Line Upgrade", customer: "Tesla", status: "active", partsCount: 24, lastModified: new Date() },
  { id: "2", name: "Motor Housing Rev B", customer: "Ford", status: "pending", partsCount: 8, lastModified: new Date(Date.now() - 86400000) },
  { id: "3", name: "Bracket System 2024", customer: "GM", status: "completed", partsCount: 15, lastModified: new Date(Date.now() - 172800000) },
];

const statusColors = {
  active: "success",
  pending: "warning",
  completed: "default",
} as const;

export function Projects() {
  const [projects] = useState<Project[]>(mockProjects);

  return (
    <div className="space-y-4 mt-4">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold text-white">Active Projects</h2>
        <Button variant="primary" size="sm">+ New Project</Button>
      </div>
      
      <div className="grid gap-4">
        {projects.map((project) => (
          <Card key={project.id} className="hover:border-vulcan-accent/50 transition-colors cursor-pointer">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-white">{project.name}</h3>
                  <p className="text-sm text-white/50">{project.customer}</p>
                </div>
                <div className="flex items-center gap-3">
                  <Badge variant={statusColors[project.status]}>{project.status}</Badge>
                  <span className="text-sm text-white/50">{project.partsCount} parts</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
