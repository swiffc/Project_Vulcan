import { NextRequest, NextResponse } from "next/server";

const DESKTOP_SERVER_URL =
  process.env.DESKTOP_SERVER_URL || "http://localhost:8000";

export async function GET(request: NextRequest) {
  try {
    const response = await fetch(`${DESKTOP_SERVER_URL}/health`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });

    if (!response.ok) {
      return NextResponse.json(
        { status: "error", message: "Desktop server unhealthy" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { status: "error", message: "Desktop server unreachable" },
      { status: 503 }
    );
  }
}
