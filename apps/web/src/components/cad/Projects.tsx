"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "../ui/Card";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";

interface ACHEProject {
  id: string;
  unitTag: string;
  jobNumber: string;
  customer: string;
  endUser: string;
  location: string;
  status: "engineering" | "approval" | "fabrication" | "testing" | "shipped";
  type: "ACHE" | "ACC" | "Fin-Fan";
  specs: {
    duty: string;
    designPressure: string;
    designTemp: string;
    tubeMaterial: string;
    finType: string;
    bays: number;
    bundlesPerBay: number;
  };
  progress: number;
  dueDate: string;
  engineer: string;
}

const mockProjects: ACHEProject[] = [
  {
    id: "1",
    unitTag: "E-4501 A/B",
    jobNumber: "CHT-2024-0892",
    customer: "ExxonMobil",
    endUser: "Baytown Refinery",
    location: "Texas, USA",
    status: "approval",
    type: "ACHE",
    specs: {
      duty: "45.2 MMBtu/hr",
      designPressure: "450 PSIG",
      designTemp: "650°F",
      tubeMaterial: "A179 Seamless",
      finType: "L-Fin Aluminum",
      bays: 2,
      bundlesPerBay: 2,
    },
    progress: 75,
    dueDate: "2025-01-15",
    engineer: "D. Cornealius",
  },
  {
    id: "2",
    unitTag: "AC-2201 A/B/C",
    jobNumber: "CHT-2024-0915",
    customer: "Chevron",
    endUser: "Pascagoula Refinery",
    location: "Mississippi, USA",
    status: "engineering",
    type: "ACHE",
    specs: {
      duty: "78.5 MMBtu/hr",
      designPressure: "285 PSIG",
      designTemp: "500°F",
      tubeMaterial: "A214 ERW",
      finType: "Extruded Aluminum",
      bays: 3,
      bundlesPerBay: 2,
    },
    progress: 35,
    dueDate: "2025-02-10",
    engineer: "D. Cornealius",
  },
  {
    id: "3",
    unitTag: "E-1101",
    jobNumber: "CHT-2024-0878",
    customer: "Saudi Aramco",
    endUser: "Ras Tanura",
    location: "Saudi Arabia",
    status: "fabrication",
    type: "ACHE",
    specs: {
      duty: "112.0 MMBtu/hr",
      designPressure: "600 PSIG",
      designTemp: "750°F",
      tubeMaterial: "A213 T5",
      finType: "Embedded Steel",
      bays: 4,
      bundlesPerBay: 3,
    },
    progress: 90,
    dueDate: "2025-01-08",
    engineer: "D. Cornealius",
  },
  {
    id: "4",
    unitTag: "E-3301 A/B",
    jobNumber: "CHT-2024-0923",
    customer: "Shell",
    endUser: "Deer Park",
    location: "Texas, USA",
    status: "engineering",
    type: "ACC",
    specs: {
      duty: "28.7 MMBtu/hr",
      designPressure: "150 PSIG",
      designTemp: "350°F",
      tubeMaterial: "A179 Seamless",
      finType: "L-Fin Aluminum",
      bays: 1,
      bundlesPerBay: 2,
    },
    progress: 15,
    dueDate: "2025-03-01",
    engineer: "D. Cornealius",
  },
  {
    id: "5",
    unitTag: "AC-501",
    jobNumber: "CHT-2024-0901",
    customer: "ADNOC",
    endUser: "Ruwais Refinery",
    location: "UAE",
    status: "testing",
    type: "ACHE",
    specs: {
      duty: "55.3 MMBtu/hr",
      designPressure: "400 PSIG",
      designTemp: "600°F",
      tubeMaterial: "A213 T11",
      finType: "L-Fin Aluminum",
      bays: 2,
      bundlesPerBay: 3,
    },
    progress: 95,
    dueDate: "2025-01-05",
    engineer: "D. Cornealius",
  },
];

const statusColors = {
  engineering: "warning",
  approval: "info",
  fabrication: "success",
  testing: "default",
  shipped: "success",
} as const;

const statusLabels = {
  engineering: "Engineering",
  approval: "Customer Approval",
  fabrication: "In Fabrication",
  testing: "Testing/QC",
  shipped: "Shipped",
};

