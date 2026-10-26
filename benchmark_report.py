# benchmark_report.py
import sqlite3
import os
from pathlib import Path

DB_PATH = "data/contextsentry.db"
TEST_DB_PATH = "data/test_contextsentry.db"

def get_active_db():
    if os.path.exists(DB_PATH):
        return DB_PATH
    elif os.path.exists(TEST_DB_PATH):
        return TEST_DB_PATH
    return None

def print_professional_report():
    db_file = get_active_db()
    if not db_file:
        print("\n[!] Error: No telemetry database found in 'data/'. Please run your test suite or pipeline first.\n")
        return

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    print("\n" + "═" * 78)
    print(f"               CONTEXTSENTRY — ENTERPRISE TELEMETRY REPORT")
    print(f"               Target Database: {db_file}")
    print("═" * 78)

    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        # 1. Executions / Gating Telemetry
        if "executions" in tables:
            cursor.execute("""
                SELECT file_path, line_count, passed_to_primary, saved_tokens_est 
                FROM executions
            """)
            rows = cursor.fetchall()
            
            print("\n[+] Gating & Offloading Executions:")
            print(f" {'File Path':<35} │ {'Lines':<6} │ {'Status':<15} │ {'Est. Saved Tokens':<16}")
            print("─" * 78)
            
            total_saved = 0
            for file_path, line_count, passed, saved in rows:
                status = "Passed (Direct)" if passed else "Gated & Offloaded"
                saved_tokens = saved if saved else 0
                total_saved += saved_tokens
                print(f" {file_path:<35} │ {line_count:<6} │ {status:<15} │ {saved_tokens:<16}")
            print("─" * 78)
            print(f" Total Estimated Tokens Saved Across Interceptions: {total_saved}\n")

        # 2. Benchmark Logs / Detailed Latency & Security
        if "benchmark_logs" in tables:
            cursor.execute("""
                SELECT file_path, raw_lines, raw_tokens, injected_tokens, latency_ms, secrets, complexity 
                FROM benchmark_logs
            """)
            bench_rows = cursor.fetchall()
            
            print("[+] Detailed Performance & Security Audit:")
            print(f" {'File Path':<30} │ {'Latency (ms)':<12} │ {'Secrets Scrubbed':<16} │ {'Complexity':<10}")
            print("─" * 78)
            for file_path, lines, r_tok, i_tok, latency, secrets, comp in bench_rows:
                print(f" {file_path:<30} │ {latency:<12.2f} │ {secrets:<16} │ {comp:<10}")
            print("─" * 78 + "\n")

    except Exception as e:
        print(f"[!] Database query execution failed: {e}")
    finally:
        conn.close()

    print("═" * 78)
    print(" Report Generated Successfully | ContextSentry Governance Engine")
    print("═" * 78 + "\n")

if __name__ == "__main__":
    print_professional_report()