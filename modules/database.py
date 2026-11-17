import json
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "clipquest.db"


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                language TEXT,
                transcript TEXT,
                chapters TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_media(name, file_path, language, transcript, chapters):
    if not str(name).strip():
        raise ValueError("Media name cannot be empty.")

    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO media
            (name, file_path, language, transcript, chapters)
            VALUES (?, ?, ?, ?, ?)
        """, (
            str(name).strip(),
            str(file_path),
            language,
            transcript or "",
            json.dumps(chapters or [], ensure_ascii=False)
        ))
        return cursor.lastrowid


def get_all_media():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM media ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_media_by_id(media_id):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM media WHERE id = ?",
            (media_id,)
        ).fetchone()
        return dict(row) if row else None


def delete_media(media_id):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM media WHERE id = ?",
            (media_id,)
        )
        return cursor.rowcount > 0


def update_media_name(media_id, new_name):
    new_name = str(new_name).strip()

    if not new_name:
        raise ValueError("Media name cannot be empty.")

    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE media SET name = ? WHERE id = ?",
            (new_name, media_id)
        )
        return cursor.rowcount > 0