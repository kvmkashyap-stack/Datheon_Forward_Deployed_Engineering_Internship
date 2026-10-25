import re

def rewrite_query(query: str) -> str:
    """Normalize a search query without changing its intended meaning."""

    normalized = re.sub(r"\s+", " ", query).strip()

    if not normalized:
        return ""

    # Remove common conversational prefixes while preserving the question.
    prefixes = (
        "please tell me ",
        "could you explain ",
        "can you explain ",
        "please explain ",
        "i want to know ",
    )

    lowered = normalized.lower()
    for prefix in prefixes:
        if lowered.startswith(prefix):
            normalized = normalized[len(prefix):].strip()
            break

    return normalized
