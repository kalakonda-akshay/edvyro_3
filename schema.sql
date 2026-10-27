CREATE TABLE IF NOT EXISTS internships (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL CHECK (length(title) BETWEEN 3 AND 120),
    company     TEXT    NOT NULL CHECK (length(company) BETWEEN 2 AND 120),
    location    TEXT    NOT NULL,
    work_mode   TEXT    NOT NULL CHECK (work_mode IN ('remote','onsite','hybrid')),
    stipend     INTEGER CHECK (stipend IS NULL OR stipend >= 0),
    description TEXT    NOT NULL DEFAULT '',
    deadline    TEXT,                                   -- ISO date: YYYY-MM-DD
    status      TEXT    NOT NULL DEFAULT 'open' CHECK (status IN ('open','closed')),
    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    updated_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
CREATE INDEX IF NOT EXISTS idx_internships_status ON internships(status);
