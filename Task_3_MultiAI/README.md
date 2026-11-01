
MULTIAI — AUTONOMOUS ENTERPRISE ERP/CRM FIELD AGENT DETAILED PROJECT
README ==========================================================

Purpose: describe the project’s goals, architecture, module
responsibilities, safety model, setup, testing, and roadmap. Project
directory: MultiAI Language: Python Planned frameworks: LangChain,
LangGraph, Gemini, FastAPI, Streamlit, Pydantic, Pytest

STATUS WARNING

This documentation describes the intended design. A folder or empty file
is not evidence that a feature is implemented. Only mark a capability
complete after code exists, tests pass, and observed behavior matches
the description. The initial ERP and CRM adapters use simulated data,
not live enterprise systems.

CONTENTS

1.  Project Overview
2.  Project Goals
3.  Non-Goals
4.  Business Problem
5.  Supported ERP Action: Inventory Lookup
6.  Supported ERP Action: Stock Availability
7.  Supported CRM Action: Lead Lookup
8.  Supported CRM Action: Update Lead Status
9.  Supported CRM Action: Create Ticket
10. Natural-Language Understanding
11. Tool Registry
12. LangChain
13. LangGraph
14. Gemini
15. FastAPI
16. Streamlit
17. Pydantic Schemas
18. Configuration
19. ERP Adapter
20. CRM Lead Adapter
21. CRM Ticket Adapter
22. Validation
23. Permissions
24. Human Approval
25. Approval State Machine
26. Idempotency
27. Retry Policy
28. Audit Logging
29. Agent State
30. Deterministic Fallback
31. Prompt Injection
32. API Endpoints
33. API Error Handling
34. Streamlit Interface
35. Seed Data
36. Testing Strategy
37. Acceptance Criteria
38. Local Setup
39. Environment File
40. Run the API
41. Run the UI
42. Run Tests
43. Troubleshooting Dependencies
44. Troubleshooting Gemini
45. Troubleshooting API Imports
46. Troubleshooting Approval
47. Troubleshooting Duplicate Writes
48. Production Hardening
49. Privacy
50. Interview Explanation
51. Demo Script
52. Development Roadmap
53. Definition of Done
54. Future Enhancements
55. Repository Hygiene
56. Glossary: Agent
57. Glossary: Tool Orchestration
58. Glossary: Idempotency
59. Final Summary

IMPLEMENTATION CHECKLIST

[ ] Configuration loads from environment variables. [ ] Pydantic schemas
are implemented and tested. [ ] ERP inventory lookup works. [ ] Stock
availability comparison works. [ ] CRM lead lookup works. [ ] Lead
status updates require approval. [ ] Ticket creation requires approval.
[ ] Tool registry contains only supported actions. [ ] Deterministic
planning works without Gemini. [ ] Gemini planning returns validated
structured proposals. [ ] LangGraph routes read and write operations
correctly. [ ] Permissions are enforced by backend code. [ ] Approval
transitions are tested. [ ] Idempotency prevents duplicate writes. [ ]
Retry behavior is bounded and tested. [ ] Audit logs exclude secrets. [
] FastAPI endpoints are tested. [ ] Streamlit UI calls the backend. [ ]
Full pytest suite passes. [ ] README reflects the actual implementation.

DETAILED DOCUMENTATION

01. Project Overview

MultiAI is an autonomous enterprise agent for controlled ERP and CRM
workflows. It translates natural-language requests into calls to a
small, registered set of business tools. The first version uses
simulated local records so it can be developed without real company
access. Gemini may interpret requests; LangChain defines tools;
LangGraph coordinates workflow state. Python validation, permissions,
approvals, idempotency, retries, and audit events control execution.
This document describes the target architecture; verify implementation
status against the actual code.

Practical review questions: - Is the behavior for project overview
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

02. Project Goals

Make common business actions accessible through natural-language
requests. Support inventory lookup, stock checks, lead lookup,
lead-status updates, and ticket creation. Validate every proposed action
before invoking a business tool. Require human approval before any
operation that changes business records. Prevent repeated requests from
accidentally creating duplicate side effects. Keep the workflow testable
without requiring a live model API or real ERP/CRM credentials.

