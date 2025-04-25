# CodeCoach Knowledge Graph Service

A service that ingests and updates a knowledge graph from a codecoach.md file, then exposes it via a Flask API.

## Setup

### Prerequisites

- Python 3.10 or higher
- Neo4j (local instance or remote)
- GitHub token with repo scope

### Environment Variables

Create a `.env` file with the following variables:


### GITHUB_TOKEN=your_github_token

NEO4J_URI=bolt://localhost:7687

NEO4J_USER=neo4j

NEO4J_PASSWORD=your_password

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/pga-graphiti.git
cd pga-graphiti
```

2. Install dependencies using Poetry:
```bash
# Install Poetry if you don't have it
pip install poetry

# Install dependencies
poetry install
```

Or using pip:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Command Line

#### Initial Ingestion

```bash
# Using Poetry
poetry run python -m src.ingest owner/repo [path/to/codecoach.md]

# Using venv
python -m src.ingest owner/repo [path/to/codecoach.md]
```

#### Incremental Update

```bash
# Using Poetry
poetry run python -m src.update owner/repo [path/to/codecoach.md]

# Using venv
python -m src.update owner/repo [path/to/codecoach.md]
```

### Flask API

Start the Flask server:

```bash
# Using Poetry
poetry run python -m src.api

# Using venv
python -m src.api
```

#### API Endpoints

1. **Ingest a codecoach.md file**

   `POST /ingest`

   Request body:
   ```json
   {
     "repo": "owner/repo",
     "path": "codecoach.md"  // Optional, defaults to "codecoach.md"
   }
   ```

2. **Update a codecoach.md file**

   `POST /update`

   Request body:
   ```json
   {
     "repo": "owner/repo",
     "path": "codecoach.md"  // Optional, defaults to "codecoach.md"
   }
   ```

3. **Search the knowledge graph**

   `POST /search`

   Request body:
   ```json
   {
     "query": "search query string",
     "center_node_uuid": "optional-uuid-for-reranking"  // Optional
   }
   ```

## Development

### Project Structure

```
pga-graphiti/
├── .env                  # Environment variables
├── .gitignore            # Git ignore file
├── pyproject.toml        # Poetry configuration
├── README.md             # Documentation
├── src/
│   ├── __init__.py
│   ├── ingest.py         # Initial ingest script
│   ├── update.py         # Incremental update script
│   ├── api.py            # Flask API
│   └── utils.py          # Shared utilities
└── tests/
    ├── __init__.py
    ├── test_ingest.py
    └── test_update.py
```

### Running Tests

```bash
# Using Poetry
poetry run pytest

# Using venv
pytest
```

## License

[MIT](LICENSE)

## Next Steps

1. **Fix Python Version**: Update your `pyproject.toml` to use Python 3.10 or 3.11 instead of 3.13 to avoid compatibility issues.

2. **Create the Project Structure**: Set up the directory structure and files as outlined above.

3. **Install Dependencies**: Use Poetry or pip to install the required dependencies.

4. **Test Each Component**: Test the ingest and update scripts individually before integrating with the Flask API.

5. **Set Up Neo4j**: Ensure you have a Neo4j instance running locally or remotely.

6. **Implement Error Handling**: Add more robust error handling and validation in the production version.

7. **Add Authentication**: Consider adding authentication to the Flask API for production use.

This implementation provides a solid foundation for your CodeCoach knowledge graph service. The modular design allows for easy testing and extension, and the Flask API makes it accessible to your AI application.



Here are some commands to test with, these run the ingest and update scripts:

poetry run python -m src.ingest alwaysmaria1/TestingPGAApps-Maria
poetry run python -m src.update alwaysmaria1/TestingPGAApps-Maria

to run the flask api: "poetry run python -m src.api"

