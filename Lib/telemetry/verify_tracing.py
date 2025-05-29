import time

from .config import initialize_telemetry
from .context import trace_context
from .otel_decorators import trace_span


def main():
	# Initialize OpenTelemetry (prints to console if exporter is set to console in config)
	initialize_telemetry(
		service_name="td-arena-test",
		endpoint="http://localhost:4317",
		log_level="INFO"
	)
	print("[verify_tracing] Telemetry initialized.")

	# Use context manager for tracing
	with trace_context(
		"verify_context_span", attributes={"test": "context"}
	) as span:
		ctx = span.get_span_context()
		print(
			f"[verify_tracing] In context span: span_id={ctx.span_id}, trace_id={ctx.trace_id}, is_recording={span.is_recording()}"
		)
		time.sleep(0.1)

	# Use decorator for tracing
	@trace_span(attributes={"test": "decorator"})
	def traced_function(x, y):
		print(f"[verify_tracing] In decorated function: x={x}, y={y}")
		time.sleep(0.1)
		return x + y

	result = traced_function(2, 3)
	print(f"[verify_tracing] Decorated function result: {result}")

	print(
		"[verify_tracing] Tracing verification complete. Check your OpenTelemetry backend for spans."
	)


main()
