import os
import json
import logging

import requests

logger = logging.getLogger(__name__)


def analyze_slice_performance(slice_summary, recent_metrics):
    """Call the Kindo Slice Performance Agent to analyze metrics.

    Falls back to a local heuristic when the agent is not configured.
    """
    api_key = os.environ.get("KINDO_API_KEY", "")
    agent_id = os.environ.get("KINDO_SLICE_PERFORMANCE_AGENT_ID", "")

    payload = {
        "slice": slice_summary.get("slice", {}),
        "metric_count": slice_summary.get("metric_count", 0),
        "avg_latency_ms": slice_summary.get("avg_latency_ms"),
        "avg_throughput_mbps": slice_summary.get("avg_throughput_mbps"),
        "avg_packet_loss_pct": slice_summary.get("avg_packet_loss_pct"),
        "sla_latency_ok": slice_summary.get("sla_latency_ok"),
        "sla_throughput_ok": slice_summary.get("sla_throughput_ok"),
        "recent_metrics": recent_metrics[:20],
    }

    if api_key and agent_id:
        try:
            return _call_kindo_agent(api_key, agent_id, payload)
        except Exception as exc:
            logger.exception("Kindo agent call failed — %s", exc)
            # Fall through to local fallback

    return _local_fallback(payload)


def _call_kindo_agent(api_key, agent_id, payload):
    """Call the Kindo chat completions API."""
    resp = requests.post(
        "https://api.kindo.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": agent_id,
            "messages": [
                {
                    "role": "user",
                    "content": json.dumps(payload),
                }
            ],
        },
        timeout=30,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]

    # Try to parse JSON response from the agent
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "health_score": None,
            "assessment": content,
            "recommendations": [],
            "alerts": [],
        }


def _local_fallback(payload):
    """Generate a basic analysis without calling an external agent."""
    alerts = []
    recommendations = []
    health_score = 100

    sla_lat = payload["slice"].get("sla_latency_ms", 10)
    sla_tp = payload["slice"].get("sla_throughput_mbps", 50)
    avg_lat = payload.get("avg_latency_ms")
    avg_tp = payload.get("avg_throughput_mbps")
    avg_pl = payload.get("avg_packet_loss_pct")

    if avg_lat is not None and avg_lat > sla_lat:
        pct_over = ((avg_lat - sla_lat) / sla_lat) * 100
        health_score -= min(30, pct_over)
        alerts.append({
            "severity": "high" if pct_over > 50 else "medium",
            "message": f"Average latency ({avg_lat:.1f} ms) exceeds SLA target ({sla_lat} ms) by {pct_over:.0f}%.",
        })
        recommendations.append("Investigate network path congestion and consider traffic re-routing.")

    if avg_tp is not None and avg_tp < sla_tp:
        pct_under = ((sla_tp - avg_tp) / sla_tp) * 100
        health_score -= min(30, pct_under)
        alerts.append({
            "severity": "high" if pct_under > 50 else "medium",
            "message": f"Average throughput ({avg_tp:.1f} Mbps) is below SLA target ({sla_tp} Mbps) by {pct_under:.0f}%.",
        })
        recommendations.append("Review resource allocation and consider scaling slice bandwidth.")

    if avg_pl is not None and avg_pl > 1.0:
        health_score -= min(20, avg_pl * 5)
        alerts.append({
            "severity": "high" if avg_pl > 5 else "medium",
            "message": f"Packet loss ({avg_pl:.2f}%) is above acceptable threshold.",
        })
        recommendations.append("Check physical layer integrity and antenna alignment.")

    if payload.get("metric_count", 0) == 0:
        alerts.append({
            "severity": "info",
            "message": "No metrics collected yet. Analysis is based on configuration only.",
        })
        health_score = None

    if not alerts:
        alerts.append({
            "severity": "info",
            "message": "All metrics are within SLA targets. Slice is healthy.",
        })

    if not recommendations:
        recommendations.append("Continue monitoring. No action needed at this time.")

    return {
        "health_score": max(0, round(health_score)) if health_score is not None else None,
        "assessment": _build_assessment(payload, health_score),
        "recommendations": recommendations,
        "alerts": alerts,
    }


def _build_assessment(payload, health_score):
    slice_name = payload["slice"].get("name", "Unknown")
    slice_type = payload["slice"].get("type", "Unknown")
    if health_score is None:
        return f"{slice_name} ({slice_type}): No metrics data available for assessment."
    if health_score >= 90:
        return f"{slice_name} ({slice_type}): Excellent performance. All SLA targets are being met."
    if health_score >= 70:
        return f"{slice_name} ({slice_type}): Acceptable performance with minor degradation. Monitor closely."
    if health_score >= 50:
        return f"{slice_name} ({slice_type}): Performance degradation detected. Immediate attention recommended."
    return f"{slice_name} ({slice_type}): Critical performance issues. SLA violations detected."
