import asyncio
import logging
from flask import Flask, request, jsonify
from .ingest import ingest_codecoach
from .update import update_codecoach
from .utils import get_graphiti_client

logger = logging.getLogger(__name__)

app = Flask(__name__)

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

@app.route('/search', methods=['POST'])
async def search_endpoint():
    """
    Endpoint to search the knowledge graph.
    
    Expected JSON body:
    {
        "query": "search query string",
        "center_node_uuid": "optional-uuid-for-reranking"  # Optional
    }
    """
    try:
        data = request.json
        
        if not data or 'query' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing required field: query"
            }), 400
        
        query = data['query']
        center_node_uuid = data.get('center_node_uuid')
        
        # Initialize Graphiti client
        graphiti = get_graphiti_client()
        
        try:
            # Perform search
            if center_node_uuid:
                results = await graphiti.search(query, center_node_uuid=center_node_uuid)
            else:
                results = await graphiti.search(query)
            
            # Convert results to JSON-serializable format
            serialized_results = []
            for result in results:
                serialized_result = {
                    "uuid": result.uuid,
                    "fact": result.fact,
                    "source_node_uuid": result.source_node_uuid,
                    "target_node_uuid": result.target_node_uuid,
                }
                
                if hasattr(result, 'valid_at') and result.valid_at:
                    serialized_result["valid_at"] = result.valid_at.isoformat()
                
                if hasattr(result, 'invalid_at') and result.invalid_at:
                    serialized_result["invalid_at"] = result.invalid_at.isoformat()
                
                serialized_results.append(serialized_result)
            
            return jsonify({
                "status": "success",
                "query": query,
                "results": serialized_results
            }), 200
        
        finally:
            # Close the Graphiti connection
            await graphiti.close()
    
    except Exception as e:
        logger.exception("Error in search endpoint")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))