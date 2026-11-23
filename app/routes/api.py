import logging

from flask import Blueprint, request, jsonify

from app.models import data_store
from app.services import kindo_agent

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)


# ── Slices CRUD ──────────────────────────────────────────────────────

@api_bp.route("/slices", methods=["GET"])
def api_list_slices():
    try:
        slices = data_store.list_slices()
    except Exception as exc:
        logger.exception("api_list_slices: error — %s", exc)
        return jsonify({"error": "Failed to list slices", "detail": str(exc)}), 500

    if slices is None:
        slices = []
    return jsonify(slices)


@api_bp.route("/slices", methods=["POST"])
def api_create_slice():
    data = request.get_json(silent=True)
    if not data or not data.get("name"):
        return jsonify({"error": "Missing required field: name"}), 400

    try:
        record = data_store.create_slice(data)
    except Exception as exc:
        logger.exception("api_create_slice: error — %s", exc)
        return jsonify({"error": "Failed to create slice", "detail": str(exc)}), 500

    if record is None:
        return jsonify({"error": "Failed to create slice"}), 500
    return jsonify(record), 201


@api_bp.route("/slices/<slice_id>", methods=["GET"])
def api_get_slice(slice_id):
    try:
        s = data_store.get_slice(slice_id)
    except Exception as exc:
        logger.exception("api_get_slice: error — %s", exc)
        return jsonify({"error": "Failed to get slice", "detail": str(exc)}), 500

    if s is None:
        return jsonify({"error": "Slice not found"}), 404
    return jsonify(s)


@api_bp.route("/slices/<slice_id>", methods=["PUT"])
def api_update_slice(slice_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        updated = data_store.update_slice(slice_id, data)
    except Exception as exc:
        logger.exception("api_update_slice: error — %s", exc)
        return jsonify({"error": "Failed to update slice", "detail": str(exc)}), 500

    if updated is None:
        return jsonify({"error": "Slice not found"}), 404
    return jsonify(updated)


@api_bp.route("/slices/<slice_id>", methods=["DELETE"])
def api_delete_slice(slice_id):
    try:
        deleted = data_store.delete_slice(slice_id)
    except Exception as exc:
        logger.exception("api_delete_slice: error — %s", exc)
        return jsonify({"error": "Failed to delete slice", "detail": str(exc)}), 500

    if not deleted:
        return jsonify({"error": "Slice not found"}), 404
    return jsonify({"ok": True})


# ── Metrics ──────────────────────────────────────────────────────────

@api_bp.route("/metrics", methods=["GET"])
def api_list_metrics():
    slice_id = request.args.get("slice_id")
    limit = request.args.get("limit", 100, type=int)
    try:
        metrics = data_store.list_metrics(slice_id=slice_id, limit=limit)
    except Exception as exc:
        logger.exception("api_list_metrics: error — %s", exc)
        return jsonify({"error": "Failed to list metrics", "detail": str(exc)}), 500

    if metrics is None:
        metrics = []
    return jsonify(metrics)


@api_bp.route("/metrics", methods=["POST"])
def api_add_metric():
    data = request.get_json(silent=True)
    if not data or not data.get("slice_id"):
        return jsonify({"error": "Missing required field: slice_id"}), 400

    try:
        record = data_store.add_metric(data)
    except Exception as exc:
        logger.exception("api_add_metric: error — %s", exc)
        return jsonify({"error": "Failed to add metric", "detail": str(exc)}), 500

    if record is None:
        return jsonify({"error": "Failed to add metric"}), 500
    return jsonify(record), 201


# ── Analysis ─────────────────────────────────────────────────────────

@api_bp.route("/slices/<slice_id>/analyze", methods=["POST"])
def api_analyze_slice(slice_id):
    try:
        summary = data_store.get_slice_summary(slice_id)
    except Exception as exc:
        logger.exception("api_analyze_slice: summary error — %s", exc)
        return jsonify({"error": "Failed to get slice summary", "detail": str(exc)}), 500

    if summary is None:
        return jsonify({"error": "Slice not found"}), 404

    try:
        metrics = data_store.list_metrics(slice_id=slice_id, limit=50)
    except Exception as exc:
        logger.exception("api_analyze_slice: metrics error — %s", exc)
        metrics = []

    try:
        analysis = kindo_agent.analyze_slice_performance(summary, metrics)
    except Exception as exc:
        logger.exception("api_analyze_slice: agent error — %s", exc)
        return jsonify({"error": "Analysis failed", "detail": str(exc)}), 500

    if analysis is None:
        return jsonify({"error": "Analysis returned no results"}), 500
    return jsonify(analysis)


# ── Slice summary ────────────────────────────────────────────────────

@api_bp.route("/slices/<slice_id>/summary", methods=["GET"])
def api_slice_summary(slice_id):
    try:
        summary = data_store.get_slice_summary(slice_id)
    except Exception as exc:
        logger.exception("api_slice_summary: error — %s", exc)
        return jsonify({"error": "Failed to get summary", "detail": str(exc)}), 500

    if summary is None:
        return jsonify({"error": "Slice not found"}), 404
    return jsonify(summary)
