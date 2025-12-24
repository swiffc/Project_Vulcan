# Project Vulcan - Troubleshooting

This document lists common errors and their solutions.

---

## Infrastructure

### PostgreSQL Connection Issues

**Error:** `Environment variable not found: DATABASE_URL` or `Authentication failed`

- **Cause:** Database server not running or incorrect credentials in `.env`.
- **Solution:** 
  1. Ensure PostgreSQL is installed and running.
  2. Check `DATABASE_URL` in `.env`. It should look like: `postgresql://postgres:password@localhost:5432/vulcan`.
  3. Run `npx prisma db push` to synchronize the schema.

### Sentry Monitoring

**Error:** `Sentry is not initialized`

- **Cause:** Missing `SENTRY_DSN` in `.env`.
- **Solution:** 
  1. Get your DSN from [sentry.io](https://sentry.io).
  2. Add `NEXT_PUBLIC_SENTRY_DSN` for the frontend and `SENTRY_DSN` for the backend server.

### Tailscale VPN Tunneling

**Error:** `Cannot connect to desktop server (100.x.x.x)`

- **Cause:** Tailscale not authenticated or node is offline.
- **Solution:**
  1. Run `tailscale status` on both machines.
  2. Ensure the firewall on the host machine allows inbound traffic on port 8000.
  3. Test connectivity with `curl http://[Tailscale-IP]:8000/health`.

---

## Application Modules

### CAD Automation

**Error:** `SolidWorks/Inventor COM connection failed`

- **Cause:** Software is closed or running with different permissions.
- **Solution:**
  1. Open the CAD application manually first.
  2. Run the Desktop Control Server and CAD application as the *same* user (preferably not Administrator unless both are).

### Trading Journal

**Error:** `Failed to save trade: 500 Internal Server Error`

- **Cause:** Prisma client or database sync error.
- **Solution:** 
  1. Check terminal logs for specific database constraints.
  2. Run `npx prisma generate` if you've recently updated the schema.

---

## Development Tools

### Pytest Failure (FastAPI)

**Error:** `TypeError: AsyncClient.__init__() got an unexpected keyword argument 'app'`

- **Cause:** Incompatible `httpx` version.
- **Solution:** Use `fastapi.testclient.TestClient` for synchronous testing or update `httpx` and `pytest-asyncio`.
