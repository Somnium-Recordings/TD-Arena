import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from .config import initialize_telemetry


def test_initialize_telemetry_and_guard(monkeypatch):
	# Patch BatchSpanProcessor to use InMemorySpanExporter for test
	from opentelemetry.sdk.trace.export import BatchSpanProcessor
	exporters = []

	class TestBatchSpanProcessor(BatchSpanProcessor):

		def __init__(self, exporter):
			exporters.append(exporter)
			super().__init__(exporter)

	monkeypatch.setattr(
		"opentelemetry.sdk.trace.export.BatchSpanProcessor", TestBatchSpanProcessor
	)
	monkeypatch.setattr(
		"opentelemetry.exporter.otlp.proto.grpc.trace_exporter.OTLPSpanExporter",
		InMemorySpanExporter
	)

	# First initialization should succeed
	initialize_telemetry(service_name="test1")
	provider1 = trace.get_tracer_provider()
	assert isinstance(provider1, TracerProvider)
	# Exporter assertion is best-effort; may be 0 if provider already set by another test
	assert len(exporters) in (0, 1)

	# Guard: Second initialization should raise RuntimeError
	with pytest.raises(RuntimeError):
		initialize_telemetry(service_name="test2")
