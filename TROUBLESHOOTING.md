# Project Vulcan - Troubleshooting

This document lists common errors and their solutions.

## Docker

### Error: `unable to get image 'postgres:13-alpine'`

**Cause:** The Docker daemon is not running or is not responsive.

**Solution:**
1.  Make sure Docker Desktop is running.
2.  Run `docker info` to check if the Docker daemon is responsive.
3.  If the issue persists, try restarting Docker Desktop.

### Error: `no configuration file provided: not found`

**Cause:** The `docker-compose` command is being run from a directory that does not contain a `docker-compose.yml` file.

**Solution:**
-   Run the `docker-compose` command from the root of the project, where the `docker-compose.yml` file is located.

## Prisma

### Error: `Environment variable not found: DATABASE_URL`

**Cause:** The `DATABASE_URL` environment variable is not set.

**Solution:**
1.  Create a `.env` file in the `apps/web` directory.
2.  Add the `DATABASE_URL` to the `.env` file. For local development, it should be `DATABASE_URL="postgresql://vulcan:vulcan@localhost:5432/vulcan"`.

### Error: `P1000: Authentication failed against database server`

**Cause:** The PostgreSQL container is not running, or the credentials in the `DATABASE_URL` are incorrect.

**Solution:**
1.  Make sure the PostgreSQL container is running by running `docker-compose up -d`.
2.  Verify that the username, password, and database name in the `DATABASE_URL` match the values in the `docker-compose.yml` file.

## Pytest

### Error: `TypeError: AsyncClient.__init__() got an unexpected keyword argument 'app'`

**Cause:** This can be caused by an old version of `httpx` or a dependency conflict.

**Solution:**
-   Use `fastapi.testclient.TestClient` instead of `httpx.AsyncClient` for testing FastAPI applications.