Practical review questions: - Is the behavior for project goals
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

03. Non-Goals

MultiAI is not a complete ERP product or a complete CRM product. The
initial adapters are simulated and do not represent live company data.
The LLM must not execute arbitrary Python, shell commands, or raw SQL.
The LLM must not bypass approval or authorization rules. A local demo
token is not production-grade authentication. Passing unit tests does
not by itself prove production readiness.

Practical review questions: - Is the behavior for non-goals implemented
in code? - Are success, invalid-input, and failure cases covered by
tests? - Does the documentation match observed behavior? - Are
permissions and side effects enforced by deterministic backend code? -
Is sensitive information excluded from logs and source control?

04. Business Problem

Employees often switch between systems to find inventory or update
customer records. Natural-language requests can reduce the effort needed
to locate the correct operation. Business actions have consequences and
should not be executed solely on model confidence. An incorrect update
can affect sales processes, customer service, or downstream workflows.
MultiAI combines a convenient interface with deterministic controls
around side effects. The system aims to make actions traceable,
constrained, and recoverable.

Practical review questions: - Is the behavior for business problem
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

05. Supported ERP Action: Inventory Lookup

Action name: inventory_lookup. Input: a SKU identifier such as SKU-100.
Output: the known product identifier, quantity, and availability
information. Behavior: read-only; no human approval is required for this
lookup. Unknown SKUs should return a clear not-found result rather than
fabricated stock. Stock values in the initial demo are sample data, not
live enterprise inventory.

Practical review questions: - Is the behavior for supported erp action:
inventory lookup implemented in code? - Are success, invalid-input, and
failure cases covered by tests? - Does the documentation match observed
behavior? - Are permissions and side effects enforced by deterministic
backend code? - Is sensitive information excluded from logs and source
control?

06. Supported ERP Action: Stock Availability

Action name: check_stock_availability. Input: a SKU and a requested
quantity. Output: whether available stock meets the requested quantity.
The requested quantity must be a positive integer. Zero stock should be
represented explicitly as unavailable. The result must be calculated
from the tool result, not guessed by the language model.

Practical review questions: - Is the behavior for supported erp action:
stock availability implemented in code? - Are success, invalid-input,
and failure cases covered by tests? - Does the documentation match
observed behavior? - Are permissions and side effects enforced by
deterministic backend code? - Is sensitive information excluded from
logs and source control?

07. Supported CRM Action: Lead Lookup

Action name: crm_lead_lookup. Input: a lead identifier such as LEAD-002.
Output: a structured record with the fields the caller is allowed to
view. Unknown lead identifiers should return a predictable not-found
response. Lookup is read-only and should not change the lead record.
Real deployments must apply resource-level authorization to returned
fields.

Practical review questions: - Is the behavior for supported crm action:
lead lookup implemented in code? - Are success, invalid-input, and
failure cases covered by tests? - Does the documentation match observed
behavior? - Are permissions and side effects enforced by deterministic
backend code? - Is sensitive information excluded from logs and source
control?

08. Supported CRM Action: Update Lead Status

Action name: crm_update_lead_status. Input: a lead identifier and a
supported target status. Allowed status values must be declared by
application code. The operation changes business data and therefore
requires human approval. The lead record must remain unchanged while
approval is pending or rejected. Repeated approval requests must not
execute the same update more than once.

Practical review questions: - Is the behavior for supported crm action:
update lead status implemented in code? - Are success, invalid-input,
and failure cases covered by tests? - Does the documentation match
observed behavior? - Are permissions and side effects enforced by
deterministic backend code? - Is sensitive information excluded from
logs and source control?

09. Supported CRM Action: Create Ticket

Action name: crm_create_ticket. Input: title, description, customer
reference, and priority. Required fields must be validated before an
approval operation is created. Priority should be restricted to a
defined set such as low, medium, and high. Ticket creation is a write
operation and requires approval. An idempotency key should prevent
duplicate tickets from repeated logical requests.

