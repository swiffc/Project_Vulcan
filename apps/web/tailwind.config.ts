import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        vulcan: {
          dark: "#1e1b4b",
          darker: "#0d1117",
          light: "#4338ca",
          accent: "#6366f1",
          success: "#34d399",
          warning: "#fbbf24",
          error: "#f87171",
          surface: "rgba(255, 255, 255, 0.1)",
        },
        trading: {
          bullish: "var(--trading-bullish)",
          bearish: "var(--trading-bearish)",
          neutral: "var(--trading-neutral)",
          warning: "var(--trading-warning)",
          info: "var(--trading-info)",
        },
        session: {
          asian: "var(--session-asian)",
          london: "var(--session-london)",
          newyork: "var(--session-newyork)",
          gap: "var(--session-gap)",
        },
        ema: {
          mustard: "var(--ema-mustard)",
          ketchup: "var(--ema-ketchup)",
          water: "var(--ema-water)",
          mayo: "var(--ema-mayo)",
          blueberry: "var(--ema-blueberry)",
        },
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "glass-gradient":
          "linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)",
      },
      backdropBlur: {
        glass: "12px",
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
        "glass-inset": "inset 0 0 0 1px rgba(255, 255, 255, 0.1)",
      },
    },
  },
  plugins: [],
};

export default config;
