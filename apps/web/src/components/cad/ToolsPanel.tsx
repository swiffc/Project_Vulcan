"use client";

import { useState, useCallback } from "react";
import toast from "react-hot-toast";

interface ToolCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  tools: Tool[];
  color: string;
}

interface Tool {
  id: string;
  name: string;
  description: string;
  software: "solidworks" | "inventor" | "both";
}

const TOOL_CATEGORIES: ToolCategory[] = [
  {
    id: "sketching",
    name: "Sketching",
    description: "2D sketch creation and constraints",
    icon: "M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z",
    color: "from-blue-500 to-cyan-500",
    tools: [
      { id: "sw_draw_circle", name: "Circle", description: "Draw circle with center and radius", software: "both" },
      { id: "sw_draw_rectangle", name: "Rectangle", description: "Draw corner rectangle", software: "both" },
      { id: "sw_draw_line", name: "Line", description: "Draw line between two points", software: "both" },
      { id: "sw_draw_spline", name: "Spline", description: "Draw smooth curve through points", software: "both" },
      { id: "sw_draw_polygon", name: "Polygon", description: "Draw regular polygon", software: "both" },
      { id: "sw_draw_ellipse", name: "Ellipse", description: "Draw ellipse with axes", software: "both" },
      { id: "sw_add_sketch_constraint", name: "Add Constraint", description: "Add geometric constraint", software: "both" },
      { id: "sw_add_sketch_dimension", name: "Add Dimension", description: "Dimension sketch entity", software: "both" },
    ],
  },
  {
    id: "features",
    name: "Features",
    description: "3D feature creation and modification",
    icon: "M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4",
    color: "from-purple-500 to-pink-500",
    tools: [
      { id: "sw_extrude", name: "Extrude Boss", description: "Create boss extrusion from sketch", software: "both" },
      { id: "sw_extrude_cut", name: "Extrude Cut", description: "Cut material from part", software: "both" },
      { id: "sw_revolve", name: "Revolve", description: "Create revolve feature", software: "both" },
      { id: "sw_fillet", name: "Fillet", description: "Round edges", software: "both" },
      { id: "sw_chamfer", name: "Chamfer", description: "Angle edges", software: "both" },
      { id: "sw_loft", name: "Loft", description: "Create loft between profiles", software: "both" },
      { id: "sw_sweep", name: "Sweep", description: "Sweep profile along path", software: "both" },
      { id: "sw_shell", name: "Shell", description: "Hollow out part", software: "both" },
      { id: "sw_mirror", name: "Mirror", description: "Mirror features", software: "both" },
      { id: "sw_draft", name: "Draft", description: "Add draft angle", software: "both" },
      { id: "sw_rib", name: "Rib", description: "Create rib feature", software: "both" },
    ],
  },
  {
    id: "patterns",
    name: "Patterns",
    description: "Feature and component patterns",
    icon: "M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z",
    color: "from-amber-500 to-orange-500",
    tools: [
      { id: "sw_pattern_circular", name: "Circular Pattern", description: "Pattern around axis", software: "both" },
      { id: "sw_pattern_linear", name: "Linear Pattern", description: "Pattern in X/Y direction", software: "both" },
      { id: "sw_pattern_component", name: "Component Pattern", description: "Pattern assembly components", software: "solidworks" },
    ],
  },
  {
    id: "assembly",
    name: "Assembly",
    description: "Assembly operations and mates",
    icon: "M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10",
    color: "from-emerald-500 to-teal-500",
    tools: [
      { id: "sw_insert_component", name: "Insert Component", description: "Add part to assembly", software: "both" },
      { id: "sw_add_mate", name: "Add Mate", description: "Create mate constraint", software: "solidworks" },
      { id: "sw_add_advanced_mate", name: "Advanced Mate", description: "Gear, cam, path mates", software: "solidworks" },
      { id: "sw_move_component", name: "Move Component", description: "Reposition component", software: "both" },
      { id: "sw_create_exploded_view", name: "Exploded View", description: "Create exploded view", software: "solidworks" },
      { id: "sw_check_interference", name: "Check Interference", description: "Detect collisions", software: "both" },
      { id: "sw_suppress_component", name: "Suppress/Unsuppress", description: "Toggle component visibility", software: "solidworks" },
      { id: "sw_replace_component", name: "Replace Component", description: "Swap with different file", software: "solidworks" },
    ],
  },
  {
    id: "drawings",
    name: "Drawings",
    description: "Drawing views and annotations",
    icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
    color: "from-red-500 to-rose-500",
    tools: [
      { id: "sw_create_drawing_view", name: "Create View", description: "Add view to drawing", software: "both" },
      { id: "sw_add_drawing_dimension", name: "Add Dimension", description: "Dimension drawing view", software: "both" },
      { id: "sw_add_drawing_note", name: "Add Note", description: "Add text annotation", software: "both" },
      { id: "sw_add_bom", name: "Add BOM", description: "Insert Bill of Materials", software: "both" },
      { id: "sw_add_balloon", name: "Add Balloon", description: "Add callout balloon", software: "both" },
      { id: "sw_edit_title_block", name: "Edit Title Block", description: "Update title block fields", software: "solidworks" },
      { id: "sw_add_revision_table", name: "Revision Table", description: "Add revision block", software: "solidworks" },
      { id: "sw_add_centerline", name: "Add Centerline", description: "Add centerlines to view", software: "both" },
      { id: "sw_add_hatching", name: "Add Hatching", description: "Section view hatching", software: "solidworks" },
    ],
  },
  {
    id: "validation",
    name: "Validation",
    description: "Drawing and design validation",
    icon: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",
    color: "from-indigo-500 to-violet-500",
    tools: [
      { id: "validate_gdt", name: "GD&T Check", description: "ASME Y14.5 validation", software: "both" },
      { id: "validate_weld", name: "Weld Check", description: "AWS D1.1 compliance", software: "both" },
      { id: "validate_material", name: "Material Check", description: "ASTM/ASME specs", software: "both" },
      { id: "validate_ache", name: "ACHE Validation", description: "130-point heat exchanger check", software: "both" },
      { id: "validate_dimensions", name: "Dimension Check", description: "Tolerance stack analysis", software: "both" },
      { id: "validate_holes", name: "Hole Pattern Check", description: "AISC edge distance & spacing", software: "both" },
      // Phase 25 - New validators
      { id: "validate_structural", name: "Structural Capacity", description: "Bolt/weld capacity per AISC", software: "both" },
      { id: "validate_shaft", name: "Shaft/Machining", description: "Tolerances, keyways (ANSI B17.1)", software: "both" },
      { id: "validate_handling", name: "Handling/Lifting", description: "Lifting lugs, CG, rigging", software: "both" },
      { id: "validate_bom", name: "BOM Validation", description: "Part number, qty, material", software: "both" },
      { id: "validate_osha", name: "OSHA Safety", description: "Guardrails, ladders, platforms", software: "both" },
    ],
  },
  {
    id: "export",
    name: "Export & Import",
    description: "File format conversion",
    icon: "M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12",
    color: "from-sky-500 to-blue-500",
    tools: [
      { id: "sw_export", name: "Export File", description: "Export to STEP, IGES, STL, PDF", software: "both" },
      { id: "sw_save", name: "Save As", description: "Save to new location", software: "both" },
      { id: "sw_open", name: "Open File", description: "Open existing file", software: "both" },
      { id: "pdm_checkout", name: "PDM Checkout", description: "Check out from vault", software: "solidworks" },
      { id: "pdm_checkin", name: "PDM Check-in", description: "Check in to vault", software: "solidworks" },
      { id: "drive_upload", name: "Upload to Drive", description: "Export to Google Drive", software: "both" },
    ],
  },
];