Practical review questions: - Is the behavior for supported crm action:
create ticket implemented in code? - Are success, invalid-input, and
failure cases covered by tests? - Does the documentation match observed
behavior? - Are permissions and side effects enforced by deterministic
backend code? - Is sensitive information excluded from logs and source
control?

10. Natural-Language Understanding

Users should be able to phrase supported requests in ordinary language.
Gemini can help map varied wording to a structured action proposal.
Model output may be incomplete, malformed, ambiguous, or incorrect. The
application must validate action names and arguments after model
interpretation. If required information is missing, the agent should ask
a question or return validation feedback. The agent must not claim an
action succeeded before the tool reports success.

Practical review questions: - Is the behavior for natural-language
understanding implemented in code? - Are success, invalid-input, and
failure cases covered by tests? - Does the documentation match observed
behavior? - Are permissions and side effects enforced by deterministic
backend code? - Is sensitive information excluded from logs and source
control?

11. Tool Registry

The registry is an allowlist of callable business operations. Each entry
should define a stable name, description, argument schema, and handler.
Each entry should identify whether it is read-only or changes data. Each
entry should specify the permissions and approval policy it requires.
Model output must resolve to a registered entry before any tool can be
called. Unknown action names should be rejected rather than imported or
executed dynamically.

Practical review questions: - Is the behavior for tool registry
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

12. LangChain

LangChain provides interfaces for language-model integration and tool
definitions. Tools should expose narrow business functions with typed
arguments. Tool descriptions help the model select an operation but do
not enforce security. All arguments must be validated by deterministic
application code. Tool handlers should return structured results and
known error categories. LangChain is an integration layer, not a
substitute for business policy.

Practical review questions: - Is the behavior for langchain implemented
in code? - Are success, invalid-input, and failure cases covered by
tests? - Does the documentation match observed behavior? - Are
permissions and side effects enforced by deterministic backend code? -
Is sensitive information excluded from logs and source control?

13. LangGraph

LangGraph coordinates the agent workflow through state and transitions.
Potential nodes include request understanding, planning, validation,
permission checks, and execution. Conditional edges route read
operations to execution and write operations to approval. Failure states
should route to safe response handling rather than continue blindly.
Graph state should contain only the information needed for the current
request. Workflow tests should verify transitions as well as the final
message.

Practical review questions: - Is the behavior for langgraph implemented
in code? - Are success, invalid-input, and failure cases covered by
tests? - Does the documentation match observed behavior? - Are
permissions and side effects enforced by deterministic backend code? -
Is sensitive information excluded from logs and source control?

14. Gemini

Gemini may interpret a user request and propose a structured action. The
API key belongs in environment configuration, never in source code.
Model output is untrusted input, even when returned in valid JSON. Only
registered actions may be selected for execution. Model errors should be
handled with a clear error or a documented deterministic fallback. Unit
tests should run without a real Gemini API key.

Practical review questions: - Is the behavior for gemini implemented in
code? - Are success, invalid-input, and failure cases covered by
tests? - Does the documentation match observed behavior? - Are
permissions and side effects enforced by deterministic backend code? -
Is sensitive information excluded from logs and source control?

15. FastAPI

FastAPI exposes the backend through typed HTTP endpoints. Request and
response schemas should be explicit. Route handlers should remain thin
and call shared service functions. GET endpoints should not perform
business writes. Protected operations must enforce approval and
permissions server-side. OpenAPI documentation helps development but
does not itself secure endpoints.

Practical review questions: - Is the behavior for fastapi implemented in
code? - Are success, invalid-input, and failure cases covered by
tests? - Does the documentation match observed behavior? - Are
permissions and side effects enforced by deterministic backend code? -
Is sensitive information excluded from logs and source control?

16. Streamlit

Streamlit provides a lightweight interface for trying MultiAI requests.
The UI should display the request result and operation status clearly.
Pending writes should be visibly distinct from completed writes. The UI
may show pending approvals and recent safe audit events. The UI must
call the backend rather than bypassing its safety controls. Hiding a
button is not a substitute for server-side authorization.

