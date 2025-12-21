/**
 * J2 Tracker Client
 *
 * Communicates with Desktop Server to access J2 Tracker via browser automation.
 * J2 requires SSO login which is handled by opening a visible browser window.
 */

import type { J2Job, J2Summary, J2SessionStatus, J2Response } from "./types";
import { storeJ2Session, getJ2Session, removeJ2Session } from "./token-manager";

// Desktop Server URL (runs on local machine)
const DESKTOP_SERVER_URL = process.env.DESKTOP_SERVER_URL || "http://localhost:8000";

// ============= Types =============

interface J2StatusResponse {
  browser_available: boolean;
  session_valid: boolean;
  j2_base_url: string;
  session_id: string;
}

interface J2LoginResponse {
  status: "authenticated" | "timeout" | "error";
  url?: string;
  cookies_saved?: boolean;
  message?: string;
}

interface J2JobsResponse {
  jobs: J2Job[];
  summary: J2Summary;
  session_valid: boolean;
  last_refresh: string;
}

// ============= Helper Functions =============

async function desktopRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T | null> {
  try {
    const response = await fetch(`${DESKTOP_SERVER_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      console.error(`Desktop Server error: ${response.status} ${response.statusText}`);
      return null;
    }

    return response.json();
  } catch (error) {
    console.error("Desktop Server connection error:", error);
    return null;
  }
}

// ============= Status & Authentication =============

/**
 * Check if Desktop Server is running and J2 session is valid
 */
export async function getJ2Status(): Promise<J2StatusResponse | null> {
  return desktopRequest<J2StatusResponse>("/j2/status");
}

/**
 * Check if Desktop Server is reachable
 */
export async function isDesktopServerAvailable(): Promise<boolean> {
  try {
    const response = await fetch(`${DESKTOP_SERVER_URL}/health`, {
      method: "GET",
      signal: AbortSignal.timeout(3000), // 3 second timeout
    });
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Start J2 SSO login process
 * Opens a browser window for user to complete authentication
 */
export async function startJ2Login(timeout = 120): Promise<J2LoginResponse | null> {
  const result = await desktopRequest<J2LoginResponse>("/j2/login", {
    method: "POST",
    body: JSON.stringify({ timeout }),
  });

  if (result?.status === "authenticated" && result.cookies_saved) {
    // Store session info locally
    await storeJ2Session("j2_authenticated", Date.now() + 24 * 60 * 60 * 1000); // 24 hour expiry
  }

  return result;
}

/**
 * Clear J2 session
 */
export async function j2Logout(): Promise<boolean> {
  await removeJ2Session();
  const result = await desktopRequest<{ status: string }>("/j2/logout", {
    method: "POST",
  });
  return result?.status === "ok";
}

/**
 * Get J2 session status from local storage
 */
export async function getLocalJ2Status(): Promise<J2SessionStatus> {
  const session = await getJ2Session();

  if (!session) {
    return { isAuthenticated: false };
  }

  const isValid = session.expiresAt > Date.now();

  return {
    isAuthenticated: isValid,
    expiresAt: session.expiresAt,
  };
}

// ============= Job Data =============

/**
 * Get all jobs from J2 Tracker
 */
export async function getJ2Jobs(options?: {
  status?: string;
  assignedTo?: string;
  limit?: number;
}): Promise<J2JobsResponse | null> {
  const params = new URLSearchParams();

  if (options?.status) params.append("status", options.status);
  if (options?.assignedTo) params.append("assigned_to", options.assignedTo);
  if (options?.limit) params.append("limit", options.limit.toString());

  const queryString = params.toString();
  const endpoint = `/j2/jobs${queryString ? `?${queryString}` : ""}`;

  return desktopRequest<J2JobsResponse>(endpoint);
}

/**
 * Get jobs assigned to the current user
 */
export async function getMyJ2Jobs(): Promise<J2JobsResponse | null> {
  return desktopRequest<J2JobsResponse>("/j2/my-jobs");
}

/**
 * Get details for a specific job
 */
export async function getJ2JobDetail(jobId: string): Promise<J2Job | null> {
  return desktopRequest<J2Job>(`/j2/jobs/${jobId}`);
}

// ============= Summary =============

/**
 * Get J2 summary for dashboard widget
 */
export async function getJ2Summary(): Promise<{
  summary: J2Summary;
  topJobs: J2Job[];
} | null> {
  const result = await getMyJ2Jobs();

  if (!result) return null;

  // Get top 5 most urgent jobs (overdue first, then due soon)
  const sortedJobs = [...result.jobs].sort((a, b) => {
    // Prioritize overdue
    const aOverdue = a.due_date && new Date(a.due_date) < new Date();
    const bOverdue = b.due_date && new Date(b.due_date) < new Date();

    if (aOverdue && !bOverdue) return -1;
    if (!aOverdue && bOverdue) return 1;

    // Then by priority
    const priorityOrder = { Critical: 0, High: 1, Medium: 2, Low: 3 };
    const aPriority = priorityOrder[a.priority as keyof typeof priorityOrder] ?? 2;
    const bPriority = priorityOrder[b.priority as keyof typeof priorityOrder] ?? 2;

    if (aPriority !== bPriority) return aPriority - bPriority;

    // Then by due date
    if (a.due_date && b.due_date) {
      return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
    }

    return 0;
  });

  return {
    summary: result.summary,
    topJobs: sortedJobs.slice(0, 5),
  };
}

// ============= Formatted Response for Work Hub =============

/**
 * Get J2 data formatted for the Work Hub widget
 */
export async function getJ2ForWorkHub(): Promise<J2Response | null> {
  const status = await getJ2Status();

  if (!status?.browser_available) {
    return {
      jobs: [],
      summary: { total: 0, active: 0, overdue: 0, dueThisWeek: 0 },
      sessionValid: false,
    };
  }

  if (!status.session_valid) {
    return {
      jobs: [],
      summary: { total: 0, active: 0, overdue: 0, dueThisWeek: 0 },
      sessionValid: false,
    };
  }

  const result = await getMyJ2Jobs();

  if (!result) {
    return {
      jobs: [],
      summary: { total: 0, active: 0, overdue: 0, dueThisWeek: 0 },
      sessionValid: false,
    };
  }

  // Transform to Work Hub format
  return {
    jobs: result.jobs.map((job) => ({
      id: job.id,
      title: job.title,
      status: job.status as "Pending" | "In Progress" | "Review" | "Complete" | "On Hold",
      assignedTo: job.assigned_to,
      dueDate: job.due_date || "",
      priority: job.priority as "Low" | "Medium" | "High" | "Critical",
      workflow: {
        currentStep: job.workflow_step || "",
        totalSteps: job.workflow_total || 0,
        completedSteps: job.workflow_current || 0,
      },
      webUrl: job.web_url,
    })),
    summary: {
      total: result.summary.total,
      active: result.summary.active,
      overdue: result.summary.overdue,
      dueThisWeek: result.summary.due_this_week,
    },
    sessionValid: result.session_valid,
  };
}
