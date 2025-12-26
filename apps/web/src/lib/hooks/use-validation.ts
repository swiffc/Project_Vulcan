"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import type { ValidationResult, ApiResponse } from "@/lib/types/api";

const DESKTOP_SERVER_URL = process.env.NEXT_PUBLIC_DESKTOP_SERVER_URL || "http://localhost:8000";

// Fetch validation history
async function fetchValidationHistory(): Promise<ValidationResult[]> {
  const response = await fetch(`${DESKTOP_SERVER_URL}/api/v1/validation/history`);
  if (!response.ok) {
    throw new Error("Failed to fetch validation history");
  }
  const data = await response.json();
  return data.validations || [];
}

// Run validation on a file
async function runValidation(filePath: string): Promise<ValidationResult> {
  const response = await fetch(`${DESKTOP_SERVER_URL}/api/v1/validation/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ file_path: filePath }),
  });

  if (!response.ok) {
    throw new Error("Validation failed");
  }

  return response.json();
}

// Fetch validation statistics
async function fetchValidationStats(): Promise<{
  total_validations: number;
  avg_pass_rate: number;
  total_checks: number;
  by_standard: Record<string, number>;
}> {
  const response = await fetch(`${DESKTOP_SERVER_URL}/api/v1/validation/stats`);
  if (!response.ok) {
    throw new Error("Failed to fetch validation stats");
  }
  return response.json();
}

/**
 * Hook for fetching validation history
 */
export function useValidationHistory() {
  return useQuery({
    queryKey: ["validation", "history"],
    queryFn: fetchValidationHistory,
    staleTime: 60000, // 1 minute
  });
}

/**
 * Hook for running validation
 */
export function useRunValidation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: runValidation,
    onSuccess: () => {
      // Invalidate history to refetch after new validation
      queryClient.invalidateQueries({ queryKey: ["validation", "history"] });
      queryClient.invalidateQueries({ queryKey: ["validation", "stats"] });
    },
  });
}

/**
 * Hook for validation statistics
 */
export function useValidationStats() {
  return useQuery({
    queryKey: ["validation", "stats"],
    queryFn: fetchValidationStats,
    staleTime: 60000, // 1 minute
  });
}

/**
 * Hook for a single validation result
 */
export function useValidationResult(id: string | undefined) {
  return useQuery({
    queryKey: ["validation", "result", id],
    queryFn: async () => {
      if (!id) throw new Error("No validation ID");
      const response = await fetch(`${DESKTOP_SERVER_URL}/api/v1/validation/${id}`);
      if (!response.ok) throw new Error("Failed to fetch validation");
      return response.json() as Promise<ValidationResult>;
    },
    enabled: !!id,
  });
}