export function ToolsPanel() {
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [softwareFilter, setSoftwareFilter] = useState<"all" | "solidworks" | "inventor">("all");
  const [executingTool, setExecutingTool] = useState<string | null>(null);
  const [toolResult, setToolResult] = useState<{ tool: string; success: boolean; message: string } | null>(null);

  const executeTool = useCallback(async (toolId: string, toolName: string) => {
    setExecutingTool(toolId);
    setToolResult(null);

    try {
      const res = await fetch("/api/cad", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tool: toolId,
          input: {}, // Default empty input - would need a modal for params
        }),
      });

      const data = await res.json();

      if (data.success) {
        toast.success(`${toolName} executed successfully`);
        setToolResult({ tool: toolName, success: true, message: data.message || "Operation completed" });
      } else {
        toast.error(data.error || "Tool execution failed");
        setToolResult({ tool: toolName, success: false, message: data.error || "Failed" });
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Connection failed";
      toast.error(errorMsg);
      setToolResult({ tool: toolName, success: false, message: errorMsg });
    } finally {
      setExecutingTool(null);
    }
  }, []);

  const filteredCategories = TOOL_CATEGORIES.map((category) => ({
    ...category,
    tools: category.tools.filter((tool) => {
      const matchesSearch = tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tool.description.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesSoftware = softwareFilter === "all" ||
        tool.software === softwareFilter ||
        tool.software === "both";
      return matchesSearch && matchesSoftware;
    }),
  })).filter((category) => category.tools.length > 0 || searchQuery === "");

  const totalTools = TOOL_CATEGORIES.reduce((sum, cat) => sum + cat.tools.length, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">CAD Tools</h2>
          <p className="text-white/50">
            {totalTools}+ tools for SolidWorks and Inventor automation
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Software Filter */}
          <div className="flex items-center gap-1 bg-white/10 rounded-lg p-1">
            {(["all", "solidworks", "inventor"] as const).map((sw) => (
              <button
                key={sw}
                onClick={() => setSoftwareFilter(sw)}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                  softwareFilter === sw
                    ? "bg-vulcan-accent text-white"
                    : "text-white/60 hover:text-white"
                }`}
              >
                {sw === "all" ? "All" : sw.charAt(0).toUpperCase() + sw.slice(1)}
              </button>
            ))}
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
              placeholder="Search tools..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:border-vulcan-accent w-64"
            />
          </div>
        </div>
      </div>

      {/* Categories Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
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
                  <p className="text-xs text-white/60">{category.tools.length} tools</p>
                </div>
              </div>
            </div>

            {/* Tools List */}
            <div className={`transition-all overflow-hidden ${
              activeCategory === category.id ? "max-h-96" : "max-h-0"
            }`}>
              <div className="p-3 space-y-1 max-h-80 overflow-y-auto">
                {category.tools.map((tool) => (
                  <button
                    key={tool.id}
                    className={`w-full text-left p-2 rounded-lg hover:bg-white/10 transition-colors group ${
                      executingTool === tool.id ? "bg-vulcan-accent/20 animate-pulse" : ""
                    }`}
                    disabled={executingTool !== null}
                    onClick={(e) => {
                      e.stopPropagation();
                      executeTool(tool.id, tool.name);
                    }}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-white">{tool.name}</span>
                      <span className={`text-xs px-1.5 py-0.5 rounded ${
                        tool.software === "solidworks"
                          ? "bg-red-500/20 text-red-400"
                          : tool.software === "inventor"
                          ? "bg-orange-500/20 text-orange-400"
                          : "bg-white/10 text-white/40"
                      }`}>
                        {tool.software === "both" ? "SW/INV" : tool.software === "solidworks" ? "SW" : "INV"}
                      </span>
                    </div>
                    <p className="text-xs text-white/40 mt-0.5">{tool.description}</p>
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

      {/* Quick Reference */}
      <div className="glass rounded-2xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Standards Reference</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { name: "ASME Y14.5", desc: "GD&T Standard", icon: "M9 12l2 2 4-4" },
            { name: "AWS D1.1", desc: "Structural Welding", icon: "M17.657 18.657A8 8 0 016.343 7.343" },
            { name: "ASME B16.5", desc: "Pipe Flanges", icon: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0" },
            { name: "API 661", desc: "Heat Exchangers", icon: "M13 10V3L4 14h7v7l9-11h-7z" },
          ].map((std) => (
            <div key={std.name} className="p-3 rounded-lg bg-white/5 border border-white/10">
              <p className="text-sm font-medium text-white">{std.name}</p>
              <p className="text-xs text-white/40">{std.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
