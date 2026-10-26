---
name: contextsentry
description: Use the connected ContextSentry MCP tools to inspect files through its size and complexity gate, request focused summaries, generate requested files, and review telemetry estimates. The server is opt-in and must already be configured and running.
---

# ContextSentry Skill

Use this skill when the ContextSentry MCP server is connected and the task involves reading a large file, generating a requested file through the local worker, or reviewing ContextSentry telemetry.

## Read and summarize files

1. For a large file, call `intercept_read_file` with its path and a focused query, such as “Find the public entry points and explain how they interact.”
2. The current gate blocks files over 350 lines or Python files with calculated cyclomatic complexity over 15. It returns smaller files directly and routes gated files to the configured Ollama worker (`llama3.2` by default).
3. Treat summaries and symbol ranges as navigation aids. For exact behavior, quoted text, or code changes, inspect the relevant source lines directly and verify the details.
4. If the tool is missing, returns a worker fallback/error, or the file is small or the request needs exact text, use ordinary targeted file reads where possible. Do not infer file contents from an error response.

The MCP tool is opt-in: only reads explicitly routed through `intercept_read_file` pass through ContextSentry. It does not automatically intercept normal IDE or coding-agent reads.

## Generate files

- Use `intercept_write_file` only when the user asks for generated file output. Provide the exact target path and a clear specification.
- Check whether the target already exists before calling the tool. Do not overwrite an existing file unless the user authorized that overwrite.
- Review the generated file after the tool reports success; model output may need correction and should not be treated as verified code.

## Review telemetry

- Call `get_telemetry_stats` when asked for ContextSentry usage or savings statistics.
- Explain that token savings use a rough estimate of 10 tokens per blocked line, and dollar savings apply a fixed GPT-4o input price. These figures are not tokenizer measurements, actual billing, or proof of productivity gains or summary quality.
- The CLI also offers `python main.py stats` for local telemetry.

## Data handling and integration limits

- The worker reader sends file contents to the configured Ollama endpoint. Use it only when that endpoint is approved for the file's data.
- The current secret-pattern scan is not end-to-end redaction: the worker reader reopens and sends the original file contents. Do not claim detected secrets are removed from the worker request.
- Ollama is the implemented worker backend. Do not imply an Azure/EY endpoint is configured unless the project has since added and verified one.
- This skill provides usage guidance; it does not install or configure the MCP server, and it is not an automatic PreToolUse hook. A client must have the ContextSentry MCP server configured and running for these tools to be available.
