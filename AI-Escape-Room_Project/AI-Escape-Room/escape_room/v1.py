"""V1: conversational baseline. Deliberately trusts model narration."""
from .config import V1_SYSTEM
from .llm import generate


def turn(history, message, generator=generate):
    # Return new history only after a successful request, so retries are clean.
    pending = [*history, {"role": "user", "content": message}]
    reply = generator(V1_SYSTEM, pending)
    return [*pending, {"role": "assistant", "content": reply}], "[ESCAPED]" in reply
