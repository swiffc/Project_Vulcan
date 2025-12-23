# Project Vulcan - API Documentation

This document provides a summary of the available API endpoints for the Project Vulcan orchestrator.

## Authentication

All endpoints (except `/health`) require an API key to be passed in the `X-API-Key` header.

## Endpoints

### Health

-   **GET /health**: Health check endpoint.

### Chat

-   **POST /chat**: Process a chat message and return an AI response.

### Desktop

-   **POST /desktop/command**: Proxy a command to the local desktop server.
-   **GET /desktop/health**: Check desktop server connectivity.

### Trading Journal

-   **POST /api/trading/journal**: Create a new trade.
-   **GET /api/trading/journal**: Get a list of all trades.
-   **GET /api/trading/journal/{trade_id}**: Get a single trade by ID.
-   **PUT /api/trading/journal/{trade_id}**: Update a trade by ID.
-   **DELETE /api/trading/journal/{trade_id}**: Delete a trade by ID.

### CAD Validation History

-   **GET /api/cad/validations/recent**: Get a list of recent validations.
-   **GET /api/cad/validations/{validation_id}**: Get a single validation by ID.