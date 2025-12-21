"use client";

import { Card, CardHeader, CardContent } from "../ui/Card";
import { Badge } from "../ui/Badge";

interface ActiveJob {
  id: string;
  unitTag: string;
  customer: string;
  type: string;
  duty: string;
  progress: number;
  dueDate: string;
  status: "design" | "review" | "fabrication" | "shipped";
}

const activeJobs: ActiveJob[] = [
  { id: "1", unitTag: "E-4501 A/B", customer: "ExxonMobil", type: "ACHE", duty: "45.2 MMBtu/hr", progress: 75, dueDate: "Jan 15", status: "review" },
  { id: "2", unitTag: "E-2201", customer: "Chevron", type: "ACHE", duty: "28.7 MMBtu/hr", progress: 45, dueDate: "Jan 22", status: "design" },
  { id: "3", unitTag: "AC-101 A/B/C", customer: "Saudi Aramco", type: "ACHE", duty: "112.0 MMBtu/hr", progress: 90, dueDate: "Jan 8", status: "fabrication" },
];

const statusColors = {
  design: "warning",
  review: "info",
  fabrication: "success",
  shipped: "default",
} as const;

export function Dashboard() {
  return (
    <div className="space-y-6 mt-4">
      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <div>
                <p className="text-2xl font-bold text-white">12</p>
                <p className="text-xs text-white/50">Active Units</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
                <svg className="w-5 h-5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-2xl font-bold text-white">3</p>
                <p className="text-xs text-white/50">Due This Week</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                <svg className="w-5 h-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-2xl font-bold text-white">28</p>
                <p className="text-xs text-white/50">YTD Shipped</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                <svg className="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <div>
                <p className="text-2xl font-bold text-white">5</p>
                <p className="text-xs text-white/50">Pending ECNs</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Active Jobs */}
        <Card className="lg:col-span-2">
          <CardHeader
            title="Active ACHE Units"
            subtitle="Current projects in progress"
            action={
              <Badge variant="info">{activeJobs.length} units</Badge>
            }
          />
          <CardContent>
            <div className="space-y-3">
              {activeJobs.map((job) => (
                <div key={job.id} className="p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-mono font-bold text-white">{job.unitTag}</h3>
                        <Badge variant={statusColors[job.status]} size="sm">{job.status}</Badge>
                      </div>
                      <p className="text-sm text-white/50">{job.customer}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-vulcan-accent">{job.duty}</p>
                      <p className="text-xs text-white/40">Due: {job.dueDate}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-vulcan-accent to-blue-500 rounded-full transition-all"
                        style={{ width: `${job.progress}%` }}
                      />
                    </div>
                    <span className="text-xs text-white/50 w-10">{job.progress}%</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions & Standards */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <Card>
            <CardHeader title="Quick Actions" />
            <CardContent className="space-y-2">
              <button className="w-full flex items-center gap-3 p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-left">
                <div className="w-8 h-8 rounded-lg bg-vulcan-accent/20 flex items-center justify-center">
                  <svg className="w-4 h-4 text-vulcan-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium text-white">New ACHE Unit</p>
                  <p className="text-xs text-white/40">Start from template</p>
                </div>
              </button>
              <button className="w-full flex items-center gap-3 p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-left">
                <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
                  <svg className="w-4 h-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium text-white">Import HTRI</p>
                  <p className="text-xs text-white/40">Load thermal data</p>
                </div>
              </button>
              <button className="w-full flex items-center gap-3 p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-left">
                <div className="w-8 h-8 rounded-lg bg-green-500/20 flex items-center justify-center">
                  <svg className="w-4 h-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium text-white">Generate BOM</p>
                  <p className="text-xs text-white/40">Bill of materials</p>
                </div>
              </button>
            </CardContent>
          </Card>

          {/* Standards Compliance */}
          <Card>
            <CardHeader title="Standards Compliance" subtitle="Active certifications" />
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between p-2 bg-green-500/10 rounded-lg border border-green-500/20">
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-sm text-white">API 661</span>
                </div>
                <span className="text-xs text-green-400">Compliant</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-green-500/10 rounded-lg border border-green-500/20">
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-sm text-white">ASME VIII</span>
                </div>
                <span className="text-xs text-green-400">Certified</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-green-500/10 rounded-lg border border-green-500/20">
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-sm text-white">PED 2014/68/EU</span>
                </div>
                <span className="text-xs text-green-400">Category IV</span>
              </div>
              <div className="flex items-center justify-between p-2 bg-amber-500/10 rounded-lg border border-amber-500/20">
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm text-white">TEMA R</span>
                </div>
                <span className="text-xs text-amber-400">Renewal Due</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
