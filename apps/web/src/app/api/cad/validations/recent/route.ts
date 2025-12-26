import { NextResponse } from "next/server";

// Mock data for when database is not available
const mockRecentValidations = [
  {
    id: "val-001",
    jobId: "job-001",
    status: "complete",
    inputFile: "ACHE-UNIT-001.pdf",
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    durationMs: 2100,
    passRate: 92.3,
    passed: 196,
    warnings: 12,
    errors: 5,
    criticalFailures: 0,
  },
  {
    id: "val-002",
    jobId: "job-002",
    status: "complete",
    inputFile: "HEADER-BOX-A12.pdf",
    timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    durationMs: 1890,
    passRate: 88.7,
    passed: 184,
    warnings: 18,
    errors: 8,
    criticalFailures: 1,
  },
  {
    id: "val-003",
    jobId: "job-003",
    status: "complete",
    inputFile: "FAN-ASSEMBLY-03.pdf",
    timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
    durationMs: 3200,
    passRate: 78.2,
    passed: 162,
    warnings: 25,
    errors: 18,
    criticalFailures: 3,
  },
  {
    id: "val-004",
    jobId: "job-004",
    status: "complete",
    inputFile: "WALKWAY-SECT-B.pdf",
    timestamp: new Date(Date.now() - 1000 * 60 * 180).toISOString(),
    durationMs: 1560,
    passRate: 95.1,
    passed: 201,
    warnings: 8,
    errors: 2,
    criticalFailures: 0,
  },
  {
    id: "val-005",
    jobId: "job-005",
    status: "complete",
    inputFile: "TUBE-BUNDLE-07.pdf",
    timestamp: new Date(Date.now() - 1000 * 60 * 240).toISOString(),
    durationMs: 2780,
    passRate: 84.6,
    passed: 175,
    warnings: 20,
    errors: 12,
    criticalFailures: 1,
  },
];

export async function GET() {
  // Check if DATABASE_URL is configured
  if (!process.env.DATABASE_URL) {
    // Return mock data for development/demo
    return NextResponse.json(mockRecentValidations);
  }

  try {
    // Dynamic import to avoid initialization errors
    const { PrismaClient } = await import("@prisma/client");
    const prisma = new PrismaClient();

    const validations = await prisma.validation.findMany({
      orderBy: { created_at: "desc" },
      take: 10,
    });

    await prisma.$disconnect();

    // Transform Prisma model to frontend expected ValidationReport format
    const reports = validations.map((v) => ({
      id: v.id,
      jobId: v.job_id,
      status: v.status,
      inputFile: v.file_path,
      timestamp: v.created_at.toISOString(),
      durationMs: v.completed_at
        ? v.completed_at.getTime() - v.created_at.getTime()
        : 0,
      passRate: (v.metadata as Record<string, unknown>)?.pass_rate || 0,
      passed: (v.metadata as Record<string, unknown>)?.passed || 0,
      warnings: (v.metadata as Record<string, unknown>)?.warnings || 0,
      errors: (v.metadata as Record<string, unknown>)?.errors || 0,
      criticalFailures:
        (v.metadata as Record<string, unknown>)?.critical_failures || 0,
    }));

    return NextResponse.json(reports);
  } catch (error) {
    console.error("Failed to fetch recent validations:", error);
    // Return mock data on error
    return NextResponse.json(mockRecentValidations);
  }
}
