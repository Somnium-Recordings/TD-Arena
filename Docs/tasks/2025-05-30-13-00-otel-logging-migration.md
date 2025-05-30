# Migration Instructions: OpenTelemetry Unified Logging & Tracing

## Phase 1: Redirect OTEL Traces to Alloy

### Step 1: Update OTEL trace exporter to point to Alloy
**Commit: "feat: redirect OTEL traces from LGTM to Alloy"**

In `Lib/tda_telemetry`:
```python
# Change the endpoint from LGTM to Alloy
# FROM:
trace_exporter = OTLPSpanExporter(
    endpoint="localhost:4317",  # or whatever LGTM endpoint
    insecure=True,
)

# TO:
trace_exporter = OTLPSpanExporter(
    endpoint="localhost:4317",  # Alloy's OTLP receiver
    insecure=True,
    timeout=1,  # Short timeout for local connection
    compression=None,  # No compression needed locally
)
```

## Phase 2: Setup OpenTelemetry Logging

### Step 2: Add OpenTelemetry logging dependencies
**Commit: "build: add OpenTelemetry logging dependencies"**

Update `requirements.txt` or `pyproject.toml`:
```txt
opentelemetry-api
opentelemetry-sdk
opentelemetry-exporter-otlp
opentelemetry-instrumentation-logging
```

### Step 3: Create OpenTelemetry logging setup
**Commit: "feat: add OpenTelemetry logging configuration"**

Create `Lib/tda_telemetry/logging_setup.py`:
```python
import logging
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource

def setup_otel_logging(service_name: str = "tda-app", 
                      alloy_endpoint: str = "localhost:4317"):
    """Configure OpenTelemetry logging to send to Alloy."""
    
    # Create resource with service info
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.0",  # Update as needed
    })
    
    # Setup log exporter pointing to Alloy
    log_exporter = OTLPLogExporter(
        endpoint=alloy_endpoint,
        insecure=True,
        timeout=1,
    )
    
    # Create logger provider
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)
    
    # Add batch processor for performance
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(
            log_exporter,
            max_queue_size=2048,
            max_export_batch_size=512,
            schedule_delay_millis=1000,  # Export every second
        )
    )
    
    # Create handler for Python logging integration
    handler = LoggingHandler(
        level=logging.INFO,
        logger_provider=logger_provider
    )
    
    # Don't add to root logger yet - we'll do that in migration
    return handler
```

### Step 4: Create custom filter for existing fields
**Commit: "feat: add OpenTelemetry filter for custom log fields"**

Create `Lib/tda_telemetry/log_filter.py`:
```python
import logging
from opentelemetry import trace

class TdContextOTELFilter(logging.Filter):
    """
    Filter that adds custom TDA context and OTEL trace context to log records.
    Replaces TdContextJsonFormatter functionality.
    """
    
    def filter(self, record):
        
        # TODO: Add your custom fields here
        # Copy the logic from TdContextJsonFormatter.add_fields()
        # For example:
        # record.user_id = get_current_user_id()
        # record.session_id = get_session_id()
        # record.environment = os.getenv("ENVIRONMENT", "development")
        
        return True
```

## Phase 3: Migrate Logging System

### Step 5: Create parallel logging setup
**Commit: "feat: add parallel OTEL logging alongside existing JSON logging"**

In `Lib/Logger`, create `otel_migration.py`:
```python
import logging
from Lib.tda_telemetry.logging_setup import setup_otel_logging
from Lib.tda_telemetry.log_filter import TdContextOTELFilter

def add_otel_logging():
    """Add OTEL logging in parallel with existing file logging."""
    # Setup OTEL handler
    otel_handler = setup_otel_logging()
    
    # Add custom context filter
    otel_filter = TdContextOTELFilter()
    otel_handler.addFilter(otel_filter)
    
    # Add to root logger without removing existing handlers
    root_logger = logging.getLogger()
    root_logger.addHandler(otel_handler)
    
    return otel_handler

# Call this after your existing logger setup
def enable_dual_logging():
    """Enable both file and OTEL logging for migration period."""
    add_otel_logging()
    logging.info("Dual logging enabled - writing to both files and OTEL")
```

### Step 6: Integrate dual logging into application startup
**Commit: "feat: enable dual logging mode for migration testing"**

In your main application initialization:
```python
# After existing logger setup
from Lib.Logger.otel_migration import enable_dual_logging
enable_dual_logging()
```

## Phase 4: Update Alloy Configuration

### Step 7: Update Alloy config for OTLP reception
**Commit: "feat: update Alloy config to receive OTLP logs and traces"**

