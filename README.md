# 5G Network Slice Performance Monitor

A Flask web application for monitoring and analyzing 5G network slice performance metrics against SLA targets. Features an integrated AI agent for health assessments and actionable recommendations.

## Features

- **Dashboard** — Real-time overview of all network slices with SLA compliance status
- **Slice Management** — Create, edit, and delete 5G network slices (eMBB, URLLC, mMTC)
- **Metrics Collection** — Submit and track latency, throughput, packet loss, and jitter
- **AI-Powered Analysis** — Health scoring and recommendations via Kindo AI agent
- **Analytics** — Performance trend visualization per slice
- **Light/Dark Theme** — Persistent theme preference
- **Getting Started Guide** — Step-by-step onboarding for new users

## Quick Start

### Docker (recommended)

```bash
cp .env.example .env
docker compose up --build
```

Open [http://localhost:8000](http://localhost:8000)

### Local Development

```bash
pip install -r requirements.txt
python -m flask --app wsgi:app run --port 8000
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/slices` | List all slices |
| POST | `/api/slices` | Create a slice |
| GET | `/api/slices/<id>` | Get a slice |
| PUT | `/api/slices/<id>` | Update a slice |
| DELETE | `/api/slices/<id>` | Delete a slice |
| GET | `/api/metrics` | List metrics (optional `?slice_id=` filter) |
| POST | `/api/metrics` | Submit a metric |
| POST | `/api/slices/<id>/analyze` | Run AI analysis on a slice |
| GET | `/api/slices/<id>/summary` | Get slice summary statistics |
| GET | `/health` | Health check |

## AI Agent

The Slice Performance Agent analyzes metrics and provides health scores. See `agent/` directory for configuration. Set `KINDO_API_KEY` and `KINDO_SLICE_PERFORMANCE_AGENT_ID` to enable.

## Built With

- [Flask](https://flask.palletsprojects.com/) — Web framework
- [Gunicorn](https://gunicorn.org/) — WSGI server
- [Kindo](https://kindo.ai/) — AI agent platform
- [KinHelm](https://kinhelm.com/) — Studio platform

## License

Proprietary — All rights reserved.
