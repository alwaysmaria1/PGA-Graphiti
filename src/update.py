import asyncio
import logging
import difflib
from .utils import (
    get_graphiti_client,
    fetch_file_content,
    get_current_time,
    get_cached_content,
    save_content_to_cache
)

logger = logging.getLogger(__name__)

def compute_diff(old_content, new_content):
    """
    Compute the difference between old and new content.
    
    Returns:
        tuple: (added_sections, removed_sections)
    """
    # Split content into sections (using markdown headers as delimiters)
    def split_into_sections(content):
        sections = []
        current_section = []
        lines = content.split('\n')
        
        for line in lines:
            if line.startswith('#') and current_section:
                sections.append('\n'.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)
        
        if current_section:
            sections.append('\n'.join(current_section))
        
        return sections
    
    old_sections = split_into_sections(old_content)
    new_sections = split_into_sections(new_content)
    
    # Find added and removed sections
    matcher = difflib.SequenceMatcher(None, old_sections, new_sections)
    added = []
    removed = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace' or tag == 'delete':
            # Sections that were in old but not in new (or modified)
            removed.extend(old_sections[i1:i2])
        
        if tag == 'replace' or tag == 'insert':
            # Sections that are in new but not in old (or modified)
            added.extend(new_sections[j1:j2])
    
    return added, removed

async def update_codecoach(repo_full, file_path="codecoach.md"):
    """
    Update a codecoach.md file in Neo4j using Graphiti, applying only the changes.
    
    Args:
        repo_full (str): GitHub repository in format "owner/repo"
        file_path (str): Path to the codecoach.md file in the repository
        
    Returns:
        dict: Summary of the update process
    """
    logger.info(f"Starting update for {repo_full}/{file_path}")
    
    # Fetch new content from GitHub
    new_content = fetch_file_content(repo_full, file_path)
    
    # Get old content from cache
    old_content = get_cached_content(repo_full, file_path)
    print("Old content from cache:", old_content[:200] if old_content else "No cached content")  # Debug print
    
    if not old_content:
        logger.warning("No cached content found. Performing full ingestion instead.")
        from .ingest import ingest_codecoach
        return await ingest_codecoach(repo_full, file_path)
    
    # Initialize Graphiti client
    graphiti = get_graphiti_client()
    
    try:
        # Update the graph with changes
        reference_time = get_current_time()
        
        # Instead of deleting and recreating, we'll add a new episode
        # The new episode will automatically supersede the old one in Graphiti
        await graphiti.add_episode(
            name=file_path,  # Use the same name
            episode_body=new_content,
            source="text",
            source_description=f"Updated CodeCoach documentation from {repo_full}",
            reference_time=reference_time,
        )
        
        # Cache the new content
        save_content_to_cache(repo_full, file_path, new_content)
        
        logger.info(f"Successfully updated {file_path} in Neo4j graph")
        return {
            "status": "success",
            "repository": repo_full,
            "file": file_path,
            "timestamp": reference_time.isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error during update: {str(e)}")
        raise
    
    finally:
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
        print("Usage: python -m src.update <owner/repo> [file_path]")
        sys.exit(1)
    
    owner_repo = sys.argv[1]
    path = sys.argv[2] if len(sys.argv) > 2 else "codecoach.md"
    
    result = asyncio.run(update_codecoach(owner_repo, path))
    print(f"✅ Update complete: {result}")