# Musicalement

A social app for sharing what you are listening to. Once a day, you share the track you are playing on Spotify. Your post disappears from the feed after 24 hours. You can only see your friends' posts if you have posted yourself that day.

Inspired by BeReal, built as a portfolio project to cover Python, React, Docker, EKS, Terraform, and observability end to end.

---

## Stack

| Layer | Technology |
|---|---|
| Backend API | Django 4.2 + Django REST Framework |
| Auth | Spotify OAuth 2.0 + SimpleJWT |
| Background jobs | Celery + Celery Beat |
| Database | PostgreSQL 16 |
| Cache / broker | Redis 7 |
| Frontend | React 18 + Vite + Tailwind CSS |
| Local dev | Docker Compose |
| CI | GitHub Actions (lint → test → build → push ECR) |
| Infra (Phase 2+) | Terraform, EKS, RDS, ElastiCache, ECR |

---

## How it works

### Authentication

Spotify is the only identity provider. There are no passwords.

1. The browser is redirected to `/api/v1/auth/spotify/` which bounces to Spotify's OAuth consent screen.
2. Spotify calls back to `/api/v1/auth/spotify/callback/` with a one-time `code`.
3. The backend exchanges the code for a Spotify `access_token` + `refresh_token`, fetches the user's Spotify profile, and creates or updates the local `User` record.
4. A JWT pair (access + refresh) is issued and the browser is redirected to `/callback?token=...&refresh=...`.
5. The React app stores the tokens in `localStorage` and attaches them to every API request via an Axios interceptor.

Spotify access tokens expire every hour. A Celery Beat task runs every 45 minutes and refreshes tokens for users whose token expires within 10 minutes.

### Posting

1. Search for a track: `GET /api/v1/posts/search-tracks/?q=<query>` returns up to 10 Spotify results.
2. Select one and post it: `POST /api/v1/posts/` with `{"spotify_track_id": "<id>"}`.
3. The backend fetches full track metadata from Spotify, creates the post with `expires_at = now + 24h`, and returns the post data.

### Feed gate

`GET /api/v1/posts/feed/` checks whether the authenticated user has posted today.

- If not → `403 {"detail": "post_required"}`
- If yes → returns all friends' posts where `expires_at > now`, ordered by newest first

Posts older than 24 hours are excluded at query time. They are never deleted — they remain visible on the user's own profile at `GET /api/v1/posts/me/`.

### Social graph

Friend requests use a `Friendship` model with `status: pending | accepted`. Both directions of a friendship are stored as a single row (the sender is `from_user`). Accepting a request flips the status to `accepted`. Either user can delete the friendship at any time.

---

## Prerequisites

