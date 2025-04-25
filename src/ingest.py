import asyncio
import logging
from .utils import (
    get_graphiti_client, 
    fetch_file_content, 
    get_current_time,
    save_content_to_cache
)

logger = logging.getLogger(__name__)

async def ingest_codecoach(repo_full, file_path="codecoach.md"):
    """
    Ingest a codecoach.md file into Neo4j using Graphiti.
    
    Args:
        repo_full (str): GitHub repository in format "owner/repo"
        file_path (str): Path to the codecoach.md file in the repository
        
    Returns:
        dict: Summary of the ingestion process
    """
    logger.info(f"Starting ingestion for {repo_full}/{file_path}")
    
    # Fetch content from GitHub
    content = fetch_file_content(repo_full, file_path)
    
    # Cache the content for future updates
    save_content_to_cache(repo_full, file_path, content)
    
    # Initialize Graphiti client
    graphiti = get_graphiti_client()
    
    try:
        # Set up indices and constraints (only needs to run once per database)
        logger.info("Building indices and constraints")
        await graphiti.build_indices_and_constraints()
        
        # Add the content as an episode
        logger.info(f"Adding episode for {file_path}")
        reference_time = get_current_time()
        await graphiti.add_episode(
            name=file_path,
            episode_body=content,
            source="text",
            source_description=f"CodeCoach documentation from {repo_full}",
            reference_time=reference_time,
        )
        
        logger.info(f"Successfully ingested {file_path} into Neo4j graph")
        return {
            "status": "success",
            "repository": repo_full,
            "file": file_path,
            "content_length": len(content),
            "timestamp": reference_time.isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}")
        raise
    
    finally:
        # Close the Graphiti connection
        await graphiti.close()
        logger.info("Graphiti connection closed")

# Command-line interface
if __name__ == "__main__":
    import sys
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.ingest <owner/repo> [file_path]")
        sys.exit(1)
    
    owner_repo = sys.argv[1]
    path = sys.argv[2] if len(sys.argv) > 2 else "codecoach.md"
    
    result = asyncio.run(ingest_codecoach(owner_repo, path))
    print(f"✅ Ingestion complete: {result}")