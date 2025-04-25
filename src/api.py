import asyncio
import logging
from flask import Flask, request, jsonify
from .ingest import ingest_codecoach
from .update import update_codecoach
from .search import query_service
from .utils import get_graphiti_client

logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return jsonify(status="ok")

@app.route('/ingest', methods=['POST'])
def ingest_endpoint():
    """
    Endpoint to ingest a codecoach.md file into Neo4j.
    
    Expected JSON body:
    {
        "repo": "owner/repo",
        "path": "codecoach.md"  # Optional, defaults to "codecoach.md"
    }
    """
    try:
        data = request.json
        
        if not data or 'repo' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing required field: repo"
            }), 400
        
        repo = data['repo']
        path = data.get('path', 'codecoach.md')
        
        # Run the ingest function asynchronously
        result = asyncio.run(ingest_codecoach(repo, path))
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.exception("Error in ingest endpoint")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/update', methods=['POST'])
def update_endpoint():
    """
    Endpoint to update a codecoach.md file in Neo4j.
    
    Expected JSON body:
    {
        "repo": "owner/repo",
        "path": "codecoach.md"  # Optional, defaults to "codecoach.md"
    }
    """
    try:
        data = request.json
        
        if not data or 'repo' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing required field: repo"
            }), 400
        
        repo = data['repo']
        path = data.get('path', 'codecoach.md')
        
        # Run the update function asynchronously
        result = asyncio.run(update_codecoach(repo, path))
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.exception("Error in update endpoint")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


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
    host, port = "0.0.0.0", 4000
    debug = True
else:
    # when run as module, still use these
    host, port, debug = "0.0.0.0", 4000, False

app.run(host=host, port=port, debug=debug)