export function Projects() {
  const [projects] = useState<ACHEProject[]>(mockProjects);
  const [selectedProject, setSelectedProject] = useState<ACHEProject | null>(null);
  const [filter, setFilter] = useState<string>("all");

  const filteredProjects = filter === "all"
    ? projects
    : projects.filter(p => p.status === filter);

  return (
    <div className="space-y-4 mt-4">
      {/* Header */}
      <div className="flex flex-wrap justify-between items-center gap-4">
        <div className="flex gap-2">
          {["all", "engineering", "approval", "fabrication", "testing"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                filter === f
                  ? "bg-vulcan-accent text-white"
                  : "bg-white/5 text-white/60 hover:bg-white/10"
              }`}
            >
              {f === "all" ? "All" : statusLabels[f as keyof typeof statusLabels]}
            </button>
          ))}
        </div>
        <Button variant="primary" size="sm">
          <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New ACHE Unit
        </Button>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Project List */}
        <div className="lg:col-span-2 space-y-3">
          {filteredProjects.map((project) => (
            <Card
              key={project.id}
              className={`cursor-pointer transition-all ${
                selectedProject?.id === project.id
                  ? "border-vulcan-accent ring-1 ring-vulcan-accent"
                  : "hover:border-white/20"
              }`}
              onClick={() => setSelectedProject(project)}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-mono font-bold text-white text-lg">{project.unitTag}</h3>
                      <Badge variant={statusColors[project.status]} size="sm">
                        {statusLabels[project.status]}
                      </Badge>
                    </div>
                    <p className="text-sm text-white/50">{project.jobNumber}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-white">{project.customer}</p>
                    <p className="text-xs text-white/40">{project.endUser}</p>
                  </div>
                </div>

                <div className="grid grid-cols-4 gap-4 mb-3 text-xs">
                  <div>
                    <p className="text-white/40">Duty</p>
                    <p className="text-vulcan-accent font-medium">{project.specs.duty}</p>
                  </div>
                  <div>
                    <p className="text-white/40">Design Press.</p>
                    <p className="text-white">{project.specs.designPressure}</p>
                  </div>
                  <div>
                    <p className="text-white/40">Design Temp.</p>
                    <p className="text-white">{project.specs.designTemp}</p>
                  </div>
                  <div>
                    <p className="text-white/40">Configuration</p>
                    <p className="text-white">{project.specs.bays} Bay × {project.specs.bundlesPerBay} Bundle</p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        project.progress >= 90 ? "bg-green-500" :
                        project.progress >= 50 ? "bg-vulcan-accent" :
                        "bg-amber-500"
                      }`}
                      style={{ width: `${project.progress}%` }}
                    />
                  </div>
                  <span className="text-xs text-white/50">{project.progress}%</span>
                  <span className="text-xs text-white/30">|</span>
                  <span className="text-xs text-white/50">Due: {new Date(project.dueDate).toLocaleDateString()}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Project Details Sidebar */}
        <div>
          {selectedProject ? (
            <Card className="sticky top-4">
              <CardHeader
                title={selectedProject.unitTag}
                subtitle={selectedProject.jobNumber}
              />
              <CardContent className="space-y-4">
                {/* Customer Info */}
                <div className="p-3 bg-white/5 rounded-lg">
                  <p className="text-xs text-white/40 mb-1">Customer / End User</p>
                  <p className="text-white font-medium">{selectedProject.customer}</p>
                  <p className="text-sm text-white/60">{selectedProject.endUser}</p>
                  <p className="text-xs text-white/40 mt-1">{selectedProject.location}</p>
                </div>

                {/* Technical Specs */}
                <div>
                  <p className="text-xs text-white/40 uppercase tracking-wider mb-2">Technical Specifications</p>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-white/50">Type</span>
                      <span className="text-white">{selectedProject.type}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/50">Duty</span>
                      <span className="text-vulcan-accent font-mono">{selectedProject.specs.duty}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/50">Design Pressure</span>
                      <span className="text-white font-mono">{selectedProject.specs.designPressure}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/50">Design Temp</span>
                      <span className="text-white font-mono">{selectedProject.specs.designTemp}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/50">Tube Material</span>
                      <span className="text-white">{selectedProject.specs.tubeMaterial}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/50">Fin Type</span>
                      <span className="text-white">{selectedProject.specs.finType}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/50">Configuration</span>
                      <span className="text-white">{selectedProject.specs.bays} Bays × {selectedProject.specs.bundlesPerBay} Bundles</span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="space-y-2 pt-2">
                  <Button variant="primary" className="w-full">
                    <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    Open in SolidWorks
                  </Button>
                  <div className="grid grid-cols-2 gap-2">
                    <Button variant="secondary" size="sm">View GA</Button>
                    <Button variant="secondary" size="sm">View BOM</Button>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <Button variant="ghost" size="sm">HTRI Data</Button>
                    <Button variant="ghost" size="sm">Datasheet</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-white/5 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
                  </svg>
                </div>
                <p className="text-white/50">Select a project to view details</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
