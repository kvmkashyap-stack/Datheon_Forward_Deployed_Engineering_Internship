# Task 4 — Production AI Service
## Containerized FastAPI Microservice, Observability, Security, and Latency Benchmarking

**Internship:** Datheon — Forward Deployed Engineering Internship  
**Task:** Task 4 — Client VPC Deployment, Dockerized Microservice and Latency Benchmark  
**Project Directory:** `Task_4_ProductionAIService`  
**Status:** Core implementation and automated tests completed; Docker runtime verification pending.

---

## 1. Project Overview

Production AI Service is a containerization-ready AI microservice designed to demonstrate how an AI-powered API can be structured for deployment in a client-controlled environment.

The service uses FastAPI to expose generation and health-check endpoints, Prometheus to collect operational metrics, environment-based configuration to manage secrets, and Docker Compose to define a hardened container deployment.

The project focuses on reliability, observability, API validation, security-oriented container configuration, and performance measurement.

The current implementation uses a mock AI provider so that the API, metrics, and benchmark workflow can be exercised without requiring a paid AI model or an external API key.

### Key Features

- **REST API:** FastAPI endpoints for AI generation and service health.
- **Input validation:** Pydantic schemas for validating incoming requests and structuring responses.
- **Service separation:** Independent configuration, middleware, metrics, schemas, and AI-service modules.
- **Prometheus observability:** Request counts, latency distributions, error counts, and token counters.
- **Security-oriented middleware:** Request-size checks, error handling, and request instrumentation.
- **Container hardening:** Non-root container user, health checks, restricted capabilities, read-only root filesystem, and temporary writable storage configured in Docker files.
- **Environment-based configuration:** Settings loaded from environment variables and `.env` during local development.
- **Automated testing:** Pytest tests covering health, metrics, and AI endpoints.
- **Latency benchmarking:** A configurable benchmark script that measures percentile latency, throughput, and failure rate.
- **Deployment configuration:** Dockerfile, Docker Compose, and Prometheus configuration.

---

## 2. Problem Statement

AI services deployed in client environments must be more than functional API endpoints. They need predictable interfaces, operational visibility, controlled configuration, repeatable deployment instructions, and measurable performance.

A service that works locally may still fail in production because of missing health checks, insecure container privileges, unhandled errors, absent metrics, or poor latency under concurrent requests.

This project addresses these engineering concerns by implementing a modular FastAPI service and providing supporting deployment, monitoring, testing, and benchmarking components.

The implementation establishes the foundation for integrating a real AI inference provider and deploying the service inside a client-controlled network or VPC.

---

## 3. Objectives

The primary objectives are:

1. Build a modular FastAPI microservice for AI generation.
2. Implement health and readiness endpoints for operational checks.
3. Instrument API requests using Prometheus metrics.
4. Measure request latency, throughput, and failure rate.
5. Track input and output token counts through dedicated metrics.
6. Load configuration and sensitive credentials through environment variables.
7. Define a hardened Docker image and Docker Compose deployment.
8. Add automated tests for core API behavior.
9. Produce machine-readable benchmark results.
10. Document the architecture, API contract, configuration, deployment process, and operational limitations.

---

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Application runtime |
| FastAPI | REST API framework |
| Uvicorn | ASGI application server |
| Pydantic | Request and response validation |
| Pydantic Settings | Environment-based configuration |
| Prometheus Client | Metrics instrumentation and exposition |
| Docker | Container image definition |
| Docker Compose | Service deployment configuration |
| Prometheus | Metrics scraping configuration |
| Pytest | Automated testing |
| HTTPX | HTTP client and API testing |
| Python asyncio | Concurrent benchmark requests |
| JSON | Benchmark result storage |

---

## 5. System Architecture

### High-Level Architecture

```text
                   Client Application
                          |
                          | HTTP Request
                          v
                 FastAPI Application
                          |
                          v
                Security and Metrics
                     Middleware
                          |
                          v
                    API Routing
                          |
                          v
                  Request Validation
                       Pydantic
                          |
                          v
                    AI Service Layer
                          |
                          v
                    Mock AI Provider
                          |
                          v
                  Structured API Response
```

