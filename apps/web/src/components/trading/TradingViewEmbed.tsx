"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Button } from "../ui/Button";

interface TradingViewEmbedProps {
  symbol?: string;
  interval?: string;
  desktopServerUrl?: string;
}

type ViewState = "setup" | "connecting" | "streaming" | "error";

export function TradingViewEmbed({
  symbol = "GBPUSD",
  interval = "60",
  desktopServerUrl = "http://localhost:8000",
}: TradingViewEmbedProps) {
  const [viewState, setViewState] = useState<ViewState>("setup");
  const [screenshot, setScreenshot] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [hasCredentials, setHasCredentials] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const [sessionIdSign, setSessionIdSign] = useState("");
  const [showSetup, setShowSetup] = useState(false);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  // Check status on mount
  useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    try {
      const response = await fetch(`${desktopServerUrl}/tradingview/status`);
      if (response.ok) {
        const data = await response.json();
        setHasCredentials(data.ready);
        if (data.browser_active) {
          setViewState("streaming");
          startPolling();
        }
      }
    } catch {
      // Server not running
    }
  };

  // Fetch screenshot
  const fetchScreenshot = useCallback(async () => {
    try {
      const response = await fetch(`${desktopServerUrl}/tradingview/screenshot`);
      if (response.ok) {
        const data = await response.json();
        if (data.screenshot) {
          setScreenshot(data.screenshot);
          setErrorMessage(null);
        }
      }
    } catch {
      // Silent fail for polling
    }
  }, [desktopServerUrl]);

  // Start polling for screenshots
  const startPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
    }
    pollingRef.current = setInterval(fetchScreenshot, 150);
    fetchScreenshot();
  }, [fetchScreenshot]);

  // Stop polling
  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);

  // Save cookies
  const saveCookies = async () => {
    if (!sessionId || !sessionIdSign) {
      setErrorMessage("Both cookie values are required");
      return;
    }

    try {
      const response = await fetch(`${desktopServerUrl}/tradingview/setup-cookies`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          session_id_sign: sessionIdSign,
        }),
      });

      if (response.ok) {
        setHasCredentials(true);
        setShowSetup(false);
        setErrorMessage(null);
      } else {
        const data = await response.json();
        setErrorMessage(data.detail || "Failed to save cookies");
      }
    } catch (error) {
      setErrorMessage("Failed to connect to Desktop Server");
    }
  };

  // Launch TradingView
  const launchTradingView = async () => {
    setViewState("connecting");
    setErrorMessage(null);

    try {
      const response = await fetch(`${desktopServerUrl}/tradingview/launch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol: `FX:${symbol}`, interval }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to launch");
      }

      const data = await response.json();
      setIsLoggedIn(data.logged_in);
      setViewState("streaming");
      startPolling();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to connect");
      setViewState("error");
    }
  };

  // Navigate to symbol
  useEffect(() => {
    if (viewState === "streaming") {
      fetch(`${desktopServerUrl}/tradingview/navigate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol: `FX:${symbol}`, interval }),
      }).catch(() => {});
    }
  }, [symbol, interval, viewState, desktopServerUrl]);

  // Cleanup on unmount
  useEffect(() => {
    return () => stopPolling();
  }, [stopPolling]);

  // Setup/Error view
  if (viewState === "setup" || viewState === "error" || showSetup) {
    return (
      <div className="h-full flex flex-col items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg p-6 overflow-auto">
        <div className="text-center max-w-lg w-full">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>

          <h3 className="text-lg font-bold text-white mb-2">TradingView Integration</h3>

          {errorMessage && (
            <div className="mb-4 p-3 rounded-lg bg-red-500/20 border border-red-500/30 text-red-300 text-sm">
              {errorMessage}
            </div>
          )}

          {!hasCredentials || showSetup ? (
            <>
              <p className="text-white/60 text-sm mb-4">
                Enter your TradingView session cookies to view charts with your indicators.
              </p>

              <div className="bg-slate-800/50 rounded-lg p-4 mb-4 text-left">
                <p className="text-xs text-white/50 mb-3">
                  <strong>How to get cookies:</strong><br/>
                  1. Log into TradingView.com<br/>
                  2. Press F12 → Application → Cookies<br/>
                  3. Copy <code className="text-indigo-300">sessionid</code> and <code className="text-indigo-300">sessionid_sign</code>
                </p>

                <div className="space-y-3">
                  <div>
                    <label className="block text-xs text-white/40 mb-1">sessionid</label>
                    <input
                      type="text"
                      value={sessionId}
                      onChange={(e) => setSessionId(e.target.value)}
                      placeholder="Paste sessionid cookie value"
                      className="w-full px-3 py-2 bg-slate-700 border border-white/10 rounded text-sm text-white placeholder-white/30 focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-white/40 mb-1">sessionid_sign</label>
                    <input
                      type="text"
                      value={sessionIdSign}
                      onChange={(e) => setSessionIdSign(e.target.value)}
                      placeholder="Paste sessionid_sign cookie value"
                      className="w-full px-3 py-2 bg-slate-700 border border-white/10 rounded text-sm text-white placeholder-white/30 focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                </div>
              </div>

              <div className="flex gap-2">
                <Button variant="primary" onClick={saveCookies} className="flex-1">
                  Save Cookies
                </Button>
                {hasCredentials && (
                  <Button variant="secondary" onClick={() => setShowSetup(false)}>
                    Cancel
                  </Button>
                )}
              </div>
            </>
          ) : (
            <>
              <p className="text-white/60 text-sm mb-4">
                Cookies saved. Ready to launch TradingView with your account.
              </p>

              <div className="flex gap-2 justify-center">
                <Button variant="primary" onClick={launchTradingView}>
                  Launch TradingView
                </Button>
                <Button variant="secondary" onClick={() => setShowSetup(true)}>
                  Update Cookies
                </Button>
              </div>
            </>
          )}

          <p className="text-white/30 text-xs mt-4">
            Requires Desktop Server on localhost:8000
          </p>
        </div>
      </div>
    );
  }

  // Connecting view
  if (viewState === "connecting") {
    return (
      <div className="h-full flex items-center justify-center bg-slate-900 rounded-lg">
        <div className="text-center">
          <div className="w-12 h-12 mx-auto mb-4 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-white/60">Loading TradingView...</p>
          <p className="text-white/40 text-sm mt-2">This may take a few seconds</p>
        </div>
      </div>
    );
  }

  // Streaming view
  return (
    <div className="h-full relative bg-slate-900 rounded-lg overflow-hidden">
      {screenshot ? (
        <img
          src={screenshot}
          alt="TradingView Chart"
          className="w-full h-full object-contain"
          draggable={false}
        />
      ) : (
        <div className="h-full flex items-center justify-center">
          <div className="text-center">
            <div className="w-8 h-8 mx-auto mb-4 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-white/50">Loading chart...</p>
          </div>
        </div>
      )}

      {/* Status indicator */}
      <div className="absolute top-2 right-2 flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/50 backdrop-blur-sm">
        <div className={`w-2 h-2 rounded-full ${isLoggedIn ? "bg-emerald-400" : "bg-amber-400"} animate-pulse`} />
        <span className="text-xs text-white/70">
          {isLoggedIn ? "Logged In" : "Not Logged In"}
        </span>
      </div>

      {/* Controls */}
      <div className="absolute top-2 left-2 flex gap-2">
        <button
          onClick={() => {
            stopPolling();
            setViewState("setup");
            setScreenshot(null);
          }}
          className="px-3 py-1.5 rounded-lg bg-black/50 hover:bg-black/70 text-white/70 text-xs transition-colors"
        >
          Stop
        </button>
        <button
          onClick={() => setShowSetup(true)}
          className="px-3 py-1.5 rounded-lg bg-black/50 hover:bg-black/70 text-white/70 text-xs transition-colors"
        >
          Settings
        </button>
      </div>

      {/* Symbol indicator */}
      <div className="absolute bottom-2 left-2 px-3 py-1.5 rounded-lg bg-black/50 backdrop-blur-sm">
        <span className="text-sm font-mono text-white">{symbol}</span>
      </div>
    </div>
  );
}
