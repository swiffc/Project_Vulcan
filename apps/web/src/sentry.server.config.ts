import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  
  // Environment and release tracking
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT || "development",
  release: process.env.NEXT_PUBLIC_RELEASE_VERSION || "dev",
  
  // Performance Monitoring
  tracesSampleRate: process.env.NEXT_PUBLIC_ENVIRONMENT === "production" ? 0.1 : 1.0,
  
  // Don't send PII
  sendDefaultPii: false,
});
