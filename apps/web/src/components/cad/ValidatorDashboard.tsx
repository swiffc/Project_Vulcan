"use client";

import { useState, useEffect } from "react";

interface ValidatorInfo {
  id: string;
  name: string;
  category: string;
  description: string;
  endpoint: string;
  checksCount: number;
  standard?: string;
}

interface ValidationStats {
  totalValidators: number;
  totalChecks: number;
  categories: { name: string; count: number }[];
  recentValidations: number;
}

const VALIDATORS: ValidatorInfo[] = [
  // Fabrication & Manufacturing
  { id: "fabrication", name: "Fabrication Feasibility", category: "Manufacturing", description: "Check manufacturing constraints for holes, slots, bends", endpoint: "/phase25/check-fabrication", checksCount: 12, standard: "DFM" },
  { id: "sheet-metal", name: "Sheet Metal", category: "Manufacturing", description: "Validate bend radii, K-factors, flat patterns", endpoint: "/phase25/check-sheet-metal", checksCount: 8, standard: "ASME" },
  { id: "machining", name: "Machining Tolerance", category: "Manufacturing", description: "Check achievable tolerances by process", endpoint: "/phase25/check-shaft", checksCount: 10, standard: "ASME Y14.5" },

  // Structural
  { id: "aisc-holes", name: "AISC Hole Patterns", category: "Structural", description: "Bolt hole spacing, edge distances", endpoint: "/phase25/check-holes", checksCount: 15, standard: "AISC 360-16" },
  { id: "beam", name: "Beam Design", category: "Structural", description: "Flexure, shear, LTB, deflection", endpoint: "/phase25/validate-beam", checksCount: 5, standard: "AISC 360-16" },
  { id: "column", name: "Column Design", category: "Structural", description: "Slenderness, compression capacity", endpoint: "/phase25/validate-column", checksCount: 4, standard: "AISC 360-16" },
  { id: "connection", name: "Steel Connections", category: "Structural", description: "Bolted and welded connections", endpoint: "/phase25/validate-connection", checksCount: 6, standard: "AISC 360-16" },
  { id: "base-plate", name: "Base Plate", category: "Structural", description: "Bearing, bending, anchor bolts", endpoint: "/phase25/validate-base-plate", checksCount: 3, standard: "AISC DG1" },

  // Materials & Finishing
  { id: "materials", name: "Materials & Finishing", category: "Materials", description: "Material compatibility, coating systems", endpoint: "/phase25/check-materials", checksCount: 10, standard: "ASTM" },
  { id: "sspc", name: "SSPC Coating", category: "Materials", description: "Surface prep, coating systems", endpoint: "/phase25/check-sspc", checksCount: 8, standard: "SSPC" },

  // Fasteners & Connections
  { id: "fasteners", name: "Fastener Analysis", category: "Fasteners", description: "Bolt capacity, torque, slip resistance", endpoint: "/phase25/check-fasteners", checksCount: 12, standard: "RCSC" },
  { id: "rigging", name: "Rigging & Lifting", category: "Fasteners", description: "Lifting lugs, sling angles, CG", endpoint: "/phase25/check-rigging", checksCount: 10, standard: "OSHA" },

  // GD&T & Dimensions
  { id: "gdt", name: "GD&T Validation", category: "GD&T", description: "ASME Y14.5 geometric tolerancing", endpoint: "/phase25/check-gdt", checksCount: 20, standard: "ASME Y14.5-2018" },
  { id: "dimensions", name: "Dimension Check", category: "GD&T", description: "Over/under dimensioning", endpoint: "/phase25/check-dimensions", checksCount: 8 },
  { id: "tolerance", name: "Tolerance Stack", category: "GD&T", description: "Flatness, squareness, parallelism", endpoint: "/phase25/check-tolerance", checksCount: 6, standard: "ASME Y14.5" },

  // Welding
  { id: "weld", name: "Weld Validation", category: "Welding", description: "AWS D1.1 weld requirements", endpoint: "/phase25/check-weld", checksCount: 15, standard: "AWS D1.1" },
  { id: "inspection", name: "Inspection/QC", category: "Welding", description: "NDE requirements, inspection plans", endpoint: "/phase25/check-inspection", checksCount: 10, standard: "AWS D1.1" },

  // ACHE / Heat Exchangers
  { id: "api661", name: "API 661 Bundle", category: "ACHE", description: "Air-cooled heat exchanger validation", endpoint: "/phase25/check-api661", checksCount: 82, standard: "API 661" },
  { id: "asme-viii", name: "ASME VIII Vessel", category: "ACHE", description: "Pressure vessel validation", endpoint: "/phase25/check-asme-viii", checksCount: 15, standard: "ASME VIII" },
  { id: "tema", name: "TEMA Standards", category: "ACHE", description: "Shell & tube heat exchangers", endpoint: "/phase25/check-tema", checksCount: 12, standard: "TEMA" },
  { id: "nema", name: "NEMA Motor", category: "ACHE", description: "Motor frame, efficiency", endpoint: "/phase25/check-nema", checksCount: 8, standard: "NEMA MG1" },

  // Piping
  { id: "b31-3", name: "ASME B31.3 Piping", category: "Piping", description: "Process piping design", endpoint: "/phase25/check-b31-3", checksCount: 12, standard: "ASME B31.3" },

  // Documentation
  { id: "documentation", name: "Documentation", category: "Documentation", description: "Title block, notes, BOM completeness", endpoint: "/phase25/check-documentation", checksCount: 15, standard: "ASME Y14" },
  { id: "bom", name: "BOM Validation", category: "Documentation", description: "Bill of materials completeness", endpoint: "/phase25/check-bom", checksCount: 8 },
  { id: "cross-part", name: "Cross-Part", category: "Documentation", description: "Interface compatibility", endpoint: "/phase25/check-cross-part", checksCount: 6 },
];

