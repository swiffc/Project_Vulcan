/**
 * Full Scope CAD API Endpoint
 * 
 * This endpoint provides access to the complete range of CAD operations
 * for both SolidWorks and Inventor, including parts, assemblies, and drawings.
 */

import { NextRequest, NextResponse } from "next/server";
import { executeCADTool, CAD_TOOLS } from "@/lib/cad-tools";

/**
 * Execute a CAD operation
 * Body: { tool: string, input: any }
 */
export async function POST(request: NextRequest) {
  try {
    const { tool, input } = await request.json();

    if (!tool) {
      return NextResponse.json({ error: "Missing tool name" }, { status: 400 });
    }

    console.log(`[CAD API] Executing action: ${tool}`);
    const result = await executeCADTool(tool, input || {});

    if (!result.success) {
      return NextResponse.json(result, { status: 400 });
    }

    return NextResponse.json(result);

  } catch (error) {
    console.error("[CAD API] Error:", error);
    return NextResponse.json(
      { success: false, error: error instanceof Error ? error.message : "Internal server error" },
      { status: 500 }
    );
  }
}

/**
 * Get available CAD tools and current system status
 */
export async function GET() {
  try {
    // Return the list of available tools to the client
    return NextResponse.json({
      success: true,
      tools: CAD_TOOLS.map(t => ({
        name: t.name,
        description: t.description,
        schema: t.input_schema
      })),
      systems: ["SolidWorks", "Inventor"]
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: "Failed to fetch CAD tool definitions" },
      { status: 500 }
    );
  }
}
