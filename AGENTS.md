# AGENTS.md — 5G Network Slice Performance Monitor

This repository is managed by the KinHelm Studio agent.

## Agent Configuration

Agent configuration files live in the `agent/` directory:

```
agent/
├── agent-config.yaml              # Index of all agents
└── agents/
    └── slice-performance.yaml     # Slice Performance Agent config
```

## Agents

### Slice Performance Agent

- **Config file:** `agent/agents/slice-performance.yaml`
- **Env var:** `KINDO_SLICE_PERFORMANCE_AGENT_ID`
- **Called by:** `app/services/kindo_agent.py` → `analyze_slice_performance()`
- **Purpose:** Analyzes 5G network slice performance metrics against SLA targets and returns a health score, alerts, and actionable recommendations.

## Project Structure

```
├── app/
│   ├── __init__.py                # Flask app factory
│   ├── models/
│   │   └── data_store.py          # JSON file data store (slices, metrics)
│   ├── routes/
│   │   ├── main.py                # Page routes (dashboard, slices, analytics)
│   │   └── api.py                 # REST API endpoints
│   ├── services/
│   │   └── kindo_agent.py         # Kindo AI agent integration
│   ├── static/
│   │   ├── css/style.css          # Stylesheet
│   │   └── js/app.js              # Client-side JavaScript
│   └── templates/
│       ├── layouts/base.html      # Base template with nav and theme
│       ├── pages/                 # Page templates
│       └── errors/                # Error templates
├── agent/                         # Kindo agent config files
├── wsgi.py                        # WSGI entry point
├── gunicorn.conf.py               # Gunicorn configuration
├── Dockerfile                     # Container image
├── docker-compose.yml             # Docker Compose stack
├── requirements.txt               # Python dependencies
└── .env.example                   # Environment variable template
```
