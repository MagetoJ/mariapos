# Repository Reference

## Project Overview
- **Name**: Maria Havens POS
- **Description**: Full-stack Point of Sale system for hotel & restaurant operations with dashboards, order management, inventory, guests, payments, reports, and notifications.
- **Frontend**: Next.js 15 (App Router) with TypeScript, TailwindCSS v4, Zustand state management, Recharts for data visualization, shadcn/ui components.
- **Backend**: Django REST Framework with JWT authentication, PostgreSQL/SQLite support, Celery for async tasks, Channels/WebSockets for notifications.

## Key Directories
1. `frontend/` — Next.js application
   - `app/` — App Router routes (dashboard, orders, tables, inventory, etc.)
   - `components/` — Reusable UI widgets (dashboard cards, charts, forms)
   - `lib/api/data-service.ts` — Data layer calling Django APIs
   - `lib/mock-data/` — Mock data used when backend is not configured
2. `backend/` — Django project (`mariahavens_pos_backend`)
   - Apps: `accounts`, `dashboard_stats`, `orders`, `inventory`, `guests`, `service_requests`, `reports`, `payments`, `menu`
   - `mariahavens_pos_backend/settings.py` — Global settings & installed apps
   - `mariahavens_pos_backend/urls.py` — Root API routes under `/api/`
3. `DJANGO_API_DOCUMENTATION.md` — Detailed REST endpoint specs and payloads
4. `ENVIRONMENT_SETUP.md` — Local environment configuration instructions

## Environment Variables
### Frontend (`frontend/.env.local`)
- `NEXT_PUBLIC_API_URL` — Base URL for Django API (e.g., `http://localhost:8000/api`)
- Additional variables (if needed) follow `NEXT_PUBLIC_*` naming for client usage.

### Backend (`backend/.env` or `.env.django`)
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, database connection vars
- Email and Celery configuration as required

## Setup & Commands
### Frontend
1. Install dependencies:
   ```bash
   pnpm install
   ```
2. Development server:
   ```bash
   pnpm dev
   ```
3. Production build:
   ```bash
   pnpm build
   pnpm start
   ```
4. Linting/tests (if configured):
   ```bash
   pnpm lint
   pnpm test
   ```

### Backend
1. Create virtual environment (if not using provided `.venv`):
   ```bash
   python -m venv .venv
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Apply migrations:
   ```bash
   python manage.py migrate
   ```
4. Run development server:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
5. Run unit tests:
   ```bash
   python manage.py test
   ```

## Data Flow
- Frontend services in `lib/api/data-service.ts` communicate with the Django API using `fetch` and JWT Bearer tokens.
- Dashboard statistics and charts expected from endpoints under `/api/dashboard/` (stats, sales, category sales, etc.).
- WebSocket notifications configured via Django Channels (`notifications` app).

## Testing & Verification
- Frontend: manual dashboard checks or E2E tests (Playwright/Cypress if added). Some scripts like `comprehensive_test.py`, `final_system_validation.py` exist for integrated checks.
- Backend: Django `manage.py test` plus custom scripts in repo root for combined validation.

## Notes
- Remove mock data directory from frontend when fully integrated with backend.
- Ensure CORS and authentication settings are aligned between Next.js and Django.
- Media assets stored under `media/` directories; ensure proper storage configuration in production.