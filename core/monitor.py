import os
import sqlite3
import threading
from typing import Dict, Any, List, Tuple

class TelemetryMonitor:
    def __init__(self, db_path: str = "data/contextsentry.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    line_count INTEGER NOT NULL,
                    passed_to_primary BOOLEAN NOT NULL,
                    saved_tokens_est INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()

    def log_interception(self, file_path: str, line_count: int, passed: bool):
        # Estimate ~10 tokens per line saved if blocked
        saved_tokens = 0 if passed else line_count * 10
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO executions (file_path, line_count, passed_to_primary, saved_tokens_est)
                VALUES (?, ?, ?, ?)
            """, (file_path, line_count, passed, saved_tokens))
            conn.commit()
            conn.close()

    def get_summary_stats(self) -> Dict[str, Any]:
        """Fetches aggregated telemetry metrics from SQLite."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM executions")
            total_reads = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*) FROM executions WHERE passed_to_primary = 0")
            total_blocked = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(line_count) FROM executions WHERE passed_to_primary = 0")
            lines_offloaded = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(saved_tokens_est) FROM executions")
            total_tokens_saved = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT file_path, line_count, passed_to_primary, saved_tokens_est, timestamp 
                FROM executions ORDER BY id DESC LIMIT 5
            """)
            recent_logs = cursor.fetchall()

            conn.close()

        # Estimated GPT-4o input cost: ~$2.50 per 1M tokens
        dollar_savings = (total_tokens_saved / 1_000_000) * 2.50

        return {
            "total_reads": total_reads,
            "total_blocked": total_blocked,
            "total_passed": total_reads - total_blocked,
            "lines_offloaded": lines_offloaded,
            "total_tokens_saved": total_tokens_saved,
            "dollar_savings_est": dollar_savings,
            "recent_logs": recent_logs
        }