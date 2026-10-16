import os
from mcp.server.mcpserver import MCPServer
from core.hook import PreToolUseHook
from core.worker_reader import BulkReadWorker
from core.worker_writer import BulkWriteWorker
from core.monitor import TelemetryMonitor

# Initialize MCP Server v2
mcp = MCPServer("ContextSentry-Gatekeeper")

# Initialize core Sentry services
hook = PreToolUseHook(line_threshold=350)
reader_worker = BulkReadWorker()
writer_worker = BulkWriteWorker()
monitor = TelemetryMonitor()


@mcp.tool()
def intercept_read_file(file_path: str, query: str = "Extract core structure and key symbols.") -> str:
    """
    Intercepts file read operations. Files under 350 lines return full content.
    Files over 350 lines are blocked and summarized via local Ollama worker.
    """
    if not os.path.exists(file_path):
        return f"[ContextSentry Gate]: File '{file_path}' does not exist on disk."

    should_pass, line_count, reason = hook.inspect_file_read(file_path)
    monitor.log_interception(file_path, line_count, should_pass)

    if should_pass:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return f"[ContextSentry Gate: PASSED ({line_count} lines)]\n\n{content}"
    else:
        summary = reader_worker.summarize_large_file(file_path, query)
        return (
            f"[ContextSentry Gate: BLOCKED & DELEGATED ({line_count} lines > 350)]\n"
            f"Primary context preserved. Summary offloaded to local worker:\n\n"
            f"{summary}"
        )


@mcp.tool()
def intercept_write_file(target_path: str, specification: str) -> str:
    """
    Offloads large file generation directly to disk via local model to keep conversation history clean.
    """
    result = writer_worker.write_code_to_disk(target_path, specification)
    return f"[ContextSentry Gate: DIRECT-TO-DISK WRITE]\n{result}"


@mcp.tool()
def get_telemetry_stats() -> str:
    """
    Returns total intercepted requests, offloaded line counts, and estimated token/dollar savings.
    """
    data = monitor.get_summary_stats()
    return (
        f"=== ContextSentry Telemetry Ledger ===\n"
        f"Total Reads Intercepted: {data['total_reads']}\n"
        f"Passed (<= 350 lines): {data['total_passed']}\n"
        f"Blocked (> 350 lines): {data['total_blocked']}\n"
        f"Lines Offloaded: {data['lines_offloaded']:,}\n"
        f"Tokens Saved: {data['total_tokens_saved']:,}\n"
        f"Estimated Dollar Savings (GPT-4o): ${data['dollar_savings_est']:.4f}"
    )


if __name__ == "__main__":
    mcp.run()