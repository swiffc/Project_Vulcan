"use client";

import { useState, useCallback, useEffect } from "react";
import toast from "react-hot-toast";

interface ACHECategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  endpoints: ACHEEndpoint[];
}

interface ACHEEndpoint {
  id: string;
  name: string;
  description: string;
  method: "GET" | "POST";
  path: string;
  hasParams: boolean;
}

interface ACHEStatus {
  ache_available: boolean;
  listener_active: boolean;
  current_model: string | null;
}

const API_BASE = process.env.NEXT_PUBLIC_DESKTOP_SERVER_URL || "http://localhost:8000";

const ACHE_CATEGORIES: ACHECategory[] = [
  {
    id: "calculations",
    name: "Calculations",
    description: "Thermal, fan, and pressure drop calculations",
    icon: "M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z",
    color: "from-cyan-500 to-blue-500",
    endpoints: [
      { id: "thermal", name: "Thermal Performance", description: "LMTD/NTU-effectiveness calculation", method: "POST", path: "/ache/calculate/thermal", hasParams: true },
      { id: "fan", name: "Fan Performance", description: "Power, tip speed per API 661", method: "POST", path: "/ache/calculate/fan", hasParams: true },
      { id: "pressure_tube", name: "Tube Pressure Drop", description: "Tube-side pressure loss", method: "POST", path: "/ache/calculate/pressure-drop/tube", hasParams: true },
      { id: "pressure_air", name: "Air Pressure Drop", description: "Air-side pressure loss", method: "POST", path: "/ache/calculate/pressure-drop/air", hasParams: true },
      { id: "size", name: "Preliminary Sizing", description: "Quick ACHE sizing estimate", method: "POST", path: "/ache/calculate/size", hasParams: true },
      { id: "batch_fan", name: "Batch Fan Calc", description: "Multiple fan configurations", method: "POST", path: "/ache/calculate/batch/fan", hasParams: true },
    ],
  },
  {
    id: "design",
    name: "Structural Design",
    description: "Frame, columns, beams, access systems",
    icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4",
    color: "from-amber-500 to-orange-500",
    endpoints: [
      { id: "frame", name: "Frame Design", description: "Complete support structure per AISC", method: "POST", path: "/ache/design/frame", hasParams: true },
      { id: "column", name: "Column Design", description: "Column per AISC (KL/r ≤ 200)", method: "POST", path: "/ache/design/column", hasParams: true },
      { id: "beam", name: "Beam Design", description: "Beam per AISC (L/240)", method: "POST", path: "/ache/design/beam", hasParams: true },
      { id: "anchor", name: "Anchor Bolts", description: "Foundation bolt design", method: "POST", path: "/ache/design/anchor-bolts", hasParams: true },
      { id: "access", name: "Access System", description: "Platforms, ladders per OSHA", method: "POST", path: "/ache/design/access", hasParams: true },
    ],
  },
  {
    id: "ai",
    name: "AI Assistant",
    description: "Compliance, recommendations, troubleshooting",
    icon: "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z",
    color: "from-purple-500 to-pink-500",
    endpoints: [
      { id: "compliance", name: "API 661 Compliance", description: "Check design against standard", method: "POST", path: "/ache/compliance/check", hasParams: true },
      { id: "recommendations", name: "AI Recommendations", description: "Design optimization suggestions", method: "POST", path: "/ache/ai/recommendations", hasParams: true },
      { id: "troubleshoot", name: "Troubleshooting", description: "Problem diagnosis guide", method: "GET", path: "/ache/ai/troubleshoot/{problem}", hasParams: true },
      { id: "knowledge", name: "Knowledge Base", description: "Query ACHE engineering database", method: "GET", path: "/ache/ai/knowledge", hasParams: true },
      { id: "optimize", name: "Optimize Design", description: "Cost/efficiency suggestions", method: "POST", path: "/ache/optimize/suggestions", hasParams: true },
    ],
  },
  {
    id: "erection",
    name: "Erection Planning",
    description: "Lifting, rigging, and installation",
    icon: "M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z",
    color: "from-emerald-500 to-teal-500",
    endpoints: [
      { id: "plan", name: "Erection Plan", description: "Complete lift & install sequence", method: "POST", path: "/ache/erection/plan", hasParams: true },
      { id: "lifting_lug", name: "Lifting Lug Design", description: "Per ASME BTH-1", method: "POST", path: "/ache/erection/lifting-lug", hasParams: true },
    ],
  },
  {
    id: "export",
    name: "Export & Reports",
    description: "Datasheet, BOM, documentation",
    icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
    color: "from-red-500 to-rose-500",
    endpoints: [
      { id: "datasheet", name: "Export Datasheet", description: "API 661 compliant datasheet", method: "POST", path: "/ache/export/datasheet", hasParams: true },
      { id: "bom", name: "Export BOM", description: "Bill of Materials", method: "POST", path: "/ache/export/bom", hasParams: true },
      { id: "standards", name: "API 661 Reference", description: "Key requirements lookup", method: "GET", path: "/ache/standards/api661", hasParams: false },
    ],
  },
];

