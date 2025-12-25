/**
 * CAD Validation API Route
 * 
 * Proxies validation requests to the desktop server.
 */

import { NextRequest, NextResponse } from "next/server";

const DESKTOP_SERVER_URL = process.env.DESKTOP_SERVER_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    
    const file = formData.get("file") as File | null;
    const fileId = formData.get("fileId") as string | null;
    const checks = formData.get("checks") as string || '["all"]';
    const severity = formData.get("severity") as string || "all";
    const userId = formData.get("userId") as string || "anonymous";
    const projectId = formData.get("projectId") as string | null;
    const validationType = formData.get("type") as string || "drawing";
    
    // Create form data for desktop server
    const desktopFormData = new FormData();
    
    if (file) {
      desktopFormData.append("file", file);
    }
    
    if (fileId) {
      desktopFormData.append("file_id", fileId);
    }
    
    desktopFormData.append("checks", checks);
    desktopFormData.append("severity", severity);
    desktopFormData.append("user_id", userId);
    
    if (projectId) {
      desktopFormData.append("project_id", projectId);
    }
    
    // Determine endpoint
    const endpoint = validationType === "ache" 
      ? "/cad/validate/ache"
      : "/cad/validate/drawing";
    
    // Forward to desktop server
    const response = await fetch(`${DESKTOP_SERVER_URL}${endpoint}`, {
      method: "POST",
      body: desktopFormData,
    });
    
    if (!response.ok) {
      const error = await response.text();
      return NextResponse.json(
        { error: `Validation failed: ${error}` },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error("Validation API error:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Validation failed" },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    // Get validation system status
    const response = await fetch(`${DESKTOP_SERVER_URL}/cad/validate/status`);
    
    if (!response.ok) {
      return NextResponse.json(
        { available: false, error: "Desktop server not reachable" },
        { status: 503 }
      );
    }
    
    const data = await response.json();
    
    return NextResponse.json(data);
    
  } catch (error) {
    console.error("Validation status error:", error);
    return NextResponse.json(
      { available: false, error: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}
