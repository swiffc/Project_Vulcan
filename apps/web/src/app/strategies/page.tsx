"use client";

import { useState, useEffect } from 'react';

interface Strategy {
  id: number;
  name: string;
  description: string;
  product_type: string;
  is_experimental: boolean;
  created_at?: string;
}

export default function StrategiesPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    try {
      // Try to fetch from the orchestrator API
      const orchestratorUrl = process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || 'http://localhost:8000';
      const response = await fetch(`${orchestratorUrl}/api/strategies`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch strategies');
      }
      
      const data = await response.json();
      setStrategies(data.strategies || []);
    } catch (err) {
      console.error('Error loading strategies:', err);
      // Load fallback mock data
      setStrategies([
        {
          id: 1,
          name: "flange_rfwn",
          description: "ASME B16.5 Raised Face Weld Neck Flange",
          product_type: "standard_part",
          is_experimental: false,
        },
        {
          id: 2,
          name: "pipe_segment",
          description: "Standard Pipe Segment with ASME specs",
          product_type: "standard_part",
          is_experimental: false,
        },
        {
          id: 3,
          name: "pressure_vessel_shell",
          description: "Multi-body Revolve for Vessel Shell + Heads",
          product_type: "manufacturing",
          is_experimental: true,
        },
        {
          id: 4,
          name: "repad_curved",
          description: "Reinforcement Pad on Curved Surface",
          product_type: "feature",
          is_experimental: true,
        }
      ]);
      setError('Using offline strategy data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (strategy: Strategy) => {
    if (strategy.is_experimental) {
      return <span className="px-3 py-1 rounded-full text-xs font-medium bg-yellow-500/20 text-yellow-400">Experimental</span>;
    }
    return <span className="px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/20 text-emerald-400">Active</span>;
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white p-8">
      <header className="mb-12">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent mb-4">
          CAD Strategies Library
        </h1>
        <p className="text-neutral-400 text-lg max-w-2xl">
          The central repository of engineering intelligence. These strategies define how the Vulcan Bot converts intent into manufacturing-ready SolidWorks models.
        </p>
        {error && (
          <div className="mt-4 px-4 py-2 bg-yellow-500/10 border border-yellow-500/20 rounded-lg text-yellow-400 text-sm">
            {error}
          </div>
        )}
      </header>

      {loading ? (
        <div className="text-center py-12 text-neutral-400">
          Loading strategies...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {strategies.map((strategy, idx) => (
            <div
              key={strategy.id}
              className="p-6 rounded-xl bg-neutral-900 border border-neutral-800 hover:border-blue-500/50 transition-colors group"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-white group-hover:text-blue-400 transition-colors">
                    {strategy.name}
                  </h3>
                  <span className="inline-block mt-2 px-2 py-1 text-xs font-mono rounded bg-neutral-800 text-neutral-400">
                    Type: {strategy.product_type}
                  </span>
                </div>
                {getStatusBadge(strategy)}
              </div>
              
              <p className="text-neutral-400 mb-6">
                {strategy.description}
              </p>

              <div className="flex items-center justify-between pt-4 border-t border-neutral-800">
                <span className="text-xs text-neutral-500 font-mono">
                  ID: {strategy.id}
                </span>
                <button 
                  onClick={() => {
                    const orchestratorUrl = process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || 'http://localhost:8000';
                    window.open(`${orchestratorUrl}/api/strategies/${strategy.id}`, '_blank');
                  }}
                  className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
                >
                  View JSON →
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
