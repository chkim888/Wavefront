# Wavefront

A social analytics and experimentation platform for tracking content performance, monitoring audience signals, and running statistically rigorous A/B tests.

Built with FastAPI, React, PostgreSQL, Redis, and Celery.

## Overview

Wavefront is a full-stack SaaS application that combines social-content analytics with experimentation infrastructure. The platform ingests content data from external sources, processes it through asynchronous analytics pipelines, surfaces real-time insights through interactive dashboards, and provides an experimentation framework for measuring feature and content performance.

The project was built to explore the engineering challenges behind analytics platforms, experimentation systems, and real-time data products.

## Architecture

Wavefront follows a service-oriented architecture:

* **FastAPI** handles authentication, experimentation APIs, analytics endpoints, and business logic.
* **PostgreSQL** stores tenant, experiment, event, and analytics data.
* **Redis** provides task queuing and inter-service messaging.
* **Celery** executes asynchronous ingestion and analytics workloads.
* **React** powers the analytics dashboard and experiment management interface.

```text
YouTube API
     │
     ▼
Celery + Redis Workers
     │
     ▼
Sentiment Analysis
     │
     ▼
PostgreSQL
     │
     ├── Analytics APIs
     ├── Experimentation APIs
     └── Real-Time Alerts
              │
              ▼
       React Dashboard
```

## Key Features

### Experimentation Engine

* Deterministic user assignment using MD5 hashing
* Event tracking and conversion measurement
* Chi-squared significance testing
* Confidence interval and lift calculations
* Feature-flag-driven rollouts

### Analytics Pipeline

* Automated YouTube Data API ingestion
* Asynchronous processing with Celery and Redis
* HuggingFace sentiment analysis
* Time-series aggregation
* Engagement spike detection and alerting

### Real-Time Analytics

* Live dashboard updates via WebSockets
* Real-time alert delivery
* Content performance and sentiment monitoring
* 
## Technology Stack

**Backend:** Python, FastAPI, PostgreSQL, Redis, Celery, SQLAlchemy, Alembic

**Frontend:** React, JavaScript, WebSockets

**Infrastructure:** Docker, Docker Compose, Railway

**Machine Learning:** HuggingFace Transformers, RoBERTa Sentiment Models
