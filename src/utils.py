import os
import logging
from datetime import datetime, timezone
from github import Github
from graphiti_core import Graphiti

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

def get_github_client():
    """Initialize and return a GitHub client using the token from environment."""
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable is required")
    return Github(github_token)

def get_graphiti_client():
    """Initialize and return a Graphiti client using Neo4j credentials from environment."""
    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_pass = os.environ.get("NEO4J_PASSWORD", "password")
    
    if not all([neo4j_uri, neo4j_user, neo4j_pass]):
        raise ValueError("NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set")
    
    return Graphiti(neo4j_uri, neo4j_user, neo4j_pass)

def fetch_file_content(repo_full, file_path):
    """Fetch file content from GitHub repository."""
    logger.info(f"Fetching {file_path} from {repo_full}")
    gh = get_github_client()
    repo = gh.get_repo(repo_full)
    try:
        blob = repo.get_contents(file_path)
        content = blob.decoded_content.decode()
        logger.info(f"Successfully fetched {file_path} ({len(content)} bytes)")
        return content
    except Exception as e:
        logger.error(f"Error fetching {file_path} from {repo_full}: {str(e)}")
        raise

def get_current_time():
    """Return current time in UTC timezone."""
    return datetime.now(timezone.utc)

def save_content_to_cache(repo_full, file_path, content):
    """Save content to local cache for future diff comparison."""
    cache_dir = os.path.join(os.getcwd(), ".cache")
    os.makedirs(cache_dir, exist_ok=True)
    
    # Create a filename based on repo and path
    safe_name = f"{repo_full.replace('/', '_')}_{file_path.replace('/', '_')}"
    cache_path = os.path.join(cache_dir, safe_name)
    
    with open(cache_path, "w") as f:
        f.write(content)
    
    logger.info(f"Cached content to {cache_path}")
    return cache_path

def get_cached_content(repo_full, file_path):
    """Retrieve content from local cache if available."""
    cache_dir = os.path.join(os.getcwd(), ".cache")
    safe_name = f"{repo_full.replace('/', '_')}_{file_path.replace('/', '_')}"
    cache_path = os.path.join(cache_dir, safe_name)
    
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            content = f.read()
        logger.info(f"Retrieved cached content from {cache_path}")
        return content
    
    logger.info(f"No cached content found for {repo_full}/{file_path}")
    return None