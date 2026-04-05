"""
Gestion des utilisateurs et du suivi quotidien des requêtes.
Stockage : SQLite (un seul fichier, zéro dépendance externe).
"""

import sqlite3
import os
from datetime import date
from contextlib import contextmanager

DB_PATH = os.getenv("DB_PATH", "data/users.db")
FREE_DAILY_LIMIT = int(os.getenv("FREE_DAILY_LIMIT", "3"))

# ── Helpers de connexion ──────────────────────────────────────────────────────

@contextmanager
def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ── Initialisation de la base ─────────────────────────────────────────────────

def init_db() -> None:
    """Crée les tables si elles n'existent pas encore."""
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                first_name  TEXT,
                joined_at   TEXT DEFAULT (date('now')),
                is_premium  INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS daily_usage (
                user_id     INTEGER NOT NULL,
                usage_date  TEXT    NOT NULL,
                count       INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, usage_date)
            );
        """)


# ── Gestion des utilisateurs ──────────────────────────────────────────────────

def register_user(user_id: int, username: str | None, first_name: str | None) -> None:
    """Enregistre un utilisateur s'il n'existe pas déjà."""
    with get_conn() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
            """,
            (user_id, username, first_name),
        )


def is_premium(user_id: int) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT is_premium FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return bool(row and row["is_premium"])


def set_premium(user_id: int, status: bool = True) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET is_premium = ? WHERE user_id = ?",
            (int(status), user_id),
        )


# ── Comptage des requêtes ─────────────────────────────────────────────────────

def get_usage_today(user_id: int) -> int:
    today = str(date.today())
    with get_conn() as conn:
        row = conn.execute(
            "SELECT count FROM daily_usage WHERE user_id = ? AND usage_date = ?",
            (user_id, today),
        ).fetchone()
        return row["count"] if row else 0


def increment_usage(user_id: int) -> int:
    """Incrémente le compteur et retourne la nouvelle valeur."""
    today = str(date.today())
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO daily_usage (user_id, usage_date, count)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id, usage_date)
            DO UPDATE SET count = count + 1
            """,
            (user_id, today),
        )
        row = conn.execute(
            "SELECT count FROM daily_usage WHERE user_id = ? AND usage_date = ?",
            (user_id, today),
        ).fetchone()
        return row["count"]


def get_remaining(user_id: int) -> int:
    if is_premium(user_id):
        return 999  # illimité
    used = get_usage_today(user_id)
    return max(0, FREE_DAILY_LIMIT - used)


def can_use(user_id: int) -> bool:
    return get_remaining(user_id) > 0


# Initialisation au démarrage du module
init_db()
