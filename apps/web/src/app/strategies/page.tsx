"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';

// Mock data based on seed_strategies.json
const strategies = [
  {
    name: "flange_rfwn",
    description: "ASME B16.5 Raised Face Weld Neck Flange",
    type: "Standard Part",
    source: "Wrapper (bolt)",
    status: "Active"
  },
  {
    name: "pipe_segment",
    description: "Standard Pipe Segment",
    type: "Standard Part",
    source: "Hybrid (DB + Extrude)",
    status: "Active"
  },
  {
    name: "pressure_vessel_shell",
    description: "Multi-body Revolve for Vessel Shell + Heads",
    type: "Manufacturing",
    source: "Parametric Logic",
    status: "Beta"
  },
  {
    name: "repad_curved",
    description: "Reinforcement Pad on Curved Surface (Offset/Thicken)",
    type: "Feature",
    source: "Elite Logic",
    status: "Development"
  }
];

export default function StrategiesPage() {
  return (
    <div className="min-h-screen bg-neutral-950 text-white p-8">
      <header className="mb-12">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent mb-4">
          CAD Strategies Library
        </h1>
        <p className="text-neutral-400 text-lg max-w-2xl">
          The central repository of engineering intelligence. These strategies define how the Vulcan Bot converts intent into manufacturing-ready SolidWorks models.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {strategies.map((strategy, idx) => (
          <motion.div
            key={strategy.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="p-6 rounded-xl bg-neutral-900 border border-neutral-800 hover:border-blue-500/50 transition-colors group"
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-semibold text-white group-hover:text-blue-400 transition-colors">
                  {strategy.name}
                </h3>
                <span className="inline-block mt-2 px-2 py-1 text-xs font-mono rounded bg-neutral-800 text-neutral-400">
                  Type: {strategy.type}
                </span>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                strategy.status === 'Active' ? 'bg-emerald-500/20 text-emerald-400' :
                strategy.status === 'Beta' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-blue-500/20 text-blue-400'
              }`}>
                {strategy.status}
              </span>
            </div>
            
            <p className="text-neutral-400 mb-6">
              {strategy.description}
            </p>

            <div className="flex items-center justify-between pt-4 border-t border-neutral-800">
              <span className="text-xs text-neutral-500 font-mono">
                Source: {strategy.source}
              </span>
              <button className="text-sm text-blue-400 hover:text-blue-300 transition-colors">
                View JSON →
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
