import { NextResponse } from "next/server";
import { getRecentFiles, searchFiles } from "@/lib/work/microsoft-client";
import { isMicrosoftTokenValid } from "@/lib/work/token-manager";

export const runtime = "nodejs";

export async function GET(request: Request) {
  try {
    const isValid = await isMicrosoftTokenValid();
    if (!isValid) {
      return NextResponse.json(
        { error: "Not authenticated", authenticated: false },
        { status: 401 }
      );
    }

    const { searchParams } = new URL(request.url);
    const query = searchParams.get("q");
    const top = parseInt(searchParams.get("top") || "10", 10);

    let files;
    if (query) {
      files = await searchFiles(query, top);
    } else {
      files = await getRecentFiles(top);
    }

    return NextResponse.json({
      files,
      source: "onedrive",
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("Files API error:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to fetch files" },
      { status: 500 }
    );
  }
}
