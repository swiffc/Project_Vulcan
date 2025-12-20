import { NextResponse } from "next/server";
import { getTeamsChats, getTeamsMentions } from "@/lib/work/microsoft-client";
import { isMicrosoftTokenValid } from "@/lib/work/token-manager";

export const runtime = "nodejs";

export async function GET() {
  try {
    const isValid = await isMicrosoftTokenValid();
    if (!isValid) {
      return NextResponse.json(
        { error: "Not authenticated", authenticated: false },
        { status: 401 }
      );
    }

    const [chats, mentions] = await Promise.all([
      getTeamsChats(10),
      getTeamsMentions(),
    ]);

    const totalUnread = chats.reduce((sum, chat) => sum + chat.unreadCount, 0);

    return NextResponse.json({
      chats,
      mentions,
      totalUnread,
      mentionCount: mentions.length,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("Teams API error:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to fetch Teams data" },
      { status: 500 }
    );
  }
}
