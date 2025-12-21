import { NextResponse } from "next/server";
import { isDesktopServerAvailable, getJ2Status } from "@/lib/work/j2-client";
import { getJ2SessionStatus } from "@/lib/work/token-manager";

export const runtime = "nodejs";

export async function GET() {
  try {
    // Check Desktop Server first
    const desktopAvailable = await isDesktopServerAvailable();

    if (!desktopAvailable) {
      return NextResponse.json({
        available: false,
        sessionValid: false,
        message: "Desktop Server not running. Start it to access J2 Tracker.",
      });
    }

    // Check J2 session status
    const j2Status = await getJ2Status();
    const localStatus = await getJ2SessionStatus();

    return NextResponse.json({
      available: true,
      browserAvailable: j2Status?.browser_available ?? false,
      sessionValid: j2Status?.session_valid ?? false,
      localSessionValid: localStatus.isAuthenticated,
      j2BaseUrl: j2Status?.j2_base_url ?? null,
    });
  } catch (error) {
    console.error("J2 status check failed:", error);
    return NextResponse.json(
      {
        available: false,
        sessionValid: false,
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
