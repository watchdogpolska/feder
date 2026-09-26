import * as Sentry from "@sentry/browser";

if (window.SENTRY_DSN) {
  Sentry.init({
    dsn: window.SENTRY_DSN,
    environment: window.SENTRY_ENVIRONMENT || "production",
    release: window.SENTRY_RELEASE || undefined,
  });
}
