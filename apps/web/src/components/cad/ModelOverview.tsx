"use client";

import { useEffect, useState, useCallback } from "react";

interface ModelProperties {
  standard: {
    filename: string;
    path: string;
    configuration: string;
    sw_version: string;
  };
  mass: {
    mass_kg: number;
    volume_m3: number;
    surface_area_m2: number;
    center_of_gravity: number[];
    moments_of_inertia: number[];
  };
  custom: {
    job_info: Record<string, string>;
    design_data: Record<string, string>;
    tube_bundle: Record<string, string>;
    header_box: Record<string, string>;
    structural: Record<string, string>;
    drawing_info: Record<string, string>;
    paint_coating: Record<string, string>;
    other: Record<string, string>;
  };
}

interface AnalysisResults {
  hole_analysis: {
    total_holes: number;
    patterns: Array<{ type: string; count: number }>;
    edge_distance_violations: Array<{ hole: string; edge: string }>;
    ligament_violations: Array<{ hole1: string; hole2: string }>;
  };
  bend_analysis: {
    total_bends: number;
    violations: Array<{ feature: string; issue: string }>;
  };
  mates_analysis?: {
    total_mates: number;
    satisfied: number;
    broken: number;
    over_defined: number;
    issues: string[];
  };
  interference_check?: {
    total_interferences: number;
    interferences: Array<{ component1: string; component2: string }>;
  };
}

interface QuickStat {
  label: string;
  value: string | number;
  unit?: string;
  icon: string;
  status?: "ok" | "warning" | "error";
}

