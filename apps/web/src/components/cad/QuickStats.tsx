"use client";

import { useEffect, useState } from "react";

interface Stats {
  todayValidations: number;
  passRate: number;
  issuesFound: number;
  toolsUsed: number;
  hasData: boolean;
}

export function QuickStats() {
  const [stats, setStats] = useState<Stats>({
    todayValidations: 0,
    passRate: 0,
    issuesFound: 0,
    toolsUsed: 0,
    hasData: false,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Fetch stats from API
    const fetchStats = async () => {
      try {
        const res = await fetch("/api/cad/validations/recent");
        if (res.ok) {
          const data = await res.json();

          // Handle both array response and object with validations property
          const records = Array.isArray(data) ? data : (data.validations || []);

          if (records.length > 0) {
            // Calculate stats from records
            const today = new Date();
            today.setHours(0, 0, 0, 0);

            const todayRecords = records.filter((v: any) => {
              const vDate = new Date(v.timestamp || v.created_at);
              return vDate >= today;
            });

            const totalPassRate = records.reduce((sum: number, v: any) =>
              sum + (v.passRate || v.pass_rate || 0), 0);
            const avgPassRate = records.length > 0 ? Math.round(totalPassRate / records.length) : 0;

            const totalIssues = records.reduce((sum: number, v: any) =>
              sum + (v.warnings || 0) + (v.errors || 0) + (v.criticalFailures || 0), 0);

            setStats({
              todayValidations: todayRecords.length,
              passRate: avgPassRate,
              issuesFound: totalIssues,
              toolsUsed: data.toolsUsed || 0,
              hasData: true,
            });
          } else {
            // No records in database
            setStats({
              todayValidations: 0,
              passRate: 0,
              issuesFound: 0,
              toolsUsed: 0,
              hasData: false,
            });
          }
        } else {
          // API error
          setStats({
            todayValidations: 0,
            passRate: 0,
            issuesFound: 0,
            toolsUsed: 0,
            hasData: false,
          });
        }
      } catch {
        setStats({
          todayValidations: 0,
          passRate: 0,
          issuesFound: 0,
          toolsUsed: 0,
          hasData: false,
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();

    // Refresh every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const statItems = [
    {
      label: "Today",
      value: stats.todayValidations,
      suffix: "validations",
      color: "text-vulcan-accent",
      icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2",
    },
    {
      label: "Avg Pass Rate",
      value: stats.passRate,
      suffix: "%",
      color: stats.passRate >= 85 ? "text-emerald-400" : "text-amber-400",
      icon: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",
    },
    {
      label: "Issues Found",
      value: stats.issuesFound,
      suffix: "total",
      color: "text-amber-400",
      icon: "M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
    },
    {
      label: "Tools Used",
      value: stats.toolsUsed,
      suffix: "today",
      color: "text-blue-400",
      icon: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z",
    },
  ];

  if (isLoading) {
    return (
      <div className="glass rounded-2xl p-4">
        <h3 className="text-sm font-medium text-white/60 mb-3">Quick Stats</h3>
        <div className="grid grid-cols-2 gap-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="p-3 rounded-xl bg-white/5 border border-white/10 animate-pulse">
              <div className="h-4 w-16 bg-white/10 rounded mb-2" />
              <div className="h-6 w-12 bg-white/10 rounded" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!stats.hasData) {
    return (
      <div className="glass rounded-2xl p-4">
        <h3 className="text-sm font-medium text-white/60 mb-3">Quick Stats</h3>
        <div className="text-center py-4">
          <svg className="w-8 h-8 mx-auto text-white/20 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-white/40 text-sm">No validation data yet</p>
          <p className="text-white/30 text-xs mt-1">Run a validation to see stats</p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass rounded-2xl p-4">
      <h3 className="text-sm font-medium text-white/60 mb-3">Quick Stats</h3>
      <div className="grid grid-cols-2 gap-3">
        {statItems.map((item) => (
          <div
            key={item.label}
            className="p-3 rounded-xl bg-white/5 border border-white/10"
          >
            <div className="flex items-center gap-2 mb-1">
              <svg className={`w-4 h-4 ${item.color}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
              </svg>
              <span className="text-xs text-white/50">{item.label}</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className={`text-xl font-bold ${item.color}`}>{item.value}</span>
              <span className="text-xs text-white/30">{item.suffix}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
