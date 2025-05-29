# Task: Implement OpenTelemetry Tracing with Local LGTM Stack

## Commit 1: feat: add OpenTelemetry dependencies and configuration

**Description:**
Add required OpenTelemetry packages and create initial configuration module. This will set up the core tracing infrastructure.

Files to modify/create:

- `pyproject.toml`: Add OpenTelemetry dependencies
- `Lib/telemetry/config.py`: Create new configuration module
- `Lib/telemetry/__init__.py`: Create package initialization

**Verification:**

1. **Automated Test(s):**
   - **Command:** `pytest Lib/telemetry/test_config.py -v`
   - **Expected Outcome:** `Tests verify that OpenTelemetry configuration is properly initialized with correct endpoints and service name`
2. **Logging Check:**
   - **Action:** `Initialize telemetry configuration and check logs`
   - **Expected Log:** `INFO: OpenTelemetry initialized with service name: td-arena, endpoint: http://localhost:4318`
   - **Toggle Mechanism:** `LOG_LEVEL=info`

---

## Commit 2: feat: implement base tracing decorators and context

**Description:**
Create base tracing decorators and context management for TouchDesigner operators. This will provide the foundation for instrumenting specific components.

Files to modify/create:

- `Lib/telemetry/decorators.py`: Create tracing decorators
- `Lib/telemetry/context.py`: Create context management utilities
- `Lib/telemetry/test_decorators.py`: Add unit tests
- `Lib/telemetry/test_context.py`: Add unit tests

**Verification:**

1. **Automated Test(s):**
   - **Command:** `pytest Lib/telemetry/test_decorators.py Lib/telemetry/test_context.py -v`
   - **Expected Outcome:** `Tests verify that decorators properly create spans and context management works as expected`
2. **Logging Check:**
   - **Action:** `Apply tracing decorator to a test operator and check logs`
   - **Expected Log:** `INFO: Created span: operator_execute, parent: None, attributes: {'operator.name': 'test_op'}`
   - **Toggle Mechanism:** `LOG_LEVEL=info`

---

## Commit 3: feat: integrate tracing with core TD-Arena components

**Description:**
Integrate tracing into core TD-Arena components, focusing on key operations and state changes.

Files to modify:

- `Lib/core/state.py`: Add tracing to state management
- `Lib/core/operators.py`: Add tracing to operator lifecycle
- `Lib/core/events.py`: Add tracing to event handling
- `Lib/core/test_state.py`: Update tests
- `Lib/core/test_operators.py`: Update tests
- `Lib/core/test_events.py`: Update tests

**Verification:**

1. **Automated Test(s):**
   - **Command:** `pytest Lib/core/test_*.py -v`
   - **Expected Outcome:** `Tests verify that tracing is properly integrated into core components and spans are created for key operations`
2. **Logging Check:**
   - **Action:** `Perform state change and check logs`
   - **Expected Log:** `INFO: State change span created: state_update, attributes: {'state.key': 'test_state', 'state.value': 'new_value'}`
   - **Toggle Mechanism:** `LOG_LEVEL=info`

---

## Commit 4: feat: add Grafana Tempo integration and visualization

**Description:**
Configure Grafana Tempo integration and create initial dashboards for trace visualization.

Files to modify/create:

- `Monitoring/grafana/provisioning/dashboards/traces.json`: Create traces dashboard
- `Monitoring/grafana/provisioning/datasources/tempo.yaml`: Configure Tempo datasource
- `Docs/monitoring/traces.md`: Add documentation for trace visualization

**Verification:**

1. **Automated Test(s):**
   - **Command:** `curl -s http://localhost:3000/api/datasources | grep tempo`
   - **Expected Outcome:** `Verify Tempo datasource is properly configured`
2. **Logging Check:**
   - **Action:** `Check Grafana logs for datasource initialization`
   - **Expected Log:** `INFO: Datasource "Tempo" initialized successfully`
   - **Toggle Mechanism:** `ENABLE_LOGS_GRAFANA=true in docker-compose.yml`

---

## Commit 5: docs: add OpenTelemetry usage documentation

**Description:**
Create comprehensive documentation for using OpenTelemetry tracing in TD-Arena.

Files to create/modify:

- `Docs/telemetry/README.md`: Create main telemetry documentation
- `Docs/telemetry/best-practices.md`: Add best practices guide
- `Docs/telemetry/examples.md`: Add usage examples
- Update main `README.md` with telemetry section

**Verification:**

1. **Automated Test(s):**
   - **Command:** `markdownlint Docs/telemetry/*.md`
   - **Expected Outcome:** `All markdown files pass linting`
2. **Logging Check:**
   - **Action:** `N/A - Documentation only`
   - **Expected Log:** `N/A`
   - **Toggle Mechanism:** `N/A`
