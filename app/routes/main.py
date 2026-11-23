import logging

from flask import Blueprint, render_template, request, session, redirect, url_for

from app.models import data_store

logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def dashboard():
    try:
        slices = data_store.list_slices()
    except Exception as exc:
        logger.exception("dashboard: failed to load slices — %s", exc)
        return render_template("errors/500.html"), 500

    if slices is None:
        slices = []

    summaries = []
    for s in slices:
        try:
            summary = data_store.get_slice_summary(s["id"])
        except Exception as exc:
            logger.exception("dashboard: summary error for %s — %s", s["id"], exc)
            summary = {"slice": s, "metric_count": 0}
        if summary is not None:
            summaries.append(summary)

    return render_template("pages/dashboard.html", summaries=summaries, slices=slices)


@main_bp.route("/slices")
def slices_list():
    try:
        slices = data_store.list_slices()
    except Exception as exc:
        logger.exception("slices_list: service error — %s", exc)
        return render_template("errors/500.html"), 500

    if slices is None:
        slices = []

    return render_template("pages/slices.html", slices=slices)


@main_bp.route("/slices/<slice_id>")
def slice_detail(slice_id):
    try:
        s = data_store.get_slice(slice_id)
    except Exception as exc:
        logger.exception("slice_detail: service error — %s", exc)
        return render_template("errors/500.html"), 500

    if s is None:
        return redirect(url_for("main.slices_list"))

    try:
        metrics = data_store.list_metrics(slice_id=slice_id, limit=50)
    except Exception as exc:
        logger.exception("slice_detail: metrics error — %s", exc)
        metrics = []

    try:
        summary = data_store.get_slice_summary(slice_id)
    except Exception as exc:
        logger.exception("slice_detail: summary error — %s", exc)
        summary = None

    return render_template(
        "pages/slice_detail.html", slice=s, metrics=metrics, summary=summary
    )


@main_bp.route("/analytics")
def analytics():
    try:
        slices = data_store.list_slices()
    except Exception as exc:
        logger.exception("analytics: service error — %s", exc)
        return render_template("errors/500.html"), 500

    if slices is None:
        slices = []

    return render_template("pages/analytics.html", slices=slices)


@main_bp.route("/getting-started")
def getting_started():
    return render_template("pages/getting_started.html")


@main_bp.route("/health")
def health():
    return {"status": "ok"}, 200


@main_bp.route("/toggle-theme", methods=["POST"])
def toggle_theme():
    current = session.get("theme", "light")
    session["theme"] = "dark" if current == "light" else "light"
    return {"theme": session["theme"]}, 200
