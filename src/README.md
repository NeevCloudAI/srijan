# Srijan

An AI-powered engineering assistant for chat platforms.

Srijan lets engineers delegate routine coding and debugging tasks to autonomous
AI agents via simple slash commands — without leaving their chat window.

## Commands

| Command | Purpose | Output |
|---|---|---|
| `/neevai-dev <task>` | Coding tasks — bug fixes, small features | GitHub Pull Request |
| `/neevai-debug <issue>` | Debugging — root cause analysis, log inspection | Diagnosis report |

## Local Development

### Prerequisites
- Python 3.11+
- Docker + Docker Compose

### Setup

1. Clone the repo
   git clone https://github.com/NeevCloudAI/srijan.git
   cd srijan

2. Copy the environment variable template
   cp .env.example .env

3. Start PostgreSQL and Redis
   docker compose up -d

4. Install dependencies
   pip install -e .

5. Run the server
   uvicorn src.main:app --reload

6. Verify it's working
   curl http://localhost:8000/health
   # Expected: {"status": "ok", "service": "srijan"}

## Project Structure

See docs/rfcs/002_code_organization.md for full details.

## Documentation

- 001 — Initial Design: docs/rfcs/001_initial_design.md
- 002 — Code Organization: docs/rfcs/002_code_organization.md