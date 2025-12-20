"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge, StatusDot } from "@/components/ui/Badge";

interface ServiceStatus {
  service: string;
  configured: boolean;
  authenticated: boolean;
}

interface WorkHealthResponse {
  status: string;
  services: {
    microsoft: ServiceStatus;
    j2: ServiceStatus;
  };
  lastTokenUpdate: string;
}

export default function WorkPage() {
  const [workStatus, setWorkStatus] = useState<WorkHealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  const checkWorkHealth = async () => {
    try {
      const res = await fetch("/api/work/health");
      if (res.ok) {
        const data = await res.json();
        setWorkStatus(data);
      }
    } catch (error) {
      console.error("Failed to check work health:", error);
    } finally {
      setLoading(false);
      setLastRefresh(new Date());
    }
  };

  useEffect(() => {
    checkWorkHealth();
    const interval = setInterval(checkWorkHealth, 60000); // Check every minute
    return () => clearInterval(interval);
  }, []);

  const isServiceConnected = (service: ServiceStatus | undefined) => {
    return service?.configured && service?.authenticated;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Work Hub</h1>
          <p className="text-white/50">All your work info in one place</p>
        </div>
        <div className="flex items-center gap-4">
          {/* Connection Status */}
          <div className="flex items-center gap-2">
            <StatusDot
              status={
                workStatus?.services.microsoft.authenticated
                  ? "online"
                  : workStatus?.services.microsoft.configured
                    ? "offline"
                    : "checking"
              }
            />
            <span className="text-sm text-white/50">
              {workStatus?.services.microsoft.authenticated
                ? "Microsoft Connected"
                : "Microsoft Disconnected"}
            </span>
          </div>

          {/* Last Refresh */}
          <span className="text-xs text-white/30">
            {lastRefresh ? `Updated ${lastRefresh.toLocaleTimeString()}` : "Loading..."}
          </span>

          {/* Refresh Button */}
          <Button variant="secondary" size="sm" onClick={checkWorkHealth}>
            <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </Button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Email Widget */}
        <Card>
          <CardHeader
            title="Emails"
            subtitle="Microsoft Outlook"
            action={
              <Badge variant={isServiceConnected(workStatus?.services.microsoft) ? "success" : "warning"}>
                {isServiceConnected(workStatus?.services.microsoft) ? "Connected" : "Not Connected"}
              </Badge>
            }
          />
          <CardContent>
            {!isServiceConnected(workStatus?.services.microsoft) ? (
              <div className="text-center py-8">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-blue-500/10 flex items-center justify-center">
                  <svg className="w-8 h-8 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <p className="text-white/50 mb-4">Connect your Microsoft account to view emails</p>
                <Button variant="primary">
                  <svg className="w-4 h-4 mr-2" viewBox="0 0 21 21" fill="currentColor">
                    <path d="M0 0h10v10H0V0zm11 0h10v10H11V0zM0 11h10v10H0V11zm11 0h10v10H11V11z"/>
                  </svg>
                  Connect Microsoft
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white/50">Unread</span>
                  <Badge variant="info">0</Badge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white/50">Important</span>
                  <Badge variant="warning">0</Badge>
                </div>
                <div className="border-t border-white/10 pt-3 mt-3">
                  <p className="text-white/30 text-sm text-center">No emails to display</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Teams Widget */}
        <Card>
          <CardHeader
            title="Teams"
            subtitle="Messages & Mentions"
            action={
              <Badge variant={isServiceConnected(workStatus?.services.microsoft) ? "success" : "warning"}>
                {isServiceConnected(workStatus?.services.microsoft) ? "Connected" : "Not Connected"}
              </Badge>
            }
          />
          <CardContent>
            {!isServiceConnected(workStatus?.services.microsoft) ? (
              <div className="text-center py-8">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-purple-500/10 flex items-center justify-center">
                  <svg className="w-8 h-8 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
                  </svg>
                </div>
                <p className="text-white/50 mb-4">Connect Microsoft to view Teams messages</p>
                <Button variant="ghost" disabled>Uses same Microsoft connection</Button>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white/50">Mentions</span>
                  <Badge variant="error">0</Badge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white/50">Unread Chats</span>
                  <Badge variant="info">0</Badge>
                </div>
                <div className="border-t border-white/10 pt-3 mt-3">
                  <p className="text-white/30 text-sm text-center">No messages to display</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Files Widget */}
        <Card>
          <CardHeader
            title="Files"
            subtitle="SharePoint & OneDrive"
            action={
              <Badge variant={isServiceConnected(workStatus?.services.microsoft) ? "success" : "warning"}>
                {isServiceConnected(workStatus?.services.microsoft) ? "Connected" : "Not Connected"}
              </Badge>
            }
          />
          <CardContent>
            {!isServiceConnected(workStatus?.services.microsoft) ? (
              <div className="text-center py-8">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-green-500/10 flex items-center justify-center">
                  <svg className="w-8 h-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                  </svg>
                </div>
                <p className="text-white/50 mb-4">Connect Microsoft to browse files</p>
                <Button variant="ghost" disabled>Uses same Microsoft connection</Button>
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-white/30 text-sm text-center py-4">No recent files</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* J2 Tracker Widget */}
        <Card>
          <CardHeader
            title="J2 Tracker"
            subtitle="Jobs & Workflows"
            action={
              <Badge variant={isServiceConnected(workStatus?.services.j2) ? "success" : "warning"}>
                {isServiceConnected(workStatus?.services.j2) ? "Connected" : "Not Connected"}
              </Badge>
            }
          />
          <CardContent>
            {!isServiceConnected(workStatus?.services.j2) ? (
              <div className="text-center py-8">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-amber-500/10 flex items-center justify-center">
                  <svg className="w-8 h-8 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                  </svg>
                </div>
                <p className="text-white/50 mb-4">Connect J2 Tracker to view jobs</p>
                <Button variant="primary">
                  <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                  Connect J2 Tracker
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="grid grid-cols-3 gap-2">
                  <div className="text-center p-2 rounded-lg bg-white/5">
                    <p className="text-2xl font-bold text-white">0</p>
                    <p className="text-xs text-white/50">Active</p>
                  </div>
                  <div className="text-center p-2 rounded-lg bg-red-500/10">
                    <p className="text-2xl font-bold text-red-400">0</p>
                    <p className="text-xs text-white/50">Overdue</p>
                  </div>
                  <div className="text-center p-2 rounded-lg bg-amber-500/10">
                    <p className="text-2xl font-bold text-amber-400">0</p>
                    <p className="text-xs text-white/50">Due Soon</p>
                  </div>
                </div>
                <div className="border-t border-white/10 pt-3 mt-3">
                  <p className="text-white/30 text-sm text-center">No jobs to display</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Setup Instructions */}
      {!workStatus?.services.microsoft.authenticated && (
        <Card className="mt-6">
          <CardHeader title="Getting Started" subtitle="Connect your work accounts" />
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-white font-medium mb-2">Microsoft 365</h3>
                <p className="text-white/50 text-sm mb-3">
                  Connect once to access Outlook, Teams, and SharePoint. Uses Device Code Flow -
                  no admin approval needed.
                </p>
                <ol className="text-sm text-white/40 space-y-1 list-decimal list-inside">
                  <li>Click Connect Microsoft</li>
                  <li>Copy the code shown</li>
                  <li>Visit microsoft.com/devicelogin</li>
                  <li>Enter the code and sign in</li>
                </ol>
              </div>
              <div>
                <h3 className="text-white font-medium mb-2">J2 Tracker</h3>
                <p className="text-white/50 text-sm mb-3">
                  Opens a browser window for SSO login. Session is saved automatically.
                </p>
                <ol className="text-sm text-white/40 space-y-1 list-decimal list-inside">
                  <li>Click Connect J2 Tracker</li>
                  <li>Complete SSO in the browser</li>
                  <li>Window closes when done</li>
                </ol>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
