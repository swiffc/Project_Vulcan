import { NextResponse } from "next/server";
import { getCurrentUser, getAccessToken } from "@/lib/work/microsoft-client";
import { isMicrosoftTokenValid } from "@/lib/work/token-manager";

export const runtime = "nodejs";

export async function GET() {
  try {
    const isValid = await isMicrosoftTokenValid();

    if (!isValid) {
      return NextResponse.json({
        isAuthenticated: false,
      });
    }

    // Try to get user info
    const user = await getCurrentUser();

    if (!user) {
      return NextResponse.json({
        isAuthenticated: false,
        error: "Could not fetch user info",
      });
    }

    return NextResponse.json({
      isAuthenticated: true,
      userEmail: user.email,
      userName: user.name,
    });
  } catch (error) {
    console.error("Auth status check error:", error);
    return NextResponse.json({
      isAuthenticated: false,
      error: error instanceof Error ? error.message : "Failed to check auth status",
    });
  }
}
