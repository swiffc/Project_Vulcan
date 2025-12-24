import React, { useEffect, useRef, useState } from 'react';

// Types representing GD&T data structures
interface GDTFeature {
  id: string;
  type: 'flatness' | 'parallelism' | 'perpendicularity' | 'position' | 'surface_profile';
  value: number;
  tolerance: number;
  datum_refs: string[];
  status: 'pass' | 'fail' | 'warning';
}

interface GDTViewerProps {
  modelUrl?: string; // URL to the GLB/GLTF model
  features: GDTFeature[];
  onFeatureSelect?: (feature: GDTFeature) => void;
}

/**
 * GDTViewer - Geometric Dimensioning and Tolerancing Visualization
 * 
 * Displays a list of GD&T callouts and (eventually) overlays them on a 3D model.
 */
export const GDTViewer: React.FC<GDTViewerProps> = ({ modelUrl, features, onFeatureSelect }) => {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const handleSelect = (feature: GDTFeature) => {
    setSelectedId(feature.id);
    if (onFeatureSelect) onFeatureSelect(feature);
  };

  return (
    <div className="flex flex-col h-full bg-slate-50 border rounded-lg overflow-hidden">
      <div className="bg-slate-800 text-white p-3 font-semibold flex justify-between items-center">
        <span>GD&T Inspector</span>
        <span className="text-xs bg-slate-600 px-2 py-1 rounded">
          {features.length} features
        </span>
      </div>

      <div className="flex-1 overflow-auto p-4 space-y-3">
        {/* 3D Viewer Placeholder */}
        <div className="aspect-video bg-slate-200 rounded-md flex items-center justify-center border-2 border-dashed border-slate-300 mb-4">
          {modelUrl ? (
             <div className="text-center">
               <p className="text-slate-500 font-medium">3D Model Loaded</p>
               <p className="text-xs text-slate-400">{modelUrl}</p>
               {/* Integration point for Three.js Canvas */}
             </div>
          ) : (
            <p className="text-slate-400">No Model Loaded</p>
          )}
        </div>

        {/* Feature List */}
        <div className="grid grid-cols-1 gap-2">
          {features.map((feature) => (
            <div
              key={feature.id}
              onClick={() => handleSelect(feature)}
              className={`
                p-3 rounded border transition-all cursor-pointer flex justify-between items-center
                ${selectedId === feature.id ? 'border-blue-500 bg-blue-50 shadow-sm' : 'border-slate-200 hover:bg-slate-100'}
              `}
            >
              <div className="flex flex-col">
                <div className="flex items-center gap-2">
                   <span className="font-bold text-slate-700 uppercase">{feature.type.replace('_', ' ')}</span>
                   {feature.datum_refs.length > 0 && (
                     <span className="text-xs text-slate-500 bg-slate-200 px-1 rounded">
                       {feature.datum_refs.join('-')}
                     </span>
                   )}
                </div>
                <span className="text-sm text-slate-600">
                  Measured: {feature.value.toFixed(3)} / Tol: {feature.tolerance.toFixed(3)}
                </span>
              </div>

              <StatusBadge status={feature.status} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const StatusBadge: React.FC<{ status: 'pass' | 'fail' | 'warning' }> = ({ status }) => {
  const styles = {
    pass: "bg-green-100 text-green-700 border-green-200",
    fail: "bg-red-100 text-red-700 border-red-200",
    warning: "bg-amber-100 text-amber-700 border-amber-200"
  };
  
  const icons = {
    pass: "✓",
    fail: "✗",
    warning: "!"
  };

  return (
    <div className={`px-2 py-1 rounded text-xs font-bold border ${styles[status]} flex items-center gap-1 min-w-[60px] justify-center`}>
      <span>{icons[status]}</span>
      <span className="uppercase">{status}</span>
    </div>
  );
};

export default GDTViewer;
