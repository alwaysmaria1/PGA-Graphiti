import asyncio
import os
# from ingestion import _get_graphiti
from graphiti_core import Graphiti
from pathlib import Path
from dotenv import load_dotenv

from graphiti_core.search.search import search
from graphiti_core.search.search_config_recipes import COMBINED_HYBRID_SEARCH_RRF
from graphiti_core.search.search_filters import SearchFilters


# SET UP GRAPHITI CLIENT

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
NEO4J_URI = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER   = os.environ.get('NEO4J_USER', 'neo4j')
NEO4J_PASS   = os.environ.get('NEO4J_PASSWORD', 'password')
GROUP_PREFIX = os.environ.get("GROUP_ID_PREFIX", "demo")

if not all([GITHUB_TOKEN, NEO4J_URI, NEO4J_USER, NEO4J_PASS]):
    print("❌ please set GITHUB_TOKEN, NEO4J_URI, NEO4J_USER, NEO4J_PASS")
    exit(1)

def get_graphiti() -> Graphiti:
    """
    Initialize and return a Graphiti client using the
    NEO4J_URI, NEO4J_USER, and NEO4J_PASS from your env.
    """
    return Graphiti(NEO4J_URI, NEO4J_USER, NEO4J_PASS)


# SEARCH SERVICE


async def _do_search(group_id: str, query: str, top_k: int = 5):
    graph = get_graphiti()
    try:
        cfg = COMBINED_HYBRID_SEARCH_RRF
        cfg.limit = top_k
        filters = SearchFilters()

        # this returns a SearchResults object
        results = await search(
            driver        = graph.driver,
            embedder      = graph.embedder,
            cross_encoder = graph.cross_encoder,
            query         = query,
            group_ids     = [group_id],
            config        = cfg,
            search_filter = filters,
        )
        return results
    finally:
        await graph.close()

def query_service(group_id: str, query: str, top_k: int = 5):
    """
    Runs Graphiti’s unified hybrid search and returns JSON-serializable dict.
    """
    results = asyncio.run(_do_search(group_id, query, top_k))

    return {
        "nodes": [
            {"id":    n.uuid,
             "summary": n.summary}
            for n in results.nodes
        ],
        "facts": [
            {"id":        e.uuid,
             "subject":   e.source_node_uuid,
             "predicate": e.predicate,
             "object":    e.target_node_uuid,
             "score":     e.score}
            for e in results.edges
        ],
        "episodes": [
            {"id":      ep.uuid,
             "content": ep.content}
            for ep in results.episodes
        ],
        "communities": [
            {"id":   c.uuid,
             "name": c.name}
            for c in results.communities
        ],
    }