// Default test parameters for each endpoint
const DEFAULT_PARAMS: Record<string, object> = {
  thermal: {
    duty_kw: 1000,
    process_inlet_temp_c: 120,
    process_outlet_temp_c: 60,
    air_inlet_temp_c: 35,
    air_flow_kg_s: 100,
    surface_area_m2: 500,
    u_clean_w_m2_k: 45.0,
    fouling_factor: 0.0002,
  },
  fan: {
    air_flow_m3_s: 50,
    static_pressure_pa: 200,
    fan_diameter_m: 3.0,
    fan_rpm: 300,
    fan_efficiency: 0.75,
  },
  pressure_tube: {
    mass_flow_kg_s: 50,
    tube_id_mm: 22,
    tube_length_m: 6,
    num_tubes: 500,
    num_passes: 4,
    fluid_density_kg_m3: 800,
    fluid_viscosity_pa_s: 0.001,
  },
  pressure_air: {
    air_flow_kg_s: 100,
    air_inlet_temp_c: 35,
    bundle_face_area_m2: 30,
    tube_od_mm: 25.4,
    fin_pitch_mm: 2.5,
    fin_height_mm: 12.7,
    num_tube_rows: 4,
  },
  size: {
    duty_kw: 1000,
    process_inlet_temp_c: 120,
    process_outlet_temp_c: 60,
    air_inlet_temp_c: 35,
  },
  frame: {
    bundle_weight_kn: 500,
    bundle_length_m: 12,
    bundle_width_m: 3,
    bundle_height_m: 2,
    num_bays: 2,
    elevation_m: 4.0,
    wind_speed_m_s: 40.0,
  },
  access: {
    bundle_length_m: 12,
    bundle_width_m: 3,
    elevation_m: 5,
    num_bays: 2,
    fan_deck_required: true,
    header_access_required: true,
  },
  compliance: {
    tube_bundle: { tube_length_m: 10, tube_od_mm: 25.4 },
    fan_system: { tip_speed_m_s: 55 },
  },
  recommendations: {
    thermal_performance: { approach_temp_c: 8 },
  },
  optimize: {
    optimization_targets: ["cost", "efficiency", "footprint"],
  },
  plan: {
    project_name: "Test Project",
    equipment_tag: "AC-101",
    ache_properties: {
      mass_properties: { mass_kg: 50000 },
      bounding_box: { length_mm: 12000, width_mm: 3000, height_mm: 4000 },
      fan_system: { num_fans: 2 },
    },
  },
  datasheet: {
    equipment_tag: "AC-101",
    service: "Cooling",
    thermal: { duty_kw: 1000 },
    fan_system: { num_fans: 2 },
  },
  bom: {
    equipment_tag: "AC-101",
    tube_bundle: { num_tubes: 500, tube_od_mm: 25.4, tube_length_m: 6 },
    fan_system: { num_fans: 2, fan_diameter_m: 3.0 },
  },
};