Practical review questions: - Is the behavior for streamlit implemented
in code? - Are success, invalid-input, and failure cases covered by
tests? - Does the documentation match observed behavior? - Are
permissions and side effects enforced by deterministic backend code? -
Is sensitive information excluded from logs and source control?

17. Pydantic Schemas

schemas.py should define request, response, tool-argument, and operation
models. Examples include AgentRequest, AgentResponse, InventoryQuery,
LeadStatusUpdate, and TicketCreate. Constrain string lengths, numeric
ranges, supported status values, and required fields. Reject unexpected
fields when strict validation is appropriate. Do not pass arbitrary
dictionaries directly into sensitive business functions. Tests should
cover both valid inputs and invalid boundary cases.

Practical review questions: - Is the behavior for pydantic schemas
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

18. Configuration

config.py should load environment settings in one predictable place.
Potential settings include Gemini model, API key, API base URL, and
local approval configuration. .env.example documents required setting
names with placeholder values. .env contains local secrets and must be
excluded from version control. Missing model configuration should
trigger a documented fallback or clear configuration error. Never print
secret values while debugging configuration.

Practical review questions: - Is the behavior for configuration
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

19. ERP Adapter

erp/inventory.py owns the simulated inventory adapter. Keep inventory
storage details out of the agent graph and API route handlers. Normalize
SKU identifiers and return structured results. Unknown SKUs should not
be treated as zero stock unless that is an explicit domain rule. Future
adapters may call an external ERP API behind the same interface. Real
integrations need authentication, timeouts, rate-limit handling, and
data-access controls.

Practical review questions: - Is the behavior for erp adapter
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

20. CRM Lead Adapter

crm/leads.py owns lead lookup and lead-status changes. Define supported
lead statuses in code or a central domain schema. Return not-found
results for unknown lead identifiers. Lead updates must be routed
through the approved operation service. Do not trust the LLM to
determine whether a user has permission to update a lead. Future CRM
adapters should normalize vendor responses into application schemas.

Practical review questions: - Is the behavior for crm lead adapter
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

21. CRM Ticket Adapter

crm/tickets.py owns support-ticket creation. Ticket records should have
a stable identifier and validated fields. Require a title, description,
customer reference, and supported priority. Ticket creation must wait
for approval before changing data. Repeated requests should reuse the
known operation result when the idempotency key matches. Real adapters
should reconcile uncertain outcomes after timeouts before retrying.

Practical review questions: - Is the behavior for crm ticket adapter
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

22. Validation

Validation determines whether the input satisfies the action’s data
contract. Check required fields, formats, allowed values, string
lengths, and numeric ranges. Validation must happen after model parsing
and before tool execution. Sensitive business functions should also
validate their own arguments at the service boundary. Validation is
distinct from authorization: valid data can still be unauthorized.
Invalid inputs should not create approval records or mutate business
data.

Practical review questions: - Is the behavior for validation implemented
in code? - Are success, invalid-input, and failure cases covered by
tests? - Does the documentation match observed behavior? - Are
permissions and side effects enforced by deterministic backend code? -
Is sensitive information excluded from logs and source control?

23. Permissions

Authorization determines whether an actor may perform a specific action
on a resource. Production identity must come from a trusted
authentication mechanism. Do not trust a role, tenant, or approver
identity supplied by the client. Permissions should follow least
privilege. Reading inventory should not automatically grant permission
to update CRM records. Multi-tenant deployments must enforce tenant
boundaries at the data-access layer.

Practical review questions: - Is the behavior for permissions
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

24. Human Approval

Approval is an application state transition, not a model-generated
sentence. Write requests should create a pending operation containing
exact validated arguments. Business data must remain unchanged while an
operation is pending. An approver must decide on the exact action and
arguments presented for review. If arguments change, the old approval
must no longer authorize the changed operation. Production approval
requires authenticated approvers and durable operation state.

Practical review questions: - Is the behavior for human approval
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

25. Approval State Machine

Possible statuses include proposed, pending_approval, approved,
rejected, executing, succeeded, and failed. Only documented state
transitions should be accepted. Rejected operations must not execute. An
operation already executing or succeeded must not be executed again by
repeated approval. State transitions should be atomic when concurrent
requests are possible. Uncertain external outcomes may require a
needs_reconciliation status.

