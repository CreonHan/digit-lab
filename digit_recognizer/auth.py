from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3
from pathlib import Path

from digit_recognizer.database import get_connection


def _hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return salt.hex(), digest.hex()


def create_user(db_path: Path, username: str, password: str) -> bool:
    salt, password_hash = _hash_password(password)
    try:
        with get_connection(db_path) as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                (username, password_hash, salt),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def verify_user(db_path: Path, username: str, password: str) -> dict | None:
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT id, username, password_hash, salt FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    if row is None:
        return None

    _, password_hash = _hash_password(password, bytes.fromhex(row["salt"]))
    if hmac.compare_digest(password_hash, row["password_hash"]):
        return {"id": row["id"], "username": row["username"]}
    return None
