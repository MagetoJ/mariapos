# Project Contribution & Coding Standards

## General Expectations
- **Follow TypeScript-first development**: All new frontend logic should use TypeScript with strict typing enabled. Avoid using `any`; prefer explicit interfaces or utility types.
- **Maintain Django best practices**: Leverage Django REST Framework serializers and viewsets for backend APIs. Keep business logic in services or dedicated modules, not in views.
- **Prioritize readability**: Favour clear variable and function names, add docstrings or comments for complex logic, and avoid unnecessary cleverness.
- **Keep changes focused**: Limit pull requests to a single logical feature or fix. Provide concise, informative PR descriptions referencing related issues.

## Branching & Commits
1. **Branch naming**: Use the pattern `feature/<summary>`, `fix/<summary>`, or `chore/<summary>`. Example: `feature/dashboard-loading-states`.
2. **Commit messages**: Adopt the Conventional Commits format, e.g., `feat: add revenue comparison widget` or `fix: handle 401 on dashboard stats`.
3. **Rebase regularly**: Keep feature branches updated with the default branch via rebasing to reduce merge conflicts.

## Frontend Standards (Next.js)
- **File structure**: Place shared UI elements in `frontend/components`, hooks in `frontend/lib/hooks`, and API access in `frontend/lib/api`.
- **Styling**: Use TailwindCSS utilities. For complex styling, extract reusable class generators or components.
- **State management**: Prefer Zustand stores for global state, React context for cross-cutting concerns, and local state for component-specific data.
- **API integration**: All server communication should go through the centralized data service (`frontend/lib/api/data-service.ts`). Ensure type-safe responses using the definitions in `frontend/lib/types.ts`.
- **Error handling**: Display user-friendly messages via toast notifications or inline alerts. Log unexpected errors in the browser console during development.
- **Testing**: Add or update component tests (React Testing Library) and utility tests (Vitest/Jest) when introducing new functionality.

## Backend Standards (Django)
- **App organization**: Keep domain-specific logic within app directories (`orders`, `inventory`, etc.). Shared utilities belong in a `/utils` module.
- **Serializers & viewsets**: Validate data in serializers, restrict queryset exposure, and ensure proper permissions. Use DRF viewsets or generics where possible.
- **Database migrations**: Run `makemigrations` and `migrate` for schema changes. Commit generated migration files with descriptive names.
- **Celery tasks**: Place asynchronous jobs in `tasks.py`. Ensure idempotency and add logging for traceability.
- **Testing**: Write unit tests for business logic (`tests/test_*`). Use factories/fixtures for predictable data and run `python manage.py test` before submitting changes.

## Code Review Checklist
- **Types & interfaces**: Validate that TypeScript interfaces match API payloads; update both ends when schema changes.
- **API contracts**: Confirm request/response formats are documented and adhere to existing serializers.
- **Performance**: Avoid N+1 queries via `select_related`/`prefetch_related` and reduce unnecessary re-renders with memoization.
- **Security**: Sanitize user input, enforce permission checks, and use the centralized auth helpers.
- **Accessibility**: Ensure components meet basic a11y requirements (semantic HTML, ARIA labels, keyboard navigation).

## Tooling & Automation
1. **Linting**: Run `pnpm lint` for frontend and `ruff` (or configured linter) for backend before opening a PR.
2. **Formatting**: Use Prettier for frontend code (`pnpm format`) and `black` for backend Python files.
3. **Testing**: Execute relevant unit and integration tests. Document in the PR which suites were run and their results.

## Documentation
- **README updates**: Update high-level documentation when introducing new modules or workflows.
- **Changelog**: Append noteworthy changes to the project changelog if present. Mention migrations, breaking changes, and upgrade steps.
- **Inline comments**: Keep comments up to date. Remove dead code and outdated documentation during cleanup tasks.

## Onboarding Notes
- **Environment setup**: Follow `ENVIRONMENT_SETUP.md` for initial configuration. Confirm `NEXT_PUBLIC_API_URL` and Django `.env` values before development.
- **Mock data**: When backend endpoints are unavailable, use the mock data utilities in `frontend/lib/mock-data`. Replace with live integrations once endpoints stabilize.
- **Deployment awareness**: Coordinate with DevOps/infra maintainers when changes require configuration updates (CORS, environment variables, Celery workers).