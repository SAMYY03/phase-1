import sqlite3
import json
from typing import List, Dict, Optional

DB_PATH = "storage/chat.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_sessions (
      session_id TEXT PRIMARY KEY,
      created_at TEXT DEFAULT (datetime('now'))
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id TEXT NOT NULL,
      role TEXT NOT NULL,
      content TEXT NOT NULL,
      created_at TEXT DEFAULT (datetime('now'))
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS retrieval_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id TEXT NOT NULL,
      user_message_id INTEGER,
      top_k INTEGER NOT NULL,
      best_score REAL,
      retrieved_json TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    )
    """)

    conn.commit()
    conn.close()

def ensure_session(session_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO chat_sessions(session_id) VALUES(?)", (session_id,))
    conn.commit()
    conn.close()

def save_message(session_id: str, role: str, content: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_messages(session_id, role, content) VALUES(?,?,?)",
        (session_id, role, content),
    )
    msg_id = cur.lastrowid
    conn.commit()
    conn.close()
    return msg_id

def get_history(session_id: str, limit: int = 8) -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
      SELECT role, content, created_at
      FROM chat_messages
      WHERE session_id = ?
      ORDER BY id DESC
      LIMIT ?
    """, (session_id, limit))
    rows = cur.fetchall()
    conn.close()

    # reverse so oldest->newest
    rows.reverse()
    return [{"role": r[0], "content": r[1], "created_at": r[2]} for r in rows]

def save_retrieval_log(session_id: str, user_message_id: int, top_k: int, best_score: float, retrieved: List[Dict]):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
      INSERT INTO retrieval_logs(session_id, user_message_id, top_k, best_score, retrieved_json)
      VALUES(?,?,?,?,?)
    """, (session_id, user_message_id, top_k, best_score, json.dumps(retrieved, ensure_ascii=False)))
    conn.commit()
    conn.close()
