"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "../ui/Card";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";

interface ECN {
  id: string;
  ecnNumber: string;
  title: string;
  description: string;
  unitTag: string;
  customer: string;
  status: "draft" | "review" | "approved" | "implemented";
  priority: "low" | "medium" | "high" | "critical";
  category: "design" | "material" | "process" | "drawing";
  createdBy: string;
  createdAt: string;
  affectedParts: string[];
}

const mockECNs: ECN[] = [
  {
    id: "1",
    ecnNumber: "ECN-2024-0156",
    title: "Header Nozzle Reinforcement Pad",
    description: "Add reinforcement pad to 8\" inlet nozzle per customer request. Pad size 16\" OD x 3/4\" thick SA-516 Gr70.",
    unitTag: "E-4501 A/B",
    customer: "ExxonMobil",
    status: "approved",
    priority: "high",
    category: "design",
    createdBy: "D. Cornealius",
    createdAt: "2024-12-18",
    affectedParts: ["HDR-BOX-24", "NZL-INL-8"],
  },
  {
    id: "2",
    ecnNumber: "ECN-2024-0157",
    title: "Tube Material Change - T5 to T11",
    description: "Customer spec revision requires A213 T11 tubes in lieu of A213 T5 for improved high-temp corrosion resistance.",
    unitTag: "E-1101",
    customer: "Saudi Aramco",
    status: "review",
    priority: "critical",
    category: "material",
    createdBy: "D. Cornealius",
    createdAt: "2024-12-19",
    affectedParts: ["TB-6X2-T5", "FT-EMB-CS"],
  },
  {
    id: "3",
    ecnNumber: "ECN-2024-0158",
    title: "Fan Hub Variable Pitch Upgrade",
    description: "Upgrade from manual variable pitch to auto-variable pitch hub per process turndown requirements.",
    unitTag: "AC-2201 A/B/C",
    customer: "Chevron",
    status: "draft",
    priority: "medium",
    category: "design",
    createdBy: "D. Cornealius",
    createdAt: "2024-12-20",
    affectedParts: ["FAN-14-4BL", "HUB-VP-14"],
  },
  {
    id: "4",
    ecnNumber: "ECN-2024-0155",
    title: "Drawing Note - Lifting Lugs",
    description: "Add lifting lug detail and notes to GA drawing per API 661 requirements. Include load rating and orientation.",
    unitTag: "E-4501 A/B",
    customer: "ExxonMobil",
    status: "implemented",
    priority: "low",
    category: "drawing",
    createdBy: "D. Cornealius",
    createdAt: "2024-12-15",
    affectedParts: ["STR-BAY-STD"],
  },
  {
    id: "5",
    ecnNumber: "ECN-2024-0159",
    title: "Fin Pitch Change 10 to 11 FPI",
    description: "Increase fin pitch from 10 FPI to 11 FPI to meet duty with reduced air flow at high ambient temperature.",
    unitTag: "AC-501",
    customer: "ADNOC",
    status: "review",
    priority: "high",
    category: "process",
    createdBy: "D. Cornealius",
    createdAt: "2024-12-20",
    affectedParts: ["FT-LFIN-AL", "TB-2X4-A179"],
  },
];

const statusColors = {
  draft: "default",
  review: "warning",
  approved: "success",
  implemented: "info",
} as const;

const priorityColors = {
  low: "default",
  medium: "warning",
  high: "error",
  critical: "error",
} as const;

const categoryIcons = {
  design: "M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z",
  material: "M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z",
  process: "M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z",
  drawing: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
};

