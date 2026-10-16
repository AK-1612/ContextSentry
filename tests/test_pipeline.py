import os
import sqlite3
import pytest
from core.hook import PreToolUseHook
from core.worker_reader import BulkReadWorker
from core.monitor import TelemetryMonitor

TEST_DB = "data/test_contextsentry.db"

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Sets up test files and cleans up databases after execution."""
    # Create small test file (10 lines)
    with open("tests/small_file.py", "w") as f:
        f.write("\n".join([f"print('line {i}')" for i in range(1, 11)]))

    # Create large test file (400 lines)
    with open("tests/large_file.py", "w") as f:
        f.write("\n".join([f"def function_{i}(): return {i}" for i in range(1, 401)]))

    yield

    # Clean up artifacts
    for path in ["tests/small_file.py", "tests/large_file.py", TEST_DB]:
        if os.path.exists(path):
            os.remove(path)

def test_small_file_passes_gate():
    """Validates that files under 350 lines pass without offloading."""
    hook = PreToolUseHook(line_threshold=350)
    should_pass, line_count, reason = hook.inspect_file_read("tests/small_file.py")

    assert should_pass is True
    assert line_count == 10
    assert "Pass" in reason

def test_large_file_blocks_and_delegates():
    """Validates that files over 350 lines are blocked and offloaded to worker LLM."""
    hook = PreToolUseHook(line_threshold=350)
    worker = BulkReadWorker(model="llama3.2")
    monitor = TelemetryMonitor(db_path=TEST_DB)

    file_path = "tests/large_file.py"
    should_pass, line_count, reason = hook.inspect_file_read(file_path)

    # 1. Gate Inspection Check
    assert should_pass is False
    assert line_count == 400
    assert "Block" in reason

    # 2. Worker LLM Offload Check
    summary = worker.summarize_large_file(file_path, "Extract function definitions")
    assert isinstance(summary, str)
    assert len(summary) > 0
    assert "[BulkRead Fallback]" not in summary

    # 3. Telemetry Log Verification
    monitor.log_interception(file_path, line_count, should_pass)
    
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT file_path, line_count, passed_to_primary, saved_tokens_est FROM executions")
    record = cursor.fetchone()
    conn.close()

    assert record[0] == file_path
    assert record[1] == 400
    assert record[2] == 0  # False / Blocked
    assert record[3] == 4000  # 400 lines * 10 estimated tokens