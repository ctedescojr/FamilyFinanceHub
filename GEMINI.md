# FamilyFinanceHub Project Context

## Project Overview

**FamilyFinanceHub** is a comprehensive family financial control system designed to manage finances, process invoices via OCR, and optimize shopping routes. It is a full-stack application built with modern technologies and containerized for consistent development and deployment environments.

## Tech Stack & Architecture

### Backend (`/backend`)
*   **Framework:** Django 5.2/6.0 with Django REST Framework (DRF).
*   **Language:** Python 3.13+ (Managed by `uv`).
*   **Database:** PostgreSQL 17+.
*   **Async Tasks:** Celery + Redis.
*   **OCR:** Tesseract.
*   **Admin Interface:** Django Unfold.
*   **Key Libraries:** `django-cors-headers`, `djangorestframework-simplejwt`, `psycopg`.

### Frontend (`/frontend`)
*   **Framework:** React 19+.
*   **Build Tool:** Vite 7+.
*   **Styling:** Tailwind CSS 4+ (configured via `@tailwindcss/vite`).
*   **State Management:** Zustand.
*   **Forms:** React Hook Form.
*   **Charts:** Recharts.

### Infrastructure
*   **Containerization:** Docker & Docker Compose.
*   **Orchestration:** `docker-compose.yml` (Dev) and `docker-compose.prod.yml` (Prod).
*   **Reverse Proxy:** Nginx (Production).

## Domain Logic & Requirements

### Users App (`apps.users`)
The system centers around family financial management. The User model is customized to include:
*   **Personal Info:** First Name, Last Name, Cellphone, E-mail, Job.
*   **Family Role:** Defines the user's position in the family structure.
    *   *Roles:* Father, Mother, Son, Daughter, Grandfather, Grandmother, Uncle, Aunt, Friends, Pets.
*   **Capabilities:** Users can record their own expenses. Future updates will allow recording expenses for other family members.

## Key Files & Directories

*   `docker-compose.yml`: Main entry point for the development environment. Orchestrates `backend`, `frontend`, `db`, `redis`, `celery-worker`, and `celery-beat`.
*   `.env`: **CRITICAL**. Must exist and contain `UID` and `GID` to map host permissions to containers.
*   `backend/`:
    *   `config/`: Main Django configuration (settings, URLs, WSGI/ASGI).
    *   `apps/`: Custom Django apps (`core`, `users`).
    *   `entrypoint.sh`: Handles UID mapping, waiting for DB, and **auto-initializing** the Django project if `manage.py` is missing.
    *   `uv.lock` / `pyproject.toml`: Python dependency definitions.
*   `frontend/`:
    *   `src/`: React source code.
    *   `scripts/entrypoint.sh`: Handles UID mapping and **auto-initializing** the Vite+Tailwind project if `package.json` is missing.
    *   `vite.config.js`: Vite configuration with Tailwind plugin.

## Development Workflow

### 1. Initial Setup
The project relies on strict permission handling. You **must** configure your `.env` file first.

```bash
cp .env.example .env
echo "UID=$(id -u)" >> .env
echo "GID=$(id -g)" >> .env
```

### 2. Running the Environment
Start all services. The first run will trigger the auto-initialization scripts in backend and frontend containers.

```bash
docker-compose up --build
```

*   **Backend API:** `http://localhost:8000`
*   **Frontend:** `http://localhost:5173`

### 3. Common Commands

| Action | Command |
| :--- | :--- |
| **Stop Services** | `docker-compose down` |
| **View Logs** | `docker-compose logs -f [service_name]` |
| **Backend Shell** | `docker-compose exec backend python manage.py shell` |
| **Run Migrations** | `docker-compose exec backend python manage.py migrate` |
| **Create Superuser** | `docker-compose exec backend python manage.py createsuperuser` |
| **Add Python Pkg** | `docker-compose exec backend uv add <package_name>` |
| **Add Node Pkg** | `docker-compose exec frontend npm install <package_name>` |

### 4. Testing
*   **Backend:** `docker-compose exec backend python manage.py test`
*   **Frontend:** `docker-compose exec frontend npm run lint` (Linting)

## Development Conventions

*   **Dependency Management:**
    *   **Backend:** Use `uv`. **Do not** use `pip` directly. Run `uv add` or `uv remove` inside the container to update `pyproject.toml` and `uv.lock`.
    *   **Frontend:** Use `npm`.
*   **Permissions:** The `entrypoint.sh` scripts use `gosu` to match the container user (`appuser` in backend, `node` in frontend) with your host user (`UID`/`GID` from `.env`). This ensures files created inside the container (like migrations or new components) are editable on your host machine.
*   **Code Structure:**
    *   Django apps go into `backend/apps/`.
    *   React components go into `frontend/src/`.
*   **Hot Reloading:** Both Backend (Django runserver) and Frontend (Vite) are configured for hot reloading via Docker volumes.

## Troubleshooting

*   **Permission Errors:** Ensure `UID` and `GID` in `.env` match your host user (`id -u`, `id -g`). Re-build containers if you change these: `docker-compose up --build --force-recreate`.
*   **Database Connection:** The backend waits for the DB to be ready (`wait_for_db` command). Check logs if it hangs.