Practical review questions: - Is the behavior for approval state machine
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

26. Idempotency

Idempotency prevents repeated logical requests from duplicating side
effects. Associate an idempotency key with the normalized action and
arguments. Same key plus same payload should return the existing
operation or result. Same key plus different payload should be rejected
as a conflict. In-memory idempotency only protects a single running
process. Production systems need durable uniqueness constraints or
equivalent atomic storage.

Practical review questions: - Is the behavior for idempotency
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

27. Retry Policy

Retries should be bounded and visible in logs or audit events. Eligible
failures may include selected timeouts, connection failures, rate
limits, and transient server errors. Do not retry validation failures,
permission denials, or rejected approvals. Retries for writes require
idempotency or a reconciliation strategy. Define maximum attempts and
backoff behavior explicitly. After the retry limit, return a clear
failure or reconciliation status.

Practical review questions: - Is the behavior for retry policy
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

28. Audit Logging

Audit events record important decisions and side effects. Useful events
include request_received, action_proposed, approval_requested, and
execution_succeeded. Include timestamps, request IDs, operation IDs,
action names, and safe status metadata. Do not log API keys, passwords,
approval tokens, or full authorization headers. Audit records should not
contain unnecessary sensitive customer information. Production audit
history needs access controls, retention, and integrity protections.

Practical review questions: - Is the behavior for audit logging
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

29. Agent State

State can include request ID, user message, action proposal, arguments,
validation result, and tool result. Track approval requirement and
operation ID explicitly. Track error categories rather than relying only
on free-form messages. Do not store secrets or unnecessary personal data
in graph state. Conversation context can help interpret follow-ups but
does not grant permission. Bound the context and isolate it by user or
session.

Practical review questions: - Is the behavior for agent state
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

30. Deterministic Fallback

A deterministic planner can recognize a limited set of common request
patterns. It helps the project remain testable when Gemini is
unavailable. It should share the same registry, schemas, permissions,
and approval controls as the model path. Fallback should report
ambiguity rather than guess missing business identifiers. A failed model
call must never relax safety policy. Document which phrases the fallback
supports and test them.

Practical review questions: - Is the behavior for deterministic fallback
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

31. Prompt Injection

User messages and retrieved business text must be treated as untrusted
data. An instruction to ignore approval rules must not change
application policy. The model must not have access to arbitrary shell,
filesystem, import, or SQL execution. Only registered tools should be
exposed to the agent. Critical controls must run after model output,
regardless of prompt content. Test explicit attempts to bypass approvals
and request unsupported actions.

Practical review questions: - Is the behavior for prompt injection
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

32. API Endpoints

A possible health route is GET /health. A possible agent route is POST
/agent/run. Approval routes may list pending operations and decide a
specific operation. Read routes may expose inventory and lead lookup.
Write routes must use the same approval service as agent-triggered
operations. Finalize exact route names in code and keep this
documentation synchronized.

Practical review questions: - Is the behavior for api endpoints
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

33. API Error Handling

Use consistent error categories such as invalid_request, not_found,
permission_denied, and approval_required. Return actionable but safe
messages. Do not expose stack traces, secrets, database internals, or
private headers to users. Use suitable HTTP status codes and structured
response bodies. Attach a correlation identifier to logs when possible.
Tests should cover success, validation errors, authorization errors, and
dependency failures.

Practical review questions: - Is the behavior for api error handling
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

34. Streamlit Interface

Provide a request input and submit control. Display the result and
current operation status. Show pending approval details to an authorized
demo approver. Show recent audit events with sensitive fields excluded.
Provide sample requests to make supported capabilities easy to discover.
Display API connectivity errors rather than inventing successful
results.

Practical review questions: - Is the behavior for streamlit interface
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

35. Seed Data

Seed data is only for demonstration and automated tests. Example
inventory can include SKU-100, SKU-200, and SKU-300. Example lead
records can include LEAD-001, LEAD-002, and LEAD-003. Define seed
records centrally rather than duplicating them in every module. Tests
should reset the store so test cases remain independent. Never represent
sample inventory or leads as live company information.

