import sqlite3
from pathlib import Path

DB_DIR = Path("data")
DB_NAME = DB_DIR / "developer_toolkit.db"

def get_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(DB_NAME))

def initialize_database():
    conn = get_connection()
    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS Settings (
        Id INTEGER PRIMARY KEY,
        Prompt TEXT,
        OneDrivePath TEXT,
        FastModelName TEXT,
        FinalModelName TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS Journals (
        Id INTEGER PRIMARY KEY,
        FileName TEXT,
        GeneratedAt TEXT,
        JournalContent TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS ToolUsage (
        UsageId INTEGER PRIMARY KEY AUTOINCREMENT,
        ToolName TEXT NOT NULL,
        ActionName TEXT NOT NULL,
        UsedAt DATETIME NOT NULL,
        TotalDurationMs INTEGER,
        PreprocessDurationMs INTEGER,
        AiDurationMs INTEGER,
        PostprocessDurationMs INTEGER,
        ModelName TEXT,
        InputSize INTEGER,
        OutputSize INTEGER,
        Metadata TEXT
    )
    """)

    conn.commit()
    conn.close()