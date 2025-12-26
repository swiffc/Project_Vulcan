"use client";

import { DashboardGridSkeleton } from "@/components/ui/Skeleton";

export default function Loading() {
  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-8 h-8 rounded-lg bg-white/10 animate-pulse" />
        <div className="h-8 w-48 bg-white/10 rounded-lg animate-pulse" />
      </div>
      <DashboardGridSkeleton />
    </div>
  );
}
