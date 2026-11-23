import os
import json
import logging
import time

logger = logging.getLogger(__name__)

_DATA_DIR = None
_SLICES_FILE = None
_METRICS_FILE = None


def init_data_store(data_dir):
    """Initialize the data store paths and seed default data."""
    global _DATA_DIR, _SLICES_FILE, _METRICS_FILE
    _DATA_DIR = os.path.abspath(data_dir)
    _SLICES_FILE = os.path.join(_DATA_DIR, "slices.json")
    _METRICS_FILE = os.path.join(_DATA_DIR, "metrics.json")
    os.makedirs(_DATA_DIR, exist_ok=True)
    _seed_defaults()


def _seed_defaults():
    """Idempotent seed — only writes if files do not exist."""
    if not os.path.exists(_SLICES_FILE):
        default_slices = [
            {
                "id": "slice-embb-001",
                "name": "eMBB Urban Core",
                "type": "eMBB",
                "status": "active",
                "sla_latency_ms": 20,
                "sla_throughput_mbps": 100,
                "sla_availability_pct": 99.9,
                "description": "Enhanced Mobile Broadband slice for urban high-density areas.",
            },
            {
                "id": "slice-urllc-001",
                "name": "URLLC Factory Floor",
                "type": "URLLC",
                "status": "active",
                "sla_latency_ms": 1,
                "sla_throughput_mbps": 50,
                "sla_availability_pct": 99.999,
                "description": "Ultra-Reliable Low-Latency slice for industrial automation.",
            },
            {
                "id": "slice-mmtc-001",
                "name": "mMTC Smart Grid",
                "type": "mMTC",
                "status": "active",
                "sla_latency_ms": 100,
                "sla_throughput_mbps": 10,
                "sla_availability_pct": 99.5,
                "description": "Massive Machine-Type Communications slice for IoT sensors.",
            },
        ]
        _write_json(_SLICES_FILE, default_slices)
        logger.info("Seeded default slices data.")

    if not os.path.exists(_METRICS_FILE):
        _write_json(_METRICS_FILE, [])
        logger.info("Seeded empty metrics file.")


def _read_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _write_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


# ── Slice CRUD ───────────────────────────────────────────────────────

def list_slices():
    return _read_json(_SLICES_FILE)


def get_slice(slice_id):
    for s in list_slices():
        if s["id"] == slice_id:
            return s
    return None


def create_slice(data):
    slices = list_slices()
    new_id = f"slice-{data.get('type', 'custom').lower()}-{int(time.time())}"
    record = {
        "id": new_id,
        "name": data.get("name", "Unnamed Slice"),
        "type": data.get("type", "custom"),
        "status": data.get("status", "active"),
        "sla_latency_ms": data.get("sla_latency_ms", 10),
        "sla_throughput_mbps": data.get("sla_throughput_mbps", 50),
        "sla_availability_pct": data.get("sla_availability_pct", 99.9),
        "description": data.get("description", ""),
    }
    slices.append(record)
    _write_json(_SLICES_FILE, slices)
    return record


def update_slice(slice_id, data):
    slices = list_slices()
    for i, s in enumerate(slices):
        if s["id"] == slice_id:
            for key in ("name", "type", "status", "sla_latency_ms",
                        "sla_throughput_mbps", "sla_availability_pct", "description"):
                if key in data:
                    slices[i][key] = data[key]
            _write_json(_SLICES_FILE, slices)
            return slices[i]
    return None


def delete_slice(slice_id):
    slices = list_slices()
    new_slices = [s for s in slices if s["id"] != slice_id]
    if len(new_slices) == len(slices):
        return False
    _write_json(_SLICES_FILE, new_slices)
    return True


# ── Metrics ──────────────────────────────────────────────────────────

def list_metrics(slice_id=None, limit=100):
    metrics = _read_json(_METRICS_FILE)
    if slice_id:
        metrics = [m for m in metrics if m.get("slice_id") == slice_id]
    return sorted(metrics, key=lambda m: m.get("timestamp", 0), reverse=True)[:limit]


def add_metric(data):
    metrics = _read_json(_METRICS_FILE)
    record = {
        "id": f"metric-{int(time.time() * 1000)}",
        "slice_id": data["slice_id"],
        "timestamp": data.get("timestamp", time.time()),
        "latency_ms": data.get("latency_ms", 0),
        "throughput_mbps": data.get("throughput_mbps", 0),
        "packet_loss_pct": data.get("packet_loss_pct", 0),
        "jitter_ms": data.get("jitter_ms", 0),
        "active_connections": data.get("active_connections", 0),
    }
    metrics.append(record)
    # Keep last 10000 entries
    if len(metrics) > 10000:
        metrics = metrics[-10000:]
    _write_json(_METRICS_FILE, metrics)
    return record


def get_slice_summary(slice_id):
    """Compute summary statistics for a given slice."""
    metrics = list_metrics(slice_id=slice_id, limit=100)
    s = get_slice(slice_id)
    if not s:
        return None
    if not metrics:
        return {
            "slice": s,
            "metric_count": 0,
            "avg_latency_ms": None,
            "avg_throughput_mbps": None,
            "avg_packet_loss_pct": None,
            "sla_latency_ok": None,
            "sla_throughput_ok": None,
        }
    avg_lat = sum(m["latency_ms"] for m in metrics) / len(metrics)
    avg_tp = sum(m["throughput_mbps"] for m in metrics) / len(metrics)
    avg_pl = sum(m["packet_loss_pct"] for m in metrics) / len(metrics)
    return {
        "slice": s,
        "metric_count": len(metrics),
        "avg_latency_ms": round(avg_lat, 2),
        "avg_throughput_mbps": round(avg_tp, 2),
        "avg_packet_loss_pct": round(avg_pl, 4),
        "sla_latency_ok": avg_lat <= s["sla_latency_ms"],
        "sla_throughput_ok": avg_tp >= s["sla_throughput_mbps"],
    }
