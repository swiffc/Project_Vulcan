import { NextRequest, NextResponse } from "next/server";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const trade = await prisma.trade.findUnique({
      where: { id: params.id },
    });
    if (!trade) {
      return NextResponse.json({ error: "Trade not found" }, { status: 404 });
    }
    return NextResponse.json(trade);
  } catch (error) {
    console.error("Failed to fetch trade:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json();
    const trade = await prisma.trade.update({
      where: { id: params.id },
      data: {
        symbol: body.pair || body.symbol,
        direction: body.direction,
        entry_price: body.entryPrice || body.entry_price,
        exit_price: body.exitPrice || body.exit_price,
        quantity: body.positionSize || body.quantity,
        notes: body.notes,
        setup: body.setupType || body.setup,
        result: body.result,
      },
    });
    return NextResponse.json(trade);
  } catch (error) {
    console.error("Failed to update trade:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    await prisma.trade.delete({
      where: { id: params.id },
    });
    return new NextResponse(null, { status: 204 });
  } catch (error) {
    console.error("Failed to delete trade:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
