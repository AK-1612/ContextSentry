# ContextSentry

ContextSentry is a local PreToolUse hook and context optimization CLI designed to stop LLM coding agents from overloading context windows with large files.

## Key Features

- **350-Line Circuit Breaker:** Intercepts file read requests and blocks raw file exposure for files over 350 lines.
- **Local Worker Delegation:** Offloads large file parsing out-of-band to a local model (`llama3.2` via Ollama) to generate line-numbered summaries.
- **Direct-to-Disk Writer:** Generates large code files out-of-band directly to disk without polluting context history.
- **Telemetry Engine:** Tracks file interceptions, offloaded lines, and estimated GPT-4o dollar savings in SQLite.

## Tech Stack

- Python 3.14
- Typer & Rich
- SQLite
- Ollama (`llama3.2`)
- Pytest

## Setup & Usage

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run read interception
python main.py read <file_path>

# Direct code generation to disk
python main.py write <file_path> -p "Specification prompt"

# View telemetry stats
python main.py stats
