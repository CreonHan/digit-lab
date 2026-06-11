from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def get_connection(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS histories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                predicted_digit INTEGER NOT NULL,
                probabilities_json TEXT NOT NULL,
                thumbnail TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )


def add_history(
    db_path: Path,
    user_id: int,
    predicted_digit: int,
    probabilities_json: str,
    thumbnail: str,
) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO histories (user_id, predicted_digit, probabilities_json, thumbnail)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, predicted_digit, probabilities_json, thumbnail),
        )


def get_history(db_path: Path, user_id: int, limit: int = 30) -> list[dict]:
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT predicted_digit, probabilities_json, thumbnail, created_at
            FROM histories
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()

    result = []
    for row in rows:
        probabilities = json.loads(row["probabilities_json"])
        confidence = max(probabilities) if probabilities else 0.0
        result.append(
            {
                "predicted_digit": row["predicted_digit"],
                "probabilities": probabilities,
                "confidence": confidence,
                "thumbnail": row["thumbnail"],
                "created_at": row["created_at"],
            }
        )
    return result
