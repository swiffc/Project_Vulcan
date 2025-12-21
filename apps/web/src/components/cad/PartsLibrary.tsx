"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";

interface ACHEPart {
  id: string;
  partNumber: string;
  name: string;
  category: string;
  subcategory: string;
  material: string;
  specs: string;
  standard: string;
  hasModel: boolean;
  hasDrawing: boolean;
}

const categories = [
  { id: "all", name: "All Parts", icon: "M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" },
  { id: "bundles", name: "Tube Bundles", icon: "M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm0 8a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1v-2z" },
  { id: "headers", name: "Headers & Plugs", icon: "M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2z" },
  { id: "fins", name: "Finned Tubes", icon: "M13 10V3L4 14h7v7l9-11h-7z" },
  { id: "fans", name: "Fan Assemblies", icon: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" },
  { id: "structure", name: "Structure", icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" },
  { id: "flanges", name: "Flanges & Nozzles", icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" },
];

const mockParts: ACHEPart[] = [
  // Tube Bundles
  { id: "1", partNumber: "TB-2X4-A179", name: "Tube Bundle 2-Row x 4-Pass", category: "bundles", subcategory: "Carbon Steel", material: "A179 Seamless", specs: "1\" OD x 14 BWG x 30' Tubes", standard: "API 661", hasModel: true, hasDrawing: true },
  { id: "2", partNumber: "TB-4X2-A214", name: "Tube Bundle 4-Row x 2-Pass", category: "bundles", subcategory: "Carbon Steel", material: "A214 ERW", specs: "1\" OD x 12 BWG x 40' Tubes", standard: "API 661", hasModel: true, hasDrawing: true },
  { id: "3", partNumber: "TB-6X2-T5", name: "Tube Bundle 6-Row x 2-Pass", category: "bundles", subcategory: "Alloy Steel", material: "A213 T5", specs: "1\" OD x 10 BWG x 35' Tubes", standard: "API 661", hasModel: true, hasDrawing: false },

  // Headers
  { id: "4", partNumber: "HDR-BOX-24", name: "Box Header Assembly 24\"", category: "headers", subcategory: "Removable Cover", material: "SA-516 Gr70", specs: "24\" x 18\" x 600# Rating", standard: "ASME VIII", hasModel: true, hasDrawing: true },
  { id: "5", partNumber: "HDR-PLUG-18", name: "Plug Header Assembly 18\"", category: "headers", subcategory: "Plug Type", material: "SA-516 Gr70", specs: "18\" Dia x 450# Rating", standard: "ASME VIII", hasModel: true, hasDrawing: true },
  { id: "6", partNumber: "PLG-1.0-SS", name: "Tube Plug 1\" SS", category: "headers", subcategory: "Tube Plugs", material: "316 SS", specs: "1\" OD Shoulder Type", standard: "API 661", hasModel: true, hasDrawing: true },

  // Finned Tubes
  { id: "7", partNumber: "FT-LFIN-AL", name: "L-Fin Aluminum 10 FPI", category: "fins", subcategory: "L-Foot Fin", material: "1100 Aluminum", specs: "10 FPI x 5/8\" Fin Height", standard: "API 661", hasModel: true, hasDrawing: true },
  { id: "8", partNumber: "FT-EXT-AL", name: "Extruded Aluminum 11 FPI", category: "fins", subcategory: "Extruded", material: "6063 Aluminum", specs: "11 FPI x 9/16\" Fin Height", standard: "API 661", hasModel: true, hasDrawing: true },
  { id: "9", partNumber: "FT-EMB-CS", name: "Embedded Steel Fin 7 FPI", category: "fins", subcategory: "Embedded", material: "Carbon Steel", specs: "7 FPI x 1/2\" Fin Height", standard: "API 661", hasModel: false, hasDrawing: true },

  // Fan Assemblies
  { id: "10", partNumber: "FAN-14-4BL", name: "Fan Assembly 14' 4-Blade", category: "fans", subcategory: "Axial Flow", material: "Aluminum Blades", specs: "14' Dia x 4 Blade x 1750 RPM", standard: "API 661", hasModel: true, hasDrawing: true },
  { id: "11", partNumber: "FAN-12-6BL", name: "Fan Assembly 12' 6-Blade", category: "fans", subcategory: "Axial Flow", material: "FRP Blades", specs: "12' Dia x 6 Blade x 1150 RPM", standard: "API 661", hasModel: true, hasDrawing: true },
  { id: "12", partNumber: "HUB-VP-14", name: "Variable Pitch Hub 14'", category: "fans", subcategory: "Fan Hubs", material: "Cast Iron", specs: "14' Fan x Auto-Variable Pitch", standard: "API 661", hasModel: true, hasDrawing: false },

  // Structure
  { id: "13", partNumber: "STR-BAY-STD", name: "Standard Bay Structure", category: "structure", subcategory: "Bay Frame", material: "A36 Steel", specs: "Hot-Dip Galvanized", standard: "AISC", hasModel: true, hasDrawing: true },
  { id: "14", partNumber: "PLN-FRC-STD", name: "Forced Draft Plenum", category: "structure", subcategory: "Plenums", material: "A36 Steel", specs: "Standard FD Configuration", standard: "API 661", hasModel: true, hasDrawing: true },
  { id: "15", partNumber: "PLN-IND-STD", name: "Induced Draft Plenum", category: "structure", subcategory: "Plenums", material: "A36 Steel", specs: "Standard ID Configuration", standard: "API 661", hasModel: true, hasDrawing: true },

  // Flanges & Nozzles
  { id: "16", partNumber: "FLG-WN-6-150", name: "Weld Neck Flange 6\" 150#", category: "flanges", subcategory: "ANSI B16.5", material: "A105", specs: "6\" NPS x 150# RF", standard: "ASME B16.5", hasModel: true, hasDrawing: true },
  { id: "17", partNumber: "FLG-WN-8-300", name: "Weld Neck Flange 8\" 300#", category: "flanges", subcategory: "ANSI B16.5", material: "A105", specs: "8\" NPS x 300# RF", standard: "ASME B16.5", hasModel: true, hasDrawing: true },
  { id: "18", partNumber: "NZL-INL-8", name: "Inlet Nozzle Assembly 8\"", category: "flanges", subcategory: "Nozzles", material: "SA-106 Gr B", specs: "8\" Sch 80 x WN Flange", standard: "ASME VIII", hasModel: true, hasDrawing: true },
];

export function PartsLibrary() {
  const [parts] = useState<ACHEPart[]>(mockParts);
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedPart, setSelectedPart] = useState<ACHEPart | null>(null);

  const filtered = parts.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.partNumber.toLowerCase().includes(search.toLowerCase()) ||
      p.material.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = selectedCategory === "all" || p.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-4 mt-4">
      {/* Search and Filter */}
      <div className="flex flex-wrap gap-4">
        <div className="flex-1 min-w-[300px]">
          <div className="relative">
            <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="Search parts by name, number, or material..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/30 focus:border-vulcan-accent focus:outline-none"
            />
          </div>
        </div>
        <Button variant="primary">
          <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Part
        </Button>
      </div>

      <div className="grid lg:grid-cols-4 gap-6">
        {/* Category Sidebar */}
        <div className="space-y-2">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors text-left ${
                selectedCategory === cat.id
                  ? "bg-vulcan-accent text-white"
                  : "bg-white/5 text-white/60 hover:bg-white/10 hover:text-white"
              }`}
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={cat.icon} />
              </svg>
              <span className="text-sm font-medium">{cat.name}</span>
              <Badge variant="default" size="sm" className="ml-auto">
                {cat.id === "all" ? parts.length : parts.filter(p => p.category === cat.id).length}
              </Badge>
            </button>
          ))}
        </div>

        {/* Parts Grid */}
        <div className="lg:col-span-2">
          <div className="grid gap-3">
            {filtered.map((part) => (
              <Card
                key={part.id}
                className={`cursor-pointer transition-all ${
                  selectedPart?.id === part.id
                    ? "border-vulcan-accent ring-1 ring-vulcan-accent"
                    : "hover:border-white/20"
                }`}
                onClick={() => setSelectedPart(part)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <p className="font-mono text-vulcan-accent text-sm">{part.partNumber}</p>
                      <h3 className="font-medium text-white">{part.name}</h3>
                    </div>
                    <div className="flex gap-1">
                      {part.hasModel && (
                        <div className="w-6 h-6 rounded bg-blue-500/20 flex items-center justify-center" title="3D Model Available">
                          <svg className="w-3.5 h-3.5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
                          </svg>
                        </div>
                      )}
                      {part.hasDrawing && (
                        <div className="w-6 h-6 rounded bg-green-500/20 flex items-center justify-center" title="Drawing Available">
                          <svg className="w-3.5 h-3.5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2 text-xs">
                    <span className="px-2 py-0.5 rounded bg-white/10 text-white/70">{part.material}</span>
                    <span className="px-2 py-0.5 rounded bg-white/10 text-white/70">{part.subcategory}</span>
                    <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400">{part.standard}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Part Details */}
        <div>
          {selectedPart ? (
            <Card className="sticky top-4">
              <CardHeader title={selectedPart.partNumber} subtitle={selectedPart.name} />
              <CardContent className="space-y-4">
                {/* Preview Placeholder */}
                <div className="aspect-square bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg flex items-center justify-center border border-white/10">
                  <div className="text-center">
                    <svg className="w-16 h-16 mx-auto text-white/20 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
                    </svg>
                    <p className="text-xs text-white/30">3D Preview</p>
                  </div>
                </div>

                {/* Specs */}
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between py-1 border-b border-white/5">
                    <span className="text-white/50">Category</span>
                    <span className="text-white">{selectedPart.subcategory}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-white/5">
                    <span className="text-white/50">Material</span>
                    <span className="text-white">{selectedPart.material}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-white/5">
                    <span className="text-white/50">Specifications</span>
                    <span className="text-white text-right text-xs">{selectedPart.specs}</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-white/50">Standard</span>
                    <span className="text-amber-400">{selectedPart.standard}</span>
                  </div>
                </div>

                {/* Actions */}
                <div className="space-y-2 pt-2">
                  <Button variant="primary" className="w-full" disabled={!selectedPart.hasModel}>
                    <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Insert into Assembly
                  </Button>
                  <div className="grid grid-cols-2 gap-2">
                    <Button variant="secondary" size="sm" disabled={!selectedPart.hasModel}>
                      Open Model
                    </Button>
                    <Button variant="secondary" size="sm" disabled={!selectedPart.hasDrawing}>
                      View Drawing
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-white/5 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                  </svg>
                </div>
                <p className="text-white/50">Select a part to view details</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
