"use client";

import { useState } from "react";
import type { ValidationResult, ValidationIssue } from "@/app/cad/page";

interface ValidationResultsProps {
  result: ValidationResult | null;
  isValidating: boolean;
  onClear: () => void;
}

const SEVERITY_CONFIG = {
  critical: { color: "text-red-400", bg: "bg-red-500/20", border: "border-red-500/30", icon: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" },
  error: { color: "text-orange-400", bg: "bg-orange-500/20", border: "border-orange-500/30", icon: "M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" },
  warning: { color: "text-amber-400", bg: "bg-amber-500/20", border: "border-amber-500/30", icon: "M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" },
  info: { color: "text-blue-400", bg: "bg-blue-500/20", border: "border-blue-500/30", icon: "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" },
};

export function ValidationResults({ result, isValidating, onClear }: ValidationResultsProps) {
  const [expandedIssue, setExpandedIssue] = useState<string | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<string>("all");

  if (isValidating) {
    return (
      <div className="glass rounded-2xl p-8 h-full flex flex-col items-center justify-center">
        <div className="w-16 h-16 rounded-2xl bg-vulcan-accent/20 flex items-center justify-center mb-4 animate-pulse">
          <svg className="w-8 h-8 text-vulcan-accent animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-white mb-2">Analyzing Drawing</h3>
        <p className="text-white/50 text-center max-w-md">
          Running 130+ validation checks including GD&T, welding symbols, material specs, and dimensional analysis...
        </p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="glass rounded-2xl p-8 h-full flex flex-col items-center justify-center">
        <div className="w-16 h-16 rounded-2xl bg-white/10 flex items-center justify-center mb-4">
          <svg className="w-8 h-8 text-white/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-white mb-2">No Results Yet</h3>
        <p className="text-white/50 text-center max-w-md">
          Upload a drawing and run validation to see detailed results here.
        </p>
        <div className="mt-6 grid grid-cols-2 gap-3 text-center">
          <div className="p-3 rounded-lg bg-white/5">
            <p className="text-2xl font-bold text-vulcan-accent">130+</p>
            <p className="text-xs text-white/40">Validation checks</p>
          </div>
          <div className="p-3 rounded-lg bg-white/5">
            <p className="text-2xl font-bold text-emerald-400">14</p>
            <p className="text-xs text-white/40">GD&T types</p>
          </div>
        </div>
      </div>
    );
  }

  const filteredIssues = filterSeverity === "all"
    ? result.issues
    : result.issues.filter((i) => i.severity === filterSeverity);

  const issueCounts = {
    critical: result.issues.filter((i) => i.severity === "critical").length,
    error: result.issues.filter((i) => i.severity === "error").length,
    warning: result.issues.filter((i) => i.severity === "warning").length,
    info: result.issues.filter((i) => i.severity === "info").length,
  };

  return (
    <div className="glass rounded-2xl overflow-hidden">
      {/* Header */}
      <div className={`p-6 ${
        result.status === "passed" ? "bg-emerald-500/10" :
        result.status === "warnings" ? "bg-amber-500/10" : "bg-red-500/10"
      }`}>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className={`w-14 h-14 rounded-2xl flex items-center justify-center ${
              result.status === "passed" ? "bg-emerald-500/20" :
              result.status === "warnings" ? "bg-amber-500/20" : "bg-red-500/20"
            }`}>
              {result.status === "passed" ? (
                <svg className="w-7 h-7 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              ) : result.status === "warnings" ? (
                <svg className="w-7 h-7 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              ) : (
                <svg className="w-7 h-7 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">{result.filename}</h3>
              <p className="text-white/50 text-sm">
                {result.timestamp.toLocaleString()} • {result.totalChecks} checks completed
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className={`text-3xl font-bold ${
              result.passRate >= 90 ? "text-emerald-400" :
              result.passRate >= 70 ? "text-amber-400" : "text-red-400"
            }`}>
              {result.passRate}%
            </div>
            <p className="text-white/40 text-sm">Pass Rate</p>
          </div>
        </div>

        {/* Category Progress Bars */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
          {result.categories.map((cat) => {
            const pct = Math.round((cat.passed / cat.total) * 100);
            return (
              <div key={cat.name} className="bg-black/20 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-white/70">{cat.name}</span>
                  <span className={`text-sm font-medium ${
                    pct >= 90 ? "text-emerald-400" : pct >= 70 ? "text-amber-400" : "text-red-400"
                  }`}>{pct}%</span>
                </div>
                <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      pct >= 90 ? "bg-emerald-500" : pct >= 70 ? "bg-amber-500" : "bg-red-500"
                    }`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <p className="text-xs text-white/40 mt-1">{cat.passed}/{cat.total} passed</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Filter & Actions */}
      <div className="p-4 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm text-white/50">Filter:</span>
          {["all", "critical", "error", "warning", "info"].map((sev) => (
            <button
              key={sev}
              onClick={() => setFilterSeverity(sev)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                filterSeverity === sev
                  ? "bg-vulcan-accent text-white"
                  : "bg-white/10 text-white/60 hover:bg-white/20"
              }`}
            >
              {sev.charAt(0).toUpperCase() + sev.slice(1)}
              {sev !== "all" && (
                <span className="ml-1 opacity-60">
                  ({issueCounts[sev as keyof typeof issueCounts]})
                </span>
              )}
            </button>
          ))}
        </div>
        <button
          onClick={onClear}
          className="text-sm text-white/50 hover:text-white flex items-center gap-1"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
          Clear
        </button>
      </div>

      {/* Issues List */}
      <div className="max-h-96 overflow-y-auto">
        {filteredIssues.length === 0 ? (
          <div className="p-8 text-center text-white/40">
            No issues found with current filter.
          </div>
        ) : (
          <div className="divide-y divide-white/5">
            {filteredIssues.map((issue) => {
              const config = SEVERITY_CONFIG[issue.severity];
              const isExpanded = expandedIssue === issue.id;

              return (
                <div
                  key={issue.id}
                  className={`p-4 hover:bg-white/5 transition-colors cursor-pointer ${config.bg.replace("/20", "/5")}`}
                  onClick={() => setExpandedIssue(isExpanded ? null : issue.id)}
                >
                  <div className="flex items-start gap-3">
                    <div className={`w-8 h-8 rounded-lg ${config.bg} flex items-center justify-center flex-shrink-0`}>
                      <svg className={`w-4 h-4 ${config.color}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={config.icon} />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className={`text-xs font-medium px-2 py-0.5 rounded ${config.bg} ${config.color}`}>
                          {issue.severity.toUpperCase()}
                        </span>
                        <span className="text-xs text-white/40">{issue.category}</span>
                      </div>
                      <p className="text-sm font-medium text-white mt-1">{issue.title}</p>
                      {isExpanded && (
                        <div className="mt-2 space-y-2">
                          <p className="text-sm text-white/60">{issue.description}</p>
                          {issue.location && (
                            <p className="text-xs text-white/40">
                              <span className="font-medium">Location:</span> {issue.location}
                            </p>
                          )}
                          {issue.standard && (
                            <p className="text-xs text-white/40">
                              <span className="font-medium">Standard:</span> {issue.standard}
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                    <svg
                      className={`w-4 h-4 text-white/30 transition-transform ${isExpanded ? "rotate-180" : ""}`}
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer Actions */}
      <div className="p-4 border-t border-white/10 flex items-center justify-between bg-white/5">
        <button className="flex items-center gap-2 text-sm text-white/60 hover:text-white">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download Report
        </button>
        <button className="flex items-center gap-2 text-sm text-white/60 hover:text-white">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          View Annotated PDF
        </button>
      </div>
    </div>
  );
}