### Observability Architecture

```text
             Incoming API Requests
                       |
                       v
              FastAPI Middleware
                       |
          +------------+------------+
          |            |            |
          v            v            v
      Request      Latency       Error
       Counts     Histogram      Counts
          |            |            |
          +------------+------------+
                       |
                       v
               Prometheus Metrics
                 /metrics endpoint
                       |
                       v
                Prometheus Scraper
          (configured for deployment)
```

### Deployment Architecture

```text
             Client / Internal Network
                       |
                       v
              Host Port 8000
                       |
                       v
              Docker Compose
                       |
                       v
             Production AI Service
              FastAPI + Uvicorn
                       |
            +----------+----------+
            |                     |
            v                     v
       Health Checks         /metrics
                                  |
                                  v
                              Prometheus
                         (if deployed and configured)
```

The architecture separates API transport, request validation, business logic, configuration, and observability. This allows the AI provider to be replaced without redesigning the entire API.

**Deployment status:** The Docker and Compose configuration files are implemented, and Compose configuration validation succeeded. Actual image building, container startup, and VPC deployment remain unverified because the local Docker Engine was unavailable.

---

## 6. Repository Structure

```text
Task_4_ProductionAIService/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── middleware.py
│   ├── metrics.py
│   ├── schemas.py
│   │
│   └── services/
│       ├── __init__.py
│       └── ai_service.py
│
├── tests/
│   ├── test_health.py
│   ├── test_metrics.py
│   └── test_ai.py
│
├── benchmarks/
│   ├── benchmark.py
│   └── results/
│       └── benchmark_20261103_153949.json
│
├── deployment/
│   └── prometheus.yml
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

### Module Responsibilities

**`app/main.py`**

Creates the FastAPI application, registers middleware and API routes, and exposes the health, readiness, generation, and metrics endpoints.

**`app/config.py`**

Defines application settings and loads configuration from environment variables. Sensitive configuration is represented using Pydantic's `SecretStr` where applicable.

**`app/middleware.py`**

Implements request-size checks, request instrumentation, error tracking, and generic handling of unhandled application exceptions.

**`app/metrics.py`**

Defines Prometheus metrics used to monitor request volume, latency, failures, and token counts.

**`app/schemas.py`**

Defines Pydantic request and response schemas for the generation API.

**`app/services/ai_service.py`**

Contains the AI service abstraction and current mock provider implementation.

**`tests/`**

Contains automated tests for health endpoints, metrics exposure, and generation behavior.

**`benchmarks/benchmark.py`**

Executes concurrent HTTP requests and calculates performance statistics, including percentile latency, throughput, and failure rate.

**`benchmarks/results/`**

Stores timestamped JSON benchmark reports for reproducibility and comparison.

**`deployment/prometheus.yml`**

Provides the Prometheus scraping configuration.

**`Dockerfile`**

Defines the application image, runtime setup, non-root user, and container health check.

**`docker-compose.yml`**

Defines the service configuration, port binding, health-check behavior, and security-related container options.

---

## 7. API Documentation

The service exposes the following endpoints.

### 7.1 Root Endpoint

**Method:** `GET`  
**Path:** `/`

Purpose:
- Confirm that the API application responds.
- Provide a basic service entry point.

Example:

```bash
curl http://127.0.0.1:8001/
```

The example uses port `8001` because that was the port used during local verification.

### 7.2 Liveness Endpoint

**Method:** `GET`  
**Path:** `/health/live`

Purpose:
- Check whether the application process is alive.
- Support basic liveness monitoring.

Example:

```bash
curl http://127.0.0.1:8001/health/live
```

### 7.3 Readiness Endpoint

**Method:** `GET`  
**Path:** `/health/ready`

Purpose:
- Provide a readiness check for the service.
- Support deployment health checks.

Example:

```bash
curl http://127.0.0.1:8001/health/ready
```

The current mock-provider architecture does not establish connectivity to a real external AI provider.

### 7.4 Combined Health Endpoint

**Method:** `GET`  
**Path:** `/health`

Purpose:
- Provide a general health status for monitoring and operational inspection.

Example:

```bash
curl http://127.0.0.1:8001/health
```

### 7.5 AI Generation Endpoint

**Method:** `POST`  
**Path:** `/api/v1/generate`  
**Content-Type:** `application/json`

Purpose:
- Accept a generation request.
- Validate the input.
- Invoke the AI service layer.
- Return a structured response.

Example request:

```json
{
  "prompt": "Explain retrieval-augmented generation in simple terms."
}
```

Example command:

```bash
curl -X POST http://127.0.0.1:8001/api/v1/generate \
  -H "Content-Type: application/json" \
  -d "{\"prompt\":\"Explain retrieval-augmented generation in simple terms.\"}"
