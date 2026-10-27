import os
import tempfile

os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

VALID = {"title": "Python Intern", "company": "Acme Corp", "location": "Remote",
         "work_mode": "remote", "stipend": 5000, "description": "Learn APIs", "deadline": "2026-12-31"}


def test_all():
    with TestClient(app) as c:
        r = c.get("/internships")
        assert r.status_code == 200 and r.json()["meta"]["total"] == 5
        assert len(c.get("/internships?status=closed").json()["data"]) == 1
        assert c.get("/internships?limit=2").json()["meta"]["limit"] == 2
        assert c.get("/internships?status=bad").status_code == 400

        r = c.post("/internships", json=VALID)
        assert r.status_code == 201 and r.headers["location"].startswith("/internships/")
        new_id = r.json()["data"]["id"]
        assert r.json()["data"]["status"] == "open"

        assert c.get(f"/internships/{new_id}").json()["data"]["title"] == "Python Intern"
        r = c.get("/internships/9999")
        assert r.status_code == 404 and r.json()["error"]["code"] == "NOT_FOUND"
        assert c.get("/internships/abc").status_code == 400

        r = c.post("/internships", json={"title": "x"})
        assert r.status_code == 400 and r.json()["error"]["code"] == "VALIDATION_ERROR"
        assert c.post("/internships", json={**VALID, "work_mode": "mars"}).status_code == 400
        assert c.post("/internships", json={**VALID, "stipend": -1}).status_code == 400
        assert c.post("/internships", json={**VALID, "deadline": "not-a-date"}).status_code == 400
        assert c.post("/internships", json={**VALID, "extra": 1}).status_code == 400
        assert c.post("/internships", content="{bad json", headers={"content-type": "application/json"}).status_code == 400

        r = c.put(f"/internships/{new_id}", json={**VALID, "title": "Senior Intern"})
        assert r.status_code == 200 and r.json()["data"]["title"] == "Senior Intern"
        r = c.patch(f"/internships/{new_id}", json={"status": "closed"})
        assert r.status_code == 200 and r.json()["data"]["status"] == "closed"
        assert c.patch(f"/internships/{new_id}", json={}).status_code == 400
        assert c.patch("/internships/9999", json={"status": "open"}).status_code == 404
        assert c.put("/internships/9999", json=VALID).status_code == 404

        assert c.delete(f"/internships/{new_id}").status_code == 204
        assert c.delete(f"/internships/{new_id}").status_code == 404
        assert c.get(f"/internships/{new_id}").status_code == 404
