import { NextResponse } from "next/server";
import { startJ2Login, j2Logout, isDesktopServerAvailable } from "@/lib/work/j2-client";

export const runtime = "nodejs";

export async function POST() {
  try {
    // Check Desktop Server first
    const desktopAvailable = await isDesktopServerAvailable();

    if (!desktopAvailable) {
      return NextResponse.json(
        {
          success: false,
          error: "Desktop Server not running. Start the Desktop Server first.",
        },
        { status: 503 }
      );
    }

    // Start login process (opens browser for SSO)
    const result = await startJ2Login(120); // 2 minute timeout

    if (!result) {
      return NextResponse.json(
        {
          success: false,
          error: "Failed to start J2 login. Check Desktop Server logs.",
        },
        { status: 500 }
      );
    }

    if (result.status === "authenticated") {
      return NextResponse.json({
        success: true,
        status: "authenticated",
        url: result.url,
        message: "Successfully logged in to J2 Tracker",
      });
    }

    if (result.status === "timeout") {
      return NextResponse.json(
        {
          success: false,
          status: "timeout",
          message: result.message || "Login timed out. Try again.",
        },
        { status: 408 }
      );
    }

    return NextResponse.json(
      {
        success: false,
        status: result.status,
        message: result.message || "Login failed",
      },
      { status: 400 }
    );
  } catch (error) {
    console.error("J2 login error:", error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}

export async function DELETE() {
  try {
    const success = await j2Logout();

    return NextResponse.json({
      success,
      message: success ? "Logged out of J2 Tracker" : "Logout failed",
    });
  } catch (error) {
    console.error("J2 logout error:", error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
