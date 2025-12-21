"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";

interface ExportJob {
  id: string;
  fileName: string;
  unitTag: string;
  format: "STEP" | "PDF" | "DXF" | "IGES" | "DWG" | "XLSX";
  type: "GA Drawing" | "Bundle Assembly" | "BOM" | "Datasheet" | "3D Model" | "Detail Drawing";
  status: "queued" | "processing" | "completed" | "failed";
  destination: string;
  size?: string;
  completedAt?: string;
}

interface BOMItem {
  itemNo: number;
  partNumber: string;
  description: string;
  material: string;
  qty: number;
  unitWeight: number;
  totalWeight: number;
}

const mockJobs: ExportJob[] = [
  { id: "1", fileName: "E-4501_GA_Drawing_Rev2.pdf", unitTag: "E-4501 A/B", format: "PDF", type: "GA Drawing", status: "completed", destination: "Customer Portal", size: "2.4 MB", completedAt: "2024-12-20 10:30" },
  { id: "2", fileName: "E-4501_Bundle_Assembly.step", unitTag: "E-4501 A/B", format: "STEP", type: "Bundle Assembly", status: "processing", destination: "SharePoint" },
  { id: "3", fileName: "E-1101_BOM_Rev1.xlsx", unitTag: "E-1101", format: "XLSX", type: "BOM", status: "completed", destination: "Local", size: "156 KB", completedAt: "2024-12-20 09:15" },
  { id: "4", fileName: "AC-2201_Thermal_Datasheet.pdf", unitTag: "AC-2201 A/B/C", format: "PDF", type: "Datasheet", status: "queued", destination: "Email" },
  { id: "5", fileName: "E-4501_Full_Unit.step", unitTag: "E-4501 A/B", format: "STEP", type: "3D Model", status: "failed", destination: "Google Drive" },
];

const mockBOM: BOMItem[] = [
  { itemNo: 1, partNumber: "TB-2X4-A179", description: "Tube Bundle 2-Row x 4-Pass", material: "A179 Seamless", qty: 4, unitWeight: 6125, totalWeight: 24500 },
  { itemNo: 2, partNumber: "HDR-BOX-24", description: "Box Header Assembly 24\"", material: "SA-516 Gr70", qty: 4, unitWeight: 2050, totalWeight: 8200 },
  { itemNo: 3, partNumber: "FT-LFIN-AL", description: "L-Fin Aluminum 10 FPI", material: "1100 Aluminum", qty: 480, unitWeight: 12, totalWeight: 5760 },
  { itemNo: 4, partNumber: "FAN-14-4BL", description: "Fan Assembly 14' 4-Blade", material: "Aluminum Blades", qty: 2, unitWeight: 1600, totalWeight: 3200 },
  { itemNo: 5, partNumber: "STR-BAY-STD", description: "Standard Bay Structure", material: "A36 Steel", qty: 2, unitWeight: 9250, totalWeight: 18500 },
  { itemNo: 6, partNumber: "PLN-FRC-STD", description: "Forced Draft Plenum", material: "A36 Steel", qty: 2, unitWeight: 1200, totalWeight: 2400 },
  { itemNo: 7, partNumber: "FLG-WN-8-300", description: "Weld Neck Flange 8\" 300#", material: "A105", qty: 4, unitWeight: 85, totalWeight: 340 },
  { itemNo: 8, partNumber: "NZL-INL-8", description: "Inlet Nozzle Assembly 8\"", material: "SA-106 Gr B", qty: 2, unitWeight: 120, totalWeight: 240 },
];

const statusColors = { queued: "default", processing: "warning", completed: "success", failed: "error" } as const;

