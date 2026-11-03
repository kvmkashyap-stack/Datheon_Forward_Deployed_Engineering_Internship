TASK 4 — PRODUCTION AI SERVICE Datheon Forward Deployed Engineering
Internship

============================================================ 1. PROJECT
OVERVIEW ============================================================

Task_4_ProductionAIService is a container-oriented FastAPI microservice
scaffold for exposing an AI text-generation endpoint with operational
monitoring, health checks, request validation, and deployment
configuration.

The implementation focuses on production-service concerns: - A versioned
FastAPI generation endpoint. - Liveness and readiness health
endpoints. - Prometheus metrics for request counts, latency, errors, and
token counts. - Environment-based configuration and secret handling. - A
non-root Docker image definition. - Docker Compose configuration with
restrictive runtime settings. - A small asynchronous benchmark utility
that reports latency percentiles, throughput, and failures. - Automated
tests for health, metrics, and generation behavior.

IMPORTANT IMPLEMENTATION STATUS The current AI provider is a mock
provider. The endpoint returns a simulated response; it does not call a
real language model, and its token counts are zero. The benchmark
numbers included below were measured against the local mock service, not
a real model or a verified Docker deployment.

Docker and Compose configuration files are present, and the Compose
configuration was validated. The Docker engine was not available in the
development environment, so the image was not built and the container
was not launched or tested. Do not interpret the presence of Docker
files as proof that the container has been successfully built or
deployed.

============================================================ 2. FEATURES
============================================================

API - FastAPI application. - POST /api/v1/generate for simulated text
generation. - JSON request and response schemas. - Request validation
through Pydantic. - Generic error handling intended to avoid exposing
internal exception details.

HEALTH CHECKS - GET /health/live — liveness check. - GET /health/ready —
readiness check. - GET /health — general health endpoint. - GET / — root
endpoint.

OBSERVABILITY - GET /metrics — Prometheus-compatible metrics endpoint. -
Request counters. - Request-latency histogram. - Error counters. - Input
and output token counters. - Request middleware for timing and
request/error instrumentation.

CONFIGURATION AND SECURITY - Configuration is managed through Pydantic
Settings and environment variables. - API key configuration uses
SecretStr so secret values are not treated as ordinary display
strings. - A .env.example file provides a template for environment
configuration. - .env files should remain local and must not be
committed. - Request middleware checks the declared Content-Length
against the configured request-size limit. - Dockerfile defines a
non-root runtime user. - Docker Compose includes restrictive options
such as a read-only root filesystem, temporary writable storage, dropped
Linux capabilities, no-new-privileges, and a localhost-only port
binding.

Limitations: the Content-Length check does not independently guarantee
that every streamed or chunked request body is bounded. Production
deployments should enforce request-size limits at the application and
ingress/proxy layers. Security settings also need to be reviewed against
the target deployment environment.

BENCHMARKING - Asynchronous HTTP requests. - Configurable request count
and concurrency. - Successful and failed request counts. - Failure
rate. - Total duration and throughput. - p50, p95, p99, and mean
latency. - Timestamped JSON output under benchmarks/results/.

TESTING - Automated tests cover health endpoints, metrics, and
generation behavior. - The latest recorded test run passed 10 tests.

============================================================ 3. PROJECT
STRUCTURE ============================================================

Task_4_ProductionAIService/ | |– app/ | |– init.py | |– main.py FastAPI
application and routes | |– config.py Environment-backed application
settings | |– middleware.py Request timing, size check, and error
instrumentation | |– metrics.py Prometheus metric definitions | |–
schemas.py Request and response models | | |
-- services/ |       |-- __init__.py |– ai_service.py Mock AI provider
implementation | |– tests/ | |– test_health.py Health endpoint tests |
|– test_metrics.py Metrics endpoint tests |
-- test_ai.py              Generation endpoint tests | |-- benchmarks/ |   |-- benchmark.py            HTTP benchmark runner |–
results/ JSON benchmark reports | |– deployment/ |
-- prometheus.yml          Prometheus scrape configuration | |-- Dockerfile                  Container image definition |-- docker-compose.yml          Local service orchestration and runtime restrictions |-- .dockerignore               Files excluded from Docker build context |-- .env.example                Example environment configuration |-- .gitignore                  Git ignore rules |-- requirements.txt            Python dependencies–
README.md Project documentation

============================================================ 4.
REQUIREMENTS
============================================================

-   Python 3.12 recommended.
-   pip.
-   Git, if cloning the repository.
-   Docker Engine with Docker Compose, if building and running the
    container.
-   A compatible Windows PowerShell, macOS shell, or Linux shell.

The service can be run directly with Python without Docker. Docker-based
execution requires a functioning Docker Engine.

============================================================ 5. LOCAL
SETUP — WINDOWS POWERSHELL
============================================================

Open PowerShell in the Task_4_ProductionAIService directory.

Create a virtual environment:

    py -3.12 -m venv .venv

Activate it:

    .\.venv\Scripts\Activate.ps1

If PowerShell blocks script activation, use an approved local
execution-policy approach or invoke the environment’s Python executable
directly.

