# core/security.py
import re
from typing import Tuple

class SecretRedactor:
    """Scrubs hardcoded credentials, tokens, IP addresses, and private keys."""

    PATTERNS = {
        "api_key": r'(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*["\']([A-Za-z0-9_\-]{16,})["\']',
        "jwt": r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',
        "ipv4": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        "private_key": r'-----BEGIN ((?:RSA |EC )?PRIVATE KEY)-----[\s\S]*?-----END \1-----',
    }

    @classmethod
    def sanitize(cls, content: str) -> Tuple[str, int]:
        redacted_content = content
        total_redactions = 0

        for secret_type, pattern in cls.PATTERNS.items():
            matches = len(re.findall(pattern, redacted_content))
            if matches > 0:
                total_redactions += matches
                redacted_content = re.sub(
                    pattern,
                    f'[REDACTED_{secret_type.upper()}]',
                    redacted_content
                )

        return redacted_content, total_redactions