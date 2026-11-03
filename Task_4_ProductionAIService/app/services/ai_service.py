
from dataclasses import dataclass

from app.config import get_settings
from app.metrics import AI_INPUT_TOKENS, AI_OUTPUT_TOKENS


@dataclass
class AIResult:
    answer: str
    input_tokens: int
    output_tokens: int
    model: str
    provider: str


class AIService:
    def generate(self, prompt: str) -> AIResult:
        settings = get_settings()

        if settings.ai_provider == "mock":
            answer = f"Mock AI response: {prompt}"
            input_tokens = 0
            output_tokens = 0

            # Mock mode does not estimate or invent token usage.
            return AIResult(
                answer=answer,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model="mock",
                provider="mock",
            )

        raise NotImplementedError(
            f"AI provider '{settings.ai_provider}' is not integrated yet"
        )


def record_token_usage(result: AIResult) -> None:
    if result.input_tokens > 0:
        AI_INPUT_TOKENS.inc(result.input_tokens)

    if result.output_tokens > 0:
        AI_OUTPUT_TOKENS.inc(result.output_tokens)
