"use client";

import { Clock, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

export default function JobQueueWidget() {
  const jobs = [
    { id: "JOB-001", name: "Export Flange Assembly", status: "running", progress: 75 },
    { id: "JOB-002", name: "BOM Cross Check", status: "queued", progress: 0 },
    { id: "JOB-003", name: "PDF Generation", status: "running", progress: 45 },
    { id: "JOB-004", name: "STEP Export", status: "queued", progress: 0 },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "running":
        return <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />;
      case "queued":
        return <Clock className="w-4 h-4 text-yellow-400" />;
      case "completed":
        return <CheckCircle className="w-4 h-4 text-emerald-400" />;
      default:
        return <AlertCircle className="w-4 h-4 text-red-400" />;
    }
  };

  return (
    <div className="glass-base p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white">Active Jobs</h2>
        <span className="px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-400 text-sm font-medium">
          {jobs.filter((j) => j.status === "running").length} Running
        </span>
      </div>

      <div className="space-y-3">
        {jobs.map((job) => (
          <div key={job.id} className="p-3 rounded-lg bg-white/5">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                {getStatusIcon(job.status)}
                <div>
                  <p className="text-white font-medium text-sm">{job.name}</p>
                  <p className="text-gray-400 text-xs">{job.id}</p>
                </div>
              </div>
              {job.status === "running" && (
                <span className="text-sm text-gray-400">{job.progress}%</span>
              )}
            </div>

            {job.status === "running" && (
              <div className="w-full bg-gray-700 rounded-full h-1.5">
                <div
                  className="bg-gradient-to-r from-indigo-500 to-purple-600 h-1.5 rounded-full transition-all duration-500"
                  style={{ width: `${job.progress}%` }}
                />
              </div>
            )}
          </div>
        ))}
      </div>

      <button className="w-full mt-4 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-white text-sm font-medium transition-colors">
        View All Jobs
      </button>
    </div>
  );
}
