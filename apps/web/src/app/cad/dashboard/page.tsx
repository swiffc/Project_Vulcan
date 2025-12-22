"use client";

import { useState } from "react";
import CADHeader from "@/components/cad/layout/CADHeader";
import CADNav from "@/components/cad/layout/CADNav";
import StatusBar from "@/components/cad/layout/StatusBar";
import SystemStatus from "@/components/cad/dashboard/SystemStatus";
import JobQueueWidget from "@/components/cad/dashboard/JobQueueWidget";
import PerformanceWidget from "@/components/cad/dashboard/PerformanceWidget";
import RecentFiles from "@/components/cad/dashboard/RecentFiles";
import QuickActions from "@/components/cad/dashboard/QuickActions";

export default function CADDashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <CADHeader />

      <div className="flex flex-1 overflow-hidden">
        {/* Side Navigation */}
        <CADNav isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* Header */}
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">CAD Dashboard</h1>
              <p className="text-gray-400">
                Workspace overview • SolidWorks integration • Performance monitoring
              </p>
            </div>

            {/* Top Row: System Status + Quick Actions */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
              <div className="xl:col-span-2">
                <SystemStatus />
              </div>
              <QuickActions />
            </div>

            {/* Middle Row: Job Queue + Performance */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <JobQueueWidget />
              <PerformanceWidget />
            </div>

            {/* Bottom Row: Recent Files */}
            <RecentFiles />
          </div>
        </main>
      </div>

      {/* Status Bar */}
      <StatusBar />
    </div>
  );
}
