import sqlite3
from datetime import datetime

def init_database():
    """Initialize SQLite database with all required tables"""
    conn = sqlite3.connect('health_tracker.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE NOT NULL,
                  password_hash TEXT,
                  google_id TEXT UNIQUE,
                  full_name TEXT,
                  date_of_birth TEXT,
                  blood_group TEXT,
                  height REAL,
                  weight REAL,
                  allergies TEXT,
                  medications TEXT,
                  chronic_conditions TEXT,
                  emergency_contact TEXT,
                  created_at TEXT NOT NULL,
                  last_login TEXT NOT NULL)''')
    
    # Health logs table
    c.execute('''CREATE TABLE IF NOT EXISTS health_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  date TEXT NOT NULL,
                  symptoms TEXT,
                  severity_score INTEGER,
                  notes TEXT,
                  created_at TEXT NOT NULL,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Triage results table
    c.execute('''CREATE TABLE IF NOT EXISTS triage_results
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  symptoms TEXT NOT NULL,
                  triage_level TEXT NOT NULL,
                  confidence TEXT NOT NULL,
                  reasoning TEXT,
                  recommended_action TEXT,
                  detailed_analysis TEXT,
                  created_at TEXT NOT NULL,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Chat sessions table
    c.execute('''CREATE TABLE IF NOT EXISTS chat_sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  session_type TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Chat messages table
    c.execute('''CREATE TABLE IF NOT EXISTS chat_messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id INTEGER NOT NULL,
                  role TEXT NOT NULL,
                  content TEXT NOT NULL,
                  timestamp TEXT NOT NULL,
                  FOREIGN KEY (session_id) REFERENCES chat_sessions (id))''')
    
    # Daily streaks table
    c.execute('''CREATE TABLE IF NOT EXISTS daily_streaks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  date TEXT NOT NULL,
                  completed INTEGER DEFAULT 0,
                  created_at TEXT NOT NULL,
                  FOREIGN KEY (user_id) REFERENCES users (id),
                  UNIQUE(user_id, date))''')
    
    conn.commit()
    conn.close()

# Initialize database when this module is imported
init_database()