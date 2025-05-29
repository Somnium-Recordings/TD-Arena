import pytest
from opentelemetry import trace
from opentelemetry.trace import StatusCode

from .decorators import trace_span


def get_inmemory_exporter():
	return trace.get_tracer_provider(
	)._test_exporter  # type: ignore[attr-defined]


@pytest.fixture(autouse=True)
def clear_exporter():
	exporter = get_inmemory_exporter()
	exporter.clear()
	yield


def test_trace_span_basic():

	@trace_span()
	def test_func():
		return "test"

	result = test_func()
	assert result == "test"

	# Get the finished spans
	exporter = get_inmemory_exporter()
	spans = exporter.get_finished_spans()
	assert len(spans) == 1
	span = spans[0]
	assert span.name == "test_func"
	assert span.status.status_code == StatusCode.OK


def test_trace_span_with_attributes():

	@trace_span(attributes={"test_key": "test_value"})
	def test_func():
		return "test"

	result = test_func()
	assert result == "test"

	# Get the finished spans
	exporter = get_inmemory_exporter()
	spans = exporter.get_finished_spans()
	assert len(spans) == 1
	span = spans[0]
	assert span.name == "test_func"
	assert span.status.status_code == StatusCode.OK
	assert span.attributes is not None
	assert span.attributes.get("test_key") == "test_value"


def test_trace_span_with_error():

	@trace_span()
	def test_func():
		raise ValueError("test error")

	with pytest.raises(ValueError):
		test_func()

	# Get the finished spans
	exporter = get_inmemory_exporter()
	spans = exporter.get_finished_spans()
	assert len(spans) == 1
	span = spans[0]
	assert span.name == "test_func"
	assert span.status.status_code == StatusCode.ERROR
