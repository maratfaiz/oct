import os
import sqlite3
from typing import TypedDict

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "octera.db")
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "uploads")


class ImageRecord(TypedDict):
    status: str
    label: str
    confidence: float


def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS images (
            image_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            label TEXT,
            confidence REAL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    return conn


def save(image_id: str, record: ImageRecord) -> None:
    conn = _connect()
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO images (image_id, status, label, confidence) VALUES (?, ?, ?, ?)",
            (image_id, record["status"], record["label"], record["confidence"]),
        )
    conn.close()


def get(image_id: str) -> ImageRecord | None:
    conn = _connect()
    row = conn.execute(
        "SELECT status, label, confidence FROM images WHERE image_id = ?", (image_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return {"status": row[0], "label": row[1], "confidence": row[2]}


def save_image_file(image_id: str, image_bytes: bytes) -> str:
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    path = os.path.join(UPLOADS_DIR, image_id)
    with open(path, "wb") as f:
        f.write(image_bytes)
    return path
