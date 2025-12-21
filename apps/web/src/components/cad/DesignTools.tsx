"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";

interface ThermalData {
  duty: number;
  inletTemp: number;
  outletTemp: number;
  flowRate: number;
  fluid: string;
  airInletTemp: number;
  altitude: number;
}

interface WeightEstimate {
  category: string;
  dryWeight: number;
  operatingWeight: number;
}

const defaultThermalData: ThermalData = {
  duty: 45.2,
  inletTemp: 350,
  outletTemp: 150,
  flowRate: 125000,
  fluid: "Light Hydrocarbon",
  airInletTemp: 95,
  altitude: 0,
};

const weightEstimates: WeightEstimate[] = [
  { category: "Tube Bundles (2)", dryWeight: 24500, operatingWeight: 28200 },
  { category: "Headers & Plugs", dryWeight: 8200, operatingWeight: 8200 },
  { category: "Structure & Plenum", dryWeight: 18500, operatingWeight: 18500 },
  { category: "Fan Assembly (2)", dryWeight: 3200, operatingWeight: 3200 },
  { category: "Piping & Nozzles", dryWeight: 2100, operatingWeight: 2400 },
  { category: "Louvers & Accessories", dryWeight: 1800, operatingWeight: 1800 },
];

const api661Checklist = [
  { id: "1", item: "Design pressure per ASME VIII", status: "pass", notes: "450 PSIG @ 650°F" },
  { id: "2", item: "Tube material per Table 1", status: "pass", notes: "A179 Seamless Carbon Steel" },
  { id: "3", item: "Minimum tube wall thickness", status: "pass", notes: "14 BWG (0.083\")" },
  { id: "4", item: "Header box design", status: "pass", notes: "Removable cover type" },
  { id: "5", item: "Fin bond integrity test", status: "pending", notes: "Awaiting QC inspection" },
  { id: "6", item: "Hydrostatic test pressure", status: "pending", notes: "1.5x design = 675 PSIG" },
  { id: "7", item: "Nozzle reinforcement calc", status: "pass", notes: "Per ASME VIII UG-37" },
  { id: "8", item: "Fan tip clearance", status: "pass", notes: "1% of fan diameter" },
  { id: "9", item: "Vibration analysis", status: "warning", notes: "Review acoustic resonance" },
  { id: "10", item: "Corrosion allowance", status: "pass", notes: "1/8\" per spec" },
];

