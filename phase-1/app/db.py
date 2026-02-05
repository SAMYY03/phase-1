
import sqlite3
# sqlite3 is Python’s built-in library for using SQLite databases

import json
# json is used to convert Python lists/dictionaries into text

from typing import List, Dict, Optional
# typing is used to describe return types

DB_PATH = "storage/chat.db"

# DB connection
def get_conn():
   
    return sqlite3.connect(DB_PATH)
    # Every database operation needs a connection


# CREATE TABLES

def init_db():
  
    conn = get_conn()        # Open database connection
    cur = conn.cursor()      # Cursor lets us execute SQL commands

    # chat sessions
    # Stores one row per conversation session
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_sessions (
      session_id TEXT PRIMARY KEY,             
      created_at TEXT DEFAULT (datetime('now')) 
    )
    """)

    # chat messages
    # Stores all user and assistant messages
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,     
      session_id TEXT NOT NULL,                 
      role TEXT NOT NULL,                       
      content TEXT NOT NULL,                    
      created_at TEXT DEFAULT (datetime('now')) 
    )
    """)

    
    # retrieval logs
    # Stores RAG retrieval information
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

    conn.commit()   # Save changes to database file
    conn.close()    # Close database connection


# ENSURE SESSION EXISTS

def ensure_session(session_id: str):
    """
    Ensure a chat session exists.
    If it already exists, do nothing.
    """
    conn = get_conn()
    cur = conn.cursor()

    
    #  insert if session does not exist or ignore if session already exists
    cur.execute(
        "INSERT OR IGNORE INTO chat_sessions(session_id) VALUES(?)",
        (session_id,)
    )

    conn.commit()
    conn.close()


# Save msg

def save_message(session_id: str, role: str, content: str) -> int:
    """
    Save a user or assistant message.
    Returns the message ID.
    """
    conn = get_conn()
    cur = conn.cursor()

    # Insert message into chat_messages table
    cur.execute(
        "INSERT INTO chat_messages(session_id, role, content) VALUES(?,?,?)",
        (session_id, role, content)
    )

    msg_id = cur.lastrowid
    # lastrowid gives the ID of the inserted row

    conn.commit()
    conn.close()

    return msg_id


# chat history

def get_history(session_id: str, limit: int = 8) -> List[Dict]:
    """
    Get the last N messages from a session.
    Returns messages in chronological order.
    """
    conn = get_conn()
    cur = conn.cursor()

    # Select messages for a session
    # Order by id DESC gives newest first
    cur.execute("""
      SELECT role, content, created_at
      FROM chat_messages
      WHERE session_id = ?
      ORDER BY id DESC
      LIMIT ?
    """, (session_id, limit))

    rows = cur.fetchall()
    conn.close()

    # Reverse order so messages go from oldest → newest
    rows.reverse()

    # Convert rows into list of dictionaries
    return [
        {
            "role": r[0],
            "content": r[1],
            "created_at": r[2]
        }
        for r in rows
    ]


# save retrieval logs

def save_retrieval_log(
    session_id: str,
    user_message_id: int,
    top_k: int,
    best_score: float,
    retrieved: List[Dict]
):
    """
    Save retrieval evidence for RAG.
    This allows debugging and transparency.
    """
    conn = get_conn()
    cur = conn.cursor()

    # Convert retrieved chunks into JSON text
    retrieved_json = json.dumps(retrieved, ensure_ascii=False)

    cur.execute("""
      INSERT INTO retrieval_logs(
        session_id,
        user_message_id,
        top_k,
        best_score,
        retrieved_json
      )
      VALUES(?,?,?,?,?)
    """, (
        session_id,
        user_message_id,
        top_k,
        best_score,
        retrieved_json
    ))

    conn.commit()
    conn.close()
