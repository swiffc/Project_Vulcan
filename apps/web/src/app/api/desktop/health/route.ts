import { NextResponse } from "next/server";

const DESKTOP_SERVER_URL =
  process.env.DESKTOP_SERVER_URL || "http://localhost:8000";

export async function GET() {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 2000); // 2 second timeout

  try {
    const response = await fetch(`${DESKTOP_SERVER_URL}/health`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      return NextResponse.json(
        { status: "error", message: "Desktop server unhealthy" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    clearTimeout(timeoutId);
    return NextResponse.json(
      { status: "offline", message: "Desktop server unreachable" },
      { status: 200 } // Return 200 so it doesn't cause UI errors
    );
  }
}
