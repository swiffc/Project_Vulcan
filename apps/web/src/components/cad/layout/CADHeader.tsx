"use client";

import { Bell, Settings, Power } from "lucide-react";

export default function CADHeader() {
  return (
    <header className="glass-base border-b border-white/10 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Logo/Title */}
        <div className="flex items-center space-x-4">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <svg
              className="w-6 h-6 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">CAD Agent AI</h1>
            <p className="text-xs text-gray-400">SolidWorks • Inventor • AutoCAD</p>
          </div>
        </div>

        {/* Connection Status */}
        <div className="flex items-center space-x-4">
          {/* SolidWorks Status */}
          <div className="flex items-center space-x-2 px-4 py-2 rounded-lg glass-success">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-sm font-medium text-emerald-100">SolidWorks Connected</span>
          </div>

          {/* Action Buttons */}
          <button className="p-2 rounded-lg hover:bg-white/10 transition-colors relative">
            <Bell className="w-5 h-5 text-gray-300" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
          </button>
          
          <button className="p-2 rounded-lg hover:bg-white/10 transition-colors">
            <Settings className="w-5 h-5 text-gray-300" />
          </button>
          
          <button className="p-2 rounded-lg hover:bg-red-500/20 transition-colors">
            <Power className="w-5 h-5 text-red-400" />
          </button>
        </div>
      </div>
    </header>
  );
}
