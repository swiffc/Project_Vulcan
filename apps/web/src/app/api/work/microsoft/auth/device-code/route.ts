import { NextResponse } from "next/server";
import { initiateDeviceCodeFlow, checkDeviceCodeStatus } from "@/lib/work/microsoft-client";

export const runtime = "nodejs";

// POST: Start device code flow
export async function POST() {
  try {
    const result = await initiateDeviceCodeFlow();

    return NextResponse.json({
      success: true,
      userCode: result.userCode,
      verificationUri: result.verificationUri,
      message: result.message,
      expiresIn: result.expiresIn,
      requestId: result.requestId,
    });
  } catch (error) {
    console.error("Device code flow error:", error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Failed to start authentication",
      },
      { status: 500 }
    );
  }
}

// GET: Check status of device code flow
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const requestId = searchParams.get("requestId");

    if (!requestId) {
      return NextResponse.json(
        { success: false, error: "Missing requestId" },
        { status: 400 }
      );
    }

    const status = await checkDeviceCodeStatus(requestId);

    return NextResponse.json({
      success: true,
      ...status,
    });
  } catch (error) {
    console.error("Device code status check error:", error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Failed to check status",
      },
      { status: 500 }
    );
  }
}
