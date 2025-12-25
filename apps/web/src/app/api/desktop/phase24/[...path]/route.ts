import { NextRequest, NextResponse } from "next/server";

const DESKTOP_SERVER_URL =
  process.env.DESKTOP_SERVER_URL || "http://localhost:8000";

// Dynamic route handler for all Phase 24 endpoints
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const endpoint = path.join("/");

  try {
    const response = await fetch(`${DESKTOP_SERVER_URL}/phase24/${endpoint}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });

    if (!response.ok) {
      const error = await response.text();
      return NextResponse.json(
        { error: error || "Request failed" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error(`Phase 24 API error (${endpoint}):`, error);
    return NextResponse.json(
      { error: "Desktop server unreachable" },
      { status: 503 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const endpoint = path.join("/");

  try {
    const body = await request.json();

    const response = await fetch(`${DESKTOP_SERVER_URL}/phase24/${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.text();
      return NextResponse.json(
        { error: error || "Request failed" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error(`Phase 24 API error (${endpoint}):`, error);
    return NextResponse.json(
      { error: "Desktop server unreachable" },
      { status: 503 }
    );
  }
}