```

The exact response fields and validation constraints are defined in `app/schemas.py`.

**Important:** The current provider is a mock implementation. The generated content is not produced by a real language model.

### 7.6 Prometheus Metrics Endpoint

**Method:** `GET`  
**Path:** `/metrics`

Purpose:
- Expose instrumentation in Prometheus-compatible format.
- Allow a configured Prometheus server to scrape application metrics.

Example:

```bash
curl http://127.0.0.1:8001/metrics
```

The endpoint exposes metrics defined in `app/metrics.py`.

---

## 8. Observability and Metrics

Operational visibility is essential when deploying an AI service inside a client environment.

The application defines metrics for the following categories.

### Request Count

Tracks the volume of incoming requests.

Use cases:
- Monitor API traffic.
- Compare request volume between deployments.
- Identify sudden traffic changes.

### Request Latency

A Prometheus histogram records request latency.

Use cases:
- Observe response-time distributions.
- Identify slow requests.
- Support percentile-based performance analysis.

### Error Count

Tracks request failures according to the application's instrumentation.

Use cases:
- Detect application instability.
- Identify changes in failure behavior.
- Support incident investigation.

### Input and Output Token Counts

Dedicated counters are provided for input and output token usage.

Use cases:
- Prepare for usage monitoring after integrating a real language model.
- Track token consumption when actual provider-reported token counts are available.
- Support future cost and capacity analysis.

**Current limitation:** The mock provider returns zero token counts. These counters therefore do not represent actual language-model consumption.

### Prometheus Integration

The `deployment/prometheus.yml` file defines the intended scraping configuration.

A typical Prometheus deployment needs to:
1. Start the Prometheus server.
2. Load the scraping configuration.
3. Reach the service's `/metrics` endpoint over the configured network.
4. Verify that the target is healthy in Prometheus.

Prometheus scraping has not been verified end-to-end in the current environment.

---

## 9. Security and Reliability

The project incorporates several security-oriented design choices.

### Environment-Based Configuration

Configuration is loaded through environment variables and local environment files.

The `.env.example` file provides a template for required settings without containing actual credentials.

Actual `.env` files should not be committed to version control.

### Request Validation

Pydantic schemas validate incoming generation requests and structure API responses.

Validation helps reject malformed requests before they reach the service layer.

### Request-Size Checks

The middleware checks the declared `Content-Length` header against the configured request-size limit.

**Limitation:** This implementation does not independently guarantee size enforcement for streamed or chunked requests without a declared content length. Production deployment should enforce body limits at the application and reverse-proxy layers.

### Error Handling

The middleware tracks errors and provides generic handling for unhandled application exceptions.

Internal exception details should not be exposed to clients.

### Non-Root Container

The Dockerfile configures the service to run as a non-root user, reducing the privileges available to the application inside the container.

### Read-Only Root Filesystem

The Compose configuration specifies a read-only container root filesystem, with temporary writable storage configured where needed.

### Restricted Capabilities

The Compose configuration drops Linux capabilities and enables `no-new-privileges`.

These settings reduce the privileges available to the container process.

### Local Port Binding

The Compose configuration binds the service to `127.0.0.1:8000` on the host rather than exposing it to all host interfaces by default.

This is appropriate for local testing. A client VPC deployment would require an explicitly designed network exposure strategy.

### Health Checks

Health checks are defined to support service monitoring and container lifecycle management.

### Security Work Still Required for Production

Before exposing the service to client traffic, the following should be addressed or verified:

- Authentication and authorization.
- TLS termination and certificate management.
- Network policies and ingress restrictions.
- Complete request-body size enforcement.
- Rate limiting and abuse protection.
- Secret injection through the client's approved secret-management system.
- Dependency and container-image vulnerability scanning.
- Centralized logging and retention policies.
- Production AI-provider timeout and retry behavior.
- End-to-end verification of health checks under failure conditions.

The current implementation should be treated as a security-oriented deployment foundation, not as a completed security certification.

---

## 10. Environment Configuration

The project includes `.env.example` as the template for local configuration.

General workflow:

1. Review `.env.example`.
2. Create a local `.env` file if the application configuration requires it.
3. Populate the required values locally.
4. Never commit real credentials.
5. Use the client's approved secret-management mechanism in production.

The current AI provider defaults to mock mode, allowing development and benchmarking without a real model API key.

No real external AI-provider integration is currently implemented.

---

## 11. Docker and Docker Compose

### Dockerfile

The Dockerfile defines the Python runtime, application dependencies, service startup, non-root execution, and health-check configuration.

The intended container deployment provides a repeatable environment independent of the developer's local Python virtual environment.

### Docker Compose

The Compose file defines the service and its operational settings, including:

- Application port mapping.
- Environment configuration.
- Health-check behavior.
- Read-only root filesystem.
- Temporary writable storage.
- Dropped Linux capabilities.
- No-new-privileges security option.

### Configuration Validation

Docker Compose configuration validation succeeded.

However, the Docker Engine was unavailable in the development environment, so the following have **not** been verified:

- Building the Docker image.
- Starting the container.
- Running the application inside the container.
- Verifying the container health check at runtime.
- Testing the complete Compose deployment.
- Deploying to an actual client VPC.

### Local Docker Verification

After Docker Engine is available, run these commands from the `Task_4_ProductionAIService` directory.

Validate the Compose configuration:

```bash
docker compose config
```

Build the image:

```bash
docker compose build
```

Start the service:

```bash
docker compose up -d
```

Inspect the running containers:

```bash
docker compose ps
```

Inspect application logs:

```bash
docker compose logs -f
```

Stop the service:

```bash
docker compose down
```

Run these commands only after Docker Engine is running and the Compose configuration has been reviewed for the target environment.

---

## 12. Automated Testing

The project contains three test modules.

| Test File | Responsibility |
|---|---|
| `tests/test_health.py` | Health and readiness endpoint behavior |
| `tests/test_metrics.py` | Metrics endpoint and instrumentation behavior |
| `tests/test_ai.py` | AI generation endpoint behavior |

The test suite was executed successfully with **10 tests passing** in the local development environment.

Run the test suite with:

```bash
pytest -v
```

For coverage reporting:

```bash
pytest --cov=app --cov-report=term-missing
```

Automated tests help validate API behavior and reduce the risk of regressions when the service implementation changes.

The successful test result applies to the local Python application; it does not establish that the application has passed tests inside Docker or in a production VPC.

---

## 13. Performance Benchmarking

The benchmark script in `benchmarks/benchmark.py` sends concurrent requests to the running service and calculates performance statistics.

### Metrics Collected

**Total requests:** Number of requests attempted.

**Successful requests:** Requests classified as successful by the benchmark.

**Failed requests:** Requests that did not complete successfully according to the benchmark's criteria.

**Failure rate:** Percentage of failed requests.

**Latency percentiles:**
- **p50:** Median observed request latency.
- **p95:** Latency at the 95th percentile.
- **p99:** Latency at the 99th percentile.

**Mean latency:** Average observed request latency.

**Throughput:** Successful requests per second, as calculated by the benchmark.

### Recorded Benchmark

The following results were recorded during local testing against the mock-provider API on port `8001`.

| Metric | Result |
|---|---:|
| Total requests | 100 |
| Successful requests | 100 |
| Failed requests | 0 |
| Failure rate | 0.00% |
| Concurrency | 10 |
| Duration | 0.647 seconds |
| Throughput | 154.47 requests/second |
| p50 latency | 42.41 ms |
| p95 latency | 111.74 ms |
| p99 latency | 254.66 ms |
| Mean latency | 54.86 ms |

**Benchmark report:** `benchmarks/results/benchmark_20261103_153949.json`

### Interpreting the Results

The recorded run completed 100 benchmark requests without failures and achieved approximately 154.47 requests per second in that test environment.

The p50 latency was 42.41 ms, while p95 latency was 111.74 ms and p99 latency was 254.66 ms.

The difference between median and tail latency indicates that some requests took longer than a typical request.

These results describe one local benchmark run against the mock implementation. They are not a production performance guarantee and should not be compared directly with real-model latency.

Actual AI inference performance will depend on the model, provider, network, prompt length, generated output length, concurrency, and infrastructure.

### Running the Benchmark

Start the service first, then execute:

```bash
python benchmarks/benchmark.py
```

Use the script's supported command-line options or configuration to adjust the target URL, request count, and concurrency where available.

The benchmark generates a timestamped JSON report in `benchmarks/results/`.

For reproducible comparisons, record the target environment, provider, request workload, concurrency, and date for each run.

---

## 14. Client Integration Guide

This section describes how a client application can integrate with the API.

### Step 1: Establish Network Access

Ensure the client application can reach the service host and configured port.

For local development, the service was tested on:

```text
http://127.0.0.1:8001
```

The Compose configuration uses host port `8000` by default.

In a VPC, use the approved internal hostname or service address rather than assuming that localhost refers to the remote service.

### Step 2: Check Service Health

Call:

```http
GET /health
```

Use the result to determine whether the service is responding.

For orchestrator-specific liveness and readiness behavior, use the corresponding dedicated endpoints.

### Step 3: Send a Generation Request

Call:

```http
POST /api/v1/generate
Content-Type: application/json
```

Provide a JSON body that conforms to the request schema defined in `app/schemas.py`.

Example request:

```json
{
  "prompt": "Summarize the following text in three sentences."
}
```

### Step 4: Handle Errors

Client applications should handle HTTP errors, network timeouts, invalid responses, and service unavailability.

Production clients should use bounded timeouts and retry only where appropriate. Retry policies should avoid duplicating non-idempotent operations.

### Step 5: Monitor the Service

Use the `/metrics` endpoint to expose application instrumentation to an approved Prometheus deployment.

Monitor request volume, latency, failures, and token counts once actual model usage is integrated.

### Step 6: Configure Production Networking

Before production use, configure the required ingress, TLS, authentication, authorization, and network policies according to the client's security requirements.

**Integration limitation:** The documented generation workflow currently uses a mock provider. A real AI provider must be integrated before this service can be used for actual model inference.

---

## 15. Failure Handling and Operational Considerations

Production-oriented API services should be designed around expected failure modes.

### Invalid Input

Request schemas validate incoming data and allow malformed inputs to be rejected before application processing.

### Application Exceptions

The middleware tracks errors and handles unhandled application exceptions with a generic response.

### Provider Failure

A real provider has not yet been integrated. Provider-specific failures, timeouts, throttling, retries, and fallback behavior therefore remain future implementation work.

### Container Failure

The Docker and Compose files define health-check and runtime security configuration. Runtime recovery behavior must be verified after the container has been started successfully.

### Monitoring Failure

The application exposes metrics, but a working Prometheus server must be deployed and configured to scrape the endpoint before end-to-end monitoring can be confirmed.

### Performance Degradation

Latency percentiles and throughput measurements provide a baseline for detecting performance changes. Real-provider benchmarks should be conducted before setting production service-level objectives.

---

## 16. Engineering Decisions

### Why FastAPI?

FastAPI provides a clear HTTP interface, request validation, typed schemas, and an ASGI-based runtime suitable for Python microservices.

### Why a Separate Service Layer?

Keeping generation logic outside the routing module makes the API easier to maintain and allows the mock provider to be replaced with a real inference provider.

### Why Prometheus?

Prometheus-compatible metrics support request monitoring, latency analysis, error tracking, and integration with standard observability systems.

### Why Docker?

Containerization provides a repeatable application environment and simplifies deployment into controlled infrastructure.

### Why Docker Compose?

Compose provides a readable, version-controlled definition of service configuration and container runtime security settings.

### Why a Mock AI Provider?

The mock provider enables local API development, automated testing, and performance measurement without depending on external credentials or paid inference services.

It also isolates API overhead from model inference latency. The resulting benchmark must not be interpreted as real-model performance.

### Why Percentile Latency?

Mean latency alone can hide slow requests. p50, p95, and p99 provide a more informative view of typical and tail response times.

---

## 17. Current Limitations and Future Improvements

The following work would strengthen the service before production deployment.

1. **Real AI provider integration:** Add a configurable model provider and secure credential handling.
2. **Provider token accounting:** Record actual provider-reported input and output token usage.
3. **Provider timeout handling:** Introduce bounded timeouts and appropriate retry policies.
4. **Authentication and authorization:** Protect generation and operational endpoints according to client requirements.
5. **Complete body-size enforcement:** Enforce request limits for both declared and streamed request bodies.
6. **Production logging:** Add structured logs, request correlation IDs, and a documented retention strategy.
7. **Container runtime verification:** Build the image, start the container, and test health checks.
8. **Prometheus verification:** Run Prometheus and confirm successful metric scraping.
9. **Realistic benchmarks:** Benchmark with a real provider and representative prompt and response sizes.
10. **Load and stress testing:** Increase concurrency and request volume while measuring errors and resource utilization.
11. **Deployment automation:** Add a repeatable deployment workflow for the intended client environment.
12. **VPC validation:** Verify network access, secrets, DNS, TLS, and observability in the target client infrastructure.
13. **Dependency security:** Scan dependencies and container images for known vulnerabilities.
14. **Operational documentation:** Establish deployment, rollback, troubleshooting, and incident-response procedures.

---

## 18. Reproducibility

The project includes the code, test modules, dependency manifest, deployment configuration, benchmark script, and recorded benchmark output required to inspect the current implementation.

To reproduce local testing:

1. Create and activate a Python 3.12 virtual environment.
2. Install dependencies from `requirements.txt`.
3. Configure environment variables as needed.
4. Start the FastAPI application using the project's configured startup command.
5. Run `pytest -v`.
6. Execute the benchmark script against the running service.
7. Inspect the resulting JSON report.

Docker-based reproduction requires a working Docker Engine and successful container startup.

---

## 19. Conclusion

Task 4 implements a modular, containerization-ready FastAPI service with health endpoints, Prometheus instrumentation, environment-based configuration, security-oriented Docker settings, automated tests, and a repeatable latency benchmark.

The local test suite passed 10 tests, and the recorded mock-provider benchmark completed 100 requests with a 0% failure rate and measured throughput of 154.47 requests per second.

The work establishes a foundation for integrating a real AI provider and deploying the service into a client-controlled environment. Actual Docker runtime validation, end-to-end Prometheus scraping, real-model performance testing, and client VPC deployment remain outstanding verification steps.

---

**Project:** `Task_4_ProductionAIService`  
**Repository:** `Datheon_Forward_Deployed_Engineering_Internship`  
**Primary focus:** Production-oriented API engineering, observability, container hardening, and performance measurement.
