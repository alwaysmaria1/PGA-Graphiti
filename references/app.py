import logging
logger = logging.getLogger(__name__)

# ─── Logging Setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,   # or INFO if you want less noise
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
# Optionally, mute very noisy loggers (like the HTTP client, etc.)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("neo4j").setLevel(logging.INFO)

# Now import the rest
from flask import Flask, request, jsonify
from src.search import  query_service

app = Flask(__name__)

@app.route("/ingest", methods=["POST"])
def http_ingest():
    """
    POST /ingest
    Expects JSON body:
      {
        "repo": "owner/repo",       # required: GitHub repository identifier
        "path": "codecoach.md"      # optional: filename in the repo (default: "codecoach.md")
      }
    Returns:
      {
        "status": "ingested",
        "group_id": "owner_repo"
      }
    """
    data = request.get_json()
    repo = data["repo"]                   # e.g. "alwaysmaria1/TestingPGAApps-Maria"
    path = data.get("path", "codecoach.md")
    try:
        result = ingest_service(repo, path)
        return jsonify(result)
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route("/update", methods=["POST"])
def http_update():
    """
    POST /update
    Expects JSON body:
      {
        "repo": "owner/repo",       # required: GitHub repository identifier
        "path": "codecoach.md"      # optional: filename (default: "codecoach.md")
      }
    Returns:
      {
        "status": "updated",
        "delta": "<unified-diff-text>"
      }
    """
    data = request.get_json()
    repo = data["repo"]
    path = data.get("path", "codecoach.md")
    try:
        result = update_service(repo, path)
        return jsonify(result)
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route("/query", methods=["POST"])
def http_query():
    data = request.get_json(force=True)
    repo = data.get("repo")
    if not repo or not isinstance(repo, str):
        return jsonify(error="'repo' is required and must be a string"), 400
    group_id = repo.replace("/", "_")

    raw_q = data.get("query")
    if raw_q is None:
        return jsonify(error="'query' is required"), 400
    query_str = raw_q.strip() if isinstance(raw_q, str) else str(raw_q)

    try:
        result = query_service(group_id, query_str, int(data.get("top_k", 5)))
        return jsonify(result)
    except Exception as e:
        # this will show the full stack in your console
        logger.exception("Error running /query for %s : %s", group_id, query_str)
        # bubble up so Flask’s debugger prints the trace
        raise

if __name__ == "__main__":
    app.run(debug=True, port=5000)
