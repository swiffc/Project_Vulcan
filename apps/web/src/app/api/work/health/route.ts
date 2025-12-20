import { NextResponse } from "next/server";
import { getTokenStoreInfo, isMicrosoftTokenValid, isJ2SessionValid } from "@/lib/work/token-manager";

export const runtime = "nodejs";

export async function GET() {
  try {
    const storeInfo = await getTokenStoreInfo();
    const microsoftValid = await isMicrosoftTokenValid();
    const j2Valid = await isJ2SessionValid();

    return NextResponse.json({
      status: "ok",
      service: "work-hub",
      timestamp: new Date().toISOString(),
      services: {
        microsoft: {
          configured: storeInfo.hasMicrosoft,
          authenticated: microsoftValid,
        },
        j2: {
          configured: storeInfo.hasJ2,
          authenticated: j2Valid,
        },
      },
      lastTokenUpdate: storeInfo.updatedAt,
    });
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        service: "work-hub",
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
