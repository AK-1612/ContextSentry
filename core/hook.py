import os
from typing import Tuple

LINE_THRESHOLD = 350

class PreToolUseHook:
    def __init__(self, line_threshold: int = LINE_THRESHOLD):
        self.line_threshold = line_threshold

    def inspect_file_read(self, file_path: str) -> Tuple[bool, int, str]:
        """
        Inspects a file before tool execution.
        Returns: (should_pass_to_primary, line_count, reason)
        """
        if not os.path.exists(file_path):
            return True, 0, f"File '{file_path}' does not exist."

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                line_count = len(lines)

            if line_count <= self.line_threshold:
                return True, line_count, f"Pass: File is {line_count} lines (<= {self.line_threshold})."
            else:
                return False, line_count, f"Block: File is {line_count} lines (> {self.line_threshold}). Offloading to bulk reader."
        except Exception as e:
            return True, 0, f"Error reading file bounds: {str(e)}"