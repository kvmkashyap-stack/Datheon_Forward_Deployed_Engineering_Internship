
import argparse
import asyncio
import json
import statistics
import time
from pathlib import Path

import httpx


def percentile(values: list[float], percent: float) -> float:
    """Calculate a percentile using the nearest-rank method."""
    if not values:
        return 0.0

    ordered = sorted(values)
    rank = max(1, (len(ordered) * percent + 99.999999) // 100)
    index = min(len(ordered) - 1, int(rank) - 1)

    return ordered[index]


async def run_benchmark(
    base_url: str,
    total_requests: int,
    concurrency: int,
) -> dict:
    """Send concurrent requests and collect performance metrics."""
    latencies: list[float] = []
    failures = 0
    successful_requests = 0

    semaphore = asyncio.Semaphore(concurrency)
    timeout = httpx.Timeout(30.0)

    async with httpx.AsyncClient(timeout=timeout) as client:

        async def send_request() -> None:
            nonlocal failures, successful_requests

            async with semaphore:
                start = time.perf_counter()

                try:
                    response = await client.post(
                        f"{base_url.rstrip('/')}/api/v1/generate",
                        json={
                            "prompt": (
                                "Explain AI service reliability briefly."
                            )
                        },
                    )

                    elapsed_ms = (
                        time.perf_counter() - start
                    ) * 1000

                    latencies.append(elapsed_ms)

                    if response.is_success:
                        successful_requests += 1
                    else:
                        failures += 1

                except httpx.HTTPError:
                    failures += 1

        benchmark_start = time.perf_counter()

        await asyncio.gather(
            *(send_request() for _ in range(total_requests))
        )

        duration_seconds = time.perf_counter() - benchmark_start

    return {
        "target_url": base_url.rstrip("/"),
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failures,
        "failure_rate_percent": round(
            failures / total_requests * 100, 2
        ),
        "concurrency": concurrency,
        "duration_seconds": round(duration_seconds, 3),
        "throughput_requests_per_second": round(
            successful_requests / duration_seconds
            if duration_seconds > 0
            else 0.0,
            2,
        ),
        "latency_ms": {
            "p50": round(percentile(latencies, 50), 2),
            "p95": round(percentile(latencies, 95), 2),
            "p99": round(percentile(latencies, 99), 2),
            "mean": round(
                statistics.mean(latencies), 2
            ) if latencies else 0.0,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark the FastAPI AI service."
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8001",
        help="Base URL of the running AI service.",
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=100,
        help="Total number of requests to send.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Maximum number of concurrent requests.",
    )
    args = parser.parse_args()

    if args.requests < 1:
        parser.error("--requests must be at least 1.")

    if args.concurrency < 1:
        parser.error("--concurrency must be at least 1.")

    result = asyncio.run(
        run_benchmark(
            base_url=args.url,
            total_requests=args.requests,
            concurrency=args.concurrency,
        )
    )

    report_dir = Path("benchmarks/results")
    report_dir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"benchmark_{timestamp}.json"

    report_path.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(result, indent=2))
    print(f"\nResults saved to: {report_path}")


if __name__ == "__main__":
    main()
