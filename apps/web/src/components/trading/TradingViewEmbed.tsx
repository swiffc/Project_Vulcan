"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Button } from "../ui/Button";

interface TradingViewEmbedProps {
  symbol?: string;
  interval?: string;
  desktopServerUrl?: string;
}

type ConnectionStatus = "disconnected" | "connecting" | "connected" | "error";

export function TradingViewEmbed({
  symbol = "GBPUSD",
  interval = "60",
  desktopServerUrl = "http://localhost:8000",
}: TradingViewEmbedProps) {
  const [status, setStatus] = useState<ConnectionStatus>("disconnected");
  const [screenshot, setScreenshot] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Launch TradingView browser
  const launchTradingView = useCallback(async () => {
    setStatus("connecting");
    setErrorMessage(null);

    try {
      const response = await fetch(`${desktopServerUrl}/tradingview/launch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol, interval }),
      });

      if (!response.ok) {
        throw new Error(`Failed to launch: ${response.statusText}`);
      }

      const data = await response.json();
      setIsLoggedIn(data.logged_in);
      setStatus("connected");

      // Start screenshot stream
      startStream();
    } catch (error) {
      console.error("Launch error:", error);
      setErrorMessage(
        error instanceof Error ? error.message : "Failed to connect to Desktop Server"
      );
      setStatus("error");
    }
  }, [desktopServerUrl, symbol, interval]);

  // Start WebSocket screenshot stream
  const startStream = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const wsUrl = desktopServerUrl.replace("http", "ws");
    const ws = new WebSocket(`${wsUrl}/tradingview/stream`);

    ws.onopen = () => {
      console.log("TradingView stream connected");
      setStatus("connected");
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.screenshot) {
          setScreenshot(data.screenshot);
        }
        if (data.error) {
          setErrorMessage(data.error);
        }
      } catch (e) {
        console.error("Parse error:", e);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setStatus("error");
    };

    ws.onclose = () => {
      console.log("WebSocket closed");
      if (status === "connected") {
        setStatus("disconnected");
      }
    };

    wsRef.current = ws;
  }, [desktopServerUrl, status]);

  // Navigate to symbol
  const navigateToSymbol = useCallback(async (newSymbol: string, newInterval: string) => {
    try {
      await fetch(`${desktopServerUrl}/tradingview/navigate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol: newSymbol, interval: newInterval }),
      });
    } catch (error) {
      console.error("Navigate error:", error);
    }
  }, [desktopServerUrl]);

  // Handle click on the chart image
  const handleClick = useCallback(async (e: React.MouseEvent<HTMLImageElement>) => {
    if (!containerRef.current || status !== "connected") return;

    const rect = e.currentTarget.getBoundingClientRect();
    const scaleX = 1920 / rect.width;
    const scaleY = 1080 / rect.height;

    const x = Math.round((e.clientX - rect.left) * scaleX);
    const y = Math.round((e.clientY - rect.top) * scaleY);

    try {
      await fetch(`${desktopServerUrl}/tradingview/click`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ x, y, button: "left" }),
      });
    } catch (error) {
      console.error("Click error:", error);
    }
  }, [desktopServerUrl, status]);

  // Update symbol when props change
  useEffect(() => {
    if (status === "connected") {
      navigateToSymbol(symbol, interval);
    }
  }, [symbol, interval, status, navigateToSymbol]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Render based on status
  if (status === "disconnected" || status === "error") {
    return (
      <div className="h-full flex flex-col items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg p-8">
        <div className="text-center max-w-md">
          <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <svg className="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-white mb-2">TradingView Integration</h3>
          <p className="text-white/60 mb-6">
            Launch TradingView with your account to see your custom indicators and saved layouts.
          </p>

          {errorMessage && (
            <div className="mb-4 p-3 rounded-lg bg-red-500/20 border border-red-500/30 text-red-300 text-sm">
              {errorMessage}
            </div>
          )}

          <Button
            variant="primary"
            onClick={launchTradingView}
            className="px-6 py-3 text-lg"
          >
            <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Launch TradingView
          </Button>

          <p className="text-white/40 text-xs mt-4">
            Requires Desktop Server running on localhost:8000
          </p>
        </div>
      </div>
    );
  }

  if (status === "connecting") {
    return (
      <div className="h-full flex items-center justify-center bg-slate-900 rounded-lg">
        <div className="text-center">
          <div className="w-12 h-12 mx-auto mb-4 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-white/60">Launching TradingView...</p>
          <p className="text-white/40 text-sm mt-2">Browser will open for login if needed</p>
        </div>
      </div>
    );
  }

  // Connected - show screenshot stream
  return (
    <div ref={containerRef} className="h-full relative bg-slate-900 rounded-lg overflow-hidden">
      {screenshot ? (
        <img
          src={screenshot}
          alt="TradingView Chart"
          className="w-full h-full object-contain cursor-crosshair"
          onClick={handleClick}
          draggable={false}
        />
      ) : (
        <div className="h-full flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {/* Status indicator */}
      <div className="absolute top-2 right-2 flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/50 backdrop-blur-sm">
        <div className={`w-2 h-2 rounded-full ${isLoggedIn ? "bg-emerald-400" : "bg-amber-400"} animate-pulse`} />
        <span className="text-xs text-white/70">
          {isLoggedIn ? "Logged In" : "Log in to see indicators"}
        </span>
      </div>

      {/* Symbol indicator */}
      <div className="absolute bottom-2 left-2 px-3 py-1.5 rounded-lg bg-black/50 backdrop-blur-sm">
        <span className="text-sm font-mono text-white">{symbol}</span>
        <span className="text-white/40 mx-2">|</span>
        <span className="text-sm text-white/60">{interval}m</span>
      </div>
    </div>
  );
}
