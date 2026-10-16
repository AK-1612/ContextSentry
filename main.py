import os
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.hook import PreToolUseHook
from core.worker_reader import BulkReadWorker
from core.worker_writer import BulkWriteWorker
from core.monitor import TelemetryMonitor

app = typer.Typer(help="ContextSentry: PreToolUse Interceptor & Context Optimizer CLI")
console = Console()

hook = PreToolUseHook()
worker = BulkReadWorker()
writer = BulkWriteWorker()
monitor = TelemetryMonitor()


@app.command()
def read(
    file_path: str = typer.Argument(..., help="Path to file requested by agent"),
    query: str = typer.Option("Extract core structure and key symbols.", "--query", "-q", help="Specific focus query")
):
    """
    Intercepts a file read tool call and evaluates context bounds before returning data.
    """
    console.print(f"\n[bold yellow]ContextSentry Intercepting Read:[/] [cyan]{file_path}[/]")

    if not os.path.exists(file_path):
        console.print(Panel(f"[bold yellow]FILE NOT FOUND[/]\nPath '{file_path}' does not exist on disk.", title="PreToolUse Gate", border_style="yellow"))
        return

    should_pass, line_count, reason = hook.inspect_file_read(file_path)
    monitor.log_interception(file_path, line_count, should_pass)

    if should_pass:
        console.print(Panel(f"[bold green]PASSED TO PRIMARY MODEL[/]\n{reason}", title="PreToolUse Gate"))
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        console.print(content)
    else:
        console.print(Panel(f"[bold red]BLOCKED & DELEGATED[/]\n{reason}", title="PreToolUse Gate"))
        console.print("\n[bold dim]Executing Bulk-Read Worker via local model...[/]")
        summary = worker.summarize_large_file(file_path, query)
        
        console.print(Panel(summary, title="Offloaded Bullet Summary (Primary Context Preserved)", border_style="cyan"))


@app.command()
def write(
    file_path: str = typer.Argument(..., help="Path to write generated file to"),
    prompt: str = typer.Option(..., "--prompt", "-p", help="Specification for generated code")
):
    """
    Generates code offloaded via local model and writes directly to disk.
    """
    console.print(f"\n[bold yellow]ContextSentry Intercepting Write:[/] [cyan]{file_path}[/]")
    console.print("[bold dim]Delegating code generation directly to local worker model...[/]")

    result = writer.write_code_to_disk(file_path, prompt)
    console.print(Panel(result, title="Direct-To-Disk Writer Action", border_style="green"))


@app.command()
def stats():
    """
    Displays telemetry statistics and estimated token/dollar savings from SQLite.
    """
    data = monitor.get_summary_stats()

    console.print("\n[bold cyan]=== ContextSentry Telemetry & Savings Ledger ===[/]\n")

    # Metrics Summary Table
    summary_table = Table(title="Aggregate Optimization Metrics", show_header=True, header_style="bold magenta")
    summary_table.add_column("Metric", style="dim")
    summary_table.add_column("Value", justify="right", style="bold green")

    summary_table.add_row("Total Read Requests Intercepted", str(data["total_reads"]))
    summary_table.add_row("Requests Passed (<= 350 lines)", str(data["total_passed"]))
    summary_table.add_row("Requests Blocked & Offloaded (> 350 lines)", str(data["total_blocked"]))
    summary_table.add_row("Total Code Lines Offloaded", f"{data['lines_offloaded']:,}")
    summary_table.add_row("Estimated Tokens Saved", f"{data['total_tokens_saved']:,}")
    summary_table.add_row("Est. Dollar Cost Saved (GPT-4o Rate)", f"${data['dollar_savings_est']:.4f}")

    console.print(summary_table)

    # Recent Executions Table
    if data["recent_logs"]:
        console.print("\n")
        logs_table = Table(title="Recent Execution History (Last 5 Events)", show_header=True, header_style="bold blue")
        logs_table.add_column("Timestamp", style="dim")
        logs_table.add_column("File Path", style="cyan")
        logs_table.add_column("Lines", justify="right")
        logs_table.add_column("Gate Action", justify="center")
        logs_table.add_column("Tokens Saved", justify="right", style="green")

        for log in data["recent_logs"]:
            file_path, lines, passed, saved_tokens, timestamp = log
            action_str = "[green]PASSED[/green]" if passed else "[bold red]BLOCKED[/bold red]"
            logs_table.add_row(timestamp, file_path, str(lines), action_str, f"{saved_tokens:,}")

        console.print(logs_table)


if __name__ == "__main__":
    app()