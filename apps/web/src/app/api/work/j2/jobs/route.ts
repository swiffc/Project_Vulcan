import { NextRequest, NextResponse } from "next/server";
import { getJ2Jobs, getMyJ2Jobs, getJ2ForWorkHub, isDesktopServerAvailable } from "@/lib/work/j2-client";

export const runtime = "nodejs";

export async function GET(request: NextRequest) {
  try {
    // Check Desktop Server first
    const desktopAvailable = await isDesktopServerAvailable();

    if (!desktopAvailable) {
      return NextResponse.json(
        {
          success: false,
          error: "Desktop Server not running",
          jobs: [],
          summary: { total: 0, active: 0, overdue: 0, dueThisWeek: 0 },
          sessionValid: false,
        },
        { status: 503 }
      );
    }

    // Parse query params
    const { searchParams } = new URL(request.url);
    const view = searchParams.get("view"); // "my" for my jobs, "all" for all, "hub" for work hub format
    const status = searchParams.get("status");
    const assignedTo = searchParams.get("assigned_to");
    const limit = searchParams.get("limit");

    let result;

    switch (view) {
      case "hub":
        // Format for Work Hub widget
        result = await getJ2ForWorkHub();
        break;

      case "my":
        // My assigned jobs
        result = await getMyJ2Jobs();
        break;

      case "all":
      default:
        // All jobs with optional filters
        result = await getJ2Jobs({
          status: status || undefined,
          assignedTo: assignedTo || undefined,
          limit: limit ? parseInt(limit, 10) : undefined,
        });
        break;
    }

    if (!result) {
      return NextResponse.json(
        {
          success: false,
          error: "Failed to fetch J2 jobs. You may need to log in first.",
          jobs: [],
          summary: { total: 0, active: 0, overdue: 0, dueThisWeek: 0 },
          sessionValid: false,
        },
        { status: 401 }
      );
    }

    return NextResponse.json({
      success: true,
      ...result,
    });
  } catch (error) {
    console.error("J2 jobs fetch error:", error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
        jobs: [],
        summary: { total: 0, active: 0, overdue: 0, dueThisWeek: 0 },
        sessionValid: false,
      },
      { status: 500 }
    );
  }
}
