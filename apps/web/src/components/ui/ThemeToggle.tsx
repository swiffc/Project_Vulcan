"use client";

import { useEffect, useState } from "react";
import * as Switch from "@radix-ui/react-switch";

type Theme = "dark" | "light" | "system";

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>("dark");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const savedTheme = localStorage.getItem("vulcan-theme") as Theme;
    if (savedTheme) {
      setTheme(savedTheme);
    }
  }, []);

  useEffect(() => {
    if (!mounted) return;

    const root = document.documentElement;
    localStorage.setItem("vulcan-theme", theme);

    if (theme === "system") {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
      root.classList.toggle("light-mode", systemTheme === "light");
    } else {
      root.classList.toggle("light-mode", theme === "light");
    }
  }, [theme, mounted]);

  if (!mounted) {
    return null;
  }

  const isDark = theme === "dark" || (theme === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches);

  return (
    <div className="flex items-center gap-2">
      {/* Sun Icon */}
      <svg
        className={`w-4 h-4 transition-colors ${isDark ? "text-white/40" : "text-amber-400"}`}
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
        />
      </svg>

      <Switch.Root
        checked={isDark}
        onCheckedChange={(checked) => setTheme(checked ? "dark" : "light")}
        className="w-11 h-6 bg-white/20 rounded-full relative data-[state=checked]:bg-vulcan-accent transition-colors focus:outline-none focus:ring-2 focus:ring-vulcan-accent focus:ring-offset-2 focus:ring-offset-transparent"
        aria-label="Toggle dark mode"
      >
        <Switch.Thumb className="block w-5 h-5 bg-white rounded-full shadow-lg transition-transform duration-200 translate-x-0.5 data-[state=checked]:translate-x-[22px]" />
      </Switch.Root>

      {/* Moon Icon */}
      <svg
        className={`w-4 h-4 transition-colors ${isDark ? "text-indigo-400" : "text-white/40"}`}
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
        />
      </svg>
    </div>
  );
}

export default ThemeToggle;
