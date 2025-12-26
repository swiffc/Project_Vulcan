"use client";

import { useQuery } from "@tanstack/react-query";
import type { HealthResponse } from "@/lib/types/api";

const DESKTOP_SERVER_URL = process.env.NEXT_PUBLIC_DESKTOP_SERVER_URL || "http://localhost:8000";

async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${DESKTOP_SERVER_URL}/health`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Health check failed");
  }

  return response.json();
}

/**
 * Hook for fetching desktop server health status
 * Shared across all components that need health data
 */
export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
    refetchInterval: 30000, // Refetch every 30 seconds
    retry: 1,
    staleTime: 10000, // Consider data stale after 10 seconds
  });
}

/**
 * Hook for fetching health with custom interval
 */
export function useHealthWithInterval(intervalMs: number) {
  return useQuery({
    queryKey: ["health", intervalMs],
    queryFn: fetchHealth,
    refetchInterval: intervalMs,
    retry: 1,
  });
}
