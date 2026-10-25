import re

_RESPONSES = {
    "greeting": (
        "Hi! 👋 I'm your Enterprise RAG Assistant. "
        "I can chat with you, answer questions about your uploaded documents, "
        "and show source-page citations. What would you like to do?"
    ),
    "how_are_you": (
        "I'm doing well, thanks for asking! 😊 "
        "Would you like to chat or ask me something about your documents?"
    ),
    "thanks": "You're welcome! 😊 What else can I help you with?",
    "goodbye": "Goodbye! 👋 Come back whenever you need help.",
    "capabilities": (
        "I can answer questions using your uploaded PDFs, retrieve relevant "
        "clauses, and provide source-page citations. I can also respond to "
        "greetings and casual conversation."
    ),
}

_PATTERNS = [
    (
        "greeting",
        r"^(?:hi|hello|hey|hiya|howdy|"
        r"hi there|hello there|hey there|"
        r"good morning|good afternoon|good evening)[!. ]*$",
    ),
    (
        "how_are_you",
        r"^(?:how are you|how are you doing|"
        r"how's it going|hows it going|"
        r"how have you been)[?!. ]*$",
    ),
    (
        "thanks",
        r"^(?:thanks|thank you|thanks a lot|"
        r"thank you so much|thx)[!. ]*$",
    ),
    (
        "goodbye",
        r"^(?:bye|goodbye|see you|see you later|"
        r"talk to you later)[!. ]*$",
    ),
    (
        "capabilities",
        r"^(?:what can you do|what do you do|"
        r"how can you help me|what are your capabilities)[?!. ]*$",
    ),
]


def get_conversation_response(message: str) -> str | None:
    """Respond to recognized casual messages; return None for RAG queries."""

    normalized = re.sub(r"\s+", " ", message.strip().lower())

    if not normalized:
        return None

    for intent, pattern in _PATTERNS:
        if re.fullmatch(pattern, normalized):
            return _RESPONSES[intent]

    return None