Install dependencies:

    python -m pip install --upgrade pip
    pip install -r requirements.txt

Create a local environment file from the example:

    Copy-Item .env.example .env

Open .env and review the settings. Keep real credentials out of source
control. The current mock provider does not require a real model API key
to produce its simulated response. Consult app/config.py and
.env.example for the exact supported variable names and defaults; do not
assume that an environment variable is supported unless it is declared
there.

Start the API:

    uvicorn app.main:app --host 127.0.0.1 --port 8001

Port 8001 is used in the example because port 8000 may already be
occupied. If you choose another port, use that same port in the API and
benchmark URLs.

Open the interactive API documentation:

    http://127.0.0.1:8001/docs

Alternative OpenAPI documentation:

    http://127.0.0.1:8001/redoc

============================================================ 6. API
ENDPOINTS ============================================================

GET /

Purpose: Returns the root endpoint response.

GET /health

Purpose: Returns the general health response.

GET /health/live

Purpose: Liveness endpoint for determining whether the application
process is responding.

GET /health/ready

Purpose: Readiness endpoint intended for readiness checks. Review the
current implementation before treating it as a dependency-aware
readiness check; a mock provider does not establish the health of a real
external model service.

GET /metrics

Purpose: Exposes Prometheus-formatted metrics. The exact metric names
are defined in app/metrics.py.

POST /api/v1/generate

Purpose: Accepts a validated JSON request and returns a simulated
generation response from the mock provider.

Example request: The exact request fields are defined in app/schemas.py.
Use the Swagger UI at /docs or inspect that schema before relying on a
specific payload shape.

Example using curl: Replace the JSON body with the fields required by
the current Generate request schema.

    curl -X POST "http://127.0.0.1:8001/api/v1/generate" ^
      -H "Content-Type: application/json" ^
      -d "{\"prompt\":\"Explain vector databases briefly.\"}"

PowerShell note: The caret (^) is a cmd.exe line-continuation character,
not a PowerShell continuation character. In PowerShell, use a
single-line curl.exe command or Invoke-RestMethod. Example:

    $body = @{ prompt = "Explain vector databases briefly." } | ConvertTo-Json
    Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/v1/generate" -Method Post -ContentType "application/json" -Body $body

The example payload above is illustrative. If the current schema
requires additional fields or uses a different field name, follow
app/schemas.py and /docs.

============================================================ 7.
PROMETHEUS METRICS
============================================================

The service exposes metrics at /metrics in Prometheus exposition format.

The implementation tracks these categories: - Request count. - Request
latency. - Error count. - Input token count. - Output token count.

Metric names, labels, histogram buckets, and units should be taken from
app/metrics.py. Use those exact names when writing PromQL queries; do
not guess metric identifiers.

The token counters currently receive zero values from the mock provider.
They are instrumentation placeholders for a future real provider
integration and should not be interpreted as actual model usage.

The deployment/prometheus.yml file is intended to configure Prometheus
scraping. Confirm its target address and port against the runtime
environment before starting Prometheus. A target configured for a
container network may not work unchanged when Prometheus runs directly
on the host, and vice versa.

============================================================ 8.
ENVIRONMENT VARIABLES AND SECRETS
============================================================

Application settings are loaded through Pydantic Settings. The exact
setting names and defaults are defined in: - app/config.py -
.env.example

Use .env.example as the authoritative template. Copy it to .env for
local development and replace example values only when needed.

Security practices: - Never commit .env. - Never paste production API
keys into README files, source code, benchmark reports, logs, or GitHub
issues. - Use your deployment platform’s secret manager for real
deployments. - Rotate any credential that has accidentally been
committed or exposed. - Keep .env.example limited to placeholders and
non-sensitive defaults. - Review logs to ensure request bodies, prompts,
and secrets are not unintentionally recorded.

The current provider is mock-only. Adding a real model provider requires
implementing provider calls, handling timeouts and upstream errors,
accurately recording token usage, and configuring credentials through a
secure secret mechanism.

============================================================ 9. DOCKER
AND DOCKER COMPOSE
============================================================

The repository includes: - Dockerfile - docker-compose.yml -
.dockerignore - deployment/prometheus.yml

The Dockerfile is configured to run the service as a non-root user and
includes a health check. Compose includes several container-hardening
settings, including a read-only root filesystem, temporary writable
storage, dropped capabilities, no-new-privileges, and a localhost-bound
service port.

When Docker Engine is available, validate and start the service from the
Task_4_ProductionAIService directory:

    docker compose config
    docker compose build
    docker compose up -d

Inspect status and logs:

    docker compose ps
    docker compose logs --tail=100

Check the health endpoint:

    curl http://127.0.0.1:8000/health

Stop the service:

    docker compose down

The port in the health-check command must match the published port in
docker-compose.yml. Do not assume the Compose service uses port 8001;
the local Python development run and the container mapping may differ.

Verification status: - Compose configuration validation succeeded during
development. - Docker image build and container startup were not
verified because Docker Engine was unavailable in the development
environment. - The commands above are the next validation steps on a
machine with Docker Engine running.

