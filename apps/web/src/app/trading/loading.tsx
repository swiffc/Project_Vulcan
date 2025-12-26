"use client";

export default function TradingLoading() {
  return (
    <div className="h-screen flex flex-col">
      {/* Header skeleton */}
      <div className="h-14 border-b border-white/10 bg-white/5 flex items-center px-4 gap-4">
        <div className="h-8 w-32 bg-white/10 rounded-lg animate-pulse" />
        <div className="h-8 w-48 bg-white/10 rounded-lg animate-pulse" />
        <div className="flex-1" />
        <div className="h-8 w-24 bg-white/10 rounded-lg animate-pulse" />
      </div>

      {/* Main content skeleton */}
      <div className="flex-1 flex">
        {/* Left panel skeleton */}
        <div className="w-80 border-r border-white/10 p-4 space-y-4">
          <div className="h-10 bg-white/10 rounded-lg animate-pulse" />
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-16 bg-white/10 rounded-lg animate-pulse" />
          ))}
        </div>

        {/* Center chart area */}
        <div className="flex-1 p-4">
          <div className="h-full bg-white/5 rounded-xl animate-pulse" />
        </div>

        {/* Right panel skeleton */}
        <div className="w-80 border-l border-white/10 p-4 space-y-4">
          <div className="h-10 bg-white/10 rounded-lg animate-pulse" />
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 bg-white/10 rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    </div>
  );
}
