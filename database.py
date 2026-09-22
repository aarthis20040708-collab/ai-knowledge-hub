import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "app_data.db")

def get_db_connection():
    """Returns a SQLite connection with row dictionary access."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates the necessary database tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Workspaces Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workspaces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # 3. Conversations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        workspace_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
    )
    """)

    # 4. Messages Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()


# --- Password Hashing ---
def hash_password(password: str) -> str:
    """Hashes a password using SHA-256 with a salt."""
    salt = "ai_projects_secure_salt_2026"
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()


# --- User Authentication Operations ---
def create_user(username: str, password: str):
    """Registers a new user and creates their default workspace."""
    username = username.strip().lower()
    if not username or not password:
        return False, "Username and password cannot be empty."

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        pw_hash = hash_password(password)
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pw_hash))
        user_id = cursor.lastrowid

        # Create a default workspace for this user
        cursor.execute("INSERT INTO workspaces (user_id, name, description) VALUES (?, ?, ?)", 
                       (user_id, "Default Workspace", "General workspace for daily tasks"))
        conn.commit()
        return True, "Account created successfully! You can now log in."
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose another."
    except Exception as e:
        return False, f"Error creating account: {str(e)}"
    finally:
        conn.close()


def authenticate_user(username: str, password: str):
    """Verifies user credentials and returns the user record if valid."""
    username = username.strip().lower()
    pw_hash = hash_password(password)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE username = ? AND password_hash = ?", (username, pw_hash))
    user = cursor.fetchone()
    conn.close()

    if user:
        return dict(user)
    return None


# --- Workspace Operations ---
def get_user_workspaces(user_id: int):
    """Returns all workspaces belonging to the user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description FROM workspaces WHERE user_id = ? ORDER BY id ASC", (user_id,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def create_workspace(user_id: int, name: str, description: str = ""):
    """Creates a new custom workspace for the user."""
    name = name.strip()
    if not name:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO workspaces (user_id, name, description) VALUES (?, ?, ?)", (user_id, name, description))
    conn.commit()
    ws_id = cursor.lastrowid
    conn.close()
    return ws_id


# --- Conversation Operations ---
def create_conversation(user_id: int, workspace_id: int, title: str = "New Chat"):
    """Creates a new conversation thread."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversations (user_id, workspace_id, title) VALUES (?, ?, ?)", 
                   (user_id, workspace_id, title))
    conn.commit()
    conv_id = cursor.lastrowid
    conn.close()
    return conv_id


def get_conversations(user_id: int, workspace_id: int):
    """Retrieves all conversation sessions in a workspace."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, updated_at 
        FROM conversations 
        WHERE user_id = ? AND workspace_id = ? 
        ORDER BY updated_at DESC
    """, (user_id, workspace_id))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_conversation_messages(conversation_id: int):
    """Retrieves all messages for a specific conversation."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, content, created_at FROM messages WHERE conversation_id = ? ORDER BY id ASC", (conversation_id,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def save_message(conversation_id: int, role: str, content: str):
    """Saves a user or assistant message to the database and touches updated_at."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)", (conversation_id, role, content))
    cursor.execute("UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (conversation_id,))
    conn.commit()
    conn.close()


def update_conversation_title(conversation_id: int, title: str):
    """Updates the title of a conversation."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE conversations SET title = ? WHERE id = ?", (title, conversation_id))
    conn.commit()
    conn.close()


def delete_conversation(conversation_id: int):
    """Deletes a conversation and its messages."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    conn.commit()
    conn.close()


# --- Search History Operations ---
def search_messages(user_id: int, query: str, workspace_id: int = None):
    """
    Searches across message content and conversation titles for the given user.
    """
    if not query.strip():
        return []

    conn = get_db_connection()
    cursor = conn.cursor()
    like_query = f"%{query.strip()}%"

    if workspace_id:
        cursor.execute("""
            SELECT m.id, m.conversation_id, m.role, m.content, m.created_at, c.title as conversation_title, w.name as workspace_name
            FROM messages m
            JOIN conversations c ON m.conversation_id = c.id
            JOIN workspaces w ON c.workspace_id = w.id
            WHERE c.user_id = ? AND c.workspace_id = ? AND (m.content LIKE ? OR c.title LIKE ?)
            ORDER BY m.created_at DESC
            LIMIT 30
        """, (user_id, workspace_id, like_query, like_query))
    else:
        cursor.execute("""
            SELECT m.id, m.conversation_id, m.role, m.content, m.created_at, c.title as conversation_title, w.name as workspace_name
            FROM messages m
            JOIN conversations c ON m.conversation_id = c.id
            JOIN workspaces w ON c.workspace_id = w.id
            WHERE c.user_id = ? AND (m.content LIKE ? OR c.title LIKE ?)
            ORDER BY m.created_at DESC
            LIMIT 30
        """, (user_id, like_query, like_query))

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

# Initialize DB on load
init_db()
