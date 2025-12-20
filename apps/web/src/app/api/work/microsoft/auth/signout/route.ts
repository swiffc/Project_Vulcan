import { NextResponse } from "next/server";
import { signOut } from "@/lib/work/microsoft-client";

export const runtime = "nodejs";

export async function POST() {
  try {
    await signOut();

    return NextResponse.json({
      success: true,
      message: "Signed out successfully",
    });
  } catch (error) {
    console.error("Sign out error:", error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Failed to sign out",
      },
      { status: 500 }
    );
  }
}
