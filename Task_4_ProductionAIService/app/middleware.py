
import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import get_settings
from app.metrics import REQUEST_COUNT, REQUEST_LATENCY, ERROR_COUNT


logger = logging.getLogger("ai_service")


class SecurityAndMetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path == "/metrics":
            return await call_next(request)

        settings = get_settings()
        method = request.method
        endpoint = request.url.path
        start = time.perf_counter()
        status = 500

        try:
            content_length = request.headers.get("content-length")

            if content_length:
                try:
                    size = int(content_length)
                except ValueError:
                    status = 400
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "Invalid Content-Length"},
                    )

                if size < 0:
                    status = 400
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "Invalid Content-Length"},
                    )

                if size > settings.max_request_size_bytes:
                    status = 413
                    return JSONResponse(
                        status_code=413,
                        content={"detail": "Request body too large"},
                    )

            response = await call_next(request)
            status = response.status_code
            return response

        except Exception:
            logger.exception(
                "Unhandled request error",
                extra={"method": method, "path": endpoint},
            )
            status = 500
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )

        finally:
            duration = time.perf_counter() - start

            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status=str(status),
            ).inc()

            REQUEST_LATENCY.labels(
                method=method,
                endpoint=endpoint,
            ).observe(duration)

            if status >= 400:
                ERROR_COUNT.labels(
                    method=method,
                    endpoint=endpoint,
                    status=str(status),
                ).inc()
