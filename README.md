# Internship Board API

A beginner-friendly REST API for managing internship listings. Built with **Python, FastAPI and SQLite**.

## Features
- Full CRUD: list, detail, create, update (PUT + PATCH), delete
- Input validation with clear, consistent error responses
- Filtering (`status`, `work_mode`, `q`) and pagination (`limit`, `offset`)
- SQLite persistence, schema in `schema.sql`, seed data in `data/seed.json`
- Automated tests with Pytest

## Setup
```bash
git clone <your-repo-url>
cd internship-board-api
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m app.db                 # (optional) reset DB and load seed data
uvicorn app.main:app --reload
```
The API runs at http://127.0.0.1:8000 — interactive docs at http://127.0.0.1:8000/docs.
The database file `internships.db` is created automatically and seeded on first start.

## Run tests
```bash
pytest -q
```

## Data model (`internships` table)
| Field | Type | Rules |
|---|---|---|
| id | integer | auto-generated |
| title | string | required, 3–120 chars |
| company | string | required, 2–120 chars |
| location | string | required |
| work_mode | string | required: `remote`, `onsite`, `hybrid` |
| stipend | integer / null | optional, >= 0 |
| description | string | optional, max 5000 chars |
| deadline | string / null | optional, ISO date `YYYY-MM-DD` |
| status | string | `open` (default) or `closed` |
| created_at / updated_at | string | set by server (UTC) |

## Endpoints
| Method | Path | Description | Success |
|---|---|---|---|
| GET | `/health` | Health check | 200 |
| GET | `/internships` | List (filters + pagination) | 200 |
| GET | `/internships/{id}` | Get one | 200 |
| POST | `/internships` | Create | 201 + `Location` header |
| PUT | `/internships/{id}` | Replace (all fields required) | 200 |
| PATCH | `/internships/{id}` | Partial update | 200 |
| DELETE | `/internships/{id}` | Delete | 204 (no body) |

## Response format
Success:
```json
{ "data": { "id": 1, "title": "..." } }
```
List responses add `"meta": {"total": 5, "limit": 20, "offset": 0}`.

Error (always this shape):
```json
{ "error": { "code": "VALIDATION_ERROR", "message": "Request validation failed",
             "details": [ { "field": "work_mode", "message": "Input should be 'remote', 'onsite' or 'hybrid'" } ] } }
```

| Status | Code | When |
|---|---|---|
| 400 | `VALIDATION_ERROR` | bad/missing fields, invalid JSON, bad id or query value |
| 404 | `NOT_FOUND` | internship id doesn't exist |
| 405 | `METHOD_NOT_ALLOWED` | wrong HTTP method |
| 500 | `INTERNAL_ERROR` | unexpected server error |

## API examples (curl)
**List**
```bash
curl "http://127.0.0.1:8000/internships?status=open&work_mode=remote&limit=10"
curl "http://127.0.0.1:8000/internships?q=developer"
```
**Detail**
```bash
curl http://127.0.0.1:8000/internships/1
```
**Create**
```bash
curl -X POST http://127.0.0.1:8000/internships \
  -H "Content-Type: application/json" \
  -d '{"title":"Python Intern","company":"Acme Corp","location":"Remote","work_mode":"remote","stipend":5000,"description":"Learn APIs","deadline":"2026-12-31"}'
```
**Update (full)**
```bash
curl -X PUT http://127.0.0.1:8000/internships/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Backend Intern","company":"BrightLabs","location":"Hyderabad","work_mode":"hybrid","stipend":16000,"description":"Updated","deadline":"2026-12-20","status":"open"}'
```
**Update (partial)**
```bash
curl -X PATCH http://127.0.0.1:8000/internships/1 \
  -H "Content-Type: application/json" -d '{"status":"closed"}'
```
**Delete**
```bash
curl -X DELETE http://127.0.0.1:8000/internships/1 -i
```
**Validation error example**
```bash
curl -X POST http://127.0.0.1:8000/internships -H "Content-Type: application/json" -d '{"title":"x"}'
```

## Project structure
```
app/main.py      # routes + error handling
app/schemas.py   # validation rules
app/db.py        # SQLite connection, init, seeding
schema.sql       # table definition
data/seed.json   # sample records
tests/           # pytest tests
```
