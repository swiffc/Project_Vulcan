"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { StatusDot } from "../ui/Badge";
import { ThemeToggle } from "../ui/ThemeToggle";
import { useEffect, useState } from "react";

interface NavItem {
  path: string;
  label: string;
  icon: React.ReactNode;
  ariaLabel: string;
}

const navItems: NavItem[] = [
  {
    path: "/",
    label: "Dashboard",
    ariaLabel: "Go to Dashboard",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
      </svg>
    ),
  },
  {
    path: "/trading",
    label: "Trading",
    ariaLabel: "Go to Trading module",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
    ),
  },
  {
    path: "/cad",
    label: "CAD",
    ariaLabel: "Go to CAD validation module",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
      </svg>
    ),
  },
  {
    path: "/work",
    label: "Work",
    ariaLabel: "Go to Work hub",
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
  },
];

export function Navigation() {
  const pathname = usePathname();
  const [desktopStatus, setDesktopStatus] = useState<"online" | "offline" | "checking">("checking");
  const [currentTime, setCurrentTime] = useState<string>("");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Check desktop server health
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch("/api/desktop/health", { cache: "no-store" });
        setDesktopStatus(res.ok ? "online" : "offline");
      } catch {
        setDesktopStatus("offline");
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  // Update time
  useEffect(() => {
    const updateTime = () => {
      setCurrentTime(new Date().toLocaleDateString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
      }));
    };
    updateTime();
    const interval = setInterval(updateTime, 60000);
    return () => clearInterval(interval);
  }, []);

  return (
    <nav className="glass border-b border-white/10 sticky top-0 z-50" role="navigation" aria-label="Main navigation">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3" aria-label="Project Vulcan Home">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-vulcan-accent to-purple-600 flex items-center justify-center shadow-lg shadow-vulcan-accent/20">
              <span className="text-xl font-bold text-white" aria-hidden="true">V</span>
            </div>
            <div className="hidden sm:block">
              <h1 className="text-lg font-bold text-white">Project Vulcan</h1>
              <p className="text-xs text-white/40">AI Operating System</p>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center gap-1" role="menubar">
            {navItems.map((item) => {
              const isActive = pathname === item.path;
              return (
                <Link
                  key={item.path}
                  href={item.path}
                  aria-label={item.ariaLabel}
                  aria-current={isActive ? "page" : undefined}
                  role="menuitem"
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all focus:outline-none focus:ring-2 focus:ring-vulcan-accent focus:ring-offset-2 focus:ring-offset-transparent ${
                    isActive
                      ? "bg-vulcan-accent text-white shadow-lg shadow-vulcan-accent/20"
                      : "text-white/60 hover:text-white hover:bg-white/5"
                  }`}
                >
                  {item.icon}
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </div>

          {/* Status Indicators */}
          <div className="flex items-center gap-4">
            {/* Theme Toggle */}
            <div className="hidden sm:block">
              <ThemeToggle />
            </div>

            {/* Desktop Server Status */}
            <div className="hidden sm:flex items-center gap-2 text-sm" role="status" aria-live="polite">
              <StatusDot status={desktopStatus} />
              <span className="text-white/50">
                {desktopStatus === "checking" ? "Checking..." :
                 desktopStatus === "online" ? "Connected" : "Offline"}
              </span>
            </div>

            {/* Mobile Status Dot Only */}
            <div className="sm:hidden" role="status" aria-label={`Desktop server ${desktopStatus}`}>
              <StatusDot status={desktopStatus} />
            </div>

            {/* Date */}
            <time className="text-white/40 text-sm hidden lg:inline" dateTime={new Date().toISOString()}>
              {currentTime}
            </time>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-white/60 hover:text-white hover:bg-white/5 transition-colors focus:outline-none focus:ring-2 focus:ring-vulcan-accent"
              aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
              aria-expanded={mobileMenuOpen}
              aria-controls="mobile-menu"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                {mobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div id="mobile-menu" className="md:hidden border-t border-white/10 py-2" role="menu">
            <div className="flex flex-col gap-1">
              {navItems.map((item) => {
                const isActive = pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    href={item.path}
                    onClick={() => setMobileMenuOpen(false)}
                    aria-label={item.ariaLabel}
                    aria-current={isActive ? "page" : undefined}
                    role="menuitem"
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all focus:outline-none focus:ring-2 focus:ring-vulcan-accent ${
                      isActive
                        ? "bg-vulcan-accent text-white shadow-lg shadow-vulcan-accent/20"
                        : "text-white/60 hover:text-white hover:bg-white/5"
                    }`}
                  >
                    {item.icon}
                    <span className="font-medium">{item.label}</span>
                  </Link>
                );
              })}
              {/* Theme toggle in mobile menu */}
              <div className="px-4 py-3 border-t border-white/10 mt-2">
                <div className="flex items-center justify-between">
                  <span className="text-white/60 font-medium">Theme</span>
                  <ThemeToggle />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
