#!/usr/bin/env python3
import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from logging import INFO
from dotenv import load_dotenv
from github import Github
from pathlib import Path
from graphiti_core import Graphiti
# from graphiti_core.config import GraphitiConfig
from graphiti_core.nodes import EpisodeType
from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF

# ─── CONFIGURATION ──────────────────────────────────────────────────────────────

# Required environment variables:
#   GITHUB_TOKEN : a token with `repo` scope
#   NEO4J_URI    : e.g. bolt://localhost:7687
#   NEO4J_USER   : usually "neo4j"
#   NEO4J_PASS   : your Neo4j password
# Optional:
#   GROUP_ID_PREFIX : defaults to "demo"

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


# ─── Ingest logic ────────────────────────────────────────────────────────────────
async def ingest(repo_full: str, file_path: str = "codecoach.md"):
    # 1) fetch the text via GitHub API
    gh = Github(GITHUB_TOKEN)
    repo = gh.get_repo(repo_full)
    blob = repo.get_contents(file_path)
    text = blob.decoded_content.decode()

    # 2) init Graphiti (three‑arg constructor per Quick‑Start)
    graphiti = Graphiti(NEO4J_URI, NEO4J_USER, NEO4J_PASS)
    try:
        # only needs to run once per database
        await graphiti.build_indices_and_constraints()

        # 3) add your markdown as an “episode”
        await graphiti.add_episode(
            name=file_path,
            episode_body=text,
            source="text",
            source_description="codecoach docs",
            reference_time=datetime.now(timezone.utc),
        )
        print(f"✅ Ingested `{file_path}` into Neo4j graph.")
    finally:
        await graphiti.close()
        print("🔌 Connection closed")

# ─── Entrypoint ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 demo_ingest.py <owner/repo> [file_path]")
        sys.exit(1)
    owner_repo = sys.argv[1]
    path       = sys.argv[2] if len(sys.argv) > 2 else "codecoach.md"
    asyncio.run(ingest(owner_repo, path))