"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";

interface ExportJob {
  id: string;
  fileName: string;
  format: "STEP" | "PDF" | "DXF" | "IGES";
  status: "queued" | "processing" | "completed" | "failed";
  destination: string;
}

const mockJobs: ExportJob[] = [
  { id: "1", fileName: "Assembly_v2.SLDASM", format: "STEP", status: "completed", destination: "Google Drive" },
  { id: "2", fileName: "Bracket_001.SLDPRT", format: "PDF", status: "processing", destination: "Customer Portal" },
  { id: "3", fileName: "Housing_Rev_B.SLDPRT", format: "DXF", status: "queued", destination: "Local" },
];

const statusColors = { queued: "default", processing: "warning", completed: "success", failed: "error" } as const;

export function ExportDrive() {
  const [jobs] = useState<ExportJob[]>(mockJobs);

  return (
    <div className="space-y-4 mt-4">
      <div className="grid md:grid-cols-2 gap-4">
        <Card>
          <CardHeader title="Export Queue" subtitle="Active export jobs" />
          <CardContent>
            <div className="space-y-2">
              {jobs.map((job) => (
                <div key={job.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <div>
                    <p className="text-white text-sm">{job.fileName}</p>
                    <p className="text-white/50 text-xs">{job.destination}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-vulcan-accent">{job.format}</span>
                    <Badge variant={statusColors[job.status]} size="sm">{job.status}</Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader title="Quick Export" subtitle="Export current file" />
          <CardContent className="space-y-3">
            <Button variant="outline" className="w-full justify-start">Export as STEP</Button>
            <Button variant="outline" className="w-full justify-start">Export as PDF Drawing</Button>
            <Button variant="outline" className="w-full justify-start">Export as DXF</Button>
            <Button variant="primary" className="w-full">Upload to Google Drive</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