export function ECNTracker() {
  const [ecns] = useState<ECN[]>(mockECNs);
  const [selectedECN, setSelectedECN] = useState<ECN | null>(null);
  const [filter, setFilter] = useState<string>("all");

  const filteredECNs = filter === "all"
    ? ecns
    : ecns.filter(e => e.status === filter);

  return (
    <div className="space-y-4 mt-4">
      {/* Header */}
      <div className="flex flex-wrap justify-between items-center gap-4">
        <div className="flex gap-2">
          {["all", "draft", "review", "approved", "implemented"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                filter === f
                  ? "bg-vulcan-accent text-white"
                  : "bg-white/5 text-white/60 hover:bg-white/10"
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
              {f !== "all" && (
                <span className="ml-1.5 px-1.5 py-0.5 rounded bg-white/10 text-xs">
                  {ecns.filter(e => e.status === f).length}
                </span>
              )}
            </button>
          ))}
        </div>
        <Button variant="primary" size="sm">
          <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New ECN
        </Button>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* ECN List */}
        <div className="lg:col-span-2 space-y-3">
          {filteredECNs.map((ecn) => (
            <Card
              key={ecn.id}
              className={`cursor-pointer transition-all ${
                selectedECN?.id === ecn.id
                  ? "border-vulcan-accent ring-1 ring-vulcan-accent"
                  : "hover:border-white/20"
              }`}
              onClick={() => setSelectedECN(ecn)}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                      ecn.category === "design" ? "bg-blue-500/20" :
                      ecn.category === "material" ? "bg-purple-500/20" :
                      ecn.category === "process" ? "bg-amber-500/20" :
                      "bg-green-500/20"
                    }`}>
                      <svg className={`w-4 h-4 ${
                        ecn.category === "design" ? "text-blue-400" :
                        ecn.category === "material" ? "text-purple-400" :
                        ecn.category === "process" ? "text-amber-400" :
                        "text-green-400"
                      }`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={categoryIcons[ecn.category]} />
                      </svg>
                    </div>
                    <div>
                      <p className="font-mono text-vulcan-accent text-sm">{ecn.ecnNumber}</p>
                      <h3 className="font-medium text-white">{ecn.title}</h3>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Badge variant={priorityColors[ecn.priority]} size="sm">
                      {ecn.priority}
                    </Badge>
                    <Badge variant={statusColors[ecn.status]} size="sm">
                      {ecn.status}
                    </Badge>
                  </div>
                </div>

                <p className="text-sm text-white/50 line-clamp-2 mb-3">{ecn.description}</p>

                <div className="flex items-center justify-between text-xs text-white/40">
                  <div className="flex items-center gap-2">
                    <span className="font-mono">{ecn.unitTag}</span>
                    <span>•</span>
                    <span>{ecn.customer}</span>
                  </div>
                  <span>{new Date(ecn.createdAt).toLocaleDateString()}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* ECN Details */}
        <div>
          {selectedECN ? (
            <Card className="sticky top-4">
              <CardHeader
                title={selectedECN.ecnNumber}
                subtitle={selectedECN.title}
              />
              <CardContent className="space-y-4">
                {/* Status & Priority */}
                <div className="flex gap-2">
                  <Badge variant={statusColors[selectedECN.status]}>
                    {selectedECN.status.toUpperCase()}
                  </Badge>
                  <Badge variant={priorityColors[selectedECN.priority]}>
                    {selectedECN.priority.toUpperCase()} PRIORITY
                  </Badge>
                </div>

                {/* Description */}
                <div>
                  <p className="text-xs text-white/40 uppercase tracking-wider mb-1">Description</p>
                  <p className="text-sm text-white/70">{selectedECN.description}</p>
                </div>

                {/* Details */}
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between py-1 border-b border-white/5">
                    <span className="text-white/50">Unit</span>
                    <span className="text-white font-mono">{selectedECN.unitTag}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-white/5">
                    <span className="text-white/50">Customer</span>
                    <span className="text-white">{selectedECN.customer}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-white/5">
                    <span className="text-white/50">Category</span>
                    <span className="text-white capitalize">{selectedECN.category}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-white/5">
                    <span className="text-white/50">Created By</span>
                    <span className="text-white">{selectedECN.createdBy}</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-white/50">Created</span>
                    <span className="text-white">{new Date(selectedECN.createdAt).toLocaleDateString()}</span>
                  </div>
                </div>

                {/* Affected Parts */}
                <div>
                  <p className="text-xs text-white/40 uppercase tracking-wider mb-2">Affected Parts</p>
                  <div className="flex flex-wrap gap-2">
                    {selectedECN.affectedParts.map((part) => (
                      <span key={part} className="px-2 py-1 bg-white/5 rounded text-xs font-mono text-vulcan-accent">
                        {part}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Actions */}
                <div className="space-y-2 pt-2">
                  {selectedECN.status === "draft" && (
                    <Button variant="primary" className="w-full">Submit for Review</Button>
                  )}
                  {selectedECN.status === "review" && (
                    <Button variant="primary" className="w-full">Approve ECN</Button>
                  )}
                  {selectedECN.status === "approved" && (
                    <Button variant="primary" className="w-full">Mark Implemented</Button>
                  )}
                  <div className="grid grid-cols-2 gap-2">
                    <Button variant="secondary" size="sm">Edit ECN</Button>
                    <Button variant="ghost" size="sm">View History</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-white/5 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <p className="text-white/50">Select an ECN to view details</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
