"use client";

import { useState, useCallback } from "react";
import { ValidationUploader } from "@/components/cad/ValidationUploader";
import { ValidationResults } from "@/components/cad/ValidationResults";
import { CADStatusBar } from "@/components/cad/CADStatusBar";
import { QuickStats } from "@/components/cad/QuickStats";
import { RecentValidations } from "@/components/cad/RecentValidations";
import { ToolsPanel } from "@/components/cad/ToolsPanel";
import { ModelOverview } from "@/components/cad/ModelOverview";
import { Sidebar } from "@/components/layout/Sidebar";

export interface ValidationResult {
  id: string;
  filename: string;
  timestamp: Date;
  status: "passed" | "failed" | "warnings";
  passRate: number;
  totalChecks: number;
  issues: ValidationIssue[];
  categories: CategoryResult[];
}

export interface ValidationIssue {
  id: string;
  severity: "critical" | "error" | "warning" | "info";
  category: string;
  title: string;
  description: string;
  location?: string;
  standard?: string;
}

export interface CategoryResult {
  name: string;
  passed: number;
  failed: number;
  total: number;
}

export default function CADPage() {
  const [activeView, setActiveView] = useState<"overview" | "validate" | "tools" | "history">("overview");
  const [currentValidation, setCurrentValidation] = useState<ValidationResult | null>(null);
  const [isValidating, setIsValidating] = useState(false);

  const handleValidationComplete = useCallback((result: ValidationResult) => {
    setCurrentValidation(result);
    setIsValidating(false);
  }, []);

  const handleValidationStart = useCallback(() => {
    setIsValidating(true);
    setCurrentValidation(null);
  }, []);

  const handleClearResults = useCallback(() => {
    setCurrentValidation(null);
  }, []);

  return (
    <div className="flex h-[calc(100vh-64px)]">
      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Status Bar */}
        <CADStatusBar />

        {/* View Tabs */}
        <div className="border-b border-white/10 px-6">
          <div className="flex gap-1">
            {[
              { id: "overview", label: "Model Overview", icon: "M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" },
              { id: "validate", label: "Validate Drawing", icon: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" },
              { id: "tools", label: "CAD Tools", icon: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z" },
              { id: "history", label: "History", icon: "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveView(tab.id as typeof activeView)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-all border-b-2 -mb-px ${
                  activeView === tab.id
                    ? "text-white border-vulcan-accent"
                    : "text-white/50 border-transparent hover:text-white/80"
                }`}
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={tab.icon} />
                </svg>
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-auto p-6">
          {activeView === "validate" && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left: Upload & Stats */}
              <div className="lg:col-span-1 space-y-6">
                <ValidationUploader
                  onValidationStart={handleValidationStart}
                  onValidationComplete={handleValidationComplete}
                  isValidating={isValidating}
                />
                <QuickStats />
              </div>

              {/* Right: Results */}
              <div className="lg:col-span-2">
                <ValidationResults
                  result={currentValidation}
                  isValidating={isValidating}
                  onClear={handleClearResults}
                />
              </div>
            </div>
          )}

          {activeView === "tools" && <ToolsPanel />}

          {activeView === "history" && <RecentValidations />}
        </div>
      </div>

      {/* AI Assistant Sidebar */}
      <div className="border-l border-white/10 h-full">
        <Sidebar agentContext="cad" defaultCollapsed={false} />
      </div>
    </div>
  );
}
