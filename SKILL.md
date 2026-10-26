---
name: contextsentry
description: Use ContextSentry MCP tools to summarize large files, verify key details against source, and interpret telemetry estimates. Applies when the ContextSentry server is connected; does not install the server or intercept reads automatically.
---

# ContextSentry

Use this skill when the ContextSentry MCP server is available and a task involves inspecting large files or reviewing ContextSentry telemetry.

## Read large files

- Call `intercept_read_file` with the file path and a focused question tied to the task.
- Treat the returned summary as a guide to relevant symbols and line ranges, not as proof of exact source behavior. Read the relevant source directly before relying on details or changing code.
- For small files, exact text, or a narrow known range, use the normal file-reading tools.
- If the MCP tool is unavailable or returns a fallback/error, continue with ordinary targeted reads where possible. Do not infer content from the error.

The current MCP tool is opt-in: it handles reads routed through `intercept_read_file`. It does not automatically intercept every read made by an IDE or coding agent.

## Write files

`intercept_write_file` sends a generation request to the local worker and writes its output directly to the target path. Use it only when the user requested generated file output. Check the exact target first; do not overwrite an existing file unless the user has explicitly authorized that overwrite. Inspect generated output before treating it as usable.

## Interpret telemetry

- Use `get_telemetry_stats` when asked for ContextSentry usage statistics.
- Describe token and cost figures as estimates. The current implementation estimates 10 tokens per blocked line and applies a fixed GPT-4o input rate; these are not measured token counts or realized savings.
- Interception counts alone do not establish summary quality, productivity gains, or cost reduction.

## Data and integration context

The reader sends file contents to the configured Ollama endpoint. Use the tool only where that endpoint is approved for the repository's data.

This skill provides instructions; it does not configure or install an MCP server. A GitHub Copilot custom agent profile is a separate integration artifact and may expose MCP tools only when the selected Copilot client and organization policy support them. Do not describe the skill as a Copilot agent or as an automatic PreToolUse hook.
