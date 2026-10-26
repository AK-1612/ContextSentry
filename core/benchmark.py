# core/benchmark.py
import sqlite3
import time

def init_benchmark_db(db_path: str = "data/contextsentry.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS benchmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT,
            raw_lines INTEGER,
            raw_tokens INTEGER,
            injected_tokens INTEGER,
            token_savings_pct REAL,
            latency_ms REAL,
            secrets_redacted INTEGER,
            complexity INTEGER
        )
    """)
    conn.commit()
    conn.close()

def log_benchmark_entry(
    file_path: str, 
    raw_lines: int, 
    raw_tokens: int, 
    injected_tokens: int, 
    latency_ms: float, 
    secrets: int, 
    complexity: int, 
    db_path: str = "data/contextsentry.db"
):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    savings = ((raw_tokens - injected_tokens) / raw_tokens) * 100 if raw_tokens > 0 else 0.0

    cursor.execute("""
        INSERT INTO benchmarks 
        (file_path, raw_lines, raw_tokens, injected_tokens, token_savings_pct, latency_ms, secrets_redacted, complexity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (file_path, raw_lines, raw_tokens, injected_tokens, savings, latency_ms, secrets, complexity))

    conn.commit()
    conn.close()