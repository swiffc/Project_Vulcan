"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
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

interface DeviceCodeInfo {
  userCode: string;
  verificationUri: string;
  requestId: string;
  expiresIn: number;
}

interface Email {
  id: string;
  subject: string;
  from: { name: string; email: string };
  receivedAt: string;
  isRead: boolean;
  importance: "low" | "normal" | "high";
  preview: string;
}

interface EmailData {
  emails: Email[];
  unreadCount: number;
  importantUnread: number;
}

interface TeamsChat {
  id: string;
  topic: string;
  type: "group" | "oneOnOne";
  lastMessage: { content: string; from: string; timestamp: string };
  unreadCount: number;
}

interface TeamsMention {
  chatId: string;
  messageId: string;
  mentionedBy: string;
  preview: string;
  timestamp: string;
}

interface TeamsData {
  chats: TeamsChat[];
  mentions: TeamsMention[];
  totalUnread: number;
  mentionCount: number;
}

interface DriveFile {
  id: string;
  name: string;
  path: string;
  webUrl: string;
  lastModified: string;
  modifiedBy: string;
  size: number;
  mimeType: string;
}

interface FilesData {
  files: DriveFile[];
  source: string;
}

export default function WorkPage() {
  const [workStatus, setWorkStatus] = useState<WorkHealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  // Device Code Flow State
  const [deviceCode, setDeviceCode] = useState<DeviceCodeInfo | null>(null);
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  // Data States
  const [emailData, setEmailData] = useState<EmailData | null>(null);
  const [teamsData, setTeamsData] = useState<TeamsData | null>(null);
  const [filesData, setFilesData] = useState<FilesData | null>(null);
  const [dataLoading, setDataLoading] = useState(false);

  const checkWorkHealth = useCallback(async () => {
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
  }, []);

  // Fetch all Microsoft data when authenticated
  const fetchAllData = useCallback(async () => {
    if (!workStatus?.services.microsoft.authenticated) return;

    setDataLoading(true);
    try {
      const [emailRes, teamsRes, filesRes] = await Promise.all([
        fetch("/api/work/microsoft/mail"),
        fetch("/api/work/microsoft/teams"),
        fetch("/api/work/microsoft/files"),
      ]);

      if (emailRes.ok) setEmailData(await emailRes.json());
      if (teamsRes.ok) setTeamsData(await teamsRes.json());
      if (filesRes.ok) setFilesData(await filesRes.json());
    } catch (error) {
      console.error("Failed to fetch data:", error);
    } finally {
      setDataLoading(false);
    }
  }, [workStatus?.services.microsoft.authenticated]);

  // Initial load
  useEffect(() => {
    checkWorkHealth();
    const interval = setInterval(checkWorkHealth, 60000);
    return () => clearInterval(interval);
  }, [checkWorkHealth]);

  // Fetch data when authenticated
  useEffect(() => {
    if (workStatus?.services.microsoft.authenticated) {
      fetchAllData();
    }
  }, [workStatus?.services.microsoft.authenticated, fetchAllData]);

  // Poll for device code status
  useEffect(() => {
    if (!deviceCode) return;

    const pollInterval = setInterval(async () => {
      try {
        const res = await fetch(`/api/work/microsoft/auth/device-code?requestId=${deviceCode.requestId}`);
        const data = await res.json();

        if (data.status === "authorized") {
          setDeviceCode(null);
          setAuthError(null);
          checkWorkHealth();
        } else if (data.status === "expired" || data.status === "error") {
          setDeviceCode(null);
          setAuthError(data.message || "Authentication failed");
        }
      } catch (error) {
        console.error("Poll error:", error);
      }
    }, 3000);

    return () => clearInterval(pollInterval);
  }, [deviceCode, checkWorkHealth]);

  const startMicrosoftAuth = async () => {
    setAuthLoading(true);
    setAuthError(null);

    try {
      const res = await fetch("/api/work/microsoft/auth/device-code", { method: "POST" });
      const data = await res.json();

      if (data.success) {
        setDeviceCode({
          userCode: data.userCode,
          verificationUri: data.verificationUri,
          requestId: data.requestId,
          expiresIn: data.expiresIn,
        });
      } else {
        setAuthError(data.error || "Failed to start authentication");
      }
    } catch (error) {
      setAuthError("Failed to connect to authentication service");
    } finally {
      setAuthLoading(false);
    }
  };

  const signOut = async () => {
    try {
      await fetch("/api/work/microsoft/auth/signout", { method: "POST" });
      setEmailData(null);
      setTeamsData(null);
      setFilesData(null);
      checkWorkHealth();
    } catch (error) {
      console.error("Sign out error:", error);
    }
  };

  const isServiceConnected = (service: ServiceStatus | undefined) => {
    return service?.configured && service?.authenticated;
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    if (diff < 60000) return "Just now";
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getFileIcon = (mimeType: string) => {
    if (mimeType.includes("pdf")) return "text-red-400";
    if (mimeType.includes("word") || mimeType.includes("document")) return "text-blue-400";
    if (mimeType.includes("sheet") || mimeType.includes("excel")) return "text-green-400";
    if (mimeType.includes("presentation") || mimeType.includes("powerpoint")) return "text-orange-400";
    if (mimeType.includes("image")) return "text-purple-400";
    return "text-white/40";
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

          {workStatus?.services.microsoft.authenticated && (
            <Button variant="ghost" size="sm" onClick={signOut}>
              Sign Out
            </Button>
          )}

          <span className="text-xs text-white/30">
            {lastRefresh ? `Updated ${lastRefresh.toLocaleTimeString()}` : "Loading..."}
          </span>

          <Button variant="secondary" size="sm" onClick={() => { checkWorkHealth(); fetchAllData(); }}>
            <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </Button>
        </div>
      </div>

      {/* Device Code Modal */}
      {deviceCode && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <Card className="max-w-md w-full mx-4">
            <CardHeader title="Sign in to Microsoft" subtitle="Complete authentication in your browser" />
            <CardContent>
              <div className="text-center space-y-4">
                <div className="bg-vulcan-accent/20 rounded-xl p-4">
                  <p className="text-sm text-white/60 mb-2">Your code:</p>
                  <p className="text-3xl font-mono font-bold text-vulcan-accent tracking-wider">
                    {deviceCode.userCode}
                  </p>
                </div>
                <div className="space-y-2">
                  <p className="text-white/60 text-sm">
                    1. Go to{" "}
                    <a href={deviceCode.verificationUri} target="_blank" rel="noopener noreferrer" className="text-vulcan-accent hover:underline">
                      {deviceCode.verificationUri}
                    </a>
                  </p>
                  <p className="text-white/60 text-sm">2. Enter the code above</p>
                  <p className="text-white/60 text-sm">3. Sign in with your Microsoft account</p>
                </div>
                <Button variant="primary" onClick={() => window.open(deviceCode.verificationUri, "_blank")} className="w-full">
                  Open Microsoft Login
                </Button>
                <p className="text-white/30 text-xs">
                  Waiting for authentication... (expires in {Math.floor(deviceCode.expiresIn / 60)} minutes)
                </p>
                <Button variant="ghost" size="sm" onClick={() => setDeviceCode(null)}>Cancel</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

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
                {authError && <p className="text-red-400 text-sm mb-4">{authError}</p>}
                <Button variant="primary" onClick={startMicrosoftAuth} disabled={authLoading}>
                  {authLoading ? "Connecting..." : "Connect Microsoft"}
                </Button>
              </div>
            ) : dataLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-8 h-8 border-2 border-vulcan-accent border-t-transparent rounded-full animate-spin" />
              </div>
            ) : emailData ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white/50">Unread</span>
                  <Badge variant="info">{emailData.unreadCount}</Badge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white/50">Important</span>
                  <Badge variant="warning">{emailData.importantUnread}</Badge>
                </div>
                <div className="border-t border-white/10 pt-3 mt-3 space-y-2 max-h-48 overflow-y-auto">
                  {emailData.emails.length > 0 ? (
                    emailData.emails.slice(0, 5).map((email) => (
                      <div key={email.id} className={`p-2 rounded-lg ${email.isRead ? "bg-white/5" : "bg-vulcan-accent/10"}`}>
                        <div className="flex items-start justify-between gap-2">
                          <div className="min-w-0 flex-1">
                            <p className={`text-sm truncate ${email.isRead ? "text-white/60" : "text-white font-medium"}`}>
                              {email.subject}
                            </p>
                            <p className="text-xs text-white/40 truncate">{email.from.name}</p>
                          </div>
                          <span className="text-xs text-white/30 whitespace-nowrap">{formatTime(email.receivedAt)}</span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-white/30 text-sm text-center">No emails to display</p>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-white/30 text-sm text-center py-4">No email data available</p>
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
            ) : dataLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-8 h-8 border-2 border-purple-400 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : teamsData ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white/50">Mentions</span>
                  <Badge variant="error">{teamsData.mentionCount}</Badge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white/50">Unread Chats</span>
                  <Badge variant="info">{teamsData.totalUnread}</Badge>
                </div>
                <div className="border-t border-white/10 pt-3 mt-3 space-y-2 max-h-48 overflow-y-auto">
                  {teamsData.chats.length > 0 ? (
                    teamsData.chats.slice(0, 4).map((chat) => (
                      <div key={chat.id} className="p-2 rounded-lg bg-white/5">
                        <div className="flex items-start justify-between gap-2">
                          <div className="min-w-0 flex-1">
                            <p className="text-sm text-white truncate">{chat.topic || "Chat"}</p>
                            <p className="text-xs text-white/40 truncate">{chat.lastMessage.from}: {chat.lastMessage.content}</p>
                          </div>
                          <span className="text-xs text-white/30">{formatTime(chat.lastMessage.timestamp)}</span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-white/30 text-sm text-center">No chats to display</p>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-white/30 text-sm text-center py-4">No Teams data available</p>
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
            ) : dataLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-8 h-8 border-2 border-green-400 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : filesData ? (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {filesData.files.length > 0 ? (
                  filesData.files.slice(0, 6).map((file) => (
                    <a
                      key={file.id}
                      href={file.webUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <svg className={`w-5 h-5 ${getFileIcon(file.mimeType)}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <div className="min-w-0 flex-1">
                          <p className="text-sm text-white truncate">{file.name}</p>
                          <p className="text-xs text-white/40">{formatFileSize(file.size)} - {formatTime(file.lastModified)}</p>
                        </div>
                      </div>
                    </a>
                  ))
                ) : (
                  <p className="text-white/30 text-sm text-center py-4">No recent files</p>
                )}
              </div>
            ) : (
              <p className="text-white/30 text-sm text-center py-4">No files data available</p>
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
                <p className="text-white/50 mb-4">J2 Tracker requires Desktop Server</p>
                <Button variant="primary" disabled>
                  <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                  Coming Soon
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
                  First, you need to create a free Azure AD app registration.
                  This takes about 5 minutes and doesn't require admin approval.
                </p>
                <Link href="/work/setup">
                  <Button variant="secondary" size="sm">View Setup Guide</Button>
                </Link>
                <div className="mt-4">
                  <p className="text-white/40 text-xs">After setup, add to .env.local:</p>
                  <code className="text-xs text-green-400 bg-white/5 px-2 py-1 rounded block mt-1">
                    MICROSOFT_CLIENT_ID=your-id
                  </code>
                </div>
              </div>
              <div>
                <h3 className="text-white font-medium mb-2">J2 Tracker</h3>
                <p className="text-white/50 text-sm mb-3">
                  Requires Desktop Server with browser automation. Coming in Phase 4.
                </p>
                <ol className="text-sm text-white/40 space-y-1 list-decimal list-inside">
                  <li>Start Desktop Server locally</li>
                  <li>Click Connect J2 Tracker</li>
                  <li>Complete SSO in the browser</li>
                  <li>Session saves automatically</li>
                </ol>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
