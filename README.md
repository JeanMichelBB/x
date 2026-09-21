# X

A X-like app built with React, Vite, TypeScript, FastAPI, and MySQL. Users can post tweets, follow others, send direct messages, and more. Live at [x.sacenpapier.org](https://x.sacenpapier.org).

![image](header.png)

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [Folder Structure](#folder-structure)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Personal Information](#personal-information)

## Features

- User authentication and authorization (JWT)
- Tweet creation, deletion, liking, retweets, and comments
- GIF picker for tweets/messages
- Bookmarks and Lists
- Follow and unfollow users, profile pages
- Notifications
- Send and receive direct messages
- Search / Explore
- Cookie consent banner and legal footer
- Auto-login as a seeded demo user on the public deployment (no real accounts — see `frontend/src/App.tsx`)
- Responsive design for mobile and desktop

## Tech Stack

- **Frontend**: React, Vite, TypeScript, Nginx (port 3000)
- **Backend**: FastAPI, Uvicorn (port 8000), OpenTelemetry tracing + Prometheus metrics
- **Database**: MySQL 8 (shared instance, see [Deployment](#deployment))
- **Deployment**: Docker, k3s (Kubernetes) via Kustomize, Argo CD + Argo CD Image Updater, Doppler (secrets), Traefik, Cloudflare
- **CI/CD**: GitHub Actions, Trivy vulnerability gate

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/en/download/)
- [Python 3.10+](https://www.python.org/downloads/)
- [MySQL](https://dev.mysql.com/downloads/mysql/)
- [Docker](https://www.docker.com/products/docker-desktop)

### Installation

1. **Clone the repository:**

```bash
git clone https://github.com/JeanMichelBB/x.git
cd x
```

2. **Backend Setup:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory (see [Environment Variables](#environment-variables)).

Start the FastAPI server:

```bash
uvicorn main:app --reload --port 8000
```

3. **Frontend Setup:**

```bash
cd frontend
npm install
npm run dev
```

Optional: `backend/dev.sh` installs and starts a local MySQL via Homebrew and sets the root password from `.env` — useful if you don't already have MySQL running.

### Running the Application

| Service  | URL                    |
|----------|------------------------|
| Backend  | http://localhost:8000  |
| Frontend | http://localhost:3000  |
| API Docs | http://localhost:8000/docs |

### Tests

```bash
cd backend
pytest
```

## Folder Structure

```
x/
│
├── backend/
│   ├── app/
│   │   ├── auth.py            # JWT authentication
│   │   ├── database.py        # DB connection & session
│   │   ├── bookmarks.py       # Bookmark routes
│   │   ├── comments.py        # Tweet comment routes
│   │   ├── followers.py       # Follow/unfollow routes
│   │   ├── gifs.py            # GIF picker routes
│   │   ├── lists.py           # Lists routes
│   │   ├── messages.py        # Direct messages routes
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── notifications.py   # Notifications routes
│   │   ├── profile.py         # Profile routes
│   │   ├── search.py          # Search/explore routes
│   │   ├── seed.py            # Seed data (fictive demo users)
│   │   ├── settings.py        # User settings routes
│   │   ├── tracing.py         # OpenTelemetry setup (no-op unless TAILSCALE_IP_TSPI is set)
│   │   ├── tweets.py          # Tweet routes
│   │   └── user.py            # User/signup routes
│   ├── tests/                 # pytest test suite
│   ├── main.py                # FastAPI entry point
│   ├── dev.sh                 # Local MySQL bootstrap for dev
│   ├── requirements.txt       # Python dependencies
│   └── dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/        # React components (GifPicker, CookieBanner, Header, TweetList, ...)
│   │   ├── pages/              # React pages (Home, Profile, Messages, Bookmarks, Lists, Explore, Settings, ...)
│   │   ├── api.tsx             # API service layer
│   │   └── App.tsx             # Main App component (incl. demo auto-login)
│   ├── default.conf           # Nginx config (port 3000)
│   ├── vite.config.ts
│   └── dockerfile
│
├── k3s/
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── ingress.yaml
│   ├── networkpolicy.yaml     # NetworkPolicies restricting pod-to-pod traffic
│   ├── doppler-secret.yaml    # Doppler-managed secret sync (replaces manual secret in prod)
│   ├── image-updater.yaml     # Argo CD Image Updater config (auto-bumps image tags)
│   ├── kustomization.yaml     # Kustomize entrypoint for the manifests above
│   └── secrets/
│       └── x-backend-secret.yml   # Fallback/manual secret for non-Doppler setups
│
├── docs/
│   └── superpowers/plans/     # Planning docs for past feature work
│
└── .github/
    └── workflows/
        └── deploy.yml         # CI: build images, Trivy CRITICAL-vuln gate, push to Docker Hub
```

## Environment Variables

Create a `.env` file in `backend/`:

```env
MYSQL_DB=localhost
MYSQL_USER=app
MYSQL_PASSWORD=your_password
MYSQL_ROOT_PASSWORD=your_root_password
SECRET_KEY=your_jwt_secret_key
```

For the frontend, set in `.env` or as a Docker build arg:

```env
VITE_API_URL=https://xapi.sacenpapier.org
```

Optional, backend: `TAILSCALE_IP_TSPI` — if set, enables OpenTelemetry tracing export to that address on port 4317; tracing is a no-op locally when unset.

## Deployment

### Docker (local)

Build and run each service individually:

```bash
# Backend
docker build -t twc-backend ./backend
docker run -p 8000:8000 --env-file backend/.env twc-backend

# Frontend
docker build --build-arg VITE_API_URL=http://localhost:8000 -t twc-frontend ./frontend
docker run -p 3000:3000 twc-frontend
```

### k3s (production)

Database: see [`shared-mysql`](https://github.com/JeanMichelBB/shared-mysql) — this app connects to that instance's `twitter_db` database, it doesn't run its own.

Manifests are managed with Kustomize and deployed via Argo CD (GitOps) rather than applied by hand. Secrets come from Doppler (`k3s/doppler-secret.yaml`); `k3s/secrets/x-backend-secret.yml` is a manual fallback for non-Doppler setups. To deploy without Argo CD:

```bash
kubectl apply -k k3s/
```

`NetworkPolicies` (`k3s/networkpolicy.yaml`) restrict pod-to-pod traffic: only Traefik can reach the frontend on port 3000; the backend's port 8000 is left open (it's shared with Prometheus metrics scraping — see the comment in that file for why it isn't scoped further).

The app is exposed via Traefik + Cloudflare at:

| Service  | URL                                    |
|----------|----------------------------------------|
| Frontend | https://x.sacenpapier.org   |
| Backend  | https://xapi.sacenpapier.org |

### CI/CD

Pushing to `main` (touching `frontend/`, `backend/`, or the workflow itself) triggers GitHub Actions (`.github/workflows/deploy.yml`), which for each of frontend and backend:
1. Builds an `amd64` image and scans it with Trivy, failing the job on any CRITICAL fixable vulnerability
2. On success, builds and pushes multi-arch (`amd64`/`arm64`) images to Docker Hub tagged `latest` and the commit SHA

Required GitHub secrets: `DOCKER_USERNAME`, `DOCKER_PASSWORD`, `VITE_API_URL`.

Rollout to k3s is not done by the workflow — Argo CD Image Updater (`k3s/image-updater.yaml`) watches Docker Hub for new SHA-tagged images and writes the new tag back into `k3s/kustomization.yaml`, which Argo CD then syncs to the cluster.

## Personal Information

- [LinkedIn](http://linkedin.com/in/jeanmichelbb/)
- [Portfolio](https://jeanmichelbb.github.io/)
