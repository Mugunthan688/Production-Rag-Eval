import re
import logging

logger = logging.getLogger(__name__)


class GuardrailDetector:
    """Detects prompt injections, system prompt leaks, and jailbreak attempts."""

    INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"disregard prior directives",
        r"system prompt:",
        r"reveal your system prompt",
        r"you are now in developer mode",
    ]

    def detect_injection(self, text: str) -> bool:
        lower_text = text.lower()
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, lower_text):
                logger.warning(f"Guardrail triggered for pattern match: {pattern}")
                return True
        return False