Practical review questions: - Is the behavior for seed data implemented
in code? - Are success, invalid-input, and failure cases covered by
tests? - Does the documentation match observed behavior? - Are
permissions and side effects enforced by deterministic backend code? -
Is sensitive information excluded from logs and source control?

36. Testing Strategy

Unit tests cover schemas, validators, permissions, tools, retries, and
idempotency. Workflow tests use deterministic planning and fake tools.
API tests verify request and response contracts. Integration tests for
Gemini or vendor APIs should be optional and separately marked. Rejected
writes must be tested for absence of side effects. Run the full suite
after fixing a focused test failure.

Practical review questions: - Is the behavior for testing strategy
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

37. Acceptance Criteria

Known inventory requests return the actual tool result. Unknown
inventory SKUs return a safe not-found result. Known leads can be looked
up. Lead updates remain pending until approved. Rejected approvals leave
records unchanged. Approved operations execute at most once. Ticket
creation validates fields and prevents duplicate logical requests. Audit
events capture relevant outcomes without logging secrets. All advertised
capabilities have tests and implementation code. The full test suite
passes in a clean environment.

Practical review questions: - Is the behavior for acceptance criteria
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

38. Local Setup

Use Python 3.12 and a project-local virtual environment. Create the
environment with: py -3.12 -m venv .venv Activate it in PowerShell with:
..venv.ps1 Upgrade pip using: python -m pip install –upgrade pip Install
project dependencies using: pip install -r requirements.txt Do not
commit the virtual environment to Git.

Practical review questions: - Is the behavior for local setup
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

39. Environment File

Copy .env.example to .env for local development. Add a valid Gemini API
key only if model-backed planning is enabled. Use the environment
variable names that config.py actually reads. Keep .env excluded in
.gitignore. Never include real secrets in README files, screenshots,
tests, or public commits. Rotate any key immediately if it becomes
exposed.

Practical review questions: - Is the behavior for environment file
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

40. Run the API

The intended command is: uvicorn field_agent.api.main:app –reload
–app-dir src Run the command from the MultiAI project root with the
virtual environment active. Use reload mode only for local development.
Check the startup output for the configured host and port. Open the
health endpoint and interactive API documentation after startup. Ensure
the import path matches the actual package structure.

Practical review questions: - Is the behavior for run the api
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

41. Run the UI

The intended command is: streamlit run app.py Run the UI in a separate
terminal when it calls the API over HTTP. Configure the API base URL to
match the running backend. The UI should display an error if the API is
unreachable. The UI must not mutate business records directly to bypass
backend policy. Keep business logic in backend services rather than
Streamlit code.

Practical review questions: - Is the behavior for run the ui implemented
in code? - Are success, invalid-input, and failure cases covered by
tests? - Does the documentation match observed behavior? - Are
permissions and side effects enforced by deterministic backend code? -
Is sensitive information excluded from logs and source control?

42. Run Tests

Run the full suite with: pytest -q Use pytest -v for more detailed
output. Run a single test module while developing a focused feature.
Unit tests should not require a real Gemini API key. Use fake tools or
deterministic planning for repeatable workflow tests. Do not claim that
tests pass unless the command has completed successfully.

Practical review questions: - Is the behavior for run tests implemented
in code? - Are success, invalid-input, and failure cases covered by
tests? - Does the documentation match observed behavior? - Are
permissions and side effects enforced by deterministic backend code? -
Is sensitive information excluded from logs and source control?

43. Troubleshooting Dependencies

Confirm the virtual environment is active before installing packages.
Check the Python version if a package cannot be installed. Read the
first meaningful error rather than only the final summary. Upgrade pip
in the active environment when appropriate. Resolve package
compatibility deliberately and record working versions. Do not delete
unrelated project files to solve a dependency conflict.

Practical review questions: - Is the behavior for troubleshooting
dependencies implemented in code? - Are success, invalid-input, and
failure cases covered by tests? - Does the documentation match observed
behavior? - Are permissions and side effects enforced by deterministic
backend code? - Is sensitive information excluded from logs and source
control?

