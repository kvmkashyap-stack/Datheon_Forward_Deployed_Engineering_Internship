from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY
from fastapi import Response


REQUEST_COUNT = Counter(
    "ai_service_requests_total",
    "Total HTTP requests handled",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "ai_service_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

ERROR_COUNT = Counter(
    "ai_service_errors_total",
    "Total HTTP requests returning 4xx or 5xx responses",
    ["method", "endpoint", "status"],
)

AI_INPUT_TOKENS = Counter(
    "ai_service_input_tokens_total",
    "Total AI input tokens reported by the provider",
)

AI_OUTPUT_TOKENS = Counter(
    "ai_service_output_tokens_total",
    "Total AI output tokens reported by the provider",
)


def metrics_response() -> Response:
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST,
    )
