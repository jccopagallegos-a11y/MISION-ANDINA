import os, sqlite3
from flask import current_app, g

def get_db():
    if "_database" not in g:
        path = current_app.config["DATABASE"]
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        g._database = sqlite3.connect(path)
        g._database.row_factory = sqlite3.Row
        g._database.execute("PRAGMA foreign_keys = ON")
    return g._database

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('admin','user')),
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS missions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        objective TEXT NOT NULL,
        destination TEXT NOT NULL,
        spacecraft TEXT NOT NULL,
        launcher TEXT NOT NULL,
        instruments TEXT NOT NULL,
        budget REAL NOT NULL,
        mass REAL NOT NULL,
        power REAL NOT NULL,
        communications TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'En diseño',
        score INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    db.commit()
