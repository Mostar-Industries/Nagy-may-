# Implement full screen map

*Automatically synced with your [v0.dev](https://v0.dev) deployments*

[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)](https://vercel.com/mo-101s-projects/v0-implement-full-screen-map)
[![Built with v0](https://img.shields.io/badge/Built%20with-v0.dev-black?style=for-the-badge)](https://v0.dev/chat/projects/B86pyx5uIUD)

## Overview

This repository will stay in sync with your deployed chats on [v0.dev](https://v0.dev).
Any changes you make to your deployed app will be automatically pushed to this repository from [v0.dev](https://v0.dev).

## Deployment

Your project is live at:

**[https://vercel.com/mo-101s-projects/v0-implement-full-screen-map](https://vercel.com/mo-101s-projects/v0-implement-full-screen-map)**

## Build your app

Continue building your app on:

**[https://v0.dev/chat/projects/B86pyx5uIUD](https://v0.dev/chat/projects/B86pyx5uIUD)**

## How It Works

1. Create and modify your project using [v0.dev](https://v0.dev)
2. Deploy your chats from the v0 interface
3. Changes are automatically pushed to this repository
4. Vercel deploys the latest version from this repository

## Running the project locally

### Backend

The Flask backend lives in the `backend/` folder. You can start it using the built
in development server:

```bash
python -m app
```

For production style execution use the provided start script which launches
Gunicorn:

```bash
./backend/start.sh
```

### Required environment variables

The backend expects several environment variables to be configured:

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | Connection string for the Postgres database used by SQLAlchemy. |
| `FIREBASE_CREDENTIALS` | Path or JSON credentials for Firebase Admin SDK. |
| `JWT_SECRET_KEY` | Secret used to sign JWT tokens. |
| `DEEPSEEK_API_KEY` | API key for the DeepSeek integration. |

### Frontend

The Next.js frontend is located at the repository root. Launch it in development
mode with:

```bash
pnpm dev
```

### Tests

Unit tests for the backend reside in `backend/tests`. Run them with:

```bash
pytest backend/tests
```
