"use client";

import { motion } from 'framer-motion';

const knowledgeSources = [
  {
    level: 1,
    name: "Internal Standards Standards",
    id: "standards_db.py",
    description: "Hardcoded engineering truth (AISC, ASME B16.5, Pipe Schedules)",
    status: "Online",
    count: "450+ Entities"
  },
  {
    level: 2,
    name: "Digital Twin Wrappers",
    id: "GitHub API",
    description: "Real-time read-only access to external CAD repositories",
    status: "Online",
    repos: ["bolt", "ublox", "adafruit", "soildworks-library", "pipecad"]
  },
  {
    level: 3,
    name: "Autonomous Research",
    id: "Web Search Agent",
    description: "Fallback agent that extracts dimensions from PDF datasheets",
    status: "Standby",
    metrics: "On-Demand"
  }
];

const recentLearnings = [
  { term: "BOP Stack", source: "Web Search (Cameron Spec)", time: "2 hours ago" },
  { term: "30in Flange", source: "Wrapper (bolt)", time: "4 hours ago" },
  { term: "Standard Pipe", source: "Internal DB", time: "1 day ago" }
];

export default function LearningDashboard() {
  return (
    <div className="min-h-screen bg-neutral-950 text-white p-8">
      <header className="mb-12">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-4">
          Learning Dashboard
        </h1>
        <p className="text-neutral-400 text-lg max-w-2xl">
          Visualizing the "Hierarchy of Truth". This dashboard monitors how the agent sources engineering data and what it has recently learned.
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Knowledge Hierarchy Column */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
            <span className="w-2 h-8 bg-purple-500 rounded-full"></span>
            Knowledge Sources
          </h2>

          {knowledgeSources.map((source, idx) => (
            <motion.div
              key={source.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.15 }}
              className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 p-4 opacity-10 font-black text-9xl leading-none select-none text-white">
                {source.level}
              </div>
              
              <div className="relative z-10">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-xl font-bold text-white">{source.name}</h3>
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span className="text-xs font-mono text-emerald-400">{source.status}</span>
                  </div>
                </div>
                
                <code className="text-sm text-purple-400 block mb-3 font-mono">
                  {source.id}
                </code>
                
                <p className="text-neutral-400 mb-4 bg-neutral-950/50 p-3 rounded-lg border border-neutral-800/50">
                  {source.description}
                </p>

                {source.repos && (
                  <div className="flex flex-wrap gap-2 mt-4">
                    {source.repos.map(repo => (
                      <span key={repo} className="px-2 py-1 bg-neutral-800 rounded text-xs text-neutral-300 border border-neutral-700">
                        @{repo}
                      </span>
                    ))}
                  </div>
                )}
                
                {source.count && (
                   <div className="mt-4 text-sm font-mono text-neutral-500">
                     Indexed: {source.count}
                   </div>
                )}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Recent Activity Column */}
        <div className="space-y-6">
           <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
            <span className="w-2 h-8 bg-pink-500 rounded-full"></span>
            Recent Acquisitions
          </h2>
          
          <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 h-fit">
            <div className="space-y-6">
              {recentLearnings.map((item, idx) => (
                <div key={idx} className="flex items-start gap-3 border-l-2 border-neutral-800 pl-4 py-1 hover:border-pink-500 transition-colors">
                  <div>
                    <div className="text-white font-medium">{item.term}</div>
                    <div className="text-xs text-neutral-500 font-mono mt-1">Source: {item.source}</div>
                    <div className="text-xs text-neutral-600 mt-1">{item.time}</div>
                  </div>
                </div>
              ))}
            </div>
            
            <button className="w-full mt-8 py-3 rounded-lg border border-neutral-700 text-neutral-400 hover:bg-neutral-800 hover:text-white transition-all text-sm font-medium">
              View Full History
            </button>
          </div>

          <div className="bg-gradient-to-br from-indigo-900/40 to-purple-900/40 border border-indigo-500/30 rounded-xl p-6">
             <h3 className="text-lg font-semibold text-white mb-2">Capabilities</h3>
             <ul className="space-y-2 text-sm text-neutral-300">
               <li className="flex items-center gap-2">
                 ✅ <span className="text-neutral-400">Standard Parts (Bolts, Pipe)</span>
               </li>
               <li className="flex items-center gap-2">
                 ✅ <span className="text-neutral-400">Vessel Design (Shells, Heads)</span>
               </li>
               <li className="flex items-center gap-2">
                 ✅ <span className="text-neutral-400">Complex Assemblies (BOPs)</span>
               </li>
               <li className="flex items-center gap-2">
                 ✅ <span className="text-neutral-400">Weld Validation (ASME)</span>
               </li>
             </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