export function DesignTools() {
  const [thermalData] = useState<ThermalData>(defaultThermalData);
  const [activeSection, setActiveSection] = useState<"thermal" | "weight" | "compliance">("thermal");

  const totalDry = weightEstimates.reduce((sum, w) => sum + w.dryWeight, 0);
  const totalOp = weightEstimates.reduce((sum, w) => sum + w.operatingWeight, 0);

  const passCount = api661Checklist.filter(c => c.status === "pass").length;
  const pendingCount = api661Checklist.filter(c => c.status === "pending").length;
  const warningCount = api661Checklist.filter(c => c.status === "warning").length;

  return (
    <div className="space-y-4 mt-4">
      {/* Section Tabs */}
      <div className="flex gap-2 border-b border-white/10 pb-2">
        {[
          { id: "thermal", label: "Thermal Design", icon: "M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" },
          { id: "weight", label: "Weight Estimate", icon: "M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" },
          { id: "compliance", label: "API 661 Compliance", icon: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" },
        ].map((section) => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id as typeof activeSection)}
            className={`flex items-center gap-2 px-4 py-2 rounded-t-lg transition-colors ${
              activeSection === section.id
                ? "bg-white/10 text-white border-b-2 border-vulcan-accent"
                : "text-white/50 hover:text-white"
            }`}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={section.icon} />
            </svg>
            {section.label}
          </button>
        ))}
      </div>

      {/* Thermal Design Section */}
      {activeSection === "thermal" && (
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Input Parameters */}
          <Card>
            <CardHeader title="Process Conditions" subtitle="From HTRI thermal design" />
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div>
                  <label className="text-xs text-white/40 block mb-1">Heat Duty (MMBtu/hr)</label>
                  <input
                    type="number"
                    value={thermalData.duty}
                    readOnly
                    className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded text-white font-mono"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-white/40 block mb-1">Inlet Temp (°F)</label>
                    <input
                      type="number"
                      value={thermalData.inletTemp}
                      readOnly
                      className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded text-white font-mono"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-white/40 block mb-1">Outlet Temp (°F)</label>
                    <input
                      type="number"
                      value={thermalData.outletTemp}
                      readOnly
                      className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded text-white font-mono"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-xs text-white/40 block mb-1">Mass Flow (lb/hr)</label>
                  <input
                    type="number"
                    value={thermalData.flowRate}
                    readOnly
                    className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded text-white font-mono"
                  />
                </div>
                <div>
                  <label className="text-xs text-white/40 block mb-1">Process Fluid</label>
                  <input
                    type="text"
                    value={thermalData.fluid}
                    readOnly
                    className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded text-white"
                  />
                </div>
              </div>
              <Button variant="secondary" className="w-full">
                <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                Import from HTRI
              </Button>
            </CardContent>
          </Card>

          {/* Ambient Conditions */}
          <Card>
            <CardHeader title="Ambient Conditions" subtitle="Site design basis" />
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div>
                  <label className="text-xs text-white/40 block mb-1">Air Inlet Temp (°F)</label>
                  <input
                    type="number"
                    value={thermalData.airInletTemp}
                    readOnly
                    className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded text-white font-mono"
                  />
                </div>
                <div>
                  <label className="text-xs text-white/40 block mb-1">Altitude (ft)</label>
                  <input
                    type="number"
                    value={thermalData.altitude}
                    readOnly
                    className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded text-white font-mono"
                  />
                </div>
              </div>

              <div className="p-3 bg-white/5 rounded-lg space-y-2">
                <p className="text-xs text-white/40 uppercase tracking-wider">Calculated Values</p>
                <div className="flex justify-between text-sm">
                  <span className="text-white/50">LMTD</span>
                  <span className="text-white font-mono">127.3 °F</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-white/50">MTD Correction (F)</span>
                  <span className="text-white font-mono">0.92</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-white/50">Corrected MTD</span>
                  <span className="text-vulcan-accent font-mono">117.1 °F</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Sizing Summary */}
          <Card>
            <CardHeader title="Sizing Summary" subtitle="HTRI rating results" />
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-white/5 rounded-lg text-center">
                  <p className="text-2xl font-bold text-white">2</p>
                  <p className="text-xs text-white/40">Bays</p>
                </div>
                <div className="p-3 bg-white/5 rounded-lg text-center">
                  <p className="text-2xl font-bold text-white">4</p>
                  <p className="text-xs text-white/40">Total Bundles</p>
                </div>
                <div className="p-3 bg-white/5 rounded-lg text-center">
                  <p className="text-2xl font-bold text-white">30'</p>
                  <p className="text-xs text-white/40">Tube Length</p>
                </div>
                <div className="p-3 bg-white/5 rounded-lg text-center">
                  <p className="text-2xl font-bold text-white">14'</p>
                  <p className="text-xs text-white/40">Fan Diameter</p>
                </div>
              </div>

              <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-4 h-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-green-400 font-medium">Overdesign: 8.5%</span>
                </div>
                <p className="text-xs text-white/50">Within acceptable 5-15% margin</p>
              </div>

              <Button variant="primary" className="w-full">
                Generate Thermal Datasheet
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Weight Estimate Section */}
      {activeSection === "weight" && (
        <div className="grid lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader
              title="Weight Breakdown"
              subtitle="Per API 661 requirements"
              action={<Badge variant="info">E-4501 A/B</Badge>}
            />
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left py-3 px-4 text-xs text-white/40 uppercase tracking-wider">Component</th>
                      <th className="text-right py-3 px-4 text-xs text-white/40 uppercase tracking-wider">Dry Weight (lb)</th>
                      <th className="text-right py-3 px-4 text-xs text-white/40 uppercase tracking-wider">Operating (lb)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {weightEstimates.map((item, idx) => (
                      <tr key={idx} className="border-b border-white/5 hover:bg-white/5">
                        <td className="py-3 px-4 text-white">{item.category}</td>
                        <td className="py-3 px-4 text-right font-mono text-white/70">
                          {item.dryWeight.toLocaleString()}
                        </td>
                        <td className="py-3 px-4 text-right font-mono text-white/70">
                          {item.operatingWeight.toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr className="bg-white/5">
                      <td className="py-3 px-4 font-bold text-white">TOTAL</td>
                      <td className="py-3 px-4 text-right font-mono font-bold text-vulcan-accent">
                        {totalDry.toLocaleString()} lb
                      </td>
                      <td className="py-3 px-4 text-right font-mono font-bold text-vulcan-accent">
                        {totalOp.toLocaleString()} lb
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </CardContent>
          </Card>

          <div className="space-y-6">
            <Card>
              <CardHeader title="Weight Summary" />
              <CardContent className="space-y-4">
                <div className="p-4 bg-white/5 rounded-lg">
                  <p className="text-xs text-white/40 mb-1">Empty / Dry Weight</p>
                  <p className="text-2xl font-bold text-white font-mono">
                    {totalDry.toLocaleString()} <span className="text-sm text-white/50">lb</span>
                  </p>
                  <p className="text-xs text-white/40">
                    ({(totalDry / 2.205).toFixed(0).toLocaleString()} kg)
                  </p>
                </div>
                <div className="p-4 bg-vulcan-accent/20 rounded-lg border border-vulcan-accent/30">
                  <p className="text-xs text-white/40 mb-1">Operating Weight</p>
                  <p className="text-2xl font-bold text-vulcan-accent font-mono">
                    {totalOp.toLocaleString()} <span className="text-sm text-white/50">lb</span>
                  </p>
                  <p className="text-xs text-white/40">
                    ({(totalOp / 2.205).toFixed(0).toLocaleString()} kg)
                  </p>
                </div>
                <div className="p-4 bg-white/5 rounded-lg">
                  <p className="text-xs text-white/40 mb-1">Bundle Lift Weight (each)</p>
                  <p className="text-2xl font-bold text-white font-mono">
                    {(weightEstimates[0].dryWeight / 2).toLocaleString()} <span className="text-sm text-white/50">lb</span>
                  </p>
                </div>
              </CardContent>
            </Card>

            <Button variant="primary" className="w-full">
              Export Weight Report
            </Button>
          </div>
        </div>
      )}

      {/* API 661 Compliance Section */}
      {activeSection === "compliance" && (
        <div className="grid lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader
              title="API 661 Compliance Checklist"
              subtitle="Air-Cooled Heat Exchangers for General Refinery Service"
              action={
                <div className="flex gap-2">
                  <Badge variant="success">{passCount} Pass</Badge>
                  <Badge variant="warning">{pendingCount} Pending</Badge>
                  {warningCount > 0 && <Badge variant="error">{warningCount} Warning</Badge>}
                </div>
              }
            />
            <CardContent>
              <div className="space-y-2">
                {api661Checklist.map((item) => (
                  <div
                    key={item.id}
                    className={`flex items-center justify-between p-3 rounded-lg ${
                      item.status === "pass" ? "bg-green-500/10" :
                      item.status === "pending" ? "bg-amber-500/10" :
                      "bg-red-500/10"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                        item.status === "pass" ? "bg-green-500/20" :
                        item.status === "pending" ? "bg-amber-500/20" :
                        "bg-red-500/20"
                      }`}>
                        {item.status === "pass" && (
                          <svg className="w-4 h-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        )}
                        {item.status === "pending" && (
                          <svg className="w-4 h-4 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        )}
                        {item.status === "warning" && (
                          <svg className="w-4 h-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                        )}
                      </div>
                      <span className="text-white">{item.item}</span>
                    </div>
                    <span className={`text-sm ${
                      item.status === "pass" ? "text-green-400" :
                      item.status === "pending" ? "text-amber-400" :
                      "text-red-400"
                    }`}>
                      {item.notes}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <div className="space-y-6">
            <Card>
              <CardHeader title="Compliance Status" />
              <CardContent>
                <div className="relative w-32 h-32 mx-auto mb-4">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle cx="64" cy="64" r="56" fill="none" stroke="currentColor" strokeWidth="12" className="text-white/10" />
                    <circle
                      cx="64"
                      cy="64"
                      r="56"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="12"
                      strokeDasharray={`${(passCount / api661Checklist.length) * 351.86} 351.86`}
                      className="text-green-500"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <span className="text-2xl font-bold text-white">{Math.round((passCount / api661Checklist.length) * 100)}%</span>
                      <p className="text-xs text-white/40">Complete</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-white/50">Standard</span>
                    <span className="text-white">API 661 8th Ed.</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/50">Pressure Code</span>
                    <span className="text-white">ASME VIII Div 1</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/50">Material Code</span>
                    <span className="text-white">ASME II Part D</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader title="Actions" />
              <CardContent className="space-y-2">
                <Button variant="primary" className="w-full">
                  Generate Compliance Report
                </Button>
                <Button variant="secondary" className="w-full">
                  Export for Customer Review
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
