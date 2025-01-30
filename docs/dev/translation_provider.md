_Translation Provider_ is used to provide translation resources for front end UI interface
using `i18next` project.

# Structure

When we talking about _frontend_ and _backend_ of RRSS translation system:

- **Frontend**: Fetch translation resources from backend, then properly display the translation result to user.
- **Backend**: Manage translation resources, provide endpoints for frontend to retrieve corresponding resources.

# Frontend

Frontend should use packages [i18next](https://www.i18next.com/) as the frontend translation framework.

Additionally, `i18next-fetch-backend` could be used to retrieve translation resources from backend endpoints.

# Backend

A global `TranslationManager` is provided to allow RRSS or other plugins to register new translation resources. This manager is also responsible for loading and caching the corresponding resources when needed.

## Resource Registration

The basic resources unit is `namespace`, which shares the identical meaning in `i18next`.
