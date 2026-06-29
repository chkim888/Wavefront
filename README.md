# Wavefront

Wavefront is a full-stack, interactive A/B testing and social intelligence SaaS platform built for marketing and growth teams to make informed, data-driven decisions. At its core, it helps teams answer two questions: 
1. _What are people saying about our product online right now?_
2. _Which version of our software feature actually drives more engagement?_
    
Teams can use Wavefront to track real-time audience sentiment across social media platforms, run statistically rigorous A/B tests on their product features, and get instant alerts when public interest spikes so they can act on momentum. 

**_Demo video: (link coming soon)_**

<br>

<p align="center">
    <kbd>
        <img width=95% alt="wavefront-gif" src="https://github.com/user-attachments/assets/07c45c27-f74e-464d-8d7b-838c67d2fa72" />
    </kbd>
</p>

---

## Motivation

Storytelling shapes our perception of ourselves, other people, and the world around us — is what I realized as I began my career and started establishing my own professional brand. Because marketing is how brands tell their stories, I wanted to understand how data-driven marketing decisions get made for SaaS products, while solidifying my background in building complex backend systems. That is why I built Wavefront.


## Core Features

- **Buzz Monitoring** — Track real-time sentiment around any topic across social media
- **Sentiment Analysis** — Using LLM (HuggingFace NLP pipeline), identify sentiments behind the online posts and classify them as positive, neutral, or negative
- **A/B Testing Engine** — Utilize deterministic MD5-based variant assignment with chi-squared statistical significance testing (winner declared at ≥95% confidence) to determine which feature draws maximum engagement
- **Live Alerts** — WebSocket-powered real-time feed fires when post volume spikes beyond the rolling z-score baseline
- **Analytics Dashboard** — Display sentiment breakdown, sentiment over time, and experiment conversion rate charts


## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS v4, Recharts, React Router v6 |
| Backend | FastAPI, SQLAlchemy, PostgreSQL, Alembic, JWT auth |
| Async Pipeline | Celery, Redis, Celery Beat |
| NLP | HuggingFace Transformers (cardiffnlp/twitter-roberta-base-sentiment-latest) |
| External APIs | YouTube Data API v3 |
| Deployment | Railway (backend + frontend + Postgres + Redis + Celery) |


## Architecture Overview

Wavefront runs four services in production: a FastAPI HTTP server, a Celery worker for async ingestion and NLP, Celery Beat for scheduled ingestion, and a React frontend. Redis serves as both the Celery broker and the Pub/Sub channel for WebSocket alert delivery.

#### **Data flow:**
1. Celery Beat triggers ingestion hourly per active topic
2. Worker fetches videos and comments from YouTube Data API v3
3. HuggingFace RoBERTa scores each post for sentiment (positive / neutral / negative)
4. Spike detection computes z-scores against rolling volume baseline & alerts published to Redis Pub/Sub on spike
5. FastAPI lifespan task subscribes to Redis and broadcasts alerts to connected WebSocket clients in real time


**_Full system design document coming soon!_**


## Future Work

- **Production-scale ingestion** — swap Celery Beat for Kafka to handle higher-volume, multi-platform data streams without quota ceiling constraints
- **Multi-platform support** — extend ingestion beyond YouTube to Reddit, X/Twitter, and TikTok
- **Deployed sentiment inference** — move RoBERTa scoring into the deployed Celery pipeline (currently running locally) using a lightweight CPU-optimized model
- **Real load testing** — rerun Locust against the deployed Railway instance under realistic concurrent load
- **CI/CD pipeline** — automated testing and deployment on push to main via GitHub Actions
- **Expanded A/B testing** — multi-variant experiments (beyond binary control/treatment), sequential testing, and automatic stopping rules

---

## Local Setup

**Prerequisites:** Python 3.12, Node.js 22+, Docker

1. Clone the repo

    ```bash
    git clone https://github.com/chkim888/Wavefront/
    cd wavefront
    ```

2. Start Postgres and Redis

    ```bash
    docker-compose up -d
    ```

3. Backend setup

    ```bash
    cd backend
    python -m venv venv
    venv\Scripts\activate  # Windows
    pip install -r requirements.txt
    ```

    Create a `.env` file in `backend/` with:

    ```env
    POSTGRES_DB=wavefront
    POSTGRES_USER=your_user
    POSTGRES_PASSWORD=your_password
    DATABASE_URL=postgresql://your_user:your_password@localhost:5432/wavefront
    SECRET_KEY=your_secret_key
    JWT_ALGORITHM=HS256
    JWT_EXPIRY_MINUTES=60
    YOUTUBE_API_KEY=your_youtube_api_key
    REDIS_URL=redis://localhost:6379
    ```

    Run migrations:

    ```bash
    alembic upgrade head
    ```

    Start the API:

    ```bash
    uvicorn app.main:app --reload
    ```

4. Start Celery worker and Beat (separate terminals)

    ```bash
    celery -A app.workers.celery_app worker --loglevel=info
    celery -A app.workers.celery_app beat --loglevel=info
    ```

5. Frontend setup

    ```bash
    cd frontend
    npm install
    ```

    Create a `.env` file in `frontend/` with:

    ```env
    VITE_WS_URL=ws://localhost:8000
    VITE_API_URL=http://localhost:8000
    ```

    Start the dev server:

    ```bash
    npm run dev
    ```

6. Open `http://localhost:5173` and register an account on Wavefront.
