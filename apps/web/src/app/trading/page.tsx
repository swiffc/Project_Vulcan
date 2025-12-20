"use client";

import { useState } from "react";
import { Tabs, TabList, TabTrigger, TabContent } from "@/components/ui/Tabs";
import { Sidebar } from "@/components/layout/Sidebar";
import { MarketAnalysis } from "@/components/trading/MarketAnalysis";
import { TradeJournal } from "@/components/trading/TradeJournal";
import { Performance } from "@/components/trading/Performance";
import { Watchlist } from "@/components/trading/Watchlist";
import { SessionClock } from "@/components/trading/SessionClock";

export default function TradingPage() {
  const [activeTab, setActiveTab] = useState("analysis");

  return (
    <div className="flex h-[calc(100vh-64px)]">
      {/* Main Content */}
      <div className="flex-1 overflow-auto p-4 md:p-6">
        {/* Page Header with Session Clock */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white">Trading Terminal</h1>
            <p className="text-white/50">ICT/BTMM Market Analysis & Journal</p>
          </div>
          <SessionClock />
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabList>
            <TabTrigger value="analysis">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              Market Analysis
            </TabTrigger>
            <TabTrigger value="journal">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              Trade Journal
            </TabTrigger>
            <TabTrigger value="performance">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Performance
            </TabTrigger>
            <TabTrigger value="watchlist">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              Watchlist
            </TabTrigger>
          </TabList>

          <TabContent value="analysis">
            <MarketAnalysis />
          </TabContent>
          <TabContent value="journal">
            <TradeJournal />
          </TabContent>
          <TabContent value="performance">
            <Performance />
          </TabContent>
          <TabContent value="watchlist">
            <Watchlist />
          </TabContent>
        </Tabs>
      </div>

      {/* Trading Chat Sidebar */}
      <Sidebar agentContext="trading" />
    </div>
  );
}
