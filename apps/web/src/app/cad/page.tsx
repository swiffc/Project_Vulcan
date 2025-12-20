"use client";

import { useState } from "react";
import { Tabs, TabList, TabTrigger, TabContent } from "@/components/ui/Tabs";
import { Sidebar } from "@/components/layout/Sidebar";
import { Projects } from "@/components/cad/Projects";
import { PartsLibrary } from "@/components/cad/PartsLibrary";
import { ECNTracker } from "@/components/cad/ECNTracker";
import { ExportDrive } from "@/components/cad/ExportDrive";

export default function CADPage() {
  const [activeTab, setActiveTab] = useState("projects");

  return (
    <div className="flex h-[calc(100vh-64px)]">
      {/* Main Content */}
      <div className="flex-1 overflow-auto p-4 md:p-6">
        {/* Page Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white">CAD Automation</h1>
            <p className="text-white/50">PDF to SolidWorks Part Generation</p>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-sm text-white/70">SolidWorks Connected</span>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabList>
            <TabTrigger value="projects">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              Projects
            </TabTrigger>
            <TabTrigger value="library">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
              Parts Library
            </TabTrigger>
            <TabTrigger value="ecn">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
              </svg>
              ECN Tracker
            </TabTrigger>
            <TabTrigger value="export">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              Export / Drive
            </TabTrigger>
          </TabList>

          <TabContent value="projects">
            <Projects />
          </TabContent>
          <TabContent value="library">
            <PartsLibrary />
          </TabContent>
          <TabContent value="ecn">
            <ECNTracker />
          </TabContent>
          <TabContent value="export">
            <ExportDrive />
          </TabContent>
        </Tabs>
      </div>

      {/* CAD Chat Sidebar */}
      <Sidebar agentContext="cad" />
    </div>
  );
}
