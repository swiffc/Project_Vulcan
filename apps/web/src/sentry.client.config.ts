import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  
  // Environment and release tracking
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT || "development",
  release: process.env.NEXT_PUBLIC_RELEASE_VERSION || "dev",
  
  // Performance Monitoring
  tracesSampleRate: process.env.NEXT_PUBLIC_ENVIRONMENT === "production" ? 0.1 : 1.0,
  
  // Session Replay
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  
  // Don't send PII
  sendDefaultPii: false,
  
  // Filter sensitive data
  beforeSend(event) {
    // Remove sensitive query parameters
    if (event.request?.url) {
      try {
        const url = new URL(event.request.url);
        const sensitiveParams = ["api_key", "token", "password"];
        sensitiveParams.forEach(param => {
          if (url.searchParams.has(param)) {
            url.searchParams.set(param, "[Filtered]");
          }
        });
        event.request.url = url.toString();
      } catch (e) {
        // Invalid URL, skip filtering
      }
    }
    return event;
  },
});
