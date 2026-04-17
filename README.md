# REST API Testing Project

API-focused project for validating REST endpoints, response behavior, and basic backend functionality.

## Objective

- Practice API testing and validation workflows
- Verify endpoint behavior, status codes, and payloads
- Strengthen backend-quality testing fundamentals

## Tech Stack

- Python
- Django (project includes `manage.py`)
- SQLite
- REST API testing tools/workflows

## Project Structure

- `manage.py` - Django management entry point
- `project/` and `voting_system/` - application modules
- `db.sqlite3` - local development database

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
