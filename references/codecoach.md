# CodeCoach Documentation

Welcome to **CodeCoach**, your per‑repo guide for architecture decisions, style rules, and best practices. Treat this as your “single source of truth” for anything non‑code.

---

## 1. Project Overview  
**CodeCoach** is a lightweight service that  
- 🧠 Ingests structured documentation into a Neo4j graph  
- 💬 Powers LLM‑backed Q&A on architecture, style, and workflows  
- 🔄 Supports continuous updates via “episodes” (e.g. codecoach.md entries)

---

## 2. Architecture Snapshot  
[ GitHub App ] → [ CodeCoach Ingest Service ] → [ Neo4j Graph Database ] ↓ [ LLM Assistant ]

yaml
Copy
Edit
- **Ingest** runs on Python 3.13+, uses Graphiti for chunking + entity extraction.  
- **Neo4j** holds the doc graph: nodes = concepts, edges = relationships.  
- **Assistant** queries the graph to ground LLM replies.

---

## 3. File Structure  
/ ├── demo_ingest.py # main ingest script ├── codecoach.md # this file ├── requirements.txt # pip dependencies └── README.md # high‑level project intro

markdown
Copy
Edit

---

## 4. Coding Standards  

- **Python**  
  - Use **Black** for formatting (88‑char line length).  
  - Type hint everything; run `mypy .` before PR.  
- **Markdown**  
  - Headings use ATX style (`## Section Title`).  
  - Wrap lines at ~80 columns.  
- **Git**  
  - Commit messages follow Conventional Commits:  
    - `feat: …`, `fix: …`, `docs: …`, `refactor: …`

---

## 5. Ingesting New Episodes  

1. Add or update a section in `codecoach.md`.  
2. Run:
   ```bash
   python3 demo_ingest.py <owner/repo> codecoach.md