import os
import requests

class BulkReadWorker:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama3.2", timeout: int = 90):
        self.ollama_url = ollama_url
        self.model = model
        self.timeout = timeout

    def summarize_large_file(self, file_path: str, user_query: str) -> str:
        """
        Offloads large file parsing to a low-cost worker model.
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            prompt = f"""
You are a fast, low-cost bulk-reader worker model.
Examine the following file wrapped in XML tags and answer the user query concisely.

Rules:
- Output ONLY bullet points.
- Include specific line numbers or symbol names where relevant.
- Do NOT output preamble, conversational filler, or code fences.

<file_path>{file_path}</file_path>
<file_content>
{content}
</file_content>

User Query: {user_query}
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
                return response.json().get("response", "No summary generated.").strip()
            else:
                return f"[BulkRead Fallback]: Summary failed with status {response.status_code}."
        except Exception as e:
            return f"[BulkRead Fallback]: Local worker offline/unreachable - {str(e)}"