export function ModelOverview() {
  const [properties, setProperties] = useState<ModelProperties | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [activeSection, setActiveSection] = useState<string>("overview");

  const fetchModelData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch properties and full analysis in parallel
      const [propsRes, analysisRes] = await Promise.all([
        fetch("/api/desktop/phase24/properties"),
        fetch("/api/desktop/phase24/full-analysis"),
      ]);

      if (propsRes.ok) {
        const propsData = await propsRes.json();
        setProperties(propsData);
      }

      if (analysisRes.ok) {
        const analysisData = await analysisRes.json();
        setAnalysis(analysisData);
      }

      setLastUpdate(new Date());
    } catch (err) {
      setError("Failed to fetch model data");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchModelData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchModelData, 30000);
    return () => clearInterval(interval);
  }, [fetchModelData]);

  // Calculate quick stats
  const quickStats: QuickStat[] = properties
    ? [
        {
          label: "Mass",
          value: properties.mass.mass_kg.toFixed(2),
          unit: "kg",
          icon: "M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3",
        },
        {
          label: "Volume",
          value: (properties.mass.volume_m3 * 1e6).toFixed(1),
          unit: "cm³",
          icon: "M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4",
        },
        {
          label: "Surface Area",
          value: (properties.mass.surface_area_m2 * 1e4).toFixed(0),
          unit: "cm²",
          icon: "M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z",
        },
        {
          label: "Holes",
          value: analysis?.hole_analysis?.total_holes ?? 0,
          icon: "M15 12a3 3 0 11-6 0 3 3 0 016 0z",
          status:
            (analysis?.hole_analysis?.edge_distance_violations?.length ?? 0) > 0
              ? "warning"
              : "ok",
        },
        {
          label: "Mates",
          value: analysis?.mates_analysis?.total_mates ?? 0,
          icon: "M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1",
          status:
            (analysis?.mates_analysis?.broken ?? 0) > 0
              ? "error"
              : (analysis?.mates_analysis?.over_defined ?? 0) > 0
              ? "warning"
              : "ok",
        },
        {
          label: "Interferences",
          value: analysis?.interference_check?.total_interferences ?? 0,
          icon: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z",
          status:
            (analysis?.interference_check?.total_interferences ?? 0) > 0
              ? "error"
              : "ok",
        },
      ]
    : [];

  // Count warnings
  const warningCount =
    (analysis?.hole_analysis?.edge_distance_violations?.length ?? 0) +
    (analysis?.hole_analysis?.ligament_violations?.length ?? 0) +
    (analysis?.mates_analysis?.over_defined ?? 0) +
    (analysis?.bend_analysis?.violations?.length ?? 0);

  const errorCount =
    (analysis?.mates_analysis?.broken ?? 0) +
    (analysis?.interference_check?.total_interferences ?? 0);

  if (loading && !properties) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-3 text-white/60">
          <svg
            className="w-6 h-6 animate-spin"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
          <span>Loading model data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-red-400 mb-2">{error}</div>
          <button
            onClick={fetchModelData}
            className="px-4 py-2 bg-vulcan-accent text-white rounded-lg hover:bg-vulcan-accent/80"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with refresh and status */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">
            {properties?.standard.filename || "No Model Open"}
          </h2>
          <p className="text-sm text-white/50">
            {properties?.standard.configuration && (
              <span>Config: {properties.standard.configuration} | </span>
            )}
            SolidWorks {properties?.standard.sw_version}
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Issue Summary */}
          {(errorCount > 0 || warningCount > 0) && (
            <div className="flex items-center gap-2">
              {errorCount > 0 && (
                <span className="px-2 py-1 rounded-full bg-red-500/20 text-red-400 text-sm">
                  {errorCount} error{errorCount !== 1 ? "s" : ""}
                </span>
              )}
              {warningCount > 0 && (
                <span className="px-2 py-1 rounded-full bg-amber-500/20 text-amber-400 text-sm">
                  {warningCount} warning{warningCount !== 1 ? "s" : ""}
                </span>
              )}
            </div>
          )}

          {/* Last update */}
          {lastUpdate && (
            <span className="text-xs text-white/40">
              Updated {lastUpdate.toLocaleTimeString()}
            </span>
          )}

          {/* Refresh button */}
          <button
            onClick={fetchModelData}
            disabled={loading}
            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-white/60 hover:text-white transition-colors disabled:opacity-50"
          >
            <svg
              className={`w-4 h-4 ${loading ? "animate-spin" : ""}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Quick Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {quickStats.map((stat) => (
          <div
            key={stat.label}
            className={`p-4 rounded-xl border ${
              stat.status === "error"
                ? "bg-red-500/10 border-red-500/30"
                : stat.status === "warning"
                ? "bg-amber-500/10 border-amber-500/30"
                : "bg-white/5 border-white/10"
            }`}
          >
            <div className="flex items-center gap-2 mb-2">
              <svg
                className={`w-4 h-4 ${
                  stat.status === "error"
                    ? "text-red-400"
                    : stat.status === "warning"
                    ? "text-amber-400"
                    : "text-white/40"
                }`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d={stat.icon}
                />
              </svg>
              <span className="text-xs text-white/50">{stat.label}</span>
            </div>
            <div className="text-xl font-semibold text-white">
              {stat.value}
              {stat.unit && (
                <span className="text-sm font-normal text-white/40 ml-1">
                  {stat.unit}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Section Tabs */}
      <div className="border-b border-white/10">
        <div className="flex gap-1">
          {[
            { id: "overview", label: "Overview" },
            { id: "properties", label: "Properties" },
            { id: "ache", label: "ACHE Data" },
            { id: "issues", label: `Issues (${errorCount + warningCount})` },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveSection(tab.id)}
              className={`px-4 py-2 text-sm font-medium transition-all border-b-2 -mb-px ${
                activeSection === tab.id
                  ? "text-white border-vulcan-accent"
                  : "text-white/50 border-transparent hover:text-white/80"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Section Content */}
      <div className="min-h-[300px]">
        {activeSection === "overview" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Mass Properties Card */}
            <div className="p-6 rounded-xl bg-white/5 border border-white/10">
              <h3 className="text-lg font-medium text-white mb-4">
                Mass Properties
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-white/60">Mass</span>
                  <span className="text-white">
                    {properties?.mass.mass_kg.toFixed(3)} kg (
                    {(properties?.mass.mass_kg ?? 0 * 2.205).toFixed(2)} lbs)
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/60">Volume</span>
                  <span className="text-white">
                    {((properties?.mass.volume_m3 ?? 0) * 1e6).toFixed(2)} cm³
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/60">Surface Area</span>
                  <span className="text-white">
                    {((properties?.mass.surface_area_m2 ?? 0) * 1e4).toFixed(2)}{" "}
                    cm²
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/60">Center of Gravity</span>
                  <span className="text-white font-mono text-sm">
                    ({properties?.mass.center_of_gravity.map((v) => v.toFixed(3)).join(", ")})
                  </span>
                </div>
              </div>
            </div>

            {/* Mates Summary Card */}
            {analysis?.mates_analysis && (
              <div className="p-6 rounded-xl bg-white/5 border border-white/10">
                <h3 className="text-lg font-medium text-white mb-4">
                  Mates Summary
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-white/60">Total Mates</span>
                    <span className="text-white">
                      {analysis.mates_analysis.total_mates}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/60">Satisfied</span>
                    <span className="text-emerald-400">
                      {analysis.mates_analysis.satisfied}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/60">Over-defined</span>
                    <span
                      className={
                        analysis.mates_analysis.over_defined > 0
                          ? "text-amber-400"
                          : "text-white"
                      }
                    >
                      {analysis.mates_analysis.over_defined}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/60">Broken</span>
                    <span
                      className={
                        analysis.mates_analysis.broken > 0
                          ? "text-red-400"
                          : "text-white"
                      }
                    >
                      {analysis.mates_analysis.broken}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeSection === "properties" && properties && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Standard Properties */}
            <div className="p-6 rounded-xl bg-white/5 border border-white/10">
              <h3 className="text-lg font-medium text-white mb-4">
                Standard Properties
              </h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-white/60">Filename</span>
                  <span className="text-white">{properties.standard.filename}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/60">Path</span>
                  <span className="text-white/80 text-xs max-w-[300px] truncate">
                    {properties.standard.path}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/60">Configuration</span>
                  <span className="text-white">{properties.standard.configuration}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/60">SW Version</span>
                  <span className="text-white">{properties.standard.sw_version}</span>
                </div>
              </div>
            </div>

            {/* Custom Properties (Other) */}
            {Object.keys(properties.custom.other).length > 0 && (
              <div className="p-6 rounded-xl bg-white/5 border border-white/10">
                <h3 className="text-lg font-medium text-white mb-4">
                  Custom Properties
                </h3>
                <div className="space-y-2 text-sm max-h-[300px] overflow-y-auto">
                  {Object.entries(properties.custom.other).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-white/60">{key}</span>
                      <span className="text-white">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeSection === "ache" && properties && (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {/* Job Info */}
            {Object.keys(properties.custom.job_info).length > 0 && (
              <PropertyCard title="Job Information" data={properties.custom.job_info} />
            )}

            {/* Design Data */}
            {Object.keys(properties.custom.design_data).length > 0 && (
              <PropertyCard title="Design Data" data={properties.custom.design_data} />
            )}

            {/* Tube Bundle */}
            {Object.keys(properties.custom.tube_bundle).length > 0 && (
              <PropertyCard title="Tube Bundle" data={properties.custom.tube_bundle} />
            )}

            {/* Header Box */}
            {Object.keys(properties.custom.header_box).length > 0 && (
              <PropertyCard title="Header Box" data={properties.custom.header_box} />
            )}

            {/* Structural */}
            {Object.keys(properties.custom.structural).length > 0 && (
              <PropertyCard title="Structural Data" data={properties.custom.structural} />
            )}

            {/* Drawing Info */}
            {Object.keys(properties.custom.drawing_info).length > 0 && (
              <PropertyCard title="Drawing Info" data={properties.custom.drawing_info} />
            )}

            {/* Empty state */}
            {Object.keys(properties.custom.job_info).length === 0 &&
              Object.keys(properties.custom.design_data).length === 0 &&
              Object.keys(properties.custom.tube_bundle).length === 0 && (
                <div className="col-span-full text-center py-12 text-white/40">
                  No ACHE-specific properties found in this model.
                  <br />
                  <span className="text-sm">
                    Add custom properties with ACHE-related names to see them here.
                  </span>
                </div>
              )}
          </div>
        )}

        {activeSection === "issues" && (
          <div className="space-y-4">
            {/* Broken Mates */}
            {(analysis?.mates_analysis?.broken ?? 0) > 0 && (
              <IssueCard
                severity="error"
                title="Broken Mates"
                count={analysis?.mates_analysis?.broken ?? 0}
                items={analysis?.mates_analysis?.issues?.filter((i) =>
                  i.includes("Broken")
                ) ?? []}
              />
            )}

            {/* Interferences */}
            {(analysis?.interference_check?.total_interferences ?? 0) > 0 && (
              <IssueCard
                severity="error"
                title="Interferences Detected"
                count={analysis?.interference_check?.total_interferences ?? 0}
                items={
                  analysis?.interference_check?.interferences?.map(
                    (i) => `${i.component1} ↔ ${i.component2}`
                  ) ?? []
                }
              />
            )}

            {/* Over-defined Mates */}
            {(analysis?.mates_analysis?.over_defined ?? 0) > 0 && (
              <IssueCard
                severity="warning"
                title="Over-defined Mates"
                count={analysis?.mates_analysis?.over_defined ?? 0}
                items={analysis?.mates_analysis?.issues?.filter((i) =>
                  i.includes("Over")
                ) ?? []}
              />
            )}

            {/* Edge Distance Violations */}
            {(analysis?.hole_analysis?.edge_distance_violations?.length ?? 0) > 0 && (
              <IssueCard
                severity="warning"
                title="Edge Distance Violations"
                count={analysis?.hole_analysis?.edge_distance_violations?.length ?? 0}
                items={
                  analysis?.hole_analysis?.edge_distance_violations?.map(
                    (v) => `${v.hole}: Too close to ${v.edge} edge`
                  ) ?? []
                }
              />
            )}

            {/* No issues */}
            {errorCount === 0 && warningCount === 0 && (
              <div className="text-center py-12">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-emerald-500/20 flex items-center justify-center">
                  <svg
                    className="w-8 h-8 text-emerald-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-white mb-2">No Issues Found</h3>
                <p className="text-white/50">All checks passed successfully.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// Helper Components
function PropertyCard({
  title,
  data,
}: {
  title: string;
  data: Record<string, string>;
}) {
  return (
    <div className="p-4 rounded-xl bg-white/5 border border-white/10">
      <h4 className="text-sm font-medium text-white/80 mb-3">{title}</h4>
      <div className="space-y-2 text-sm">
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="flex justify-between gap-4">
            <span className="text-white/50 truncate">{key}</span>
            <span className="text-white truncate max-w-[150px]">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function IssueCard({
  severity,
  title,
  count,
  items,
}: {
  severity: "error" | "warning";
  title: string;
  count: number;
  items: string[];
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className={`rounded-xl border ${
        severity === "error"
          ? "bg-red-500/10 border-red-500/30"
          : "bg-amber-500/10 border-amber-500/30"
      }`}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          <div
            className={`w-2 h-2 rounded-full ${
              severity === "error" ? "bg-red-400" : "bg-amber-400"
            }`}
          />
          <span className="font-medium text-white">{title}</span>
          <span
            className={`px-2 py-0.5 rounded-full text-xs ${
              severity === "error"
                ? "bg-red-500/30 text-red-300"
                : "bg-amber-500/30 text-amber-300"
            }`}
          >
            {count}
          </span>
        </div>
        <svg
          className={`w-4 h-4 text-white/50 transition-transform ${
            expanded ? "rotate-180" : ""
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {expanded && items.length > 0 && (
        <div className="px-4 pb-4 pt-0">
          <div className="pl-5 space-y-1 text-sm text-white/70">
            {items.slice(0, 10).map((item, i) => (
              <div key={i} className="py-1 border-t border-white/5 first:border-0">
                {item}
              </div>
            ))}
            {items.length > 10 && (
              <div className="text-white/40 italic">
                ...and {items.length - 10} more
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
