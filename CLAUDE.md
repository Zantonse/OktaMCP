# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Okta MCP Server**, a Model Context Protocol server that allows LLM agents to manage Okta organizations via natural language. It integrates with Okta's Admin Management APIs through the official Okta Python SDK.

## Commands

### Install and Run
```bash
uv sync                    # Install dependencies
uv run okta-mcp-server     # Run the server
```

### Linting
```bash
uv run ruff check .        # Check for lint errors
uv run ruff check --fix .  # Auto-fix lint errors
uv run ruff format .       # Format code
```

### Testing
```bash
uv run pytest              # Run all tests
uv run pytest tests/test_users.py  # Run specific test file
uv run pytest -k "test_name"       # Run tests matching pattern
```

### Debug Mode
```bash
export OKTA_LOG_LEVEL=DEBUG
export OKTA_LOG_FILE="/path/to/okta-mcp.log"  # Optional
```

## Architecture

### Entry Point
`src/okta_mcp_server/server.py` - Creates the FastMCP server instance with OAuth lifecycle management. Tools are lazily imported at startup in `main()`.

### Tool Modules
Tools are organized under `src/okta_mcp_server/tools/`:
- `users/users.py` - User CRUD, deactivation, profile attributes
- `groups/groups.py` - Group CRUD, membership management
- `applications/applications.py` - App CRUD, activation/deactivation
- `policies/policies.py` - Policy and policy rule management
- `system_logs/system_logs.py` - System log retrieval

Each tool function is decorated with `@mcp.tool()` and receives a `Context` object to access the auth manager.

### Authentication Flow
`src/okta_mcp_server/utils/auth/auth_manager.py` - `OktaAuthManager` class handles:
- **Device Authorization Grant** - Interactive browser-based flow (default)
- **Private Key JWT** - Browserless client credentials flow (when `OKTA_PRIVATE_KEY` and `OKTA_KEY_ID` are set)

Tokens are stored securely in the system keyring under service name `OktaAuthManager`.

### Utilities
- `utils/client.py` - Creates authenticated `OktaClient` instances, handles token refresh
- `utils/pagination.py` - Shared pagination helpers: `paginate_all_results()`, `create_paginated_response()`, `build_query_params()`

## Code Conventions

### Ruff Configuration
- Line length: 119 characters
- Quote style: double quotes
- Rules: Pyflakes (F), pycodestyle (E), isort (I), Ruff-specific (RUF)

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`

### Deletion Safety Pattern
Destructive operations (delete_user, delete_group, delete_application) use a two-step confirmation:
1. First call returns `{"confirmation_required": True, "message": "..."}`
2. User must explicitly type 'DELETE'
3. Second call (`confirm_delete_*`) executes the deletion

### Environment Variables
- `OKTA_ORG_URL` (required) - Okta organization URL
- `OKTA_CLIENT_ID` (required) - OAuth client ID
- `OKTA_SCOPES` - Space-separated OAuth scopes
- `OKTA_PRIVATE_KEY` - RSA private key for browserless auth
- `OKTA_KEY_ID` - Key ID for browserless auth