export function ACHEPanel() {
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [executingEndpoint, setExecutingEndpoint] = useState<string | null>(null);
  const [status, setStatus] = useState<ACHEStatus | null>(null);
  const [statusLoading, setStatusLoading] = useState(true);
  const [result, setResult] = useState<{ endpoint: string; success: boolean; data: unknown } | null>(null);
  const [showResultModal, setShowResultModal] = useState(false);

  // Check ACHE status on mount
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await fetch(`${API_BASE}/ache/status`);
        if (res.ok) {
          const data = await res.json();
          setStatus(data);
        } else {
          setStatus({ ache_available: false, listener_active: false, current_model: null });
        }
      } catch {
        setStatus({ ache_available: false, listener_active: false, current_model: null });
      } finally {
        setStatusLoading(false);
      }
    };
    checkStatus();
    const interval = setInterval(checkStatus, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const executeEndpoint = useCallback(async (endpoint: ACHEEndpoint) => {
    setExecutingEndpoint(endpoint.id);
    setResult(null);

    try {
      let url = `${API_BASE}${endpoint.path}`;
      const options: RequestInit = {
        method: endpoint.method,
        headers: { "Content-Type": "application/json" },
      };

      if (endpoint.method === "POST") {
        options.body = JSON.stringify(DEFAULT_PARAMS[endpoint.id] || {});
      } else if (endpoint.method === "GET" && endpoint.hasParams) {
        // Handle GET with query params
        if (endpoint.id === "troubleshoot") {
          url = url.replace("{problem}", encodeURIComponent("high temperature"));
        } else if (endpoint.id === "knowledge") {
          url += "?query=tube%20selection";
        }
      }

      const res = await fetch(url, options);
      const data = await res.json();

      if (res.ok) {
        toast.success(`${endpoint.name} completed`);
        setResult({ endpoint: endpoint.name, success: true, data });
        setShowResultModal(true);
      } else {
        toast.error(data.detail || "Request failed");
        setResult({ endpoint: endpoint.name, success: false, data });
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Connection failed";
      toast.error(errorMsg);
      setResult({ endpoint: endpoint.name, success: false, data: { error: errorMsg } });
    } finally {
      setExecutingEndpoint(null);
    }
  }, []);

  const filteredCategories = ACHE_CATEGORIES.map((category) => ({
    ...category,
    endpoints: category.endpoints.filter(
      (ep) =>
        ep.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ep.description.toLowerCase().includes(searchQuery.toLowerCase())
    ),
  })).filter((category) => category.endpoints.length > 0 || searchQuery === "");

  const totalEndpoints = ACHE_CATEGORIES.reduce((sum, cat) => sum + cat.endpoints.length, 0);

  return (
    <div className="space-y-6">
      {/* Header with Status */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            ACHE Design Assistant
            <span className="text-xs px-2 py-0.5 bg-vulcan-accent/20 text-vulcan-accent rounded-full">
              Phase 24
            </span>
          </h2>
          <p className="text-white/50">
            {totalEndpoints} endpoints for Air Cooled Heat Exchanger design per API 661
          </p>
        </div>

        <div className="flex items-center gap-4">
          {/* Status Indicator */}
          <div className="flex items-center gap-3 px-4 py-2 rounded-lg bg-white/5 border border-white/10">
            <div className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  statusLoading
                    ? "bg-yellow-400 animate-pulse"
                    : status?.ache_available
                    ? "bg-green-400"
                    : "bg-red-400"
                }`}
              />
              <span className="text-sm text-white/70">
                {statusLoading ? "Checking..." : status?.ache_available ? "Connected" : "Offline"}
              </span>
            </div>
            {status?.current_model && (
              <span className="text-xs text-white/40 border-l border-white/10 pl-3">
                {status.current_model}
              </span>
            )}
          </div>

          {/* Search */}
          <div className="relative">
            <svg
              className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <input
              type="text"
              placeholder="Search endpoints..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:border-vulcan-accent w-64"
            />
          </div>
        </div>
      </div>

      {/* Categories Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {filteredCategories.map((category) => (
          <div
            key={category.id}
            className={`glass rounded-2xl overflow-hidden transition-all cursor-pointer ${
              activeCategory === category.id ? "ring-2 ring-vulcan-accent" : ""
            }`}
            onClick={() => setActiveCategory(activeCategory === category.id ? null : category.id)}
          >
            {/* Category Header */}
            <div className={`p-4 bg-gradient-to-r ${category.color} bg-opacity-20`}>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={category.icon} />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-white">{category.name}</h3>
                  <p className="text-xs text-white/60">{category.endpoints.length} endpoints</p>
                </div>
              </div>
            </div>

            {/* Endpoints List */}
            <div
              className={`transition-all overflow-hidden ${
                activeCategory === category.id ? "max-h-96" : "max-h-0"
              }`}
            >
              <div className="p-3 space-y-1 max-h-80 overflow-y-auto">
                {category.endpoints.map((endpoint) => (
                  <button
                    key={endpoint.id}
                    className={`w-full text-left p-2 rounded-lg hover:bg-white/10 transition-colors group ${
                      executingEndpoint === endpoint.id ? "bg-vulcan-accent/20 animate-pulse" : ""
                    }`}
                    disabled={executingEndpoint !== null}
                    onClick={(e) => {
                      e.stopPropagation();
                      executeEndpoint(endpoint);
                    }}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-white">{endpoint.name}</span>
                      <span
                        className={`text-xs px-1.5 py-0.5 rounded ${
                          endpoint.method === "GET"
                            ? "bg-green-500/20 text-green-400"
                            : "bg-blue-500/20 text-blue-400"
                        }`}
                      >
                        {endpoint.method}
                      </span>
                    </div>
                    <p className="text-xs text-white/40 mt-0.5">{endpoint.description}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Collapsed Preview */}
            {activeCategory !== category.id && (
              <div className="p-3 border-t border-white/10">
                <p className="text-xs text-white/40">{category.description}</p>
                <p className="text-xs text-vulcan-accent mt-1">Click to expand</p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* API 661 Quick Reference */}
      <div className="glass rounded-2xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">API 661 / ISO 13706 Quick Reference</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {[
            { param: "Max Tube Length", value: "12.0 m", ref: "5.1.1" },
            { param: "Min Tube Wall", value: "2.11 mm (BWG 14)", ref: "5.1.3" },
            { param: "Max Fan Tip Speed", value: "61 m/s", ref: "6.1.1" },
            { param: "Min Blade Clearance", value: "12.7 mm", ref: "Table 6" },
            { param: "Header Split", value: "ΔT > 110°C", ref: "7.1.6.1.2" },
            { param: "Max Air ΔP", value: "250 Pa", ref: "6.2.1" },
          ].map((item) => (
            <div key={item.param} className="p-3 rounded-lg bg-white/5 border border-white/10">
              <p className="text-xs text-white/40">{item.param}</p>
              <p className="text-sm font-medium text-white">{item.value}</p>
              <p className="text-xs text-vulcan-accent mt-1">Ref: {item.ref}</p>
            </div>
          ))}
        </div>
      </div>

      {/* OSHA Requirements */}
      <div className="glass rounded-2xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">OSHA 1910 Access Requirements</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { param: "Walkway Width", value: "≥ 450 mm", ref: "1910.22" },
            { param: "Handrail Height", value: "≥ 1070 mm", ref: "1910.29" },
            { param: "Ladder Cage", value: "> 6.1 m", ref: "1910.28" },
            { param: "Toe Plate", value: "≥ 89 mm", ref: "1910.29" },
          ].map((item) => (
            <div key={item.param} className="p-3 rounded-lg bg-white/5 border border-white/10">
              <p className="text-xs text-white/40">{item.param}</p>
              <p className="text-sm font-medium text-white">{item.value}</p>
              <p className="text-xs text-emerald-400 mt-1">OSHA {item.ref}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Result Modal */}
      {showResultModal && result && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="glass rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
            <div className="p-4 border-b border-white/10 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div
                  className={`w-3 h-3 rounded-full ${
                    result.success ? "bg-green-400" : "bg-red-400"
                  }`}
                />
                <h3 className="text-lg font-semibold text-white">{result.endpoint}</h3>
              </div>
              <button
                onClick={() => setShowResultModal(false)}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                <svg className="w-5 h-5 text-white/60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-4 overflow-auto max-h-[60vh]">
              <pre className="text-sm text-white/80 whitespace-pre-wrap font-mono bg-black/30 p-4 rounded-lg">
                {JSON.stringify(result.data, null, 2)}
              </pre>
            </div>
            <div className="p-4 border-t border-white/10 flex justify-end">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(JSON.stringify(result.data, null, 2));
                  toast.success("Copied to clipboard");
                }}
                className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white text-sm transition-colors"
              >
                Copy JSON
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
