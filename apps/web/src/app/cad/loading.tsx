"use client";

import { ValidationResultSkeleton } from "@/components/ui/Skeleton";

export default function CADLoading() {
  return (
    <div className="p-6">
      {/* Header skeleton */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/10 animate-pulse" />
          <div>
            <div className="h-7 w-40 bg-white/10 rounded animate-pulse mb-2" />
            <div className="h-4 w-64 bg-white/10 rounded animate-pulse" />
          </div>
        </div>
        <div className="h-6 w-24 bg-white/10 rounded-full animate-pulse" />
      </div>

      {/* Tabs skeleton */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="h-10 w-28 bg-white/10 rounded-lg animate-pulse flex-shrink-0" />
        ))}
      </div>

      {/* Content skeleton */}
      <ValidationResultSkeleton />
    </div>
  );
}
