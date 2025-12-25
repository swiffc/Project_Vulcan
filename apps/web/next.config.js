/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    DESKTOP_SERVER_URL: process.env.DESKTOP_SERVER_URL || "http://localhost:8000",
  },
  // PWA headers
  async headers() {
    return [
      {
        source: "/manifest.json",
        headers: [
          { key: "Content-Type", value: "application/manifest+json" },
        ],
      },
      {
        source: "/sw.js",
        headers: [
          { key: "Service-Worker-Allowed", value: "/" },
          { key: "Cache-Control", value: "no-cache" },
        ],
      },
    ];
  },
};

// Sentry configuration is optional - only enable if you have Sentry set up
const withSentry = process.env.SENTRY_DSN 
  ? require("@sentry/nextjs").withSentryConfig
  : (config) => config;

module.exports = withSentry(
  nextConfig,
  process.env.SENTRY_DSN ? {
    // For all available options, see:
    // https://github.com/getsentry/sentry-webpack-plugin#options

    // Suppress source map uploading logs during build
    silent: true,
    org: process.env.SENTRY_ORG || "your-org-slug",
    project: process.env.SENTRY_PROJECT || "your-project-slug",
  } : {},
  process.env.SENTRY_DSN ? {
    // For all available options, see:
    // https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/

    // Upload a larger set of source maps for better stack traces (increases build time)
    widenClientFileUpload: true,

    // Transpiles SDK to be compatible with IE11 (increases bundle size)
    transpileClientSDK: true,

    // Routes browser requests to Sentry through a Next.js rewrite to circumvent ad-blockers (increases server load)
    tunnelRoute: "/monitoring",

    // Hides source maps from generated client bundles
    hideSourceMaps: true,

    // Automatically tree-shake Sentry logger statements to reduce bundle size
    disableLogger: true,
  } : {}
);
  }
);
