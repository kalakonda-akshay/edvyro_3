"""Internship Board API - FastAPI + SQLite.

Response format
  success: {"data": ..., "meta": {...}}   (meta only on list)
  error:   {"error": {"code": "...", "message": "...", "details": [...]}}

Status codes
  200 OK | 201 Created | 204 No Content (delete)
  400 invalid input / malformed JSON | 404 not found | 500 unexpected error
"""
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import db
from .schemas import InternshipCreate, InternshipPatch, InternshipReplace

COLUMNS = ["title", "company", "location", "work_mode", "stipend", "description", "deadline", "status"]
NOW = "strftime('%Y-%m-%dT%H:%M:%SZ','now')"


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.seed_db()  # creates table, seeds only if empty
    yield


app = FastAPI(title="Internship Board API", version="1.0.0", lifespan=lifespan)


# ---------- consistent errors ----------
def error_response(status: int, code: str, message: str, details=None) -> JSONResponse:
    body = {"error": {"code": code, "message": message, "details": details or []}}
    return JSONResponse(status_code=status, content=body)


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    details = [
        {"field": ".".join(str(p) for p in e["loc"] if p != "body") or "body", "message": e["msg"]}
        for e in exc.errors()
    ]
    return error_response(400, "VALIDATION_ERROR", "Request validation failed", details)


@app.exception_handler(StarletteHTTPException)
async def http_handler(request: Request, exc: StarletteHTTPException):
    codes = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}
    return error_response(exc.status_code, codes.get(exc.status_code, "HTTP_ERROR"), str(exc.detail))


@app.exception_handler(Exception)
async def unhandled_handler(request: Request, exc: Exception):
    return error_response(500, "INTERNAL_ERROR", "Something went wrong")


# ---------- helpers ----------
def fetch_one(conn, internship_id: int):
    return conn.execute("SELECT * FROM internships WHERE id = ?", (internship_id,)).fetchone()


def not_found(internship_id: int):
    return error_response(404, "NOT_FOUND", f"Internship {internship_id} not found")


def to_row_data(data: dict) -> dict:
    if data.get("deadline") is not None:
        data["deadline"] = data["deadline"].isoformat()
    return data


# ---------- endpoints ----------
@app.get("/health")
def health():
    return {"data": {"status": "ok"}}


@app.get("/internships")
def list_internships(
    status: Optional[str] = Query(None, pattern="^(open|closed)$"),
    work_mode: Optional[str] = Query(None, pattern="^(remote|onsite|hybrid)$"),
    q: Optional[str] = Query(None, max_length=100, description="search title/company"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    where, params = [], []
    if status:
        where.append("status = ?"); params.append(status)
    if work_mode:
        where.append("work_mode = ?"); params.append(work_mode)
    if q:
        where.append("(title LIKE ? OR company LIKE ?)"); params += [f"%{q}%", f"%{q}%"]
    clause = f"WHERE {' AND '.join(where)}" if where else ""

    with db.get_conn() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM internships {clause}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM internships {clause} ORDER BY id LIMIT ? OFFSET ?", params + [limit, offset]
        ).fetchall()
    return {"data": [dict(r) for r in rows], "meta": {"total": total, "limit": limit, "offset": offset}}


@app.get("/internships/{internship_id}")
def get_internship(internship_id: int):
    with db.get_conn() as conn:
        row = fetch_one(conn, internship_id)
    if row is None:
        return not_found(internship_id)
    return {"data": dict(row)}


@app.post("/internships", status_code=201)
def create_internship(payload: InternshipCreate, response: Response):
    data = to_row_data(payload.model_dump())
    with db.get_conn() as conn:
        cur = conn.execute(
            f"INSERT INTO internships ({', '.join(COLUMNS)}) VALUES ({', '.join(':' + c for c in COLUMNS)})", data
        )
        row = fetch_one(conn, cur.lastrowid)
    response.headers["Location"] = f"/internships/{row['id']}"
    return {"data": dict(row)}


@app.put("/internships/{internship_id}")
def replace_internship(internship_id: int, payload: InternshipReplace):
    data = to_row_data(payload.model_dump())
    data["id"] = internship_id
    sets = ", ".join(f"{c} = :{c}" for c in COLUMNS)
    with db.get_conn() as conn:
        if fetch_one(conn, internship_id) is None:
            return not_found(internship_id)
        conn.execute(f"UPDATE internships SET {sets}, updated_at = {NOW} WHERE id = :id", data)
        row = fetch_one(conn, internship_id)
    return {"data": dict(row)}


@app.patch("/internships/{internship_id}")
def update_internship(internship_id: int, payload: InternshipPatch):
    data = to_row_data(payload.model_dump(exclude_unset=True))
    if not data:
        return error_response(400, "VALIDATION_ERROR", "Provide at least one field to update")
    sets = ", ".join(f"{c} = :{c}" for c in data)
    data["id"] = internship_id
    with db.get_conn() as conn:
        if fetch_one(conn, internship_id) is None:
            return not_found(internship_id)
        conn.execute(f"UPDATE internships SET {sets}, updated_at = {NOW} WHERE id = :id", data)
        row = fetch_one(conn, internship_id)
    return {"data": dict(row)}


@app.delete("/internships/{internship_id}", status_code=204)
def delete_internship(internship_id: int):
    with db.get_conn() as conn:
        cur = conn.execute("DELETE FROM internships WHERE id = ?", (internship_id,))
    if cur.rowcount == 0:
        return not_found(internship_id)
    return Response(status_code=204)
