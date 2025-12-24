"use client";

import { useEffect, useState } from "react";
import { formatDistanceToNow } from "date-fns";

interface ValidationRecord {
  id: string;
  filename: string;
  timestamp: Date;
  status: "passed" | "failed" | "warnings";
  passRate: number;
  checksRun: number;
  issueCount: number;
  type: string;
}

export function RecentValidations() {
  const [validations, setValidations] = useState<ValidationRecord[]>([]);
  const [filter, setFilter] = useState<"all" | "passed" | "failed" | "warnings">("all");
  const [sortBy, setSortBy] = useState<"date" | "passRate">("date");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Fetch from API
    const fetchValidations = async () => {
      try {
        const res = await fetch("/api/cad/validations/recent");
        if (res.ok) {
          const data = await res.json();

          // Handle both array response and object with validations property
          const records = Array.isArray(data) ? data : (data.validations || []);

          if (records.length > 0) {
            setValidations(records.map((v: any) => ({
              id: v.id || `val-${Date.now()}-${Math.random()}`,
              filename: v.inputFile || v.file_path || v.filename || "Unknown file",
              timestamp: new Date(v.timestamp || v.created_at || Date.now()),
              status: v.passRate >= 90 ? "passed" : v.passRate >= 70 ? "warnings" : "failed",
              passRate: v.passRate || v.pass_rate || 0,
              checksRun: v.totalChecks || v.checks_run || 130,
              issueCount: (v.warnings || 0) + (v.errors || 0) + (v.criticalFailures || 0),
              type: v.type || v.validationType || "Drawing",
            })));
          } else {
            setValidations([]);
          }
        } else {
          setValidations([]);
        }
      } catch {
        setValidations([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchValidations();

    // Refresh every 30 seconds
    const interval = setInterval(fetchValidations, 30000);
    return () => clearInterval(interval);
  }, []);

  const filteredValidations = validations
    .filter((v) => filter === "all" || v.status === filter)
    .sort((a, b) => {
      if (sortBy === "date") {
        return b.timestamp.getTime() - a.timestamp.getTime();
      }
      return b.passRate - a.passRate;
    });

  const stats = {
    total: validations.length,
    passed: validations.filter((v) => v.status === "passed").length,
    warnings: validations.filter((v) => v.status === "warnings").length,
    failed: validations.filter((v) => v.status === "failed").length,
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="glass rounded-xl p-4 animate-pulse">
              <div className="h-4 w-24 bg-white/10 rounded mb-2" />
              <div className="h-8 w-12 bg-white/10 rounded" />
            </div>
          ))}
        </div>
        <div className="glass rounded-2xl p-8 text-center">
          <div className="w-8 h-8 mx-auto border-2 border-vulcan-accent border-t-transparent rounded-full animate-spin" />
          <p className="text-white/50 mt-4">Loading validation history...</p>
        </div>
      </div>
    );
  }

  if (validations.length === 0) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-4 gap-4">
          <div className="glass rounded-xl p-4">
            <p className="text-sm text-white/50">Total Validations</p>
            <p className="text-2xl font-bold text-white">0</p>
          </div>
          <div className="glass rounded-xl p-4 border-l-2 border-emerald-500">
            <p className="text-sm text-white/50">Passed</p>
            <p className="text-2xl font-bold text-emerald-400">0</p>
          </div>
          <div className="glass rounded-xl p-4 border-l-2 border-amber-500">
            <p className="text-sm text-white/50">Warnings</p>
            <p className="text-2xl font-bold text-amber-400">0</p>
          </div>
          <div className="glass rounded-xl p-4 border-l-2 border-red-500">
            <p className="text-sm text-white/50">Failed</p>
            <p className="text-2xl font-bold text-red-400">0</p>
          </div>
        </div>
        <div className="glass rounded-2xl p-12 text-center">
          <svg className="w-16 h-16 mx-auto text-white/20 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="text-lg font-medium text-white mb-2">No Validations Yet</h3>
          <p className="text-white/50 max-w-md mx-auto">
            Upload a CAD drawing or PDF and run validation to see your history here.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4">
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-white/50">Total Validations</p>
          <p className="text-2xl font-bold text-white">{stats.total}</p>
        </div>
        <div className="glass rounded-xl p-4 border-l-2 border-emerald-500">
          <p className="text-sm text-white/50">Passed</p>
          <p className="text-2xl font-bold text-emerald-400">{stats.passed}</p>
        </div>
        <div className="glass rounded-xl p-4 border-l-2 border-amber-500">
          <p className="text-sm text-white/50">Warnings</p>
          <p className="text-2xl font-bold text-amber-400">{stats.warnings}</p>
        </div>
        <div className="glass rounded-xl p-4 border-l-2 border-red-500">
          <p className="text-sm text-white/50">Failed</p>
          <p className="text-2xl font-bold text-red-400">{stats.failed}</p>
        </div>
      </div>

      {/* Filter & Sort */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {(["all", "passed", "warnings", "failed"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                filter === f
                  ? "bg-vulcan-accent text-white"
                  : "bg-white/10 text-white/60 hover:bg-white/20"
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as "date" | "passRate")}
          className="bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-sm text-white"
        >
          <option value="date">Sort by Date</option>
          <option value="passRate">Sort by Pass Rate</option>
        </select>
      </div>

      {/* Validations Table */}
      <div className="glass rounded-2xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/10">
              <th className="text-left p-4 text-sm font-medium text-white/50">File</th>
              <th className="text-left p-4 text-sm font-medium text-white/50">Type</th>
              <th className="text-left p-4 text-sm font-medium text-white/50">Status</th>
              <th className="text-left p-4 text-sm font-medium text-white/50">Pass Rate</th>
              <th className="text-left p-4 text-sm font-medium text-white/50">Issues</th>
              <th className="text-left p-4 text-sm font-medium text-white/50">Date</th>
              <th className="text-right p-4 text-sm font-medium text-white/50">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredValidations.map((validation) => (
              <tr
                key={validation.id}
                className="border-b border-white/5 hover:bg-white/5 transition-colors"
              >
                <td className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                      <svg className="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">{validation.filename}</p>
                      <p className="text-xs text-white/40">{validation.checksRun} checks</p>
                    </div>
                  </div>
                </td>
                <td className="p-4">
                  <span className="px-2 py-1 rounded text-xs bg-white/10 text-white/60">
                    {validation.type}
                  </span>
                </td>
                <td className="p-4">
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      validation.status === "passed"
                        ? "bg-emerald-500/20 text-emerald-400"
                        : validation.status === "warnings"
                        ? "bg-amber-500/20 text-amber-400"
                        : "bg-red-500/20 text-red-400"
                    }`}
                  >
                    {validation.status.charAt(0).toUpperCase() + validation.status.slice(1)}
                  </span>
                </td>
                <td className="p-4">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-2 bg-white/10 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          validation.passRate >= 90
                            ? "bg-emerald-500"
                            : validation.passRate >= 70
                            ? "bg-amber-500"
                            : "bg-red-500"
                        }`}
                        style={{ width: `${validation.passRate}%` }}
                      />
                    </div>
                    <span className="text-sm text-white/70">{validation.passRate}%</span>
                  </div>
                </td>
                <td className="p-4">
                  <span className={`text-sm ${validation.issueCount > 0 ? "text-amber-400" : "text-white/40"}`}>
                    {validation.issueCount}
                  </span>
                </td>
                <td className="p-4">
                  <span className="text-sm text-white/50">
                    {formatDistanceToNow(validation.timestamp, { addSuffix: true })}
                  </span>
                </td>
                <td className="p-4 text-right">
                  <button className="p-2 rounded-lg hover:bg-white/10 text-white/50 hover:text-white transition-colors">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