- Docker and Docker Compose
- A Spotify developer app ([developer.spotify.com/dashboard](https://developer.spotify.com/dashboard))
  - Add `http://127.0.0.1:8000/api/v1/auth/spotify/callback/` as a Redirect URI (use `127.0.0.1`, not `localhost`)

---

## Local setup

**1. Clone and create your `.env` file**

```bash
cp .env.example .env
```

Fill in the required values:

```env
SECRET_KEY=any-long-random-string

POSTGRES_DB=musicalement
POSTGRES_USER=musicalement
POSTGRES_PASSWORD=musicalement

REDIS_URL=redis://redis:6379/0

SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/api/v1/auth/spotify/callback/

FRONTEND_URL=http://localhost:5173
```

**2. Start the stack**

```bash
make up
```

This builds and starts six services: `db`, `redis`, `web` (Django), `worker` (Celery), `beat` (Celery Beat), and `frontend` (Vite dev server).

**3. Run migrations**

```bash
make migrate
```

**4. Open the app**

- Frontend: [http://localhost:5173](http://localhost:5173)
- Django API: [http://127.0.0.1:8000/api/v1/](http://127.0.0.1:8000/api/v1/)

---

## Makefile reference

| Command | What it does |
|---|---|
| `make up` | Build images and start all services |
| `make down` | Stop and remove containers |
| `make migrate` | Run Django migrations inside the `web` container |
| `make shell` | Open a Django shell inside the `web` container |
| `make test` | Run the backend test suite (pytest) |
| `make logs` | Tail logs for all services |
| `make lint` | Run `ruff` on the backend and `eslint` on the frontend |
| `make build-backend` | Build the production backend image locally |
| `make build-frontend` | Build the production frontend image (nginx) locally |

---

## Running tests

```bash
make test
```

The test suite uses `pytest-django` with `factory_boy` for fixtures. Tests run against a real SQLite database (no mocking). Spotify API calls are mocked with `unittest.mock.patch`.

To run a specific test file:

```bash
docker compose run --rm web pytest apps/posts/tests/test_views.py -v
```

---

## Project structure

```
backend/
  manage.py
  requirements.txt          # production dependencies (incl. gunicorn)
  requirements-dev.txt      # adds pytest, factory-boy, ruff
  ruff.toml                 # linter config
  musicalement/
    settings/
      base.py               # shared settings
      local.py              # dev overrides, reads from .env
    urls.py
    celery.py               # Celery app + Beat schedule
  apps/
    users/                  # User model, Spotify OAuth views
    posts/                  # Post, Like, Comment + Celery tasks
    friendships/            # Friendship model + CRUD

frontend/
  package.json
  vite.config.js            # also configures vitest
  eslint.config.js
  nginx.conf                # SPA catch-all for the production image
  src/
    api/client.js           # Axios instance with JWT interceptor + refresh
    pages/                  # Feed, Publish, Profile, Friends
    components/             # PostCard, Navbar, PrivateRoute
    __tests__/              # vitest tests

.github/
  workflows/
    ci.yml                  # lint → test → build → push ECR
```

---

## API reference

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/auth/spotify/` | - | Redirect to Spotify OAuth |
| GET | `/api/v1/auth/spotify/callback/` | - | OAuth callback, returns JWT |
| POST | `/api/v1/auth/token/refresh/` | - | Refresh JWT |
| GET | `/api/v1/users/me/` | JWT | Current user profile |
| GET | `/api/v1/users/?search=` | JWT | Search users by username |
| GET | `/api/v1/posts/search-tracks/?q=` | JWT | Search Spotify tracks |
| POST | `/api/v1/posts/` | JWT | Create a post (`{"spotify_track_id": "..."}`) |
| GET | `/api/v1/posts/feed/` | JWT | Friend feed (gated — must have posted today) |
| GET | `/api/v1/posts/me/` | JWT | Own post history |
| DELETE | `/api/v1/posts/{id}/` | JWT | Delete own post |
| POST | `/api/v1/posts/{id}/like/` | JWT | Toggle like |
| GET | `/api/v1/posts/{id}/comments/` | JWT | List comments |
| POST | `/api/v1/posts/{id}/comments/` | JWT | Add a comment |
| DELETE | `/api/v1/posts/{id}/comments/{cid}/` | JWT | Delete own comment |
| GET | `/api/v1/friendships/` | JWT | List friends and pending requests |
| POST | `/api/v1/friendships/` | JWT | Send a friend request |
| PATCH | `/api/v1/friendships/{id}/` | JWT | Accept or reject a request |
| DELETE | `/api/v1/friendships/{id}/` | JWT | Remove a friend |

---

## CI pipeline

Every push and pull request runs four jobs in parallel:

- **lint-backend** — `ruff check` on `backend/`
- **lint-frontend** — `eslint` on `frontend/src/`
- **test-backend** — `pytest` with real Postgres and Redis service containers
- **test-frontend** — `vitest run`

On merge to `main`, a fifth job (`build-and-push`) builds the production images and pushes them to ECR with the commit SHA and `latest` tags. It authenticates to AWS via OIDC — no long-lived credentials are stored in the repo. This job requires the `AWS_ROLE_ARN` secret and the ECR repositories to exist (created in Phase 2).

---

## Dockerfiles

Both Dockerfiles are multi-stage.

**Backend** (`backend/Dockerfile`): a `builder` stage installs all dependencies into a virtualenv; the `runtime` stage copies only the venv and source code and runs `gunicorn`. Dev tools are not present in the production image.

**Frontend** (`frontend/Dockerfile`): a `base` stage installs npm dependencies; the `dev` stage is used by Docker Compose (Vite dev server); the `builder` stage runs `npm run build`; the `runtime` stage is nginx serving the static output with a catch-all SPA rule.

Docker Compose targets the `dev` stage for the frontend service so the Vite dev server is used locally.
