import sqlite3
import os

from dotenv import load_dotenv

load_dotenv()

DB_FILE = os.getenv("DB_FILE")


def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                activity_id TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                action TEXT,
                type TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                anilistID TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

def insert_activity(username, timestamp, activity_id, title, action, type):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO activities (username, timestamp, activity_id, title, action, type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, timestamp, activity_id, title, action, type))
            conn.commit()
        except sqlite3.IntegrityError:
            print("[!] Fehler bei Eintragung von Aktivitäten in die Datenbank!")
            pass

def insert_user(username, anilistID, password):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO user (username, anilistID, password)
                VALUES (?, ?)
            ''', (username, anilistID, password))
            conn.commit()
        except sqlite3.IntegrityError:
            print(f"[!] Fehler bei Eintragung von {username} in die Datenbank!")
            pass

def get_all_activities():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT username, timestamp, activity_id, title, chapters, type FROM activities ORDER BY timestamp DESC')
        return c.fetchall()
    
def get_all_activity_ids(username):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT activity_id FROM activities WHERE username = ? ORDER BY timestamp DESC', (username))
        return c.fetchall()