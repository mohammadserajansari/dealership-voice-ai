import sqlite3
import json
from datetime import datetime

DB_PATH = "bookings.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS bookings (id INTEGER PRIMARY KEY AUTOINCREMENT, model TEXT, date TEXT, time TEXT, created_at TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS sessions (session_id TEXT PRIMARY KEY, history TEXT, pending_data TEXT)")
        conn.commit()

def get_session_memory(session_id):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT history, pending_data FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
        return {"history": row[0] or "", "pending": json.loads(row[1]) if row[1] else None} if row else {"history": "", "pending": None}

def save_session_memory(session_id, history, pending=None):
    truncated_history = "\n".join(history.strip().split("\n")[-8:])
    pending_json = json.dumps(pending) if pending else None
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO sessions (session_id, history, pending_data) VALUES (?, ?, ?) ON CONFLICT(session_id) DO UPDATE SET history = excluded.history, pending_data = excluded.pending_data", (session_id, truncated_history, pending_json))
        conn.commit()

def log_booking(model, date, time_slot):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO bookings (model, date, time, created_at) VALUES (?,?,?,?)", (model, date, time_slot, datetime.utcnow().isoformat()))
        conn.commit()
        return cur.lastrowid