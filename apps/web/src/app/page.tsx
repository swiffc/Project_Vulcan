"use client";

import {
  SystemStatus,
  QuickActions,
  RecentActivity,
  PerformanceMetrics,
  CostDashboard,
  RealTimeMetrics,
} from "@/components/dashboard";

export default function DashboardPage() {
  return (
    <div className="p-4 md:p-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Dashboard</h1>
            <p className="text-white/50">System overview and quick actions</p>
          </div>
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full glass-success">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs text-emerald-300 font-medium">
              ULTIMATE Stack Active
            </span>
          </div>
        </div>
      </div>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-4 md:gap-6">
        {/* Left Column - Status & Performance */}
        <div className="xl:col-span-2 space-y-4 md:space-y-6">
          <SystemStatus />
          <RealTimeMetrics />
          <PerformanceMetrics />
        </div>

        {/* Middle Column - Cost & Actions */}
        <div className="xl:col-span-1 space-y-4 md:space-y-6">
          <CostDashboard />
          <QuickActions />
        </div>

        {/* Right Column - Activity Feed */}
        <div className="xl:col-span-1">
          <RecentActivity />
        </div>
      </div>

      {/* Footer Stats Bar */}
      <div className="mt-6 p-4 rounded-xl glass flex items-center justify-between text-xs text-white/40">
        <div className="flex items-center gap-6">
          <span>Phase 8.5 ULTIMATE</span>
          <span className="hidden md:inline">|</span>
          <span className="hidden md:inline">90-95% Cost Reduction</span>
          <span className="hidden md:inline">|</span>
          <span className="hidden md:inline">Redis + Model Router + Prompt Cache</span>
        </div>
        <div className="flex items-center gap-2">
          <span>Powered by</span>
          <span className="text-indigo-400 font-medium">Claude</span>
        </div>
      </div>
    </div>
  );
}