Before deploying to a client VPC: 1. Confirm the intended network
binding and firewall rules. 2. Configure secrets through the approved
secret manager. 3. Configure health-check behavior and restart policy.
4. Set CPU, memory, and request limits appropriate to the workload. 5.
Configure TLS at the approved ingress or reverse proxy. 6. Restrict
access to /metrics if operational policy requires it. 7. Confirm
Prometheus connectivity and scrape targets. 8. Test graceful shutdown,
timeouts, and upstream failure behavior. 9. Verify that the container’s
read-only filesystem and temporary storage meet application
requirements. 10. Review the base image and dependencies for
vulnerabilities and pin versions according to deployment policy.

============================================================ 10. LATENCY
AND THROUGHPUT BENCHMARK
============================================================

The benchmark utility is located at:

    benchmarks/benchmark.py

It sends concurrent HTTP requests to the running service and records
request success/failure, latency percentiles, mean latency, total
duration, and throughput. The JSON reports are saved under:

    benchmarks/results/

A recorded local benchmark run used: - Target: http://127.0.0.1:8001 -
Total requests: 100 - Concurrency: 10 - Successful requests: 100 -
Failed requests: 0 - Failure rate: 0.0% - Duration: 0.647 seconds -
Throughput: 154.47 requests/second - p50 latency: 42.41 ms - p95
latency: 111.74 ms - p99 latency: 254.66 ms - Mean latency: 54.86 ms

Interpretation: These figures describe one local run against the mock
generation endpoint. They are not a production capacity claim and are
not representative of a real LLM, network latency, a client VPC, or a
Docker deployment. Results can vary with hardware, concurrent processes,
warm-up, operating system, and network conditions. The p99 result is
especially sensitive to occasional delays in a small sample.

Run the benchmark with the options supported by the script:

    python benchmarks/benchmark.py --help

If the script does not implement –help, inspect its argument parser and
use its documented defaults/options. Confirm that the target URL and
request payload match the running service before interpreting the
results.

For meaningful production benchmarking: - Run against the actual
containerized deployment. - Use representative prompts and response
sizes. - Include warm-up requests. - Test multiple concurrency levels
and larger sample sizes. - Measure failures, timeouts, and latency
distributions. - Record CPU and memory use alongside throughput. -
Repeat runs and report the environment and test conditions. - Benchmark
the real model provider separately from the mock provider. - Avoid
publishing secrets or sensitive prompts in benchmark output.

============================================================ 11. TESTING
============================================================

The test suite is in the tests/ directory.

Run all tests:

    python -m pytest -q

Run with coverage, if pytest-cov is installed:

    python -m pytest --cov=app --cov-report=term-missing

Recorded result during development: 10 tests passed.

The tests cover health endpoints, metrics exposure, and AI generation
behavior. Passing tests validate the tested application behavior; they
do not prove that the Docker image builds, that a production model
provider works, or that the service is secure under every deployment
configuration.

============================================================ 12.
TROUBLESHOOTING
============================================================

Port already in use: Start the local service on another port, for
example 8001, and make sure the URL passed to the benchmark uses the
same port.

Docker cannot connect to the engine: Start and verify the Docker Engine
or Docker Desktop backend appropriate to the operating system. Docker
CLI being installed does not mean the engine is running. Re-run docker
info before attempting a build.

Environment variable is not recognized: Check app/config.py and
.env.example for the exact variable name. Restart the service after
changing environment settings.

Metrics are missing or show zero tokens: Check /metrics and
app/metrics.py. Zero token usage is expected from the current mock
provider.

Readiness succeeds while an external service is unavailable: The current
mock provider has no real external model dependency. Revisit readiness
behavior when a real provider is added.

Prometheus target is down: Check deployment/prometheus.yml, the target
hostname/port, network reachability, and whether Prometheus is running
on the host or in a container.

Request returns validation error: Inspect /docs and app/schemas.py to
confirm the required request fields and data types.

============================================================ 13. CURRENT
LIMITATIONS AND NEXT STEPS
============================================================

Current limitations: - Mock AI provider only; no real LLM provider is
integrated. - Mock token counts are zero. - Docker image build and
container startup have not been verified in the development
environment. - Benchmark results are from a local mock-service run, not
a production deployment. - Request-size protection checks Content-Length
and is not a complete streamed-body limit. - Prometheus metric names and
configuration should be checked against the exact files before
production use. - Client VPC networking, TLS, secret management, access
control, and deployment-specific resource limits require
environment-specific configuration and validation.

Recommended next steps: 1. Build and run the image with a working Docker
Engine. 2. Run the automated tests against the containerized service. 3.
Add a real provider behind the existing AI service interface. 4. Add
upstream timeout, retry, and rate-limit policies where appropriate. 5.
Record actual provider token usage and test error cases. 6. Add
integration tests for provider failures and readiness behavior. 7.
Verify Prometheus scraping from the intended deployment network. 8.
Benchmark the container with representative traffic. 9. Complete the
client integration guide with the actual request schema, response
schema, authentication model, networking assumptions, and
deployment-specific addresses. 10. Review the service against the
client’s security and operational requirements before claiming
production readiness.