const CATEGORIES = [
  { name: "Manufacturing", color: "bg-blue-500" },
  { name: "Structural", color: "bg-orange-500" },
  { name: "Materials", color: "bg-green-500" },
  { name: "Fasteners", color: "bg-yellow-500" },
  { name: "GD&T", color: "bg-purple-500" },
  { name: "Welding", color: "bg-red-500" },
  { name: "ACHE", color: "bg-cyan-500" },
  { name: "Piping", color: "bg-pink-500" },
  { name: "Documentation", color: "bg-gray-500" },
];

export function ValidatorDashboard() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [serverStatus, setServerStatus] = useState<"online" | "offline" | "checking">("checking");
  const [stats, setStats] = useState<ValidationStats | null>(null);

  useEffect(() => {
    // Check server status
    const checkServer = async () => {
      try {
        const response = await fetch("http://localhost:8000/health");
        if (response.ok) {
          setServerStatus("online");
        } else {
          setServerStatus("offline");
        }
      } catch {
        setServerStatus("offline");
      }
    };

    checkServer();
    const interval = setInterval(checkServer, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Calculate stats
    const categories = CATEGORIES.map(cat => ({
      name: cat.name,
      count: VALIDATORS.filter(v => v.category === cat.name).length,
    }));

    setStats({
      totalValidators: VALIDATORS.length,
      totalChecks: VALIDATORS.reduce((sum, v) => sum + v.checksCount, 0),
      categories,
      recentValidations: 0,
    });
  }, []);

  const filteredValidators = VALIDATORS.filter(v => {
    const matchesCategory = !selectedCategory || v.category === selectedCategory;
    const matchesSearch = !searchTerm ||
      v.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      v.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (v.standard?.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const getCategoryColor = (category: string) => {
    const cat = CATEGORIES.find(c => c.name === category);
    return cat?.color || "bg-gray-500";
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Validation Dashboard</h2>
          <p className="text-white/60 mt-1">
            {stats?.totalValidators} validators with {stats?.totalChecks}+ checks
          </p>
        </div>
        <div className="flex items-center gap-4">
          {/* Server Status */}
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${
              serverStatus === "online" ? "bg-green-500" :
              serverStatus === "offline" ? "bg-red-500" : "bg-yellow-500 animate-pulse"
            }`} />
            <span className="text-sm text-white/60">
              {serverStatus === "online" ? "Server Online" :
               serverStatus === "offline" ? "Server Offline" : "Checking..."}
            </span>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="text-3xl font-bold text-white">{stats?.totalValidators}</div>
          <div className="text-sm text-white/60">Validators</div>
        </div>
        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="text-3xl font-bold text-green-400">{stats?.totalChecks}+</div>
          <div className="text-sm text-white/60">Total Checks</div>
        </div>
        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="text-3xl font-bold text-blue-400">{stats?.categories.length}</div>
          <div className="text-sm text-white/60">Categories</div>
        </div>
        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="text-3xl font-bold text-purple-400">15+</div>
          <div className="text-sm text-white/60">Standards</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 items-center">
        {/* Search */}
        <div className="flex-1 min-w-[200px]">
          <input
            type="text"
            placeholder="Search validators..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white placeholder-white/40 focus:outline-none focus:border-vulcan-accent"
          />
        </div>

        {/* Category Pills */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-all ${
              !selectedCategory
                ? "bg-vulcan-accent text-white"
                : "bg-white/10 text-white/60 hover:bg-white/20"
            }`}
          >
            All
          </button>
          {CATEGORIES.map(cat => (
            <button
              key={cat.name}
              onClick={() => setSelectedCategory(cat.name === selectedCategory ? null : cat.name)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-all flex items-center gap-2 ${
                selectedCategory === cat.name
                  ? `${cat.color} text-white`
                  : "bg-white/10 text-white/60 hover:bg-white/20"
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${cat.color}`} />
              {cat.name}
            </button>
          ))}
        </div>
      </div>

      {/* Validator Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredValidators.map(validator => (
          <div
            key={validator.id}
            className="bg-white/5 rounded-lg p-4 border border-white/10 hover:border-vulcan-accent/50 transition-all group"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`w-2 h-2 rounded-full ${getCategoryColor(validator.category)}`} />
                  <span className="text-xs text-white/40 uppercase tracking-wide">
                    {validator.category}
                  </span>
                </div>
                <h3 className="font-semibold text-white group-hover:text-vulcan-accent transition-colors">
                  {validator.name}
                </h3>
                <p className="text-sm text-white/60 mt-1">{validator.description}</p>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-white">{validator.checksCount}</div>
                <div className="text-xs text-white/40">checks</div>
              </div>
            </div>

            <div className="flex items-center justify-between mt-4 pt-3 border-t border-white/5">
              {validator.standard && (
                <span className="text-xs px-2 py-1 bg-white/10 rounded text-white/60">
                  {validator.standard}
                </span>
              )}
              <button className="text-sm text-vulcan-accent hover:text-vulcan-accent/80 font-medium">
                Run Check →
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredValidators.length === 0 && (
        <div className="text-center py-12">
          <div className="text-white/40 text-lg">No validators found</div>
          <p className="text-white/20 mt-2">Try adjusting your search or filters</p>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white/5 rounded-lg p-6 border border-white/10">
        <h3 className="font-semibold text-white mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="flex items-center gap-3 p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all">
            <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
              <svg className="w-5 h-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="text-left">
              <div className="text-sm font-medium text-white">Run All Checks</div>
              <div className="text-xs text-white/40">Full validation</div>
            </div>
          </button>

          <button className="flex items-center gap-3 p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all">
            <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
              <svg className="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div className="text-left">
              <div className="text-sm font-medium text-white">Export Report</div>
              <div className="text-xs text-white/40">PDF/Excel</div>
            </div>
          </button>

          <button className="flex items-center gap-3 p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all">
            <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
              <svg className="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div className="text-left">
              <div className="text-sm font-medium text-white">Drawing Markup</div>
              <div className="text-xs text-white/40">SVG overlay</div>
            </div>
          </button>

          <button className="flex items-center gap-3 p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all">
            <div className="w-10 h-10 rounded-lg bg-orange-500/20 flex items-center justify-center">
              <svg className="w-5 h-5 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
            </div>
            <div className="text-left">
              <div className="text-sm font-medium text-white">Configuration</div>
              <div className="text-xs text-white/40">Settings</div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}
