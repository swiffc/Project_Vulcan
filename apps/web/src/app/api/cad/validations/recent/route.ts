import { NextResponse } from "next/server";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

export async function GET() {
  try {
    const valuations = await prisma.validation.findMany({
      orderBy: { created_at: "desc" },
      take: 10,
    });
    
    // Transform Prisma model to frontend expected ValidationReport format
    const reports = valuations.map(v => ({
      id: v.id,
      jobId: v.job_id,
      status: v.status,
      inputFile: v.file_path,
      timestamp: v.created_at.toISOString(),
      durationMs: v.completed_at ? (v.completed_at.getTime() - v.created_at.getTime()) : 0,
      passRate: (v.metadata as any)?.pass_rate || 0,
      passed: (v.metadata as any)?.passed || 0,
      warnings: (v.metadata as any)?.warnings || 0,
      errors: (v.metadata as any)?.errors || 0,
      criticalFailures: (v.metadata as any)?.critical_failures || 0,
    }));

    return NextResponse.json(reports);
  } catch (error) {
    console.error("Failed to fetch recent validations:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