44. Troubleshooting Gemini

Confirm that config.py uses the same variable name as .env. Confirm .env
is in the expected project directory. Check whether the API key is valid
and the configured model is supported. Review quota and network errors
using sanitized diagnostics. Test the deterministic fallback separately.
Never print the API key to debug a model configuration problem.

Practical review questions: - Is the behavior for troubleshooting gemini
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

45. Troubleshooting API Imports

Confirm the terminal is at the project root. Activate the project
virtual environment. Check package names and init.py files. Verify that
the Uvicorn module path matches the actual source tree. Inspect the
first traceback line that points to project code. Run a focused import
test before restarting the server.

Practical review questions: - Is the behavior for troubleshooting api
imports implemented in code? - Are success, invalid-input, and failure
cases covered by tests? - Does the documentation match observed
behavior? - Are permissions and side effects enforced by deterministic
backend code? - Is sensitive information excluded from logs and source
control?

46. Troubleshooting Approval

If a write runs before approval, stop and fix the execution path. Verify
the tool registry marks the action as a write. Verify the graph routes
writes through the approval stage. Verify the pending state does not
call the write adapter. Verify rejection leaves the record unchanged.
Add a regression test for every discovered approval bypass.

Practical review questions: - Is the behavior for troubleshooting
approval implemented in code? - Are success, invalid-input, and failure
cases covered by tests? - Does the documentation match observed
behavior? - Are permissions and side effects enforced by deterministic
backend code? - Is sensitive information excluded from logs and source
control?

47. Troubleshooting Duplicate Writes

Check whether the client submitted the same request more than once.
Inspect request IDs and idempotency-key generation. Ensure the key is
bound to normalized action arguments. Use atomic storage for idempotency
records in multi-worker deployments. Reconcile an uncertain external
result before retrying a write. Test duplicate user requests separately
from repeated approval requests.

Practical review questions: - Is the behavior for troubleshooting
duplicate writes implemented in code? - Are success, invalid-input, and
failure cases covered by tests? - Does the documentation match observed
behavior? - Are permissions and side effects enforced by deterministic
backend code? - Is sensitive information excluded from logs and source
control?

48. Production Hardening

Use trusted authentication and server-side authorization. Use durable
storage for business records, approvals, and audit events. Protect
operation transitions against concurrency. Use a secret manager and TLS
for real integrations. Add timeouts, rate limits, bounded retries, and
reconciliation procedures. Review data sent to model providers for
privacy and compliance requirements.

Practical review questions: - Is the behavior for production hardening
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

49. Privacy

Send only the business context needed for the requested action. Do not
include secrets or full authorization headers in logs. Redact
unnecessary customer details from audit events. Define retention and
access policies for stored operation history. Use sample data for
development and demonstrations. Review model-provider data handling
before sending real enterprise records.

Practical review questions: - Is the behavior for privacy implemented in
code? - Are success, invalid-input, and failure cases covered by
tests? - Does the documentation match observed behavior? - Are
permissions and side effects enforced by deterministic backend code? -
Is sensitive information excluded from logs and source control?

50. Interview Explanation

MultiAI is an enterprise agent that maps natural-language requests to
controlled ERP and CRM tools. Gemini may interpret requests, LangChain
defines tools, and LangGraph coordinates workflow state. Pydantic
validates arguments and deterministic code enforces permissions and
approval. Write operations require approval before business data
changes. Idempotency prevents duplicate side effects and bounded retries
handle selected transient failures. The initial prototype uses simulated
records and needs further hardening before production use.

Practical review questions: - Is the behavior for interview explanation
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

51. Demo Script

Start the FastAPI backend and Streamlit interface. Ask the agent to
check inventory for SKU-100. Ask the agent to look up LEAD-002. Request
a status update and show the pending approval state. Reject the
operation and verify that the record is unchanged. Repeat the request,
approve it, and verify that the update occurs once. Inspect audit events
and run the actual automated test suite. Clearly label simulated records
and do not claim unimplemented features are complete.

Practical review questions: - Is the behavior for demo script
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

52. Development Roadmap

