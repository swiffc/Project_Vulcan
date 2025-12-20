"use client";

import {
  SystemStatus,
  QuickActions,
  RecentActivity,
  PerformanceMetrics,
} from "@/components/dashboard";

export default function DashboardPage() {
  return (
    <div className="p-4 md:p-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-white/50">System overview and quick actions</p>
      </div>

      {/* Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
        {/* Left Column - Status & Actions */}
        <div className="lg:col-span-2 space-y-4 md:space-y-6">
          <SystemStatus />
          <QuickActions />
          <PerformanceMetrics />
        </div>

        {/* Right Column - Activity Feed */}
        <div className="lg:col-span-1">
          <RecentActivity />
        </div>
      </div>
    </div>
  );
}
