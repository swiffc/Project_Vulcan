"use client";

import { CardSkeleton } from "@/components/ui/Skeleton";

export default function WorkLoading() {
  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header skeleton */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-white/10 animate-pulse" />
        <div>
          <div className="h-7 w-32 bg-white/10 rounded animate-pulse mb-2" />
          <div className="h-4 w-56 bg-white/10 rounded animate-pulse" />
        </div>
      </div>

      {/* Cards skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CardSkeleton />
        <CardSkeleton />
        <CardSkeleton />
        <CardSkeleton />
      </div>
    </div>
  );
}