Update `Monitoring/config.alloy`:
```river
// OTLP receiver for both traces and logs
otelcol.receiver.otlp "default" {
  grpc {
    endpoint = "0.0.0.0:4317"
  }
  
  output {
    traces = [otelcol.processor.batch.default.input]
    logs   = [otelcol.processor.batch.default.input]
  }
}

// Batch processor for performance
otelcol.processor.batch "default" {
  output {
    traces = [otelcol.exporter.otlp.tempo.input]
    logs   = [loki.process.otlp.receiver]
  }
  
  send_batch_size     = 1000
  timeout             = "2s"
  send_batch_max_size = 2000
}

// Export traces to Tempo
otelcol.exporter.otlp "tempo" {
  client {
    endpoint = "tempo:4317"
    tls {
      insecure = true
    }
  }
}

// Process OTLP logs for Loki
loki.process "otlp" {
  forward_to = [loki.write.default.receiver]
  
  stage.json {
    expressions = {
      trace_id = "trace_id",
      span_id  = "span_id",
      severity = "severity_text",
    }
  }
  
  stage.labels {
    values = {
      severity = "",
      trace_id = "",
    }
  }
}

// Keep existing file reading for migration period
loki.source.file "json_logs" {
  targets = [
    {__path__ = "/path/to/Logs/*.log", job = "tda-legacy"},
  ]
  forward_to = [loki.process.legacy.receiver]
}

// Existing Loki write config
loki.write "default" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}
```

## Phase 5: Validate and Switch Over

### Step 8: Add logging comparison utility
**Commit: "test: add utility to verify OTEL logging parity"**

Create `Lib/Logger/verify_migration.py`:
```python
import json
import logging

def log_test_messages():
    """Generate test messages to verify both logging paths work."""
    logger = logging.getLogger(__name__)
    
    # Test different log levels
    logger.debug("Debug test message")
    logger.info("Info test message", extra={"custom_field": "test_value"})
    logger.warning("Warning test message")
    logger.error("Error test message", extra={"error_code": "TEST_001"})
    
    # Test with trace context
    from opentelemetry import trace
    tracer = trace.get_tracer(__name__)
    
    with tracer.start_as_current_span("test_operation"):
        logger.info("Message within span", extra={"operation": "test"})

def verify_logs_in_grafana():
    """
    Manual verification steps:
    1. Run log_test_messages()
    2. Check Grafana Loki for both legacy and OTLP logs
    3. Verify all custom fields are present
    4. Verify trace correlation works
    """
    print("Verification steps:")
    print("1. Check Loki query: {job='tda-legacy'}")
    print("2. Check Loki query: {service_name='tda-app'}")
    print("3. Verify trace_id correlation in Tempo")
```

### Step 9: Remove file-based logging
**Commit: "refactor: remove legacy file-based JSON logging"**

1. Remove file handler from logger configuration in `Lib/Logger`
2. Remove `pythonjsonlogger` from imports
3. Update logger initialization to only use OTEL

```python
# In your main logger setup
def setup_logging():
    """Setup logging using only OpenTelemetry."""
    from Lib.tda_telemetry.logging_setup import setup_otel_logging
    from Lib.tda_telemetry.log_filter import TdContextOTELFilter
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Setup OTEL as the only handler
    otel_handler = setup_otel_logging()
    otel_handler.addFilter(TdContextOTELFilter())
    
    root_logger.addHandler(otel_handler)
    root_logger.setLevel(logging.INFO)
```

## Phase 6: Cleanup

### Step 10: Remove legacy file reading from Alloy
**Commit: "cleanup: remove legacy file-based log ingestion from Alloy"**

Update `Monitoring/config.alloy` to remove the `loki.source.file` section.

### Step 11: Remove old dependencies and code
**Commit: "cleanup: remove pythonjsonlogger and legacy logging code"**

1. Remove `pythonjsonlogger` from requirements
2. Delete old logging files that are no longer needed
3. Clean up the `Logs/` directory

## Performance Optimization (Optional)

### Step 12: Add connection pooling and performance tuning
**Commit: "perf: optimize OTEL export settings for local setup"**

```python
# In logging_setup.py and telemetry setup
import grpc

# Create shared channel for better performance
channel = grpc.insecure_channel(
    'localhost:4317',
    options=[
        ('grpc.keepalive_time_ms', 10000),
        ('grpc.keepalive_timeout_ms', 5000),
        ('grpc.keepalive_permit_without_calls', True),
        ('grpc.http2.max_pings_without_data', 0),
    ]
)

# Use shared channel for both exporters
log_exporter = OTLPLogExporter(
    endpoint="localhost:4317",
    insecure=True,
    timeout=1,
    channel=channel,  # Reuse connection
)
```

## Testing Checklist

After each phase, verify:
- [ ] Application starts without errors
- [ ] Logs appear in Grafana Loki
- [ ] Traces appear in Tempo with correct service name
- [ ] Custom fields are preserved in logs
- [ ] Trace IDs correlate between logs and traces
- [ ] No performance degradation
- [ ] No data loss during the migration