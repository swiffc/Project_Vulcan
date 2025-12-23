import { NextRequest, NextResponse } from "next/server";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

export async function GET() {
  try {
    const trades = await prisma.trade.findMany({
      orderBy: { created_at: "desc" },
    });
    return NextResponse.json(trades);
  } catch (error) {
    console.error("Failed to fetch trades:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const trade = await prisma.trade.create({
      data: {
        symbol: body.pair || body.symbol,
        direction: body.direction,
        entry_price: body.entryPrice || body.entry_price,
        exit_price: body.exitPrice || body.exit_price,
        quantity: body.positionSize || body.quantity || 1,
        notes: body.preTradeNotes || body.notes,
        setup: body.setupType || body.setup,
        bias: body.direction === "long" ? "bullish" : "bearish",
        target: body.takeProfit1 || body.target,
        stop: body.stopLoss || body.stop,
        result: body.result,
      },
    });
    return NextResponse.json(trade, { status: 201 });
  } catch (error) {
    console.error("Failed to create trade:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
