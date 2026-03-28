import sqlite3
import json

DB_PATH = "vidyapath.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            topic           TEXT NOT NULL,
            knowledge_level TEXT DEFAULT 'BEGINNER',
            messages        TEXT DEFAULT '[]',
            completed       INTEGER DEFAULT 0,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row


def create_user(username, hashed_password):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (username, hashed_password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def get_user_sessions(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, user_id, topic, knowledge_level, messages, completed
        FROM sessions
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows


def create_session(user_id, topic):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO sessions (user_id, topic, messages, completed)
        VALUES (?, ?, '[]', 0)
    """, (user_id, topic))
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    return session_id


def update_session(session_id, messages, knowledge_level=None, completed=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    messages_json = json.dumps(messages)

    if knowledge_level is not None and completed is not None:
        c.execute("""
            UPDATE sessions
            SET messages = ?, knowledge_level = ?, completed = ?
            WHERE id = ?
        """, (messages_json, knowledge_level, completed, session_id))
    elif knowledge_level is not None:
        c.execute("""
            UPDATE sessions
            SET messages = ?, knowledge_level = ?
            WHERE id = ?
        """, (messages_json, knowledge_level, session_id))
    elif completed is not None:
        c.execute("""
            UPDATE sessions
            SET messages = ?, completed = ?
            WHERE id = ?
        """, (messages_json, completed, session_id))
    else:
        c.execute("""
            UPDATE sessions
            SET messages = ?
            WHERE id = ?
        """, (messages_json, session_id))

    conn.commit()
    conn.close()