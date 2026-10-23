# Interpals API - Project Context

## Project Description
An unofficial Python API for interpals.net, providing structured access to user data, albums, and pictures.

## Tech Stack
- **Python 3.12+**
- **Requests / Aiohttp** for HTTP communication
- **Yarl** for URL handling
- **DataClasses** for schema representation

## Development Guidelines
- **Naming**: Follow PEP 8. Use snake_case for functions/variables and PascalCase for classes.
- **Typing**: Use type hints consistently.
- **Error Handling**: Use the `InterpalsAPIError` hierarchy.
- **Parsers**: Each parser should be isolated in `interpals_api/parsers/`.
- **Session Management**: Use the `Session` class for stateful requests (cookies, user-agent).

## Key Components
- `interpals_api.session`: Login and session management.
- `interpals_api.parsers`: Logic for extracting data from Interpals HTML.
- `interpals_api.schemas`: Data models for Profile, Album, Picture, etc.
- `interpals_api.cookie`: Cookie management.

## Architecture Notes
- The library uses a hybrid approach: `login_sync` (requests) and `login_async` (aiohttp) for both synchronous and asynchronous usage.
- Parsers utilize regex and JSON extraction from `data-react-data` attributes where available.
