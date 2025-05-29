import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter


@pytest.fixture(scope="session", autouse=True)
def setup_tracer_provider():
	exporter = InMemorySpanExporter()
	provider = TracerProvider()
	processor = SimpleSpanProcessor(exporter)
	provider.add_span_processor(processor)
	trace.set_tracer_provider(provider)
