import sqlite3
from datetime import datetime

DB_PATH = "done.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS done_meals (
                meal_id INTEGER PRIMARY KEY,
                done_at TEXT
            )
        """)
        conn.commit()

def mark_done(meal_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO done_meals (meal_id, done_at) VALUES (?, ?)",
            (meal_id, datetime.utcnow().isoformat())
        )
        conn.commit()

def is_done(meal_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM done_meals WHERE meal_id = ?", (meal_id,))
        return cursor.fetchone() is not None

def get_all_done_ids():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT meal_id FROM done_meals")
        return [row[0] for row in cursor.fetchall()]

def re_add(meal_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM done_meals WHERE meal_id = ?", (meal_id,))
        conn.commit()
