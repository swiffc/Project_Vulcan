"use client";

import { useState, useEffect } from "react";

interface BOMItem {
  item: number;
  part_number: string;
  description: string;
  type: string;
  qty: number;
  level?: number;
  suppressed?: boolean;
  file_path?: string;
  properties?: Record<string, string>;
  children?: BOMItem[];
}

interface BOMData {
  assembly_name: string;
  assembly_properties?: Record<string, string>;
  total_unique_parts: number;
  total_parts?: number;
  total_sub_assemblies?: number;
  bom: BOMItem[];
  hierarchical_bom?: BOMItem[];
}

interface PartGeometry {
  mass_kg: number;
  volume_m3: number;
  surface_area_m2: number;
  bounding_box?: {
    x: number;
    y: number;
    z: number;
  };
}

interface PartFeatures {
  total: number;
  holes: number;
  fillets: number;
  chamfers: number;
  patterns: number;
  hole_details?: { name: string; type: string; diameter?: number }[];
}

interface PartAnalysis {
  part_number: string;
  suggested_name?: string;
  part_type: string;
  purpose: string;
  recommendations: string[];
  potential_issues: string[];
  related_parts: string[];
  confidence: number;
  geometry?: PartGeometry;
  material?: { name?: string; density?: number };
  features?: PartFeatures;
  mates?: { type: string; name: string }[];
}

interface AssemblyInsights {
  assembly_category: string;
  part_type_distribution: Record<string, number>;
  dominant_types: [string, number][];
  recommendations: string[];
  suggested_improvements: { area: string; suggestion: string; priority: string }[];
  complexity_score: number;
}

interface AnalysisData {
  assembly_name: string;
  total_parts_analyzed: number;
  part_analyses: PartAnalysis[];
  assembly_insights: AssemblyInsights;
  timestamp: string;
}

interface BOMPreviewProps {
  isOpen: boolean;
  onClose: () => void;
  autoAnalyze?: boolean;
}

