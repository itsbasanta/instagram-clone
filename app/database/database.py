import os
import sqlite3
from flask import g
from contextlib import closing

# ---------------------- Database Configuration ---------------------- #
DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')

# ---------------------- Connect to the Database ---------------------- #
def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # To get rows as dictionaries
    return g.db

# ---------------------- Close the Database Connection ---------------------- #
def close_db(e=None):
    """Closes the database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ---------------------- Initialize the Database ---------------------- #
def init_db():
    """Initializes the database by creating tables."""
    with closing(get_db()) as db:
        with open(os.path.join(os.path.dirname(__file__), 'schema.sql'), 'r') as f:
            db.executescript(f.read())
        db.commit()

# ---------------------- Execute SQL Queries ---------------------- #
def execute_query(query, args=(), commit=False):
    """Executes a query (select, insert, update, delete) on the database."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, args)
    
    if commit:
        db.commit()  # Commit changes if necessary
    
    if query.strip().upper().startswith("SELECT"):
        return cursor.fetchall()  # Return rows for SELECT queries
    else:
        return cursor.lastrowid  # Return last insert ID for non-SELECT queries

# ---------------------- Query Wrapper for Insert/Update/Delete ---------------------- #
def execute_insert(query, args):
    """Executes an insert query."""
    return execute_query(query, args, commit=True)

def execute_update(query, args):
    """Executes an update query."""
    return execute_query(query, args, commit=True)

def execute_delete(query, args):
    """Executes a delete query."""
    return execute_query(query, args, commit=True)

# ---------------------- Fetch a Single Record ---------------------- #
def fetch_one(query, args=()):
    """Fetches a single record from the database."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, args)
    return cursor.fetchone()

# ---------------------- Fetch Multiple Records ---------------------- #
def fetch_all(query, args=()):
    """Fetches all records matching the query."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, args)
    return cursor.fetchall()

# ---------------------- Example of Creating Tables ---------------------- #
def create_tables():
    """Creates all necessary tables for the app."""
    # User table schema
    user_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            profile_picture TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """
    
    # Post table schema
    post_table = """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    """
    
    # Other table schemas (messages, stories, notifications, etc.) can go here

    with closing(get_db()) as db:
        db.execute(user_table)
        db.execute(post_table)
        db.commit()

# ---------------------- Custom Query Examples ---------------------- #

def get_user_by_username(username):
    """Fetches a user by username."""
    query = "SELECT * FROM users WHERE username = ?"
    return fetch_one(query, (username,))

def get_all_posts():
    """Fetches all posts."""
    query = "SELECT * FROM posts"
    return fetch_all(query)

def get_user_posts(user_id):
    """Fetches posts for a specific user."""
    query = "SELECT * FROM posts WHERE user_id = ?"
    return fetch_all(query, (user_id,))

def get_post_by_id(post_id):
    """Fetches a post by its ID."""
    query = "SELECT * FROM posts WHERE id = ?"
    return fetch_one(query, (post_id,))

def add_new_post(user_id, title, content):
    """Inserts a new post."""
    query = "INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)"
    return execute_insert(query, (user_id, title, content))

# ---------------------- Closing the Database ---------------------- #
def close_all():
    """Ensure all resources are cleaned up."""
    close_db()
    if hasattr(g, 'db'):
        g.db.close()
