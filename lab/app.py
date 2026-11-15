"""SQLShield Phase 3: localhost-only SQLi comparison and evidence dashboard.

The vulnerable mode is intentionally unsafe. NEVER publicly host this app.
"""
import csv
import io
import os
from pathlib import Path

from flask import Flask, Response, abort, jsonify, render_template, request

from .auth import authenticate
from .db import DEFAULT_DATABASE, initialize_database
from .events import event_statistics, initialize_events, recent_events, record_comparison


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        LAB_DATABASE=os.environ.get("SQLSHIELD_DB_PATH", str(DEFAULT_DATABASE)),
        MAX_CONTENT_LENGTH=4096,
    )
    if test_config:
        app.config.update(test_config)

    database = Path(app.config["LAB_DATABASE"])
    initialize_database(database)
    initialize_events(database)

    @app.before_request
    def require_local_client():
        # Defence in depth; loopback binding below is the primary boundary.
        # A reverse proxy/tunnel could bypass this: do not configure either.
        if request.remote_addr not in ("127.0.0.1", "::1"):
            abort(403)

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; "
            "style-src 'self'; script-src 'self'; base-uri 'none'; "
            "form-action 'self'; frame-ancestors 'none'"
        )
        return response

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.get("/lab")
    def comparison_lab():
        return render_template("compare.html")

    @app.get("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "phase": 3})

    def parse_credentials():
        if not request.is_json:
            return None, (jsonify({"error": "Expected a JSON request."}), 415)
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return None, (jsonify({"error": "Expected a JSON object."}), 400)
        username = data.get("username")
        secret = data.get("demo_secret")
        if not isinstance(username, str) or not isinstance(secret, str):
            return None, (jsonify({"error": "Both fields must be text."}), 400)
        if not username or not secret or len(username) > 160 or len(secret) > 160:
            return None, (jsonify({"error": "Both fields are required (maximum 160 characters)."}), 400)
        return (username, secret), None

    @app.post("/api/compare")
    def compare():
        credentials, error = parse_credentials()
        if error:
            return error
        username, secret = credentials
        db = app.config["LAB_DATABASE"]
        vulnerable = authenticate("vulnerable", username, secret, db)
        protected = authenticate("protected", username, secret, db)

        if vulnerable["authenticated"] and not protected["authenticated"]:
            finding = "injection_effect_observed"
            explanation = (
                "The unsafe query matched an account while the parameterized query "
                "rejected the same input. This demonstrates a query-structure change."
            )
        elif vulnerable["authenticated"] and protected["authenticated"]:
            finding = "both_authenticated"
            explanation = "Both queries matched the same supplied demonstration credentials."
        elif vulnerable["status"] == "query_error":
            finding = "vulnerable_query_error"
            explanation = "The unsafe query failed to parse; the parameterized query kept the input as data."
        else:
            finding = "no_bypass_observed"
            explanation = "No authentication bypass was observed for these inputs."

        event_id = record_comparison(
            db, finding, vulnerable["status"], protected["status"]
        )
        return jsonify({
            "vulnerable": vulnerable,
            "protected": protected,
            "finding": finding,
            "explanation": explanation,
            "event_id": event_id,
        })

    @app.post("/api/login/<mode>")
    def login_mode(mode: str):
        # Single-mode tests are not recorded; dashboard counts /api/compare only.
        if mode not in ("vulnerable", "protected"):
            abort(404)
        credentials, error = parse_credentials()
        if error:
            return error
        username, secret = credentials
        return jsonify(authenticate(mode, username, secret, app.config["LAB_DATABASE"]))

    @app.get("/api/stats")
    def stats():
        return jsonify(event_statistics(app.config["LAB_DATABASE"]))

    @app.get("/api/events")
    def events():
        try:
            limit = int(request.args.get("limit", "50"))
        except ValueError:
            return jsonify({"error": "limit must be an integer from 1 to 200."}), 400
        if not 1 <= limit <= 200:
            return jsonify({"error": "limit must be an integer from 1 to 200."}), 400
        return jsonify({"events": recent_events(app.config["LAB_DATABASE"], limit)})

    @app.get("/api/export.csv")
    def export_csv():
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(["event_id", "timestamp_utc", "finding", "vulnerable_status", "protected_status"])
        # Export in chronological order for straightforward report analysis.
        for event in reversed(recent_events(app.config["LAB_DATABASE"], 5000)):
            writer.writerow([
                event["id"], event["created_at"], event["finding"],
                event["vulnerable_status"], event["protected_status"],
            ])
        return Response(output.getvalue(), mimetype="text/csv", headers={
            "Content-Disposition": "attachment; filename=sqlshield-lab-events.csv"
        })

    @app.get("/api/export.json")
    def export_json():
        return jsonify({
            "description": "Sanitized SQLShield lab comparison outcomes; no submitted inputs stored.",
            "events": list(reversed(recent_events(app.config["LAB_DATABASE"], 5000))),
        })

    @app.errorhandler(413)
    def payload_too_large(_error):
        return jsonify({"error": "Request is too large for this demonstration."}), 413

    return app


app = create_app()

if __name__ == "__main__":
    # Keep this exact loopback binding and debug=False. Never publicly deploy.
    app.run(host="127.0.0.1", port=5000, debug=False)