// Expandable row component for hierarchical view
function BOMRow({
  item,
  expanded,
  onToggle,
  expandedProps,
  onToggleProps
}: {
  item: BOMItem;
  expanded: Set<string>;
  onToggle: (pn: string) => void;
  expandedProps: Set<string>;
  onToggleProps: (pn: string) => void;
}) {
  const hasChildren = item.children && item.children.length > 0;
  const hasProperties = item.properties && Object.keys(item.properties).length > 0;
  const isExpanded = expanded.has(item.part_number);
  const isPropsExpanded = expandedProps.has(item.part_number);
  const indent = (item.level || 0) * 24;

  return (
    <>
      <tr className={`hover:bg-white/5 transition-colors ${item.suppressed ? "opacity-50" : ""}`}>
        <td className="px-4 py-3 text-sm text-white/70 font-mono w-16">{item.item}</td>
        <td className="px-4 py-3 text-sm" style={{ paddingLeft: `${16 + indent}px` }}>
          <div className="flex items-center gap-2">
            {hasChildren && (
              <button
                onClick={() => onToggle(item.part_number)}
                className="w-5 h-5 flex items-center justify-center rounded hover:bg-white/10 transition-colors"
              >
                <svg
                  className={`w-4 h-4 text-white/60 transition-transform ${isExpanded ? "rotate-90" : ""}`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            )}
            {!hasChildren && <span className="w-5" />}
            <span className="text-white font-medium">{item.part_number}</span>
            {item.suppressed && (
              <span className="text-xs text-yellow-400/70">(Suppressed)</span>
            )}
          </div>
        </td>
        <td className="px-4 py-3 text-sm text-white/70">{item.description}</td>
        <td className="px-4 py-3">
          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
            item.type === "Sub-Assembly"
              ? "bg-purple-500/20 text-purple-300"
              : "bg-emerald-500/20 text-emerald-300"
          }`}>
            {item.type}
          </span>
        </td>
        <td className="px-4 py-3 text-sm text-white text-center font-semibold w-16">{item.qty}</td>
        <td className="px-4 py-3 w-12">
          {hasProperties && (
            <button
              onClick={() => onToggleProps(item.part_number)}
              className={`p-1 rounded hover:bg-white/10 transition-colors ${isPropsExpanded ? "bg-indigo-500/20" : ""}`}
              title="Show properties"
            >
              <svg className="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
          )}
        </td>
      </tr>

      {/* Properties row */}
      {isPropsExpanded && hasProperties && (
        <tr className="bg-indigo-500/5">
          <td colSpan={6} className="px-4 py-3" style={{ paddingLeft: `${40 + indent}px` }}>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 text-xs">
              {Object.entries(item.properties!).map(([key, value]) => (
                <div key={key} className="bg-white/5 rounded px-2 py-1">
                  <span className="text-indigo-300 font-medium">{key}:</span>{" "}
                  <span className="text-white/80">{value}</span>
                </div>
              ))}
            </div>
          </td>
        </tr>
      )}

      {/* Children rows */}
      {isExpanded && hasChildren && item.children!.map((child) => (
        <BOMRow
          key={child.part_number}
          item={child}
          expanded={expanded}
          onToggle={onToggle}
          expandedProps={expandedProps}
          onToggleProps={onToggleProps}
        />
      ))}
    </>
  );
}

export function BOMPreview({ isOpen, onClose, autoAnalyze = false }: BOMPreviewProps) {
  const [bomData, setBomData] = useState<BOMData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [showPdf, setShowPdf] = useState(false);
  const [generatingPdf, setGeneratingPdf] = useState(false);
  const [viewMode, setViewMode] = useState<"flat" | "hierarchical">("hierarchical");
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [expandedProps, setExpandedProps] = useState<Set<string>>(new Set());
  const [showAssemblyProps, setShowAssemblyProps] = useState(false);
  const [autoAnalyzeTriggered, setAutoAnalyzeTriggered] = useState(false);

  // Analysis state
  const [activeTab, setActiveTab] = useState<"bom" | "analysis">("bom");
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [analyzingAssembly, setAnalyzingAssembly] = useState(false);
  const [selectedPartAnalysis, setSelectedPartAnalysis] = useState<string | null>(null);

  const desktopUrl = process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || "http://localhost:8000";

  const runAnalysis = async () => {
    setAnalyzingAssembly(true);
    setError(null);
    try {
      const response = await fetch(`${desktopUrl}/com/solidworks/analysis/analyze`);
      if (!response.ok) {
        throw new Error(`Failed to analyze: ${response.statusText}`);
      }
      const data = await response.json();
      setAnalysisData(data);
      setActiveTab("analysis");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze assembly");
    } finally {
      setAnalyzingAssembly(false);
    }
  };

  // Auto-analyze when triggered from chat
  useEffect(() => {
    if (autoAnalyze && bomData && !autoAnalyzeTriggered && !analyzingAssembly && !analysisData) {
      setAutoAnalyzeTriggered(true);
      setActiveTab("analysis");
      runAnalysis();
    }
  }, [autoAnalyze, bomData, autoAnalyzeTriggered, analyzingAssembly, analysisData]);

  // Reset autoAnalyzeTriggered when modal closes
  useEffect(() => {
    if (!isOpen) {
      setAutoAnalyzeTriggered(false);
    }
  }, [isOpen]);

  const toggleExpand = (partNumber: string) => {
    setExpanded(prev => {
      const next = new Set(prev);
      if (next.has(partNumber)) {
        next.delete(partNumber);
      } else {
        next.add(partNumber);
      }
      return next;
    });
  };

  const togglePropsExpand = (partNumber: string) => {
    setExpandedProps(prev => {
      const next = new Set(prev);
      if (next.has(partNumber)) {
        next.delete(partNumber);
      } else {
        next.add(partNumber);
      }
      return next;
    });
  };

  const expandAll = () => {
    if (!bomData?.hierarchical_bom) return;
    const allParts = new Set<string>();
    const collectParts = (items: BOMItem[]) => {
      items.forEach(item => {
        if (item.children && item.children.length > 0) {
          allParts.add(item.part_number);
          collectParts(item.children);
        }
      });
    };
    collectParts(bomData.hierarchical_bom);
    setExpanded(allParts);
  };

  const collapseAll = () => {
    setExpanded(new Set());
  };

  useEffect(() => {
    if (isOpen) {
      fetchBOM();
    } else {
      // Reset state when closing
      setBomData(null);
      setError(null);
      setPdfUrl(null);
      setShowPdf(false);
    }
  }, [isOpen]);

  const fetchBOM = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${desktopUrl}/com/solidworks/get_bom`);
      if (!response.ok) {
        throw new Error(`Failed to fetch BOM: ${response.statusText}`);
      }
      const data = await response.json();
      setBomData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch BOM");
    } finally {
      setLoading(false);
    }
  };

  const generatePdf = async () => {
    setGeneratingPdf(true);
    try {
      const response = await fetch(`${desktopUrl}/com/solidworks/get_bom_pdf`);
      if (!response.ok) {
        throw new Error(`Failed to generate PDF: ${response.statusText}`);
      }
      const data = await response.json();

      // Convert base64 to blob URL
      const byteCharacters = atob(data.pdf_base64);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: "application/pdf" });
      const url = URL.createObjectURL(blob);

      setPdfUrl(url);
      setShowPdf(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate PDF");
    } finally {
      setGeneratingPdf(false);
    }
  };

  const downloadPdf = () => {
    if (pdfUrl && bomData) {
      const link = document.createElement("a");
      link.href = pdfUrl;
      link.download = `BOM_${bomData.assembly_name}_${new Date().toISOString().split("T")[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-5xl max-h-[90vh] bg-gray-900 rounded-2xl shadow-2xl border border-white/10 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-gray-900/80">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center">
              <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Bill of Materials</h2>
              {bomData && (
                <p className="text-sm text-white/50">{bomData.assembly_name}</p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Tab switcher */}
            {bomData && !showPdf && (
              <div className="flex items-center bg-white/5 rounded-lg p-1 mr-2">
                <button
                  onClick={() => setActiveTab("bom")}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    activeTab === "bom" ? "bg-indigo-500 text-white" : "text-white/60 hover:text-white"
                  }`}
                >
                  BOM
                </button>
                <button
                  onClick={() => setActiveTab("analysis")}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    activeTab === "analysis" ? "bg-indigo-500 text-white" : "text-white/60 hover:text-white"
                  }`}
                >
                  Analysis
                </button>
              </div>
            )}

            {/* Analyze button */}
            {bomData && !showPdf && (
              <button
                onClick={runAnalysis}
                disabled={analyzingAssembly}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-medium transition-colors disabled:opacity-50"
              >
                {analyzingAssembly ? (
                  <>
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    <span>Analyze</span>
                  </>
                )}
              </button>
            )}

            {bomData && !showPdf && (
              <button
                onClick={generatePdf}
                disabled={generatingPdf}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-500 hover:bg-indigo-600 text-white text-sm font-medium transition-colors disabled:opacity-50"
              >
                {generatingPdf ? (
                  <>
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    <span>PDF</span>
                  </>
                )}
              </button>
            )}

            {showPdf && pdfUrl && (
              <>
                <button
                  onClick={() => setShowPdf(false)}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white text-sm font-medium transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                  </svg>
                  <span>Table View</span>
                </button>
                <button
                  onClick={downloadPdf}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-medium transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  <span>Download</span>
                </button>
              </>
            )}

            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-white/10 text-white/60 hover:text-white transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          {loading && (
            <div className="flex items-center justify-center h-64">
              <div className="flex items-center gap-3 text-white/60">
                <svg className="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                <span>Loading BOM...</span>
              </div>
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-red-500/20 flex items-center justify-center">
                  <svg className="w-6 h-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <p className="text-red-400 font-medium">{error}</p>
                <button
                  onClick={fetchBOM}
                  className="mt-3 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white text-sm transition-colors"
                >
                  Try Again
                </button>
              </div>
            </div>
          )}

          {bomData && !loading && !showPdf && activeTab === "bom" && (
            <div className="h-full overflow-auto p-6">
              {/* Assembly Properties */}
              {bomData.assembly_properties && Object.keys(bomData.assembly_properties).length > 0 && (
                <div className="mb-4">
                  <button
                    onClick={() => setShowAssemblyProps(!showAssemblyProps)}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-sm transition-colors"
                  >
                    <svg className={`w-4 h-4 transition-transform ${showAssemblyProps ? "rotate-90" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                    Assembly Properties ({Object.keys(bomData.assembly_properties).length})
                  </button>
                  {showAssemblyProps && (
                    <div className="mt-2 p-4 rounded-lg bg-indigo-500/5 border border-indigo-500/20">
                      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 text-sm">
                        {Object.entries(bomData.assembly_properties).map(([key, value]) => (
                          <div key={key} className="bg-white/5 rounded px-3 py-2">
                            <span className="text-indigo-300 font-medium">{key}:</span>{" "}
                            <span className="text-white/80">{value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-white/5 rounded-xl p-4 border border-white/10">
                  <p className="text-xs text-white/50 uppercase tracking-wider">Total Items</p>
                  <p className="text-2xl font-bold text-white mt-1">{bomData.total_unique_parts}</p>
                </div>
                <div className="bg-white/5 rounded-xl p-4 border border-white/10">
                  <p className="text-xs text-white/50 uppercase tracking-wider">Parts</p>
                  <p className="text-2xl font-bold text-white mt-1">
                    {bomData.total_parts ?? bomData.bom.filter(b => b.type === "Part").length}
                  </p>
                </div>
                <div className="bg-white/5 rounded-xl p-4 border border-white/10">
                  <p className="text-xs text-white/50 uppercase tracking-wider">Sub-Assemblies</p>
                  <p className="text-2xl font-bold text-white mt-1">
                    {bomData.total_sub_assemblies ?? bomData.bom.filter(b => b.type === "Sub-Assembly").length}
                  </p>
                </div>
              </div>

              {/* View mode toggle and expand/collapse */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setViewMode("hierarchical")}
                    className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                      viewMode === "hierarchical"
                        ? "bg-indigo-500 text-white"
                        : "bg-white/5 text-white/60 hover:bg-white/10"
                    }`}
                  >
                    Hierarchical
                  </button>
                  <button
                    onClick={() => setViewMode("flat")}
                    className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                      viewMode === "flat"
                        ? "bg-indigo-500 text-white"
                        : "bg-white/5 text-white/60 hover:bg-white/10"
                    }`}
                  >
                    Flat
                  </button>
                </div>
                {viewMode === "hierarchical" && bomData.hierarchical_bom && (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={expandAll}
                      className="px-3 py-1.5 rounded-lg text-sm bg-white/5 text-white/60 hover:bg-white/10 transition-colors"
                    >
                      Expand All
                    </button>
                    <button
                      onClick={collapseAll}
                      className="px-3 py-1.5 rounded-lg text-sm bg-white/5 text-white/60 hover:bg-white/10 transition-colors"
                    >
                      Collapse All
                    </button>
                  </div>
                )}
              </div>

              {/* Table */}
              <div className="bg-white/5 rounded-xl border border-white/10 overflow-hidden">
                <table className="w-full">
                  <thead>
                    <tr className="bg-indigo-500/20 border-b border-white/10">
                      <th className="px-4 py-3 text-left text-xs font-semibold text-indigo-300 uppercase tracking-wider w-16">Item</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-indigo-300 uppercase tracking-wider">Part Number</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-indigo-300 uppercase tracking-wider">Description</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-indigo-300 uppercase tracking-wider w-24">Type</th>
                      <th className="px-4 py-3 text-center text-xs font-semibold text-indigo-300 uppercase tracking-wider w-16">Qty</th>
                      <th className="px-4 py-3 text-center text-xs font-semibold text-indigo-300 uppercase tracking-wider w-12">Props</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {viewMode === "hierarchical" && bomData.hierarchical_bom ? (
                      bomData.hierarchical_bom.map((item) => (
                        <BOMRow
                          key={item.part_number}
                          item={item}
                          expanded={expanded}
                          onToggle={toggleExpand}
                          expandedProps={expandedProps}
                          onToggleProps={togglePropsExpand}
                        />
                      ))
                    ) : (
                      bomData.bom.map((item, index) => (
                        <tr
                          key={item.item}
                          className={`hover:bg-white/5 transition-colors ${index % 2 === 0 ? "bg-transparent" : "bg-white/[0.02]"}`}
                        >
                          <td className="px-4 py-3 text-sm text-white/70 font-mono">{item.item}</td>
                          <td className="px-4 py-3 text-sm text-white font-medium">{item.part_number}</td>
                          <td className="px-4 py-3 text-sm text-white/70">{item.description}</td>
                          <td className="px-4 py-3">
                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                              item.type === "Sub-Assembly"
                                ? "bg-purple-500/20 text-purple-300"
                                : "bg-emerald-500/20 text-emerald-300"
                            }`}>
                              {item.type}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-sm text-white text-center font-semibold">{item.qty}</td>
                          <td className="px-4 py-3 w-12">
                            {item.properties && Object.keys(item.properties).length > 0 && (
                              <button
                                onClick={() => togglePropsExpand(item.part_number)}
                                className={`p-1 rounded hover:bg-white/10 transition-colors ${expandedProps.has(item.part_number) ? "bg-indigo-500/20" : ""}`}
                                title="Show properties"
                              >
                                <svg className="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                              </button>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Analysis Tab */}
          {bomData && !loading && !showPdf && activeTab === "analysis" && (
            <div className="h-full overflow-auto p-6">
              {!analysisData ? (
                <div className="flex flex-col items-center justify-center h-64 text-center">
                  <div className="w-16 h-16 mb-4 rounded-2xl bg-emerald-500/20 flex items-center justify-center">
                    <svg className="w-8 h-8 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">No Analysis Yet</h3>
                  <p className="text-white/50 mb-4">Click the &quot;Analyze&quot; button to get AI-powered design insights</p>
                  <button
                    onClick={runAnalysis}
                    disabled={analyzingAssembly}
                    className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-medium transition-colors disabled:opacity-50"
                  >
                    {analyzingAssembly ? "Analyzing..." : "Analyze Assembly"}
                  </button>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Assembly Insights */}
                  <div className="bg-gradient-to-br from-emerald-500/10 to-indigo-500/10 rounded-xl p-6 border border-emerald-500/20">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                      <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      Assembly Insights
                    </h3>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div className="bg-white/5 rounded-lg p-3">
                        <p className="text-xs text-white/50 uppercase">Category</p>
                        <p className="text-white font-medium capitalize">{analysisData.assembly_insights.assembly_category.replace(/_/g, " ")}</p>
                      </div>
                      <div className="bg-white/5 rounded-lg p-3">
                        <p className="text-xs text-white/50 uppercase">Parts Analyzed</p>
                        <p className="text-white font-medium">{analysisData.total_parts_analyzed}</p>
                      </div>
                      <div className="bg-white/5 rounded-lg p-3">
                        <p className="text-xs text-white/50 uppercase">Complexity</p>
                        <p className="text-white font-medium">{analysisData.assembly_insights.complexity_score.toFixed(1)} / 10</p>
                      </div>
                      <div className="bg-white/5 rounded-lg p-3">
                        <p className="text-xs text-white/50 uppercase">Part Types</p>
                        <p className="text-white font-medium">{Object.keys(analysisData.assembly_insights.part_type_distribution).length}</p>
                      </div>
                    </div>

                    {/* Recommendations */}
                    <div className="mb-4">
                      <h4 className="text-sm font-semibold text-emerald-300 mb-2">Recommendations</h4>
                      <ul className="space-y-1">
                        {analysisData.assembly_insights.recommendations.map((rec, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-white/70">
                            <span className="text-emerald-400 mt-0.5">•</span>
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Improvements */}
                    {analysisData.assembly_insights.suggested_improvements.length > 0 && (
                      <div>
                        <h4 className="text-sm font-semibold text-yellow-300 mb-2">Suggested Improvements</h4>
                        <div className="space-y-2">
                          {analysisData.assembly_insights.suggested_improvements.map((imp, i) => (
                            <div key={i} className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3">
                              <div className="flex items-center gap-2 mb-1">
                                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                                  imp.priority === "high" ? "bg-red-500/20 text-red-300" :
                                  imp.priority === "medium" ? "bg-yellow-500/20 text-yellow-300" :
                                  "bg-blue-500/20 text-blue-300"
                                }`}>
                                  {imp.priority}
                                </span>
                                <span className="text-sm font-medium text-white">{imp.area}</span>
                              </div>
                              <p className="text-sm text-white/70">{imp.suggestion}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Part Type Distribution */}
                  <div className="bg-white/5 rounded-xl p-6 border border-white/10">
                    <h3 className="text-lg font-semibold text-white mb-4">Part Type Distribution</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {Object.entries(analysisData.assembly_insights.part_type_distribution)
                        .sort((a, b) => b[1] - a[1])
                        .map(([type, count]) => (
                          <div key={type} className="bg-white/5 rounded-lg p-3 flex items-center justify-between">
                            <span className="text-sm text-white/70 capitalize">{type.replace(/_/g, " ")}</span>
                            <span className="text-white font-semibold">{count}</span>
                          </div>
                        ))}
                    </div>
                  </div>

                  {/* Part Analyses */}
                  <div className="bg-white/5 rounded-xl border border-white/10 overflow-hidden">
                    <div className="px-6 py-4 border-b border-white/10">
                      <h3 className="text-lg font-semibold text-white">Part Analysis Details</h3>
                      <p className="text-sm text-white/50">Click on a part to see detailed analysis</p>
                    </div>
                    <div className="divide-y divide-white/5 max-h-96 overflow-y-auto">
                      {analysisData.part_analyses.map((part) => (
                        <div key={part.part_number}>
                          <button
                            onClick={() => setSelectedPartAnalysis(
                              selectedPartAnalysis === part.part_number ? null : part.part_number
                            )}
                            className="w-full px-6 py-3 flex items-center justify-between hover:bg-white/5 transition-colors"
                          >
                            <div className="flex items-center gap-3">
                              <span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${
                                part.part_type === "unknown" ? "bg-gray-500/20 text-gray-300" :
                                part.part_type === "seal" ? "bg-blue-500/20 text-blue-300" :
                                part.part_type === "weldment" ? "bg-orange-500/20 text-orange-300" :
                                part.part_type === "lifting" ? "bg-yellow-500/20 text-yellow-300" :
                                part.part_type === "panel" ? "bg-purple-500/20 text-purple-300" :
                                part.part_type === "structural_frame" ? "bg-red-500/20 text-red-300" :
                                "bg-emerald-500/20 text-emerald-300"
                              }`}>
                                {part.part_type.replace(/_/g, " ")}
                              </span>
                              <div className="flex flex-col">
                                <span className="text-sm text-white font-medium">{part.part_number}</span>
                                {part.suggested_name && part.suggested_name !== part.part_number && (
                                  <span className="text-xs text-cyan-400/70">→ {part.suggested_name}</span>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-xs text-white/40">
                                {Math.round(part.confidence * 100)}% confidence
                              </span>
                              <svg
                                className={`w-4 h-4 text-white/40 transition-transform ${
                                  selectedPartAnalysis === part.part_number ? "rotate-180" : ""
                                }`}
                                fill="none" viewBox="0 0 24 24" stroke="currentColor"
                              >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                              </svg>
                            </div>
                          </button>

                          {selectedPartAnalysis === part.part_number && (
                            <div className="px-6 py-4 bg-white/[0.02] border-t border-white/5">
                              <div className="space-y-4">
                                {/* Suggested Name */}
                                {part.suggested_name && part.suggested_name !== part.part_number && (
                                  <div className="bg-cyan-500/10 border border-cyan-500/20 rounded-lg p-3">
                                    <div className="flex items-center justify-between">
                                      <div>
                                        <h5 className="text-sm font-semibold text-cyan-300 mb-1">Suggested Name</h5>
                                        <p className="text-sm text-white/70">
                                          <span className="text-white/40 line-through mr-2">{part.part_number}</span>
                                          <span className="text-cyan-300 font-mono">{part.suggested_name}</span>
                                        </p>
                                      </div>
                                      <span className="text-xs text-cyan-400/60 bg-cyan-500/10 px-2 py-1 rounded">
                                        Based on function
                                      </span>
                                    </div>
                                  </div>
                                )}

                                {/* Purpose */}
                                <div>
                                  <h5 className="text-sm font-semibold text-indigo-300 mb-1">Purpose</h5>
                                  <p className="text-sm text-white/70">{part.purpose}</p>
                                </div>

                                {/* Geometry & Material Row */}
                                <div className="grid grid-cols-2 gap-4">
                                  {part.geometry && (
                                    <div className="bg-white/5 rounded-lg p-3">
                                      <h5 className="text-xs font-semibold text-cyan-300 mb-2">Geometry</h5>
                                      <div className="grid grid-cols-2 gap-2 text-xs">
                                        <div>
                                          <span className="text-white/40">Mass:</span>
                                          <span className="text-white ml-1">{part.geometry.mass_kg.toFixed(3)} kg</span>
                                        </div>
                                        <div>
                                          <span className="text-white/40">Volume:</span>
                                          <span className="text-white ml-1">{(part.geometry.volume_m3 * 1e6).toFixed(1)} cm³</span>
                                        </div>
                                        {part.geometry.bounding_box && (
                                          <div className="col-span-2">
                                            <span className="text-white/40">Size:</span>
                                            <span className="text-white ml-1">
                                              {(part.geometry.bounding_box.x * 1000).toFixed(0)} × {(part.geometry.bounding_box.y * 1000).toFixed(0)} × {(part.geometry.bounding_box.z * 1000).toFixed(0)} mm
                                            </span>
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  )}

                                  {part.material?.name && (
                                    <div className="bg-white/5 rounded-lg p-3">
                                      <h5 className="text-xs font-semibold text-orange-300 mb-2">Material</h5>
                                      <p className="text-sm text-white">{part.material.name}</p>
                                    </div>
                                  )}
                                </div>

                                {/* Features Row */}
                                {part.features && part.features.total > 0 && (
                                  <div className="bg-white/5 rounded-lg p-3">
                                    <h5 className="text-xs font-semibold text-purple-300 mb-2">Features ({part.features.total} total)</h5>
                                    <div className="flex flex-wrap gap-2">
                                      {part.features.holes > 0 && (
                                        <span className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs">
                                          {part.features.holes} Holes
                                        </span>
                                      )}
                                      {part.features.fillets > 0 && (
                                        <span className="px-2 py-1 bg-green-500/20 text-green-300 rounded text-xs">
                                          {part.features.fillets} Fillets
                                        </span>
                                      )}
                                      {part.features.chamfers > 0 && (
                                        <span className="px-2 py-1 bg-yellow-500/20 text-yellow-300 rounded text-xs">
                                          {part.features.chamfers} Chamfers
                                        </span>
                                      )}
                                      {part.features.patterns > 0 && (
                                        <span className="px-2 py-1 bg-pink-500/20 text-pink-300 rounded text-xs">
                                          {part.features.patterns} Patterns
                                        </span>
                                      )}
                                    </div>
                                    {part.features.hole_details && part.features.hole_details.length > 0 && (
                                      <div className="mt-2 text-xs text-white/50">
                                        Holes: {part.features.hole_details.map(h =>
                                          h.diameter ? `${h.diameter.toFixed(1)}mm` : h.type
                                        ).join(", ")}
                                      </div>
                                    )}
                                  </div>
                                )}

                                {/* Mates */}
                                {part.mates && part.mates.length > 0 && (
                                  <div className="bg-white/5 rounded-lg p-3">
                                    <h5 className="text-xs font-semibold text-teal-300 mb-2">Mates ({part.mates.length})</h5>
                                    <div className="flex flex-wrap gap-1">
                                      {part.mates.map((mate, i) => (
                                        <span key={i} className="px-2 py-0.5 bg-teal-500/20 text-teal-300 rounded text-xs">
                                          {mate.name}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Recommendations */}
                                <div>
                                  <h5 className="text-sm font-semibold text-emerald-300 mb-1">Recommendations</h5>
                                  <ul className="space-y-1">
                                    {part.recommendations.map((rec, i) => (
                                      <li key={i} className="flex items-start gap-2 text-sm text-white/70">
                                        <span className="text-emerald-400">✓</span>
                                        {rec}
                                      </li>
                                    ))}
                                  </ul>
                                </div>

                                {/* Issues */}
                                <div>
                                  <h5 className="text-sm font-semibold text-yellow-300 mb-1">Potential Issues</h5>
                                  <ul className="space-y-1">
                                    {part.potential_issues.map((issue, i) => (
                                      <li key={i} className="flex items-start gap-2 text-sm text-white/70">
                                        <span className="text-yellow-400">⚠</span>
                                        {issue}
                                      </li>
                                    ))}
                                  </ul>
                                </div>

                                {part.related_parts.length > 0 && (
                                  <div>
                                    <h5 className="text-sm font-semibold text-white/50 mb-1">Related Parts</h5>
                                    <div className="flex flex-wrap gap-1">
                                      {part.related_parts.map((rp) => (
                                        <span key={rp} className="px-2 py-0.5 bg-white/5 rounded text-xs text-white/50">
                                          {rp}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {showPdf && pdfUrl && (
            <div className="h-full">
              <iframe
                src={pdfUrl}
                className="w-full h-full border-0"
                title="BOM PDF Preview"
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
