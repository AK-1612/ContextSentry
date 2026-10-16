import os
import requests

class BulkWriteWorker:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama3.2", timeout: int = 90):
        self.ollama_url = ollama_url
        self.model = model
        self.timeout = timeout

    def write_code_to_disk(self, target_path: str, specification: str) -> str:
        """
        Generates code directly to disk via local worker LLM without flooding primary context.
        """
        try:
            prompt = f"""
You are a fast local code-writing worker.
Write clean, working Python code based on the specification below.

Rules:
- Output ONLY valid code.
- Do NOT output markdown code fences, conversational preamble, or explanations.
- The output will be saved directly to file path: {target_path}

Specification:
{specification}
"""

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "options": {"temperature": 0.2},
                    "stream": False
                },
                timeout=self.timeout
            )

            if response.status_code == 200:
                raw_code = response.json().get("response", "").strip()

                # Clean up any residual markdown formatting if model includes it
                if raw_code.startswith("```"):
                    lines = raw_code.splitlines()
                    raw_code = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])

                os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(raw_code)

                line_count = len(raw_code.splitlines())
                return f"Successfully generated {line_count} lines of code directly to '{target_path}'."
            else:
                return f"[BulkWrite Fallback]: Generation failed with status {response.status_code}."
        except Exception as e:
            return f"[BulkWrite Fallback]: Local worker error - {str(e)}"