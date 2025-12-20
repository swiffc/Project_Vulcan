import { NextResponse } from "next/server";
import { getEmails, getUnreadCount } from "@/lib/work/microsoft-client";
import { isMicrosoftTokenValid } from "@/lib/work/token-manager";

export const runtime = "nodejs";

export async function GET(request: Request) {
  try {
    // Check if authenticated
    const isValid = await isMicrosoftTokenValid();
    if (!isValid) {
      return NextResponse.json(
        { error: "Not authenticated", authenticated: false },
        { status: 401 }
      );
    }

    const { searchParams } = new URL(request.url);
    const top = parseInt(searchParams.get("top") || "20", 10);
    const unreadOnly = searchParams.get("unreadOnly") === "true";

    // Get emails and unread count in parallel
    const [emails, unreadCount] = await Promise.all([
      getEmails({ top, unreadOnly }),
      getUnreadCount(),
    ]);

    return NextResponse.json({
      emails,
      unreadCount: unreadCount.total,
      importantUnread: unreadCount.important,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("Mail API error:", error);
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Failed to fetch emails",
      },
      { status: 500 }
    );
  }
}