const exportTypes = [
  { id: "ga", name: "GA Drawing", icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z", formats: ["PDF", "DWG"] },
  { id: "bundle", name: "Bundle Assembly", icon: "M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5", formats: ["STEP", "IGES"] },
  { id: "bom", name: "Bill of Materials", icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01", formats: ["XLSX", "PDF"] },
  { id: "datasheet", name: "Thermal Datasheet", icon: "M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z", formats: ["PDF"] },
  { id: "model", name: "Full 3D Model", icon: "M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4", formats: ["STEP", "IGES", "SLDASM"] },
  { id: "detail", name: "Detail Drawings", icon: "M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z", formats: ["PDF", "DXF"] },
];

export function ExportDrive() {
  const [jobs] = useState<ExportJob[]>(mockJobs);
  const [bom] = useState<BOMItem[]>(mockBOM);
  const [activeView, setActiveView] = useState<"export" | "bom">("export");
  const [selectedUnit, setSelectedUnit] = useState("E-4501 A/B");

  const totalWeight = bom.reduce((sum, item) => sum + item.totalWeight, 0);

  return (
    <div className="space-y-4 mt-4">
      {/* View Toggle */}
      <div className="flex gap-2 border-b border-white/10 pb-2">
        <button
          onClick={() => setActiveView("export")}
          className={`flex items-center gap-2 px-4 py-2 rounded-t-lg transition-colors ${
            activeView === "export"
              ? "bg-white/10 text-white border-b-2 border-vulcan-accent"
              : "text-white/50 hover:text-white"
          }`}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          Export Center
        </button>
        <button
          onClick={() => setActiveView("bom")}
          className={`flex items-center gap-2 px-4 py-2 rounded-t-lg transition-colors ${
            activeView === "bom"
              ? "bg-white/10 text-white border-b-2 border-vulcan-accent"
              : "text-white/50 hover:text-white"
          }`}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
          Bill of Materials
        </button>
      </div>

      {activeView === "export" ? (
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Export Types */}
          <Card>
            <CardHeader title="Quick Export" subtitle="Select document type" />
            <CardContent className="space-y-2">
              {exportTypes.map((type) => (
                <button
                  key={type.id}
                  className="w-full flex items-center gap-3 p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-left group"
                >
                  <div className="w-10 h-10 rounded-lg bg-vulcan-accent/20 flex items-center justify-center group-hover:bg-vulcan-accent/30 transition-colors">
                    <svg className="w-5 h-5 text-vulcan-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={type.icon} />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-white">{type.name}</p>
                    <p className="text-xs text-white/40">{type.formats.join(" / ")}</p>
                  </div>
                  <svg className="w-4 h-4 text-white/30 group-hover:text-white/50 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              ))}
            </CardContent>
          </Card>

          {/* Export Queue */}
          <Card className="lg:col-span-2">
            <CardHeader
              title="Export History"
              subtitle="Recent exports and queue"
              action={
                <select
                  value={selectedUnit}
                  onChange={(e) => setSelectedUnit(e.target.value)}
                  className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-sm text-white focus:outline-none"
                >
                  <option value="all">All Units</option>
                  <option value="E-4501 A/B">E-4501 A/B</option>
                  <option value="E-1101">E-1101</option>
                  <option value="AC-2201 A/B/C">AC-2201 A/B/C</option>
                </select>
              }
            />
            <CardContent>
              <div className="space-y-3">
                {jobs.filter(j => selectedUnit === "all" || j.unitTag === selectedUnit).map((job) => (
                  <div key={job.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        job.status === "completed" ? "bg-green-500/20" :
                        job.status === "processing" ? "bg-amber-500/20" :
                        job.status === "failed" ? "bg-red-500/20" :
                        "bg-white/10"
                      }`}>
                        {job.status === "processing" ? (
                          <div className="w-4 h-4 border-2 border-amber-400 border-t-transparent rounded-full animate-spin" />
                        ) : (
                          <svg className={`w-5 h-5 ${
                            job.status === "completed" ? "text-green-400" :
                            job.status === "failed" ? "text-red-400" :
                            "text-white/40"
                          }`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            {job.status === "completed" && <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />}
                            {job.status === "failed" && <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />}
                            {job.status === "queued" && <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />}
                          </svg>
                        )}
                      </div>
                      <div>
                        <p className="text-white text-sm font-medium">{job.fileName}</p>
                        <div className="flex items-center gap-2 text-xs text-white/40">
                          <span className="font-mono">{job.unitTag}</span>
                          <span>•</span>
                          <span>{job.type}</span>
                          {job.size && (
                            <>
                              <span>•</span>
                              <span>{job.size}</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <Badge variant={statusColors[job.status]} size="sm">{job.status}</Badge>
                        <p className="text-xs text-white/30 mt-1">{job.destination}</p>
                      </div>
                      {job.status === "completed" && (
                        <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                          <svg className="w-4 h-4 text-white/50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                          </svg>
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      ) : (
        <div className="grid lg:grid-cols-4 gap-6">
          {/* BOM Table */}
          <Card className="lg:col-span-3">
            <CardHeader
              title="Bill of Materials"
              subtitle="E-4501 A/B - ExxonMobil Baytown"
              action={
                <div className="flex gap-2">
                  <Button variant="secondary" size="sm">
                    <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                    </svg>
                    Export Excel
                  </Button>
                  <Button variant="secondary" size="sm">
                    <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                    </svg>
                    Print
                  </Button>
                </div>
              }
            />
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left py-3 px-4 text-xs text-white/40 uppercase tracking-wider">Item</th>
                      <th className="text-left py-3 px-4 text-xs text-white/40 uppercase tracking-wider">Part Number</th>
                      <th className="text-left py-3 px-4 text-xs text-white/40 uppercase tracking-wider">Description</th>
                      <th className="text-left py-3 px-4 text-xs text-white/40 uppercase tracking-wider">Material</th>
                      <th className="text-right py-3 px-4 text-xs text-white/40 uppercase tracking-wider">Qty</th>
                      <th className="text-right py-3 px-4 text-xs text-white/40 uppercase tracking-wider">Unit Wt (lb)</th>
                      <th className="text-right py-3 px-4 text-xs text-white/40 uppercase tracking-wider">Total Wt (lb)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bom.map((item) => (
                      <tr key={item.itemNo} className="border-b border-white/5 hover:bg-white/5">
                        <td className="py-3 px-4 text-white font-mono">{item.itemNo}</td>
                        <td className="py-3 px-4 text-vulcan-accent font-mono text-sm">{item.partNumber}</td>
                        <td className="py-3 px-4 text-white">{item.description}</td>
                        <td className="py-3 px-4 text-white/70">{item.material}</td>
                        <td className="py-3 px-4 text-right text-white font-mono">{item.qty}</td>
                        <td className="py-3 px-4 text-right text-white/70 font-mono">{item.unitWeight.toLocaleString()}</td>
                        <td className="py-3 px-4 text-right text-white font-mono">{item.totalWeight.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr className="bg-white/5">
                      <td colSpan={6} className="py-3 px-4 text-right font-bold text-white">TOTAL DRY WEIGHT</td>
                      <td className="py-3 px-4 text-right font-mono font-bold text-vulcan-accent">{totalWeight.toLocaleString()} lb</td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* BOM Summary */}
          <div className="space-y-6">
            <Card>
              <CardHeader title="Weight Summary" />
              <CardContent className="space-y-4">
                <div className="p-4 bg-white/5 rounded-lg">
                  <p className="text-xs text-white/40 mb-1">Total Dry Weight</p>
                  <p className="text-2xl font-bold text-white font-mono">
                    {totalWeight.toLocaleString()} <span className="text-sm text-white/50">lb</span>
                  </p>
                  <p className="text-xs text-white/40">
                    ({(totalWeight / 2.205).toFixed(0).toLocaleString()} kg)
                  </p>
                </div>
                <div className="p-4 bg-vulcan-accent/20 rounded-lg border border-vulcan-accent/30">
                  <p className="text-xs text-white/40 mb-1">Est. Operating Weight</p>
                  <p className="text-2xl font-bold text-vulcan-accent font-mono">
                    {Math.round(totalWeight * 1.15).toLocaleString()} <span className="text-sm text-white/50">lb</span>
                  </p>
                  <p className="text-xs text-white/40">+15% for process fluid</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader title="Material Summary" />
              <CardContent className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-white/50">Carbon Steel</span>
                  <span className="text-white font-mono">42,500 lb</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-white/50">Aluminum</span>
                  <span className="text-white font-mono">8,960 lb</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-white/50">Alloy Steel</span>
                  <span className="text-white font-mono">11,680 lb</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