First implement configuration and schemas. Next implement ERP and CRM
tools with unit tests. Then add validation, permissions, approval,
idempotency, and audit logging. Add deterministic planning before model
integration. Integrate Gemini and build the LangGraph workflow. Expose
the workflow through FastAPI and create the Streamlit client. Complete
workflow and API tests, then update the README from tested behavior.

Practical review questions: - Is the behavior for development roadmap
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

53. Definition of Done

Code exists in the intended module and imports correctly. Inputs and
outputs have explicit schemas. Success and error paths are handled.
Tests verify both responses and side effects. Write operations cannot
execute before approval. Repeated requests cannot duplicate the same
logical write. The full regression suite passes. Documentation matches
actual behavior and known limitations.

Practical review questions: - Is the behavior for definition of done
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

54. Future Enhancements

Add durable SQLite storage for local development. Add PostgreSQL for
multi-user deployments. Integrate a trusted identity provider and
role-based permissions. Add real ERP and CRM sandbox adapters. Add
metrics, tracing, deployment automation, and monitoring. Add evaluation
datasets for intent and tool selection. Keep every new tool inside the
same registry, validation, approval, and audit conventions.

Practical review questions: - Is the behavior for future enhancements
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

55. Repository Hygiene

Commit source code, tests, documentation, and example configuration. Do
not commit .env files containing credentials. Do not commit .venv,
pycache, or pytest cache directories. Review git status before staging
changes. Stage only the intended MultiAI paths in a multi-task
repository. Use descriptive commits for individual features and safety
controls.

Practical review questions: - Is the behavior for repository hygiene
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

56. Glossary: Agent

An agent interprets a goal and selects actions to pursue it. In MultiAI,
the agent is limited to registered business operations. It does not have
unrestricted computer or shell access. Its decisions must pass
deterministic validation and policy checks. Agent behavior should be
inspectable through state and audit events. An agent response is not
proof that a business action succeeded.

Practical review questions: - Is the behavior for glossary: agent
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

57. Glossary: Tool Orchestration

Tool orchestration coordinates selection, ordering, and execution of
tools. A multi-step request may require more than one tool call. Each
step must preserve validation and authorization controls. Write steps
must not bypass the approval gate. Tool outputs should be normalized
before later steps use them. Failures should stop or branch the workflow
safely.

Practical review questions: - Is the behavior for glossary: tool
orchestration implemented in code? - Are success, invalid-input, and
failure cases covered by tests? - Does the documentation match observed
behavior? - Are permissions and side effects enforced by deterministic
backend code? - Is sensitive information excluded from logs and source
control?

58. Glossary: Idempotency

Idempotency means repeated logical operations do not repeat side
effects. It is important for ticket creation and other writes. A key
should be associated with normalized action arguments. Reusing a key
with a different payload should be rejected. In-memory tracking is not
sufficient for multiple workers or process restarts. Durable storage
should enforce uniqueness atomically.

Practical review questions: - Is the behavior for glossary: idempotency
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

59. Final Summary

MultiAI makes enterprise business actions easier to request in natural
language. It combines a limited set of ERP and CRM tools with explicit
workflow orchestration. Gemini may assist with interpretation, but
deterministic Python code controls execution. Validation, permissions,
approval, idempotency, retries, and audit events are core design
requirements. The initial adapters use simulated data and must be
labeled honestly. Every advertised capability should be backed by
implementation, tests, and current documentation.

Practical review questions: - Is the behavior for final summary
implemented in code? - Are success, invalid-input, and failure cases
covered by tests? - Does the documentation match observed behavior? -
Are permissions and side effects enforced by deterministic backend
code? - Is sensitive information excluded from logs and source control?

REFERENCE COMMANDS

Create a Python 3.12 virtual environment: py -3.12 -m venv .venv

Activate in PowerShell: ..venv.ps1


Install dependencies: python -m pip install –upgrade pip pip install -r
requirements.txt

Run API in development: uvicorn field_agent.api.main:app –reload
–app-dir src

Run Streamlit UI: streamlit run app.py

Run tests: pytest -q

These commands are intended examples. Confirm entry points and package
names against the actual project files before relying on them.

